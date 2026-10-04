import logging
from typing import List, Optional
import httpx
from backend.config import DEFAULT_EMBEDDING_MODEL, DEFAULT_MODEL, OLLAMA_BASE_URL
from backend.services.ai.provider import AIProvider

logger = logging.getLogger("anchor.ai.ollama")

class OllamaProvider(AIProvider):
    """Implementation of AIProvider connecting strictly to local Ollama at http://localhost:11434."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(12.0, connect=3.0)

    def health(self) -> bool:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return [m for m in models if m]
        except Exception as e:
            logger.debug(f"Ollama list_models failed: {e}")
        return []

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        target_model = model or DEFAULT_MODEL
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        if system:
            payload["system"] = system

        try:
            with httpx.Client(timeout=httpx.Timeout(60.0, connect=4.0)) as client:
                res = client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
                else:
                    raise RuntimeError(f"Ollama error {res.status_code}: {res.text}")
        except httpx.ConnectError:
            raise ConnectionError(f"Could not connect to Ollama at {self.base_url}")
        except httpx.TimeoutException:
            raise TimeoutError("Ollama generation timed out")
        except Exception as e:
            raise RuntimeError(f"Local LLM generation failed: {e}")

    def embed(
        self,
        texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        target_model = model or DEFAULT_EMBEDDING_MODEL
        if not texts:
            return []

        embeddings: List[List[float]] = []
        try:
            with httpx.Client(timeout=self.timeout) as client:
                # First try batch embed endpoint: /api/embed
                res = client.post(
                    f"{self.base_url}/api/embed",
                    json={"model": target_model, "input": texts},
                )
                if res.status_code == 200:
                    data = res.json()
                    if "embeddings" in data and len(data["embeddings"]) == len(texts):
                        return data["embeddings"]

                # Fallback to single text endpoint: /api/embeddings
                for t in texts:
                    single_res = client.post(
                        f"{self.base_url}/api/embeddings",
                        json={"model": target_model, "prompt": t},
                    )
                    if single_res.status_code == 200:
                        em = single_res.json().get("embedding", [])
                        embeddings.append(em)
                    else:
                        raise RuntimeError(f"Ollama embeddings endpoint returned {single_res.status_code}")
                return embeddings
        except Exception as e:
            logger.debug(f"Ollama embed call failed: {e}")
            raise ConnectionError(f"Ollama embedding unavailable: {e}")
