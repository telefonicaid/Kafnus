import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

public class KafkaConsumerExample {

    private static final Logger logger = LoggerFactory.getLogger(KafkaConsumerExample.class);
    private static final String TOPIC = "raw_historic";
    private static final String BOOTSTRAP_SERVERS = "host.docker.internal:9092";
    private static final String GROUP_ID = "test-group";

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, GROUP_ID);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false"); // Confirmación manual

        try (KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props)) {
            consumer.subscribe(Collections.singletonList(TOPIC));
            logger.info("Consumidor suscrito al tópico: {}", TOPIC);

            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

                for (ConsumerRecord<String, String> record : records) {
                    logger.info("Mensaje recibido - Offset: {}, Key: {}, Value: {}",
                            record.offset(), record.key(), record.value());

                    // Procesamiento del mensaje aquí
                }

                if (!records.isEmpty()) {
                    consumer.commitSync(); // Confirmar offsets procesados
                    logger.debug("Offsets confirmados");
                }
            }
        } catch (Exception e) {
            logger.error("Error en el consumidor Kafka", e);
        }
    }
}