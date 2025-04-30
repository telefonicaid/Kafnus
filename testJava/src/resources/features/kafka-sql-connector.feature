Feature: Conector de Kafka a SQL
  Como desarrollador
  Quiero asegurar que los mensajes de Kafka se persisten correctamente en SQL
  Para garantizar la integridad de los datos

  Scenario: Persistir mensaje JSON simple en tabla SQL
    Given Tengo un tópico de Kafka "test-topic" con 1 mensaje JSON
    And Tengo una tabla "test_table" en la base de datos SQL
    When Ejecuto el conector Kafka-SQL con la configuración adecuada
    Then El mensaje debe aparecer en la tabla SQL
    And Los campos del mensaje deben mapearse correctamente a las columnas
