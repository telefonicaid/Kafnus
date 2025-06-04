import faust
from faust import Topic
from datetime import datetime, timezone
import json
import re
import pytz
from shapely import wkt
from shapely.geometry import shape # https://shapely.readthedocs.io/en/stable/manual.html#shapely.geometry.shape
import binascii
import base64
import time
import asyncio

from metrics import start_metrics_server, messages_processed, processing_time


app = faust.App(
    'ngsi-processor',
    broker='kafka://kafka:9092',
    value_serializer='raw',
    topic_allow_declare=True
)

# Used in Prometheus service
start_metrics_server(port=8000)

# Input Kafka topics to consume raw NGSI notifications
# Separate topic for different flows or table type
raw_historic_topic = app.topic('raw_historic')
raw_lastdata_topic = app.topic('raw_lastdata')
raw_mutable_topic = app.topic('raw_mutable')
errors_topic = app.topic('postgis_errors')
mongo_topic = app.topic('raw_mongo')


def to_wkb_struct_from_wkt(wkt_str, field_name, srid=4326):
    """
    Converts a WKT geometry string to a Debezium-compatible WKB struct with schema and base64-encoded payload.
    Used for sending geo attributes in Kafka Connect format.
    """
    try:
        geom = wkt.loads(wkt_str)
        wkb = geom.wkb
        wkb_b64 = base64.b64encode(wkb).decode("ascii")
        return {
            "schema": {
                "field": field_name,
                "type": "struct",
                "name": "io.debezium.data.geometry.Geometry",
                "fields": [
                    {"field": "wkb", "type": "bytes"},
                    {"field": "srid", "type": "int32"}
                ],
                "optional": False
            },
            "payload": {
                "wkb": wkb_b64,
                "srid": srid
            }
        }
    except Exception as e:
        print(f"❌ Error generating WKB from WKT: {e}")
        return None


def to_wkt_geometry(attr_type, attr_value):
    """
    Converts NGSI geo attributes (geo:point, geo:polygon, geo:json) to WKT string.
    Supports extension for additional geo types if needed.
    """
    try:
        if attr_type == "geo:point":
            if isinstance(attr_value, str):
                lat, lon = map(float, attr_value.split(','))
                return f"POINT ({lon} {lat})"
        elif attr_type == "geo:polygon":
            coords = []
            for coord_str in attr_value:
                lat, lon = map(float, coord_str.split(','))
                coords.append(f"{lon} {lat}")
            coords_str = ", ".join(coords)
            return f"POLYGON (({coords_str}))"
        elif attr_type == "geo:json":
            geom = shape(attr_value)
            return geom.wkt
    except Exception as e:
        print(f"❌ Error generating WKT ({attr_type}): {e}")
    return None


def format_timestamp_with_utc(dt=None):
    """
    Formats a datetime object to ISO 8601 string with UTC timezone and milliseconds.
    If no datetime is provided, uses current UTC time.
    """
    if dt is None:
        return datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    else:
        return dt.astimezone(timezone.utc).isoformat(timespec='milliseconds')


def extract_timestamp(entity: dict) -> float:
    """
    Extract and transform to epoch seconds
    """
    ts = entity.get("TimeInstant") or entity.get("timestamp")
    if ts:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.timestamp()
    return 0.0


def sanitize_topic(name):
    """
    Sanitizes a string to be a valid Kafka topic name by replacing disallowed characters with underscores.
    """
    return re.sub(r'[^a-zA-Z0-9_]', '_', name.strip('/').lower())


