import os
from typing import Optional
from .providers.base import BaseLLMProvider
from .providers.gemini import GeminiProvider
from .providers.ollama import OllamaProvider
from .providers.openai import OpenAIProvider

class TranscriberConfig:
    def __init__(self):
        self.provider_name = os.getenv("AI_PROVIDER", "rule").lower()
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")

    def get_provider(self, override: Optional[str] = None) -> Optional[BaseLLMProvider]:
        name = (override or self.provider_name).lower()
        if name == "gemini":
            if not self.gemini_api_key:
                return None
            return GeminiProvider(self.gemini_api_key)
        elif name == "ollama":
            return OllamaProvider(self.ollama_model, self.ollama_host)
        elif name == "openai":
            if not self.openai_api_key:
                return None
            return OpenAIProvider(self.openai_api_key)
        return None

