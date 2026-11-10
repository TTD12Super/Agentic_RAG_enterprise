# Handoff — CONTRACT-001 Backend Compatibility Review

- Task ID: `CONTRACT-001`
- Reviewer: Backend Compatibility Reviewer
- Role: `backend`
- Contract reviewed: `docs/contracts/v1-baseline.md` v1.0
- Recheck status: `FINAL RECHECK`
- Scope: API, identity, database/migrations, idempotency, audit, cache, jobs/checkpoints, worker JWT and privacy
- Changed files: this handoff only
- Code/contracts/tasks modified: none
- Approval: not granted; this is an independent compatibility review for the Main Agent

## Final recheck — current files

### Final disposition by previous finding

| Finding | Final status | Current evidence | Review result |
|---|---|---|---|
| BE-CONTRACT-001 — generic idempotency persistence | `IMPLEMENTATION_DEFERRED` | `v1-baseline.md` §§3, lines 94–97 makes durable PostgreSQL idempotency normative. `database.md` ERD lines 376–386 defines `IDEMPOTENCY_KEYS` with operation, resource, key, fingerprint, response and expiry; constraints/indexes lines 650, 662 and 721 make the uniqueness and immutable replay response explicit. | Contract and DB mapping are compatible. Runtime repository/migration/transaction tests belong to downstream `DB-001`/backend implementation; their absence is not a contract failure. |
| BE-CONTRACT-002 — `AuthorizedScope` and policy epoch | `PASS` | `v1-baseline.md` §§2.2, lines 61–78 requires audience, tenant, policy epoch, classification constraint, server-bound document/version filter, expiry and revocation. `database.md` ERD lines 388–400 now maps `AUTHORIZED_SCOPES` to `scope_hash`, audience, principal, policy epoch, `classification_max`, `document_version_filter`, `policy_decision_ref` and issued/expiry/revocation timestamps. `database.md` lines 630–635 makes the constraints mandatory, invalidates missing policy decisions/filters, and lines 673 and 744 define active-scope uniqueness and validation indexing. | No remaining contract or database-mapping gap found for this finding. Runtime scope issuance, lookup, revocation and fail-closed tests remain downstream implementation evidence. |
| BE-CONTRACT-003 — worker replay/lease fencing | `IMPLEMENTATION_DEFERRED` | `v1-baseline.md` §§2.3, lines 82–88 and §§6, lines 141–143 require replay persistence and fencing. `database.md` ERD lines 264–287 adds lease ID, fencing token and heartbeat to `QUERY_JOBS`; lines 224–243 add attempt/checksum/fencing to `INGESTION_JOBS`; lines 400–406 define `WORKER_REPLAY_NONCES`; constraints/indexes lines 652 and 723 define replay consumption. | The normative invariant and DB mapping are explicit. Atomic consume/CAS and JWT validation remain downstream implementation/tests. |
| BE-CONTRACT-004 — citation locator | `IMPLEMENTATION_DEFERRED` | `v1-baseline.md` §4, lines 101–107 makes the locator discriminated by PDF/DOCX/XLSX and requires evidence hash. `database.md` ERD lines 318–329 and §5.4, lines 614–620 map `source_locator` and `evidence_snapshot_hash` to `ANSWER_CITATIONS`; `answer-and-citation.md` line 7 supplies the response shape. | The authoritative mapping is explicit enough for implementation. Locator validation and reauthorization tests remain downstream. |
| BE-CONTRACT-005 — conversation privacy | `IMPLEMENTATION_DEFERRED` | `v1-baseline.md` §8, line 165 requires separate body/metadata paths and forbids privileged body selection. `database.md` lines 531–535 define message storage, lines 628–635 define typed audit/privacy rules, and line 633 explicitly forbids conversation body queries through admin/operations audit paths. | The normative boundary and DB responsibility are explicit. Actual repositories/roles/RLS and negative tests are implementation work; no contract contradiction remains. |
| BE-CONTRACT-006 — atomic active-version switch | `IMPLEMENTATION_DEFERRED` | `v1-baseline.md` §7, lines 153–159 defines the two-step publication protocol and fencing. `database.md` ERD lines 164–172 adds `DOCUMENT_HEADS` with active version/corpus/index epochs/fencing; constraints lines 648, 704–705 and risk line 959 select the dedicated head-table strategy. | The previous circular-FK ambiguity is resolved. Atomic transaction and cross-store reconciliation tests belong to DB-001/ingestion implementation. |
| BE-CONTRACT-007 — version-ambiguous approve/publish | `PASS` | `v1-baseline.md` line 188 and `ingestion.md` lines 8–9 require `/documents/{document_id}/versions/{version_id}/approve|publish`; the event schema includes `version_id`, checksum, attempt and fencing token. | Fully resolved at contract level and mapped to immutable versions. |
| BE-CONTRACT-008 — anonymous-session lifecycle | `IMPLEMENTATION_DEFERRED` | `cache-and-memory.md` line 19 and `v1-baseline.md` lines 187–189 define server-issued session behavior and retention. `database.md` ERD lines 142–150 adds `ANONYMOUS_SESSIONS`; lines 515–519 and constraint/index lines 645, 701 map tenant binding, last-seen, expiry, revocation and uniqueness. | Contract and DB mapping are compatible. Session middleware, cleanup and isolation tests remain downstream. |
| BE-CONTRACT-009 — typed audit fields | `IMPLEMENTATION_DEFERRED` | `v1-baseline.md` line 165 and `events-and-audit.md` line 7 require action, decision, policy epoch, request/trace context. `database.md` ERD lines 342–359 and §5.4, lines 628–635 map request ID, action, decision, traceparent and policy epoch as typed fields. | Contract and schema mapping are compatible. Append-only enforcement and role-filtered readers remain implementation work. |
| BE-CONTRACT-010 — feedback readiness conflict | `IMPLEMENTATION_DEFERRED` | `v1-baseline.md` line 189, `chat-and-jobs.md` line 16 and `database.md` lines 622–626 now agree on one record per authenticated user/answer or anonymous session/answer, identical replay and changed-replay rejection. | Previous focused-contract/database contradiction is resolved. Unique constraint and endpoint behavior remain downstream implementation. |
| BE-CONTRACT-011 — error/pagination details | `IMPLEMENTATION_DEFERRED` | `v1-baseline.md` lines 187–193 defines endpoint additions, bounded `Retry-After`, opaque cursor binding to tenant/principal/filter/expiry and stable error codes. `docs/contracts/README.md` lines 52–54 defines cursor default/max. | Contract text is now sufficient; FastAPI schemas, cursor signer/store and negative tests remain downstream. |

