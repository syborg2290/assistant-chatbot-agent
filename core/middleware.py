import time
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from config.config import config


def setup_cors(app):
    """Configures CORS for FastAPI."""
    origins = ["*"] if config.APP_ENV == "development" else config.ALLOWED_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def log_requests(request: Request, call_next):
    """Middleware for logging API requests."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        {
            "env": config.APP_ENV.upper(),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration": f"{duration:.2f}s",
        }
    )
    return response
