import pytest
from backend.database.schema import init_db
from backend.models.journal import JournalEntryCreate
from backend.models.memory import (
    ImportanceLevel,
    MemoryCreate,
    MemoryStatus,
    MemoryType,
    MemoryUpdate,
)
from backend.seed_data import reset_all, seed_all
from backend.services.journal_service import JournalService
from backend.services.memory_service import MemoryService

def test_database_init():
    init_db()

def test_seed_and_reset():
    # Test seeding
    seed_result = seed_all()
    assert seed_result["status"] == "success"
    assert seed_result["journal_entries_seeded"] >= 8
    assert seed_result["memories_seeded"] >= 8
    assert seed_result["future_self_messages"] == 1
    assert seed_result["patterns"] >= 1

    mem_svc = MemoryService()
    memories = mem_svc.list_memories(include_suggested=True)
    assert len(memories) >= 8

    # Verify at least 2 boundaries are seeded
    boundaries = [m for m in memories if m.type == MemoryType.BOUNDARY]
    assert len(boundaries) >= 2

    # Verify reset
    reset_result = reset_all()
    assert reset_result["status"] == "success"
    assert len(mem_svc.list_memories()) == 0

def test_memory_crud_and_status_flow():
    mem_svc = MemoryService()
    
    # 1. Create AI suggested memory
    mem_in = MemoryCreate(
        type=MemoryType.EXPERIENCE,
        title="Test Event",
        content="Feeling anxious after silence",
        status=MemoryStatus.AI_SUGGESTED,
        importance=ImportanceLevel.HIGH
    )
    created = mem_svc.create_memory(mem_in)
    assert created.id is not None
    assert created.status == MemoryStatus.AI_SUGGESTED
    assert created.confirmed_at is None

    # Suggested memory not included by default in Ask Past retrieval
    confirmed_only = mem_svc.list_memories(include_suggested=False)
    assert not any(m.id == created.id for m in confirmed_only)

    # 2. Confirm memory
    confirmed = mem_svc.update_memory(created.id, MemoryUpdate(status=MemoryStatus.USER_CONFIRMED))
    assert confirmed.status == MemoryStatus.USER_CONFIRMED
    assert confirmed.confirmed_at is not None

    confirmed_now = mem_svc.list_memories(include_suggested=False)
    assert any(m.id == created.id for m in confirmed_now)

    # 3. Edit memory
    edited = mem_svc.update_memory(
        created.id,
        MemoryUpdate(
            title="Updated Title",
            content="Revised content with clearer reflection",
            status=MemoryStatus.USER_EDITED
        )
    )
    assert edited.title == "Updated Title"
    assert edited.status == MemoryStatus.USER_EDITED

    # 4. Delete memory
    deleted = mem_svc.delete_memory(created.id)
    assert deleted is True
    assert mem_svc.get_memory(created.id) is None

def test_journal_crud():
    mem_svc = MemoryService()
    jrn_svc = JournalService(memory_service=mem_svc)

    entry = jrn_svc.create_entry(
        JournalEntryCreate(title="Test Journal", content="Reflecting on my priorities today.")
    )
    assert entry.id is not None
    assert entry.title == "Test Journal"

    retrieved = jrn_svc.get_entry(entry.id)
    assert retrieved is not None
    assert retrieved.content == "Reflecting on my priorities today."

    deleted = jrn_svc.delete_entry(entry.id)
    assert deleted is True
    assert jrn_svc.get_entry(entry.id) is None
