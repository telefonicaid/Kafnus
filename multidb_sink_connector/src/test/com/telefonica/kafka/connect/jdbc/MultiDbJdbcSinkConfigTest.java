package com.telefonica.kafka.connect.jdbc;

import org.apache.kafka.common.config.ConfigException;
import org.junit.jupiter.api.Test;
import java.util.HashMap;
import java.util.Map;
import static org.junit.jupiter.api.Assertions.*;

class MultiDbJdbcSinkConfigTest {

    @Test
    void shouldCreateConfigWithValidParameters() {
        Map<String, String> props = new HashMap<>();
        props.put("connection.url.template", "jdbc:postgresql://localhost:5432/{db}");
        props.put("connection.user", "user");
        props.put("connection.password", "pass");
        
        MultiDbJdbcSinkConfig config = new MultiDbJdbcSinkConfig(props);
        
        assertEquals("jdbc:postgresql://localhost:5432/{db}", config.getConnectionUrlTemplate());
        assertEquals("user", config.getUser());
        assertEquals("pass", config.getPassword());
        assertEquals(1, config.getMinPoolSize()); // default
        assertEquals(10, config.getMaxPoolSize()); // default
    }

    @Test
    void shouldThrowExceptionWhenMissingDbPlaceholder() {
        Map<String, String> props = new HashMap<>();
        props.put("connection.url.template", "jdbc:postgresql://localhost:5432/mydb");
        props.put("connection.user", "user");
        props.put("connection.password", "pass");
        
        assertThrows(ConfigException.class, () -> new MultiDbJdbcSinkConfig(props));
    }

    @Test
    void shouldUseCustomPoolSizes() {
        Map<String, String> props = new HashMap<>();
        props.put("connection.url.template", "jdbc:postgresql://localhost:5432/{db}");
        props.put("connection.pool.min.size", "5");
        props.put("connection.pool.max.size", "20");
        
        MultiDbJdbcSinkConfig config = new MultiDbJdbcSinkConfig(props);
        
        assertEquals(5, config.getMinPoolSize());
        assertEquals(20, config.getMaxPoolSize());
    }
}
