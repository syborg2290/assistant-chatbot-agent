from fastapi import WebSocket, WebSocketDisconnect
import pika
import json
from loguru import logger
from config.config import config


class WebSocketServer:
    active_connections: list = {}

    @classmethod
    def register_connection(cls, websocket: WebSocket, topic: str):
        if topic not in cls.active_connections:
            cls.active_connections[topic] = []
        cls.active_connections[topic].append(websocket)

    @classmethod
    def unregister_connection(cls, websocket: WebSocket, topic: str):
        if topic in cls.active_connections:
            cls.active_connections[topic].remove(websocket)
            if not cls.active_connections[topic]:
                del cls.active_connections[topic]

    @classmethod
    async def broadcast(cls, message: str, topic: str):
        if topic in cls.active_connections:
            for connection in cls.active_connections[topic]:
                await connection.send_text(message)


async def send_rabbitmq_messages_to_websocket(websocket: WebSocket, queue: str):
    await websocket.accept()
    WebSocketServer.register_connection(websocket, queue)

    try:
        # Establish RabbitMQ connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.RABBITMQ_HOST)
        )
        channel = connection.channel()

        # Declare the queue (if not already declared)
        channel.queue_declare(queue=queue, durable=True)

        def callback(ch, method, properties, body):
            message = json.loads(
                body.decode("utf-8")
            )  # Deserialize RabbitMQ message to JSON
            # Send the message to the WebSocket client
            websocket.send_text(json.dumps(message))
            logger.info(f"Message sent to WebSocket (Queue: {queue}): {message}")

        # Start consuming messages from the RabbitMQ queue
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

        # Start consuming messages in the background
        channel.start_consuming()

    except WebSocketDisconnect:
        WebSocketServer.unregister_connection(websocket, queue)
        logger.info(f"WebSocket connection disconnected from queue {queue}")

    except Exception as e:
        logger.error(f"Error in RabbitMQ consumer: {str(e)}")
        await websocket.close()
