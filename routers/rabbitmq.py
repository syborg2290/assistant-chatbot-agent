from fastapi import APIRouter, WebSocket
from loguru import logger
from config.rabbitmq import RabbitMQConfig
# from websocket_server import send_rabbitmq_messages_to_websocket

# Create an APIRouter for RabbitMQ-related routes
rabbitmq_router = APIRouter()


# RabbitMQ message sending endpoint (HTTP-based)
@rabbitmq_router.post("/send_message/")
async def send_message_to_rabbitmq(queue: str, key: str, message: dict):
    try:
        rabbitmq = RabbitMQConfig()

        rabbitmq.send_message(queue, key, message)

        return {
            "status": "Message sent to RabbitMQ successfully",
            "queue": queue,
            "message": message,
        }
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return {"status": "Failed to send message", "error": str(e)}


# WebSocket route to stream RabbitMQ messages
# @rabbitmq_router.websocket("/ws/rabbitmq/{queue}")
# async def websocket_rabbitmq_connection(websocket: WebSocket, queue: str):
#     """
#     WebSocket route that accepts dynamic RabbitMQ queue names.
#     It listens to the specified RabbitMQ queue and streams messages in real-time.
#     """
#     await send_rabbitmq_messages_to_websocket(websocket, queue)
