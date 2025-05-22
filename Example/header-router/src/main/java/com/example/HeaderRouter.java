package com.example;

import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.connect.connector.ConnectRecord;
import org.apache.kafka.connect.transforms.Transformation;
import org.apache.kafka.connect.transforms.util.SimpleConfig;

import java.util.Map;

public class HeaderRouter<R extends ConnectRecord<R>> implements Transformation<R> {

    public static final String HEADER_KEY_CONFIG = "header.key";
    public static final String TOPIC_PREFIX_CONFIG = "topic.prefix";

    private static final ConfigDef CONFIG_DEF = new ConfigDef()
        .define(HEADER_KEY_CONFIG, ConfigDef.Type.STRING, ConfigDef.Importance.HIGH, "Header key to use for routing")
        .define(TOPIC_PREFIX_CONFIG, ConfigDef.Type.STRING, "", ConfigDef.Importance.LOW, "Prefix for target topic");

    private String headerKey;
    private String topicPrefix;

    @Override
    public void configure(Map<String, ?> configs) {
        SimpleConfig config = new SimpleConfig(CONFIG_DEF, configs);
        this.headerKey = config.getString(HEADER_KEY_CONFIG);
        this.topicPrefix = config.getString(TOPIC_PREFIX_CONFIG);
    }

    @Override
    public R apply(R record) {
        if (record.headers() == null) return record;

        String newTopic = null;
        if (record.headers().lastWithName(headerKey) != null) {
            Object headerValue = record.headers().lastWithName(headerKey).value();
            if (headerValue != null) {
                newTopic = topicPrefix + headerValue.toString();
            }
        }

        if (newTopic != null && !newTopic.isEmpty()) {
            return record.newRecord(
                newTopic,
                record.kafkaPartition(),
                record.keySchema(),
                record.key(),
                record.valueSchema(),
                record.value(),
                record.timestamp(),
                record.headers()
            );
        }

        return record;
    }

    @Override
    public ConfigDef config() {
        return CONFIG_DEF;
    }

    @Override
    public void close() {
        // Nothing to close
    }
}
