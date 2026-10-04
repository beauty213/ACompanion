import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.seed_data import seed_all
from backend.services.module_service import ModuleService
from backend.services.incident_analysis_service import IncidentAnalysisService
from backend.models.module import ModuleCreate

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_seed():
    seed_all()

def test_module_listing_and_stats():
    response = client.get("/api/modules")
    assert response.status_code == 200
    modules = response.json()
    assert len(modules) >= 3

    # Check Maya module
    maya = next((m for m in modules if "Maya" in m["name"]), None)
    assert maya is not None
    assert maya["incident_count"] == 3
    assert maya["active_boundaries_count"] >= 2

def test_module_crud():
    mod_svc = ModuleService()
    created = mod_svc.create_module(
        ModuleCreate(
            name="Roommate Chris",
            relationship="Roommate",
            description="Tracking shared rent and cleaning friction"
        )
    )
    assert created.id.startswith("mod_")
    assert created.name == "Roommate Chris"

    # Fetch
    fetched = mod_svc.get_module(created.id)
    assert fetched is not None
    assert fetched.relationship == "Roommate"

    # Delete
    deleted = mod_svc.delete_module(created.id)
    assert deleted is True
    assert mod_svc.get_module(created.id) is None

def test_incident_analysis_for_maya():
    response = client.get("/api/modules")
    modules = response.json()
    maya = next(m for m in modules if "Maya" in m["name"])

    # Call analyze endpoint
    analysis_res = client.post(f"/api/modules/{maya['id']}/analyze")
    assert analysis_res.status_code == 200
    report = analysis_res.json()

    assert report["module_id"] == maya["id"]
    assert report["incident_count"] == 3
    assert "Maya" in report["module_name"]

    # Verify report sections
    assert len(report["timeline_summary"]) > 20
    assert len(report["escalation_analysis"]) > 20
    assert len(report["documented_contradictions"]) >= 1
    assert "asymmetrical" in report["reciprocity_assessment"].lower() or "dynamic" in report["reciprocity_assessment"].lower()
    assert len(report["active_boundaries"]) >= 2
    assert len(report["clarifying_questions"]) >= 2
    assert len(report["key_takeaway"]) > 20

def test_incident_logging_under_module():
    response = client.get("/api/modules")
    modules = response.json()
    maya = next(m for m in modules if "Maya" in m["name"])

    # Log 4th incident
    post_res = client.post(
        f"/api/modules/{maya['id']}/incidents",
        json={
            "title": "Maya sent mutual friends to ask me why I'm ignoring her",
            "content": "Today two mutual friends texted me asking why I am being cold to Maya. She told them I'm holding a grudge over nothing."
        }
    )
    assert post_res.status_code == 201
    entry = post_res.json()
    assert entry["module_id"] == maya["id"]

    # Verify incident count increases
    incidents_res = client.get(f"/api/modules/{maya['id']}/incidents")
    assert len(incidents_res.json()) == 4

def test_module_alias_and_deduplication():
    mod_svc = ModuleService()
    # 1. Create with alias
    created = mod_svc.create_module(
        ModuleCreate(
            name="Neighbor Dave",
            alias="Loud Neighbor",
            relationship="Neighbor",
            description="Property disputes"
        )
    )
    assert created.alias == "Loud Neighbor"

    # 2. Duplicate creation returns existing module
    dup = mod_svc.create_module(
        ModuleCreate(
            name="Neighbor Dave",
            relationship="Neighbor"
        )
    )
    assert dup.id == created.id

    # 3. Cleanup
    mod_svc.delete_module(created.id)
