# Enterprise Agentic RAG — Shared Contract Baseline v1.0

**Status:** `APPROVED` for MVP implementation on 2026-11-10
**Authority:** Main Agent acting under Project Owner delegation recorded in the project conversation on 2026-11-10
**Scope:** public API, worker messages, authorization scopes, retrieval/citation, cache, jobs, ingestion, tools and privacy-safe events

This document is the normative compatibility profile for MVP implementation. The focused contract documents remain the domain reference; when an example conflicts with this file, this v1.0 profile wins until a versioned change is approved.

## 1. Versioning and envelope

Public APIs use REST/HTTP JSON under `/api/v1`. Internal commands, results, events and checkpoints use JSON Schema/Pydantic payloads with the following envelope:

```json
{
  "contract_name": "enterprise-agentic-rag",
  "schema_version": "1.0",
  "message_id": "msg-uuid",
  "request_id": "req-uuid",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "tenant_id": "tenant-a",
  "producer": "core-api",
  "issued_at": "2026-11-10T10:00:00Z",
  "expires_at": "2026-11-10T10:05:00Z",
  "idempotency_key": "idem-uuid",
  "attempt_id": "attempt-uuid",
  "payload": {}
}
```

Rules:

- `message_id`, `request_id`, `producer`, `issued_at`, `schema_version` and `payload` are required; `tenant_id` is required for tenant-scoped messages.
- Timestamps are UTC RFC 3339 with `Z`. `expires_at` is required for worker commands, scopes and signed citation references.
- A major version change is breaking. Within v1, fields may be added as optional; required fields cannot be removed or change meaning.
- Consumers ignore unknown optional fields and reject unknown required semantics. Unsupported `schema_version` returns `SCHEMA_UNSUPPORTED` and is not retried indefinitely.
- Public HTTP error responses use `application/problem+json`-like JSON: `code`, safe `message`, `request_id`, optional redacted `details`, and `retryable`. No stack traces, secrets, source text or private paths.
- `traceparent` is propagated unchanged as the parent context and a new child span is created at each service boundary. `request_id` is the application correlation identifier; it is not a substitute for `traceparent`.
- `policy_epoch` is the authoritative numeric freshness value in v1. A legacy/display `policy_version` may be logged as metadata but must not replace `policy_epoch` in authorization, cache or replay checks.

Compatibility is additive within major version. A contract change that changes authorization, privacy, state transitions, required fields, provider egress, or data meaning requires a new version and owner approval.

## 2. Identity, authorization and worker trust

### 2.1 Principal and policy

The Core creates `AuthenticatedPrincipal` only from validated authentication. Browser, LLM and retrieved text cannot supply roles, tenant, departments or scopes.

Authorization evaluation is fail-closed and follows this order:

1. Validate principal, session and tenant binding.
2. Validate resource classification and current lifecycle state.
3. Apply RBAC and department membership.
4. Apply document-level ACL.
5. Apply explicit deny; any matching deny overrides every allow.
6. Require the current ACTIVE document version and current policy epoch.

`chairman` is a broad read allow only; it does not bypass explicit deny or grant upload, delete, approval, website-management or developer actions. `system_admin` cannot read another user's conversation body, including through audit, support, incident, export, cache or trace views. `website_manager` has website-management powers but no code/system powers. Anonymous access is PUBLIC-only.

### 2.2 AuthorizedScope

`AuthorizedScope` is a server-issued opaque reference stored in the authoritative policy store. It is never accepted from the browser or LLM as an arbitrary document list.

```json
{
  "scope_ref": "scope-random-256-bit",
  "audience": "retrieval-worker",
  "principal_id": "u-123",
  "tenant_id": "tenant-a",
  "policy_epoch": 42,
  "classification_max": "INTERNAL",
  "document_version_filter": "server-bound-query",
  "issued_at": "2026-11-10T10:00:00Z",
  "expires_at": "2026-11-10T10:05:00Z",
  "revoked_at": null
}
```

The Core rechecks scope, tenant, policy epoch, version state and ACL at admission, each retrieval branch, parent expansion, citation and source download. Missing, expired, revoked or mismatched scope returns `DENY` without revealing resource existence.

