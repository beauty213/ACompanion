import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from backend.database.connection import get_db_connection
from backend.models.module import Module, ModuleCreate, ModuleUpdate, ModuleWithStats

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class ModuleService:
    def create_module(self, data: ModuleCreate, conn: Optional[sqlite3.Connection] = None) -> Module:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            # Check for existing module with same name or alias (case-insensitive deduplication)
            normalized_name = data.name.strip().lower()
            existing_rows = conn.execute("SELECT * FROM modules").fetchall()
            for r in existing_rows:
                r_name = (r["name"] or "").strip().lower()
                r_alias = (r["alias"] or "").strip().lower() if "alias" in r.keys() and r["alias"] else ""
                if r_name == normalized_name or (r_alias and r_alias == normalized_name):
                    # Reuse existing module to avoid fragmented duplicate tracks
                    return Module(
                        id=r["id"],
                        name=r["name"],
                        alias=r["alias"] if "alias" in r.keys() else None,
                        relationship=r["relationship"],
                        description=r["description"],
                        created_at=r["created_at"],
                        updated_at=r["updated_at"],
                    )

            mod_id = data.id or f"mod_{uuid.uuid4().hex[:12]}"
            now = utc_now()

            conn.execute(
                """
                INSERT INTO modules (id, name, alias, relationship, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (mod_id, data.name.strip(), data.alias.strip() if data.alias else None, data.relationship, data.description, now, now)
            )
            conn.commit()
            return Module(
                id=mod_id,
                name=data.name.strip(),
                alias=data.alias.strip() if data.alias else None,
                relationship=data.relationship,
                description=data.description,
                created_at=now,
                updated_at=now,
            )
        finally:
            if close_after:
                conn.close()

    def get_module(self, module_id: str, conn: Optional[sqlite3.Connection] = None) -> Optional[Module]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            row = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
            if not row:
                return None
            return Module(
                id=row["id"],
                name=row["name"],
                alias=row["alias"] if "alias" in row.keys() else None,
                relationship=row["relationship"],
                description=row["description"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        finally:
            if close_after:
                conn.close()

    def list_modules(self, conn: Optional[sqlite3.Connection] = None) -> List[ModuleWithStats]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            rows = conn.execute("SELECT * FROM modules ORDER BY updated_at DESC").fetchall()
            results = []
            for r in rows:
                mod_id = r["id"]
                # Incident count & latest date
                stat_row = conn.execute(
                    "SELECT COUNT(*) as cnt, MAX(created_at) as latest FROM journal_entries WHERE module_id = ?",
                    (mod_id,)
                ).fetchone()
                # Boundary count
                bound_row = conn.execute(
                    "SELECT COUNT(*) as cnt FROM memories WHERE module_id = ? AND type = 'Boundary'",
                    (mod_id,)
                ).fetchone()

                results.append(
                    ModuleWithStats(
                        id=r["id"],
                        name=r["name"],
                        alias=r["alias"] if "alias" in r.keys() else None,
                        relationship=r["relationship"],
                        description=r["description"],
                        created_at=r["created_at"],
                        updated_at=r["updated_at"],
                        incident_count=stat_row["cnt"] if stat_row else 0,
                        latest_incident_date=stat_row["latest"] if stat_row and stat_row["latest"] else None,
                        active_boundaries_count=bound_row["cnt"] if bound_row else 0,
                    )
                )
            return results
        finally:
            if close_after:
                conn.close()

    def update_module(self, module_id: str, data: ModuleUpdate, conn: Optional[sqlite3.Connection] = None) -> Optional[Module]:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            current = self.get_module(module_id, conn=conn)
            if not current:
                return None

            now = utc_now()
            updates = []
            params = []

            if data.name is not None:
                updates.append("name = ?")
                params.append(data.name.strip())
            if data.alias is not None:
                updates.append("alias = ?")
                params.append(data.alias.strip() if data.alias else None)
            if data.relationship is not None:
                updates.append("relationship = ?")
                params.append(data.relationship)
            if data.description is not None:
                updates.append("description = ?")
                params.append(data.description)

            if not updates:
                return current

            updates.append("updated_at = ?")
            params.append(now)
            params.append(module_id)

            conn.execute(f"UPDATE modules SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

            return self.get_module(module_id, conn=conn)
        finally:
            if close_after:
                conn.close()

    def delete_module(self, module_id: str, conn: Optional[sqlite3.Connection] = None) -> bool:
        close_after = False
        if conn is None:
            conn = get_db_connection()
            close_after = True

        try:
            # Unlink entries and memories
            conn.execute("UPDATE journal_entries SET module_id = NULL WHERE module_id = ?", (module_id,))
            conn.execute("UPDATE memories SET module_id = NULL WHERE module_id = ?", (module_id,))
            cursor = conn.execute("DELETE FROM modules WHERE id = ?", (module_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            if close_after:
                conn.close()
