package com.telefonica.kafka.connect.jdbc;

import org.apache.commons.dbcp2.BasicDataSource;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.sql.Connection;
import java.sql.SQLException;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ConnectionPoolManagerTest {

    @Mock
    private MultiDbJdbcSinkConfig config;
    @Mock
    private BasicDataSource dataSource;
    @Mock
    private Connection connection;
    
    private ConnectionPoolManager poolManager;

    @BeforeEach
    void setUp() {
        when(config.getConnectionUrlTemplate()).thenReturn("jdbc:postgresql://localhost:5432/{db}");
        when(config.getUser()).thenReturn("user");
        when(config.getPassword()).thenReturn("pass");
        when(config.getMinPoolSize()).thenReturn(1);
        when(config.getMaxPoolSize()).thenReturn(10);
        
        poolManager = new ConnectionPoolManager(config) {
            @Override
            protected BasicDataSource createDataSource(String dbName) {
                return dataSource;
            }
        };
    }

    @Test
    void shouldGetConnectionForDatabase() throws SQLException {
        when(dataSource.getConnection()).thenReturn(connection);
        
        Connection result = poolManager.getConnection("testdb");
        
        assertNotNull(result);
        verify(dataSource).getConnection();
    }

    @Test
    void shouldCreateDataSourcePerDatabase() throws SQLException {
        ConnectionPoolManager realPoolManager = new ConnectionPoolManager(config);
        
        realPoolManager.getConnection("db1");
        realPoolManager.getConnection("db2");
        realPoolManager.getConnection("db1");
        
        // Shoould create on 2 pools ( db1 and db2)
        // No exception
    }

    @Test
    void shouldCloseAllPools() throws SQLException {
        poolManager.getConnection("db1");
        poolManager.getConnection("db2");
        
        poolManager.closeAll();
        
        verify(dataSource, times(2)).close();
    }
}
