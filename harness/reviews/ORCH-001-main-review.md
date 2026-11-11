# ORCH-001 — Main Agent review

## Decision

`ACCEPTED — LANGGRAPH RUNTIME`

ORCH-001 is accepted and ready for downstream Phase 4 work. The runtime now
uses a real compiled LangGraph `StateGraph`; the graph is the workflow engine,
while the backend Tool Gateway remains the authorization and execution
boundary.

## Acceptance evidence

- Graph nodes: `prepare`, `retrieve`, `synthesize`, `finish`.
- Graph edges: `START` through the conditional retrieval loop to `END`.
- Exact Tool Gateway allowlist: `search_documents`,
  `read_authorized_chunk`, `get_document_metadata`.
- Bounds: maximum 2 retrieval rounds, 4 subqueries and 8 tool calls.
- Guardrails reject unsafe user input, untrusted retrieved text and unsafe
  answer output.
- No runtime multi-agent architecture was introduced.
- LangGraph dependency: `langgraph>=1.2,<2.0`; tested version `1.2.20`.
- ORCH/Gateway focused tests: `69 passed`.
- Required QA matrix: `40 passed`.
- Full regression: `519 passed, 2 skipped`; skips are the existing DB smoke
  tests without `DB001_DATABASE_URL`.
- `compileall`, `git diff --check` and harness validation passed.
- Graphify query and post-change refresh completed.

## Scope boundary

The accepted implementation is a provider-neutral in-memory runtime. Durable
PostgreSQL-backed scope/policy repositories, real retrieval backends, Qdrant,
provider/API-key wiring, durable job/checkpoint resume and deployment remain
owned by later tasks. `CHAT-001` owns durable query jobs, conversation history
and the later checkpoint/resume integration. The project-wide production
  quality gate remains deferred.
