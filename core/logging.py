from loguru import logger
from config.config import config

# Structured Logging Configuration
logger.add(
    "logs/app.json",
    rotation="1 day",
    retention="7 days",
    level=config.LOG_LEVEL,
    format="{time} | {level} | {message}",
    serialize=True,  # JSON logs for structured logging
)


def get_logger():
    return logger