def infer_field_type(name, value, attr_type=None):
    """
    Infers Kafka Connect field type from NGSI attrType or Python native type.
    Also transforms the value if needed (e.g. formatting dates, serializing JSON).
    Returns a tuple (field_type, processed_value).
    """
    if attr_type:
        if attr_type.startswith("geo:"):
            return "geometry", value  # handled externally
        elif attr_type == "DateTime":
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                value = format_timestamp_with_utc(dt)
            except Exception as e:
                print(f"⚠️ Error formatting DateTime for '{name}': {e}")
            return "string", value
        elif attr_type == "Number":
            return "float", value
        elif attr_type == "Integer":
            return "int32", value
        elif attr_type == "Boolean":
            return "boolean", value
        elif attr_type == "json":
            try:
                return "string", json.dumps(value, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ Error serializing {name} as JSON: {e}")
                return "string", str(value)
        elif attr_type == "Text":
            return "string", value

    # Fallback to Python type inference
    if isinstance(value, bool):
        return "boolean", value
    elif isinstance(value, int):
        return "int32", value
    elif isinstance(value, float):
        return "float", value
    elif name.lower() == "timeinstant":
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            dt = dt.astimezone(pytz.timezone('Europe/Madrid'))
            value = format_timestamp_with_utc(dt)
        except Exception as e:
            print(f"⚠️ Error formatting timeinstant: {e}")
        return "string", value
    else:
        return "string", value


def to_kafka_connect_schema(entity: dict, schema_overrides: dict = None):
    """
    Builds a Kafka Connect compatible schema and payload dict from the entity dict.
    Allows overriding field schemas (used mainly for geo attributes).
    """
    schema_fields = []
    payload = {}

    if schema_overrides is None:
        schema_overrides = {}

    for k, v in entity.items():
        if k in schema_overrides:
            schema_fields.append(schema_overrides[k])
            payload[k] = v
            continue
        
        field_type, v = infer_field_type(k, v)

        schema_fields.append({
            "field": k,
            "type": field_type,
            "optional": False
        })
        payload[k] = v

    # Add processing timestamp field
    recvtime = format_timestamp_with_utc()
    schema_fields.append({
        "field": "recvtime",
        "type": "string",
        "optional": False
    })
    payload["recvtime"] = recvtime

    return {
        "schema": {
            "type": "struct",
            "fields": schema_fields,
            "optional": False
        },
        "payload": payload
    }


def build_kafka_key(entity: dict, key_fields: list, include_timeinstant=False):
    """
    Builds the Kafka message key with schema based on key_fields and optionally timeinstant.
    This key is used for Kafka Connect upsert mode or primary key definition.
    """
    fields = []
    payload = {}

    for key in key_fields:
        fields.append({"field": key, "type": "string", "optional": False})
        payload[key] = entity.get(key)

    if include_timeinstant:
        fields.append({"field": "timeinstant", "type": "string", "optional": False})
        payload["timeinstant"] = entity.get("timeinstant")

    return json.dumps({
        "schema": {
            "type": "struct",
            "fields": fields,
            "optional": False
        },
        "payload": payload
    }).encode("utf-8")


async def handle_entity(raw_value, suffix="", include_timeinstant=True, key_fields=None):
    """
    Consumes raw NGSI notifications, processes and transforms them into Kafka Connect format.
    key_fields allows configuring which fields to use as primary key for upsert.
    """
    event = json.loads(raw_value)
    headers = event.get("headers", {})
    body = event.get("body", {})

    service = headers.get("fiware-service", "default").lower()
    servicepath = headers.get("fiware-servicepath", "/")
    entity_type = body.get("entityType", "unknown").lower()

    target_table = sanitize_topic(f"{servicepath}_{entity_type}{suffix}")
    topic_name = f"{service}{suffix}"
    output_topic = app.topic(topic_name)

    entity = {
        "entityid": body.get("entityId"),
        "entitytype": body.get("entityType"),
        "fiwareservicepath": servicepath
    }

    attributes = {}
    schema_overrides = {}

    for attr in sorted(body.get("attributes", []), key=lambda x: x['attrName']):
        name = attr["attrName"]
        value = attr["attrValue"]
        attr_type = attr.get("attrType", "")

        if attr_type.startswith("geo:"):
            wkt_str = to_wkt_geometry(attr_type, value)
            if wkt_str:
                wkb_struct = to_wkb_struct_from_wkt(wkt_str, name)
                if wkb_struct:
                    attributes[name] = wkb_struct["payload"]
                    schema_overrides[name] = wkb_struct["schema"]
                    continue
        elif attr_type == "json":
            try:
                value = json.dumps(value, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ Error serializing field {name} as JSON string: {e}")
                value = str(value)

        attributes[name] = value

    entity.update(attributes)

    if key_fields is None:
        key_fields = ["entityid"]

    kafka_message = to_kafka_connect_schema(entity, schema_overrides)
    kafka_key = build_kafka_key(entity, key_fields=key_fields, include_timeinstant=include_timeinstant)

    await output_topic.send(
        key=kafka_key,
        value=json.dumps(kafka_message).encode("utf-8"),
        headers=[("target_table", target_table.encode())]
    )

    print(f"✅ [{suffix.lstrip('_') or 'historic'}] Sent to topic '{topic_name}' (table: '{target_table}'): {entity.get('entityid')}")


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
            await handle_entity(raw_value, suffix="", include_timeinstant=True, key_fields=["entityid"])
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
                await handle_entity(raw_value, suffix="_lastdata", include_timeinstant=False, key_fields=["entityid"])
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
            await handle_entity(raw_value, suffix="_mutable", include_timeinstant=True, key_fields=["entityid"])
        except Exception as e:
            print(f"❌ Mutable error: {e}")
        
        duration = time.time() - start
        messages_processed.labels(flow="mutable").inc()
        processing_time.labels(flow="mutable").set(duration)


# Errors Agent
@app.agent(errors_topic)
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
        timestamp = format_timestamp_with_utc()
        
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

def encode_mongo(value: str) -> str:
    if value == '/':
        return 'x002f'
    value = value.replace('/', 'x002f')
    value = value.replace('.', 'x002e')
    value = value.replace('$', 'x0024')
    value = value.replace('"', 'x0022')
    value = value.replace('=', 'xffff')
    return value


mongo_output_topic = app.topic('alcobendas_mongo')
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
