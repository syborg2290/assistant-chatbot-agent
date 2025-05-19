import pika
from loguru import logger
from config.config import config
import json
from datetime import datetime


class RabbitMQConfig:
    _connection = None
    _channel = None

    @classmethod
    def get_channel(cls):
        if cls._channel is None or cls._channel.is_closed:
            try:
                credentials = pika.PlainCredentials(
                    config.RABBITMQ_USERNAME, config.RABBITMQ_PASSWORD
                )
                parameters = pika.ConnectionParameters(
                    host=config.RABBITMQ_HOST,
                    port=config.RABBITMQ_PORT,
                    virtual_host=config.RABBITMQ_VHOST,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )

                cls._connection = pika.BlockingConnection(parameters)
                cls._channel = cls._connection.channel()
                logger.info("RabbitMQ channel initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize RabbitMQ channel: {str(e)}")
                raise e
        return cls._channel

    @classmethod
    def send_message(cls, exchange, routing_key, message):
        try:

            # Convert datetime to string if present in message
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()  # Convert to ISO 8601 format
                raise TypeError("Type not serializable")

            # Manually serialize the message with datetime conversion
            encoded_message = json.dumps(message, default=convert_datetime)

            channel = cls.get_channel()

            # Safe declare (no-op if already declared)
            channel.exchange_declare(
                exchange=exchange, exchange_type="direct", durable=True
            )

            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=encoded_message,
                properties=pika.BasicProperties(content_type="application/json"),
            )
            logger.info(
                f"Message sent to exchange '{exchange}' with routing key '{routing_key}': {encoded_message}"
            )
        except Exception as e:
            logger.error(f"Error sending message to RabbitMQ: {str(e)}")
