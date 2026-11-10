# Handoff — CONTRACT-001 / Security Agent

- Task ID: `CONTRACT-001`
- Agent owner: Security Agent
- Status: `READY_FOR_INTEGRATION`
- Contract version(s) used: No concrete approved implementation version exists. Reviewed the contract proposals and the owner-provided baseline requiring OpenAPI 3.1, JSON Schema/Pydantic worker payloads with `schema_version`, UTC/RFC 3339 timestamps, `X-Request-ID`, W3C `traceparent`, idempotency keys and safe Problem Details-like errors.
- Upstream dependencies checked: `ARCH-001` is recorded `DONE`; architecture overview and ADR-0001 through ADR-0005 were read. `CONTRACT-001` remains a proposal review; no dependent implementation is authorized by this handoff.
- Changed files: `harness/handoffs/CONTRACT-001.md` only.
- New/updated tests: None. This handoff contains a 40-case coverage proposal only, as required by task scope.

## Review conclusion

The shared contracts have a sound security direction: backend-owned authorization, default deny, explicit deny precedence, tenant and immutable version identifiers, rechecks at retrieval/citation/cache/resume boundaries, read-only MVP tools, two-stage document publication and privacy restrictions for conversation bodies.

The contracts are not yet safe to freeze as an implementation boundary. Several material details are underspecified, and one approval-state conflict must be resolved. The Main Agent may use this package to prepare a versioned contract update, but must not mark the contracts `APPROVED` until the affected-agent compatibility review and explicit Project Owner approval are recorded.

## Findings by severity

### BLOCKER

#### SEC-CONTRACT-001 — No concrete compatibility/versioning profile

The baseline requires `schema_version`, but the contracts do not define a contract identifier, version negotiation, compatibility rules, required/optional field evolution, unknown-field handling, deprecation window, content type, or whether public API versioning and worker payload versioning are independent. Examples also omit common envelope fields inconsistently. A consumer could accept a structurally valid but semantically incompatible message.

`ESCALATE: DEC-010 and DEC-014.` Main Agent should propose a versioned envelope and compatibility matrix for every public request/response, worker command/result, event and checkpoint before implementation. Project Owner approval is required because this changes shared behavior.

#### SEC-CONTRACT-002 — Worker trust and revocation mechanism is not specified

The documents require short-lived service identities, trusted Core policy decisions and revocation-aware rechecks, but do not specify worker authentication, token audience, expiry, nonce/replay protection, key rotation, credential revocation, authorization of a worker to a job, or how a stale worker result is rejected. A client-supplied `principal_ref`, `authorized_scope_ref`, job ID or document ID must never be sufficient.

`ESCALATE: DEC-010.` The approved design must bind worker identity, job, tenant, policy version, document/version scope, request ID and expiry, and must define fail-closed behavior for stale/revoked workers and replayed results.

#### SEC-CONTRACT-003 — Authorization composition and scope freshness are not fully contractual

RBAC + department + document ACL + default deny + explicit deny precedence is clear as policy direction, but the exact composition, deny subject scope, policy-version freshness/expiry, scope audience, scope revocation, tenant replacement/offboarding behavior and anonymous-session binding are not encoded in a versioned schema. Chairman broad read is explicitly subordinate to an explicit deny, but the contract does not provide a machine-checkable policy decision/scope model for this rule.

`ESCALATE: DEC-011 and DEC-014.` Do not let an implementation agent invent precedence or silently broaden Chairman/Admin access.

### HIGH

#### SEC-CONTRACT-004 — Citation and source capability is incomplete

Citation metadata has `page`/`source_span`, while the document contract uses page ranges and the requirements also need Word sections and Excel sheet/ranges. The unit of `start`/`end`, normalization, maximum span, version binding, signed-token audience/expiry, replay behavior and safe response for revoked/nonexistent sources are not defined. `source:download` is separate from `document:read`, which is correct, but the enforcement response and non-existence behavior need a stable contract.

`ESCALATE: DEC-011 and DEC-014.` A citation must remain bound to `tenant_id`, `document_version_id`, source location and current authorization; it must never silently substitute a newer version.

#### SEC-CONTRACT-005 — Cache invalidation is a policy statement, not an atomic protocol

The cache contract lists useful key dimensions and invalidation triggers, but not cache namespace ownership, negative-cache behavior, invalidation ordering, race handling, tombstones, outbox/retry semantics, stale-read policy or what happens when invalidation cannot be confirmed. A response cache can disclose revoked data during a publication/ACL update race unless the read path fails closed on uncertain freshness. Provider prompt caching must remain isolated from authorization and answer caching.

`ESCALATE: DEC-009 and DEC-005.` Main Agent should require source/version/policy epochs or equivalent revocation markers and an atomic publish/invalidate protocol before enabling response caching.

