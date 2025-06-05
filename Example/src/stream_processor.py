from app.faust_app import app
from app.agents import *  # Import agents = launch agents
from app.metrics import start_metrics_server

# Start Prometheus HTTP server for Faust metrics
start_metrics_server(port=8000)