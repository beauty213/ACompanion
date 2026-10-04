import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.seed_data import seed_all
from backend.services.reflection_engine import ReflectionEngine
from backend.services.ai.ollama_provider import OllamaProvider
from backend.services.ai.ai_service import AIService

client = TestClient(app)

def test_full_demo_path_end_to_end():
    # Setup fresh seed data with clean reset
    client.post("/api/reset")
    seed_res = client.post("/api/seed")
    assert seed_res.status_code == 200

    # Step 1: Write journal entry or query: "I'm thinking about reconnecting with this person."
    journal_post = client.post("/api/journal", json={
        "title": "Thinking about reconnecting",
        "content": "Alex sent a message and I am thinking about reconnecting with this person and giving another chance."
    })
    assert journal_post.status_code == 201
    entry_data = journal_post.json()
    assert entry_data["id"] is not None

    # Step 2: Anchor retrieves relevant memories & reflects
    reflect_res = client.post("/api/ask-past", json={
        "query": "I'm thinking about reconnecting with this person."
    })
    assert reflect_res.status_code == 200
    ref_data = reflect_res.json()
    assert "You mentioned something similar before" in ref_data["answer"]
    assert len(ref_data["sources"]) > 0
    assert len(ref_data["source_details"]) > 0

    # Step 3: Open previous memory; open "Why am I seeing this?"
    top_source = ref_data["source_details"][0]
    assert "memory_id" in top_source
    assert "date" in top_source
    assert "type" in top_source

    mem_detail = client.get(f"/api/memories/{top_source['memory_id']}")
    assert mem_detail.status_code == 200
    assert mem_detail.json()["id"] == top_source["memory_id"]

    # Step 4: Open Timeline
    timeline_res = client.get("/api/timeline")
    assert timeline_res.status_code == 200
    t_data = timeline_res.json()
    assert len(t_data["timeline"]) >= 4

    # Step 5: Future-self message appears
    fs_res = client.get("/api/future-self")
    assert fs_res.status_code == 200
    active_notes = [f for f in fs_res.json() if not f["dismissed"]]
    assert len(active_notes) >= 1
    # Verify triggered note contains the warning
    alex_note = next((f for f in active_notes if "Remember how heavy it felt" in f["message"]), None)
    assert alex_note is not None
    assert alex_note["triggered_at"] is not None

    # Step 6: Reflect on "What feels different this time?" -> Save a new memory
    new_mem = client.post("/api/memories", json={
        "type": "Reflection",
        "title": "Evaluating what changed before reconnecting",
        "content": "I realized nothing has changed fundamentally in communication habits. Choosing my peace over reacting.",
        "status": "user_confirmed",
        "importance": "high",
        "related_people": ["Alex"],
        "related_topics": ["reconnecting", "peace", "boundaries"],
        "source_journal_id": entry_data["id"]
    })
    assert new_mem.status_code == 201
    saved_mem_id = new_mem.json()["id"]

    # Step 7 & 8: Turn off networking / AI offline simulation
    # Simulate completely offline environment (unreachable Ollama host)
    offline_provider = OllamaProvider(base_url="http://127.0.0.1:59999")
    offline_ai = AIService(provider=offline_provider)
    offline_engine = ReflectionEngine(ai_service=offline_ai)

    # Repeat retrieval and Ask My Past offline
    offline_reflection = offline_engine.reflect(
        query="What did I decide about reconnecting with Alex?"
    )
    assert offline_reflection.status == "fallback_template"
    assert len(offline_reflection.sources) > 0
    # Must retrieve the newly saved confirmed memory!
    assert any(s == saved_mem_id for s in offline_reflection.sources)
    assert "You mentioned something similar before" in offline_reflection.answer
    assert "What feels different this time?" in offline_reflection.answer
