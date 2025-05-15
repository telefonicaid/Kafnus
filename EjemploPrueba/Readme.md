# 🔄 NGSI Kafka Stream Processor

This project implements a lightweight NGSIv2 notification processing architecture using Kafka, Faust, and Kafka Connect, with persistence in PostgreSQL/PostGIS.

---

## 📁 Files and Structure

```
.
├── accesscount_notification.json # NGSIv2 notification (accesses)
├── parking_notification.json # NGSIv2 notification (parking)
├── pg-sink-historic.json # JDBC connector for storing historical data
├── pg-sink-lastdata.json # JDBC connector for the last value
├── producer.py # Script for sending NGSIv2 notifications to Kafka
├── stream_processor.py # Faust microservice that processes raw notifications
├── requirements.txt # Python dependencies (includes Faust and Kafka)
├── Dockerfile # Image to run Faust
├── docker-compose.yml # Kafka Services, Connect, etc.
├── docker-compose.override.yml # Additional settings for local environments
├── kafka-faust-env/ # Python virtual environment for running Faust
└── plugins/ # Custom Kafka connector (JDBC, MongoDB, etc.)
```

---

## 🧠 Key Concepts

### 🔹 NGSIv2 Notifications and `producer.py`

- `.json` files such as `accesscount_notification.json` and `parking_notification.json` contain examples of NGSIv2-style notifications.
- These notifications are sent to the Kafka `raw_notifications` topic using the `producer.py` script.
- The script requires the `kafka-python` library installed, which you can use within the `kafka-faust-env` virtual environment.

---

### 🔹 System Architecture

- **Kafka + Kafka Connect** handle the streaming infrastructure and integration with external systems.
- **Faust (`stream_processor.py`)** is a Kafka Stream-like microservice that replaces the Cygnus logic:
- Processes NGSIv2 notifications from the `raw_notifications` topic.
- Automatically adds the `recvtime` field.
- Transforms `geo:*` geometries (such as `geo:point`, `geo:polygon`) into serializable structures compatible with PostGIS (WKB).
- Constructs messages with the Kafka Connect schema to facilitate JDBC integration.
- **PostGIS** is set up as a separate service and serves as the destination for persisted data.

---

### 🔹 Plugins

The `plugins/` directory includes the `.jar` for the custom JDBC and MongoDB connector required for Kafka Connect. These are mounted in the container using a volume.

**Important:** If you change the project structure, be sure to update this line in `docker-compose.yml`:

```
volumes:
- ./plugins:/etc/kafka-connect/plugins
```

---

## 🧪 How to Run it

1. **Set up PostGIS separately**
You can use a container or a local installation.

2. **Start services with docker**
The Docker file is already configured, so you don’t need to follow the detailed setup process below. If everything works correctly, simply run the following command from the project root:

```bash
docker compose -f docker-compose.yml up
```

If you encounter any issues, you can try the following:

- **Start Kafka and Kafka Connect manually**

```bash
docker compose -f docker-compose.yml up
```

- **Start the Faust microservice**
In case of code changes, it will also need to be built:

```bash
docker compose build faust-stream
docker compose up faust-stream
```

In case there is no `raw_notifications` topic created, it could fail and it may need to re-launch `faust-stream`.

- **Register the connectors in Kafka Connect**
For now, only the history connector has been tested:

```bash
curl -X POST http://localhost:8083/connectors \
-H "Content-Type: application/json" \
--data @pg-sink-historic.json
```

- **Send NGSIv2 notifications** to the raw topic:

```bash
python producer.py accesscount_notification.json
```

If a topic needs to be checked because changes in message processing cause errors, you can do so with this command:

```bash
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic TOPIC_NAME --from-beginning --max-messages 10
```

---

## 🛠️ Pending Improvements

- ✅ Process `application/json` as `attrValue` (not just string).
- ✅ Support for more complex geometries such as `geo:json`.
- ⚠️ **Known bug:** If Faust creates a new topic and no partitions are yet available, it may not connect correctly. In this case, simply shut down and restart the Faust service.
- 🕒 Improve date handling and normalization (e.g., `timeinstant`, timezones).
- ➕ Include `fiware-servicepath` in the processed payload (currently only used for the topic name, but not saved in the resulting message).