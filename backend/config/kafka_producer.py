from confluent_kafka import Producer
import logging


class KafkaProducer:
    def __init__(self, broker_url, topic):
        self.topic = topic
        self.producer = Producer({"bootstrap.servers": broker_url})
        self.logger = logging.getLogger(__name__)

    def send_message(self, message: dict):
        try:
            self.producer.produce(
                self.topic, key=str(message.get("user_id")), value=str(message)
            )
            self.producer.flush()
            self.logger.info(f"Message sent to Kafka: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send message to Kafka: {e}")
