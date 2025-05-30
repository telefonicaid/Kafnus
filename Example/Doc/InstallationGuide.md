# 🛠️ Installation Guide – NGSI Kafka Stream Processor

This document outlines all necessary steps to **compile plugins, prepare the Python environment, download external connectors, and launch the full system**. It assumes the project is already cloned and initialized.

---

## 1. 📦 Prepare Kafka Connect Plugins

Kafka Connect requires custom and external plugins to be available **before** launching the Docker environment. These must be placed in the `./plugins` directory.

### 1.1. 🔨 Compile `HeaderRouter` (Custom SMT)

This custom SMT routes Kafka records to different topics based on a **Kafka header**.

#### Steps:

1. Navigate to the plugin's source directory:

```bash
cd header-router/
```

2. Build with Maven:

```bash
mvn clean package
```

3. The compiled JAR will be located in the `target/` directory:

```
target/header-router-1.0.0-jar-with-dependencies.jar
```

4. Move it to the plugins directory:

```bash
mv target/header-router-1.0.0-jar-with-dependencies.jar ../plugins/header-router-1.0.0.jar
```

---

### 1.2. 🧪 Compile Own JDBC Connector

This project uses a **custom JDBC connector**. Refer to the compilation guide provided in pull request [#10](https://github.com/telefonicaid/kafnus/pull/10).

After compilation, place the output in:

```
plugins/kafka-connect-jdbc-10.7.0/
```

---

### 1.3. 🧩 Download External Plugins

#### 🔹 Kafka Connect JDBC (PostgreSQL/PostGIS)

Directory: `plugins/kafka-connect-jdbc-10.7.0/`

Should include:

* `kafka-connect-jdbc-10.7.0.jar` – (custom JDBC connector)
* `postgresql-42.7.1.jar` – Required for PostgreSQL connectivity

Source:

* [PostgreSQL JDBC Driver](https://jdbc.postgresql.org/)

#### 🔹 Kafka Connect MongoDB (optional)

Directory: `plugins/mongodb/`

Should include:

* `kafka-connect-mongodb-1.10.0.jar`
* All required MongoDB dependencies

Source:

* [MongoDB Kafka Connector](https://www.confluent.io/hub/mongodb/kafka-connect-mongodb)

---

### 1.4. 🔧 Mount Plugins in Kafka Connect

This step is likely pre-configured, but ensure the following lines exist in `docker-compose.yml`:

```yaml
volumes:
  - ./plugins:/etc/kafka-connect/plugins
```

Kafka Connect must be configured to scan the plugins path:

```yaml
environment:
  CONNECT_PLUGIN_PATH: "/etc/kafka-connect/plugins"
```

---

## 2. 🐍 Set Up Python Environment (Producer & Validation Scripts)

Scripts such as `producer.py` require Python dependencies. It is recommended to use a **virtual environment**.

### Steps:

```bash

# Navigate to the tests folder (included in .gitignore)
cd tests

# Create a virtual environment
python -m venv kafka-fiware-env

# Activate (Linux/Mac)
source kafka-fiware-env/bin/activate

# Install required packages
pip install kafka-python psycopg2-binary python-dateutil shapely
```

This installs all required libraries used in the scripts, including:
- `kafka-python` for KafkaProducer
- `psycopg2-binary` for PostgreSQL/PostGIS connectivity
- `python-dateutil` for date parsing
- `shapely` for WKB handling

---

## 3. 🗕️ Create PostgreSQL Database & Tables

The system **does not automatically create** the database or tables.

Before launching:

* Ensure PostGIS is installed and enabled (can use a container).
* Create the required databases and schemas.
* Create all tables expected by the sinks (`historic`, `lastdata`, etc.).

---

## 4. 🚀 Launch the System with Docker

Once everything is in place:

```bash
docker compose up
```

Wait until all services are running. Kafka Connect will be ready when you see logs like:

```
kafka-connect | "GET /connectors HTTP/1.1" 200 ...
```

---

## 5. 🔌 Register Kafka Connectors

From the `sinks/` directory, register each connector:

```bash
curl -X POST http\://localhost:8083/connectors&#x20;
-H "Content-Type: application/json"&#x20;
\--data @pg-sink-historic.json

curl -X POST [http://localhost:8083/connectors](http://localhost:8083/connectors)&#x20;
-H "Content-Type: application/json"&#x20;
\--data @pg-sink-lastdata.json

curl -X POST [http://localhost:8083/connectors](http://localhost:8083/connectors)&#x20;
-H "Content-Type: application/json"&#x20;
\--data @pg-sink-mutable.json

curl -X POST [http://localhost:8083/connectors](http://localhost:8083/connectors)&#x20;
-H "Content-Type: application/json"&#x20;
\--data @pg-sink-errors.json
```

---

## 6. 📤 Send NGSIv2 Notifications

Use `producer.py` to send sample notifications (with virtual enviroment):

```bash
python tests/postgis/producer.py tests/postgis/003\_geometries/parking\_zone\_notification.json
```

You should see Faust logs indicating the message has been processed.

---

## 7. 🔎 Inspect Kafka Topics

To view messages in a Kafka topic:

```bash
docker exec -it kafka kafka-console-consumer
\--bootstrap-server localhost:9092
\--topic YOUR_TOPIC_NAME
\--from-beginning --max-messages 10
```

---

## ✅ Done!

At this point, you should have:

* All plugins compiled and correctly mounted
* NGSIv2 events being routed and transformed
* Kafka Connect writing to PostGIS sinks
* All tools in place for validation and debugging
