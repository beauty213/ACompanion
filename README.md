# ⚓ ANCHOR — Local-First AI Memory & Reflection Companion

> **Built for the Hacktoberfest 2026 DEV "Build for a Friend" Challenge**  
> *Core Principle: The AI remembers. The human decides.*

Anchor is an intentional, local-first reflection companion. When we navigate recurring personal situations — like contemplating whether to reconnect with someone after a painful cycle of waiting — we often forget our past commitments and boundaries in the heat of the moment.

Anchor stores what you **choose** to remember, retrieves relevant past context when similar situations arise, and asks reflective questions. It **never** makes decisions for you, **never** diagnoses, and **never** tells you what to do. It is not a generic conversational chatbot; its defining feature is **hindsight memory with verifiable provenance**.

---

## 🏗️ Architecture

Anchor is built on a decoupled, offline-first architecture where the memory system operates independently of the AI layer:

```
┌────────────────────────────────────────────────────────┐
│                   React + Vite UI                      │
│     (Neutral, calm, mature, zero cloud / Ollama calls) │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP (127.0.0.1:8001)
┌───────────────────────────▼────────────────────────────┐
│                    FastAPI Local API                   │
├───────────────────────────┬────────────────────────────┤
│       MemoryService       │         AIService          │
│   (SQLite + VectorStore)  │  (ModelMgr + EmbeddingMgr) │
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

### Key Technical Pillars
1. **AI Down Resilience**: SQLite and stored memories are the foundation. If Ollama is offline or stopped, Anchor remains 100% usable (journaling, browsing memories, timeline, data export).
2. **Zero Fabricated Memory (Hard Gate)**: Small local LLMs can drift. Anchor passes numbered memories `[M1]...[Mn]` and verifies citations server-side. Any uncited claims ("you told me...", "you previously felt...") are stripped. If validation fails twice, a deterministic template constructed directly from retrieved memories is returned.
3. **Dual-Store Atomic Deletion**: Deleting a memory purges the SQLite row, its source relationships, and its vector embedding. A dedicated test guarantees it can never be retrieved afterwards.
4. **Safety Boundaries**: Anchor is not a therapist or crisis service. If expressions of self-harm or imminent danger are detected, Anchor immediately surfaces plain, non-judgmental crisis hotline information.

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) (optional for base memory usage; required for local inference)

### 2. Install & Setup
```bash
# Clone repository
git clone https://github.com/your-repo/anchor.git
cd anchor

# Setup Python Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # or pip install fastapi uvicorn pydantic pytest httpx chromadb

# Install Frontend Dependencies
npm --prefix frontend install
```

### 3. Local Model Setup (Ollama)
```bash
# Pull the default open-weight reflection and embedding models
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

### 4. Seed Demo Data & Launch
```bash
# Seed the fictional June–October scenario
source .venv/bin/activate
python3 -m backend.seed_data

# Option A: Using convenience scripts
./run_backend.sh     # Terminal 1 (runs on http://127.0.0.1:8001)
./run_frontend.sh    # Terminal 2 (runs on http://localhost:5173)

# Option B: Manual commands (run from the project root)
# Terminal 1:
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8001

# Terminal 2:
npm --prefix frontend run dev
```
Open **http://localhost:5173** in your browser.

---

## 🎬 The Demo Path (Section 13)

1. **Write**: In the Journal tab, write:
   > *"I'm thinking about reconnecting with this person."*
2. **Retrieve Past Context**: Anchor surfaces past records from June–August:
   > *"You mentioned something similar before [M1]. You previously recorded (Boundary): 'I step back and preserve space whenever communication becomes an anxious one-sided waiting game.' What feels different this time?"*
3. **Verify Provenance**: Click **Why am I seeing this?** to inspect the exact date, type, and source journal note.
4. **Inspect Timeline**: View the chronological journey across June–October and observe the recurring theme banner.
5. **Future Self Note**: See the note you left for yourself:
   > *"Remember how heavy it felt waiting by the phone all summer. If you consider reconnecting, ask what is actually different before stepping back in."*
6. **Decide & Save**: Reflect on *"What feels different this time?"* and save your new confirmed memory.
7. **Offline Test**: Disconnect Wi-Fi or kill Ollama (`pkill ollama`). Query **Ask My Past** and watch Anchor generate a local reflection completely offline!

---

## 🔒 Why Open-Weight and Local Matters

Building Anchor as a local-first software utilizing open-weight AI models (`gemma3:4b`, `nomic-embed-text`) is not merely a technical preference — it is an ethical requirement:

1. **Privacy of Vulnerable Reflections**: Personal reflections contain relationship dynamics, boundaries, emotional vulnerabilities, and private dilemmas. Sending these thoughts to third-party cloud APIs poses unacceptable data leakage and behavioral profiling risks.
2. **Zero Vendor Lock-In & Cloud Dependency**: Proprietary APIs can be sunset, terms of service can change, and subscription costs can skyrocket. Open-weight models belong to the user indefinitely.
3. **True Offline Sovereignty**: Life happens everywhere — on airplanes, in rural retreats, or during power outages. Anchor works without internet connectivity.
4. **Model Inspectability & Swappability**: Users can inspect, swap, or fine-tune models behind standard interfaces without rewriting their companion.
5. **Zero Training on Personal Data**: Your personal journals and private thoughts are never ingested into commercial training corpora.

---

## 💬 Built for a Friend: Feedback & Evolution

Anchor was created for a close friend who noticed a recurring pattern of giving second chances to people who routinely went silent for days, only to re-experience the same letdown. She needed a calm, non-judgmental space that wouldn't lecture her or tell her what to do, but would gently hold up a mirror to her own past words when the familiar dilemma returned.

> *Placeholder: Awaiting post-challenge feedback notes from the friend this was built for (to be included with her consent; no real personal data will ever be committed to this repository).*

---

## 🧪 Running Automated Tests

Run the complete 18-test automated test suite:
```bash
source .venv/bin/activate
PYTHONPATH=. pytest -v tests/
```

- `tests/test_memory_service.py`: SQLite CRUD, status transitions, export/reset/seed.
- `tests/test_ai_layer.py`: Local AI provider health, model manager, graceful offline handling.
- `tests/test_retrieval.py`: Ranked semantic retrieval and atomic dual-store deletion.
- `tests/test_provenance.py`: Zero uncited historical claims across 20 test prompts & crisis safety.
- `tests/test_demo_path.py`: Complete end-to-end Section 13 demo scenario.

---

## 📄 License
MIT License. Built for Hacktoberfest 2026.
