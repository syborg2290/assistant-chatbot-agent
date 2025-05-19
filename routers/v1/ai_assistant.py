from fastapi import APIRouter
from services.tools_communicator import tools_communicator
from utils.response_handler import success_response
from dto.ai_assistant_requests import (
    AIQueryRequest,
    AIMistralQueryRequest,
    AICustomValidationRequest,
    ImageAnalysisRequest,
)

router = APIRouter(prefix="/ai", tags=["AI Assistant v.1"])


@router.post("/query")
async def query_ai(request: AIQueryRequest):
    """Query the AI assistant for insights based on vectorized data.

    *** Number of Final Results to Return ***
    k determines how many relevant documents will be returned after applying ranking methods (like MMR).

    Example: If k=3, it returns the top 3 most relevant documents.

    *** filter: Metadata-Based Filtering ***
    This applies filtering based on specific metadata fields (e.g., company_id, data_type).

    If metadata_filter is None, it defaults to {} (an empty filter, meaning no filtering is applied).

    *** search_type (mmr/similarity) ***
    Similarity Search: If a user liked a specific movie, the system will recommend movies that are highly similar to the one they liked.
    MMR Search: The system might recommend movies that are similar to the one the user liked but will also add diverse recommendations,
                such as different genres, actors, or themes, to give the user a broader selection.

    """
    response = tools_communicator.query_ai(
        company_id=request.company_id,
        data_type=request.data_type,
        query=request.query,
        k=request.k,
        metadata_filter=request.metadata_filter,
        search_type=request.search_type,
        temperature=request.temperature,
        top_k=request.top_k,
        top_p=request.top_p,
        num_gpu=request.num_gpu,
        model=request.model,
    )
    return success_response(response)


@router.post("/validate")
async def validate_content(request: AICustomValidationRequest):
    """Validate content using Gemma3 AI tool.

    *** custom_validation_rules ***
    Defines custom validation rules to be applied.

    *** risk_threshold ***
    Sets the risk level threshold for validation (e.g., low, medium, high).

    *** contents ***
    A list of contents to be validated
    """
    response = tools_communicator.content_validator_ai(
        custom_validation_rules=request.custom_validation_rules,
        risk_threshold=request.risk_threshold,
        contents=request.contents,
        model=request.model,
    )
    return success_response(response)


@router.post("/analyze-images")
async def analyze_images(request: ImageAnalysisRequest):
    """Analyze images using GEMMA's vision capabilities

    *** image_urls ***
    List of image URLs to analyze (required)

    *** analysis_types ***
    List of analysis components to include:
    - objects: Detected objects with positions
    - colors: Dominant color palette
    - caption: Descriptive caption
    - text_present: Any visible text
    - estimated_context: Scene context

    *** company_id/data_type ***
    Optional VectorDB context for analysis

    Example Request:
    {
        "image_urls": ["https://example.com/image1.jpg"],
        "company_id": "retail_co",
        "data_type": "product_images",
        "query": "Identify products in image"
    }
    """
    response = tools_communicator.analyze_images_ai(
        image_urls=request.image_urls,
        company_id=request.company_id,
        data_type=request.data_type,
        query=request.query,
        model=request.model,
        k=request.k,
        metadata_filter=request.metadata_filter,
        search_type=request.search_type,
    )
    return success_response(response)


@router.post("/mistral-chat")
async def mistral_chat(request: AIMistralQueryRequest):
    """Interact with the Mistral AI tool for chat queries."""
    response = tools_communicator.mistral_chat(
        company_id=request.company_id,
        user_id=request.user_id,
        data_type=request.data_type,
        query=request.query,
        user_instructions=request.instructions,
        k=request.k,
        metadata_filter=request.metadata_filter,
        search_type=request.search_type,
        temperature=request.temperature,
        top_k=request.top_k,
        top_p=request.top_p,
        num_gpu=request.num_gpu,
    )
    return success_response(response)
