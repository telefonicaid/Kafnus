Feature: Ingesta de datos desde Kafka a SQL

  Scenario: Mensaje valido es insertado en la tabla SQL
    Given el topico "clientes" en Kafka contiene un mensaje JSON valido
    When el conector Kafka-SQL procesa el mensaje
    Then una fila correspondiente debe existir en la tabla "clientes" de SQL
