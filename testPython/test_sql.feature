Feature: Ingesta de datos desde Kafka a SQL

  Scenario: Mensaje v�lido es insertado en la tabla SQL
    Given el t�pico "clientes" en Kafka contiene un mensaje JSON v�lido
    When el conector Kafka-SQL procesa el mensaje
    Then una fila correspondiente debe existir en la tabla "clientes" de SQL
