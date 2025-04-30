# kafka-sql-multi-topic.feature
Feature: Conector Kafka-SQL con múltiples topics y datasets

  Scenario Outline: Procesamiento de múltiples topics con diferentes esquemas
    Given Tengo un tópico "<topic>" con los siguientes mensajes:
      | content                             |
      | <message_1>                        |
      | <message_2>                        |
    And Tengo una tabla SQL "<table>" con esquema:
      """
      <schema_definition>
      """
    When Ejecuto el conector Kafka-SQL mapeando "<topic>" a "<table>"
    Then La tabla "<table>" debe contener los registros equivalentes

    Examples:
      | topic         | table        | schema_definition               | message_1                  | message_2                  |
      | orders        | db_orders    | id INT, product VARCHAR, qty INT | {"id":1,"product":"A","qty":2} | {"id":2,"product":"B","qty":5} |
      | customers     | db_customers | id INT, name VARCHAR, email VARCHAR | {"id":1,"name":"John","email":"john@test.com"} | {"id":2,"name":"Maria","email":"maria@test.com"} |
      | transactions  | db_txns      | tx_id VARCHAR, amount DECIMAL(10,2), currency VARCHAR | {"tx_id":"TX1001","amount":150.75,"currency":"USD"} | {"tx_id":"TX1002","amount":89.99,"currency":"EUR"} |
