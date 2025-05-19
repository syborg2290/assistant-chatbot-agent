from fastapi import APIRouter
from utils.response_handler import success_response
from routers.common import router as common_router
from routers.rabbitmq import rabbitmq_router
from routers.v1 import api_router_v1

# Create a single API router that includes all sub-routers
api_router = APIRouter(prefix="/api")


# Register individual routers


@api_router.get("/")
async def api_root():
    """
    Root API Endpoint

    Returns a welcome message indicating that the API is up and running.
    """
    return success_response(message="Welcome to AI Core API")


api_router.include_router(common_router)
api_router.include_router(api_router_v1)
