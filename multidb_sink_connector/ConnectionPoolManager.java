package com.example.kafka.connect.jdbc;

import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ConnectionPoolManager {
    private static final Logger log = LoggerFactory.getLogger(ConnectionPoolManager.class);

    private final Map<String, BasicDataSource> dataSourceMap = new ConcurrentHashMap<>();
    private final MultiTenantJdbcSinkConfig config;

    public ConnectionPoolManager(MultiTenantJdbcSinkConfig config) {
        this.config = config;
    }

    public synchronized Connection getConnection(String databaseName) throws SQLException {
        BasicDataSource dataSource = dataSourceMap.computeIfAbsent(databaseName, k -> {
            BasicDataSource ds = new BasicDataSource();
            String jdbcUrl = config.getBaseConnectionUrl().replace("{database}", databaseName);
            ds.setUrl(jdbcUrl);
            ds.setUsername(config.getUser());
            ds.setPassword(config.getPassword());
            ds.setMinIdle(config.getMinPoolSize());
            ds.setMaxTotal(config.getMaxPoolSize());
            ds.setMaxWaitMillis(10000); // 10 seconds
            ds.setValidationQuery("SELECT 1");
            ds.setTestOnBorrow(true);
            log.info("Created connection pool for database: {}", databaseName);
            return ds;
        });
        return dataSource.getConnection();
    }

    public synchronized void closeAll() {
        dataSourceMap.forEach((dbName, dataSource) -> {
            try {
                dataSource.close();
                log.info("Closed connection pool for database: {}", dbName);
            } catch (SQLException e) {
                log.error("Error closing connection pool for database: {}", dbName, e);
            }
        });
        dataSourceMap.clear();
    }
}
