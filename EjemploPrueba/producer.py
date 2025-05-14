import json
import argparse
from kafka import KafkaProducer

def enviar_notificacion():
    parser = argparse.ArgumentParser(description='Envía notificaciones NGSI a Kafka')
    parser.add_argument('archivo_json', type=str, help='Ruta al archivo JSON con la notificación')
    args = parser.parse_args()

    # Cargar notificación desde el archivo
    with open(args.archivo_json) as f:
        notificacion = json.load(f)

    # Configurar productor Kafka
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Enviar a raw_notifications
    producer.send('raw_notifications', value=notificacion)
    producer.flush()

    print(f"✅ Notificación enviada a raw_notifications")
    print(f"Se creará el tópico: {notificacion['headers']['fiware-servicepath'].strip('/')}_{notificacion['body']['entityType'].lower()}")

if __name__ == "__main__":
    enviar_notificacion()