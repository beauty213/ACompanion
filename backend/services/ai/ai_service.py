from typing import Any, Dict, List, Optional
from backend.models.ai import AIStatusResponse
from backend.services.ai.embedding_manager import EmbeddingManager
from backend.services.ai.model_manager import ModelManager
from backend.services.ai.ollama_provider import OllamaProvider
from backend.services.ai.provider import AIProvider

class AIService:
    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or OllamaProvider()
        self.model_manager = ModelManager(self.provider)
        self.embedding_manager = EmbeddingManager(self.provider)

    def get_status(self) -> AIStatusResponse:
        model_status = self.model_manager.get_status()
        embed_ok = self.embedding_manager.is_available()

        is_ready = bool(
            model_status["runtime_available"]
            and model_status["model_available"]
            and embed_ok
            and model_status["inference_test"]
        )

        return AIStatusResponse(
            runtime=model_status["runtime"],
            runtime_available=model_status["runtime_available"],
            model=model_status["model"],
            model_available=model_status["model_available"],
            embeddings_available=embed_ok,
            inference_test=model_status["inference_test"],
            ready=is_ready,
            offline_capable=True,
            error_message=model_status.get("error_message"),
            available_models=model_status.get("available_models", []),
        )

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        return self.provider.generate(
            prompt=prompt,
            model=self.model_manager.configured_model,
            system=system,
            temperature=temperature,
        )

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.embedding_manager.embed(texts)

# Singleton accessor
_ai_service_instance: Optional[AIService] = None

def get_ai_service() -> AIService:
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
