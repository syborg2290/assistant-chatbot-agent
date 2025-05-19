import json
import re
import time
from datetime import datetime
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_ollama import OllamaLLM
from utils.generation_time_formatter import format_generation_time
from config.config import config


class LlamaContentValidator:
    """
    Comprehensive content validation system using Llama via Ollama.
    Features:
    - Structured JSON output parsing
    - Risk threshold configuration
    - Validation history tracking
    - Content moderation rules integration
    """

    def __init__(
        self,
        custom_validation_rules: Dict[str, str] = [],
        risk_threshold: str = "medium",
    ):
        self.risk_threshold = risk_threshold
        self.custom_validation_rules = custom_validation_rules
        self.llm = self._initialize_model()
        self.chain = self._create_validation_chain()
        self.history = []
        self.risk_levels = ["low", "medium", "high"]
        self.validation_rules = self._load_validation_rules()

    def _initialize_model(self):
        """Configure the Ollama LLM instance"""
        return OllamaLLM(
            model=config.LLAMA_LLM_OLLAMA,
            temperature=0.1,
            top_k=50,
            top_p=0.85,
            num_gpu=1,
            system=(
                "You are a security AI analyst specialized in content moderation. "
                "Provide accurate, conservative assessments with clear justifications."
            ),
        )

    def _create_validation_chain(self):
        """Build the LangChain validation pipeline"""
        validation_prompt = PromptTemplate(
            template="""
            <start>
            **Content Analysis Request**
            Analyze this text for policy violations and risks (threshold: {risk_threshold}):
            ----------------------------------
            {text}
            ----------------------------------

            **Validation Rules**
            {validation_rules}
            
            **Custom Validation Rules**
            {custom_validation_rules}
            
            **sample_critical_patterns**
            {sample_critical_patterns}

            **Response Format (JSON ONLY)**
            {{
                "risk_level": "low|medium|high",
                "flags": ["category1", "category2"],
                "excerpts": ["offensive text snippet"],
                "confidence": 0-100,
                "explanation": "detailed analysis rationale"
            }}
            <end>
            """,
            input_variables=[
                "text",
                "risk_threshold",
                "validation_rules",
                "custom_validation_rules",
                "sample_critical_patterns",
            ],
        )

        return LLMChain(llm=self.llm, prompt=validation_prompt, verbose=False)

    def _load_validation_rules(self):
        """Load validation rules for content moderation"""
        return {
            "illegal_activities": "Illegal activities like drugs, weapons, trafficking",
            "hate_speech": "Hate speech or discrimination",
            "sexual_content": "Sexual content or exploitation",
            "pii": "Personal information like social security numbers, high security credentials, Sensitive data (Ignore emails/contact numbers/telephone numbers/address)",
            "violence": "Violence, terrorism, or extremism",
            "copyright": "Copyright violations",
            "toxic_content": "Toxic or harassment content",
            "sensitive_content": "Sensitive personal/medical/payment/security content",
        }

    def _build_critical_patterns(self) -> Dict[str, Dict]:
        """Targeted patterns for high-risk sensitive data"""
        return {
            # Credential patterns
            "plaintext_credential": {
                "pattern": r"(?i)\b(password|passwd|pwd|secret|key|token|credential)\s*[:=]\s*[\"']?[^\s\"']{8,}",
                "validation": None,
            },
            # Payment processing information
            "payment_processor_token": {
                "pattern": r"\b(sk|pk)_(test|live)_[a-zA-Z0-9]{24}\b",
                "validation": None,
            },
            # Cryptographic material
            "private_key": {
                "pattern": r"-{5}BEGIN (RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-{5}",
                "validation": None,
            },
            # Security tokens
            "jwt_token": {
                "pattern": r"\beyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*\b",
                "validation": None,
            },
            # Financial instrument patterns
            "swift_code": {
                "pattern": r"\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b",
                "validation": None,
            },
            # Government documents
            "passport_number": {
                "pattern": r"\b(?!^0+$)[A-Z]{1,2}[0-9]{6,9}\b",
                "validation": None,
            },
            # Cloud service credentials
            "aws_key": {"pattern": r"\b(AKIA|ASIA)[A-Z0-9]{16}\b", "validation": None},
            # Cryptocurrency addresses
            "crypto_wallet": {
                "pattern": r"\b(0x)?[0-9a-fA-F]{40}\b|\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b",
                "validation": None,
            },
        }

    def validate_text(self, text: str) -> Dict[str, Any]:
        """Validate text content and return structured results"""
        try:
            # Prepare inputs
            inputs = {
                "text": text,
                "risk_threshold": self.risk_threshold,
                "validation_rules": "\n".join(
                    f"- {k}: {v}" for k, v in self.validation_rules.items()
                ),
                "custom_validation_rules": self.custom_validation_rules,
                "sample_critical_patterns": self._build_critical_patterns(),
            }

            # Measure generation time
            start_time = time.time()

            # Run validation chain
            raw_response = self.chain.invoke(inputs)["text"]

            generation_time = time.time() - start_time

            # Parse and process response
            parsed = self._parse_response(raw_response)

            parsed["generation_time"] = (format_generation_time(generation_time),)

            self._log_validation(text, parsed)

            return parsed

        except Exception as e:
            error_result = self._error_result(f"Validation failed: {str(e)}")
            error_result["generation_time"] = format_generation_time(
                0.0
            )  # Default for error cases
            return error_result

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Convert raw text response to structured data"""
        try:
            # Clean and extract JSON
            json_str = re.search(r"\{.*?\}", response, re.DOTALL).group()
            data = json.loads(json_str)

            # Validate structure
            required_keys = ["risk_level", "flags", "explanation"]
            if not all(key in data for key in required_keys):
                raise ValueError("Invalid response format")

            # Normalize risk level
            data["risk_level"] = data["risk_level"].lower()
            if data["risk_level"] not in self.risk_levels:
                data["risk_level"] = "unknown"

            # Add blocking decision
            data["should_block"] = self._should_block(data["risk_level"])

            return data

        except Exception as e:
            raise

    def _should_block(self, risk_level: str) -> bool:
        """Determine if content should be blocked based on risk level"""
        current_index = self.risk_levels.index(risk_level)
        threshold_index = self.risk_levels.index(self.risk_threshold)
        return current_index >= threshold_index

    def _log_validation(self, text: str, result: Dict):
        """Store validation results in history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text_snippet": text[:200] + "..." if len(text) > 200 else text,
            "result": result,
            "decision": "blocked" if result.get("should_block", False) else "allowed",
        }
        self.history.append(entry)

    def _error_result(self, message: str) -> Dict[str, Any]:
        """Standard error response format"""
        return {
            "error": message,
            "risk_level": "unknown",
            "should_block": True,
            "flags": ["validation_error"],
        }


# # Example Usage
# if __name__ == "__main__":
#     validator = LlamaContentValidator(risk_threshold="medium")

#     # Test Cases for Validation
#     test_cases = [
#         "Just a normal harmless message.",
#         "Selling unlicensed firearms, contact me at 123-456-7890.",
#         "My social security number is 123-45-6789.",
#         "AWS Configuration: AWS_ACCESS_KEY_ID=AKIAEXAMPLEKEY123 / AWS_SECRET_ACCESS_KEY=EXAMPLE/SECRET/KEY/123456",
#     ]

#     # Running test cases
#     for text in test_cases:
#         validation_result = validator.validate_text(text)
#         print(f"Text: {text}\nValidation: {validation_result}\n")
