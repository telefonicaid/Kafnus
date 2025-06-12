package com.telefonica.kafka.connect.jdbc;

import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.connect.connector.Task;
import org.apache.kafka.connect.sink.SinkConnector;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MultiDbJdbcSinkConnector extends SinkConnector {
    private Map<String, String> configProps;

    @Override
    public String version() {
        return "1.0.0";
    }

    @Override
    public void start(Map<String, String> props) {
        configProps = props;
    }

    @Override
    public Class<? extends Task> taskClass() {
        return MultiDbJdbcSinkTask.class;
    }

    @Override
    public List<Map<String, String>> taskConfigs(int maxTasks) {
        List<Map<String, String>> taskConfigs = new ArrayList<>();
        for (int i = 0; i < maxTasks; i++) {
            taskConfigs.add(configProps);
        }
        return taskConfigs;
    }

    @Override
    public void stop() {
        // No resources to release
    }

    @Override
    public ConfigDef config() {
        return MultiDbJdbcSinkConfig.CONFIG_DEF;
    }
}
