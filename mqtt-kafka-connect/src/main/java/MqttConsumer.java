import com.hivemq.client.mqtt.MqttClient;
import com.hivemq.client.mqtt.MqttGlobalPublishFilter;
import com.hivemq.client.mqtt.datatypes.MqttQos;
import com.hivemq.client.mqtt.mqtt5.Mqtt5BlockingClient;
import com.hivemq.client.mqtt.mqtt5.message.publish.Mqtt5Publish;

import java.net.InetAddress;

public class MqttConsumer {

    public static void main(String[] args) {

        // 1. Crear cliente MQTT
        final Mqtt5BlockingClient client = MqttClient.builder()
                .useMqttVersion5() // Usar MQTT v5 (opcional: también soporta v3.1.1)
                .identifier("java-consumer-" + System.currentTimeMillis())
                .serverHost("localhost") // Broker público de prueba
                .serverPort(1883) // Puerto estándar MQTT
                .buildBlocking();

        try {
            // 2. Conectar al broker
            client.connect();
            System.out.println("Conectado al broker!");

            // 3. Suscribirse a un tópico
            final String topic = "kafnus/tovar/test/raw_historic";
            client.subscribeWith()
                    .topicFilter(topic)
                    .qos(MqttQos.AT_LEAST_ONCE) // Calidad de servicio
                    .send();

            System.out.println("Suscrito al tópico: " + topic);

            // 4. Recibir mensajes de forma asíncrona
            client.toAsync().publishes(MqttGlobalPublishFilter.ALL, publish -> {
                System.out.println("\nMensaje Recibido:");
                System.out.println("-> Tópico: " + publish.getTopic());
                System.out.println("-> Contenido: " + new String(publish.getPayloadAsBytes()));
                System.out.println("-> QoS: " + publish.getQos());
            });

            // Mantener el programa en ejecución
            Thread.sleep(Long.MAX_VALUE);

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // 5. Desconectar
            client.disconnect();
        }
    }
}