#### SEC-CONTRACT-006 — Job and maintenance state transitions are underspecified

The states are separated correctly (`job_state` versus `document_version_state`, with `MAINTENANCE` as a system mode), but there is no normative transition table for leases, heartbeat expiry, retry scheduling, cancellation, duplicate completion, checkpoint ownership, crash recovery, queue-position disclosure or watchdog expiry. The 60-minute maintenance ceiling, 30-minute approval expiry and provider-specific pause behavior remain proposal inputs.

`ESCALATE: DEC-007 and DEC-006.` A stale checkpoint or resumed job must fail closed and recheck identity, tenant, ACL, policy version and document version before any retrieval, source delivery or completion write.

#### SEC-CONTRACT-007 — Audit/privacy boundary lacks a field-level event contract

The policy correctly denies System Admin access to other users' conversation bodies, including incident handling, and avoids raw prompts/outputs by default. However, the audit/event contract does not define a redaction allowlist, body-versus-metadata separation, export/dashboard filtering, correlation-field restrictions, or how worker errors, traces, cache entries and retry payloads avoid conversation content. `conversation:read` exists as an action but ownership/resource scoping is not expressed in a concrete schema.

`ESCALATE: DEC-003, DEC-005 and P-FR-09/P-NFR-09.` Require a field-level privacy contract and negative tests across API, audit, metrics, traces, queue payloads, support views and exports.

#### SEC-CONTRACT-008 — Idempotency and tracing requirements are not uniformly propagated

The baseline names `X-Request-ID`, `traceparent` and idempotency keys, and upload/chat examples use some of them, but administration mutations, retries, event envelopes, worker results and checkpoint writes do not define duplicate semantics, key binding/fingerprint, TTL, replay response, or parent/child trace propagation. Several examples use `trace_id` without defining its relation to W3C `traceparent` and `X-Request-ID`.

`ESCALATE: DEC-010 and DEC-014.` Define one correlation model and idempotency behavior per mutation/command before clients and workers are implemented.

#### SEC-CONTRACT-009 — Tool and prompt boundary identifiers are inconsistent

The tool example uses `request_context_ref`; retrieval uses `authorized_scope_ref`; identity uses `AuthenticatedPrincipal`. The contracts do not define a single server-issued scope reference, tool-manifest version, argument size limits, per-job deadline propagation, output classification, replay behavior or error non-disclosure. The allowlist and read-only boundary are correct and must remain exact.

`ESCALATE: DEC-010 and DEC-011.` The LLM must never supply or alter the authorization scope, and every tool call must independently reauthorize even when a prior retrieval result exists.

#### SEC-CONTRACT-010 — Ingestion publication and retry atomicity are incomplete

The lifecycle and file limits are well defined, but the contracts do not fully bind upload checksum/version identity, attempt identity, parser isolation result, ACL propagation to chunks, staging-index visibility, atomic activation, cache invalidation confirmation, review-event idempotency and cleanup/tombstone ordering. A failed or stale attempt could otherwise publish an unapproved projection or leave maintenance active indefinitely.

`ESCALATE: DEC-007, DEC-009 and DEC-012.` Require an attempt-scoped state machine and an atomic publication protocol that preserves the previous ACTIVE version on every failure.

### MEDIUM

#### SEC-CONTRACT-011 — Error and pagination compatibility is incomplete

The safe error envelope and cursor pagination limits are proposed, but endpoint-specific error codes, retryability, `Retry-After` units, cursor binding to tenant/principal/filter, maximum query/body lengths and existence-leak rules are not enumerated. These omissions can produce incompatible clients or reveal resource existence.

Main Agent may standardize these as a non-breaking contract proposal, subject to affected-agent review and Owner approval.

#### SEC-CONTRACT-012 — Single-enterprise MVP versus tenant lifecycle is not operationally closed

The product is single-enterprise per deployment, while `tenant_id` is mandatory throughout the contracts and future enterprise replacement/offboarding is a stated security boundary. The contracts do not define tenant deactivation, index/cache/object cleanup, conversation isolation during replacement or tombstone replay. This is not permission to add a live multi-tenant control plane, but it must be safe for a deployment replacement.

`ESCALATE: DEC-009 and DEC-012.`

## Cross-document conflict requiring escalation

`ADR-0004` is marked `Accepted`, while its consequences say that the same administrator performing both reviews remains unapproved until the Project Owner explicitly accepts the ADR. The architecture overview and contract baseline describe the same-admin option as an owner-provided/confirmed proposal, while the functional/NFR documents still retain the corresponding policy details as pending. This is an approval-state conflict, not something Security may reconcile silently.

`ESCALATE: Project Owner via Main Agent.` The Owner must explicitly confirm one of:

