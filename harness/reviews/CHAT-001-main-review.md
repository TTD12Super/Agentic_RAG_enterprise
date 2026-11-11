# CHAT-001 — Main Agent review

## Decision

`ACCEPTED — CHAT/JOB/CONVERSATION BOUNDARY`

CHAT-001 is accepted for the Phase 4 provider-neutral backend boundary. The
API exposes versioned conversation, query-job, completion, citation
preview/download and feedback flows while reusing the existing policy,
orchestration, cache/memory and audit boundaries.

## Accepted behavior

- Authenticated conversations are owner-only; anonymous sessions use a
  server-issued token and cannot cross-read another session.
- Query admission requires idempotency, preserves request/job/attempt scope,
  returns safe timeout/maintenance states and rechecks policy scope before
  delivering completion.
- Checkpoints are metadata-only and do not store raw prompts, answers, source
  text, conversation bodies or secrets.
- Citation preview and source download perform separate fresh authorization
  checks against the exact citation version and current document state.
- Feedback is actor/answer scoped, idempotent and excludes comments from the
  API response and audit metadata.

## Evidence

- CHAT implementation tests: `8 passed`.
- CHAT QA matrix: `40 passed` (`10` behavior/component, `10`
  contract/integration, `10` security/adversarial, `10` E2E/operational).
- Combined CHAT focused suite: `48 passed`.
- Full regression including ORCH, CACHE and CHAT QA: `619 passed, 2 skipped`.
- The two skips are the existing PostgreSQL smoke tests requiring
  `DB001_DATABASE_URL`.
- `compileall`, `git diff --check` and harness validation passed.
- Graphify query and post-change refresh completed.

## Scope boundary

The default adapter is process-local and the default executor safely returns
insufficient evidence until a real worker/orchestrator/provider is injected.
Durable PostgreSQL repositories, queue transport, live provider execution,
frontend E2E, cloud deployment and production load tests remain deferred.
