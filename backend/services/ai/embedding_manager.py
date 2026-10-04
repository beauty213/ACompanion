import logging
from typing import List, Optional
from backend.config import DEFAULT_EMBEDDING_MODEL
from backend.services.ai.provider import AIProvider
from backend.services.vector_store import local_text_embedding

logger = logging.getLogger("anchor.ai.embedding")

class EmbeddingManager:
    def __init__(self, provider: AIProvider, default_model: str = DEFAULT_EMBEDDING_MODEL):
        self.provider = provider
        self.configured_model = default_model

    def is_available(self) -> bool:
        if not self.provider.health():
            return False
        models = self.provider.list_models()
        for m in models:
            if m == self.configured_model or m.startswith(f"{self.configured_model}:") or self.configured_model.startswith(f"{m}:"):
                return True
        return False

    def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        if not texts:
            return []
        
        target = model or self.configured_model
        # If Ollama is available, use nomic-embed-text
        if self.is_available():
            try:
                embeddings = self.provider.embed(texts, model=target)
                if embeddings and len(embeddings) == len(texts):
                    return embeddings
            except Exception as e:
                logger.debug(f"Ollama embedding failed ({e}), falling back to local text embedding.")

        # Smooth offline fallback to deterministic local text embedding
        return [local_text_embedding(t) for t in texts]

    def embed_single(self, text: str, model: Optional[str] = None) -> List[float]:
        res = self.embed([text], model=model)
        return res[0] if res else local_text_embedding(text)