### Final conclusion

Final backend review result for BE-CONTRACT-002: `PASS`. The normative scope constraints and their authoritative database mapping are explicit. Runtime scope issuance, lookup, revocation and fail-closed tests remain downstream implementation evidence, not a contract-text failure. No remaining contract gap was found for this finding.

### Validation evidence

```text
python3 scripts/validate_harness.py
exit 0
HARNESS VALID: 17 blocks, 8 agents, 32 tasks; no dependency cycles
```

The validator checks harness structure and dependency consistency only. Runtime migrations, PostgreSQL constraints, authorization enforcement and worker replay behavior remain downstream implementation evidence. `pytest` was not run because the environment has no `pytest` module.

## Historical recheck — superseded by final recheck

## Executive result — recheck

The Main Agent hardening resolves the contract-level ambiguity for worker fencing, durable idempotency, citation formats, cache epochs, publication protocol, privacy separation, version-targeted approval/publish and feedback behavior. The recheck therefore passes the contract semantics for those items.

The backend/database compatibility review does not pass overall yet. `docs/database/database.md` remains a design proposal with no migrations/schema execution and still lacks durable mappings for several newly normative fields. Those are implementation blockers even though the v1 contract now states the required behavior.

## Recheck result by original finding

| Finding | Status | Current evidence | Remaining backend consequence |
|---|---|---|---|
| BE-CONTRACT-001 — generic idempotency | `FAIL` | Contract resolved by `v1-baseline.md` §§3, lines 90–95: durable PostgreSQL records, fingerprint, 24-hour response replay and tool-call idempotency. `database.md` §6.1, lines 524–526 still only defines query-job/request-message and query-job idempotency indexes; no generic idempotency record is mapped. | Upload/review/publish/admin/checkpoint/tool replay still needs an undocumented persistence design. |
| BE-CONTRACT-002 — scope/policy epoch | `FAIL` | Contract resolved by `v1-baseline.md` §§1–2, lines 38, 61–78: numeric `policy_epoch`, stored `AuthorizedScope`, audience/expiry/revocation and rechecks. `database.md` §§3.2, 5.4 and ERD still define no scope table, epoch authority or epoch transaction mapping. | Authorization and cache freshness cannot be implemented from the current DB proposal without inference. |
| BE-CONTRACT-003 — worker replay/lease fencing | `PARTIAL → FAIL` | Contract resolved by `v1-baseline.md` §2.3, lines 82–86: persisted replay state and monotonic `fencing_token`. `database.md` §§5.2 and 9.2, lines 421–427 and 683–687 mention heartbeat and lease-token CAS, but the QUERY_JOBS ERD has no heartbeat/fencing fields and no JWT replay-state store. | Worker completion/checkpoint/publication cannot be safely implemented or migrated yet. |
| BE-CONTRACT-004 — citation locator | `PARTIAL → FAIL` | Contract resolved by `v1-baseline.md` §4, lines 101–107 and `answer-and-citation.md` line 7: format-specific locator plus evidence snapshot hash. `database.md` §§4 and 5.4, lines 284–294 and 492–497 still model only chunk/version/page fields and optional quote; DOCX/XLSX locator persistence is absent. | API can validate a typed DTO only by keeping data outside the proposed authoritative schema; migration mapping is incomplete. |
| BE-CONTRACT-005 — conversation privacy | `PASS contract / FAIL DB enforcement` | Contract resolved by `v1-baseline.md` §8, line 143 and `chat-and-jobs.md` lines 11, 14, 16: separate body/metadata paths and no privileged body access. `database.md` §§5.2, 10 and ERD still have `MESSAGES.content` but no body-safe view/role/repository mapping; RLS is explicitly only proposed at lines 717–720. | Privacy boundary is normative but not yet enforceable/evidenced at the backend data layer. |
| BE-CONTRACT-006 — active-version atomic switch | `PARTIAL → FAIL` | Contract resolved by `v1-baseline.md` §7, lines 133–137: publication ID, checksum, corpus/index epochs, fencing and former ACTIVE fallback. `database.md` §13, lines 806–817 still lists the circular active-version FK strategy as an open blocker; no migration choice is recorded. | DB-001 cannot safely implement the publication invariant without choosing head-table or tested deferrable-FK design. |
| BE-CONTRACT-007 — version-ambiguous approve/publish | `PASS` | `v1-baseline.md` §9, line 148 and `ingestion.md` lines 8–9 now use `/documents/{document_id}/versions/{version_id}/approve|publish`; ingestion event line 14 carries checksum, attempt and fencing token. | No remaining contract mismatch found for this finding. |
| BE-CONTRACT-008 — anonymous-session lifecycle | `FAIL` | `cache-and-memory.md` line 19 and `chat-and-jobs.md` lines 9, 14, 26 define server-issued binding and 30-minute/24-hour/7-day lifecycle. `database.md` §§5.2 and ERD still only have `anonymous_session_hash` on conversations, with no session expiry/last-seen/revocation record. | Idle/max expiry and session binding require a schema/authority not specified in the DB proposal. |
| BE-CONTRACT-009 — typed audit fields | `PARTIAL → FAIL` | Contract resolved by `v1-baseline.md` §8, line 143 and `events-and-audit.md` lines 7–9: action, decision, policy epoch and trace context are normative. `database.md` ERD and §5.4, lines 505–510 still expose only event type/outcome/trace ID plus untyped `safe_metadata`; request ID/action/decision/epoch are not mapped as required fields. | Audit queries and privacy projections remain dependent on undocumented JSON validation. |
| BE-CONTRACT-010 — feedback readiness conflict | `PASS contract / FAIL DB doc consistency` | Contract resolved by `v1-baseline.md` §9, line 149 and `chat-and-jobs.md` line 16: one record per authenticated user/answer or anonymous session/answer, identical replay returns original, changed replay rejects. `database.md` lines 499–503 and 816 still say anonymous feedback policy is pending. | Focused contracts are clear, but the authoritative DB design still contradicts them; feedback migration cannot be marked compatible until the stale DB text is reconciled. |
| BE-CONTRACT-011 — error/pagination details | `FAIL` | `v1-baseline.md` lines 32–37 resolves envelope shape and `README.md` lines 52–54 defines cursor defaults/max. `chat-and-jobs.md` line 22 still only names `Retry-After`; no typed endpoint error-code/retry-after format or cursor binding schema is present in backend/database docs. | FastAPI clients can still diverge on retry semantics, cursor ownership and non-disclosure behavior. |

