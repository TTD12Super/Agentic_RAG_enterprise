# RAG-V4-001 — Main Agent review

## Decision

`ACCEPTED — RUNTIME INTEGRATED`

Parent-child expansion is now part of the real hybrid retrieval-to-answer
path. It runs only after child retrieval and reranking, rechecks the parent
against the authoritative Dense PEP, preserves child provenance, and adds
bounded parent context without changing ranking.

## Evidence

- Parent helper and runtime integration: `30 passed` in the focused suite.
- Required QA matrix: `40 passed` (`10` behavior, `10` contract/integration,
  `10` security/adversarial, `10` E2E/operational).
- Full backend/integration/evaluation/security/QA regression: `490 passed,
  2 skipped`.
- `compileall`, `git diff --check` and `python3 scripts/validate_harness.py`:
  PASS.
- Graphify refreshed after implementation: `2,833 nodes`, `8,025 edges`.

## Security boundary

Cross-tenant, cross-document, cross-version, inactive, staging, denied and
policy-outage parents are omitted fail-closed. A valid child remains valid
when its parent is unavailable. Parent text is placed in the existing
untrusted context envelope and is never trusted as instructions.

## Scope boundary

This is the provider-neutral in-memory runtime. Durable parent lookup through
PostgreSQL/Qdrant and live provider tests remain owned by later integration
tasks; the production quality gate remains deferred by the recorded owner
decision.
