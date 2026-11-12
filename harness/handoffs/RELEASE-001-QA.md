# Handoff — RELEASE-001 / QA Agent

- Task ID: `RELEASE-001`
- Agent owner: `qa_tester`
- Status: `BLOCKED`
- Release decision: **NOT DONE; no go/no-go approval issued**
- Scope: local-only QA; no Render/Vercel/cloud writes and no API keys
- Contract/version context: approved v1 contract surfaces; current local FE–BE integration worktree

## Upstream and documents checked

Read before execution:

- `AGENTS.md`, `tests/AGENTS.md`, `tests/README.md`
- `harness/tasks/tasks.json` (`RELEASE-001` scope and acceptance)
- `harness/checklists/phase-5.md`, `phase-6.md`, `phase-7.md`
- `docs/testing/quality-gates.md`, `docs/testing/README.md`, `docs/testing/golden-dataset-schema.md`
- `docs/operations/deployment-runbook.md`, `docs/operations/incident-response.md`
- applicable `docs/security/*`, `docs/contracts/README.md`, evaluation plan and ORCH-001 QA handoff

First codebase navigation query, as required by `AGENTS.md`:

```text
graphify query "RELEASE-001 release quality gates QA full local backend pytest frontend typecheck lint test build integration evaluation security suites blockers handoff" --graph graphify-out/graph.json --budget 5000
```

Result: exit `0`; graph had `3,875` nodes, BFS depth `2`, `1,428` matching nodes; output was truncated by the requested token budget. It identified the backend, frontend, integration, evaluation, security, LangGraph, citation and handoff surfaces.

## Files changed by this QA task

Only this handoff was written:

- `harness/handoffs/RELEASE-001-QA.md`

No backend, frontend, infrastructure, task registry, contract or test source was modified by this QA task. The frontend production build was directed to `/tmp`; the disposable PostgreSQL container used loopback-only synthetic data and was stopped after testing. No commit, push or deployment was performed.

The worktree was already dirty and also contained unrelated/concurrent changes. Current status included modified `.gitignore`, `backend/app/db/runtime.py`, `backend/app/main.py`, `graphify-out/*`, phase/task files and QA tests, plus untracked Neon/package/egg-info files. These were not changed by this task.

## Commands and results

All Python suites were run with `PYTHONDONTWRITEBYTECODE=1` and with cloud/provider variables unset (`DATABASE_URL`, `DATABASE_URL_UNPOOLED`, `BACKEND_DATABASE_URL`, `DB001_DATABASE_URL`, LLM keys, `QDRANT_URL`, and `REDIS_URL`) unless the command explicitly supplied the loopback-only synthetic DB URL below.

### Backend

```text
backend/.venv/bin/python -m pytest backend/tests -ra --tb=short
```

PASS: `270 passed, 2 skipped`, exit `0`.

The skips were the two opt-in disposable-PostgreSQL checks because no local DB URL was supplied in this first isolated run.

Local database rerun:

```text
docker compose -f infra/docker/postgres-test.compose.yml up -d
DB001_DATABASE_URL=postgresql+psycopg://enterprise_rag_test:synthetic_only_not_secret@127.0.0.1:55432/enterprise_rag_test \
  backend/.venv/bin/alembic -c backend/app/db/alembic.ini upgrade head
```

PASS: container health became `healthy`; Alembic applied `0001_identity_tenants` through `0005_indexes`, exit `0`.

```text
DB001_DATABASE_URL=postgresql+psycopg://enterprise_rag_test:synthetic_only_not_secret@127.0.0.1:55432/enterprise_rag_test \
  backend/.venv/bin/python -m pytest backend/tests -ra --tb=short
docker compose -f infra/docker/postgres-test.compose.yml down --remove-orphans
```

PASS: `272 passed`, exit `0`; cleanup exit `0`.

### Frontend

From `frontend/`:

```text
npm run typecheck
```

PASS, exit `0`.

```text
npm run lint
```

PASS, exit `0`.

```text
npm test -- --run
```

PASS: `1` test file, `9 passed`, exit `0`.

```text
BUILD_DIR=$(mktemp -d /tmp/release-001-frontend-dist.XXXXXX)
npm run build -- --outDir "$BUILD_DIR"
```

PASS: Vite production build, `29 modules transformed`, exit `0`; output was outside the repository.

### Contract, integration, evaluation and security suites

```text
backend/.venv/bin/python -m pytest tests/integration -ra --tb=short
```

PASS: `43 passed`, exit `0`.

```text
backend/.venv/bin/python -m pytest tests/evaluation -ra --tb=short
```

PASS: `52 passed`, exit `0`.

```text
backend/.venv/bin/python -m pytest tests/security -ra --tb=short
```

PASS: `20 passed`, exit `0`.

The documented one-command contracts invocation initially failed collection because its tests import a package-local `_baseline` without an explicit path:

```text
backend/.venv/bin/python -m pytest tests/contracts -ra --tb=short
```

BLOCKED at collection: `0 items / 4 errors`, `ModuleNotFoundError: No module named '_baseline'`, exit `2`.

