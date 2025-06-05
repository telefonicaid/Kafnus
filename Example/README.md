# NGSI Kafka Stream Processor for FIWARE Smart Cities

This project replaces Cygnus with a Kafka-based architecture for processing NGSIv2 notifications. It features Faust stream processing and persistence to PostgreSQL/PostGIS via Kafka Connect.

There is an [Installation Guide](/Example/Doc/InstallationGuide.md) avaible.

---

## Project Structure

The project files are organized as follows:

```plaintext
.
├── docker/                      # Docker files and service configurations
│   ├── docker-compose.yml
│   ├── docker-compose.override.yml
│   └── Dockerfile
├── src/                         # Source code for the modularized Faust processor
│   ├── app/
│   │   ├── agents.py
│   │   ├── config.py
│   │   ├── entity_handler.py
│   │   ├── faust_app.py
│   │   ├── kafka_utils.py
│   │   ├── metrics.py
│   │   ├── types_utils.py
│   │   └── __init__.py
│   ├── stream_processor.py      # Main entry point (can be executed directly)
│   └── requirements.txt
├── plugins/                     # Custom connectors and libraries
│   ├── kafka-connect-jdbc-10.7.0/
│   ├── mongodb/
│   └── header-router-1.0.0.jar
├── header-router/               # Java source code for the custom SMT
│   └── src/main/java/com/example/HeaderRouter.java
├── sinks/                       # Kafka Connect sink configurations
├── tests/                       # Test scripts and sample notifications
├── monitoring/                  # Prometheus/Grafana dashboards and config
├── Doc/                         # Documentation and images
└── README.md
```

---

## Core Architecture

### Data Flow

This part is for postgis cases, mongo cases are documented apart.

1. **Ingestion**: 
   - Context Broker sends raw NGSIv2 notifications to Kafka topics (one per flow: `historic`, `lastdata`, `mutable`).
For now, this step is simulated using this [Python producer script](/Example/tests/postgis/producer.py) .
   
2. **Processing**:
   - Faust agents (`stream_processor.py`) transform messages by:
     - Adding `recvtime` timestamps
     - Converting geo-formats to PostGIS WKB
     - Building JDBC-compatible schemas
     - Routing to client-specific topics
   - The processed messages are then sent to a new Kafka topic, with the target table specified in the message headers.

3. **Persistence**:
   - Custom Kafka Connect JDBC sinks (with PostGIS support) write to:
     - Historical tables
     - Last data tables
     - Mutable tables
     - Error table.
   - A custom SMT is used to change the name of the topic to target table.

The following image shows a simplified architecture for a single data flow:
![Simplified Arquitecture Schema](/Example/Doc/SimplifiedSchema.png)

Here we can check the full schema for postgis data:
![Full Arquitecture Schema](/Example/Doc/FullSchema.png)

---

## 🧠 Key Concepts

### 🔹 NGSIv2 Notifications and `producer.py`

- JSON files such as [accesscount_access_notification.json](/Example/tests/postgis/001_basic_historic/accesscount_access_notification.json) and [parking_zone_notification.json](/Example/tests/postgis/003_geometries/parking_zone_notification.json) contain examples of NGSIv2-style notifications.
- These notifications are sent to the Kafka raw topics (for example `raw_historic`) using the [producer.py](/Example/tests/postgis/producer.py) script.
- The script requires the `kafka-python` library to be installed. Using a virtual environment is highly recommended and describe it in [Installation Guide](/Example/Doc/InstallationGuide.md).


### 🔹 Plugins

Kafka Connect supports **plugins** to extend its default functionality. A plugin is typically a `.jar` (or set of `.jar`s) that adds support for additional connectors (like JDBC or MongoDB), transforms (SMTs), converters, etc. If it's you first time, you can find information about how to get this plugins in the [Installation Guide](/Example/Doc/InstallationGuide.md).

This project uses **three plugin types**:

---

#### 🔸 1. Kafka Connect JDBC (PostGIS-ready)

Located in: `plugins/kafka-connect-jdbc-10.7.0/`

This includes:

