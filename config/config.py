import os
from dotenv import load_dotenv

# Load environment-specific file
# env_file = ".env.production" if os.getenv("APP_ENV") == "production" else ".env"
env_file = ".env"
load_dotenv(env_file)


class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", 9001))
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    ENABLE_SWAGGER = APP_ENV == "development"  # Disable Swagger in production
    BASE_URL = f"http://{APP_HOST}:{APP_PORT}"
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    CHROMA_ALLOW_RESET = os.getenv("CHROMA_ALLOW_RESET", "True").lower() == "true"

    # Kafka related configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
    KAFKA_SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM", "PLAIN")
    KAFKA_SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME", "")
    KAFKA_SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD", "")

    # RabbitMQ related configuration
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "127.0.0.1")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

    # LLM configuration
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

    AGENT_LLM_OLLAMA = os.getenv("AGENT_LLM_OLLAMA", "")
    AGENT_FUNCTION_CALLING_LLM_OLLAMA = os.getenv(
        "AGENT_FUNCTION_CALLING_LLM_OLLAMA", ""
    )

    CREW_FUNCTION_CALLING_LLM_OLLAMA = os.getenv(
        "CREW_FUNCTION_CALLING_LLM_OLLAMA", "ollama/gemma3"
    )
    CREW_MANAGER_LLM_OLLAMA = os.getenv("CREW_MANAGER_LLM_OLLAMA", "ollama/gemma3")
    CREW_PLANNING_LLM_OLLAMA = os.getenv("CREW_PLANNING_LLM_OLLAMA", "ollama/gemma3")
    CREW_CHAT_LLM_OLLAMA = os.getenv("CREW_CHAT_LLM_OLLAMA", "ollama/openhermes")

    DEEPSEEK_LLM_OLLAMA = os.getenv("DEEPSEEK_LLM_OLLAMA", "")
    FALCON_LLM_OLLAMA = os.getenv("FALCON_LLM_OLLAMA", "")
    GEMMA_LLM_OLLAMA = os.getenv("GEMMA_LLM_OLLAMA", "")
    GRANITE_LLM_OLLAMA = os.getenv("GRANITE_LLM_OLLAMA", "")
    LLAMA_LLM_OLLAMA = os.getenv("LLAMA_LLM_OLLAMA", "")
    LLAMA_VISION_LLM_OLLAMA = os.getenv("LLAMA_VISION_LLM_OLLAMA", "")
    LLAVA_LLM_OLLAMA = os.getenv("LLAVA_LLM_OLLAMA", "")
    MISTRAL_LLM_OLLAMA = os.getenv("MISTRAL_LLM_OLLAMA", "")
    QWEN_LLM_OLLAMA = os.getenv("QWEN_LLM_OLLAMA", "")

    AGENT_EMBEDDER_PROVIDER = os.getenv("AGENT_EMBEDDER_PROVIDER", "")
    AGENT_EMBEDDER_MODEL = os.getenv("AGENT_EMBEDDER_MODEL", "")
    CREW_EMBEDDER_PROVIDER = os.getenv("CREW_EMBEDDER_PROVIDER", "")
    CREW_EMBEDDER_MODEL = os.getenv("CREW_EMBEDDER_MODEL", "")

    MISTRAL_CHATBOT_LLM_OLLAMA = os.getenv("MISTRAL_CHATBOT_LLM_OLLAMA", "")
    LLAMA_CHATBOT_LLM_OLLAMA = os.getenv("LLAMA_CHATBOT_LLM_OLLAMA", "")
    FALCON_CHATBOT_LLM_OLLAMA = os.getenv("FALCON_CHATBOT_LLM_OLLAMA", "")


config = Config()
