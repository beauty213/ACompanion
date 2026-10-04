import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.models.memory import ImportanceLevel, MemoryResponse, MemoryStatus
from backend.services.ai.ai_service import get_ai_service
from backend.services.memory_service import MemoryService
from backend.services.vector_store import get_vector_store

DEFAULT_MIN_SIMILARITY = 0.36

def calculate_recency_score(created_at_iso: str) -> float:
    """Calculates recency score in [0.2, 1.0] based on elapsed days."""
    try:
        created = datetime.fromisoformat(created_at_iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        days = max(0, (now - created).days)
        # Half-life of ~90 days
        return max(0.2, math.exp(-0.007 * days))
    except Exception:
        return 0.5

def calculate_importance_score(importance: ImportanceLevel) -> float:
    if importance == ImportanceLevel.HIGH:
        return 1.0
    elif importance == ImportanceLevel.MED:
        return 0.6
    return 0.3

def calculate_person_topic_match(query: str, related_people: List[str], related_topics: List[str]) -> float:
    q_lower = query.lower()
    for p in related_people:
        if p.lower() in q_lower:
            return 1.0
    for t in related_topics:
        if t.lower() in q_lower:
            return 1.0
    return 0.0

class RetrievalResult:
    def __init__(self, memory: MemoryResponse, score: float, semantic_sim: float):
        self.memory = memory
        self.score = score
        self.semantic_sim = semantic_sim

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory": self.memory.model_dump(),
            "score": round(self.score, 4),
            "semantic_sim": round(self.semantic_sim, 4),
        }

class RetrievalService:
    def __init__(self, memory_service: Optional[MemoryService] = None, ai_service: Optional[AIService] = None):
        self.memory_service = memory_service or MemoryService()
        self.vector_store = get_vector_store()
        self.ai_service = ai_service or get_ai_service()


    def search_memories(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = DEFAULT_MIN_SIMILARITY,
        include_suggested: bool = False,
        filter_type: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """Performs multi-factor ranked retrieval across confirmed memories."""
        if not query.strip():
            return []

        # 1. Compute query embedding vector via local embedding engine
        query_vector = self.ai_service.embed([query])[0]

        # 2. Search vector store
        where_filter = None
        if filter_type:
            where_filter = {"type": filter_type}

        # Vector search top 20 candidates for ranking
        raw_hits = self.vector_store.search(
            query_text=query,
            query_vector=query_vector,
            top_k=max(20, top_k * 2),
            where=where_filter,
        )

        if not raw_hits:
            return []

        # 3. Fetch SQLite memory details and calculate multi-factor rank
        ranked_results: List[RetrievalResult] = []

        for hit in raw_hits:
            mid = hit["memory_id"]
            mem = self.memory_service.get_memory(mid)
            if not mem:
                continue

            # Only confirmed/edited memories count as strong commitments and appear in Ask My Past by default
            if not include_suggested and mem.status == MemoryStatus.AI_SUGGESTED:
                continue

            sem_sim = hit["score"]
            match_score = calculate_person_topic_match(query, mem.related_people, mem.related_topics)

            # Filter out entries with no semantic match and no person/topic match
            if sem_sim < min_similarity and match_score == 0.0:
                continue

            imp_score = calculate_importance_score(mem.importance)
            rec_score = calculate_recency_score(mem.created_at)
            conf_score = 1.0 if mem.status in (MemoryStatus.USER_CONFIRMED, MemoryStatus.USER_EDITED) else 0.2

            # Rank = semantic similarity + importance + recency + person/topic match + confirmation status
            total_score = (
                0.55 * sem_sim +
                0.15 * imp_score +
                0.10 * rec_score +
                0.15 * match_score +
                0.05 * conf_score
            )

            ranked_results.append(RetrievalResult(mem, total_score, sem_sim))

        # Sort by final total_score descending
        ranked_results.sort(key=lambda r: r.score, reverse=True)
        return ranked_results[:top_k]
