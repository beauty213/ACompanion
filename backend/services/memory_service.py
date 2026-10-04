import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.database.connection import get_db_connection
from backend.models.memory import (
    ImportanceLevel,
    MemoryCreate,
    MemoryResponse,
    MemorySource,
    MemoryStatus,
    MemoryType,
    MemoryUpdate,
)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class MemoryService:
    def __init__(self, vector_store=None):
        self._vector_store = vector_store

    def _get_vector_store(self):
        if self._vector_store is None:
            try:
                from backend.services.vector_store import get_vector_store
                self._vector_store = get_vector_store()
            except Exception as e:
                # Vector store optional if running bare SQLite
                pass
        return self._vector_store

    def create_memory(self, data: MemoryCreate, conn: Optional[sqlite3.Connection] = None) -> MemoryResponse:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            mem_id = data.id or f"mem_{uuid.uuid4().hex[:12]}"
            now = utc_now()
            confirmed_at = now if data.status in (MemoryStatus.USER_CONFIRMED, MemoryStatus.USER_EDITED) else None

            people_json = json.dumps(data.related_people or [])
            topics_json = json.dumps(data.related_topics or [])

            conn.execute(
                """
                INSERT INTO memories (
                    id, type, title, content, summary, related_people, related_topics,
                    emotion, importance, confidence, status, source_journal_id,
                    source_conversation_id, module_id, created_at, updated_at, confirmed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mem_id,
                    data.type.value if hasattr(data.type, "value") else str(data.type),
                    data.title,
                    data.content,
                    data.summary,
                    people_json,
                    topics_json,
                    data.emotion,
                    data.importance.value if hasattr(data.importance, "value") else str(data.importance),
                    data.confidence,
                    data.status.value if hasattr(data.status, "value") else str(data.status),
                    data.source_journal_id,
                    data.source_conversation_id,
                    data.module_id,
                    now,
                    now,
                    confirmed_at,
                )
            )

            # Insert source relationship if present
            sources = []
            if data.source_journal_id:
                src_id = f"src_{uuid.uuid4().hex[:10]}"
                conn.execute(
                    """
                    INSERT INTO memory_sources (id, memory_id, source_type, source_id, excerpt, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (src_id, mem_id, "journal", data.source_journal_id, data.content[:150], now)
                )
                sources.append(MemorySource(
                    id=src_id,
                    memory_id=mem_id,
                    source_type="journal",
                    source_id=data.source_journal_id,
                    excerpt=data.content[:150],
                    created_at=now
                ))
            elif data.source_conversation_id:
                src_id = f"src_{uuid.uuid4().hex[:10]}"
                conn.execute(
                    """
                    INSERT INTO memory_sources (id, memory_id, source_type, source_id, excerpt, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (src_id, mem_id, "chat", data.source_conversation_id, data.content[:150], now)
                )
                sources.append(MemorySource(
                    id=src_id,
                    memory_id=mem_id,
                    source_type="chat",
                    source_id=data.source_conversation_id,
                    excerpt=data.content[:150],
                    created_at=now
                ))

            conn.commit()

            # Index into vector store if confirmed/edited
            if data.status in (MemoryStatus.USER_CONFIRMED, MemoryStatus.USER_EDITED):
                vs = self._get_vector_store()
                if vs:
                    try:
                        people_str = " ".join(data.related_people or [])
                        topics_str = " ".join(data.related_topics or [])
                        full_text = f"{data.title or ''} {data.content} {data.emotion or ''} {people_str} {topics_str}".strip()
                        vs.add(
                            memory_id=mem_id,
                            text=full_text,
                            metadata={
                                "type": data.type.value if hasattr(data.type, "value") else str(data.type),
                                "created_at": now,
                                "status": data.status.value if hasattr(data.status, "value") else str(data.status),
                                "importance": data.importance.value if hasattr(data.importance, "value") else str(data.importance),
                            }
                        )
                    except Exception as e:
                        print(f"[MemoryService] Warning: Vector store sync failed: {e}")

            return self.get_memory(mem_id, conn=conn)

        finally:
            if close_after:
                conn.close()

    def get_memory(self, memory_id: str, conn: Optional[sqlite3.Connection] = None) -> Optional[MemoryResponse]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
            if not row:
                return None

            sources_rows = conn.execute("SELECT * FROM memory_sources WHERE memory_id = ?", (memory_id,)).fetchall()
            sources = [
                MemorySource(
                    id=s["id"],
                    memory_id=s["memory_id"],
                    source_type=s["source_type"],
                    source_id=s["source_id"],
                    excerpt=s["excerpt"],
                    created_at=s["created_at"],
                )
                for s in sources_rows
            ]

            return self._row_to_memory(row, sources)
        finally:
            if close_after:
                conn.close()

    def list_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        status: Optional[MemoryStatus] = None,
        importance: Optional[ImportanceLevel] = None,
        module_id: Optional[str] = None,
        search_query: Optional[str] = None,
        include_suggested: bool = True,
        conn: Optional[sqlite3.Connection] = None,
    ) -> List[MemoryResponse]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            sql = "SELECT * FROM memories WHERE 1=1"
            params: List[Any] = []

            if module_id:
                sql += " AND module_id = ?"
                params.append(module_id)

            if memory_type:
                sql += " AND type = ?"
                params.append(memory_type.value if hasattr(memory_type, "value") else str(memory_type))

            if status:
                sql += " AND status = ?"
                params.append(status.value if hasattr(status, "value") else str(status))
            elif not include_suggested:
                sql += " AND status IN ('user_confirmed', 'user_edited')"

            if importance:
                sql += " AND importance = ?"
                params.append(importance.value if hasattr(importance, "value") else str(importance))

            if search_query:
                sql += " AND (content LIKE ? OR title LIKE ? OR summary LIKE ?)"
                q = f"%{search_query}%"
                params.extend([q, q, q])

            sql += " ORDER BY created_at DESC"

            rows = conn.execute(sql, params).fetchall()
            
            # Fetch all sources for these memories in one query
            if rows:
                ids = [r["id"] for r in rows]
                placeholders = ",".join("?" for _ in ids)
                sources_rows = conn.execute(
                    f"SELECT * FROM memory_sources WHERE memory_id IN ({placeholders})",
                    ids
                ).fetchall()
                sources_by_mem: Dict[str, List[MemorySource]] = {}
                for s in sources_rows:
                    mid = s["memory_id"]
                    if mid not in sources_by_mem:
                        sources_by_mem[mid] = []
                    sources_by_mem[mid].append(MemorySource(
                        id=s["id"],
                        memory_id=s["memory_id"],
                        source_type=s["source_type"],
                        source_id=s["source_id"],
                        excerpt=s["excerpt"],
                        created_at=s["created_at"],
                    ))
            else:
                sources_by_mem = {}

            return [self._row_to_memory(r, sources_by_mem.get(r["id"], [])) for r in rows]
        finally:
            if close_after:
                conn.close()

    def update_memory(self, memory_id: str, data: MemoryUpdate, conn: Optional[sqlite3.Connection] = None) -> Optional[MemoryResponse]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            current = self.get_memory(memory_id, conn=conn)
            if not current:
                return None

            now = utc_now()
            updates = []
            params = []

            if data.title is not None:
                updates.append("title = ?")
                params.append(data.title)
            if data.content is not None:
                updates.append("content = ?")
                params.append(data.content)
            if data.summary is not None:
                updates.append("summary = ?")
                params.append(data.summary)
            if data.type is not None:
                updates.append("type = ?")
                params.append(data.type.value if hasattr(data.type, "value") else str(data.type))
            if data.related_people is not None:
                updates.append("related_people = ?")
                params.append(json.dumps(data.related_people))
            if data.related_topics is not None:
                updates.append("related_topics = ?")
                params.append(json.dumps(data.related_topics))
            if data.emotion is not None:
                updates.append("emotion = ?")
                params.append(data.emotion)
            if data.importance is not None:
                updates.append("importance = ?")
                params.append(data.importance.value if hasattr(data.importance, "value") else str(data.importance))
            if data.module_id is not None:
                updates.append("module_id = ?")
                params.append(data.module_id)

            if data.status is not None:
                st_val = data.status.value if hasattr(data.status, "value") else str(data.status)
                updates.append("status = ?")
                params.append(st_val)
                # Transitioning into confirmed/edited marks confirmed_at
                if st_val in (MemoryStatus.USER_CONFIRMED.value, MemoryStatus.USER_EDITED.value) and not current.confirmed_at:
                    updates.append("confirmed_at = ?")
                    params.append(now)

            updates.append("updated_at = ?")
            params.append(now)

            params.append(memory_id)
            sql = f"UPDATE memories SET {', '.join(updates)} WHERE id = ?"
            conn.execute(sql, params)
            conn.commit()

            updated_memory = self.get_memory(memory_id, conn=conn)
            
            # Sync with vector store
            vs = self._get_vector_store()
            if vs and updated_memory:
                if updated_memory.status in (MemoryStatus.USER_CONFIRMED, MemoryStatus.USER_EDITED):
                    try:
                        p_str = " ".join(updated_memory.related_people or [])
                        t_str = " ".join(updated_memory.related_topics or [])
                        full_up_text = f"{updated_memory.title or ''} {updated_memory.content} {updated_memory.emotion or ''} {p_str} {t_str}".strip()
                        vs.add(
                            memory_id=memory_id,
                            text=full_up_text,
                            metadata={
                                "type": updated_memory.type.value if hasattr(updated_memory.type, "value") else str(updated_memory.type),
                                "created_at": updated_memory.created_at,
                                "status": updated_memory.status.value if hasattr(updated_memory.status, "value") else str(updated_memory.status),
                                "importance": updated_memory.importance.value if hasattr(updated_memory.importance, "value") else str(updated_memory.importance),
                            }
                        )
                    except Exception as e:
                        print(f"[MemoryService] Warning: Vector store update failed: {e}")
                else:
                    # If switched back to suggested or unconfirmed, remove from vector index
                    vs.delete(memory_id)

            return updated_memory
        finally:
            if close_after:
                conn.close()

    def delete_memory(self, memory_id: str, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Completely deletes a memory, its vector, and all source references."""
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            conn.execute("DELETE FROM memory_sources WHERE memory_id = ?", (memory_id,))
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()

            # Remove from vector store
            vs = self._get_vector_store()
            if vs:
                vs.delete(memory_id)

            return cursor.rowcount > 0
        finally:
            if close_after:
                conn.close()

    def delete_all(self, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Deletes all user data (memories, journal entries, conversations, etc.)."""
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            conn.execute("DELETE FROM memory_sources;")
            conn.execute("DELETE FROM memories;")
            conn.execute("DELETE FROM messages;")
            conn.execute("DELETE FROM conversations;")
            conn.execute("DELETE FROM journal_entries;")
            conn.execute("DELETE FROM future_self_messages;")
            conn.execute("DELETE FROM patterns;")
            conn.execute("DELETE FROM people;")
            conn.execute("DELETE FROM modules;")
            conn.commit()

            vs = self._get_vector_store()
            if vs:
                vs.reset()

            return True
        finally:
            if close_after:
                conn.close()

    def export_data(self, conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
        """Exports all Anchor user data to a portable JSON object."""
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            tables = [
                "journal_entries",
                "conversations",
                "messages",
                "memories",
                "memory_sources",
                "future_self_messages",
                "patterns",
                "people",
                "modules",
                "settings"
            ]
            export: Dict[str, Any] = {
                "exported_at": utc_now(),
                "version": "1.0",
                "app": "Anchor",
            }
            for table in tables:
                rows = conn.execute(f"SELECT * FROM {table}").fetchall()
                export[table] = [dict(r) for r in rows]
            return export
        finally:
            if close_after:
                conn.close()

    def _row_to_memory(self, row: sqlite3.Row, sources: List[MemorySource]) -> MemoryResponse:
        related_people = []
        if row["related_people"]:
            try:
                related_people = json.loads(row["related_people"])
            except Exception:
                related_people = []

        related_topics = []
        if row["related_topics"]:
            try:
                related_topics = json.loads(row["related_topics"])
            except Exception:
                related_topics = []

        # Check if module_id exists in row
        keys = row.keys() if hasattr(row, "keys") else []
        module_id = row["module_id"] if "module_id" in keys else None

        return MemoryResponse(
            id=row["id"],
            type=MemoryType(row["type"]),
            title=row["title"],
            content=row["content"],
            summary=row["summary"],
            related_people=related_people,
            related_topics=related_topics,
            emotion=row["emotion"],
            importance=ImportanceLevel(row["importance"] or "med"),
            confidence=row["confidence"] if row["confidence"] is not None else 1.0,
            status=MemoryStatus(row["status"]),
            source_journal_id=row["source_journal_id"],
            source_conversation_id=row["source_conversation_id"],
            module_id=module_id,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            confirmed_at=row["confirmed_at"],
            sources=sources,
        )
