import json
import argparse
from kafka import KafkaProducer

def send_notification():
    parser = argparse.ArgumentParser(description='Send NGSI notification to Kafka')
    parser.add_argument('archivo_json', type=str, help='Path to the JSON file with notification')
    args = parser.parse_args()

    # Load notification from file
    with open(args.archivo_json) as f:
        notificacion = json.load(f)

    # Configure and create Kafka producer
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Send to raw_notifications
    producer.send('raw_notifications', value=notificacion)
    producer.flush()

    print(f"✅ Notification sent successfully to raw_notifications")
    topic_name = (
        f"{notificacion['headers']['fiware-servicepath'].strip('/')}_{notificacion['body']['entityType'].lower()}_lastdata"
        if notificacion['headers'].get('lastdata')
        else f"{notificacion['headers']['fiware-servicepath'].strip('/')}_{notificacion['body']['entityType'].lower()}"
    )
    print(f"This topic will be created if not exists: {topic_name}")

if __name__ == "__main__":
    send_notification()