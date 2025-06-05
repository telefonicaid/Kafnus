import time
import json
import re
from datetime import datetime, timezone

from app.types_utils import sanitize_topic, extract_timestamp, format_timestamp, encode_mongo
from app.kafka_utils import build_kafka_key
from app.entity_handler import handle_entity
from app.metrics import start_metrics_server, messages_processed, processing_time
from app.faust_app import app, raw_historic_topic, raw_lastdata_topic, raw_mutable_topic, raw_errors_topic, mongo_output_topic, mongo_topic

# Historic Agent
@app.agent(raw_historic_topic)
async def process_historic(stream):
    """
    Consumes raw NGSI notifications from the 'raw_historic' topic and processes them as historic records.
    Each message is transformed to Kafka Connect format and forwarded to the corresponding output topic.
    Primary key includes entity ID and TimeInstant for proper versioning of historical data.
    """
    async for raw_value in stream:
        start = time.time()
        try:
            await handle_entity(app, raw_value, suffix="", include_timeinstant=True, key_fields=["entityid"])
        except Exception as e:
            print(f"❌ Historic error: {e}")
        
        duration = time.time() - start
        messages_processed.labels(flow="historic").inc()
        processing_time.labels(flow="historic").set(duration)


# Table of last timeinstant for entity
last_seen_timestamps = app.Table(
    'lastdata_entity_timeinstant',
    default=float,
    partitions=1  # Match the raw_lastdata topic
)


# Lastdata Agent
@app.agent(raw_lastdata_topic)
async def process_lastdata(stream):
    """
    Consumes NGSI notifications from the 'raw_lastdata' topic and stores the latest timestamp of each entity.
    If the notification timestamp is more recent than the previously seen one, the entity is updated.
    Handles deletion events explicitly by sending a null value with the proper key to trigger deletion in the sink.
    """
    async for raw_value in stream:
        start = time.time()
        try:
            event = json.loads(raw_value)
            body = event.get("body", {})
            entity_id = body.get("entityId")
            alteration_type = event.get("alterationType")

            if not entity_id:
                continue

            # Handle entity deletion
            if alteration_type == "entityDelete":
                # Create a minimal entity structure for deletion
                delete_entity = {
                    "entityid": entity_id,
                    "entitytype": body.get("entityType"),
                    "fiwareservicepath": event.get("headers", {}).get("fiware-servicepath", "/")
                }
                
                # Get topic info (same logic as handle_entity)
                headers = event.get("headers", {})
                service = headers.get("fiware-service", "default").lower()
                servicepath = headers.get("fiware-servicepath", "/")
                entity_type = body.get("entityType", "unknown").lower()
                
                target_table = sanitize_topic(f"{servicepath}_{entity_type}_lastdata")
                topic_name = f"{service}_lastdata"
                output_topic = app.topic(topic_name)
                
                # Build Kafka key (same as handle_entity with include_timeinstant=False)
                kafka_key = build_kafka_key(delete_entity, include_timeinstant=False)
                
                # Send null value to trigger deletion
                await output_topic.send(
                    key=kafka_key,
                    value=None,  # This will trigger deletion in JDBC sink with delete.enabled=true
                    headers=[("target_table", target_table.encode())]
                )
                
                # Also remove from timestamps table
                last_seen_timestamps.pop(entity_id, None)
                
                print(f"🗑️ [lastdata] Sent delete for entity: {entity_id}")
                continue

            # Processing flow for normal updates
            current_ts = extract_timestamp(body)
            last_ts = last_seen_timestamps[entity_id]

            if current_ts >= last_ts:
                last_seen_timestamps[entity_id] = current_ts
                await handle_entity(app, raw_value, suffix="_lastdata", include_timeinstant=False, key_fields=["entityid"])
            else:
                print(f"⚠️ Ignorado {entity_id} por timestamp viejo ({current_ts} < {last_ts})")

        except Exception as e:
            print(f"❌ Lastdata error: {e}")
        
        duration = time.time() - start
        messages_processed.labels(flow="lastdata").inc()
        processing_time.labels(flow="lastdata").set(duration)


# Mutable Agent
@app.agent(raw_mutable_topic)
async def process_mutable(stream):
    """
    Consumes NGSI notifications from the 'raw_mutable' topic and stores them as mutable records.
    Includes TimeInstant in the primary key.
    """
    async for raw_value in stream:
        start = time.time()
        try:
            await handle_entity(app, raw_value, suffix="_mutable", include_timeinstant=True, key_fields=["entityid"])
        except Exception as e:
            print(f"❌ Mutable error: {e}")
        
        duration = time.time() - start
        messages_processed.labels(flow="mutable").inc()
        processing_time.labels(flow="mutable").set(duration)


