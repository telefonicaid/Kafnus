package com.example.kafka.connect.jdbc;

import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.common.config.ConfigException;
import java.util.Map;

public class MultiDbJdbcSinkConfig {
    public static final String CONNECTION_URL_CONFIG = "connection.url";
    public static final String CONNECTION_USER_CONFIG = "connection.user";
    public static final String CONNECTION_PASSWORD_CONFIG = "connection.password";
    public static final String MAX_POOL_SIZE_CONFIG = "connection.pool.max.size";
    public static final String MIN_POOL_SIZE_CONFIG = "connection.pool.min.size";

    private final String baseConnectionUrl;
    private final String user;
    private final String password;
    private final int maxPoolSize;
    private final int minPoolSize;

    public static final ConfigDef CONFIG_DEF = new ConfigDef()
            .define(CONNECTION_URL_CONFIG, ConfigDef.Type.STRING, ConfigDef.Importance.HIGH,
                    "JDBC connection URL template with {database} placeholder")
            .define(CONNECTION_USER_CONFIG, ConfigDef.Type.STRING, ConfigDef.Importance.HIGH,
                    "JDBC user with access to all databases")
            .define(CONNECTION_PASSWORD_CONFIG, ConfigDef.Type.PASSWORD, ConfigDef.Importance.HIGH,
                    "JDBC password")
            .define(MAX_POOL_SIZE_CONFIG, ConfigDef.Type.INT, 10, ConfigDef.Importance.MEDIUM,
                    "Maximum connection pool size per database")
            .define(MIN_POOL_SIZE_CONFIG, ConfigDef.Type.INT, 1, ConfigDef.Importance.MEDIUM,
                    "Minimum connection pool size per database");

    public MultiDbJdbcSinkConfig(Map<String, String> props) {
        super(CONFIG_DEF, props);
        this.baseConnectionUrl = getString(CONNECTION_URL_CONFIG);
        if (!baseConnectionUrl.contains("{database}")) {
            throw new ConfigException("Connection URL must contain '{database}' placeholder");
        }
        this.user = getString(CONNECTION_USER_CONFIG);
        this.password = getPasswordValue(CONNECTION_PASSWORD_CONFIG);
        this.maxPoolSize = getInt(MAX_POOL_SIZE_CONFIG);
        this.minPoolSize = getInt(MIN_POOL_SIZE_CONFIG);
    }

    // Getters
    public String getBaseConnectionUrl() { return baseConnectionUrl; }
    public String getUser() { return user; }
    public String getPassword() { return password; }
    public int getMaxPoolSize() { return maxPoolSize; }
    public int getMinPoolSize() { return minPoolSize; }
}
