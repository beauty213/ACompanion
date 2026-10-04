# Anchor — Privacy Specification & Data Sovereignty

**Core Principle**: *The AI remembers. The human decides.*

Anchor is designed from the ground up as a **zero-cloud, local-first reflection companion**. When building a tool to hold someone's most vulnerable thoughts, relational dilemmas, and personal boundaries, privacy cannot be a "feature" or an add-on setting — it must be an immutable architectural constraint.

---

## 1. Where Data Lives

All user data is stored strictly on your local machine:

1. **Relational Database (`anchor.db`)**:
   - Stored in the local SQLite file: `data/anchor.db`
   - Contains: journal entries, user-confirmed memories, future-self notes, detected patterns, conversations, and configuration.
   - Bound strictly to local disk.
2. **Local Vector Store (`chroma/`)**:
   - Stored in the local Chroma database directory: `data/chroma/`
   - Contains vector embeddings and metadata: `memory_id`, `type`, `created_at`, `status`.
   - Never calls remote embedding endpoints or cloud analytics.

---

## 2. Network & Telemetry Isolation

- **Zero Cloud Fallbacks**: There is no fallback to OpenAI, Anthropic, Google, or any remote provider. If local AI is down or offline, Anchor remains fully functional as a local journaling, memory, and timeline engine without failing or leaking data.
- **Local API Binding**: The FastAPI backend binds strictly to `127.0.0.1` (localhost). It does not listen on public interfaces or broadcast across the local network.
- **No Analytics or Trackers**: No Google Analytics, no PostHog, no Sentry, no telemetry pings.
- **No Third-Party Models**: When AI inference or embedding is performed, it talks exclusively to your local Ollama daemon (`http://localhost:11434`).

---

## 3. Privacy-Preserving Logging

Anchor enforces strict privacy filtering in code:
- **No Prompt Logging**: Raw prompts, journal text, memory contents, and reflective answers are never written to log files.
- **No Plaintext Leaks**: Server logs only record operational lifecycle events (e.g. `Database initialized`, `Health check ok`).

---

## 4. User Control & Deletion Guarantee

You maintain absolute sovereignty over what is remembered and what is erased:
- **Human-Gated Memory Flow**: AI-extracted memories are suggestions only (`ai_suggested`). They only enter long-term hindsight memory if you explicitly click **Save Memory** or edit them.
- **Atomic Dual-Store Deletion**: When you delete a memory, Anchor permanently purges:
  1. The SQLite record in `memories`
  2. All provenance links in `memory_sources`
  3. The vector embedding in `Chroma`
  An automated regression test (`tests/test_retrieval.py::test_deleted_memory_never_returns`) continuously verifies that deleted memories can never be retrieved afterwards.
- **Instant Export**: Download your entire data repository anytime as clean JSON via `POST /api/export` or the Settings UI.
- **Nuke / Reset**: Erase all local memories and journals in one click with **Delete All Data** in Settings.