### 2.3 Worker authentication

MVP workers use TLS plus short-lived asymmetric-signed service JWTs. The token must include `iss`, `sub`, `aud`, `iat`, `exp`, `jti`, `tenant_id` where applicable, `job_id`, `attempt_id`, `policy_epoch` and the permitted document/version scope. Resource services validate signature, issuer, audience, expiry, job/tenant binding and one-time `jti` replay state. Stale, revoked, cross-tenant or replayed commands/results are rejected and never treated as successful.

Production hardening may add mTLS or sender-constrained tokens without changing the v1 authorization semantics. No browser token is accepted as worker identity.

The Core persists worker replay state and lease fencing in the authoritative store. A worker command/result is valid only when its `worker_jti`, `job_id`, `attempt_id`, `tenant_id`, `document_version_id` where applicable, `policy_epoch` and monotonic `fencing_token` match the current record. A stale fencing token cannot write completion, publication, cache invalidation or maintenance release.

Signing keys are published with a `kid` through an authenticated key-set endpoint. Rotation overlaps old/new keys for the maximum token lifetime; an unknown, revoked or expired `kid` fails closed. Replay records retain a hash of `jti` until token expiry plus clock-skew allowance, not the raw token.

The MVP service channel requires TLS 1.3 where supported (TLS 1.2 only with approved cipher policy), certificate identity verification, asymmetric `RS256` or stronger approved algorithms, and a server clock-skew budget of 30 seconds. JWKS/trust-material outage fails closed for new worker commands and results; readiness must not report healthy without valid trust material. Rotation overlap is at least the maximum token lifetime plus the 30-second skew budget.

## 3. Idempotency and correlation

- Mutating POST commands require an opaque high-entropy idempotency key. GET and DELETE rely on their resource semantics and do not use idempotency keys.
- The server stores the canonical request fingerprint and final safe response for 24 hours. Reuse with a different fingerprint returns `IDEMPOTENCY_KEY_REUSED`; reuse with the same fingerprint returns the original result.
- Admission, upload, review, publish, chat submission, worker completion and checkpoint writes are unique by the relevant `tenant_id + resource/job_id + operation + idempotency_key` tuple.
- Idempotency records are durable PostgreSQL records, not process memory or best-effort cache. Tool calls additionally use `tool_call_id` plus a canonical argument fingerprint; a repeated call returns the recorded safe result and a different fingerprint is rejected.
- `X-Request-ID` is accepted only as a bounded correlation value; the server generates one when absent and never trusts it as authorization.
- `traceparent` follows W3C Trace Context. Traces, logs and events contain metadata only; payload bodies, prompts, answers, source text, secrets and tokens are excluded by default.

## 4. Retrieval and citations

Retrieval is authorized before dense and lexical search, after fusion/reranking, before parent expansion, and again before returning content. Qdrant/index metadata is never the policy authority.

Citation locations are version-bound and carry an immutable evidence snapshot hash. The locator is a discriminated object, not a free-form page/span pair:

```json
{"kind":"PDF","page":4,"source_span":{"start":101,"end":412}}
{"kind":"DOCX","heading":"Security policy","paragraph":17}
{"kind":"XLSX","sheet":"Revenue","cell_range":"B4:F12"}
```

- PDF: page number plus UTF-8 character span within the normalized page text.
- DOCX: stable heading plus paragraph number in the normalized document.
- XLSX: workbook sheet name plus bounded A1 cell range.

Citation references include `tenant_id`, immutable `document_version_id`, source locator, evidence snapshot hash, `policy_epoch`, audience and expiry. The server performs a fresh `document:read` check for preview and a separate `source:download` check for original files. A revoked, superseded or nonexistent source returns a safe unavailable response and never substitutes a newer version.

If parent expansion is denied or stale, the denied parent is omitted and never used for ranking, context or citation. An independently authorized child may remain as evidence; the denial must not broaden or silently alter the child's authorization decision.

## 5. Cache and revocation

Authoritative data remains in PostgreSQL and private object storage; Qdrant is an index projection; Redis is optional cache/rate-limit state and never the only durable checkpoint.

