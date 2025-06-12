package com.telefonica.kafka.connect.jdbc;

import org.apache.kafka.connect.data.Struct;
import org.apache.kafka.connect.errors.ConnectException;
import org.apache.kafka.connect.sink.SinkRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.*;
import java.util.Collection;
import java.util.List;

public class DatabaseWriter {
    private static final Logger log = LoggerFactory.getLogger(DatabaseWriter.class);
    private final String dbName;
    private final ConnectionPoolManager poolManager;
    private final MultiDbJdbcSinkConfig config;

    public DatabaseWriter(String dbName, ConnectionPoolManager poolManager, MultiDbJdbcSinkConfig config) 
            throws SQLException {
        this.dbName = dbName;
        this.poolManager = poolManager;
        this.config = config;
        testConnection();
    }

    private void testConnection() throws SQLException {
        try (Connection conn = poolManager.getConnection(dbName)) {
            log.info("Successfully connected to database: {}", dbName);
        }
    }

    public void write(Collection<SinkRecord> records) {
        if (records.isEmpty()) return;

        try (Connection conn = poolManager.getConnection(dbName)) {
            conn.setAutoCommit(false);
            
            for (SinkRecord record : records) {
                String tableName = extractTableName(record.topic());
                writeRecord(conn, tableName, record);
            }
            
            conn.commit();
        } catch (SQLException e) {
            throw new ConnectException("Failed to write to database: " + dbName, e);
        }
    }

    private String extractTableName(String topic) {
        String[] parts = topic.split(config.getTopicDbSeparator(), 2);
        return parts[1];
    }

    private void writeRecord(Connection conn, String tableName, SinkRecord record) throws SQLException {
        Struct value = (Struct) record.value();
        String sql = buildInsertStatement(tableName, value);
        
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            int i = 1;
            for (org.apache.kafka.connect.data.Field field : value.schema().fields()) {
                Object fieldValue = value.get(field);
                if (fieldValue instanceof java.util.Date) {
                    ps.setObject(i++, fieldValue, Types.TIMESTAMP);
                } else {
                    ps.setObject(i++, fieldValue);
                }
                //ps.setObject(i++, value.get(field));
            }
            ps.executeUpdate();
        }
    }

    private String buildInsertStatement(String tableName, Struct value) {
        StringBuilder columns = new StringBuilder();
        StringBuilder placeholders = new StringBuilder();

        for (org.apache.kafka.connect.data.Field field : value.schema().fields()) {
            if (columns.length() > 0) {
                columns.append(", ");
                placeholders.append(", ");
            }
            columns.append(field.name());
            placeholders.append("?");
        }

        return String.format("INSERT INTO %s (%s) VALUES (%s)", 
                tableName, columns, placeholders);
    }

    public void close() {
        // Connection pool is managed by ConnectionPoolManager
    }
}
