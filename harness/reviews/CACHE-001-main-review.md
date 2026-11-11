# CACHE-001 — Main Agent review

## Decision

`ACCEPTED — SCOPED CACHE AND MEMORY BOUNDARY`

CACHE-001 is accepted for the provider-neutral Phase 4 boundary. The adapters
are intentionally non-authoritative, but their keys, expiry and invalidation
semantics fail closed before later PostgreSQL/Redis/outbox integration.

## Accepted behavior

- Cache keys carry tenant, principal, policy epoch, document-version scope,
  entitlement, corpus epoch and index generation; query/model/prompt inputs are
  hashed rather than placed in clear text.
- Reads require an exact current scope and stale/revoked writes are rejected.
- ACL, principal-revocation, policy, document-version and deletion invalidation
  hooks are present.
- A document-version event invalidates both the exact version and broad corpus
  cache entries, while leaving unrelated version entries intact.
- Conversation memory is bounded, retention-aware, deletion-aware and redacts
  message bodies from representations and invalidation metadata.
- PostgreSQL remains the durable authority; Redis is only a future cache
  adapter, never the sole checkpoint store.

## Evidence

- CACHE implementation tests: `12 passed`.
- CACHE QA matrix: `40 passed` (`10` behavior/component, `10`
  contract/integration, `10` security/adversarial, `10` E2E/operational).
- Combined CACHE implementation + QA: `52 passed`.
- Backend regression: `250 passed, 2 skipped`; the skips are the existing
  PostgreSQL smoke tests requiring `DB001_DATABASE_URL`.
- `compileall` and `git diff --check` passed.
- Graphify query and post-change refresh completed.

## Scope boundary

Durable PostgreSQL repositories, Redis transport, ordered outbox delivery,
policy/PDP caller wiring and CHAT integration remain downstream work. The
in-memory adapters must not be promoted as production authority without the
durable integration and revocation-lag tests.