Retrieval/answer cache keys include tenant, principal entitlement fingerprint, `policy_epoch`, `corpus_epoch`, `index_generation`, query hash, model configuration and prompt version. Publication, ACL/role revocation, classification changes, deletion and policy changes advance the relevant epoch in the same durable transaction as the source-of-truth change and enqueue an ordered outbox invalidation event.

Readers compare all epochs before serving. If an epoch is stale, missing or invalidation confirmation is unavailable, restricted content is a cache miss/fail-closed path. Negative cache entries use the same epochs and a short TTL. The outbox records sequence, attempts and acknowledgement; an unacknowledged invalidation cannot be treated as complete. Provider prompt-prefix caching is isolated from answer authorization and never proves permission.

Each outbox event has a unique `(tenant_id, aggregate_type, aggregate_id, event_type, sequence_no)` key. A dispatcher claims rows with a lease, retries with bounded backoff, deduplicates by that key, and moves poison events to a dead-letter state with an audit event. Each consumer stores an applied sequence/watermark per tenant and aggregate; out-of-order events wait or trigger reconciliation. A consumer freshness timeout of 60 seconds is measurable; beyond it, restricted cache/source reads fail closed and emit stale-read/consumer-lag metrics.

The minimum durable records for this protocol are `IDEMPOTENCY_KEYS`, `AUTHORIZED_SCOPES`, `WORKER_REPLAY_NONCES`, `JOB_LEASES`, `INDEX_PUBLICATIONS`, `REVOCATION_TOMBSTONES` and `OUTBOX_EVENTS`. Each record is tenant-bound where applicable and has a unique operation/resource key.

Replay consume is one atomic compare-and-insert operation: the first valid `jti` changes from unseen to consumed; a duplicate returns `REPLAY_DETECTED`; an unavailable replay store returns `AUTH_UNAVAILABLE` and the command fails closed. Replay entries expire only after token expiry plus the clock-skew budget.

## 6. Jobs, maintenance and recovery

`job_state` is one of `QUEUED`, `RUNNING`, `PAUSED`, `RETRY_SCHEDULED`, `COMPLETED`, `FAILED`, `CANCELLED`. Maintenance is a system mode, not a job state. A job is `COMPLETED` only after its answer/result and audit outcome are durably persisted.

Normative rules:

- Queue delivery is at-least-once; job/attempt IDs and durable idempotency make completion safe under redelivery.
- A worker lease has a heartbeat, owner, `lease_id`, monotonic fencing token and expiry. Lease expiry creates at most one retryable attempt through a compare-and-swap state transition.
- Retry is bounded: unchanged ingestion versions have at most three attempts; provider retries use bounded exponential backoff and approved fallback only.
- `PAUSED` is entered only by maintenance, explicit cancellation or an approved operational pause. `MAINTENANCE_ACTIVE` is a separate system mode/UI status, never a `job_state`. Resume requires a valid checkpoint plus fresh principal, tenant, ACL, policy epoch and document-version checks.
- Duplicate completion, stale checkpoint, unknown transition, expired scope or failed policy check is rejected without exposing content. Checkpoints contain stage, IDs, hashes, policy/version epochs and redacted metadata only; they never contain conversation bodies, raw prompts, answers, source text or secrets.
- Upload maintenance blocks new chat admission with `503 MAINTENANCE_ACTIVE`; existing jobs checkpoint at safe boundaries. An in-flight external model call is not assumed to pause mid-token.
- Approval expiry is 30 minutes; the maintenance watchdog is 60 minutes and never auto-approves. Failure cleanup restores the previous ACTIVE version and releases maintenance safely.

## 7. Document lifecycle and review actors

The lifecycle remains `UPLOADED → QUARANTINED → REVIEW_1_APPROVED → PROCESSING → PROCESS_VALIDATED → PENDING_REVIEW_2 → ACTIVE`. The same administrator may perform both reviews in MVP, but each review is a separate authenticated, authorized, timestamped, idempotent event with an independent decision. No single action auto-approves both stages, and permanent deletion still requires retention/legal-hold checks.

