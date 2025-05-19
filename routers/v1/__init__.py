from fastapi import APIRouter
from routers.v1.company import router as company_router
from routers.v1.ai_assistant import router as ai_assistant_router
from routers.v1.crew_agent import router as crew_agent_router
from routers.v1.chatbot import router as chatbot_router

# Create a single API router that includes all sub-routers
api_router_v1 = APIRouter(prefix="/v1")

# Register individual routers
api_router_v1.include_router(company_router)
api_router_v1.include_router(ai_assistant_router)
api_router_v1.include_router(crew_agent_router)
api_router_v1.include_router(chatbot_router)
