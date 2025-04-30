public class KafkaSqlConnectorSteps {

    private KafkaContainer kafka;
    private PostgreSQLContainer<?> postgres;
    private Map<String, String> connectorConfig;
    private List<SourceRecord> consumedRecords;

    @Given("Tengo un tópico de Kafka {string} con {int} mensaje JSON")
    public void crearTopicoConMensaje(String topic, int count) {
        // Configurar Kafka con TestContainers
        kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:latest"));
        kafka.start();
        
        // Crear tópico y publicar mensaje(s) de prueba
        try (AdminClient admin = AdminClient.create(...)) {
            admin.createTopics(Collections.singleton(new NewTopic(topic, 1, (short)1)));
        }
        
        // Publicar mensaje(s) de prueba
        try (Producer<String, String> producer = new KafkaProducer<>(...)) {
            producer.send(new ProducerRecord<>(topic, "{\"id\":1,\"name\":\"test\"}"));
        }
    }

    @Given("Tengo una tabla {string} en la base de datos SQL")
    public void crearTablaEnSQL(String tableName) {
        postgres = new PostgreSQLContainer<>("postgres:latest");
        postgres.start();
        
        try (Connection conn = DriverManager.getConnection(...)) {
            Statement stmt = conn.createStatement();
            stmt.execute("CREATE TABLE " + tableName + " (id INT, name VARCHAR(100))");
        }
    }

    @When("Ejecuto el conector Kafka-SQL con la configuración adecuada")
    public void ejecutarConector() {
        // Configurar el conector
        connectorConfig = Map.of(
            "name", "test-connector",
            "connector.class", "io.confluent.connect.jdbc.JdbcSinkConnector",
            "tasks.max", "1",
            "topics", "test-topic",
            "connection.url", postgres.getJdbcUrl(),
            "connection.user", postgres.getUsername(),
            "connection.password", postgres.getPassword(),
            "auto.create", "true",
            "insert.mode", "insert"
        );
        
        // Iniciar el conector (usando Kafka Connect API o embebido)
        ConnectRunner.startConnector(connectorConfig);
    }

    @Then("El mensaje debe aparecer en la tabla SQL")
    public void verificarMensajeEnSQL() {
        try (Connection conn = DriverManager.getConnection(...)) {
            ResultSet rs = conn.createStatement().executeQuery("SELECT COUNT(*) FROM test_table");
            rs.next();
            assertThat(rs.getInt(1)).isEqualTo(1);
        }
    }

    @Then("Los campos del mensaje deben mapearse correctamente a las columnas")
    public void verificarMapeoDeCampos() {
        try (Connection conn = DriverManager.getConnection(...)) {
            ResultSet rs = conn.createStatement().executeQuery("SELECT id, name FROM test_table");
            assertThat(rs.next()).isTrue();
            assertThat(rs.getInt("id")).isEqualTo(1);
            assertThat(rs.getString("name")).isEqualTo("test");
        }
    }
}