- `kafka-connect-jdbc-10.7.0.jar`: The main JDBC sink connector.
- `postgresql-42.7.1.jar`: The PostgreSQL driver required for connectivity and PostGIS compatibility.

This connector is used in the **PostGIS sinks** (`pg-sink-historic.json`, `pg-sink-lastdata.json`, etc.)

---

#### 🔸 2. Kafka Connect MongoDB

Located in: `plugins/mongodb/`

This includes:

- `kafka-connect-mongodb-1.10.0.jar`: MongoDB sink connector.
- All required MongoDB driver dependencies.

> **Note**: MongoDB support is still under development in this project.

---

#### 🔸 3. Custom SMT: HeaderRouter

Located in: `plugins/header-router-1.0.0.jar`

Kafka Connect allows the use of **Single Message Transforms (SMTs)** to modify records before writing to the sink. This project includes a **custom SMT** written in Java (`HeaderRouter.java`), which dynamically reroutes records based on Kafka headers (set by the Faust processor).

**Purpose**: Routes records to different topics based on a Kafka header key.

**How it works**:
- Reads a header (e.g., `target_table`)
- Change the topic value to header value.
- It does not create a new topic.

##### SMT Configuration Example:

In sink configuration, this **custom SMT** is added as follows:

```json
"transforms": "HeaderRouter,...",
"transforms.HeaderRouter.type": "com.example.HeaderRouter",
"transforms.HeaderRouter.header.key": "target_table",
```

---


## 🔄 Faust Stream Processing Details

