# Main Agent Review: KNOW-001

## Decision

ACCEPTED for the provider-neutral knowledge metadata boundary.

## Evidence

- Independent QA: 40/40 cases passed after revalidation.
- Backend suite: 96 passed, 2 skipped because `DB001_DATABASE_URL` was not configured.
- Existing DB-001 migration boundary was verified; no migration was added.
- Harness validator and compile checks passed.
- Graphify refreshed after the model invariant fixes.

## Scope decision

The task delivers immutable document/version/chunk metadata, tenant/version scope checks, ACL inheritance and a derived Qdrant payload. PostgreSQL remains authoritative and authorization remains in the PDP/PEP.

## Deferred

Live PostgreSQL, Qdrant, object storage and ingestion-worker integration belong to downstream ingestion work and require their approved runtime configuration.
