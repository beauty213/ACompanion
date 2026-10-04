import re
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional
from backend.database.connection import get_db_connection
from backend.models.future_self import FutureSelfResponse
from backend.models.memory import ImportanceLevel

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class FutureSelfService:
    def check_triggers(self, text: str, conn: Optional[sqlite3.Connection] = None) -> List[FutureSelfResponse]:
        """Checks if the given text matches any non-dismissed future self trigger context."""
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            rows = conn.execute("SELECT * FROM future_self_messages WHERE dismissed = 0").fetchall()
            triggered_notes: List[FutureSelfResponse] = []
            text_lower = text.lower()

            for r in rows:
                triggers = [t.strip().lower() for t in r["trigger_context"].split(",") if t.strip()]
                # Check for keyword or phrase overlap
                is_match = False
                for trig in triggers:
                    if trig and trig in text_lower:
                        is_match = True
                        break

                if is_match:
                    now = utc_now()
                    conn.execute("UPDATE future_self_messages SET triggered_at = ? WHERE id = ?", (now, r["id"]))
                    conn.commit()
                    triggered_notes.append(FutureSelfResponse(
                        id=r["id"],
                        message=r["message"],
                        related_person=r["related_person"],
                        related_topic=r["related_topic"],
                        importance=ImportanceLevel(r["importance"] or "med"),
                        trigger_context=r["trigger_context"],
                        expires_at=r["expires_at"],
                        created_at=r["created_at"],
                        triggered_at=now,
                        dismissed=bool(r["dismissed"]),
                    ))

            return triggered_notes
        finally:
            if close_after:
                conn.close()
