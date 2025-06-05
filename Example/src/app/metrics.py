from prometheus_client import Counter, Gauge, start_http_server

messages_processed = Counter("messages_processed_total", "Processed messages total", ['flow'])
processing_time = Gauge("message_processing_time_seconds", "Message processing time in seconds", ['flow'])

def start_metrics_server(port=8000):
    start_http_server(port)