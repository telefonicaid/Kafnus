from time import sleep
from testcontainers.compose import DockerCompose
import pytest
import json
from kafka import KafkaConsumer
import requests
import time
from requests.exceptions import RequestException
from dataclasses import dataclass
from typing import List, Dict

headers_mqtt_to_kafka_connector = {
        "content-type": "application/json",
        "Accept": "application/json"
    }

mqtt_to_kafka_connector = {
        "name": "mosquitto-source-connector",
        "config": {
            "connector.class": "com.example.mqtt.MqttSourceConnector",
            "mqtt.broker": "mosquitto",
            "mqtt.topic": "kafnus/+/+/+",
            "kafka.topic": "mqtt_events",
            "mqtt.username": "user",
            "mqtt.password": "pass",
            "tasks.max": "1",
            "mqtt.qos": "1"
        }
    }

@dataclass
class MultiServiceContainer:
    """Centralizes management of multiservice Docker environments during end-to-end testing."""
    orionHost: str
    orionPort: str
    kafkaHost: str
    kafkaPort: str
    consumer: KafkaConsumer
    mqttToKafkaConnectHost: str
    mqttToKafkaConnectPort: str

@pytest.fixture(scope="function")
def multiservice_stack():
    with DockerCompose("../", compose_file_name=["docker-compose.yml"], pull=False, wait=True, build=True) as compose:
        #orion service
        orion_host = compose.get_service_host("orion")
        orion_post = compose.get_service_port("orion", 1026)
        wait_for_orion(orion_host, orion_post)

        #kafka service
        kafka_host = compose.get_service_host("kafka", 9092)
        kafka_port = compose.get_service_port("kafka", 9092)
        wait_for_kafka(kafka_host, kafka_port)

        #mqtt to kafka connect
        mqtt_to_kafka_connect_host = compose.get_service_host("connect", 8083)
        mqtt_to_kafka_connect_port = compose.get_service_port("connect", 8083)
        wait_for_mqtt_to_kafka_connect(mqtt_to_kafka_connect_host, mqtt_to_kafka_connect_port)

        # Configuring Kafka consumer
        consumer = KafkaConsumer(
            bootstrap_servers=f"{kafka_host}:{kafka_port}",
            auto_offset_reset="earliest",
            group_id="test-group",
            enable_auto_commit=False,
            consumer_timeout_ms=10000)

        yield MultiServiceContainer(
            orionHost=orion_host,
            orionPort=orion_post,
            kafkaHost=kafka_host,
            kafkaPort=kafka_port,
            consumer=consumer,
            mqttToKafkaConnectHost=mqtt_to_kafka_connect_host,
            mqttToKafkaConnectPort=mqtt_to_kafka_connect_port
        )
        # Cleaning
        consumer.close()

def wait_for_orion(host, port, timeout=30):
    """Wait until orion is ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://{host}:{port}/version")
            if response.status_code == 200:
                return
        except:
            time.sleep(1)
    raise Exception("Orion did not start in the expected time")

def wait_for_kafka(host_kafka, port_kafka, timeout=60):
    """Wait until Kafka is ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            consumer = KafkaConsumer(
                bootstrap_servers=f"{host_kafka}:{port_kafka}",
                auto_offset_reset="earliest",
                group_id="test-wait-group",
                consumer_timeout_ms=1000
            )
            consumer.topics()
            consumer.close()
            return
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError("Kafka no estuvo listo a tiempo")

def wait_for_mqtt_to_kafka_connect(host: str = "connect", port: int = 8083):
    """Wait until mqtt to kafka Connect is ready."""
    timeout: int = 120
    interval: int = 5
    health_path: str = "/connectors"
    expected_status: int = 200
    start_time = time.time()
    url = f"http://{host}:{port}{health_path}"

    print(f"Esperando a Kafka Connect en {url}...")

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == expected_status:
                print("✓ Kafka Connect is ready and responding")
                response_connect = requests.post(f"{url}", data=json.dumps(mqtt_to_kafka_connector), headers=headers_mqtt_to_kafka_connector)
                assert response_connect.status_code in [201, 204]
                return True
            print(f"! Unexpected response: {response.status_code}")

        except RequestException as e:
            print(f"x Connection error: {str(e)}")
        time.sleep(interval)

    sleep(1000)
    raise TimeoutError(
        f"Kafka Connect was not ready after {timeout} seconds."
        f"Last URL tested: {url}"
    )

