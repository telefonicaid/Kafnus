public class MultiTopicConnectorSteps {

    private static KafkaContainer kafka;
    private static PostgreSQLContainer<?> postgres;
    private Map<String, List<String>> topicMessages = new HashMap<>();
    private Map<String, String> tableSchemas = new HashMap<>();

    @BeforeAll
    public static void setupContainers() {
        kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:latest"));
        postgres = new PostgreSQLContainer<>("postgres:latest");
        kafka.start();
        postgres.start();
    }

    @AfterAll
    public static void tearDownContainers() {
        kafka.stop();
        postgres.stop();
    }

    @Given("Tengo un tópico {string} con los siguientes mensajes:")
    public void crearTopicoConMensajes(String topic, List<Map<String, String>> messages) {
        // Crear tópico si no existe
        try (AdminClient admin = AdminClient.create(Map.of(
            "bootstrap.servers", kafka.getBootstrapServers()
        ))) {
            admin.createTopics(Collections.singleton(new NewTopic(topic, 1, (short)1)));
        }
        
        // Almacenar mensajes para este topic
        List<String> messageList = messages.stream()
            .map(m -> m.get("content"))
            .collect(Collectors.toList());
        
        topicMessages.put(topic, messageList);
        
        // Publicar mensajes
        try (Producer<String, String> producer = new KafkaProducer<>(Map.of(
            "bootstrap.servers", kafka.getBootstrapServers(),
            "key.serializer", StringSerializer.class.getName(),
            "value.serializer", StringSerializer.class.getName()
        ))) {
            for (String message : messageList) {
                producer.send(new ProducerRecord<>(topic, message));
            }
        }
    }

    @Given("Tengo una tabla SQL {string} con esquema:")
    public void crearTablaConEsquema(String tableName, String schema) {
        tableSchemas.put(tableName, schema);
        
        try (Connection conn = DriverManager.getConnection(
            postgres.getJdbcUrl(), 
            postgres.getUsername(), 
            postgres.getPassword()
        )) {
            Statement stmt = conn.createStatement();
            stmt.execute("DROP TABLE IF EXISTS " + tableName);
            stmt.execute("CREATE TABLE " + tableName + " (" + schema + ")");
        } catch (SQLException e) {
            throw new RuntimeException("Error creando tabla " + tableName, e);
        }
    }

    @When("Ejecuto el conector Kafka-SQL mapeando {string} a {string}")
    public void ejecutarConectorParaTopic(String topic, String table) {
        Map<String, String> config = Map.of(
            "name", "test-connector-" + topic,
            "connector.class", "io.confluent.connect.jdbc.JdbcSinkConnector",
            "tasks.max", "1",
            "topics", topic,
            "connection.url", postgres.getJdbcUrl(),
            "connection.user", postgres.getUsername(),
            "connection.password", postgres.getPassword(),
            "auto.create", "false", // Ya creamos la tabla manualmente
            "insert.mode", "insert",
            "table.name.format", table,
            "pk.mode", "record_value",
            "pk.fields", "id" // Ajustar según esquema
        );
        
        ConnectRunner.startConnector(config);
        
        // Esperar a que se procesen los mensajes
        await().atMost(30, SECONDS).until(() -> {
            return verificarRegistrosEnTabla(table, topicMessages.get(topic).size());
        });
    }

    @Then("La tabla {string} debe contener los registros equivalentes")
    public void verificarRegistrosEnTabla(String tableName, int expectedCount) {
        try (Connection conn = DriverManager.getConnection(
            postgres.getJdbcUrl(), 
            postgres.getUsername(), 
            postgres.getPassword()
        )) {
            ResultSet rs = conn.createStatement().executeQuery("SELECT COUNT(*) FROM " + tableName);
            rs.next();
            assertThat(rs.getInt(1)).isEqualTo(expectedCount);
            
            // Verificación adicional podría incluir comprobar campos específicos
        } catch (SQLException e) {
            throw new RuntimeException("Error verificando tabla " + tableName, e);
        }
    }
}
