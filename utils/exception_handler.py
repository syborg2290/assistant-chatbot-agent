from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from utils.exceptions.custom_exceptions import CustomException


async def global_exception_handler(request: Request, exc: Exception):
    """Handles all unhandled exceptions globally"""
    logger.error(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(
        content={"status": "error", "message": "An unexpected error occurred"},
        status_code=500,
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles FastAPI's HTTPException"""
    return JSONResponse(
        content={"status": "error", "message": exc.detail},
        status_code=exc.status_code,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles validation errors (e.g., missing or invalid fields in requests)"""
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation error",
            "errors": exc.errors(),
        },
    )


async def custom_exception_handler(request: Request, exc: CustomException):
    """Handles custom business logic exceptions"""
    logger.warning(f"🚨 Custom Exception: {exc.detail} (Code: {exc.status_code})")
    return JSONResponse(
        content={"status": "error", "message": exc.detail},
        status_code=exc.status_code,
    )
