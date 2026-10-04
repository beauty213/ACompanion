# Testing Anchor Offline

Anchor is architected to work in an airplane, in a cabin, or with networking completely disabled. **The SQLite memory engine is the foundation; the local AI is a layer on top.**

Follow the steps below to verify offline operation on your machine.

---

## 1. Automated Offline Verification

Anchor includes automated unit and integration tests that verify offline behavior by pointing to unreachable local endpoints:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the automated offline resilience and provenance test suite
PYTHONPATH=. pytest -v tests/test_ai_layer.py tests/test_provenance.py tests/test_demo_path.py
```

### What This Verifies:
1. `test_ollama_graceful_offline_handling`: Verifies the API reports accurate diagnostics without crashing when Ollama is stopped.
2. `test_embedding_offline_fallback`: Verifies local dense subword hashing takes over when remote embedding models are offline.
3. `test_insufficient_context_when_unrelated`: Verifies strict threshold gating prevents hallucinations when offline.
4. `test_full_demo_path_end_to_end`: Simulates the complete Section 13 user flow and executes offline retrieval and template reflection.

---

## 2. Manual Verification with Networking Disabled

### Step 1: Seed the Test Data
Ensure the fictional June–October scenario is seeded:
```bash
source .venv/bin/activate
python3 -m backend.seed_data
```

### Step 2: Start the Servers
Terminal 1 (Backend):
```bash
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### Step 3: Turn Off Wi-Fi / Disconnect Networking
- Disable Wi-Fi or unplug your Ethernet cable.
- Optionally stop Ollama if running: `pkill ollama`

### Step 4: Verify Local App Functionality
Open `http://localhost:5173` in your browser:
1. **Journal**: Browse past entries (June–October). Click **New Entry**, write a thought, and save. Notice it saves instantly to local SQLite without internet.
2. **Remember this**: Click **Remember this** on any journal note. Adjust the memory type and confirm. It indexes into your local Chroma store offline.
3. **Timeline**: Navigate to **Timeline**. View chronological entries and detected theme patterns grouped month by month.
4. **Ask My Past**:
   - Query: `"What boundaries did I set for myself?"`
   - Observe the response generated from your local memory bank with clickable citations (`[M1]`, `[M2]`).
   - Click **Why am I seeing this?** to inspect the exact stored memory and date.
5. **Data Export**: Navigate to **Settings** and click **Export All**. Confirm the JSON file downloads locally without any network connection.
