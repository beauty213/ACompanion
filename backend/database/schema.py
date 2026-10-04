import sqlite3
from backend.database.connection import get_db_connection

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS journal_entries (
    id TEXT PRIMARY KEY,
    title TEXT,
    content TEXT NOT NULL,
    module_id TEXT,
    critique_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    citations TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    related_people TEXT,
    related_topics TEXT,
    emotion TEXT,
    importance TEXT DEFAULT 'med',
    confidence REAL DEFAULT 1.0,
    status TEXT NOT NULL,
    source_journal_id TEXT,
    source_conversation_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    confirmed_at TEXT,
    FOREIGN KEY(source_journal_id) REFERENCES journal_entries(id) ON DELETE SET NULL,
    FOREIGN KEY(source_conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS memory_sources (
    id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    excerpt TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(memory_id) REFERENCES memories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS future_self_messages (
    id TEXT PRIMARY KEY,
    message TEXT NOT NULL,
    related_person TEXT,
    related_topic TEXT,
    importance TEXT DEFAULT 'med',
    trigger_context TEXT NOT NULL,
    expires_at TEXT,
    created_at TEXT NOT NULL,
    triggered_at TEXT,
    dismissed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS patterns (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    memory_ids TEXT NOT NULL,
    dismissed INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS people (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    relationship TEXT,
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS modules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    alias TEXT,
    relationship TEXT,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(status);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_journal_created_at ON journal_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
"""

def init_db(conn: sqlite3.Connection = None) -> None:
    """Initializes the database schema and performs non-destructive column additions."""
    close_after = False
    if conn is None:
        conn = get_db_connection()
        close_after = True

    try:
        conn.executescript(CREATE_TABLES_SQL)

        # Non-destructive migrations for existing SQLite databases
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(journal_entries)")
        journal_cols = [row[1] for row in cursor.fetchall()]
        if "module_id" not in journal_cols:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN module_id TEXT REFERENCES modules(id) ON DELETE SET NULL")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_journal_module ON journal_entries(module_id)")
        if "critique_json" not in journal_cols:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN critique_json TEXT")

        cursor.execute("PRAGMA table_info(memories)")
        memories_cols = [row[1] for row in cursor.fetchall()]
        if "module_id" not in memories_cols:
            cursor.execute("ALTER TABLE memories ADD COLUMN module_id TEXT REFERENCES modules(id) ON DELETE SET NULL")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_module ON memories(module_id)")

        cursor.execute("PRAGMA table_info(modules)")
        mod_cols = [row[1] for row in cursor.fetchall()]
        if "alias" not in mod_cols:
            cursor.execute("ALTER TABLE modules ADD COLUMN alias TEXT")

        conn.commit()
    finally:
        if close_after:
            conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")

