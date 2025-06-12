package com.example.mqtt;

import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.connect.connector.Task;
import org.apache.kafka.connect.source.SourceConnector;

import java.util.Collections;
import java.util.List;
import java.util.Map;

public class MqttSourceConnector extends SourceConnector {

    private Map<String, String> configProps;

    @Override
    public void start(Map<String, String> props) {
        this.configProps = props;
    }

    @Override
    public Class<? extends Task> taskClass() {
        return MqttSourceTask.class;
    }

    @Override
    public List<Map<String, String>> taskConfigs(int maxTasks) {
        return Collections.nCopies(maxTasks, configProps);
    }

    @Override
    public void stop() {
        // Cleanup resources
    }

    @Override
    public ConfigDef config() {
        return MqttSourceConfig.configDef();
    }

    @Override
    public String version() {
        return "1.0.0";
    }
}