### Recheck conclusion

`CONTRACT-001-backend.md` is `RECHECKED`, but the backend compatibility result is `FAIL` for implementation readiness. One finding fully passes (BE-CONTRACT-007); BE-CONTRACT-005 and BE-CONTRACT-010 pass at contract level but fail the current DB mapping/consistency check. The remaining findings are still partial or failed for the same reason: the contract was hardened, while the database design remains proposal-level and does not yet map the required durable fields/constraints.

No new backend finding was added outside the original eleven. The existing detailed findings below remain the historical evidence and recommendations; this recheck table is authoritative for their current status.

## Executive result — original review

The baseline is directionally compatible with the FastAPI/PostgreSQL modular-monolith plan: backend-owned authorization, PostgreSQL as the source of truth, Qdrant as a projection, durable jobs, transactional outbox, explicit deny precedence and fail-closed behavior are implementable.

It is not yet a sufficiently concrete backend implementation boundary. The main blockers are not technology choices; they are missing durable schema/invariant mappings for capabilities, policy epochs, generic idempotency, worker replay/lease ownership, citation locators and privacy-safe data access. Implementing these by inference would make the backend choose contract semantics.

## Compatible areas

| Area | Evidence | Backend assessment |
|---|---|---|
| Runtime shape | `backend/README.md` §2, §4; `backend/AGENTS.md` | FastAPI modular monolith with PostgreSQL authority, Qdrant projection, optional Redis and private object storage is compatible. |
| Tenant and identity authority | `v1-baseline.md` §2.1; `database.md` §§3.1, 5.1 | Active tenant membership, server-derived principal and composite tenant references fit the proposed schema. |
| Authorization placement | `v1-baseline.md` §§2.1–2.2; `identity-and-policy.md` | PDP/PEP checks at API, retrieval, parent expansion, citation and source download fit backend service boundaries. |
| Document lifecycle | `v1-baseline.md` §7; `database.md` §8.1; `document.md` | Two review stages, immutable versions and preservation of the prior ACTIVE version are implementable with the proposed document/version tables. |
| Durable jobs | `v1-baseline.md` §6; `database.md` §§3.4, 5.2, 8.2–8.3 | PostgreSQL jobs, revision/checkpoint fields, leases and outbox are compatible with at-least-once delivery. |
| Derived vector index | `v1-baseline.md` §§4–5; `database.md` §§3.3–3.4, 9.3 | PostgreSQL publication gate plus staged Qdrant projection is compatible and preserves fail-closed retrieval. |
| API error/correlation direction | `v1-baseline.md` §§1, 3; `chat-and-jobs.md` §3 | JSON errors, bounded request IDs and W3C trace context can be implemented in FastAPI middleware. |

