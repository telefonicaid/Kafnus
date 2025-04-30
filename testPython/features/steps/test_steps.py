from behave import given, when, then
from kafka import KafkaProducer
import requests
import json
import time
import sqlalchemy

# USE this
KAFKA_BROKER = "localhost:9092"
POSTGRES_URL = "postgresql://test:test@localhost:5432/testdb"
CONNECT_URL = "http://localhost:8083"

@given('el topico "{topic}" en Kafka contiene un mensaje JSON valido')
def step_impl(context, topic):
    context.message = {"id": 1, "nombre": "Juan"}
    producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER,
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    producer.send(topic, context.message)
    producer.flush()

@when('el conector JDBC está configurado para ese tópico')
def step_impl(context):
    config = {
        "name": "jdbc-sink",
        "config": {
            "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
            "tasks.max": "1",
            "topics": context.topic,
            "connection.url": "jdbc:postgresql://postgres:5432/testdb?user=test&password=test",
            "auto.create": "true",
            "insert.mode": "insert",
            "pk.mode": "none",
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "value.converter.schemas.enable": "false"
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{CONNECT_URL}/connectors", headers=headers, data=json.dumps(config))
    if response.status_code not in (200, 201, 409):  # 409 = Already exists
        raise Exception(f"Error configurando conector: {response.text}")
    time.sleep(10)  # espera a que el conector procese el mensaje

    
@then('una fila correspondiente debe existir en la tabla "{tabla}" de SQL')
def step_impl(context, tabla):
    import sqlalchemy
    engine = sqlalchemy.create_engine(POSTGRES_URL)
    with engine.connect() as conn:
        result = conn.execute(f"SELECT * FROM {tabla} WHERE id = 1")
        row = result.fetchone()
        assert row is not None
        assert row['nombre'] == "Juan"
