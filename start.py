import uvicorn
from config.config import config
from main import app
from core.logging import get_logger

# Initialize logger
logger = get_logger()


def start():
    """Run the FastAPI application with Uvicorn"""
    logger.info(
        f"🚀 Starting server in {config.APP_ENV.upper()} mode at {config.BASE_URL}"
    )
    uvicorn.run(
        "main:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=(config.APP_ENV == "development"),
    )


if __name__ == "__main__":
    start()
