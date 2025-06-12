package com.telefonica.kafka.connect.jdbc;

import org.apache.kafka.connect.errors.ConnectException;
import org.apache.kafka.connect.sink.SinkRecord;
import org.apache.kafka.connect.sink.SinkTask;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.SQLException;
import java.util.*;

public class MultiDbJdbcSinkTask extends SinkTask {
    private static final Logger log = LoggerFactory.getLogger(MultiDbJdbcSinkTask.class);

    private MultiDbJdbcSinkConfig config;
    private ConnectionPoolManager connectionPoolManager;
    private final Map<String, DatabaseWriter> dbWriters = new HashMap<>();

    @Override
    public String version() {
        return "1.0.0";
    }

    @Override
    public void start(Map<String, String> props) {
        config = new MultiDbJdbcSinkConfig(props);
        connectionPoolManager = new ConnectionPoolManager(config);
        log.info("Starting MultiDbJdbcSinkTask with configuration: {}", config);
    }

    @Override
    public void put(Collection<SinkRecord> records) {
        if (records.isEmpty()) {
            return;
        }

        // Group records by database
        Map<String, List<SinkRecord>> recordsByDb = new HashMap<>();
        for (SinkRecord record : records) {
            String[] dbAndTable = parseTopic(record.topic());
            String dbName = dbAndTable[0];
            recordsByDb.computeIfAbsent(dbName, k -> new ArrayList<>()).add(record);
        }

        // Process each database group
        recordsByDb.forEach((dbName, dbRecords) -> {
            try {
                DatabaseWriter writer = dbWriters.computeIfAbsent(dbName, k -> {
                    try {
                        return new DatabaseWriter(dbName, connectionPoolManager, config);
                    } catch (SQLException e) {
                        throw new ConnectException("Failed to initialize writer for database: " + dbName, e);
                    }
                });
                writer.write(dbRecords);
            } catch (Exception e) {
                log.error("Failed to write records to database: {}", dbName, e);
                throw new ConnectException("Failed to write records to database: " + dbName, e);
            }
        });
    }

    private String[] parseTopic(String topic) {
        String separator = config.getTopicDbSeparator();
        String[] parts = topic.split(separator, 2);
        if (parts.length != 2) {
            throw new ConnectException(String.format(
                "Topic name '%s' doesn't match expected format: <dbName>%s<tableName>", 
                topic, separator));
        }
        return parts;
    }

    @Override
    public void stop() {
        log.info("Stopping MultiDbJdbcSinkTask");
        dbWriters.values().forEach(DatabaseWriter::close);
        connectionPoolManager.closeAll();
    }
}
