from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional, Any
from utils.data_validator import ValidationUtils


# class SearchType(str, Enum):
#     MMR = "mmr"
#     SIMILARITY = "similarity"


class Document(BaseModel):
    page_content: str = Field(
        ..., min_length=1, max_length=5000, description="Content of the document"
    )
    metadata: Dict[str, str] = Field(
        ..., description="Metadata associated with the document"
    )
    id: str = Field(..., min_length=1, description="Unique identifier for the document")

    @field_validator("page_content")
    def validate_page_content(cls, value):
        value = ValidationUtils.validate_non_empty(value, "Page content")
        return value

    # @field_validator("metadata")
    # def validate_metadata(cls, value):
    #     return ValidationUtils.validate_metadata(value)

    @field_validator("id")
    def validate_id(cls, value):
        return ValidationUtils.validate_non_empty(value, "ID")


# Example usage
# document_1 = Document(
#     page_content="I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",
#     metadata={"source": "tweet"},
#     id=1,
# )


class AddDocumentRequest(BaseModel):
    company_id: str
    documents: list[dict]
    data_type: str = "test"  # "live", "test" or "hold" and "corrections"


class QueryRequest(BaseModel):
    company_id: str
    data_type: str = "test"  # "live", "test" or "hold" and "corrections"
    query: str
    k: int = 1
    metadata_filter: dict = None
    search_type: str = "mmr"


class DeleteDocumentRequest(BaseModel):
    company_id: str
    metadata_id: str
    data_type: str = "test"


# {
#     "company_id": "123",
#     "user_id": "user_456",
#     "chat_content": """{
#         "User: How do I reset my password?\n"
#         "Assistant: Go to Settings > Security > Reset Password.\n"
#         "User: That worked, thanks!"
#     }""",
#     "feedback_type": "positive",
#     "feedback_reason": "Helpful instructions",
#     "additional_metadata": {"session_id": "abc123"},
# }


class ChatFeedbackRequest(BaseModel):
    company_id: str
    user_id: str
    chat_content: str
    feedback_type: str
    feedback_reason: str
    additional_metadata: Optional[Dict[str, Any]] = None


class CompanyFeedbackRequest(BaseModel):
    company_id: str
    k: int = 50
    filters: Optional[Dict[str, Any]] = None


class UserFeedbackRequest(BaseModel):
    company_id: str
    user_id: str
    k: int = 20
    filters: Optional[Dict[str, Any]] = None
