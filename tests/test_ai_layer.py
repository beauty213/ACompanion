import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.ai.future_provider import FutureProvider
from backend.services.ai.ollama_provider import OllamaProvider
from backend.services.ai.model_manager import ModelManager
from backend.services.ai.embedding_manager import EmbeddingManager
from backend.services.ai.ai_service import AIService

client = TestClient(app)

def test_future_provider_stub():
    provider = FutureProvider()
    assert provider.health() is False
    assert provider.list_models() == []
    with pytest.raises(NotImplementedError):
        provider.generate("Test")
    with pytest.raises(NotImplementedError):
        provider.embed(["Test"])

def test_ollama_graceful_offline_handling():
    # Points to an unreachable port to simulate Ollama being stopped / killed
    provider = OllamaProvider(base_url="http://127.0.0.1:59999")
    assert provider.health() is False
    assert provider.list_models() == []

    mm = ModelManager(provider)
    status = mm.get_status()
    assert status["runtime_available"] is False
    assert status["model_available"] is False
    assert status["inference_test"] is False
    assert status["error_message"] is not None

def test_embedding_offline_fallback():
    # EmbeddingManager must NEVER crash even if Ollama is down
    provider = OllamaProvider(base_url="http://127.0.0.1:59999")
    em = EmbeddingManager(provider)
    assert em.is_available() is False

    # Graceful fallback produces valid normalized embedding
    vecs = em.embed(["Thinking about reconnecting with someone."])
    assert len(vecs) == 1
    assert len(vecs[0]) == 384
    # Check norm is ~1.0
    import math
    norm = math.sqrt(sum(x * x for x in vecs[0]))
    assert abs(norm - 1.0) < 1e-4

def test_ai_status_endpoint_offline():
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "runtime" in data
    assert "runtime_available" in data
    assert "model" in data
    assert "model_available" in data
    assert "embeddings_available" in data
    assert "inference_test" in data
    assert "ready" in data
    assert "offline_capable" in data
    assert data["offline_capable"] is True

def test_app_usable_when_ai_offline():
    # Acceptance check: kill Ollama -> app stays usable with clear messages
    # Testing that journal, memory, and timeline work seamlessly
    j_res = client.get("/api/journal")
    assert j_res.status_code == 200

    m_res = client.get("/api/memories")
    assert m_res.status_code == 200

    t_res = client.get("/api/timeline")
    assert t_res.status_code == 200
