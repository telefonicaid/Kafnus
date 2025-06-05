import json
import argparse
from kafka import KafkaProducer

VALID_FLOWS = {
    "historic": "raw_historic",
    "lastdata": "raw_lastdata",
    "mutable": "raw_mutable",
    "errors": "errors",
    "mongo": "raw_mongo",
}

def send_notification():
    parser = argparse.ArgumentParser(description='Send NGSI notification to Kafka')
    parser.add_argument('archivo_json', type=str, help='Path to the JSON file with notification')
    args = parser.parse_args()

    # Load notification from file
    with open(args.archivo_json) as f:
        notificacion = json.load(f)

    # Determine topic based on 'flow'
    flow = notificacion.get("flow", "").lower()
    topic = VALID_FLOWS.get(flow)

    if topic is None:
        print(f"❌ Invalid or missing 'flow' value: '{flow}'. Must be one of: {list(VALID_FLOWS.keys())}")
        return

    # Configure Kafka producer
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Send notification to selected topic
    producer.send(topic, value=notificacion)
    producer.flush()

    print(f"✅ Notification sent successfully to topic: {topic}")

if __name__ == "__main__":
    send_notification()
