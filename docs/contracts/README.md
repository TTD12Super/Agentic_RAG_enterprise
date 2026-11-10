# Contracts — shared boundaries (contract-first)

**Current baseline:** [`v1-baseline.md`](v1-baseline.md) is the approved MVP compatibility profile. Do not start incompatible implementations. Focused contract documents remain domain references and must follow v1.0 when examples differ.

## Required reading by team
- `identity-and-policy.md`: principal and authorization decision.
- `chat-and-jobs.md`: proposed chat, conversation and durable query-job API boundary.
- `admin-management.md`: proposed Backend-owned administration API boundary.
- `document.md`: source, version, ACL, chunk, lifecycle.
- `ingestion.md`: upload/ingestion job.
- `retrieval.md`: secure search and evidence.
- `agent-tools.md`: tool registry, authorization and execution.
- `answer-and-citation.md`: answer/source provenance.
- `cache-and-memory.md`: invalidation and isolation.
- `events-and-audit.md`: correlation and privacy-safe events.
- `CHANGE-PROCESS.md`: protocol for breaking changes.

## Global invariants
- Required IDs include `tenant_id` and immutable `document_version_id` when related to a document.
- Every tool call carries server-verified principal and trace ID; never accepts role claims from user input.
- `ALLOW` and `DENY` are backend decisions; search returns only authorized, ACTIVE chunk IDs.
- All cross-module outputs include structured error handling, no raw stack trace.
- Contract schemas are reviewed before code is parallelized. A mock may be used only for local testing.


## Contract Lifecycle

Contracts follow these states:

DRAFT → REVIEW → APPROVED → IMPLEMENTING → VERIFIED → DEPRECATED

`REJECTED` is a terminal outcome from review; a rejected contract must return to `DRAFT` as a new revision before review.

Only versions explicitly approved by the Project Owner may be used as shared integration boundaries. The same approved version remains usable while marked `IMPLEMENTING` or `VERIFIED`; `DEPRECATED` requires a documented migration and is not a new integration target.

Breaking changes require explicit Owner approval.

- Missing, invalid, or unavailable authorization
  decisions must result in DENY.

- Retrieval and citation responses must reference
  approved, ACTIVE, authorized document versions.
  
- Revoked or superseded versions must not be served.

## Owner-provided contract baseline

The shared proposal baseline is [`../requirements/owner-decision-baseline.md`](../requirements/owner-decision-baseline.md). Contract implementations must use:

- REST/HTTP JSON with OpenAPI 3.1 for public APIs under `/api/v1`.
- JSON Schema/Pydantic worker payloads carrying `schema_version`.
- UTC/RFC 3339 timestamps, `X-Request-ID`, W3C `traceparent` and idempotency keys for upload/retry/mutation operations.
- A safe Problem Details-like error envelope: code, message, request ID and redacted details.
- Cursor pagination with default 20 and maximum 100.
- Job states `QUEUED`, `RUNNING`, `PAUSED`, `RETRY_SCHEDULED`, `COMPLETED`, `FAILED`, `CANCELLED`; `MAINTENANCE` is a system mode.

These inputs are accepted for the v1.0 MVP contract baseline on 2026-11-10. Provider, cloud, model and release decisions remain separately pending where noted in the decision register.
