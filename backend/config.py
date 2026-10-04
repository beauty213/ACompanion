import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = os.getenv("ANCHOR_DB_PATH", str(DATA_DIR / "anchor.db"))
CHROMA_DIR = os.getenv("ANCHOR_CHROMA_DIR", str(DATA_DIR / "chroma"))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("ANCHOR_LLM", "gemma3:4b")
DEFAULT_EMBEDDING_MODEL = os.getenv("ANCHOR_EMBED", "nomic-embed-text")

HOST = os.getenv("ANCHOR_HOST", "127.0.0.1")
PORT = int(os.getenv("ANCHOR_PORT", "8001"))

