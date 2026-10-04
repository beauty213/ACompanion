import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router
from backend.config import HOST, PORT
from backend.database.schema import init_db

# Configure minimal privacy-preserving logging
# Explicit rule: "Never log journal text, chat content, memory contents, or prompts."
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("anchor")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database on startup
    init_db()
    logger.info("Anchor database initialized.")
    yield

app = FastAPI(
    title="Anchor Local API",
    description="Local-first AI memory and reflection companion. The AI remembers. The human decides.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS strictly configured for local UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "app": "Anchor",
        "description": "Local-first AI memory and reflection companion",
        "status": "online",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # Bind API strictly to 127.0.0.1 for local privacy
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