## Findings

### BE-CONTRACT-001 — Generic idempotency persistence is not mapped to the database

- **Classification:** `MISMATCH / BLOCKER`
- **Severity:** Blocker for safe mutation implementation
- **Evidence:** `v1-baseline.md` §§3, lines 87–90 requires a 24-hour request fingerprint and final safe response for mutating POSTs, and uniqueness for upload, review, publish, chat, worker completion and checkpoint writes. `database.md` §6.1, lines 524–526 only specifies query-job/request-message and query-job idempotency indexes; the ERD has no generic idempotency table or equivalent columns for all operations.
- **Problem:** Upload/review/publish/admin mutations and worker/checkpoint writes have no durable place to atomically record fingerprint, response, expiry and operation scope. A unique `QUERY_JOBS.idempotency_key` cannot enforce the other required operations.
- **Recommendation:** Main Agent should add an approved persistence profile, preferably a tenant-scoped `IDEMPOTENCY_RECORDS` table with operation/resource/fingerprint/status/safe-response/expiry and a uniqueness key, or explicitly map every operation to an equivalent durable record. Define transaction boundaries and replay response behavior before implementing mutation routes.

### BE-CONTRACT-002 — `AuthorizedScope` and policy epoch have no authoritative persistence mapping

- **Classification:** `MISSING INVARIANT / BLOCKER`
- **Severity:** Blocker for authorization/retrieval integration
- **Evidence:** `v1-baseline.md` §§2.2 and 5, lines 60–77 and 109–111 require an opaque stored scope reference, audience, expiry, revocation, current `policy_epoch` and epoch advancement in the same source-of-truth transaction. `database.md` §§3.2 and 5.4 mention policy version and grants, but the ERD/table responsibilities do not define scope records, a tenant policy-epoch source, or epoch columns/transaction rules.
- **Problem:** Backend cannot implement scope admission, replay/revocation or cache freshness deterministically from the proposed schema. Deriving the epoch from unrelated timestamps would weaken the contract.
- **Recommendation:** Define the authoritative policy epoch/version store and `AUTHORIZED_SCOPES` persistence (or an approved equivalent), including audience, tenant, principal, scope constraints, issued/expiry/revocation and lookup transaction semantics. Map every epoch-changing mutation to that store and its outbox event.

