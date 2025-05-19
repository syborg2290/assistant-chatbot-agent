from typing import Dict
from presidio_analyzer import AnalyzerEngine


class ValidationUtils:
    """
    Utility class for performing various validation checks, including PII detection.
    """

    analyzer = AnalyzerEngine()

    @classmethod
    def validate_pii(cls, text: str) -> None:
        """
        Validates that the given text does not contain any PII.

        :param text: The text content to check for PII.
        :raises ValueError: If PII is detected in the text.
        
        PII detected in document:
        Type: EMAIL_ADDRESS, Redacted Value: *******************, Confidence: 0.92, Position: [14-35]
        Type: PHONE_NUMBER, Redacted Value: **********, Confidence: 0.85, Position: [45-57]

        """
        results = cls.analyzer.analyze(text=text, language="en")
        if results:
            pii_details = []
            for result in results:
                # Redact the detected PII value by replacing it with asterisks of the same length
                redacted_value = "*" * (result.end - result.start)
                pii_details.append(
                    f"Type: {result.entity_type}, Redacted Value: {redacted_value}, "
                    f"Confidence: {result.score:.2f}, Position: [{result.start}-{result.end}]"
                )

            # Join all PII details into a single error message
            error_message = "PII detected in document:\n" + "\n".join(pii_details)
            raise ValueError(error_message)

    @classmethod
    def validate_non_empty(cls, value: str, field_name: str) -> str:
        """
        Validates that the given value is a non-empty string.

        :param value: The string to validate.
        :param field_name: The name of the field being validated.
        :return: The validated value.
        :raises ValueError: If the value is empty or contains only whitespace.
        """
        if not value.strip():
            raise ValueError(f"{field_name} cannot be empty or just whitespace.")
        return value

    @classmethod
    def validate_metadata(cls, metadata: Dict[str, str]) -> Dict[str, str]:
        """
        Validates that the metadata is a non-empty dictionary with non-empty keys and values.

        :param metadata: The metadata dictionary to validate.
        :return: The validated metadata dictionary.
        :raises ValueError: If the metadata is invalid.
        """
        if not isinstance(metadata, dict) or not metadata:
            raise ValueError("Metadata must be a non-empty dictionary.")
        for key, val in metadata.items():
            cls.validate_non_empty(key, "Metadata key")
            cls.validate_pii(key)
            cls.validate_non_empty(val, "Metadata value")
            cls.validate_pii(val)
        return metadata
