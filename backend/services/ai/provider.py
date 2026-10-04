from abc import ABC, abstractmethod
from typing import List, Optional

class AIProvider(ABC):
    """Abstract interface for local AI providers."""

    @abstractmethod
    def health(self) -> bool:
        """Check if local AI runtime daemon is running and responsive."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List locally available models."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate text completion from local model."""
        pass

    @abstractmethod
    def embed(
        self,
        texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """Generate vector embeddings for texts."""
        pass