# Errors Agent
@app.agent(raw_errors_topic)
async def process_errors(stream):
    """
    Processes Kafka Connect error messages from the 'postgis_errors' topic.
    Parses failed inserts or connector issues, extracts the relevant SQL error message and context,
    and emits a structured error log message to a per-tenant error topic (e.g., 'clientname_error_log').
    """
    async for message in stream.events():
        start = time.time()

        headers = {k: v.decode("utf-8") for k, v in (message.message.headers or [])}
        value_raw = message.value

        try:
            value_json = json.loads(value_raw)
        except Exception as e:
            print(f"⚠️ Error parsing JSON payload: {e}")
            continue

        # Extract full error information
        full_error_msg = headers.get("__connect.errors.exception.message", "Unknown error")
        
        # Get timestamp
        timestamp = format_timestamp(tz='Europe/Madrid')

        
        # Get database name
        db_name = headers.get("__connect.errors.topic", "")
        if db_name == "":
            db_name_match = re.search(r'INSERT INTO "([^"]+)"', full_error_msg)
            if db_name_match:
                db_name = db_name_match.group(1).split('.')[0]

        # Remove unwanted suffixes
        db_name = re.sub(r'_(lastdata|mutable)$', '', db_name)

        # Get name of output topic
        error_topic_name = f"{db_name}_error_log"
        error_topic = app.topic(error_topic_name, value_serializer='json')

        # Process error message
        error_match = re.search(r'(ERROR: .+?)(\n|$)', full_error_msg)
        if error_match:
            error_message = error_match.group(1).strip()

            # Add details if present
            detail_match = re.search(r'(Detail: .+?)(\n|$)', full_error_msg)
            if detail_match:
                error_message += f" - {detail_match.group(1).strip()}"
        else:
            error_message = full_error_msg

        # Extract query if aviable
        query_match = re.search(r'(INSERT INTO "[^"]+"[^)]+\)[^)]*\))', full_error_msg)
        if query_match:
            original_query = query_match.group(1)
        else:
            # Construct query from payload
            payload = value_json.get("payload", {})
            table = headers.get("target_table", "unknown_table")
            
            if payload:
                columns = ",".join(f'"{k}"' for k in payload.keys())
                values = []
                for k, v in payload.items():
                    if isinstance(v, str):
                        v = v.replace("'", "''")
                        values.append(f"'{v}'")
                    elif v is None:
                        values.append("NULL")
                    else:
                        values.append(str(v))
                values_str = ",".join(values)
                original_query = f'INSERT INTO "{db_name}"."{table}" ({columns}) VALUES ({values_str})'
            else:
                original_query = ""

        # Construct kafka message ready for connector
        error_record = {
            "schema": {
                "type": "struct",
                "fields": [
                    {"field": "timestamp", "type": "string", "optional": False},
                    {"field": "error", "type": "string", "optional": False},
                    {"field": "query", "type": "string", "optional": True}
                ],
                "optional": False
            },
            "payload": {
                "timestamp": timestamp,
                "error": error_message,
                "query": original_query
            }
        }

        # Send to client error_log topic
        await error_topic.send(value=error_record)

        print(f"🐞 Logged SQL error to '{error_topic_name}': {error_message}")

        duration = time.time() - start
        messages_processed.labels(flow="errors").inc()
        processing_time.labels(flow="errors").set(duration)


# Mongo Agent
@app.agent(mongo_topic)
async def process(events):
    """
    Consumes NGSI notifications from the 'raw_mongo' topic and transforms them into MongoDB-compatible documents.
    Encodes Fiware service and service path to match MongoDB naming restrictions.
    Each message is enriched with reception timestamp and entity metadata before being published to the output topic.
    """
    async for raw in events:
        start = time.time()
        try:
            data = json.loads(raw)

            headers = data.get("headers", {})
            body = data.get("body", {})
            attributes = body.get("attributes", [])

            fiware_service = headers.get("fiware-service", "default")
            service_path = headers.get("fiware-servicepath", "/")

            # Encode database and collection
            mongo_db = f"sth_{encode_mongo(fiware_service)}"
            mongo_collection = f"sth_{encode_mongo(service_path)}"

            timestamp = int(headers.get("timestamp", datetime.now().timestamp()))
            recv_time_ts = str(timestamp * 1000)
            recv_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc).isoformat()

            # Document to be inserted
            doc = {
                "recvTimeTs": recv_time_ts,
                "recvTime": recv_time,
                "entityId": body.get("entityId"),
                "entityType": body.get("entityType")
            }

            for attr in attributes:
                name = attr.get("attrName")
                value = attr.get("attrValue")
                doc[name] = value

            # Send to Kafka with key for routing
            await mongo_output_topic.send(
                key=json.dumps({
                    "database": mongo_db,
                    "collection": mongo_collection
                }),
                value=json.dumps(doc)
            )

            print(f"✅ ['mongo'] Sent to topic 'alcobendas_mongo' | DB: {mongo_db}, Collection: {mongo_collection}")

        except Exception as e:
            print("❌ Error processing event:", e)
        
        duration = time.time() - start
        messages_processed.labels(flow="mongo").inc()
        processing_time.labels(flow="mongo").set(duration)