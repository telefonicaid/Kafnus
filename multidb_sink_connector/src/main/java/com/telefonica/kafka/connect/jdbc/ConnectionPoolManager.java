package com.telefonica.kafka.connect.jdbc;

import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ConnectionPoolManager {
    private static final Logger log = LoggerFactory.getLogger(ConnectionPoolManager.class);
    private final Map<String, BasicDataSource> dataSources = new ConcurrentHashMap<>();
    private final MultiDbJdbcSinkConfig config;

    public ConnectionPoolManager(MultiDbJdbcSinkConfig config) {
        this.config = config;
    }

    public Connection getConnection(String dbName) throws SQLException {
        BasicDataSource dataSource = dataSources.computeIfAbsent(dbName, this::createDataSource);
        return dataSource.getConnection();
    }

    private BasicDataSource createDataSource(String dbName) {
        BasicDataSource ds = new BasicDataSource();
        String jdbcUrl = config.getConnectionUrlTemplate().replace("{db}", dbName);
        
        ds.setUrl(jdbcUrl);
        ds.setUsername(config.getUser());
        ds.setPassword(config.getPassword());
        ds.setMinIdle(config.getMinPoolSize());
        ds.setMaxTotal(config.getMaxPoolSize());
        ds.setMaxWaitMillis(10000); // 10 seconds
        ds.setValidationQuery("SELECT 1");
        ds.setTestOnBorrow(true);
        
        log.info("Created connection pool for database: {}", dbName);
        return ds;
    }

    public void closeAll() {
        dataSources.forEach((dbName, ds) -> {
            try {
                ds.close();
                log.info("Closed connection pool for database: {}", dbName);
            } catch (SQLException e) {
                log.error("Error closing connection pool for database: {}", dbName, e);
            }
        });
        dataSources.clear();
    }
}
