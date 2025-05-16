import faust
from faust import Topic
from datetime import datetime, timezone
import json
import re
import pytz
from shapely import wkt
from shapely.geometry import shape
import binascii
import base64
import asyncio


app = faust.App(
    'ngsi-processor',
    broker='kafka://kafka:9092',
    value_serializer='raw',
    topic_allow_declare=True
)


# Topic definition
input_topic = app.topic('raw_notifications')


def to_wkb_struct_from_wkt(wkt_str, field_name, srid=4326):
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
    try:
        if attr_type == "geo:point":
            if isinstance(attr_value, str):
                lat, lon = map(float, attr_value.split(','))
                return f"POINT ({lon} {lat})"  # WKT: POINT (X Y)
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
        # Añadir más tipos geométricos según sea necesario (geo:line, geo:box, etc.)
    except Exception as e:
        print(f"❌ Error generating WKT ({attr_type}): {e}")
    return None

def format_timestamp_with_utc(dt=None):
    if dt is None:
        return datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    else:
        return dt.astimezone(timezone.utc).isoformat(timespec='milliseconds')


def sanitize_topic(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name.strip('/').lower())

def infer_field_type(name, value, attr_type=None):
    """
    Infer Kafka Connect field type based on NGSI attribute type or Python type,
    and return the possibly transformed value.
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

    # Add recvtime
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



def build_kafka_key(entity: dict, include_timeinstant=False):
    fields = [{"field": "entityid", "type": "string", "optional": False}]
    payload = {"entityid": entity.get("entityid")}

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


@app.agent(input_topic)
async def process(stream):
    async for raw_value in stream:
        try:
            event = json.loads(raw_value)
            headers = event.get("headers", {})
            body = event.get("body", {})

            service = headers.get("fiware-service", "default").lower()
            servicepath = headers.get("fiware-servicepath")
            is_lastdata = headers.get("lastdata", False)

            entity_type = body.get("entityType", "unknown").lower()
            suffix = "_lastdata" if is_lastdata else ""
            topic_name = sanitize_topic(f"{servicepath}_{entity_type}{suffix}")
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
                elif attr_type=="json":
                    try:
                        value = json.dumps(value, ensure_ascii=False)
                    except Exception as e:
                        print(f"⚠️ Error serializing field {name} as JSON string: {e}")
                        value = str(value)

                attributes[name] = value
            
            print("Valor para linearrivaltime antes de esquema:", attributes.get("linearrivaltime"))

            entity.update(attributes)
            kafka_message = to_kafka_connect_schema(entity, schema_overrides)

            kafka_key = build_kafka_key(entity, include_timeinstant=not is_lastdata)

            await output_topic.send(
                key=kafka_key,
                value=json.dumps(kafka_message).encode("utf-8")
            )

            print(f"✅ Processed and sent to topic '{topic_name}': {entity['entityid']}")

        except Exception as e:
            print(f"❌ Error processing message: {e}")
