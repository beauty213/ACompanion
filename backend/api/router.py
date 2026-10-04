import json
import sqlite3
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.models.future_self import FutureSelfCreate, FutureSelfResponse
from backend.models.journal import (
    JournalEntryCreate,
    JournalEntryResponse,
    JournalEntryUpdate,
)
from backend.models.memory import (
    ImportanceLevel,
    MemoryCreate,
    MemoryResponse,
    MemorySearchRequest,
    MemoryStatus,
    MemoryType,
    MemoryUpdate,
)
from backend.models.pattern import PatternResponse
from backend.models.ai import AIStatusResponse, AskPastRequest, ReflectionResponse
from backend.models.module import Module, ModuleCreate, ModuleUpdate, ModuleWithStats
from backend.models.incident_analysis import IncidentAnalysisReport
from backend.seed_data import reset_all, seed_all
from backend.services.journal_service import JournalService
from backend.services.memory_service import MemoryService
from backend.services.module_service import ModuleService
from backend.services.incident_analysis_service import IncidentAnalysisService
from backend.services.ai.ai_service import get_ai_service
from backend.services.reflection_engine import ReflectionEngine


api_router = APIRouter(prefix="/api")

# Services
mem_service = MemoryService()
journal_service = JournalService(memory_service=mem_service)
module_service = ModuleService()
incident_analysis_service = IncidentAnalysisService(
    module_service=module_service,
    journal_service=journal_service,
    memory_service=mem_service
)

@api_router.get("/health")
def health_check():
    return {"status": "ok", "app": "Anchor", "version": "1.0.0"}

# --- Local AI Endpoints ---

@api_router.get("/ai/status", response_model=AIStatusResponse)
def get_ai_status():
    ai_service = get_ai_service()
    return ai_service.get_status()

@api_router.post("/ai/check", response_model=AIStatusResponse)
def check_ai_status():
    ai_service = get_ai_service()
    return ai_service.get_status()

@api_router.get("/ai/models")
def get_ai_models():
    ai_service = get_ai_service()
    return {"models": ai_service.model_manager.get_available_models()}

@api_router.post("/ask-past", response_model=ReflectionResponse)
def ask_past(req: AskPastRequest):
    reflection_engine = ReflectionEngine(ai_service=get_ai_service())
    return reflection_engine.reflect(
        query=req.query,
        top_k=req.top_k,
        filter_person=req.filter_person,
    )



# --- Journal Endpoints ---

@api_router.get("/journal", response_model=List[JournalEntryResponse])
def list_journal(
    module_id: Optional[str] = None,
    conn: sqlite3.Connection = Depends(get_db)
):
    return journal_service.list_entries(module_id=module_id, conn=conn)

@api_router.post("/journal", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_journal(entry: JournalEntryCreate, conn: sqlite3.Connection = Depends(get_db)):
    return journal_service.create_entry(entry, conn=conn)

@api_router.get("/journal/{entry_id}", response_model=JournalEntryResponse)
def get_journal(entry_id: str, conn: sqlite3.Connection = Depends(get_db)):
    entry = journal_service.get_entry(entry_id, conn=conn)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry

@api_router.put("/journal/{entry_id}", response_model=JournalEntryResponse)
def update_journal(entry_id: str, update: JournalEntryUpdate, conn: sqlite3.Connection = Depends(get_db)):
    entry = journal_service.update_entry(entry_id, update, conn=conn)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry

@api_router.delete("/journal/{entry_id}")
def delete_journal(entry_id: str, conn: sqlite3.Connection = Depends(get_db)):
    deleted = journal_service.delete_entry(entry_id, conn=conn)
    if not deleted:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"success": True, "id": entry_id}

# --- Memory Endpoints ---

