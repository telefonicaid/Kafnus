package com.telefonica.kafka.connect.jdbc;

import org.apache.kafka.connect.data.Schema;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.apache.kafka.connect.data.Struct;
import org.apache.kafka.connect.sink.SinkRecord;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Collections;
import static org.junit.jupiter.api.Assertions.*;

@Testcontainers
class MultiDbJdbcSinkTaskIntegrationTest {

    @Container
    private static final PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:13")
        .withDatabaseName("testdb")
        .withUsername("testuser")
        .withPassword("testpass");

    private MultiDbJdbcSinkTask task;
    private Map<String, String> config;

    @BeforeEach
    void setUp() throws Exception {
        // Crear estructura de prueba en la base de datos
        try (Connection conn = DriverManager.getConnection(
                postgres.getJdbcUrl(), 
                postgres.getUsername(), 
                postgres.getPassword())) {
            
            try (Statement stmt = conn.createStatement()) {
                stmt.execute("CREATE TABLE test_table (id INT PRIMARY KEY, name VARCHAR(100))");
            }
        }

        config = new HashMap<>();
        config.put("connection.url.template", postgres.getJdbcUrl().replace("testdb", "{db}"));
        config.put("connection.user", postgres.getUsername());
        config.put("connection.password", postgres.getPassword());
        config.put("connection.pool.min.size", "1");
        config.put("connection.pool.max.size", "1");
        
        task = new MultiDbJdbcSinkTask();
        task.start(config);
    }

    @AfterEach
    void tearDown() {
        task.stop();
    }

    @Test
    void shouldInsertRecordIntoDatabase() throws Exception {
        Schema schema = SchemaBuilder.struct()
            .field("id", Schema.INT32_SCHEMA)
            .field("name", Schema.STRING_SCHEMA)
            .build();
        
        Struct value = new Struct(schema)
            .put("id", 1)
            .put("name", "Test Record");
        
        SinkRecord record = new SinkRecord(
            "testdb_test_table", 0, null, null, schema, value, 0);
        
        task.put(Collections.singletonList(record));

        // Check inserted record
        try (Connection conn = DriverManager.getConnection(
                postgres.getJdbcUrl(), 
                postgres.getUsername(), 
                postgres.getPassword())) {
            
            try (Statement stmt = conn.createStatement();
                 ResultSet rs = stmt.executeQuery("SELECT * FROM test_table")) {
                
                assertTrue(rs.next());
                assertEquals(1, rs.getInt("id"));
                assertEquals("Test Record", rs.getString("name"));
                assertFalse(rs.next());
            }
        }
    }
}
