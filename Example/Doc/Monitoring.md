# 📊 Observability & Monitoring for Kafnus Architecture

This document describes how monitoring has been set up for the Kafka–Faust–Kafka Connect–PostGIS pipeline using **Prometheus**, **Grafana**, and **custom metrics** from Faust.

---

## 🌐 Service Access Overview

| Service           | URL                          | Port |
|-------------------|-------------------------------|------|
| **Grafana**       | [http://localhost:3000](http://localhost:3000) | `3000` |
| **Prometheus**    | [http://localhost:9090](http://localhost:9090) | `9090` |
| **Kafka Exporter**| [http://localhost:9308/metrics](http://localhost:9308/metrics) | `9308` |
| **Faust metrics** | [http://localhost:8000/metrics](http://localhost:8000/metrics) | `8000` |

---

## 📈 Exposed Metrics

### ✅ From Faust (`prometheus_client`)

Custom metrics are published from within the Faust service using the `prometheus_client` library:

- `messages_processed_total{flow="historic"}`:  
  Counter of messages processed by each flow

- `message_processing_time_seconds{flow="historic"}`:  
  Gauge of the processing time per message

These are accessible at [`http://localhost:8000/metrics`](http://localhost:8000/metrics) and are scraped by Prometheus.

> 📝 Each flow (`historic`, `lastdata`, `mutable`, etc.) has its own set of metrics.

---

### ✅ From Kafka Connect (via kafka-connect-exporter)

Using [`danielqsj/kafka-exporter`](https://github.com/danielqsj/kafka-exporter), we also expose Kafka Connect metrics including:

- Consumer group lag
- Connector and task states
- Offsets and throughput

These are available at [`http://localhost:9308/metrics`](http://localhost:9308/metrics`).

---

## 📊 Dashboards

### ✅ Grafana Dashboards

Custom dashboards have been created and exported as `.json` files. You can import them into Grafana by going to:

- `+ Create > Import > Upload .json file`

Available dashboards (in /monitoring/dashboards_grafana folder) include:

- **Faust Metrics Dashboard**
  - Rate of messages processed per flow
  - Processing time per flow

- **Kafka Connect Metrics**
  - Lag and offset metrics from Kafka Connect
  - Connector health and task counts

---

## ⚙️ Configuration Summary

### Prometheus `prometheus.yml` (fragment)

```yaml
scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-connect-exporter:9308']
  - job_name: 'faust'
    static_configs:
      - targets: ['faust-stream:8000']
  - job_name: 'kafka-connect'
    static_configs:
      - targets: ['kafka-connect:9100']
```

### 🔍 JMX Exporter for Kafka Connect

Kafka Connect is instrumented with [JMX Exporter](https://github.com/prometheus/jmx_exporter) to expose JVM-level and Kafka Connect metrics.

Make sure the following files are present:

- `monitoring/jmx_prometheus_javaagent.jar`
- `monitoring/kafka-connect.yml`

These are mounted into the container and activated via the `JMX_PROMETHEUS_EXPORTER_OPTS` environment variable.

> If these files are missing when Docker starts, Docker may create placeholder **folders** with their names. Make sure the files are present before launching the stack.

They can be installed with:

```bash
cd ../monitoring
wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar -O jmx_prometheus_javaagent.jar
```

### Faust Docker command (in docker-compose.override.yml)

```yaml
command: faust -A stream_processor worker -l info
```
> The Faust app does not use `--web-port`, to avoid port conflicts with `prometheus_client`.

## 📚 Notes

- All metrics are emitted in **Prometheus format**.
- Ports are exposed in `docker-compose.override.yml` for **external access**.
- Faust metrics are **custom-coded**, giving more flexibility than the default web server.
- The system can be extended to include **alerts**, **dashboards per client**, or **anomaly detection** using **Prometheus alert rules** or **Grafana annotations**.