### BE-CONTRACT-003 — Worker JWT replay protection and lease ownership are underspecified in schema

- **Classification:** `MISSING INVARIANT`
- **Severity:** High; blocker for worker completion/resume paths
- **Evidence:** `v1-baseline.md` §2.3, lines 79–83 requires one-time `jti` replay state and rejects stale/revoked/cross-tenant commands/results. §6, lines 119–123 requires heartbeat, lease expiry and compare-and-swap. `database.md` §5.2, lines 421–427 mentions worker ID, heartbeat and lease expiry, but the QUERY_JOBS ERD fields shown in §4 do not include heartbeat or a lease token; no replay/jti table is defined.
- **Problem:** `worker_id` alone cannot distinguish an old lease holder from a current one, and JWT `jti` cannot be made one-time without durable consume/revoke state. A stale worker could race a completion or checkpoint unless the backend invents an additional invariant.
- **Recommendation:** Add explicit `lease_token`/generation and `heartbeat_at` (or an equivalent CAS contract) to job persistence, plus a bounded `WORKER_TOKEN_REPLAYS`/nonce store or an approved key-value authority. Define atomic claim, heartbeat, completion and checkpoint predicates: tenant, job, attempt, lease generation, policy epoch and expiry must all match.

### BE-CONTRACT-004 — Citation locator schema cannot represent the v1 citation contract

- **Classification:** `MISSING INVARIANT / MISMATCH`
- **Severity:** High
- **Evidence:** `v1-baseline.md` §4, lines 97–103 requires PDF UTF-8 spans, DOCX section/paragraph spans and XLSX sheet/range locators. `database.md` ERD and §5.4, lines 492–497 define `ANSWER_CITATIONS` with chunk/version and optional `source_quote`, while `CHUNKS` only exposes page fields in the ERD; no normalized character span, paragraph identifier, sheet name or cell range fields are specified.
- **Problem:** Backend cannot validate or return a stable citation location for DOCX/XLSX, and cannot prove a stored citation matches the normalized source span. Storing only `source_quote` is not a substitute for the required version-bound locator.
- **Recommendation:** Define a typed locator model (discriminated by source format) and its DB/JSON mapping, including normalization version, bounded offsets/ranges, version binding and validation rules. Keep source download authorization separate from preview as required by the baseline.

### BE-CONTRACT-005 — Privacy rule is stronger than the proposed message/audit data access model

- **Classification:** `MISSING INVARIANT`
- **Severity:** High
- **Evidence:** `v1-baseline.md` §§2.1 and 8, lines 56 and 137 forbids `system_admin` from reading another user's conversation body through API, audit, support, incident, export, cache or trace views. `database.md` ERD stores `MESSAGES.content`; §5.2, lines 405–418 describes ownership but does not define a database view/column policy or service boundary preventing privileged operational queries from selecting content. `events-and-audit.md` requires metadata-only events but does not define the access projection.
- **Problem:** A normal backend repository or admin dashboard query could accidentally return message content while still passing role-level authorization. Role checks alone do not prove body exclusion across support/export/telemetry paths.
- **Recommendation:** Define separate conversation-content and metadata repositories/views, explicit response DTO allowlists, and negative integration tests for system admin, website manager, audit, metrics, traces, cache and export. If RLS/column privileges are used, make them defense-in-depth and keep the application PEP authoritative.

