# RELEASE-001 — Local follow-up

**Status:** `LOCAL QA GREEN / PRODUCTION BLOCKED`
**Date:** 2026-11-11
**Scope:** localhost only; no deployment, no API key, no production-data writes.

## Changes closed in this follow-up

- RAG egress denial now returns `INSUFFICIENT_EVIDENCE` instead of an internal `ERROR`.
- Document catalog listing re-applies document policy for every role, so an explicit manager DENY is honored.
- Citation preview/download rejects expired citations and fails closed when current document state is unavailable.
- Frontend QA now checks the backend-authenticated UI contract; the client role preview was not restored.
- QA packages and contract tests are package-scoped, so one aggregate pytest run no longer collides on repeated module names.

## Executed evidence

| Check | Result |
|---|---|
| `backend/.venv/bin/python -m pytest backend/tests -q` | **270 passed, 2 skipped**; the skips require `DB001_DATABASE_URL` and a disposable PostgreSQL service |
| `backend/.venv/bin/python -m pytest --import-mode=importlib tests/contracts tests/integration tests/evaluation tests/security -q` | **155 passed** |
| `backend/.venv/bin/python -m pytest tests/qa -q` | **1010 passed** |
| `frontend`: `npm run typecheck`, `npm run lint`, `npm test -- --run`, `npm run build` | **PASS**; 9 Vitest tests |
| `backend/.venv/bin/python -m compileall -q backend` | **PASS** |
| `backend/.venv/bin/python scripts/validate_harness.py` | **PASS**; 17 blocks, 8 agents, 42 tasks, no dependency cycles |
| `git diff --check` | **PASS** |

Previous disposable-PostgreSQL evidence in `RELEASE-001-QA.md` remains valid: migrations applied and **272 backend tests passed with 0 skips**. Docker was not available for a second disposable-DB run in this follow-up.

## Decision

The project is ready for the user's localhost demo/test loop. It is not production-approved. The local RAG path still uses deterministic fixtures and the following production evidence remains absent or incomplete:

- real provider/V5 agentic evaluation, citation/recall/confidence/cost thresholds;
- durable identity, ACL and document lifecycle as the authoritative authorization path;
- signed worker identity, authorized scopes, replay protection and fencing;
- production-safe browser session and append-only audit trust boundary;
- multi-instance revocation tests, latency/error/load measurements and backup/restore drill.

No LLM API key is required for the current deterministic local checks. It becomes required only when the real-provider evaluation or production RAG integration begins.

**Release recommendation:** `NO-GO for production`; continue local testing and schedule the remaining production-boundary work before deployment.
