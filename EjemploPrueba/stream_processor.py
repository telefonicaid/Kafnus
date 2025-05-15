import faust
from datetime import datetime
import json
import re
import pytz
from shapely import wkt
from shapely.geometry import shape
import binascii
import base64

app = faust.App(
    'ngsi-processor',
    broker='kafka://kafka:9092',
    value_serializer='raw',
    topic_allow_declare=True,
    topic_disable_leader=True
)

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
        # Añadir más tipos geométricos según sea necesario (geo:line, geo:box, etc.)
    except Exception as e:
        print(f"❌ Error generating WKT ({attr_type}): {e}")
    return None

def format_timestamp_with_utc(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def sanitize_topic(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name.strip('/').lower())


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

        # Traditional typing if not override
        if isinstance(v, bool):
            field_type = "boolean"
        elif isinstance(v, int):
            field_type = "int32"
        elif isinstance(v, float):
            field_type = "float"
        elif k == "timeinstant":
            try:
                dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                dt = dt.astimezone(pytz.timezone('Europe/Madrid'))
                v = format_timestamp_with_utc(dt)
            except Exception as e:
                print(f"⚠️ Error formatting timeinstant: {e}")
            field_type = "string"
        else:
            field_type = "string"

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



@app.agent(input_topic)
async def process(stream):
    async for raw_value in stream:
        try:
            event = json.loads(raw_value)
            headers = event.get("headers", {})
            body = event.get("body", {})

            service = headers.get("fiware-service", "default").lower()
            servicepath = headers.get("fiware-servicepath", "/").strip('/')
            entity_type = body.get("entityType", "unknown").lower()

            topic_name = sanitize_topic(f"{servicepath}_{entity_type}")
            output_topic = app.topic(topic_name)

            entity = {
                "entityid": body.get("entityId"),
                "entitytype": body.get("entityType")
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

                attributes[name] = value

            entity.update(attributes)
            kafka_message = to_kafka_connect_schema(entity, schema_overrides)

            await output_topic.send(value=json.dumps(kafka_message).encode("utf-8"))

            print(f"✅ Processed and sent to topic '{topic_name}': {entity['entityid']}")

        except Exception as e:
            print(f"❌ Error processing message: {e}")
