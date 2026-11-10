# CITATION-SCHEMA-001 — Main Agent review

## Decision

`ACCEPTED — COMPLETE FOR CURRENT RUNTIME`

Citation output now carries tenant scope, immutable document/version/chunk
identity, request policy epoch, typed PDF/DOCX/XLSX locator, evidence snapshot
hash, audience and timezone-aware expiry. Legacy PDF accessors remain for
compatibility, while malformed, stale, revoked, cross-tenant and expired
references fail closed before model context or answer delivery.

## Evidence

- Focused citation, parent and end-to-end integration: `30 passed`.
- Required QA matrix: `40 passed`.
- Full regression including QA: `490 passed, 2 skipped`.
- `compileall`, `git diff --check` and harness validation: PASS.
- Contract examples and baseline locator definitions were updated to match the
  discriminated runtime schema.

## Scope boundary

The accepted expiry default is a five-minute answer-pipeline reference
window; explicit source expiry is respected and expired references are
rejected. Persistence/API signed citation storage and live adapter validation
remain outside this local runtime blocker and are covered by their owning
tasks. The project-wide production quality gate is still deferred.
