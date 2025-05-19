from typing import Dict, Any
from crewai.tools import BaseTool
from tools.gemma_image_analyzer import EnhancedGemmaVisionAnalyzer
from utils.exceptions.custom_exceptions import CustomException


class VisionAnalyzerTool(BaseTool):
    """
    Gemma Vision Analysis Tool
    Features:
    - Analyzes images for policy violations, risks, and violations of content standards.
    - Utilizes EnhancedGemmaVisionAnalyzer for robust image content analysis.
    - Provides detailed risk levels and flagging information.

    Args:
        is_use_vectordb (bool): Whether to use a vector database for storing and retrieving image data (default: False).

    Params:
        image_url (str): URL of the image to be analyzed.

    Returns:
        Dict[str, Any]: Structured result
    """

    name: str = "Vision Analyzer Tool"
    description: str = (
        "A tool to analyze image content for policy violations, risks, and content standards using Gemma's "
        "advanced vision analysis techniques. It identifies potential issues and provides structured risk assessment."
        """
        Runs the image analysis process.

        Args:
            image_url (str): URL to the image to be analyzed.

        Returns:
            Dict[str, Any]: Structured result contain various data,metadata and more.
        """
    )
    is_use_vectordb: bool = False

    def __init__(self, is_use_vectordb: bool = False):
        super().__init__()
        self.is_use_vectordb = is_use_vectordb
        self._analyzer = EnhancedGemmaVisionAnalyzer(is_use_vectordb=is_use_vectordb)

    def _run(self, image_url: str) -> Dict[str, Any]:
        try:
            result = self._analyzer.analyze(image_url=image_url)
            return result
        except Exception as e:
            # Return structured error information with status code and message
            return CustomException(500, f"Analysis Error: {str(e)}").to_dict()
