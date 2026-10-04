from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AIStatusResponse(BaseModel):
    runtime: str = "Ollama"
    runtime_available: bool = False
    model: str = "gemma3:4b"
    model_available: bool = False
    embeddings_available: bool = False
    inference_test: bool = False
    ready: bool = False
    offline_capable: bool = True
    error_message: Optional[str] = None
    available_models: List[str] = Field(default_factory=list)

class AskPastRequest(BaseModel):
    query: str
    top_k: int = 5
    filter_person: Optional[str] = None
    filter_topic: Optional[str] = None

class ReflectionResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default_factory=list)
    source_details: List[Dict[str, Any]] = Field(default_factory=list)
    reflective_question: Optional[str] = None
    status: str = "ok"  # "ok", "insufficient_context", "safety_warning", "fallback_template", "ai_unavailable"
    why_seeing_this: Optional[str] = None
