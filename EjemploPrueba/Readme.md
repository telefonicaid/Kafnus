# 🔄 NGSI Kafka Stream Processor

Este proyecto implementa una arquitectura ligera de procesamiento de notificaciones NGSIv2 usando Kafka, Faust y Kafka Connect, con persistencia en PostgreSQL/PostGIS.

---

## 📁 Archivos y estructura

```
.
├── accesscount_notification.json       # Notificación tipo NGSIv2 (accesos)
├── parking_notification.json           # Notificación tipo NGSIv2 (parking)
├── pg-sink-historic.json               # Conector JDBC para almacenar históricos
├── pg-sink-lastdata.json               # Conector JDBC para último valor
├── producer.py                         # Script para enviar notificaciones NGSIv2 a Kafka
├── stream_processor.py                 # Microservicio Faust que procesa notificaciones crudas
├── requirements.txt                    # Dependencias Python (incluye Faust y Kafka)
├── Dockerfile                          # Imagen para ejecutar Faust
├── docker-compose.yml                  # Servicios de Kafka, Connect, etc.
├── docker-compose.override.yml         # Ajustes adicionales para entornos locales
├── kafka-faust-env/                    # Entorno virtual Python para ejecutar Faust
└── plugins/                            # Conector Kafka personalizado (JDBC, MongoDB, etc.)
```

---

## 🧠 Conceptos clave

### 🔹 Notificaciones NGSIv2 y `producer.py`

- Los ficheros `.json` como `accesscount_notification.json` y `parking_notification.json` contienen ejemplos de notificaciones estilo NGSIv2.
- Estas notificaciones se envían al tópico Kafka `raw_notifications` mediante el script `producer.py`.
- El script requiere tener instalada la librería `kafka-python`, que puedes usar dentro del entorno virtual `kafka-faust-env`.

---

### 🔹 Arquitectura del sistema

- **Kafka + Kafka Connect** se encargan de la infraestructura de streaming y la integración con sistemas externos.
- **Faust (`stream_processor.py`)** es un microservicio tipo Kafka Stream que sustituye la lógica de Cygnus:
  - Procesa las notificaciones NGSIv2 del tópico `raw_notifications`.
  - Añade automáticamente el campo `recvtime`.
  - Transforma geometrías `geo:*` (como `geo:point`, `geo:polygon`) en estructuras serializables compatibles con PostGIS (WKB).
  - Construye mensajes con esquema Kafka Connect para facilitar la integración JDBC.
- **PostGIS** se levanta como servicio aparte y sirve como destino de los datos persistidos.

---

### 🔹 Plugins

En el directorio `plugins/` está incluido el `.jar` del conector personalizado JDBC y MongoDB necesario para Kafka Connect. Estos se montan en el contenedor mediante un volumen.

**Importante:** si cambias la estructura del proyecto, asegúrate de actualizar esta línea en el `docker-compose.yml`:

```
volumes:
  - ./plugins:/etc/kafka-connect/plugins
```

---

## 🧪 Cómo ejecutarlo

1. **Levanta PostGIS por separado**  
   Puedes usar un contenedor o tu instalación local.

2. **Levanta Kafka y Kafka Connect**  
   Con el siguiente comando desde la raíz del proyecto:

   ```bash
   docker-compose up -d
   ```

3. **Levanta el microservicio Faust**  
   Puedes hacerlo desde el entorno virtual (recuerda tener las dependencias instaladas):

   ```bash
   source kafka-faust-env/bin/activate
   faust -A stream_processor worker -l info
   ```

4. **Registra los conectores en Kafka Connect**  
   Por ahora solo se ha probado el conector de históricos:

   ```bash
   curl -X POST http://localhost:8083/connectors \
        -H "Content-Type: application/json" \
        --data @pg-sink-historic.json
   ```

5. **Envía notificaciones NGSIv2** al tópico crudo:

   ```bash
   python producer.py accesscount_notification.json
   ```

---

## 🛠️ Mejoras pendientes

- ✅ Procesar `application/json` como `attrValue` (no solo string).
- ✅ Soporte para geometrías más complejas como `geo:json`.
- ⚠️ **Error conocido:** Si Faust crea un tópico nuevo y aún no hay particiones disponibles, es posible que no se conecte correctamente. En ese caso, basta con cerrar y volver a lanzar el servicio Faust.
- 🕒 Mejorar el tratamiento y normalización de fechas (e.g. `timeinstant`, zonas horarias).
- ➕ Incluir `fiware-servicepath` en el payload procesado (actualmente solo se usa para el nombre del tópico, pero no se guarda en el mensaje resultante).
