# CHAT-001 handoff

Status: `DONE — MAIN AGENT ACCEPTED`

## Result

Implemented the smallest provider-neutral v1 chat boundary:

- `POST /api/v1/conversations` with authenticated ownership or server-issued anonymous session cookie.
- `POST /api/v1/conversations/{conversation_id}/messages` with 202 admission and idempotent replay.
- `GET /api/v1/query-jobs/{job_id}` and `/completion` with versioned status/completion payloads.
- Owner-only conversation/job access with anonymous-session isolation and fresh policy-scope checks.
- Durable repository/checkpoint protocols plus bounded in-memory adapters when no database repository is configured.
- Maintenance admission blocking, safe timeout failure, and pause/resume hooks.
- Citation preview/download with separate fresh `document:read` and `source:download` PEP checks.
- Feedback creation with one record per actor/answer, idempotent identical replay, changed-submission denial, and no comment in API/audit output.

The existing authorization, scoped memory/cache, orchestration request boundary, citation model, ingestion maintenance state and audit sink are reused. Contracts, authorization, migrations, orchestration, frontend, infra and task registry were not edited.

## Graphify evidence

Required focused query was run before raw source exploration:

```text
graphify query "CHAT-001 chat API job conversation boundary identity authorization orchestrator cache memory citation feedback" --graph graphify-out/graph.json --depth 3 --budget 3000
```

Result: `graphify-out/graph.json` with 3,350 nodes; BFS depth 3; starts included Conversation-memory boundary, Citation, reusable API/retrieval/tools/citation/cache boundary, ConversationMessage, CacheScope, authorization policy/PEP, InMemoryConversationMemory, identity store, and the existing `test_chat_001_owns_preview_download_reauthorization_recheck`; 1,468 nodes found, with an 82-node excerpt shown because the 3,000-token budget truncated the remaining 1,386 nodes.

After implementation, the required graph refresh was run:

```text
graphify update .
```

Result: 3,518 nodes, 10,466 edges, 177 communities; 2 changed source files were incrementally re-extracted. Graphify regenerated `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.html` and `graphify-out/manifest.json`.

## Exact changed files

Implementation:

- `backend/app/api/chat.py`
- `backend/app/api/identity.py`
- `backend/app/core/chat.py`
- `backend/app/feedback/__init__.py`
- `backend/app/feedback/service.py`

Tests:

- `backend/tests/test_chat_api.py`
- `tests/integration/test_chat_api.py`

Handoff/generated graph evidence:

- `harness/handoffs/CHAT-001.md`
- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.html`
- `graphify-out/graph.json`
- `graphify-out/manifest.json`

## Commands and results

```text
python3 -m compileall -q backend/app/core/chat.py backend/app/feedback backend/app/api/chat.py backend/app/api/identity.py
PASS

python3 -m pytest backend/tests/test_chat_api.py tests/integration/test_chat_api.py -q
8 passed in 0.38s

python3 -m pytest backend/tests tests/integration -q
299 passed, 2 skipped in 2.25s
Skipped: disposable PostgreSQL tests requiring DB001_DATABASE_URL.

python3 -m compileall -q backend/app backend/tests tests/integration
PASS

git diff --check
PASS
```

Focused tests cover anonymous and authenticated privacy, denied/revoked access, idempotent replay and changed replay, timeout, maintenance admission/resume, citation preview/download and revocation, and feedback replay/privacy.

## Limitations and risks

- No PostgreSQL runtime repository or live worker transport was added; the durable protocols are present and the process-local adapter is used because no database URL/repository is configured. The default local executor returns safe `INSUFFICIENT_EVIDENCE` until a configured worker/executor is injected.
- The in-memory adapter is not a production durability guarantee; restart loses local conversations/jobs/feedback.
- Citation source bytes/previews require a registered source artifact/provider; absent or revoked artifacts fail closed.
- Disposable PostgreSQL migration/knowledge tests were not run because `DB001_DATABASE_URL` is unset.
- No cloud/API keys, production provider, load test, or frontend E2E was used.

No commit or push was performed.
