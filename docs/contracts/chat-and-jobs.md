# Chat, conversation and query-job contract — DRAFT

This is a proposed shared boundary for `CONTRACT-001` review and explicit Project Owner approval; it is not an implemented API. Endpoint names and schemas require compatibility and security review before implementation.

## Proposed API surface

- `POST /api/v1/conversations` creates a conversation bound to the authenticated principal or a server-issued anonymous session.
- `POST /api/v1/conversations/{conversation_id}/messages` submits a question with an idempotency key. Successful asynchronous admission returns `202` with an opaque job identifier and request correlation ID.
- `GET /api/v1/conversations/{conversation_id}` returns only the current principal's own permitted history or the bound anonymous session's temporary history.
- `GET /api/v1/query-jobs/{job_id}` returns an authorized caller's job state, safe progress and completed answer/citation references. Queue position is an estimate and can change. There is no token streaming in MVP.

Tenant, role, scope and session are resolved and verified by the server, never granted by a client or model claim. Every conversation and job operation enforces ownership, tenant and current authorization. A changed/revoked identity, policy or source version fails closed before retrieval, resume, result delivery and citation access.

The chat integration also needs authorized feedback submission and citation preview/download. Exact endpoint schemas, feedback retention and anonymous/repeated feedback policy remain draft: escalate unresolved policy to the Project Owner before implementing dependent behavior. Reviewers must not infer access to another user's conversation body from feedback or administrative access.

## Job and failure semantics

Shared `job_state` values are `QUEUED`, `RUNNING`, `PAUSED`, `RETRY_SCHEDULED`, `COMPLETED`, `FAILED` and `CANCELLED`. A processing stage or pause-request flag is separate from `job_state`. A job is `COMPLETED` only when its final result is durably persisted; processing and provider failures use safe error codes and do not expose sensitive contents.

New work in maintenance returns `503 MAINTENANCE_ACTIVE`; saturation returns `503` with `Retry-After`; rate limits return `429`. Existing jobs use durable checkpoints and recheck authorization before resuming. Ordinary failed jobs require user resubmission. Responses use the approved error envelope and request correlation conventions in `README.md`.

## Required review and tests

Backend, Frontend, Orchestration and Security review ownership, state transitions, queue admission, idempotency, anonymous-session expiry, permissions and error schemas. Test another user's conversation/job denial, tenant isolation, revoked access, replay, maintenance, queue saturation, partial/insufficient-evidence results and citation reauthorization against real integrated components. Synthetic fixtures do not authorize production data use.
