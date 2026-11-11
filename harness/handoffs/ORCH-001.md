# ORCH-001 — bounded LangGraph orchestrator and Tool Gateway

## Status

`DONE — MAIN AGENT ACCEPTED`

## Delivered

- Replaced the orchestration scaffold with a real compiled LangGraph
  `StateGraph`.
- Workflow nodes are `prepare`, `retrieve`, `synthesize` and `finish`, with a
  conditional retrieval loop and an explicit `END` edge.
- `run()` invokes the compiled graph with a bounded recursion limit; it does
  not create a runtime multi-agent system.
- Retrieval is bounded to 2 rounds, 4 subqueries and 8 tool calls.
- The Tool Gateway exposes exactly the approved read-only tools:
  `search_documents`, `read_authorized_chunk` and `get_document_metadata`.
- Tool requests are typed, input/output bounded, deadline-aware,
  policy/tenant/scope checked, idempotent and fail-closed. The gateway—not the
  LLM or graph—owns authorization and backend execution.
- Retrieved text and answer output pass the existing untrusted-content
  guardrails before reaching the answer boundary or the caller.

## Files

- `backend/app/orchestration/orchestrator.py`
- `backend/app/orchestration/__init__.py`
- `backend/app/tools/gateway.py`
- `backend/app/tools/__init__.py`
- `backend/pyproject.toml`
- `backend/tests/test_orchestration_runtime.py`
- `backend/tests/test_tool_gateway.py`
- `tests/qa/orchestration_langgraph/`
- `harness/handoffs/ORCH-001-QA-001.md`
- `harness/reviews/ORCH-001-main-review.md`

## Dependency

The backend declares `langgraph>=1.2,<2.0`. Validation used LangGraph
`1.2.20`, including `StateGraph.compile()` and compiled-graph invocation.

## Evidence

- QA matrix: `40 passed` — 10 behavior/component, 10 contract/integration,
  10 security/adversarial and 10 E2E/operational.
- ORCH-001 plus Tool Gateway focused suite: `69 passed`.
- Full backend/integration/evaluation/security/QA regression including this
  task: `519 passed, 2 skipped`.
- The two skips are the existing PostgreSQL smoke tests requiring
  `DB001_DATABASE_URL`.
- `compileall` passed for production and task test paths.
- `git diff --check` passed.
- Harness validation passed after the task status update.
- Graphify was queried before review and refreshed after code changes.

## Scope boundary and residual risk

- Adapters are deterministic and in-memory. No live PostgreSQL, Qdrant,
  object storage, provider API or cloud resource is required for this task.
- Durable checkpoint/resume, queue/job integration and conversation APIs are
  deferred to `CHAT-001`; a durable LangGraph checkpointer is intentionally
  not introduced here.
- Production quality-gate thresholds remain deferred by the approved project
  decision. Per-task tests and security checks remain mandatory.