### BE-CONTRACT-006 — Atomic active-version switch is acknowledged but not implementable from the current relational shape

- **Classification:** `MISSING INVARIANT`
- **Severity:** High
- **Evidence:** `v1-baseline.md` §7, lines 129–131 requires atomic publication and epoch invalidation. `database.md` §5.3, lines 445–458 gives `DOCUMENTS.current_active_version_id`; §6.1, lines 522 and 532 requires a partial unique active-version index and matching citation version; §13 (open implementation decisions) identifies the circular active-version foreign key/deferrability issue.
- **Problem:** Directly enforcing both `DOCUMENTS.current_active_version_id → DOCUMENT_VERSIONS` and “one ACTIVE version” can require a deferrable composite FK or a document-head design. Without choosing one, a migration can leave a split-brain active pointer or weaken referential integrity.
- **Recommendation:** Main Agent should choose and record one implementation: a dedicated document-head/current-version table, or a tested deferrable composite-FK transaction. The same transaction must update the active pointer, publication state, policy/corpus epochs and outbox event, with the previous ACTIVE version preserved on failure.

### BE-CONTRACT-007 — Ingestion endpoints are version-ambiguous for approval and publication

- **Classification:** `MISMATCH`
- **Severity:** High
- **Evidence:** `docs/contracts/ingestion.md` §Commands, lines 6–10 uses `/api/v1/documents/{id}/approve` and `/publish`; `v1-baseline.md` §7 and `database.md` §§5.3/8.1 make the review and publication state belong to a specific immutable document version.
- **Problem:** A document can have multiple uploaded versions. A document-level path does not identify which version is being approved/published, so the backend would need to infer “latest pending” and could approve or publish the wrong version under concurrent uploads.
- **Recommendation:** Bind the command to `version_id` in the path or required body and include it in idempotency/resource uniqueness. Reject stale version state rather than resolving implicitly to the latest version.

### BE-CONTRACT-008 — Anonymous-session lifecycle is not fully represented in the proposed schema

- **Classification:** `MISSING INVARIANT`
- **Severity:** Medium/High privacy risk
- **Evidence:** `cache-and-memory.md` §Owner-provided lifecycle baseline sets anonymous idle expiry at 30 minutes, maximum 24 hours and retention at 7 days. `database.md` §§5.2 and 6.1 describe `anonymous_session_hash` and conversation ownership, but the ERD does not define an anonymous session table/expiry fields or uniqueness/rotation rules.
- **Problem:** Backend cannot reliably enforce idle/max expiry, bind a request to the server-issued session, or prevent hash reuse/ambiguous session ownership using only `CONVERSATIONS.anonymous_session_hash`.
- **Recommendation:** Define the trusted anonymous-session record (or explicit equivalent) with hash/token binding, tenant/deployment binding, created/last-seen/expires/revoked timestamps, retention cleanup and a unique ownership rule. Never accept a client-selected tenant or raw session identifier as authority.

### BE-CONTRACT-009 — Audit event required fields are not first-class in the proposed table

- **Classification:** `MISSING INVARIANT`
- **Severity:** Medium
- **Evidence:** `v1-baseline.md` §8, line 137 requires identifiers, action, decision, policy/version epochs, timestamps, bounded error codes and request/trace IDs. `database.md` ERD lists `event_type`, `outcome`, `trace_id` and `safe_metadata`, but no request ID, action/decision, policy epoch or schema/version field; `events-and-audit.md` example also uses `action` and `decision`.
- **Problem:** Storing mandatory authorization/audit fields only in untyped JSON weakens queryability, retention filters and privacy review. It also makes it hard to prove every deny decision carries the same correlation and policy context.
- **Recommendation:** Promote the normative audit fields to typed columns or define a versioned, validated `safe_metadata` schema with mandatory keys. Add an append-only write path and role-filtered read projections; never make raw event JSON an admin shortcut to conversation content.

### BE-CONTRACT-010 — Approved baseline and focused chat contract disagree on feedback readiness