@dataclass
class OrionRequestData:
    """Orion request data"""
    name:str
    service: str
    subservice: str
    subscriptions: dict
    updateEntities: list

@dataclass
class KafkaMessages:
    """Kafka message"""
    topic: str
    headers: dict
    message: dict

class OrionAdapter:
    """Orion adapter"""
    orionHost:str
    orionPort:str
    baseUrl: str
    headers: dict
    generators: List[OrionRequestData]

    def __init__(self, orionHost:str, orionPort:str, generators:List[OrionRequestData]):
        self.orionHost = orionHost
        self.orionPort = orionPort
        self.baseUrl = f"http://{orionHost}:{orionPort}/v2"
        self.generators = generators
        self.headers = {}
        for generator in self.generators:
            self.headers[f"""{generator.name}"""] = {
                "content-type": "application/json",
                "Fiware-Service": generator.service,
                "Fiware-ServicePath": generator.subservice,
                "Accept": "application/json"
        }

    def create_subscriptions(self):
        """create subscriptions"""
        for generator in self.generators:
            headers_: dict= self.headers[f"""{generator.name}"""]
            for key, subscription in generator.subscriptions.items():
                response = requests.post(f"{self.baseUrl}/subscriptions", headers=headers_, data=json.dumps(subscription))
                assert response.status_code in [201, 204]

    def update_entities(self):
        """update entities"""
        params = {
                 "options": "flowControl"
            }

        for generator in self.generators:
            data = {
                "actionType": "append",
                "entities": generator.updateEntities
            }
            response = requests.post(f"{self.baseUrl}/op/update", data=json.dumps(data), params = params, headers=self.headers[f"""{generator.name}"""])
            print(response.content)
            assert response.status_code in [201, 204]

class ServiceOperations:
    """Service operations"""
    multi_service_container: MultiServiceContainer
    topics_raw : list
    consumer : KafkaConsumer
    generators: List[OrionRequestData]


    def __init__(self, multi_service_container, generated_data):
        self.multi_service_container = multi_service_container
        self.topics_raw = ["raw_historic", "raw_lastdata", "raw_mutable"]
        self.consumer = self.multi_service_container.consumer
        self.generators = generated_data

    def orion_set_up(self):
        """orion set up"""
        host_orion = self.multi_service_container.orionHost
        port_orion = self.multi_service_container.orionPort

        orion_adapter = OrionAdapter(host_orion, port_orion, self.generators)
        orion_adapter.create_subscriptions()
        orion_adapter.update_entities()

    def subscribe_to_kafka_topics(self):
        """subscribe to kafka topics"""
        self.consumer.subscribe(self.topics_raw)
        self.consumer.poll(timeout_ms=1000)  # Poll inicial para asignar particiones
        self.consumer.seek_to_beginning(*self.consumer.assignment())

    def check_messages_on_kafka(self):
        """check messages on kafka"""
        # Leer mensajes
        all_entities = []
        expected_messages = 0
        for generator in self.generators:
            messages_by_generator = len(generator.updateEntities) * len(generator.subscriptions)
            expected_messages += messages_by_generator
        messages = []
        completed = False
        while not completed:
            records = self.consumer.poll(timeout_ms=6000, max_records=expected_messages, update_offsets=False)
            if records:
                for tp, msgs in records.items():
                    topic = tp.topic
                    for message in msgs:
                        # Procesar headers
                        headers_dict = {}
                        if message.headers:
                            headers_dict = dict(map(lambda header: (header[0],header[1].decode('utf-8') if isinstance(header[1], bytes) else header[1]), message.headers))
                        # Decodificar el valor del mensaje si es bytes
                        try:
                            message_value = message.value
                            data = json.loads(message_value)
                            data.pop('subscriptionId', None)
                            kafka_menssage = KafkaMessages(topic=topic, headers=headers_dict, message=data)
                            messages.append(kafka_menssage)
                        except Exception as e:
                            print(f"Error processing message: {e}")
                            continue
            else:
                completed = True
        a=1
        return messages
