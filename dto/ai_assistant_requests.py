from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from utils.data_validator import ValidationUtils


class LLMModel(str, Enum):
    GEMMA = "gemma"
    DEEPSEEK_R = "deepseek-r"
    LLAMA = "llama"
    QWEN = "qwen"
    FALCON = "falcon"


class VISIONLLMModel(str, Enum):
    GEMMA = "gemma"
    LLAVA = "llava"
    LLAMA = "llama"


class AIQueryRequest(BaseModel):

    @field_validator("query")
    def validate_query(cls, value):
        value = ValidationUtils.validate_non_empty(value, "query")
        return value

    company_id: str
    data_type: str = "test"
    query: str = Field(..., min_length=1, max_length=1000)
    k: Optional[int] = 1
    metadata_filter: Optional[Dict] = None
    search_type: str = "mmr"
    temperature: Optional[float] = 0.2
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.85
    num_gpu: Optional[int] = 1
    model: LLMModel = LLMModel.DEEPSEEK_R


class AIMistralQueryRequest(BaseModel):

    @field_validator("query")
    def validate_query(cls, value):
        value = ValidationUtils.validate_non_empty(value, "query")
        return value

    company_id: str
    user_id: str
    data_type: str = "test"
    query: str = Field(..., min_length=1, max_length=1000)
    instructions: str
    k: Optional[int] = 1
    metadata_filter: Optional[Dict] = None
    search_type: str = "mmr"
    temperature: Optional[float] = 0.2
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.85
    num_gpu: Optional[int] = 1


class AICustomValidationRequest(BaseModel):
    custom_validation_rules: Dict[str, str]
    risk_threshold: str = "low"
    contents: List[str]
    model: LLMModel = LLMModel.GEMMA


class ImageAnalysisRequest(BaseModel):
    image_urls: List[str]
    company_id: Optional[str] = None
    data_type: str = "test"
    query: str = "Analyze this image"
    model: VISIONLLMModel = VISIONLLMModel.GEMMA
    # Add other parameters as needed
    k: Optional[int] = 1
    metadata_filter: Optional[Dict] = None
    search_type: str = "mmr"
