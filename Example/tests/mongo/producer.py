import sys
import json
from kafka import KafkaProducer

if len(sys.argv) != 2:
    print("Uso: python producer.py <archivo_json>")
    sys.exit(1)

json_file = sys.argv[1]

with open(json_file, "r") as file:
    payload = json.load(file)

# Configurartion kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = "mongo_test"
producer.send(topic, value=payload)
producer.flush()

print(f"✅ Event sent to Kafka from file: {json_file}")