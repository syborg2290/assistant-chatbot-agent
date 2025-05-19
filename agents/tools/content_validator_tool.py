from typing import Dict, Any
from crewai.tools import BaseTool
from tools.gemma_data_validator import GemmaContentValidator
from utils.exceptions.custom_exceptions import CustomException


class ContentValidatorTool(BaseTool):
    """
    Gemma Content Validation Tool
    Features:
    - Validates text content for policy violations and risks
    - Utilizes GemmaContentValidator for risk assessment
    - Returns structured JSON output
    """

    name: str = "Content Validator Tool"
    description: str = (
        "A tool to validate content against policy violations and assess risk levels."
        """
        Runs the content validation process.
        Args:
            text (str): The content to be validated.
        Returns:
            Dict[str, Any]: Structured result from GemmaContentValidator.
        """
    )

    def __init__(
        self,
        risk_threshold: str = "medium",
        custom_validation_rules: Dict[str, str] = None,
    ):
        super().__init__()
        self.validator = GemmaContentValidator(
            risk_threshold=risk_threshold,
            custom_validation_rules=custom_validation_rules or {},
        )

    def _run(self, text: str) -> Dict[str, Any]:
        try:
            result = self.validator.validate_text(text)
            return result
        except Exception as e:
            return CustomException(500, f"Validation Error: {str(e)}")
