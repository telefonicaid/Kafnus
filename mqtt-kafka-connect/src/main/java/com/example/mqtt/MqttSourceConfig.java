package com.example.mqtt;

import org.apache.kafka.common.config.AbstractConfig;
import org.apache.kafka.common.config.ConfigDef;

import java.util.Map;

public class MqttSourceConfig extends AbstractConfig {
    public static final String MQTT_BROKER = "mqtt.broker";
    public static final String MQTT_TOPIC = "mqtt.topic";
    public static final String KAFKA_TOPIC = "kafka.topic";

    public MqttSourceConfig(Map<String, String> originals) {
        super(configDef(), originals);
    }

    public static ConfigDef configDef() {
        return new ConfigDef()
                .define(MQTT_BROKER, ConfigDef.Type.STRING, "tcp://localhost:1883",
                        ConfigDef.Importance.HIGH, "MQTT Broker URL")
                .define(MQTT_TOPIC, ConfigDef.Type.STRING,
                        ConfigDef.Importance.HIGH, "MQTT Topic to subscribe")
                .define(KAFKA_TOPIC, ConfigDef.Type.STRING,
                        ConfigDef.Importance.HIGH, "Destination Kafka topic");
    }
}