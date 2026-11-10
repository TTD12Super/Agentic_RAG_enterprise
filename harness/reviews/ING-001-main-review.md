# Main Agent Review: ING-001

## Decision

ACCEPTED for the provider-neutral ingestion lifecycle boundary.

## Evidence

- Independent QA: 40/40 cases passed after revalidation.
- ING implementation and integration tests: 51 passed.
- Full backend/integration suite: 160 passed, 2 skipped because `DB001_DATABASE_URL` was not configured.
- Compile and harness validation passed.
- Graphify refreshed after the lifecycle and error-boundary fix.

## Scope decision

The task delivers quarantine, scan/review gates, staged index publication, bounded retry, revocation/delete isolation, maintenance recovery and fail-closed derived-index cleanup using deterministic in-memory boundaries.

## Deferred

Durable PostgreSQL repository/outbox, object storage, parser/OCR, Qdrant, queue and cloud/provider adapters remain downstream work and require approved runtime configuration.
