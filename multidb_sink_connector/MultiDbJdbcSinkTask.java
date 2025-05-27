package com.example.kafka.connect.jdbc;

import org.apache.kafka.connect.errors.ConnectException;
import org.apache.kafka.connect.sink.SinkRecord;
import org.apache.kafka.connect.sink.SinkTask;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class MultiDbJdbcSinkTask extends SinkTask {
    private static final Logger log = LoggerFactory.getLogger(MultiDbJdbcSinkTask.class);

    private MultiDbJdbcSinkConfig config;
    private final Map<String, DatabaseWriter> databaseWriters = new ConcurrentHashMap<>();
    private ConnectionPoolManager poolManager;

    @Override
    public String version() {
        return "1.0";
    }

    @Override
    public void start(Map<String, String> props) {
        try {
            config = new MultiDbJdbcSinkConfig(props);
            poolManager = new ConnectionPoolManager(config);
            log.info("Started MultiDbJdbcSinkTask");
        } catch (Exception e) {
            throw new ConnectException("Couldn't start MultiDbJdbcSinkTask due to configuration error", e);
        }
    }

    @Override
    public void put(Collection<SinkRecord> records) {
        if (records.isEmpty()) {
            return;
        }

        // Group records by database
        Map<String, Collection<SinkRecord>> recordsByDatabase = new HashMap<>();
        for (SinkRecord record : records) {
            String databaseName = extractDatabaseName(record.topic());
            recordsByDatabase.computeIfAbsent(databaseName, k -> new ArrayList<>()).add(record);
        }

        // Process each database group
        recordsByDatabase.forEach((databaseName, dbRecords) -> {
            try {
                DatabaseWriter writer = databaseWriters.computeIfAbsent(databaseName, k -> {
                    try {
                        return new DatabaseWriter(databaseName, poolManager);
                    } catch (SQLException e) {
                        throw new ConnectException("Failed to create writer for database " + databaseName, e);
                    }
                });
                writer.write(dbRecords);
            } catch (Exception e) {
                log.error("Failed to write records to database {}", databaseName, e);
                throw new ConnectException("Failed to write records to database " + databaseName, e);
            }
        });
    }

    private String extractDatabaseName(String topic) {
        int underscoreIndex = topic.indexOf('_');
        if (underscoreIndex == -1) {
            throw new ConnectException("Topic name must follow the pattern 'databaseName_tableName'");
        }
        return topic.substring(0, underscoreIndex);
    }

    @Override
    public void stop() {
        try {
            databaseWriters.values().forEach(DatabaseWriter::close);
            poolManager.closeAll();
            log.info("Stopped MultiDbJdbcSinkTask");
        } catch (Exception e) {
            log.error("Error while stopping the task", e);
        }
    }
}
