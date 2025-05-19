import threading
from langchain_ollama import OllamaLLM
from config.config import Config


class MultiOllamaRouter:
    def __init__(self, base_url_list):
        self.base_url_list = base_url_list
        self.index = 0
        self.lock = threading.Lock()

    def get_next_llm(self):
        with self.lock:
            url = self.base_url_list[self.index]
            self.index = (self.index + 1) % len(self.base_url_list)
        return OllamaLLM(
            base_url=url,
            model=Config.LLAMA_CHATBOT_LLM_OLLAMA,
            temperature=0.7,
        )
