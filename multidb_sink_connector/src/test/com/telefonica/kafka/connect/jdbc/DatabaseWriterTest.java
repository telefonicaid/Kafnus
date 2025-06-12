package com.telefonica.kafka.connect.jdbc;

import org.apache.kafka.connect.data.Schema;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.apache.kafka.connect.data.Struct;
import org.apache.kafka.connect.sink.SinkRecord;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Collections;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DatabaseWriterTest {

    @Mock
    private ConnectionPoolManager poolManager;
    @Mock
    private MultiDbJdbcSinkConfig config;
    @Mock
    private Connection connection;
    @Mock
    private PreparedStatement preparedStatement;
    
    private DatabaseWriter dbWriter;
    private Schema schema;

    @BeforeEach
    void setUp() throws SQLException {
        when(poolManager.getConnection(anyString())).thenReturn(connection);
        when(connection.prepareStatement(anyString())).thenReturn(preparedStatement);
        when(config.getTopicDbSeparator()).thenReturn("_");
        
        dbWriter = new DatabaseWriter("testdb", poolManager, config);
        
        schema = SchemaBuilder.struct()
            .field("id", Schema.INT32_SCHEMA)
            .field("name", Schema.STRING_SCHEMA)
            .build();
    }

    @Test
    void shouldWriteRecordToDatabase() throws SQLException {
        Struct value = new Struct(schema).put("id", 1).put("name", "test");
        SinkRecord record = new SinkRecord("testdb_table", 0, null, null, schema, value, 0);
        
        dbWriter.write(Collections.singletonList(record));
        
        verify(connection).setAutoCommit(false);
        verify(preparedStatement).setObject(1, 1);
        verify(preparedStatement).setObject(2, "test");
        verify(preparedStatement).executeUpdate();
        verify(connection).commit();
    }

    @Test
    void shouldHandleMultipleRecordsInTransaction() throws SQLException {
        Struct value1 = new Struct(schema).put("id", 1).put("name", "test1");
        Struct value2 = new Struct(schema).put("id", 2).put("name", "test2");
        
        SinkRecord record1 = new SinkRecord("testdb_table", 0, null, null, schema, value1, 0);
        SinkRecord record2 = new SinkRecord("testdb_table", 0, null, null, schema, value2, 0);
        
        dbWriter.write(Arrays.asList(record1, record2));
        
        verify(preparedStatement, times(2)).executeUpdate();
        verify(connection).commit();
    }

    @Test
    void shouldExtractCorrectTableName() {
        String tableName = dbWriter.extractTableName("testdb_table1");
        assertEquals("table1", tableName);
        
        when(config.getTopicDbSeparator()).thenReturn("-");
        tableName = dbWriter.extractTableName("testdb-table2");
        assertEquals("table2", tableName);
    }
}