Publication uses a durable two-step visibility protocol because PostgreSQL and index stores are not one transaction: (1) PostgreSQL records a `publication_id`, expected checksum, `document_version_id`, new `corpus_epoch`, `index_generation` and an outbox intent while retaining the former ACTIVE version; (2) index projections are built and acknowledged with the same publication/fencing token, then PostgreSQL atomically flips the current pointer and visibility epochs. Until both steps verify, retrieval continues to use the former ACTIVE version. Any mismatch, timeout or stale writer leaves the former ACTIVE version served and emits a tombstone/repair event. Failed/rejected/cancelled versions never become searchable and never replace the former ACTIVE version.

Every ingestion attempt is bound to `document_version_id`, `content_sha256`, parser profile, `attempt_id` and fencing token. A checksum/version mismatch is a hard failure; ACL metadata is copied into each index projection and rechecked against the Core.

The ingestion retry matrix is normative: invalid format/malware/limit is terminal without retry; transient storage/quarantine/parsing/OCR/chunking/embedding/index work may retry up to three attempts for the unchanged checksum; review decisions are never auto-retried; publication and cleanup use reconciliation/outbox retry rather than blind duplicate publication. The index manifest records expected chunk count, chunk-id digest, ACL digest, checksum, version and `index_generation`; publication is blocked until the manifest matches. A maintenance lease has a durable owner, `lease_id`, fencing token and expiry. Revocation uses a deduplicated tombstone `{revocation_id, tenant_id, resource_type, resource_id, version_id, epoch, sequence, reason, issued_at}`; replay applies tombstones in sequence before any read. A duplicate SHA-256 for the same document/version is idempotent; the same bytes uploaded as a new document may reuse an immutable derived projection only as an optimization and still receives independent ACL/lifecycle checks.

ACL propagation is a publication gate: every dense, lexical, parent and citation derivative must report the same version, checksum, `policy_epoch`, ACL digest and expected-count manifest. A missing or mismatched derivative fails publication and leaves the former ACTIVE version serving. Maintenance release uses compare-and-swap on the durable `maintenance_window_id + lease_id + fencing_token`; a stale watchdog cannot release a newer window.

## 8. Tools and privacy-safe events

The v1 tool manifest is exactly `search_documents`, `read_authorized_chunk` and `get_document_metadata`. Each entry is a versioned record with tool name, input/output schema ID, read-only action, maximum argument/output bytes and timeout class. Every call receives a server-resolved principal and `authorized_scope_ref`; LLM arguments cannot grant access. Each call has a server deadline, a bounded output size, a unique `tool_call_id`, an argument fingerprint and a result state. The loop budget is per job, not per round: at most two retrieval rounds total, four subqueries total and eight tool calls total. A retry uses the same `tool_call_id` and fingerprint; a changed call is rejected. Upload, edit, delete, permission-change, SQL, shell, HTTP-fetch and email tools are absent.

Audit/event payloads allow only identifiers, action, decision, policy/version epochs, timestamps, bounded error codes, request/trace IDs and redacted operational metadata. They must not contain conversation bodies, raw prompts/answers, source text, secrets, tokens or unrestricted PII. Conversation body storage and query paths are separate from metadata/audit paths; database roles and repository queries for `system_admin`, website manager, support and incident views cannot select another user's body. Any privileged investigation is time-limited, separately authorized and itself audited.

Every workflow also has `workflow_deadline_at` and per-node deadlines. A node cannot extend the workflow deadline, and timeout returns a safe partial/insufficient-evidence result or `TIMEOUT` without bypassing authorization. Output safety checks run before persistence and reject unsupported claims, unauthorized citations, raw source leakage and tool-derived instructions.

Workflow checkpoints are metadata only: stage, graph revision, job/attempt IDs, tool-call IDs, hashes, citation IDs, policy/version epochs and safe error state. They never store raw questions, prompts, evidence text, tool output, draft answers, source quotes or secrets. Checkpoints are encrypted, readable only by the job owner/authorized worker, and purged within 7 days after terminal completion or cancellation.

The tool manifest is machine-checkable:

