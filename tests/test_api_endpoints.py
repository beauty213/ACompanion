import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.seed_data import seed_all

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_seed_and_timeline():
    # 1. Seed
    seed_res = client.post("/api/seed")
    assert seed_res.status_code == 200
    assert seed_res.json()["status"] == "success"

    # 2. Journal listing
    j_res = client.get("/api/journal")
    assert j_res.status_code == 200
    entries = j_res.json()
    assert len(entries) >= 8

    # 3. Memories listing
    m_res = client.get("/api/memories")
    assert m_res.status_code == 200
    mems = m_res.json()
    assert len(mems) >= 9

    # 4. Timeline
    t_res = client.get("/api/timeline")
    assert t_res.status_code == 200
    t_data = t_res.json()
    assert "timeline" in t_data
    assert len(t_data["timeline"]) >= 4  # Spans June to October

    # 4b. Filtered timeline for Maya
    t_filtered = client.get("/api/timeline?module_id=mod_maya")
    assert t_filtered.status_code == 200
    f_data = t_filtered.json()
    assert f_data["total_events"] >= 3
    # Check that events contain module info
    all_events = [ev for grp in f_data["timeline"] for ev in grp["events"]]
    assert any(ev.get("module_name") and "Maya" in ev["module_name"] for ev in all_events)

    # 5. Future Self
    fs_res = client.get("/api/future-self")
    assert fs_res.status_code == 200
    assert len(fs_res.json()) >= 1

    # 6. Patterns (Both Alex and Maya)
    p_res = client.get("/api/patterns")
    assert p_res.status_code == 200
    pats = p_res.json()
    assert len(pats) >= 2
    assert any("7-year" in p["title"].lower() or "friendship" in p["title"].lower() for p in pats)
