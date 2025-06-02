package com.telefonica.kafka.connect.jdbc;

import org.apache.kafka.connect.sink.SinkRecord;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MultiDbJdbcSinkTaskTest {

    @Mock
    private ConnectionPoolManager poolManager;
    @Mock
    private DatabaseWriter dbWriter;
    
    private MultiDbJdbcSinkTask task;
    private Map<String, String> props;

    @BeforeEach
    void setUp() {
        task = new MultiDbJdbcSinkTask() {
            @Override
            protected ConnectionPoolManager createPoolManager(MultiDbJdbcSinkConfig config) {
                return poolManager;
            }
            
            @Override
            protected DatabaseWriter createDbWriter(String dbName, ConnectionPoolManager poolManager, MultiDbJdbcSinkConfig config) {
                return dbWriter;
            }
        };
        
        props = new HashMap<>();
        props.put("connection.url.template", "jdbc:postgresql://localhost:5432/{db}");
        props.put("connection.user", "user");
        props.put("connection.password", "pass");
    }

    @Test
    void shouldStartWithValidConfig() {
        task.start(props);
        // No exception means success
    }

    @Test
    void shouldRouteRecordsToCorrectDatabase() {
        task.start(props);
        
        SinkRecord record1 = new SinkRecord("db1_table1", 0, null, null, null, null, 0);
        SinkRecord record2 = new SinkRecord("db2_table1", 0, null, null, null, null, 0);
        
        task.put(Arrays.asList(record1, record2));
        
        verify(dbWriter, times(2)).write(any());
    }

    @Test
    void shouldHandleEmptyRecordSet() {
        task.start(props);
        task.put(Collections.emptyList());
        
        verifyNoInteractions(dbWriter);
    }

    @Test
    void shouldStopCleanly() {
        task.start(props);
        task.stop();
        
        verify(dbWriter).close();
        verify(poolManager).closeAll();
    }
}
