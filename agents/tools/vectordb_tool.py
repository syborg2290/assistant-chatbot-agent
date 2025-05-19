from crewai.tools import BaseTool
from typing import List, Optional
from services.vector_db import chroma_service
from utils.exceptions.custom_exceptions import CustomException


class DocumentSearchTool(BaseTool):
    """
    A tool for searching documents based on a given query across multiple data types.
    """

    name: str = "Document Search Tool"
    description: str = (
        "Searches specific documents using a query string across multiple data types "
        "such as 'live', 'test', and 'corrections'. Returns the most relevant results."
        """
        Parameters:
        - query (str): The search query string.
        - data_types (List[str]): A list of data types to search in. Default is ["live", "test", "corrections"].
        - k (int): The maximum number of results to return. Default is 10.

        Returns:
        - str: Formatted search results or an error message.
        """,
    )

    def __init__(self, company_id: str, **kwargs):
        super().__init__(**kwargs)
        self.company_id = company_id

    def _run(
        self,
        query: str,
        data_types: List[str] = ["live", "test", "corrections"],
        k: int = 10,
    ) -> str:

        try:
            all_results = []
            for data_type in data_types:
                results = chroma_service.query_with_langchain(
                    company_id=self.company_id,
                    query=query,
                    data_type=data_type,
                    k=k,
                )
                all_results.extend(results)

            return (
                self._format_results(all_results)
                if all_results
                else "No documents found"
            )

        except Exception as e:
            return CustomException(
                status_code=500,
                detail=f"Search Error: {e.detail}",
            )

    def _format_results(self, results: List[dict]) -> str:
        """
        Formats the search results for display.

        Parameters:
        - results (List[dict]): A list of result dictionaries containing metadata and content.

        Returns:
        - str: Formatted string of the top search results.
        """
        return "\n".join(
            f"[{res['metadata'].get('source', 'unknown')}] {res['content'][:200]}..."
            for res in results
        )


class CompanyFeedbackTool(BaseTool):
    """
    A tool to retrieve and analyze feedback related to a specific company.
    """

    name: str = "Company Feedback Tool"
    description: str = (
        "Fetches feedback data for a specific company based on a given query and optional filters. "
        "Allows for customized search results and relevance scoring."
        """
        Runs the company feedback tool.

        Parameters:
        - query (str): The search query to look for relevant feedback.
        - filters (Optional[dict]): A dictionary of filters to narrow down the results.
        - k (int): The maximum number of results to return. Default is 10.

        Returns:
        - str: Formatted feedback results or an error message.
        """
    )

    def __init__(self, company_id: str, **kwargs):
        super().__init__(**kwargs)
        self.company_id = company_id

    def _run(
        self,
        query: str,
        filters: Optional[dict] = None,
        k: int = 10,
    ) -> str:

        try:
            feedbacks = chroma_service.get_company_feedbacks(
                company_id=self.company_id,
                query=query,
                k=k,
                filters=filters,
            )

            return (
                self._format_results(feedbacks)
                if feedbacks
                else "No company feedback found"
            )

        except Exception as e:
            return CustomException(
                status_code=500,
                detail=f"Company Feedback Retrieval Error: {str(e)}",
            )

    def _format_results(self, feedbacks: List[dict]) -> str:
        """
        Formats the feedback results for display.

        Parameters:
        - feedbacks (List[dict]): A list of feedback dictionaries containing relevance scores and content.

        Returns:
        - str: Formatted string of the top feedback results.
        """
        return "\n".join(
            f"[Company ID: {self.company_id}] Relevance: {fb['relevance_score']} - {fb['content'][:150]}..."
            for fb in feedbacks
        )


class UserFeedbackTool(BaseTool):
    """
    A tool to retrieve and analyze feedback specific to a user within a company.
    """

    name: str = "User Feedback Tool"
    description: str = (
        "Fetches feedback data specific to a user within a company based on a given query and optional filters. "
        "Returns the most relevant feedback sorted by relevance score."
        """
        Runs the user feedback tool.

        Parameters:
        - user_id (str): The ID of the user whose feedback is being retrieved.
        - query (str): The search query to filter feedback.
        - filters (Optional[dict]): Additional criteria to filter the feedback results.
        - k (int): The number of results to return. Default is 10.

        Returns:
        - str: Formatted feedback results or an error message.
        """
    )

    def __init__(self, company_id: str, **kwargs):
        super().__init__(**kwargs)
        self.company_id = company_id

    def _run(
        self,
        user_id: str,
        query: str,
        filters: Optional[dict] = None,
        k: int = 10,
    ) -> str:

        try:
            feedbacks = chroma_service.get_user_feedbacks(
                company_id=self.company_id,
                user_id=user_id,
                query=query,
                k=k,
                filters=filters,
            )

            return (
                self._format_results(feedbacks)
                if feedbacks
                else "No user feedback found"
            )

        except Exception as e:
            return CustomException(
                status_code=500,
                detail=f"User Feedback Retrieval Error: {str(e)}",
            )

    def _format_results(self, feedbacks: List[dict]) -> str:
        """
        Formats the user feedback results for display.

        Parameters:
        - feedbacks (List[dict]): A list of feedback dictionaries containing relevance scores and content.

        Returns:
        - str: Formatted string of the top feedback results.
        """
        return "\n".join(
            f"[User ID: {self.company_id}] Relevance: {fb['relevance_score']} - {fb['content'][:150]}..."
            for fb in feedbacks
        )
