from typing import Dict, List, Optional
from backend.config import DEFAULT_MODEL
from backend.services.ai.provider import AIProvider

class ModelManager:
    def __init__(self, provider: AIProvider, default_model: str = DEFAULT_MODEL):
        self.provider = provider
        self.configured_model = default_model

    def check_runtime(self) -> bool:
        return self.provider.health()

    def get_available_models(self) -> List[str]:
        return self.provider.list_models()

    def is_model_available(self, model_name: Optional[str] = None) -> bool:
        target = model_name or self.configured_model
        models = self.get_available_models()
        # Check either exact match or model:tag match
        for m in models:
            if m == target or m.startswith(f"{target}:") or target.startswith(f"{m}:"):
                return True
        return False

    def test_inference(self) -> bool:
        """Runs a minimal inference test to verify generation capability."""
        if not self.check_runtime() or not self.is_model_available():
            return False
        try:
            res = self.provider.generate(
                prompt="Say READY",
                model=self.configured_model,
                temperature=0.0,
            )
            return len(res.strip()) > 0
        except Exception:
            return False

    def get_status(self) -> Dict[str, any]:
        runtime_ok = self.check_runtime()
        models = self.get_available_models() if runtime_ok else []
        model_ok = self.is_model_available() if runtime_ok else False
        inference_ok = self.test_inference() if (runtime_ok and model_ok) else False

        error_message = None
        if not runtime_ok:
            error_message = "Ollama runtime is not reachable at http://localhost:11434"
        elif not model_ok:
            error_message = f"Model '{self.configured_model}' is not pulled in Ollama"

        return {
            "runtime": "Ollama",
            "runtime_available": runtime_ok,
            "model": self.configured_model,
            "model_available": model_ok,
            "inference_test": inference_ok,
            "available_models": models,
            "error_message": error_message,
        }
