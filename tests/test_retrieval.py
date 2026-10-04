import pytest
from backend.seed_data import seed_all
from backend.services.memory_service import MemoryService
from backend.services.retrieval_service import RetrievalService
from backend.services.vector_store import get_vector_store

def test_paraphrased_semantic_retrieval():
    seed_all()
    retrieval_svc = RetrievalService()

    # Query paraphrases "Spent hours repeatedly checking my phone waiting for replies..."
    query = "tired of constantly waiting for replies"
    results = retrieval_svc.search_memories(query=query, top_k=5)

    assert len(results) > 0
    # Top result should be related to waiting / communication boundaries
    top_ids = [r.memory.id for r in results]
    assert any(m_id in ("mem_01", "mem_02", "mem_03", "mem_04") for m_id in top_ids)

    # Paraphrased query about peace of mind
    query_peace = "preferring calm and quiet over stressful relationships"
    peace_results = retrieval_svc.search_memories(query=query_peace, top_k=3)
    assert len(peace_results) > 0
    peace_ids = [r.memory.id for r in peace_results]
    assert any(m_id in ("mem_08", "mem_06", "mem_04", "mem_05") for m_id in peace_ids)

def test_deleted_memory_never_returns():
    seed_all()
    mem_svc = MemoryService()
    retrieval_svc = RetrievalService(memory_service=mem_svc)
    vs = get_vector_store()

    # Ensure mem_01 is present before deletion
    assert mem_svc.get_memory("mem_01") is not None

    # Delete mem_01
    delete_success = mem_svc.delete_memory("mem_01")
    assert delete_success is True

    # 1. Verify gone from SQLite
    assert mem_svc.get_memory("mem_01") is None

    # 2. Verify gone from Vector Store directly
    raw_hits = vs.search(query_text="waiting for Alex replies phone", top_k=10)
    for hit in raw_hits:
        assert hit["memory_id"] != "mem_01"

    # 3. Verify retrieval engine NEVER returns mem_01
    results = retrieval_svc.search_memories(query="checking my phone waiting for a reply", top_k=10)
    for r in results:
        assert r.memory.id != "mem_01"
