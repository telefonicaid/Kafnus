import json
from app.types_utils import infer_field_type, format_timestamp

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
    recvtime = format_timestamp(tz='Europe/Madrid')

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