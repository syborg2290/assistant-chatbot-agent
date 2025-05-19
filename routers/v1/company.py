from fastapi import APIRouter
from dto.company_requests import (
    AddDocumentRequest,
    QueryRequest,
    DeleteDocumentRequest,
    ChatFeedbackRequest,
    CompanyFeedbackRequest,
    UserFeedbackRequest,
)
from services.vector_db import chroma_service
from utils.response_handler import success_response

router = APIRouter(prefix="/company", tags=["Company Vector Operations v.1"])


# Route for adding a document to the collection
@router.post("/add_document")
async def add_document(request: AddDocumentRequest):
    """Adds a document with a vector to the company's collection under 'live', 'test', or 'hold' and 'corrections'."""
    result = chroma_service.add_documents_to_collection_langchain(
        company_id=request.company_id,
        data_type=request.data_type,
        documents=request.documents,
    )
    # Call the service method to add the document
    return success_response(data=result)


# Route for querying documents from a collection
@router.post("/query")
async def query_documents(request: QueryRequest):
    """Queries the nearest documents from the company's collection filtering by 'live', 'test', or 'hold' and 'corrections'."""
    return success_response(
        chroma_service.query_with_langchain(
            request.company_id,
            request.query,
            request.data_type,
            k=request.k,
            metadata_filter=request.metadata_filter,
            search_type=request.search_type,
        )
    )


# Route for deleting a document from the collection
@router.delete("/delete_document")
async def delete_document(request: DeleteDocumentRequest):
    """Deletes a document from a company's collection under 'live', 'test', or 'hold' and 'corrections'."""
    return success_response(
        chroma_service.delete_document(
            request.company_id, request.metadata_id, request.data_type
        )
    )


# Route for listing all collections in ChromaDB
@router.get("/list_collections")
async def list_collections():
    """Lists all collections stored in ChromaDB"""
    return success_response({"collections": chroma_service.list_all_collections()})


# Route for deleting all collections for a given company
@router.delete("/delete_company/{company_id}")
async def delete_company_collections(company_id: str):
    """Deletes live, test, corrections and hold collections for a given company"""
    return success_response(chroma_service.delete_company_collection(company_id))


# New Route for listing all documents in a collection
@router.get("/list_documents/{company_id}/{data_type}")
async def list_all_documents_in_collection(company_id: str, data_type: str):
    """Lists all documents in the company's collection under the specified 'live', 'test', or 'hold' and 'corrections'."""

    return success_response(
        data=chroma_service.list_all_documents_in_collection_langchain(
            company_id, data_type
        )
    )


# New Route for deleting documents from a collection by metadata
@router.delete("/delete_documents/{company_id}/{data_type}")
async def delete_documents_from_collection_by_metadata(
    company_id: str, data_type: str, metadata_filter: dict
):

    return success_response(
        chroma_service.delete_documents_from_collection_langchain_metadata(
            company_id, data_type, metadata_filter
        )
    )


@router.post("/feedback/store")
async def store_chat_feedback(request: ChatFeedbackRequest):
    """Store user feedback with chat conversation history"""
    result = chroma_service.add_chat_feedback(
        company_id=request.company_id,
        user_id=request.user_id,
        chat_content=request.chat_content,
        feedback_type=request.feedback_type,
        feedback_reason=request.feedback_reason,
        additional_metadata=request.additional_metadata,
    )
    return success_response(result)


@router.post("/feedback/company")
async def get_company_feedback(request: CompanyFeedbackRequest):
    """Retrieve feedback entries for a specific company"""

    results = chroma_service.get_company_feedbacks(
        company_id=request.company_id, k=request.k, filters=request.filters
    )
    return success_response(
        {
            "company_id": request.company_id,
            "count": len(results),
            "feedbacks": results,
        }
    )


@router.post("/feedback/user")
async def get_user_feedback(request: UserFeedbackRequest):
    """Retrieve feedback entries for a specific user"""
    results = chroma_service.get_user_feedbacks(
        company_id=request.company_id,
        user_id=request.user_id,
        k=request.k,
        filters=request.filters,
    )
    return success_response(
        {
            "company_id": request.company_id,
            "user_id": request.user_id,
            "count": len(results),
            "feedbacks": results,
        }
    )


@router.delete("/feedback/user/{company_id}/{user_id}")
async def delete_user_feedback(company_id: str, user_id: str):
    """Delete all feedback entries for a specific user"""
    result = chroma_service.delete_user_feedback(company_id, user_id)
    return success_response(result)