The same suite was executed with its required local import path and isolated import mode:

```text
PYTHONPATH="$PWD/tests/contracts" backend/.venv/bin/python -m pytest \
  tests/contracts --import-mode=importlib -ra --tb=short
```

PASS: `40 passed`, exit `0`.

### QA four-family packages

The one-command invocation is not executable as currently structured because all packages reuse module basenames and local `_baseline` imports:

```text
backend/.venv/bin/python -m pytest tests/qa -ra --tb=short
```

BLOCKED at collection: `160 items / 84 errors`, consisting of import-file mismatches and missing package-local `_baseline`/`_common` modules, exit `2`.

Each of the 25 QA packages was then run separately with its own `PYTHONPATH` and `--import-mode=importlib`:

```text
PYTHONPATH="$PWD/tests/qa/<package>" backend/.venv/bin/python -m pytest \
  tests/qa/<package> --import-mode=importlib -q -ra --tb=short
```

Aggregate result: `25` packages, `968` tests executed; `956 passed`, `12 failed`, exit `1` overall.

Passing packages (`23`):

`admin_api`, `answer_baseline`, `audit`, `authorization`, `backend_boot`, `cache_memory`, `chat_api`, `dashboard_api`, `db`, `evidence`, `graphify`, `guardrails`, `identity`, `infra_boot`, `infra_dev`, `ingestion`, `knowledge`, `model`, `monitoring`, `orchestration_langgraph`, `prompt`, `rag_hybrid`, `rag_v4_citation`.

## Blocking findings

### `FINDING-RELEASE-001-FE-QA`: frontend QA contract is stale against the current integrated FE

Package: `tests/qa/frontend_boot`; result: `29 passed, 11 failed`.

The failing assertions expect the previous static shell: `copy.title`, a client-side `Preview role` selector, static readiness labels such as `Completed · confidence` and `RAG cluster healthy`, and exact old boundary copy. The current `frontend/src/App.tsx` intentionally uses backend identity, live API data, and removes role preview. The security pattern test also rejects the legitimate sign-in request field `password:`; it does not distinguish hard-coded credentials from a user-entered authentication payload.

This is a release blocker until the QA contract is updated/reviewed to match the approved live FE–BE behavior, or the implementation is explicitly required to restore the old shell. No test was weakened here.

### `FINDING-RELEASE-001-RAG-EGRESS`: blocked model egress returns `ERROR`, not safe abstention

Failing test:

```text
tests/qa/rag/test_behavior_component.py::DenseRetrievalBehaviorTests::test_internal_query_egress_denial_fails_closed
```

Result: expected `INSUFFICIENT_EVIDENCE` with no evidence; actual status was `ERROR`.

This is a behavior mismatch at the model-egress denial boundary. It must be reviewed by Backend/RAG/Security before release because the release policy requires fail-closed behavior and safe no-answer handling. This QA task did not modify the runtime.

## Release gates not evidenced / not run

- V5 bounded-agent Golden Dataset evaluation against the real ORCH-001 integration: **NOT RUN**. No V5 runner or V5 evaluation suite exists in `tests/evaluation`; the checked-in evaluator is EVAL-001 for deterministic V1–V3 and explicitly records V4 as `NOT_RUN`.
- Real provider-backed LLM generation, calibrated confidence, token cost and external-provider latency: **NOT MEASURED**; no API key was used.
- Production-scale load target, 200 MB/OOM upload test, real object storage/Qdrant, restore drill/RPO/RTO, and production monitoring/alert recipients: **NOT RUN** in local-only scope.
- External deployment gate: **NOT RUN** by instruction; no Render/Vercel/cloud writes.
- Current deterministic evaluation passed its executable tests, but its perfect synthetic metrics are not production quality evidence; the existing report documents the oracle/local-seam limitation.

## Additional validation

```text
python3 scripts/validate_harness.py
```

PASS: `17 blocks, 8 agents, 42 tasks; no dependency cycles`, exit `0`. This validates harness scaffolding only, not application functionality or release readiness.

## Security and integration assessment

- Deterministic integration/evaluation/security suites passed, including tenant/authorization/guardrail cases in their executable local scope.
- Backend local migration and full backend suite passed after the disposable DB became healthy.
- No cloud credentials, LLM keys, real enterprise documents or production identifiers were used.
- Release cannot be approved while the two QA findings remain and the required V5/operational evidence is absent.

## Suggested next READY tasks

1. Update/reconcile `frontend_boot` QA expectations with the approved live FE–BE contract; keep the security test focused on hard-coded secret material, not legitimate user input fields.
2. Backend/RAG/Security review and fix `FINDING-RELEASE-001-RAG-EGRESS`; rerun the complete RAG QA package and backend suite.
3. Add and run the real ORCH-001 V5 Golden Dataset evaluator without provider credentials first; obtain Project Owner approval before introducing an external LLM key.
4. Re-run RELEASE-001 locally, then request explicit Project Owner go/no-go approval. Do not update `tasks.json` to `DONE` from this handoff.

## Human approval required

Project Owner release approval is required. This handoff is evidence only and does not mark `RELEASE-001` or any phase complete.