1. The same administrator may perform both review stages, with independent recorded decisions and all other gates intact; or
2. Review stages require distinct actors/roles.

Until resolved, document publication implementation must not assume the same-admin path.

## Proposed contract changes for Main Agent (not applied here)

1. Add a common versioned envelope for all public and worker messages: `contract_name`, `schema_version`, `message_id`, `request_id`, W3C trace context, `tenant_id` where applicable, `issued_at`, `expires_at`, producer identity and redacted error metadata. Define backward/forward compatibility and unknown-field rules.
2. Add an authenticated worker-command/result profile binding worker identity, audience, job ID, tenant, document/version scope, policy version, attempt ID, expiry, nonce/idempotency and revocation check. Reject stale, replayed or cross-tenant results.
3. Define `AuthorizedScope` as a server-issued, audience-bound, expiring capability reference with policy epoch/version, tenant, allowed classification, document-version set or query constraints, and explicit deny outcome. Never accept arbitrary IDs from browser/LLM.
4. Define a machine-checkable authorization composition order: principal validity → tenant/session binding → classification → RBAC → department → document ACL → explicit deny override → current version/status. Unknown or stale inputs deny.
5. Define citation location units for PDF/DOCX/XLSX, signed citation-token claims and expiry, current reauthorization, separate read/download decisions and a safe no-existence-leak response.
6. Define cache key and revocation epochs, atomic publish/invalidation ordering, stale/unknown invalidation behavior, tombstones, negative-cache handling and a no-cache fallback when freshness cannot be proven.
7. Add normative job/maintenance transition tables, lease/heartbeat/checkpoint ownership, retry/cancel/replay rules, watchdog recovery and durable completion semantics.
8. Add a privacy-safe audit/telemetry field allowlist: no conversation body, raw prompt/output, source text, secret or token; separate operational metadata from conversation content and enforce role-filtered views.
9. Define idempotency-key fingerprint, scope, TTL and replay response for every mutation/command; propagate `request_id`/`traceparent` through queue, worker, provider, event and checkpoint boundaries without recording sensitive payloads.
10. Define a versioned tool manifest and one authorization-scope identifier, with typed argument/output schemas, budget/deadline propagation, classification, non-disclosing errors and exact MVP allowlist.
11. Define ingestion attempt/version invariants, parser/quarantine results, ACL propagation, staging visibility, atomic activation, cleanup/tombstone replay and maintenance release conditions.

These are proposals for Main Agent integration. They are not contract edits or approvals.

## Four-family test coverage proposal (minimum 10 materially different cases per family)

The Test Agent should implement these after the shared contract version is approved. This list is a coverage proposal only; no test code was created by this task.

### A. Behavior/component — 10 cases

1. Valid authenticated principal produces an allow decision for a permitted PUBLIC document.
2. Anonymous principal is limited to a published PUBLIC ACTIVE version.
3. Employee department grant permits an assigned INTERNAL document.
4. Employee without a document ACL is denied despite matching department.
5. Explicit document deny overrides Chairman broad read permission.
6. Website Manager can perform an allowed document-management action; Chairman cannot.
7. System Admin operational role cannot read another user's conversation body.
8. Retrieval returns only current ACTIVE authorized versions from both dense and lexical branches.
9. Citation preview permits `READ` while original-file download requires separate `DOWNLOAD` authorization.
10. A document version cannot transition to ACTIVE without recorded review-2 approval and publication checks.

### B. Contract/integration — 10 cases

1. Public API rejects a missing or malformed `X-Request-ID` according to the approved envelope rules.
2. W3C `traceparent` survives API → queue → worker → result → audit correlation without sensitive payload fields.
3. A duplicate upload idempotency key returns the original admission result and creates no second job.
4. A duplicate chat-message idempotency key does not create a second durable query job.
5. A worker payload with an unsupported `schema_version` is rejected safely and not retried forever.
6. A compatible additive payload with an unknown optional field follows the approved compatibility rule.
7. A worker result with the wrong tenant, job, document version or policy epoch is rejected.
8. Cursor pagination rejects a cursor bound to another principal, tenant or filter and does not leak existence.
9. Safe Problem Details errors contain code/message/request ID/redacted details and no stack trace, secret or private path.
10. A citation token from an old contract version or wrong audience is rejected without serving source content.

### C. Security/adversarial — 10 cases

