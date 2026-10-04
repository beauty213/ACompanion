import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from backend.database.connection import get_db_connection
from backend.models.pattern import PatternDetectResponse, PatternResponse
from backend.services.memory_service import MemoryService

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class PatternService:
    def __init__(self, memory_service: Optional[MemoryService] = None):
        self.memory_service = memory_service or MemoryService()

    def detect_patterns(self, conn: Optional[sqlite3.Connection] = None) -> PatternDetectResponse:
        """On-demand pattern detection across confirmed memories. Requires >= 3 supporting memories."""
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            memories = self.memory_service.list_memories(include_suggested=False, conn=conn)
            if len(memories) < 3:
                return PatternDetectResponse(
                    detected=False,
                    patterns=[],
                    message="Insufficient memories to detect patterns (minimum 3 required).",
                )

            # Group memories by shared topics, people, or track
            clusters: Dict[str, List[str]] = {}
            mod_names: Dict[str, str] = {}
            for r in conn.execute("SELECT id, name, alias FROM modules").fetchall():
                mod_names[r["id"]] = r["alias"] if ("alias" in r.keys() and r["alias"]) else r["name"]

            for m in memories:
                # Group by track / module
                if m.module_id and m.module_id in mod_names:
                    track_label = mod_names[m.module_id]
                    clusters.setdefault(f"Track: {track_label}", []).append(m.id)
                # Group by people
                for p in m.related_people:
                    key = f"Person: {p}"
                    clusters.setdefault(key, []).append(m.id)
                # Group by topics
                for t in m.related_topics:
                    key = f"Topic: {t}"
                    clusters.setdefault(key, []).append(m.id)

            # Filter clusters with >= 3 distinct memories
            new_patterns: List[PatternResponse] = []
            now = utc_now()

            for key, mem_ids in clusters.items():
                unique_ids = list(dict.fromkeys(mem_ids))
                if len(unique_ids) >= 3:
                    pat_id = f"pat_{uuid.uuid4().hex[:8]}"
                    title = f"Recurring theme regarding {key}"
                    desc = f"These entries contain similar themes across your past reflections regarding {key}."

                    # Check if similar pattern already exists
                    existing = conn.execute(
                        "SELECT id FROM patterns WHERE title = ?", (title,)
                    ).fetchone()
                    if not existing:
                        conn.execute(
                            """
                            INSERT INTO patterns (id, title, description, memory_ids, dismissed, created_at)
                            VALUES (?, ?, ?, ?, 0, ?)
                            """,
                            (pat_id, title, desc, json.dumps(unique_ids), now)
                        )
                        conn.commit()
                        new_patterns.append(PatternResponse(
                            id=pat_id,
                            title=title,
                            description=desc,
                            memory_ids=unique_ids,
                            dismissed=False,
                            created_at=now,
                        ))

            # Fetch all active non-dismissed patterns
            all_rows = conn.execute(
                "SELECT * FROM patterns WHERE dismissed = 0 ORDER BY created_at DESC"
            ).fetchall()

            final_patterns = []
            for r in all_rows:
                try:
                    mids = json.loads(r["memory_ids"])
                except Exception:
                    mids = []
                final_patterns.append(PatternResponse(
                    id=r["id"],
                    title=r["title"],
                    description=r["description"],
                    memory_ids=mids,
                    dismissed=bool(r["dismissed"]),
                    created_at=r["created_at"],
                ))

            return PatternDetectResponse(
                detected=len(final_patterns) > 0,
                patterns=final_patterns,
                message=f"Detected {len(final_patterns)} theme pattern(s) across your past entries.",
            )
        finally:
            if close_after:
                conn.close()
