# kafnus
# csv-source-custom-postgres-sink-kafka-connect

Demo of how to stream CSV file to Kafka and use a custom sink Postgres connector. 

## Data

The data used here is a MP3 playlist metadata. These CSV files are in `data` folder.

## Components

The following technologies are used through Docker containers:
* Kafka, the streaming platform
* Kafka's schema registry, needed to use the Avro data format
* Kafka Connect, to orchestrate csv file source and Postgres sink.
* Postgres, pulled from [Debezium](https://debezium.io/), tailored for use with Connect
* [Java 11+](https://openjdk.java.net)
* [Apache Maven](https://maven.apache.org)

The containers are pulled directly from official Docker Hub images.
The Connect image used here needs some additional packages, some of them from `libs` folder, so it must be built from the 
included Dockerfile.

## ⚙️ Building components

### Build the Kafka Connect image
```
docker build -t connector -f connector.Dockerfile .
```

### Create volume for Postgres
```
docker volume create postgresdata
```

### Build the custom Postgres sink Kafka Connect
```
mvn clean package
```

💡 A file named `target/postgres-sink-kafka-connector-1.0.jar` will be created. This is your Postgres sink connector for Kafka Connect.


## ⬆️ Bring up the environment

```
docker-compose up -d --build
```

### Prepare Postgres database

We will bring up a container with a psql command line, mount our local data
files inside and create a database called `musics` with `playlist` table.

```
docker exec -it postgres psql -U postgres
```

At the command line:

```
CREATE DATABASE musics;
\connect musics;
CREATE TABLE playlist
(album VARCHAR(256), track VARCHAR(256), performer VARCHAR(256),
CONSTRAINT playlist_pk PRIMARY KEY (album, track));
```

Execute `exit;` command to disconnect from Postgres.

### Using CSV file as source for Kafka

We will copy CSV data to Kafka container.

```
docker cp data/playlist.csv connect:/tmp/data/input
```

The `csv-source.json` file contains the configuration settings needed to
sink CSV file content to Kafka.

```
curl -X POST -H "Accept:application/json" -H "Content-Type: application/json" \
      --data @csv-source.json http://localhost:8083/connectors
```

The connector `csv-spooldir-connector` should show up when curling for the list
of existing connectors:

```
curl -H "Accept:application/json" localhost:8083/connectors/
```

The csv data now show up as topic in Kafka.
You can check this by entering the Kafka container:

```
docker exec -it kafka /bin/bash
```

and viewing the topic:

```
kafka-console-consumer --bootstrap-server localhost:9092 --topic playlist-topic --from-beginning
```

Execute `exit` command to disconnect from Docker.


### Add a custom connector to sink topic to Postgres

The `postgres-sink.json` configuration file will create the `playlist`
table and send the data to Postgres.

```
curl -X POST -H "Accept:application/json" -H "Content-Type: application/json" \
      --data @postgres-sink.json http://localhost:8083/connectors
```

Bring up once again the container with a psql command line:

```
docker exec -it postgres psql -U postgres
```

At the command line:

```
\connect musics;
SELECT * FROM playlist;
```

This command should return 10 rows. Execute `exit;` command to disconnect from Postgres.

## ⏹ Undeploy the connector

Use the following commands to undeploy the connectors from Kafka Connect:

```
curl -X DELETE http://localhost:8083/connectors/csv-spooldir-connector

curl -X DELETE http://localhost:8083/connectors/postgres-sink-connector
```

## ⬇️ Stopping the local environment

Stop the containers using Docker Compose.

```
docker compose down
```

## 🪲 Debugging the connector

This is actually an optional step, but if you wish to debug the connector code to learn its behavior by watching the code executing line by line, you can do so by using remote debugging. The Kafka Connect container created in the Docker Compose file was changed to rebind the port **8888** to enable support for [JDWP](https://en.wikipedia.org/wiki/Java_Debug_Wire_Protocol). The instructions below assume that you are using [Visual Studio Code](https://code.visualstudio.com) for debugging. However, most IDEs for Java should provide support for JDWP. Please check their documentation manuals about how to attach their debugger to the remote process.

1. Create a file named `.vscode/launch.json` with the following content:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Connector",
            "type": "java",
            "request": "attach",
            "hostName": "localhost",
            "port": 8888
        }
    ]
}
```

2. Set one or multiple breakpoints throughout the code.
3. Bring up the environment.
4. Launch a new debugging session to attach to the container.
5. Play with the connector to trigger the live debugging.
