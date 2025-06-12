package com.example.mqtt;

import com.hivemq.client.mqtt.MqttClient;
import com.hivemq.client.mqtt.MqttGlobalPublishFilter;
import com.hivemq.client.mqtt.datatypes.MqttQos;
import com.hivemq.client.mqtt.mqtt5.Mqtt5BlockingClient;
import com.hivemq.client.mqtt.mqtt5.message.publish.Mqtt5Publish;
import org.apache.kafka.connect.source.SourceRecord;
import org.apache.kafka.connect.source.SourceTask;
import org.apache.kafka.connect.header.ConnectHeaders;
import org.apache.kafka.connect.data.Schema;

import java.util.*;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

public class MqttSourceTask extends SourceTask {
    private Mqtt5BlockingClient mqttBlockingClient;
    private BlockingQueue<SourceRecord> queue = new LinkedBlockingQueue<>(1000);
    private String MQTT_BROKER = null;
    private int MQTT_PORT = 1883;
    private String MQTT_TOPIC =  null;

    @Override
    public String version() {
        return "1.0";
    }

    @Override
    public void start(Map<String, String> props) {
        int maxRetries = 5;
        int retryDelay = 3000; // ms
        int attempt = 0;
        boolean connected = false;
        MQTT_BROKER = props.get("mqtt.broker");
        MQTT_TOPIC = props.get("mqtt.topic");

        while (attempt < maxRetries && !connected) {
            try {
                attempt++;
                // Create and connect blocking client
                mqttBlockingClient = MqttClient.builder()
                        .useMqttVersion5()
                        .identifier("kafka-connect-" + UUID.randomUUID())
                        .serverHost(MQTT_BROKER)
                        .serverPort(MQTT_PORT)
                        .buildBlocking();

                mqttBlockingClient.connect();

                // Verify connection state
                if (mqttBlockingClient.getState().isConnected()) {
                    connected = true;
                    System.out.println("✅ Connected to MQTT broker (Attempt " + attempt + ")");

                    // Subscribe to hardcoded topic
                    mqttBlockingClient.subscribeWith()
                            .topicFilter(MQTT_TOPIC)
                            .qos(MqttQos.AT_LEAST_ONCE)
                            .send();

                    System.out.println("Subscribed to " + MQTT_TOPIC);

                    // Setup async message handling
                    mqttBlockingClient.toAsync().publishes(
                            MqttGlobalPublishFilter.ALL,
                            this::handleMessage
                    );
                } else {
                    System.err.println("⚠️ Connection attempt " + attempt + " failed");
                }
            } catch (Exception e) {
                System.err.println("⚠️ Connection failed (Attempt " + attempt + "): " + e.getMessage());
                if (mqttBlockingClient != null) {
                    mqttBlockingClient.disconnect();
                }
            }

            if (!connected && attempt < maxRetries) {
                try {
                    System.out.println("🔄 Retrying in " + retryDelay + "ms...");
                    Thread.sleep(retryDelay);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            }
        }

        if (!connected) {
            throw new RuntimeException("Failed to connect after " + maxRetries + " attempts");
        }
    }

    private void handleMessage(Mqtt5Publish message) {
        var inTopic = message.getTopic().toString();
        String[] inTopicParts = inTopic.split("/");
        if (inTopicParts.length == 4) {
            String fiware_service = inTopicParts[1];
            String fiware_servicepath =inTopicParts[2];
            String destination_topic = inTopicParts[inTopicParts.length - 1];

            try {
                ConnectHeaders headers = new ConnectHeaders();

                // Hardcoded FiWARE values for PoC
                headers.addString("fiware-service", fiware_service);
                headers.addString("fiware-servicepath", fiware_servicepath);

                SourceRecord record = new SourceRecord(
                        Collections.singletonMap("mqtt_topic", message.getTopic().toString()),
                        Collections.singletonMap("timestamp", System.currentTimeMillis()),
                        destination_topic,  // Using hardcoded Kafka topic
                        null,
                        Schema.STRING_SCHEMA,
                        null,
                        Schema.STRING_SCHEMA,
                        new String(message.getPayloadAsBytes()),
                        System.currentTimeMillis(),
                        headers
                );

                System.out.println("Forwarding message to Kafka: " + new String(message.getPayloadAsBytes()));
                queue.offer(record);

            } catch (Exception e) {
                System.err.println("Message handling failed: " + e.getMessage());
            }
        }
    }

    @Override
    public List<SourceRecord> poll() throws InterruptedException {
        List<SourceRecord> records = new ArrayList<>();
        SourceRecord record = queue.poll(1000, TimeUnit.MILLISECONDS);

        if (record != null) {
            records.add(record);
            queue.drainTo(records, 99);  // Batch up to 100 records
        }
        return records;
    }

    @Override
    public void stop() {
        if (mqttBlockingClient != null && mqttBlockingClient.getState().isConnected()) {
            mqttBlockingClient.disconnect();
            System.out.println("Disconnected from MQTT broker");
        }
    }
}