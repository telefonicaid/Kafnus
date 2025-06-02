package com.telefonica.kafka.connect.jdbc;

import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.common.config.ConfigException;
import java.util.Map;

public class MultiDbJdbcSinkConfig {
    public static final String CONNECTION_URL_TEMPLATE = "connection.url.template";
    public static final String CONNECTION_USER = "connection.user";
    public static final String CONNECTION_PASSWORD = "connection.password";
    public static final String CONNECTION_POOL_MIN_SIZE = "connection.pool.min.size";
    public static final String CONNECTION_POOL_MAX_SIZE = "connection.pool.max.size";
    public static final String TOPIC_DB_SEPARATOR = "topic.db.separator";
    public static final String AUTO_CREATE_TABLES = "auto.create.tables";

    private final String connectionUrlTemplate;
    private final String user;
    private final String password;
    private final int minPoolSize;
    private final int maxPoolSize;
    private final String topicDbSeparator;
    private final boolean autoCreateTables;

    public static final ConfigDef CONFIG_DEF = new ConfigDef()
        .define(CONNECTION_URL_TEMPLATE, ConfigDef.Type.STRING, ConfigDef.Importance.HIGH,
            "JDBC URL template with {db} placeholder (e.g., 'jdbc:postgresql://localhost:5432/{db}')")
        .define(CONNECTION_USER, ConfigDef.Type.STRING, ConfigDef.Importance.HIGH,
            "Database username")
        .define(CONNECTION_PASSWORD, ConfigDef.Type.PASSWORD, ConfigDef.Importance.HIGH,
            "Database password")
        .define(CONNECTION_POOL_MIN_SIZE, ConfigDef.Type.INT, 1, ConfigDef.Importance.MEDIUM,
            "Minimum connections in pool per database")
        .define(CONNECTION_POOL_MAX_SIZE, ConfigDef.Type.INT, 10, ConfigDef.Importance.MEDIUM,
            "Maximum connections in pool per database")
        .define(TOPIC_DB_SEPARATOR, ConfigDef.Type.STRING, "_", ConfigDef.Importance.LOW,
            "Separator between database name and table name in topic")
        .define(AUTO_CREATE_TABLES, ConfigDef.Type.BOOLEAN, false, ConfigDef.Importance.MEDIUM,
            "Whether to automatically create tables if they don't exist");

    public MultiDbJdbcSinkConfig(Map<String, String> props) {
        super(CONFIG_DEF, props);
        this.connectionUrlTemplate = getString(CONNECTION_URL_TEMPLATE);
        this.user = getString(CONNECTION_USER);
        this.password = getPasswordValue(CONNECTION_PASSWORD);
        this.minPoolSize = getInt(CONNECTION_POOL_MIN_SIZE);
        this.maxPoolSize = getInt(CONNECTION_POOL_MAX_SIZE);
        this.topicDbSeparator = getString(TOPIC_DB_SEPARATOR);
        this.autoCreateTables = getBoolean(AUTO_CREATE_TABLES);

        if (!connectionUrlTemplate.contains("{db}")) {
            throw new ConfigException("Connection URL template must contain '{db}' placeholder");
        }
    }

    // Getters
    public String getConnectionUrlTemplate() { return connectionUrlTemplate; }
    public String getUser() { return user; }
    public String getPassword() { return password; }
    public int getMinPoolSize() { return minPoolSize; }
    public int getMaxPoolSize() { return maxPoolSize; }
    public String getTopicDbSeparator() { return topicDbSeparator; }
    public boolean getAutoCreateTables() { return autoCreateTables; }
}
