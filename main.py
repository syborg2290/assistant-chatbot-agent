from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from config.config import config
from core.logging import get_logger
from core.middleware import setup_cors, log_requests
from routers import api_router, rabbitmq_router
from utils.exceptions.custom_exceptions import CustomException
from utils.exception_handler import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    custom_exception_handler,
)

# Initialize logger
logger = get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="AI Core API",
    description="An advanced AI-powered API service.",
    version="1.0.0",
    docs_url="/docs" if config.ENABLE_SWAGGER else None,
    redoc_url="/redoc" if config.ENABLE_SWAGGER else None,
    openapi_url="/openapi.json" if config.ENABLE_SWAGGER else None,
)

# Setup Middleware
setup_cors(app)
app.middleware("http")(log_requests)

# Include all API Routers
app.include_router(api_router)

# Include rabbitmq routes
app.include_router(rabbitmq_router)

# Register global exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(CustomException, custom_exception_handler)


@app.get("/", summary="Root Endpoint", response_description="Welcome message")
async def root():
    """
    Root Endpoint

    Returns a welcome message indicating that the API is up and running.
    """
    return {"message": "Welcome to AI Core API"}


# Graceful Shutdown Hook
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Core API...")
