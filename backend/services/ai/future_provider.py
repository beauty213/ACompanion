from typing import List, Optional
from backend.services.ai.provider import AIProvider

class FutureProvider(AIProvider):
    """Stub provider demonstrating interface extensibility for other local runtimes (e.g. llama.cpp or MLC).
    No cloud providers will ever be added.
    """

    def health(self) -> bool:
        return False

    def list_models(self) -> List[str]:
        return []

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        raise NotImplementedError("FutureProvider is a local architectural stub and not enabled in v1.")

    def embed(
        self,
        texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        raise NotImplementedError("FutureProvider is a local architectural stub and not enabled in v1.")
