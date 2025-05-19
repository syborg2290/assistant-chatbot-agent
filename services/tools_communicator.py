import gc
from tools.gemma_vectordb import GemmaVectorDB
from tools.deepseek_r_vectordb import DeepSeekVectorDB
from tools.falcon_vectordb import FalconVectorDB
from tools.llama_vectordb import LlamaVectorDB
from tools.qwen_vectordb import QwenVectorDB

from tools.gemma_data_validator import GemmaContentValidator
from tools.deepseek_r_data_validator import DeepSeekContentValidator
from tools.falcon_data_validator import FalconContentValidator
from tools.llama_data_validator import LlamaContentValidator
from tools.qwen_data_validator import QwenContentValidator
from tools.gemma_image_analyzer import EnhancedGemmaVisionAnalyzer
from tools.llava_image_analyzer import EnhancedLlavaVisionAnalyzer
from tools.llama_image_analyzer import EnhancedLlamaVisionAnalyzer

from tools.mistral_user import MistralUserHandler
from typing import Dict, List
from dto.ai_assistant_requests import LLMModel, VISIONLLMModel


class ToolsCommunicatorService:
    """Service layer to handle AI tool interactions."""

    @staticmethod
    def mistral_chat(
        company_id,
        user_id,
        data_type,
        query,
        user_instructions,
        k,
        metadata_filter,
        search_type,
        temperature,
        top_k,
        top_p,
        num_gpu,
    ):
        try:
            mistral_user_handler = MistralUserHandler()
            return mistral_user_handler.query(
                company_id=company_id,
                user_id=user_id,
                data_type=data_type,
                query=query,
                user_instructions=user_instructions,
                k=k,
                metadata_filter=metadata_filter,
                search_type=search_type,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                num_gpu=num_gpu,
            )

        except Exception as e:
            raise e
        finally:
            gc.collect()

    @staticmethod
    def query_ai(
        company_id,
        data_type,
        query,
        k,
        metadata_filter,
        search_type,
        temperature,
        top_k,
        top_p,
        num_gpu,
        model: LLMModel = LLMModel.DEEPSEEK_R,
    ):
        try:
            """Queries the AI tool based on the model type."""
            match model:
                case LLMModel.DEEPSEEK_R:
                    query_model = DeepSeekVectorDB()

                case LLMModel.FALCON:
                    query_model = FalconVectorDB()

                case LLMModel.GEMMA:
                    query_model = GemmaVectorDB()

                case LLMModel.LLAMA:
                    query_model = LlamaVectorDB()

                case LLMModel.QWEN:
                    query_model = QwenVectorDB()
                case _:
                    raise

            return query_model.query(
                company_id,
                data_type,
                query,
                k,
                metadata_filter,
                search_type,
                temperature,
                top_k,
                top_p,
                num_gpu,
            )

        except Exception as e:
            raise e
        finally:
            gc.collect()

    @staticmethod
    def content_validator_ai(
        custom_validation_rules: Dict[str, str] = [],
        risk_threshold: str = "medium",
        contents: list[str] = [],
        model: LLMModel = LLMModel.GEMMA,
    ):
        try:
            """Call the appropriate validation AI tool based on the model type."""
            match model:
                case LLMModel.GEMMA:
                    validator = GemmaContentValidator(
                        custom_validation_rules=custom_validation_rules,
                        risk_threshold=risk_threshold,
                    )
                case LLMModel.DEEPSEEK_R:
                    validator = DeepSeekContentValidator(
                        custom_validation_rules=custom_validation_rules,
                        risk_threshold=risk_threshold,
                    )
                case LLMModel.FALCON:
                    validator = FalconContentValidator(
                        custom_validation_rules=custom_validation_rules,
                        risk_threshold=risk_threshold,
                    )
                case LLMModel.LLAMA:
                    validator = LlamaContentValidator(
                        custom_validation_rules=custom_validation_rules,
                        risk_threshold=risk_threshold,
                    )
                case LLMModel.QWEN:
                    validator = QwenContentValidator(
                        custom_validation_rules=custom_validation_rules,
                        risk_threshold=risk_threshold,
                    )
                case _:
                    raise

            validations = [validator.validate_text(content) for content in contents]
            return validations

        except Exception as e:
            raise e
        finally:
            gc.collect()

    @staticmethod
    def analyze_images_ai(
        image_urls: List[str],
        company_id: str = None,
        data_type: str = None,
        query: str = "Analyze this image",
        model: VISIONLLMModel = VISIONLLMModel.GEMMA,
        k=None,
        metadata_filter=None,
        search_type=None,
    ):
        try:
            if not image_urls or len(image_urls) == 0:
                raise ValueError("At least one image URL is required")

            results = []

            for image_url in image_urls:
                try:
                    match model:
                        case VISIONLLMModel.GEMMA:
                            analyzer = EnhancedGemmaVisionAnalyzer(is_use_vectordb=True)
                        case VISIONLLMModel.LLAVA:
                            analyzer = EnhancedLlavaVisionAnalyzer(is_use_vectordb=True)
                        case VISIONLLMModel.LLAMA:
                            analyzer = EnhancedLlamaVisionAnalyzer(is_use_vectordb=True)
                        case _:
                            raise

                    # Process through vision capabilities
                    result = analyzer.analyze(
                        company_id,
                        data_type,
                        k,
                        metadata_filter,
                        query,
                        search_type,
                        image_url,
                    )

                    results.append(result)

                except Exception as e:
                    results.append(
                        {
                            "image_url": image_url,
                            "error": f"Processing failed: {str(e)}",
                        }
                    )
                    raise

            return {
                "model": model.value,
                "analysis_results": results,
                "total_images": len(image_urls),
                "successful_analyses": len([r for r in results if "error" not in r]),
            }
        except Exception as e:
            raise e
        finally:
            gc.collect()


# Singleton instance for service
tools_communicator = ToolsCommunicatorService()