@api_router.post("/memories/search")
def search_memories(search_req: MemorySearchRequest):
    from backend.services.retrieval_service import RetrievalService
    retrieval_svc = RetrievalService(memory_service=mem_service)
    results = retrieval_svc.search_memories(
        query=search_req.query,
        top_k=search_req.top_k,
        min_similarity=search_req.min_similarity,
        include_suggested=search_req.include_suggested,
        filter_type=search_req.filter_type.value if search_req.filter_type else None,
    )
    return [r.to_dict() for r in results]

@api_router.get("/memories", response_model=List[MemoryResponse])
def list_memories(
    type: Optional[MemoryType] = None,
    status: Optional[MemoryStatus] = None,
    importance: Optional[ImportanceLevel] = None,
    module_id: Optional[str] = None,
    search: Optional[str] = None,
    include_suggested: bool = True,
    conn: sqlite3.Connection = Depends(get_db),
):
    return mem_service.list_memories(
        memory_type=type,
        status=status,
        importance=importance,
        module_id=module_id,
        search_query=search,
        include_suggested=include_suggested,
        conn=conn,
    )

@api_router.post("/memories", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(memory: MemoryCreate, conn: sqlite3.Connection = Depends(get_db)):
    return mem_service.create_memory(memory, conn=conn)

@api_router.get("/memories/{memory_id}", response_model=MemoryResponse)
def get_memory(memory_id: str, conn: sqlite3.Connection = Depends(get_db)):
    mem = mem_service.get_memory(memory_id, conn=conn)
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    return mem

@api_router.patch("/memories/{memory_id}", response_model=MemoryResponse)
def update_memory(memory_id: str, update: MemoryUpdate, conn: sqlite3.Connection = Depends(get_db)):
    mem = mem_service.update_memory(memory_id, update, conn=conn)
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    return mem

@api_router.delete("/memories/{memory_id}")
def delete_memory(memory_id: str, conn: sqlite3.Connection = Depends(get_db)):
    deleted = mem_service.delete_memory(memory_id, conn=conn)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True, "id": memory_id}

# --- Timeline Endpoint ---

@api_router.get("/timeline")
def get_timeline(module_id: Optional[str] = None, conn: sqlite3.Connection = Depends(get_db)):
    """Aggregates journal entries and confirmed memories chronologically by month, optionally filtered by module."""
    # Build modules lookup dictionary
    mods_dict = {}
    for r in conn.execute("SELECT id, name, alias FROM modules").fetchall():
        mods_dict[r["id"]] = {
            "name": r["name"],
            "alias": r["alias"] if "alias" in r.keys() else None,
        }

    if module_id:
        journal_rows = conn.execute(
            "SELECT id, title, content, module_id, created_at FROM journal_entries WHERE module_id = ? ORDER BY created_at ASC",
            (module_id,)
        ).fetchall()
        all_memories = mem_service.list_memories(include_suggested=False, conn=conn)
        memories = [m for m in all_memories if m.module_id == module_id]
    else:
        journal_rows = conn.execute(
            "SELECT id, title, content, module_id, created_at FROM journal_entries ORDER BY created_at ASC"
        ).fetchall()
        memories = mem_service.list_memories(include_suggested=False, conn=conn)

    events = []
    for j in journal_rows:
        mid = j["module_id"] if "module_id" in j.keys() else None
        minfo = mods_dict.get(mid) if mid else None
        events.append({
            "id": j["id"],
            "item_type": "journal",
            "title": j["title"] or "Journal Note",
            "snippet": j["content"][:200],
            "module_id": mid,
            "module_name": minfo["name"] if minfo else None,
            "module_alias": minfo["alias"] if minfo else None,
            "created_at": j["created_at"],
            "date": j["created_at"][:10],
            "month": j["created_at"][:7],  # YYYY-MM
        })

    for m in memories:
        minfo = mods_dict.get(m.module_id) if m.module_id else None
        events.append({
            "id": m.id,
            "item_type": "memory",
            "memory_type": m.type.value,
            "title": m.title or f"{m.type.value} memory",
            "snippet": m.content[:200],
            "importance": m.importance.value,
            "module_id": m.module_id,
            "module_name": minfo["name"] if minfo else None,
            "module_alias": minfo["alias"] if minfo else None,
            "created_at": m.created_at,
            "date": m.created_at[:10],
            "month": m.created_at[:7],
        })

    events.sort(key=lambda x: x["created_at"])
    
    # Group by month
    months_dict: Dict[str, List[Any]] = {}
    for ev in events:
        m = ev["month"]
        if m not in months_dict:
            months_dict[m] = []
        months_dict[m].append(ev)

    timeline_grouped = [
        {"month": m, "events": evs}
        for m, evs in sorted(months_dict.items(), key=lambda x: x[0])
    ]

    return {
        "timeline": timeline_grouped,
        "total_events": len(events)
    }

