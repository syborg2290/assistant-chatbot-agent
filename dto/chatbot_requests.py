from pydantic import BaseModel


class StartRequest(BaseModel):
    message: str
    company_id: str
    user_id: str
    data_type: str
    custom_user_instructions: str
    company_name: str
    company_website: str
    assistant_role: str
    assistant_name: str
    main_domains: str
    sub_domains: str
    support_contact_emails: str
    support_phone_numbers: str
    support_page_url: str
    help_center_url: str


class ChatRequest(BaseModel):
    thread_id: str
    message: str


class FeedbackRequest(BaseModel):
    thread_id: str
    feedback: str
