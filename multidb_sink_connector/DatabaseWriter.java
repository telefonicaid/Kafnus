package com.example.kafka.connect.jdbc;

import org.apache.kafka.connect.data.Struct;
import org.apache.kafka.connect.errors.ConnectException;
import org.apache.kafka.connect.sink.SinkRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.*;
import java.util.Collection;

public class DatabaseWriter {
    private static final Logger log = LoggerFactory.getLogger(DatabaseWriter.class);

    private final String databaseName;
    private final ConnectionPoolManager poolManager;

    public DatabaseWriter(String databaseName, ConnectionPoolManager poolManager) throws SQLException {
        this.databaseName = databaseName;
        this.poolManager = poolManager;
        // Test connection on creation
        try (Connection connection = poolManager.getConnection(databaseName)) {
            log.info("Successfully connected to database: {}", databaseName);
        }
    }

    public void write(Collection<SinkRecord> records) {
        if (records.isEmpty()) {
            return;
        }

        try (Connection connection = poolManager.getConnection(databaseName)) {
            connection.setAutoCommit(false);

            for (SinkRecord record : records) {
                String tableName = extractTableName(record.topic());
                writeRecord(connection, tableName, record);
            }

            connection.commit();
        } catch (SQLException e) {
            throw new ConnectException("Failed to write records to database " + databaseName, e);
        }
    }

    private void writeRecord(Connection connection, String tableName, SinkRecord record) throws SQLException {
        Struct valueStruct = (Struct) record.value();
        String sql = generateInsertStatement(tableName, valueStruct);

        try (PreparedStatement ps = connection.prepareStatement(sql)) {
            int i = 1;
            for (org.apache.kafka.connect.data.Field field : valueStruct.schema().fields()) {
                Object value = valueStruct.get(field);
                ps.setObject(i++, value);
            }
            ps.executeUpdate();
        }
    }

    private String extractTableName(String topic) {
        int underscoreIndex = topic.indexOf('_');
        if (underscoreIndex == -1 || underscoreIndex == topic.length() - 1) {
            throw new ConnectException("Invalid topic format. Expected 'databaseName_tableName'");
        }
        return topic.substring(underscoreIndex + 1);
    }

    private String generateInsertStatement(String tableName, Struct valueStruct) {
        StringBuilder columns = new StringBuilder();
        StringBuilder values = new StringBuilder();

        for (org.apache.kafka.connect.data.Field field : valueStruct.schema().fields()) {
            if (columns.length() > 0) {
                columns.append(", ");
                values.append(", ");
            }
            columns.append(field.name());
            values.append("?");
        }

        return String.format("INSERT INTO %s (%s) VALUES (%s)", 
                tableName, columns.toString(), values.toString());
    }

    public void close() {
        // Connection pool is managed by ConnectionPoolManager
    }
}
