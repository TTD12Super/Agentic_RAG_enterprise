# DASH-API-001 — Main Agent review

## Decision

`ACCEPTED — ROLE-LIMITED DASHBOARD AND FEEDBACK REVIEW`

DASH-API-001 is accepted and completes the Phase 4 task set. The management
API reuses the existing PEP/admin boundary and exposes only bounded,
privacy-safe aggregates and feedback projections.

## Accepted behavior

- `system_admin` and `website_manager` may read dashboard and feedback review;
  `chairman`, `employee` and anonymous callers are denied without management
  data leakage.
- Dashboard metrics are tenant-scoped and carry value, unit, status,
  availability, estimate flag, provenance and measurement period.
- Provider-dependent latency, cost, cache and evaluation metrics explicitly
  return `UNAVAILABLE`; no fabricated production values are reported.
- Feedback records, idempotency and review are tenant-bound. Review returns
  only opaque feedback/answer IDs, rating and timestamp; it excludes comments,
  actor identity, conversation bodies and source text.
- Pagination and rating filters are bounded and allowlisted; policy outages
  fail closed with safe `AUTH_UNAVAILABLE` responses.

## Evidence

- DASH implementation tests: `8 passed`.
- DASH QA matrix: `40 passed` (`10` behavior/component, `10`
  contract/integration, `10` security/adversarial, `10` E2E/operational).
- Dashboard/admin/chat focused regression: `48 passed`.
- Full Phase 4 regression including all prior suites and QA: `667 passed,
  2 skipped`.
- The two skips are the existing PostgreSQL smoke tests requiring
  `DB001_DATABASE_URL`.
- `compileall`, `git diff --check` and harness validation passed.
- Graphify query and post-change refresh completed.

## Scope boundary

The dashboard currently reads provider-neutral local adapters. Durable
PostgreSQL feedback/metrics, live provider telemetry, frontend E2E, load
testing, cloud deployment and production release evidence remain downstream.
