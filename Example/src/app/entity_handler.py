import json
from app.kafka_utils import to_kafka_connect_schema, build_kafka_key
from app.types_utils import sanitize_topic, to_wkb_struct_from_wkt, to_wkt_geometry

async def handle_entity(app, raw_value, suffix="", include_timeinstant=True, key_fields=None):
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