```json
{"manifest_version":"1.0","tools":[
  {"name":"search_documents","input_schema":"search.v1","output_schema":"evidence-list.v1","action":"READ","max_input_bytes":16000,"max_output_bytes":65536,"timeout_ms":10000},
  {"name":"read_authorized_chunk","input_schema":"chunk-read.v1","output_schema":"evidence.v1","action":"READ","max_input_bytes":4096,"max_output_bytes":65536,"timeout_ms":5000},
  {"name":"get_document_metadata","input_schema":"document-metadata.v1","output_schema":"document-metadata.v1","action":"READ","max_input_bytes":4096,"max_output_bytes":16384,"timeout_ms":3000}
]}
```

Tool `TIMEOUT`/`UNAVAILABLE` consumes the call budget and may retry once with the same `tool_call_id`; a second failure returns a safe insufficient-evidence result and cannot trigger an unbounded replan. Tool calls bind `job_id` and `attempt_id`; late results from a prior graph attempt are recorded as stale and cannot mutate current state.

Trusted orchestration fields (`principal`, `authorized_scope_ref`, `job_id`, `attempt_id`, budgets and tool manifest) are separate from untrusted fields (`query`, retrieved evidence and tool output). Malformed planner/router output is rejected as `INVALID_ARGUMENTS` and does not select a new tool. Before answer persistence, a safety gate checks structured schema, evidence grounding, authorization, secret/PII leakage and unsupported claims; failure returns `SAFE_OUTPUT_BLOCKED` without persisting or delivering raw output.

## 9. API additions and UI state

- `POST /api/v1/access-requests` creates an employee access request with server-derived identity or an anonymous session reference; it never grants access. An administrator approves/provisions through a separate idempotent endpoint and audit event.
- `POST /api/v1/documents/{document_id}/versions/{version_id}/approve` and `/publish` always identify the immutable version explicitly; document-level aliases cannot select a newer version implicitly.
- `POST /api/v1/answers/{answer_id}/feedback` accepts one feedback record per authenticated user/answer and one per anonymous session/answer. A repeated identical submission returns the original result; a changed submission returns `FEEDBACK_ALREADY_RECORDED`.
- MVP has no SSE/WebSocket token streaming. The UI polls the durable job endpoint and displays `MAINTENANCE_ACTIVE` separately from a job's `PAUSED` state.
- UI role labels use the canonical values `system_admin`, `website_manager`, `employee` and `chairman`; display labels may be localized but cannot change authorization identifiers.
- The exports under `docs/design` are visual references, not an API authority. Legacy states/labels in those references are superseded for implementation by this section: use `MAINTENANCE_ACTIVE`, canonical role identifiers and durable-job polling.
- The UI must handle `429` with bounded `Retry-After` seconds and `503 MAINTENANCE_ACTIVE` separately. Cursor tokens are opaque, signed/server-stored, bound to tenant, principal, filter hash and expiry; a mismatch returns `CURSOR_INVALID` without existence leakage. v1 error codes include `SCHEMA_UNSUPPORTED`, `AUTH_UNAVAILABLE`, `SCOPE_STALE`, `REPLAY_DETECTED`, `IDEMPOTENCY_KEY_REUSED`, `CURSOR_INVALID`, `MAINTENANCE_ACTIVE`, `RATE_LIMITED`, `TIMEOUT`, `SAFE_OUTPUT_BLOCKED` and `NOT_FOUND_OR_FORBIDDEN`.

## 10. Required test evidence

Before implementation is marked integrated, the Test Agent must provide four families with at least 10 materially different cases each: behavior/component, contract/integration, security/adversarial and E2E/operational. The contract review package contains the initial 40-case proposal; implementation tasks must execute the applicable cases and record commands/results.

## 11. Approval and unresolved decisions

This v1 baseline resolves the contract decisions delegated to the Main Agent on 2026-11-10: worker trust/replay, ACL/scope semantics, same-admin review actor, cache epochs, durable job state, retention/lifecycle safeguards and current repository/runtime boundary. Cloud/provider, model, alert-recipient and benchmark/release decisions remain pending and block only their affected tasks.