This project uses [Faust](https://faust.readthedocs.io/en/latest/) to process NGSI-style Kafka messages in real time, transforming them into Kafka Connect-compatible records for downstream sinks like PostgreSQL (PostGIS) or MongoDB.

---

### 🧠 Core Concepts

- **App name**: `ngsi-processor`
- **Broker**: Connects to Kafka at `kafka://kafka:9092`
- **Serialization**: Messages are deserialized as `raw` (byte strings)
- **Input topics**: `raw_historic`, `raw_lastdata`, `raw_mutable`
- **Error topic**: `postgis_errors`

---

### 🛠️ Entity Processing Pipeline

The core logic is in `handle_entity()`:

1. **Decode & parse** NGSI-style messages from Kafka.
2. **Extract headers** (e.g. Fiware service/path).
3. **Transform attributes**:
   - Converts `geo:*` attributes to WKB (well-known binary) for PostGIS.
   - Infers Kafka Connect field types from `attrType` or Python types.
4. **Construct Kafka Connect schema** with `schema` + `payload`.
5. **Send** to an output Kafka topic with dynamic name based on headers.

SMT routing is supported by setting the `target_table` Kafka header.

---

### 📌 Topics Handled

#### 🔹 `raw_historic`
- Every record is processed regardless of timestamp.
- Output topic: `<service>`

#### 🔹 `raw_lastdata`
- Only newer records (by `TimeInstant`) are processed per entity.
- Maintains a Faust Table `last_seen_timestamps`.
- Output topic: `<service>_lastdata`

#### 🔹 `raw_mutable`
- Still in progress.
- Published to `<service>_mutable`.

#### 🔹 `postgis_errors`
Handles Kafka Connect DLQ messages for failed inserts:

- Extracts error message, SQL query, and target table.
- Formats it as a Kafka Connect record.
- Sends it to a topic like: `<dbname>_error_log`

---

### 🌍 Geometry Conversion

```python
def to_wkt_geometry(attr_type, attr_value):
    ...
def to_wkb_struct_from_wkt(wkt_str, field_name, srid=4326):
    ...
```

Geo attributes like `geo:point`, `geo:polygon`, and `geo:json` are converted into **WKT** then **WKB**, encoded as base64, and wrapped in a Debezium-compatible structure.

---

### 🔑 Kafka Keys

```python
def build_kafka_key(entity, include_timeinstant=True):
    ...
```

Each record uses a JSON-encoded key with `entityid` and optionally `timeinstant`, for upsert mode compatibility.

---

### 📅 Timestamps

- All records include `recvtime` (ISO 8601 in UTC).
- `TimeInstant` is extracted and formatted.
- Older records (in `raw_lastdata`) are ignored based on `last_seen_timestamps`.

---

### 🐞 Error Handling

When a DB insert fails in Kafka Connect:

- The DLQ message is parsed.
- SQL query and error message are extracted or reconstructed.
- The structured error record is sent to an `error_log` topic for the relevant DB/table.

Example output schema:

```json
{
  "timestamp": "2025-05-28T09:00:00Z",
  "error": "ERROR: duplicate key value violates unique constraint",
  "query": "INSERT INTO ..."
}
```

---

## 🧪  How to Run the System (with docker)

> Remember that before run it, you will need to get the correct plugins for kafka connector.
> To execute this commands you must be in docker folder.

1. **Set up PostGIS separately**
You can use a container or a local installation.  Note that, for now, you must manually create the required databases, schemas, and tables.

2. **Start services with docker**
The Docker file is already configured, so you don’t need to follow a detailed setup process. If everything works correctly, simply run the following command from the project root:

```bash
docker compose up
```

Wait until all services have been deployed, you can know it is ready when Kafka-Connect logs messages like this:

```bash
kafka-connect           | [2025-05-28 06:39:43,597] INFO [0:0:0:0:0:0:0:1] - - [28/May/2025:06:39:43 +0000] "GET /connectors HTTP/1.1" 200 2 "-" "curl/7.61.1" 13 (org.apache.kafka.connect.runtime.rest.RestServer)
```

3. **Register the connectors in Kafka Connect**
For PostGIS, There are four types of sinks, one for historic tables (insert functionality), one for lastdata tables (upsert functionality), one for mutable tables (upsert functionality) and one for errors. From sinks folder, you have to launch the following commands:

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

```bash
curl -X POST http://localhost:8083/connectors \
-H "Content-Type: application/json" \
--data @pg-sink-mutable.json
```

```bash
curl -X POST http://localhost:8083/connectors \
-H "Content-Type: application/json" \
--data @pg-sink-erros.json
```

4. **Send NGSIv2 notifications** to the raw topic:
For this part, you need the Kafka Python library. Using a Python virtual environment is recommended.

```bash
python producer.py tests/postgis/003_geometries/parking_zone_notification.json
```

The producer will log a message and in faust service you will see logs about receiving, processing and sending to processed topic.
```
faust-stream            | [2025-05-28 06:54:16,714] [1] [WARNING] ✅ [_lastdata] Sent to topic 'alcobendas_lastdata': NPO-101 
```

If everything works correctly, Kafka Connect will show logs of connecting and persisting data in PostGIS.

```bash
kafka-connect           | [2025-05-28 06:57:51,334] INFO Attempting to open connection #1 to PostgreSql (io.confluent.connect.jdbc.util.CachedConnectionProvider)
kafka-connect           | [2025-05-28 06:57:51,529] INFO Maximum table name length for database is 63 bytes (io.confluent.connect.jdbc.dialect.PostgreSqlDatabaseDialect)
kafka-connect           | [2025-05-28 06:57:51,529] INFO JdbcDbWriter Connected (io.confluent.connect.jdbc.sink.JdbcDbWriter)
kafka-connect           | [2025-05-28 06:57:51,572] INFO Checking PostgreSql dialect for existence of TABLE "alcobendas"."accesscount_access_lastdata" (io.confluent.connect.jdbc.dialect.GenericDatabaseDialect)
kafka-connect           | [2025-05-28 06:57:51,591] INFO Using PostgreSql dialect TABLE "alcobendas"."accesscount_access_lastdata" present (io.confluent.connect.jdbc.dialect.GenericDatabaseDialect)
kafka-connect           | [2025-05-28 06:57:51,648] INFO Checking PostgreSql dialect for type of TABLE "alcobendas"."accesscount_access_lastdata" (io.confluent.connect.jdbc.dialect.GenericDatabaseDialect)
kafka-connect           | [2025-05-28 06:57:51,654] INFO Setting metadata for table "alcobendas"."accesscount_access_lastdata" to ...
```

If a topic needs to be checked, for example because changes in message processing cause errors, you can do so with this command:

```bash
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic TOPIC_NAME --from-beginning --max-messages 10
```

---

## Testing & Validation

This part will be documented later.

---