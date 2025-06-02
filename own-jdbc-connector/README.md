# How to Build the Custom Kafka Connect JDBC Sink with PostGIS Support

This guide explains how to compile the Kafka Connect JDBC Sink connector with geometry (PostGIS) support, based on the version `v10.7.0` of *Confluent JDBC Connector* and applying [PR #1048](https://github.com/confluentinc/kafka-connect-jdbc/pull/1048).

---

## 🛠️ Step 1: Clone the repo and apply the PR

### 🧬 1.1 Clone the official repo

```bash
git clone https://github.com/confluentinc/kafka-connect-jdbc.git
cd kafka-connect-jdbc
```

### 🏷️ 1.2 Checkout the stable version v10.7.0

```bash
git checkout v10.7.0
```

> ✅ Kafka Connect 7.9.0 uses `kafka-connect-jdbc` v10.7.x

### 🌿 1.3 Create a new branch

```bash
git checkout -b geometry-support-based-on-10.7.0
```

### 📦 1.4 Apply the custom patch from this repo

This repo includes a pre-generated [patch file](/own-jdbc-connector/postgis-support.patch) containing the PostGIS geometry support. Apply it like this:

```bash
 git apply postgis-support.patch
```

> 💡 Make sure you're applying it from within the kafka-connect-jdbc directory, and that the patch file is there (or adjust the path accordingly if it’s in a different location).

### 1.5 Commit the changes

```bash
git add .
git commit -m "Add PostGIS geometry support from custom patch"
```

---

## 🔧 Step 2: Build the connector JAR

Skip checkstyle and tests (they're not needed):

```bash
mvn clean package -DskipTests -Dcheckstyle.skip=true
```

If successful, you’ll get a `.jar` file like:

```
target/kafka-connect-jdbc-10.7.0.jar
```

---

## ⚠️ Java version compatibility

If you see this error:
```
error: release version 8 not supported
```

It means your Java compiler doesn’t support the `--release 8` flag.

### ✅ Recommended: Use Java 8

Check current Java version:

```bash
javac -version
```

If it's not Java 8, switch to it. Example with SDKMAN:

```bash
sdk install java 8.0.392-tem
sdk use java 8.0.392-tem
```

Or in Ubuntu:

```bash
sudo apt install openjdk-8-jdk
sudo update-alternatives --config java
sudo update-alternatives --config javac
```

Or force it for Maven:

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

Then:

```bash
javac -version
mvn -version
```

> **Note**: It has been successfully built the project using OpenJDK 17.0.15 (2025-04-15). While Java 8 remains the officially recommended version for compatibility, newer versions like Java 17 may work depending on your environment.

---

## ✅ Step 3: Deploy and verify the connector

Copy the compiled JAR into the Kafka Connect classpath.

Then verify the connector is loaded (after deploying `kafka-connector` service):

```bash
curl -s http://localhost:8083/connector-plugins | jq
```

You should see:

```json
{
  "class": "io.confluent.connect.jdbc.JdbcSinkConnector",
  "type": "sink",
  "version": "10.7.0"
}
```

---
# How to use the Custom Connector

## 🌍 Send geometry data (WKB) to Kafka

Kafka Connect expects geometries using WKB + SRID in this schema:

```json
{
  "schema": {
    "type": "struct",
    "fields": [
      {"field": "entityid", "type": "string"},
      {"field": "timeinstant", "type": "string"},
      {
        "field": "geom",
        "name": "io.debezium.data.geometry.Geometry",
        "type": "struct",
        "fields": [
          {"field": "wkb", "type": "bytes"},
          {"field": "srid", "type": "int32"}
        ]
      }
    ],
    "optional": false
  },
  "payload": {
    "entityid": "some-id",
    "timeinstant": "2025-05-13T18:00:00.000Z",
    "geom": {
      "wkb": "AQEAAAD/////AA==",
      "srid": 4326
    }
  }
}
```

> The connector uses `io.debezium.data.geometry.Geometry` as the field schema type, this is what the [PR #1048](https://github.com/confluentinc/kafka-connect-jdbc/pull/1048) included.
> 💡 WKB should be Base64 encoded if you're using JSON serialization.

---

## 🧪 Convert WKT to WKB in Python

As implemented in the `faust` service, you can generate WKB using Python + Shapely:

```python
from shapely import wkt
import base64

def wkt_to_wkb_base64(wkt_str):
    geom = wkt.loads(wkt_str)
    return base64.b64encode(geom.wkb).decode("ascii")

print(wkt_to_wkb_base64("POINT(-3.7038 40.4168)"))
```

---
# 🔍 Explanation of the Changes

This custom build integrates support for **geospatial geometry data** in Kafka Connect JDBC Sink, based on the changes proposed in [PR #1048](https://github.com/confluentinc/kafka-connect-jdbc/pull/1048). Below is a breakdown of what this patch does and why it was necessary.

---

## 📐 Geometry Support (from PR #1048)

The primary goal of the patch is to allow the JDBC Sink connector to recognize and handle geometry objects encoded in the **Debezium-style format**, specifically:

``` bash
{
  "name": "io.debezium.data.geometry.Geometry",
  "type": "struct",
  "fields": [
    {"field": "wkb", "type": "bytes"},
    {"field": "srid", "type": "int32"}
  ]
}
```

### ✅ What's added:

- A new `GeometryType` mapping in the JDBC dialect logic.
- The connector now recognizes fields with schema name `io.debezium.data.geometry.Geometry`.
- The sink converts this into a `java.sql.PreparedStatement` using PostGIS-compatible WKB input.

This enables **transparent writing of geospatial data** (e.g., `POINT`, `LINESTRING`, `POLYGON`) to PostgreSQL with PostGIS extensions.

> Without this change, the connector would ignore or fail to serialize geometry types coming from sources like Debezium.

---

## 🔧 `pom.xml` Fix: HTTPS for Confluent Maven Repositories

The patch also includes a fix in the `pom.xml` file to **switch Maven repository URLs from `http` to `https`** for the Confluent repositories. This solves build failures due to modern security restrictions that block HTTP-based Maven resolutions.

### Modified block:

``` bash
<repository>
  <id>confluent</id>
  <url>https://packages.confluent.io/maven/</url>
</repository>
```

This change eliminates the need for users to manually edit the POM to fix dependency resolution errors. It also adds `<debezium.version>1.5.0.Final</debezium.version>` in dependencies.

---

## 🧵 Summary of the Patch

The patch (`postgis-support.patch`) includes:

- ✅ Code changes from [PR #1048](https://github.com/confluentinc/kafka-connect-jdbc/pull/1048) to support geometry types.
- ✅ A `pom.xml` update to enforce HTTPS for Confluent Maven repos.

---

# ✅ Conclusion

You now have:

- A compiled Kafka Connect JDBC Sink with PostGIS (WKB) support
- Geometry data flowing in binary-safe format
- Compatibility with Debezium-style geometry schema

You're ready to send geospatial data to PostgreSQL/PostGIS via Kafka Connect!
