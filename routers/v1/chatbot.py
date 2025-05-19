from fastapi import APIRouter, Request
from services.chat_service import (
    start_conversation_service,
    chat_service,
    feedback_service,
)
# from services.chat_service_vllm import (
#     start_conversation_service_vllm,
#     chat_service_vllm,
#     feedback_service_vllm,
# )
from utils.response_handler import success_response
from dto.chatbot_requests import ChatRequest, FeedbackRequest, StartRequest

# Initialize FastAPI router
router = APIRouter(prefix="/chat", tags=["Chat Service v.1"])


@router.post("/start")
async def start_conversation(req: StartRequest, request: Request):
    client_ip = request.client.host
    result = start_conversation_service(
        client_ip=client_ip,
        message=req.message,
        company_id=req.company_id,
        user_id=req.user_id,
        data_type=req.data_type,
        custom_user_instructions=req.custom_user_instructions,
        company_name=req.company_name,
        company_website=req.company_website,
        assistant_role=req.assistant_role,
        assistant_name=req.assistant_name,
        main_domains=req.main_domains,
        sub_domains=req.sub_domains,
        support_contact_emails=req.support_contact_emails,
        support_phone_numbers=req.support_phone_numbers,
        support_page_url=req.support_page_url,
        help_center_url=req.help_center_url,
    )
    return success_response(data=result)


@router.post("/message")
async def chat(req: ChatRequest):
    result = chat_service(req.thread_id, req.message)
    return success_response(data=result)


@router.post("/feedback")
async def feedback(req: FeedbackRequest):
    result = feedback_service(req.thread_id, req.feedback)
    return success_response(data=result)


# @router.post("/start-vllm")
# async def start_conversation(req: StartRequest, request: Request):
#     client_ip = request.client.host
#     result = start_conversation_service_vllm(
#         client_ip=client_ip,
#         message=req.message,
#         company_id=req.company_id,
#         user_id=req.user_id,
#         data_type=req.data_type,
#         custom_user_instructions=req.custom_user_instructions,
#         company_name=req.company_name,
#         company_website=req.company_website,
#         assistant_role=req.assistant_role,
#         assistant_name=req.assistant_name,
#         main_domains=req.main_domains,
#         sub_domains=req.sub_domains,
#         support_contact_emails=req.support_contact_emails,
#         support_phone_numbers=req.support_phone_numbers,
#         support_page_url=req.support_page_url,
#         help_center_url=req.help_center_url,
#     )
#     return success_response(data=result)


# @router.post("/message-vllm")
# async def chat(req: ChatRequest):
#     result = chat_service_vllm(req.thread_id, req.message)
#     return success_response(data=result)


# @router.post("/feedback-vllm")
# async def feedback(req: FeedbackRequest):
#     result = feedback_service_vllm(req.thread_id, req.feedback)
#     return success_response(data=result)
