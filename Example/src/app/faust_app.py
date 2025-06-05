import faust
from app.config import KAFKA_BROKER

app = faust.App(
    'ngsi-processor',
    broker=KAFKA_BROKER,
    value_serializer='raw',
    topic_allow_declare=True
)

# Topics centralizados
raw_historic_topic = app.topic('raw_historic')
raw_lastdata_topic = app.topic('raw_lastdata')
raw_mutable_topic = app.topic('raw_mutable')
raw_errors_topic = app.topic('raw_errors')
mongo_topic = app.topic('raw_mongo')
mongo_output_topic = app.topic('alcobendas_mongo')
