import sqlite3
from typing import Generator
from backend.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with foreign keys enabled, WAL mode, and thread-safety configured."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Dependency generator for FastAPI routes."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