# --- Future Self Endpoints ---

@api_router.get("/future-self", response_model=List[FutureSelfResponse])
def list_future_self(conn: sqlite3.Connection = Depends(get_db)):
    rows = conn.execute("SELECT * FROM future_self_messages ORDER BY created_at DESC").fetchall()
    return [
        FutureSelfResponse(
            id=r["id"],
            message=r["message"],
            related_person=r["related_person"],
            related_topic=r["related_topic"],
            importance=ImportanceLevel(r["importance"] or "med"),
            trigger_context=r["trigger_context"],
            expires_at=r["expires_at"],
            created_at=r["created_at"],
            triggered_at=r["triggered_at"],
            dismissed=bool(r["dismissed"]),
        )
        for r in rows
    ]

@api_router.post("/future-self", response_model=FutureSelfResponse, status_code=status.HTTP_201_CREATED)
def create_future_self(note: FutureSelfCreate, conn: sqlite3.Connection = Depends(get_db)):
    import uuid
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    note_id = note.id or f"fs_{uuid.uuid4().hex[:10]}"
    conn.execute(
        """
        INSERT INTO future_self_messages (
            id, message, related_person, related_topic, importance,
            trigger_context, expires_at, created_at, dismissed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            note_id,
            note.message,
            note.related_person,
            note.related_topic,
            note.importance.value,
            note.trigger_context,
            note.expires_at,
            now,
        )
    )
    conn.commit()
    row = conn.execute("SELECT * FROM future_self_messages WHERE id = ?", (note_id,)).fetchone()
    return FutureSelfResponse(
        id=row["id"],
        message=row["message"],
        related_person=row["related_person"],
        related_topic=row["related_topic"],
        importance=ImportanceLevel(row["importance"] or "med"),
        trigger_context=row["trigger_context"],
        expires_at=row["expires_at"],
        created_at=row["created_at"],
        triggered_at=row["triggered_at"],
        dismissed=bool(row["dismissed"]),
    )

@api_router.patch("/future-self/{note_id}/dismiss")
def dismiss_future_self(note_id: str, conn: sqlite3.Connection = Depends(get_db)):
    conn.execute("UPDATE future_self_messages SET dismissed = 1 WHERE id = ?", (note_id,))
    conn.commit()
    return {"success": True, "id": note_id}

# --- Patterns Endpoints ---

@api_router.get("/patterns", response_model=List[PatternResponse])
def list_patterns(conn: sqlite3.Connection = Depends(get_db)):
    rows = conn.execute("SELECT * FROM patterns WHERE dismissed = 0 ORDER BY created_at DESC").fetchall()
    result = []
    for r in rows:
        mids = []
        try:
            mids = json.loads(r["memory_ids"])
        except Exception:
            mids = []
        result.append(PatternResponse(
            id=r["id"],
            title=r["title"],
            description=r["description"],
            memory_ids=mids,
            dismissed=bool(r["dismissed"]),
            created_at=r["created_at"],
        ))
    return result

@api_router.post("/patterns/detect")
def detect_patterns(conn: sqlite3.Connection = Depends(get_db)):
    from backend.services.pattern_service import PatternService
    pattern_svc = PatternService(memory_service=mem_service)
    res = pattern_svc.detect_patterns(conn=conn)
    return res.model_dump()

@api_router.patch("/patterns/{pattern_id}/dismiss")
def dismiss_pattern(pattern_id: str, conn: sqlite3.Connection = Depends(get_db)):
    conn.execute("UPDATE patterns SET dismissed = 1 WHERE id = ?", (pattern_id,))
    conn.commit()
    return {"success": True, "id": pattern_id}


# --- Modular People & Incident Analysis Endpoints ---

@api_router.get("/modules", response_model=List[ModuleWithStats])
def list_modules(conn: sqlite3.Connection = Depends(get_db)):
    return module_service.list_modules(conn=conn)

@api_router.post("/modules", response_model=Module, status_code=status.HTTP_201_CREATED)
def create_module(module_in: ModuleCreate, conn: sqlite3.Connection = Depends(get_db)):
    return module_service.create_module(module_in, conn=conn)

@api_router.get("/modules/{module_id}", response_model=Module)
def get_module(module_id: str, conn: sqlite3.Connection = Depends(get_db)):
    mod = module_service.get_module(module_id, conn=conn)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")
    return mod

@api_router.put("/modules/{module_id}", response_model=Module)
def update_module(module_id: str, update: ModuleUpdate, conn: sqlite3.Connection = Depends(get_db)):
    mod = module_service.update_module(module_id, update, conn=conn)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")
    return mod

@api_router.delete("/modules/{module_id}")
def delete_module(module_id: str, conn: sqlite3.Connection = Depends(get_db)):
    deleted = module_service.delete_module(module_id, conn=conn)
    if not deleted:
        raise HTTPException(status_code=404, detail="Module not found")
    return {"success": True, "id": module_id}

@api_router.get("/modules/{module_id}/incidents", response_model=List[JournalEntryResponse])
def get_module_incidents(module_id: str, conn: sqlite3.Connection = Depends(get_db)):
    mod = module_service.get_module(module_id, conn=conn)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")
    return journal_service.list_entries(module_id=module_id, conn=conn)

@api_router.post("/modules/{module_id}/incidents", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_module_incident(module_id: str, entry: JournalEntryCreate, conn: sqlite3.Connection = Depends(get_db)):
    mod = module_service.get_module(module_id, conn=conn)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")
    entry.module_id = module_id
    return journal_service.create_entry(entry, conn=conn)

@api_router.post("/modules/{module_id}/analyze", response_model=IncidentAnalysisReport)
def analyze_module_incidents(module_id: str):
    report = incident_analysis_service.analyze_module(module_id)
    if not report:
        raise HTTPException(status_code=404, detail="Module not found")
    return report


# --- Seed, Reset, Export ---

@api_router.post("/seed")
def seed_data():
    return seed_all()

@api_router.post("/reset")
def reset_data():
    return reset_all()

@api_router.get("/export")
@api_router.post("/export")
def export_data(conn: sqlite3.Connection = Depends(get_db)):
    return mem_service.export_data(conn=conn)

@api_router.get("/memes")
def list_online_memes():
    from backend.services.online_meme_service import online_meme_service
    return {"memes": online_meme_service.catalog}

@api_router.get("/memes/search")
def search_online_memes(q: str = ""):
    from backend.services.online_meme_service import online_meme_service
    results = online_meme_service.search_online_memes(q)
    return {"query": q, "results": results}

class CritiqueRequest(BaseModel):
    text: str
    title: Optional[str] = None
    current_meme: Optional[str] = None
    shuffle: bool = False
    entry_id: Optional[str] = None

@api_router.post("/critique")
def get_meme_critique(req: CritiqueRequest, conn: sqlite3.Connection = Depends(get_db)):
    from backend.services.critique_service import critique_service
    if req.shuffle:
        res = critique_service.shuffle(req.text, req.current_meme)
    else:
        res = critique_service.evaluate(req.text, req.title)
    if req.entry_id:
        try:
            journal_service.update_entry_critique(req.entry_id, res, conn=conn)
        except Exception:
            pass
    return res


