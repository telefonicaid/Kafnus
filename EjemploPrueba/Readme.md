# 🔄 NGSI Kafka Stream Processor

This project implements a lightweight NGSIv2 notification processing architecture using Kafka, Faust, and Kafka Connect, with persistence in PostgreSQL/PostGIS.

---

## 📁 Files and Structure

The project files are organized as follows:

- `stream_processor.py`: Faust microservice responsible for real-time processing of NGSIv2 notifications.
- `pg-sink-historic.json` & `pg-sink-lastdata.json`: Kafka Connect sink configurations for historical and last data storage respectively.
- `producer.py`: Example script to send NGSIv2 notifications to Kafka for testing.
- `plugins/`: Contains Kafka Connect plugin JARs (JDBC, MongoDB connectors) with specific versions.
- `tests/`: Organized test data and scripts grouped by target system (PostGIS, MongoDB).
- Docker and environment setup files (`Dockerfile`, `docker-compose.yml`, etc.) for easy deployment.

This clear separation aids maintainability and onboarding.

---

## 🧠 Key Concepts

### 🔹 NGSIv2 Notifications and `producer.py`

- `.json` files such as `accesscount_notification.json` and `parking_notification.json` contain examples of NGSIv2-style notifications.
- These notifications are sent to the Kafka `raw_notifications` topic using the `producer.py` script.
- The script requires the `kafka-python` library installed, which you can use within the `kafka-faust-env` virtual environment.

---

### 🔹 Plugins

The `plugins/` directory includes the `.jar` for the custom JDBC and MongoDB connector required for Kafka Connect. These are mounted in the container using a volume.

**Important:** If you change the project structure, be sure to update this line in `docker-compose.yml`:

```
volumes:
- ./plugins:/etc/kafka-connect/plugins
```

---

## 🏗️ System Architecture

### Data Flow Overview

1. NGSIv2 notifications are produced to Kafka topic `raw_notifications`.
2. Faust microservice (`stream_processor.py`) consumes these messages, enriching them by:
   - Adding `recvtime` timestamps.
   - Transforming geographical attributes (e.g., `geo:point`, `geo:polygon`, `geo:json`) into PostGIS-compatible WKB.
   - Serializing json attributes.
   - Building needed kafka schema for the jdbc-connector.
3. Processed messages are emitted to dynamically named Kafka topics based on service, entity type, and data type (DM logic of Cygnus).
4. Kafka Connect sinks subscribe to these topics:
   - Historical sink inserts full records with composite keys (`entityid`, `timeinstant`).
   - Last data sink upserts records keyed by `entityid` only.
5. Data is persisted in PostgreSQL/PostGIS accordingly.

### Key Benefits

- Faust replaces Cygnus for NGSI processing, providing greater flexibility and control.
- Clear separation of last data and historical data streams allows optimized storage and querying.
- Dynamic topic and key generation based on message metadata simplifies scaling.

---

## 🔄 Faust Stream Processing Details

The Faust microservice performs the following steps per incoming message:

- **Message Parsing:** Receives NGSIv2 notifications with headers and JSON body.
- **Last Data Detection:** Checks header `lastdata` to differentiate processing mode.
- **Topic Normalization:** Builds output topic name based on `fiware-servicepath`, `entityType`, and lastdata flag, sanitized for Kafka compatibility.
- **Attribute Processing:**
  - Infers Kafka Connect types from NGSI attribute types or Python native types.
  - Formats date/time attributes to ISO 8601 UTC with millisecond precision.
  - Serializes embedded JSON attributes.
  - Converts spatial attributes (`geo:point`, `geo:polygon`, `geo:json`) to WKB with Debezium-compatible schema.
- **Kafka Key Construction:** Builds a schema-aware key including `entityid` and optionally `timeinstant` for upsert operations.
- **Message Emission:** Sends key/value pair to the appropriate Kafka topic with full schema for downstream sinks.
- **Error Handling:** Logs formatting or serialization issues without dropping messages.

The processing design is extensible to support additional NGSI attribute types and spatial formats with minimal changes.

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

3. **Register the connectors in Kafka Connect**
There are two types of sinks, one for historic tables (insert functionality) and one for lastdata tables (upsert functionality):

```bash
curl -X POST http://localhost:8083/connectors \
-H "Content-Type: application/json" \
--data @pg-sink-historic.json
```

```bash
curl -X POST http://localhost:8083/connectors \
-H "Content-Type: application/json" \
--data @pg-sink-lastdata.json
```

4. **Send NGSIv2 notifications** to the raw topic:
For this part, you need the Kafka Python library. Using a Python virtual environment is recommended.

```bash
python producer.py accesscount_notification.json
```

If a topic needs to be checked because changes in message processing cause errors, you can do so with this command:

```bash
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic TOPIC_NAME --from-beginning --max-messages 10
```

---