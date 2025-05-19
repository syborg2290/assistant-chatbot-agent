import json
from kafka import KafkaProducer
from loguru import logger
from config.config import config


class KafkaConfig:
    _producer = None

    @classmethod
    def get_producer(cls):
        if cls._producer is None:
            try:
                producer_config = {
                    "bootstrap_servers": config.KAFKA_BOOTSTRAP_SERVERS,
                    "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
                    "security_protocol": config.KAFKA_SECURITY_PROTOCOL,
                }

                # SASL authentication (if configured)
                if config.KAFKA_SECURITY_PROTOCOL in ["SASL_PLAINTEXT", "SASL_SSL"]:
                    producer_config.update(
                        {
                            "sasl_mechanism": config.KAFKA_SASL_MECHANISM,
                            "sasl_plain_username": config.KAFKA_SASL_USERNAME,
                            "sasl_plain_password": config.KAFKA_SASL_PASSWORD,
                        }
                    )

                cls._producer = KafkaProducer(**producer_config)
                logger.info("Kafka producer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka producer: {str(e)}")
                raise e
        return cls._producer

    @classmethod
    def send_message(cls, topic, key, message):
        try:
            logger.info(
                f"Message sent to Kafka topic '{topic}' with key '{key}': {message}"
            )
            producer = cls.get_producer()
            producer.send(topic, key=key, value=message)
            producer.flush()
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {str(e)}")
