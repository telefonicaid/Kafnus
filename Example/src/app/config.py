import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka://kafka:9092")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))
TIMEZONE = os.getenv("DEFAULT_TZ", "Europe/Madrid")
