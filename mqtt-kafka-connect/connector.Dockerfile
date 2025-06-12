# Use the official Confluent Kafka Connect image
FROM confluentinc/cp-kafka-connect

ENV CONNECT_PLUGIN_PATH=/usr/share/java \
    CONNECT_PLUGIN_KAFKA=/usr/share/java/kafka

# Setup SpoolDir Connector
RUN mkdir -p /tmp/data/input &&\
    mkdir /tmp/data/finished &&\
    mkdir /tmp/data/error
COPY libs/*.jar /usr/share/java/kafka

USER root