- **Classification:** `MISMATCH`
- **Severity:** Medium; blocks feedback-dependent backend endpoints
- **Evidence:** `v1-baseline.md` §10, line 145 says the delegated contract decisions are resolved, while `chat-and-jobs.md` §16 says exact feedback endpoint schemas, retention and anonymous/repeated feedback policy remain draft and must be escalated. `database.md` §5.4, lines 499–503 calls the anonymous policy pending.
- **Problem:** Backend cannot safely implement feedback mutation/listing semantics or uniqueness for anonymous submissions while one normative document says the contract is approved and another says the policy is unresolved.
- **Recommendation:** Main Agent should mark feedback behavior explicitly deferred from the v1 backend surface or record the final authenticated/anonymous policy in a versioned contract amendment. Do not infer anonymous repeat behavior from the current recommended database rule.

### BE-CONTRACT-011 — Error and pagination behavior is not sufficient for typed backend clients

- **Classification:** `MISSING INVARIANT`
- **Severity:** Medium
- **Evidence:** `v1-baseline.md` §1, line 36 defines a Problem Details-like shape but not endpoint-specific code/enums; `chat-and-jobs.md` §22 requires `Retry-After` but does not define units/format; `admin-management.md` asks for pagination/error schemas to be reviewed before implementation.
- **Problem:** FastAPI handlers can produce incompatible retryability, cursor binding or resource-existence behavior unless the backend invents the missing schema. This is especially relevant to `503 MAINTENANCE_ACTIVE`, queue saturation and cross-tenant denial responses.
- **Recommendation:** Define typed error codes, retryability and `Retry-After` format, plus cursor binding to tenant/principal/filter and bounded request/query sizes. Keep denial responses non-disclosing and stable across API routes.

## Compatibility disposition

| Capability | Result | Note |
|---|---|---|
| API shell and middleware | Compatible with conditions | Requires typed envelope/error and correlation models. |
| Identity and tenant membership | Compatible with conditions | Requires server-only principal construction and composite tenant checks. |
| Authorization/ACL | Compatible with conditions | Requires persisted scope/policy epoch and machine-enforced grant subject/effect constraints. |
| Database migrations | Not ready to implement safely | Active-version cycle, idempotency, scope/replay and lease invariants are unresolved in schema. |
| Job/checkpoint worker API | Not ready to implement safely | Lease generation, heartbeat, replay state and CAS predicates must be explicit. |
| Ingestion/review API | Not ready to implement safely | Approval/publish must target immutable `version_id`. |
| Citations/source access | Not ready to implement safely | Format-specific locator model is missing. |
| Audit/privacy | Not ready to implement safely | Body exclusion and typed audit fields need enforceable backend boundaries. |
| Cache/revocation | Compatible with conditions | Requires durable epoch authority and atomic outbox/invalidation protocol. |

## Required Main Agent actions before backend implementation

1. Resolve BE-CONTRACT-001 through BE-CONTRACT-006 as implementation invariants or approve explicit equivalent designs.
2. Resolve version-targeting in BE-CONTRACT-007 and anonymous-session lifecycle in BE-CONTRACT-008.
3. Reconcile baseline approval with the feedback draft in BE-CONTRACT-010.
4. Publish the resulting versioned contract/schema mappings before `DB-001`, `IDENT-001`, `AUTH-001`, ingestion or chat implementation is marked ready.
5. Have the Test Agent execute the four required families (at least 10 materially different cases each) against the real backend/database boundaries; this review does not claim runtime coverage.

## Validation evidence

Command:

```text
python3 scripts/validate_harness.py
```

Exit status: `0`

Output:

```text
HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles
```

This validator checks harness structure and dependency consistency only. It does not prove API behavior, migrations, authorization, JWT replay protection, privacy isolation or runtime compatibility.

## Review limits and residual risk

- No code, migrations, contracts, tasks, provider/API keys or production resources were accessed or changed.
- No application/runtime tests were run because the repository documents that implementation is not started and this review has handoff-only write scope.
- The report does not approve CONTRACT-001 or change task readiness; Main Agent owns integration and approval routing.
- Residual risk: implementing downstream backend work before the listed invariants are versioned would require undocumented choices and could create cross-tenant, stale-worker, duplicate-mutation or privacy failures.
