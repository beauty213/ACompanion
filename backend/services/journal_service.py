import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from backend.database.connection import get_db_connection
from backend.services.critique_service import critique_service
from backend.models.journal import (
    JournalEntryCreate,
    JournalEntryResponse,
    JournalEntryUpdate,
    MemeCritique,
)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class JournalService:
    def __init__(self, memory_service=None):
        self._memory_service = memory_service

    def create_entry(self, data: JournalEntryCreate, conn: Optional[sqlite3.Connection] = None) -> JournalEntryResponse:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            entry_id = data.id or f"jrn_{uuid.uuid4().hex[:12]}"
            created_at = data.created_at or utc_now()
            updated_at = created_at

            assigned_module_id = data.module_id
            if not assigned_module_id:
                # Smart matching: check if any module name or alias is mentioned in content/title
                mods = conn.execute("SELECT id, name, alias FROM modules").fetchall()
                full_text = f"{data.title or ''} {data.content}".lower()
                for m in mods:
                    m_name = (m["name"] or "").strip().lower()
                    m_alias = (m["alias"] or "").strip().lower() if "alias" in m.keys() and m["alias"] else ""
                    # primary word (e.g. "Maya" from "Maya (Friend of 7 Years)")
                    first_word = m_name.split()[0] if m_name else ""
                    if (m_name and m_name in full_text) or \
                       (len(first_word) >= 3 and first_word in full_text) or \
                       (m_alias and m_alias in full_text):
                        assigned_module_id = m["id"]
                        break

            crit_dict = critique_service.evaluate(data.content, data.title)
            import json
            crit_json = json.dumps(crit_dict) if crit_dict else None

            conn.execute(
                """
                INSERT INTO journal_entries (id, title, content, module_id, critique_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (entry_id, data.title, data.content, assigned_module_id, crit_json, created_at, updated_at)
            )
            conn.commit()

            # Trigger check for Future Self notes
            try:
                from backend.services.future_self_service import FutureSelfService
                fs_svc = FutureSelfService()
                fs_svc.check_triggers(data.content, conn=conn)
            except Exception as e:
                pass

            # Detect potential memory suggestions for user review
            if not data.id and self._memory_service:
                content_lower = data.content.lower()
                should_suggest = any(w in content_lower for w in [
                    "decided to", "will not accept", "boundary", "realized that",
                    "committed to", "my limit", "stepped back", "apology", "apologized",
                    "reconnecting", "give another chance"
                ])
                if should_suggest:
                    from backend.models.memory import ImportanceLevel, MemoryCreate, MemoryStatus, MemoryType
                    m_type = MemoryType.BOUNDARY if "boundary" in content_lower or "will not" in content_lower else MemoryType.REFLECTION
                    suggestion = MemoryCreate(
                        type=m_type,
                        title=f"Possible {m_type.value}: {data.title or 'Journal reflection'}",
                        content=data.content[:280],
                        summary="Detected potential commitment or boundary from journal.",
                        status=MemoryStatus.AI_SUGGESTED,
                        importance=ImportanceLevel.HIGH if "boundary" in content_lower else ImportanceLevel.MED,
                        source_journal_id=entry_id,
                        module_id=assigned_module_id,
                    )
                    self._memory_service.create_memory(suggestion, conn=conn)

            return self.get_entry(entry_id, conn=conn)
        finally:
            if close_after:
                conn.close()


    def get_entry(self, entry_id: str, conn: Optional[sqlite3.Connection] = None) -> Optional[JournalEntryResponse]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            row = conn.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,)).fetchone()
            if not row:
                return None

            # Find any memories suggested or linked from this journal
            suggested_memories = []
            if self._memory_service:
                all_memories = self._memory_service.list_memories(conn=conn, include_suggested=True)
                suggested_memories = [m for m in all_memories if m.source_journal_id == entry_id]

            import json
            critique = None
            if "critique_json" in row.keys() and row["critique_json"]:
                try:
                    c_dict = json.loads(row["critique_json"])
                    critique = MemeCritique(**c_dict)
                except Exception:
                    pass

            if not critique:
                crit_dict = critique_service.evaluate(row["content"], row["title"])
                critique = MemeCritique(**crit_dict) if crit_dict else None
                try:
                    conn.execute("UPDATE journal_entries SET critique_json = ? WHERE id = ?", (json.dumps(crit_dict), entry_id))
                    conn.commit()
                except Exception:
                    pass

            return JournalEntryResponse(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                module_id=row["module_id"] if "module_id" in row.keys() else None,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                suggested_memories=suggested_memories,
                related_memories=[],
                critique=critique,
            )
        finally:
            if close_after:
                conn.close()

    def list_entries(self, module_id: Optional[str] = None, conn: Optional[sqlite3.Connection] = None) -> List[JournalEntryResponse]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            if module_id:
                rows = conn.execute(
                    "SELECT * FROM journal_entries WHERE module_id = ? ORDER BY created_at DESC",
                    (module_id,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM journal_entries ORDER BY created_at DESC").fetchall()

            import json
            entries = []
            for r in rows:
                critique = None
                if "critique_json" in r.keys() and r["critique_json"]:
                    try:
                        c_dict = json.loads(r["critique_json"])
                        critique = MemeCritique(**c_dict)
                    except Exception:
                        pass

                if not critique:
                    c_dict = critique_service.evaluate(r["content"], r["title"])
                    critique = MemeCritique(**c_dict) if c_dict else None
                    try:
                        conn.execute("UPDATE journal_entries SET critique_json = ? WHERE id = ?", (json.dumps(c_dict), r["id"]))
                        conn.commit()
                    except Exception:
                        pass

                entries.append(
                    JournalEntryResponse(
                        id=r["id"],
                        title=r["title"],
                        content=r["content"],
                        module_id=r["module_id"] if "module_id" in r.keys() else None,
                        created_at=r["created_at"],
                        updated_at=r["updated_at"],
                        suggested_memories=[],
                        related_memories=[],
                        critique=critique,
                    )
                )
            return entries
        finally:
            if close_after:
                conn.close()

    def update_entry_critique(self, entry_id: str, critique_data: dict, conn: Optional[sqlite3.Connection] = None) -> bool:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True
        try:
            import json
            conn.execute("UPDATE journal_entries SET critique_json = ? WHERE id = ?", (json.dumps(critique_data), entry_id))
            conn.commit()
            return True
        finally:
            if close_after:
                conn.close()

    def update_entry(self, entry_id: str, data: JournalEntryUpdate, conn: Optional[sqlite3.Connection] = None) -> Optional[JournalEntryResponse]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            now = utc_now()
            updates = []
            params = []

            if data.title is not None:
                updates.append("title = ?")
                params.append(data.title)
            if data.content is not None:
                updates.append("content = ?")
                params.append(data.content)
            if data.module_id is not None:
                updates.append("module_id = ?")
                params.append(None if data.module_id.strip() == "" else data.module_id.strip())

            if not updates:
                return self.get_entry(entry_id, conn=conn)

            updates.append("updated_at = ?")
            params.append(now)
            params.append(entry_id)

            sql = f"UPDATE journal_entries SET {', '.join(updates)} WHERE id = ?"
            conn.execute(sql, params)
            conn.commit()

            return self.get_entry(entry_id, conn=conn)
        finally:
            if close_after:
                conn.close()

    def delete_entry(self, entry_id: str, conn: Optional[sqlite3.Connection] = None) -> bool:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            cursor = conn.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            if close_after:
                conn.close()
