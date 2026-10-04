<div align="center">

# ⚓ ANCHOR (ACompanion)

### *Local-First AI Memory & Reflection Companion with Real-World Meme Reality-Checks*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.2-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-8.3-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-32%2F32%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](tests/)
[![Git Repo](https://img.shields.io/badge/GitHub-beauty213%2FACompanion-blue.svg?logo=github)](https://github.com/beauty213/ACompanion)

<p align="center">
  <strong>The AI remembers. The human decides. Zero cloud lock-in. 100% offline sovereignty.</strong>
</p>

[Quickstart](#-quickstart) •
[Features](#-key-features) •
[Architecture](#-architecture) •
[Git Workflow](#-git-quickstart--workflow) •
[Testing](#-automated-tests) •
[Git Guide (GIT.md)](GIT.md)

</div>

---

## 📖 Overview

**Anchor** is an intentional, local-first reflection companion designed to break recurring personal loops — like contemplating whether to reconnect with someone after a painful cycle of waiting or repeating past relationship mistakes.

Most chatbots either tell you what to do, hallucinate past conversations, or send your deepest personal vulnerabilities to commercial cloud APIs. Anchor is different:
- **Hindsight Memory with Verifiable Provenance**: Anchors cite verifiable past notes (`[M1]...[Mn]`). Click *"Why am I seeing this?"* to inspect the exact date, type, and source journal note.
- **Meme Reality-Checks**: A no-nonsense, hard-hitting situational roast engine that calls out classic self-delusions (deliberately ignoring boundaries, waiting hours for replies, lending money to club-goers) with biting humor and curated internet memes.
- **Pastel Reflection Space**: A calming, modern user interface (*"What's on my mind today"*) that respects your mental space.
- **100% Local-First Sovereignty**: SQLite + ChromaDB + open-weight Ollama models (`gemma3:4b`, `nomic-embed-text`). Works completely offline — on flights, during retreats, or when disconnected from the internet.

---

## ✨ Key Features

### 🌸 1. "What's on My Mind Today" Express Journaling
- Instant thought capture with a clean, pastel aesthetic.
- Tag thoughts by context modules and severity.
- Live search and filter across your reflection history.

### 🤡 2. Meme Reality-Check & Critique Engine
- **32+ Curated Situational Matches**: Matches your reflections against universal patterns (e.g., *Left on Delivered & Replying in 2 Seconds*, *Financing Their Weekend*, *2 AM Location Stalking*, *Texting the Toxic Ex*).
- **Hard Truths & Biting Roasts**: Zero therapeutic coddling. Gives you an honest, witty wake-up call when you need it most.
- **Online & Offline Meme Explorer**: Browse, search, filter by category, or shuffle memes with direct links and source provenance (Reddit, Imgflip, Twitter, Know Your Meme).

### ⚓ 3. Hindsight Memory & Provenance Verification
- **Zero Fabricated Memories**: Strict citation gate strips any uncited claim. If validation fails, deterministic factual citations are returned.
- **Traceable History**: Every AI reflection links directly to the specific timestamped memory that triggered it.

### 📊 4. Incident & Pattern Analysis
- Chronological timeline tracking across months.
- Automatically identifies recurring themes and behavioral loops.
- "Future Self" notes: Leave commitments and guidance for your future self when cool-headed.

### 🛡️ 5. Privacy & Resilience Guarantee
- **AI-Down Resilience**: Full app functionality (journaling, browsing, data export) remains 100% available even if Ollama is paused or disabled.
- **Dual-Store Atomic Deletion**: Deleting a memory purges both SQLite and the Chroma vector database simultaneously.
- **Crisis Safety Boundaries**: Plain, empathetic, non-judgmental crisis hotline routing if self-harm or danger is detected.

---

## 🏗️ Architecture

Anchor separates the private storage layer, retrieval engine, and inference provider cleanly:

```
┌────────────────────────────────────────────────────────┐
│             React 19 + TypeScript + Vite               │
│   ("What's on my mind today", Pastel UI, Meme Explorer)│
└───────────────────────────┬────────────────────────────┘
                            │ HTTP (127.0.0.1:8001)
┌───────────────────────────▼────────────────────────────┐
│                    FastAPI Local API                   │
├───────────────────────────┬────────────────────────────┤
│       MemoryService       │    OnlineMemeService       │
│   (SQLite + VectorStore)  │   (Situations & Roasts)    │
├───────────────────────────┼────────────────────────────┤
│       JournalService      │        AIService           │
│   (CRUD + Provenance)     │  (ModelMgr + EmbeddingMgr) │
├───────────────────────────┴────────────────────────────┤
│                    ReflectionEngine                    │
│   (Retrieval, Strict Citation Gate, Safety Filter)     │
└───────────────────────────┬────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
    SQLite (anchor.db)             Ollama (127.0.0.1:11434)
    & Local Chroma Vector          gemma3:4b / nomic-embed-text
```

---

## 🚀 Quickstart

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- **[Ollama](https://ollama.ai)** (Optional for journal & memes; required for local AI reflections)

---

### 1. Clone the Git Repository
```bash
git clone https://github.com/beauty213/ACompanion.git
cd ACompanion
```

---

### 2. Backend Setup
```bash
# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

---

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

### 4. Optional: Download Local AI Models (Ollama)
```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```
*(Anchor gracefully falls back to deterministic hindsight mode if Ollama is not running).*

---

### 5. Seed Demo Data & Launch

#### Option A: Using Convenience Scripts (Recommended)
```bash
# Terminal 1: Launch Backend (http://127.0.0.1:8001)
./run_backend.sh

# Terminal 2: Launch Frontend (http://localhost:5173)
./run_frontend.sh
```

#### Option B: Manual Launch
```bash
# Terminal 1: Backend
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload

# Terminal 2: Frontend
npm --prefix frontend run dev
```

Visit **[http://localhost:5173](http://localhost:5173)** in your browser!

---

## 🐙 Git Quickstart & Workflow

For detailed Git guidelines, branching strategies, and cheatsheets, see [GIT.md](GIT.md).

### Basic Git Commands for this Repository:

```bash
# Check repository status
git status

# Fetch and sync with latest main branch
git checkout main
git pull --rebase origin main

# Create a new feature branch
git checkout -b feature/your-feature-name

# Stage and commit your changes
git add .
git commit -m "feat: describe your change"

# Push your branch to GitHub
git push -u origin feature/your-feature-name
```

---

## 🧪 Automated Tests

The repository includes a comprehensive 32-test automated test suite covering SQLite CRUD, AI provider status, ranked semantic retrieval, zero-fabrication provenance gating, meme critique generation, and incident analysis:

```bash
source .venv/bin/activate
PYTHONPATH=. pytest -v
```

### Test Coverage Highlights:
- `tests/test_memory_service.py` — SQLite transactions, status transitions, data export.
- `tests/test_ai_layer.py` — Local Ollama health, embedding resilience, offline handling.
- `tests/test_retrieval.py` — Semantic retrieval and atomic dual-store deletion.
- `tests/test_provenance.py` — Verifies 0 uncited historical claims across 20 prompt variations.
- `tests/test_critique_service.py` — Meme situation matching, verdicts, and keyword triggers.
- `tests/test_incident_analysis.py` — Incident aggregation and module analytics.
- `tests/test_demo_path.py` — End-to-end user scenario validation.

---

## 🔌 API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | Health check and system version |
| `/api/journal` | `GET`, `POST` | List and create journal entries |
| `/api/memes` | `GET` | Complete catalog of 32+ situations and memes |
| `/api/memes/search?q={query}` | `GET` | Search memes by situation or query |
| `/api/critique` | `POST` | Evaluate journal text and generate a meme reality-check |
| `/api/ai/status` | `GET` | Inspect Ollama, model availability, and embedding status |
| `/api/ai/ask-past` | `POST` | Execute verified hindsight retrieval and reflection |
| `/api/modules` | `GET`, `POST` | Manage context tracking modules |
| `/api/analysis/{module_id}` | `GET` | Generate pattern and incident analysis report |

Interactive Swagger documentation is available locally at **[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)** when the backend is running.

---

## 🔒 Privacy & Local AI Manifesto

1. **Private by Architecture**: Personal reflections, emotional vulnerabilities, and relationship boundaries must never leave your machine.
2. **Zero Commercial Data Ingestion**: Open-weight local models mean your journals are never collected into corporate training corpora.
3. **True Offline Sovereignty**: Your companion belongs to you forever, without subscription lock-in or fear of API deprecation.
4. **Resilience Over Hype**: If the AI model fails or is offline, core data remains 100% accessible and editable.

---

## 📄 License & Credits

- Licensed under the **[MIT License](LICENSE)**.
- Built with ❤️ for Hacktoberfest 2026.
- GitHub: [beauty213/ACompanion](https://github.com/beauty213/ACompanion)