1. Prompt claims of administrator status do not change the server-verified principal.
2. Browser-supplied role, tenant, allowed-document list or scope reference cannot broaden retrieval.
3. Cross-tenant dense and lexical searches return zero foreign candidates and zero foreign metadata.
4. Parent-chunk expansion cannot cross the child/source ACL boundary.
5. Revoking an ACL blocks a previously cached answer, citation and download.
6. Policy-service timeout or stale policy version fails closed at admission, retrieval and source access.
7. Replayed or expired worker credentials/results cannot complete or deliver a job.
8. Indirect prompt injection in PDF, DOCX, XLSX, chunk text or tool output cannot invoke a non-allowlisted tool.
9. An LLM-suggested upload, delete, permission-change, SQL, shell, HTTP-fetch or email tool is absent or denied.
10. System Admin, Website Manager and support/incident paths cannot expose another user's conversation body through API, audit, logs, traces, metrics, cache or export.

### D. E2E/operational — 10 cases

1. Anonymous PUBLIC question flows from admission through retrieval to answer and citation recheck.
2. Employee INTERNAL question uses department/ACL policy and delivers only authorized evidence.
3. Upload enters maintenance, pauses new work, completes both reviews, atomically publishes and invalidates affected caches.
4. Upload rejection preserves the former ACTIVE version and safely releases maintenance.
5. Parser/embedding/index failure leaves the former ACTIVE version served and leaves no staged evidence searchable.
6. Maintenance checkpoint resumes a valid queued question only after identity/policy/version rechecks.
7. ACL revocation during maintenance causes a resumed job/citation to deny instead of returning stale evidence.
8. Queue lease expiry and worker crash produce one durable retry/result with no duplicate completion or data disclosure.
9. Primary model outage follows the approved bounded retry/fallback path without bypassing egress/classification policy.
10. Restore/recovery replays tombstones before service resumes and prevents soft-deleted/revoked content from retrieval, cache or download.

## Commands actually executed

- `python3 scripts/validate_harness.py` — exit `0`.
- Result: `HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles`.
- Validator note: this checks scaffolding only; it does not prove application functionality, permissions or runtime behavior.
- Read-only review commands inspected the required AGENTS, contract, architecture/ADR, security and functional/non-functional requirement files.
- No application tests were run because this task has no implementation write scope and the repository is still a harness/documentation baseline.

## Security implications

- Positive: the reviewed baseline consistently places authorization in the backend, treats retrieved content/tool output as untrusted, requires current-version checks and restricts MVP tools to read-only operations.
- Residual: until SEC-CONTRACT-001 through SEC-CONTRACT-010 are resolved in a versioned, Owner-approved contract, downstream agents must not treat proposal examples as production authorization or data-sharing guarantees.
- Privacy: System Admin, Website Manager and incident/operational paths must remain unable to read other users' conversation bodies; diagnostics must use metadata-only, redacted fields.
- Data: no real company files, secrets, provider credentials or deployment resources were accessed.

## Integration steps for Main Agent

1. Review this handoff and obtain affected-agent compatibility comments from Backend, RAG/Orchestration, Ingestion, Frontend and DevOps where their interfaces are involved.
2. Resolve the ADR-0004 same-admin review conflict with the Project Owner; do not infer approval from the current document wording.
3. Convert the accepted proposals into versioned contract changes using `docs/contracts/CHANGE-PROCESS.md`, without silently editing the current DRAFTs.
4. Record the Owner's explicit approval for the resulting contract version and applicable `DEC-*` decisions, especially `DEC-007`, `DEC-009`, `DEC-010`, `DEC-011`, `DEC-012` and `DEC-014`.
5. Update dependent task readiness only after contract approval and compatibility evidence; keep implementation blocked on unresolved major decisions.
6. Have the Test Agent implement the four test families with at least 10 materially different cases each, then run real integration/security evidence before marking the contract or dependent feature complete.

## Known limitations / blockers with IDs

- `SEC-CONTRACT-001` through `SEC-CONTRACT-010` require contract/design resolution before implementation.
- `SEC-CONTRACT-012` requires a safe tenant replacement/offboarding lifecycle, without expanding MVP into live shared multi-tenancy.
- Cross-agent compatibility review is not evidenced in this Security-only handoff.
- The current contract documents remain DRAFT/proposal inputs; this task does not approve them.
- The pre-existing user change to `harness/tasks/tasks.json` (`CONTRACT-001` = `IN_PROGRESS`) was not modified.

## Suggested next READY task

No dependent implementation task should be made READY solely from this handoff. Suggested next action is a Main Agent contract-integration review, followed by Project Owner escalation for the listed major decisions. After an approved contract version exists, `BACKEND-BOOT-001`, `FRONTEND-BOOT-001` and `INFRA-BOOT-001` can be reconsidered according to their dependencies and write-scope checks.

## Human approval required

Project Owner approval is required for the resulting versioned shared contracts, the ADR-0004 review-actor choice, worker trust/revocation behavior, ACL precedence/scope semantics, cache revocation protocol, maintenance/retry state machine, retention/privacy details and any other `ESCALATE` item above. This handoff is a security review and approval package, not an approval.
