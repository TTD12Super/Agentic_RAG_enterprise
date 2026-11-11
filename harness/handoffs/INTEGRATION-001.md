# INTEGRATION-001 — Frontend, Backend and local RAG connection

## Outcome

The chat path is connected end to end for local development:

```text
React composer
  -> Vite /api proxy
  -> FastAPI conversation + durable query-job endpoints
  -> LocalRagExecutor
  -> ingestion lifecycle + permission-aware hybrid retrieval
  -> answer/citation verification
  -> query-job ANSWERED payload
  -> React answer and citation display
```

The local executor uses one synthetic PUBLIC PDF policy fixture. It is intentionally
not a production provider or persistence implementation.

## Changed surfaces

- `backend/app/rag/runtime.py`: local runtime adapter that publishes a fixture through
  the existing ingestion lifecycle, indexes it in the existing dense/BM25 baseline,
  and calls the existing direct answer/citation pipeline.
- `backend/app/core/chat.py`: optional executor context binding so the executor receives
  the trusted principal and policy epoch without putting identity data in the query.
- `backend/app/api/chat.py`: development default now uses `LocalRagExecutor`.
- `frontend/src/api/client.ts`: conversation creation, message submission and bounded
  query-job polling.
- `frontend/src/App.tsx`: chat composer sends real queries and renders returned answer
  text/status/citations.
- `frontend/vite.config.ts`: local `/api` proxy to FastAPI.

## Evidence

Executed successfully:

```text
/tmp/know-venv/bin/python -m pytest backend/tests/test_runtime_integration.py backend/tests/test_dense_retrieval.py backend/tests/test_hybrid_retrieval.py backend/tests/test_chat_api.py tests/integration/test_chat_api.py -q
18 passed

cd frontend
npm run lint
npm test -- --run
npm run build
11 Vitest tests passed; lint, typecheck and Vite build passed
```

Vite proxy smoke test against a running FastAPI and Vite dev server returned:

```text
proxy e2e 200 COMPLETED ANSWERED 1
```

## Current limitations to fix next

1. `LocalRagExecutor` is a development adapter with one synthetic PUBLIC fixture;
   it must be replaced/configured with the approved LLM provider and real document
   repositories before production.
2. Chat state, ingestion state and indexes are in memory; PostgreSQL, object storage,
   Qdrant and a durable worker are not wired into this runtime path yet.
3. The default chat path uses `DirectAnswerPipeline`; the bounded LangGraph/Tool
   Gateway exists but is not the default HTTP executor yet.
4. Only the chat screen is API-connected. Dashboard, documents, review, users and
   audit screens still use deterministic fixtures.
5. The FE client currently assumes same-origin cookie/session handling and does not
   yet expose login/token refresh, citation preview/download or feedback actions.
6. Real provider API keys, cloud deployment, email verification and production
   monitoring remain configuration/operations work; no secrets were added.
7. The current citation payload exposes document/version/locator identifiers but
   not a document title or calibrated numeric confidence; the FE therefore shows
   the document ID and `VERIFIED` until the approved citation schema is extended.

No commit or push was performed.

## Addendum — FE–BE integration pass

The integration pass after the initial chat wiring removed the deterministic
business fixtures from the frontend. The frontend now calls the backend for
authentication, chat, dashboard, users, departments, documents, approvals,
audit events, citation preview and feedback. Missing measurements are rendered
as unavailable rather than fabricated.

The backend now exposes the document catalog, approval queue and metadata-only
audit endpoints. When `BACKEND_DATABASE_URL` is configured, conversations,
messages, query jobs, checkpoints, anonymous sessions, idempotency records and
audit events use PostgreSQL; identity and document lifecycle stores remain
in-memory until their durable credential and lifecycle contracts are completed.

Validation: backend `270 passed, 2 skipped`; frontend typecheck, lint, 9 tests
and production build passed. A live Neon smoke test created a conversation,
submitted a query, received `COMPLETED/ANSWERED`, and read conversation history
with HTTP 200.

Current production limitations: real file upload/object storage, durable
identity/document lifecycle, durable feedback, provider-backed RAG, Qdrant,
and pagination controls remain downstream work. The anonymous production
cookie is configured for cross-origin HTTPS requests from the Vercel frontend.
