# Handoff — CONTRACT-001 / Ingestion Compatibility Reviewer

- Task ID: `CONTRACT-001`
- Agent owner: Ingestion Compatibility Reviewer (`role=ingestion`)
- Status: `IMPLEMENTATION_DEFERRED`
- Contract version(s) used: `docs/contracts/v1-baseline.md` v1.0; focused ingestion/document/cache/audit contracts v1.0
- Upstream dependencies checked: `backend/app/ingestion/AGENTS.md`, `docs/rag/ingestion-design.md`, `docs/contracts/ingestion.md`, `docs/contracts/document.md`, `docs/contracts/events-and-audit.md`, `docs/contracts/cache-and-memory.md`, `docs/architecture/blocks/11-document-lifecycle.md`, `docs/architecture/workflows/admin-ingestion.md`
- Changed files: `harness/handoffs/CONTRACT-001-ingestion.md` only
- New/updated tests: None; this was a read-only compatibility review
- Commands actually executed + exit status: `python3 scripts/validate_harness.py` — exit `0`; `HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles`
- Security implications: quarantine, parser isolation, tenant/ACL propagation, stale-attempt rejection, atomic publication, cache/tombstone invalidation and maintenance recovery affect confidentiality and availability
- Human approval required: No approval is granted by this handoff. Main Agent must resolve blockers and obtain any required contract approval.

## Review conclusion

The ingestion design is directionally compatible with contract v1.0: untrusted uploads enter quarantine, only `.pdf`, `.docx` and `.xlsx` are accepted, checksum and malware/signature checks precede processing, review 1 precedes processing, review 2 precedes publication, chunks carry source/version/tenant/ACL metadata, staging is not searchable, and the previous ACTIVE version is preserved on failure.

The final hardening and database mapping resolve all eight previously reported ingestion contract findings. The contract and DB design now state the required invariants for attempt binding, stage-aware retries, publication gating, ACL manifests, maintenance fencing, ordered tombstones and duplicate checksums. No runtime ingestion implementation or migration is present; that is correctly deferred to downstream implementation tasks and is not a contract-text failure. This handoff is an independent review and does not approve the contract.

## FINAL RECHECK — contract v1.0 hardening + database mapping

The table below is authoritative for this final recheck. The detailed findings later in this file are retained as the historical first-review record.

| Finding | Result | Current evidence / exact section | Reason and remaining requirement |
|---|---|---|---|
| `ING-MISSING-001` attempt identity bound to version/checksum | `PASS` | `docs/contracts/v1-baseline.md:86–86, 137–137`; `docs/contracts/ingestion.md:14–16` | Every attempt is now bound to `document_version_id`, `content_sha256`, parser profile, `attempt_id` and fencing token. Worker completion is also bound to job/attempt/version/policy/fencing state; mismatches and stale fencing cannot write completion/publication. The job example now includes `content_sha256`, `attempt_id` and `fencing_token`. |
| `ING-MISSING-002` retry stage boundaries and cleanup | `PASS` | `docs/contracts/v1-baseline.md:141–147, 157–157`; `docs/database/database.md:596–602, 789–807` | The normative retry matrix distinguishes terminal invalid format/malware/limit, retryable transient processing stages, non-retryable review, and reconciliation-based publication/cleanup. DB mapping defines `current_stage`, checkpoint/lease ownership, artifact cleanup and stage-aware retry. Runtime enforcement is deferred to downstream implementation. |
| `ING-MISSING-003` cross-store atomic publication | `PASS` | `docs/contracts/v1-baseline.md:135–135`; `docs/contracts/ingestion.md:16–16` | The durable two-step visibility protocol now specifies publication ID, expected checksum, corpus epoch, index generation, outbox intent, former ACTIVE retention, matching publication/fencing acknowledgements, atomic pointer/epoch flip, and stale/mismatch recovery via tombstone/repair. |
| `ING-MISSING-004` ACL propagation across derivatives | `PASS` | `docs/contracts/v1-baseline.md:153–159`; `docs/database/database.md:586–595, 663–664, 831–842` | ACL propagation is a publication gate. Every dense, lexical, parent and citation derivative must match version, checksum, `policy_epoch`, ACL digest and expected-count manifest; missing/mismatched derivatives keep the former ACTIVE version. DB `INDEX_PUBLICATIONS` and `CHUNKS` map the manifest/digest and reconciliation checks. Runtime enforcement is deferred. |
| `ING-MISSING-005` durable maintenance owner/lease/recovery | `PASS` | `docs/contracts/v1-baseline.md:142–147, 157–159`; `docs/database/database.md:305–316, 556–561, 659, 780–787` | The contract defines durable maintenance owner, lease ID, fencing token, expiry and compare-and-swap release using `maintenance_window_id + lease_id + fencing_token`; DB `MAINTENANCE_WINDOWS` stores the coordination record and enforces one active window per tenant. Runtime watchdog/race tests are deferred. |
| `ING-MISSING-006` tombstone ordering and acknowledgment barrier | `PASS` | `docs/contracts/v1-baseline.md:125–131, 153–157`; `docs/contracts/cache-and-memory.md:17–21`; `docs/database/database.md:361–374, 422–433, 653, 688, 725, 831–842` | Ordered outbox sequencing, leases, bounded retries, deduplication, consumer watermarks, out-of-order reconciliation and fail-closed freshness are normative. `REVOCATION_TOMBSTONES` maps the revocation ID/tenant/resource/version/epoch/sequence/reason schema and uniqueness; restore/read replay is required before service. Runtime consumers are deferred. |
| `ING-MISSING-007` duplicate-upload checksum policy | `PASS` | `docs/contracts/v1-baseline.md:94–97, 155–157`; `docs/database/database.md:376–386, 647, 650, 662` | Same SHA-256 for the same document/version is explicitly idempotent; same bytes for a new document may reuse only an immutable derived projection and must still perform independent ACL/lifecycle checks. Durable idempotency fingerprints and mismatch rejection are mapped to `IDEMPOTENCY_KEYS`. Runtime behavior is deferred. |
| `ING-MISSING-008` review-event uniqueness | `PASS` | `docs/contracts/v1-baseline.md:94–97, 151–157`; `docs/contracts/ingestion.md:8–9`; `docs/database/database.md:187–196, 580–584, 657, 663` | Review is explicitly independent and idempotent; durable idempotency records and `DOCUMENT_APPROVALS` map stage, reviewer, attempt and decision. Same-admin reviews remain two separate events and one request cannot auto-approve both stages. Runtime behavior is deferred. |

### Final decision

`FINAL RECHECK — PASS at contract and database-design level; IMPLEMENTATION_DEFERRED for runtime.` No true contract contradiction or serious ingestion security gap remains in the reviewed scope. The absence of migrations, ORM/repositories, workers, index adapters and runtime tests is recorded in `docs/database/database.md:32, 940–946` and belongs to downstream implementation/verification tasks.

## Compatible items

### ING-COMPAT-001 — Upload quarantine and parser safety

- Evidence: `docs/contracts/ingestion.md` “Commands” and “Owner-provided ingestion limits”; `docs/rag/ingestion-design.md` sections 1–2; `backend/app/ingestion/AGENTS.md`.
- The upload returns `202` with a job and never becomes immediately ACTIVE. Bytes are stored privately and non-searchably; MIME/magic bytes, checksum, malware status and resource limits are checked before parsing. Macros, scripts and executable formulas are not run.
- Compatibility: `COMPATIBLE`.

### ING-COMPAT-002 — Checksum and immutable version baseline

- Evidence: `docs/contracts/document.md` `DocumentVersion.sha256`; `docs/contracts/ingestion.md` “Owner-provided ingestion limits”; `docs/architecture/workflows/admin-ingestion.md` step 3.
- The version stores a SHA-256 checksum, and upload admission records checksum metadata before processing. A changed file creates a new version and an unchanged version is the retry unit.
- Compatibility: `COMPATIBLE`, with the identity clarification in `ING-MISSING-001` below.

### ING-COMPAT-003 — Two-review lifecycle and same-admin independent events

- Evidence: `docs/contracts/v1-baseline.md` section 7; `docs/contracts/document.md` lifecycle and review rules; `docs/architecture/workflows/admin-ingestion.md` steps 4 and 8.
- Review 1 precedes processing and review 2 follows validation. The same administrator may perform both reviews, but each is a separate authenticated, authorized, timestamped and idempotent event; no single action approves both stages. Approval expires after 30 minutes.
- Compatibility: `COMPATIBLE`.

### ING-COMPAT-004 — Failed/rejected attempts preserve the prior ACTIVE version

- Evidence: `docs/contracts/v1-baseline.md` section 7; `docs/contracts/ingestion.md` job event and limits; `docs/architecture/workflows/admin-ingestion.md` steps 4 and 12.
- Failed, rejected or cancelled versions are non-searchable and cannot replace the previous ACTIVE version.
- Compatibility: `COMPATIBLE`.

### ING-COMPAT-005 — Staging and source provenance

- Evidence: `backend/app/ingestion/AGENTS.md`; `docs/rag/ingestion-design.md` sections 3–6; `docs/contracts/document.md` `ChildChunk`.
- The design separates document/version/parent/child data, preserves page/section/table/sheet/cell provenance, requires source spans and hashes, and treats Qdrant as a projection rather than policy authority.
- Compatibility: `COMPATIBLE`.

## Mismatches and missing invariants

### ING-MISSING-001 — Attempt identity is not bound to document-version checksum

- Severity: `HIGH`
- Exact location: `docs/contracts/v1-baseline.md` section 3 “Idempotency and correlation”; section 6 “Jobs, maintenance and recovery”; section 7 “Document lifecycle and review actors”; `docs/contracts/ingestion.md` “Job event”; `docs/contracts/document.md` “Owner-provided upload and lifecycle baseline`.
- Baseline evidence: the envelope has `attempt_id`; retries have unique attempt IDs and are limited to three attempts for an unchanged version. The example job event exposes only numeric `attempt`, while the document version exposes `sha256` but the attempt schema does not.
- Problem: the contract does not state the immutable key that proves an attempt belongs to one exact `(tenant_id, document_id, version_id, sha256)` tuple, nor whether a late result from an earlier attempt is rejected after a new attempt starts. Numeric `attempt` and opaque `attempt_id` are not defined as equivalent.
- Recommendation: define an attempt record with immutable `tenant_id`, `document_id`, `version_id`, `sha256`, `attempt_id`, monotonic attempt number, job ID, policy epoch, stage, lease generation and terminal status. Accept completion only for the current lease/attempt and exact checksum; reject stale results idempotently without publishing or exposing content. Align the job-event example with the canonical field names.

### ING-MISSING-002 — Retry stage boundaries and cleanup obligations are incomplete

- Severity: `MEDIUM`
- Exact location: `docs/contracts/ingestion.md` “Job event” and “Owner-provided ingestion limits”; `docs/contracts/v1-baseline.md` section 6 “Normative rules”.
- Baseline evidence: retries are limited to three attempts for an unchanged version and only safe stages may retry.
- Problem: “safe stages” is not enumerated. It is unclear which artifacts are reusable, which stages must restart from quarantine, and which attempt owns temporary objects, staged vectors, OCR output and parser work directories after timeout, rejection or cancellation.
- Recommendation: publish a stage/retry matrix: admission, scan, parse, chunk, embed, index-stage, validate and publish; identify retry-safe inputs, cleanup owner, idempotency key and terminal artifact handling for each. Never reuse an artifact unless it is bound to the exact version checksum and approved attempt lineage.

### ING-MISSING-003 — Atomic publication does not define the cross-store commit protocol

- Severity: `BLOCKER`
- Exact location: `docs/contracts/v1-baseline.md` section 5 “Cache and revocation” and section 7 “Document lifecycle”; `docs/contracts/document.md` `DocumentVersion`; `docs/rag/ingestion-design.md` section 5; `docs/architecture/workflows/admin-ingestion.md` steps 7–10.
- Baseline evidence: publication changes the current version and invalidation epochs together; dense and lexical indexes are staged; publication and cache invalidation are mandatory gates.
- Problem: the contract does not define how PostgreSQL current-version state, dense index visibility, lexical index visibility, object/source visibility and outbox invalidation become one atomic publish decision across separate stores. It also does not define the recovery state if one index is committed and another is not.
- Recommendation: define a durable publication transaction/state machine with a publication ID and manifest containing exact version/checksum/index generations. Commit the authoritative PostgreSQL pointer and epoch with an outbox event; make readers require the committed publication generation in every index. Mark incomplete projections unavailable and repair/reconcile before ACTIVE is served, or fail closed. Do not describe a version as ACTIVE merely because one store committed.

### ING-MISSING-004 — ACL propagation is not machine-checkable across all derivatives

- Severity: `HIGH`
- Exact location: `backend/app/ingestion/AGENTS.md`; `docs/rag/ingestion-design.md` section 4; `docs/contracts/document.md` `ChildChunk`; `docs/contracts/v1-baseline.md` sections 2.1, 2.2 and 4.
- Baseline evidence: child chunks inherit ACL metadata; the parent cannot become broader than the source; policy is rechecked at retrieval and parent expansion.
- Problem: there is no required propagation manifest or invariant proving that every child chunk, dense vector, lexical record, parent link, citation locator and staged derivative carries the same or narrower ACL policy reference and exact policy epoch. A missing ACL chunk is mentioned as a validation failure in the design, but the contract does not define the publication gate or failure behavior.
- Recommendation: require a version-scoped ACL propagation manifest/count and validation result before review 2/publication. Fail closed if any derivative is missing, broader, cross-tenant or bound to a stale policy epoch. Keep the authoritative ACL in PostgreSQL/policy store; treat index metadata as a checked projection, never as the sole enforcement input.

### ING-MISSING-005 — Maintenance mode has no durable owner/lease/recovery contract

- Severity: `HIGH`
- Exact location: `docs/contracts/v1-baseline.md` section 6; `docs/architecture/workflows/admin-ingestion.md` steps 2, 10–12; `docs/architecture/blocks/11-document-lifecycle.md` “ARCH-OVERVIEW alignment”.
- Baseline evidence: maintenance is a system mode, new chat admission returns `503`, existing work checkpoints at safe boundaries, a 60-minute watchdog releases maintenance safely, and paused jobs are rechecked before resume.
- Problem: the contract does not define a durable maintenance record, owner/job association, fencing token, acquisition/release idempotency, concurrent-ingestion behavior, or what happens when the watchdog races with a successful publication/failure cleanup. “Release maintenance safely” is not a checkable invariant.
- Recommendation: define one durable maintenance lease with mode, owner job/publication ID, fencing generation, started/expiry timestamps and terminal outcome. All admission and release operations must compare the generation; stale cleanup cannot release a newer maintenance session. Watchdog expiry must move the ingestion to a recoverable terminal/reconciliation state and keep uncommitted data non-searchable.

### ING-MISSING-006 — Tombstone ordering and cache/index acknowledgment are underspecified

- Severity: `HIGH`
- Exact location: `docs/contracts/v1-baseline.md` section 5; `docs/contracts/document.md` “Owner-provided upload and lifecycle baseline”; `docs/contracts/cache-and-memory.md` “Owner-provided lifecycle baseline”; `docs/architecture/workflows/admin-ingestion.md` invariants.
- Baseline evidence: soft delete immediately removes retrieval/preview access, advances epochs in the source-of-truth transaction, enqueues an outbox invalidation event, and restore must replay tombstones/revocations before serving data.
- Problem: no tombstone schema, sequence/order key, deduplication rule, consumer acknowledgment or replay barrier is defined. It is therefore unclear how a delayed index/cache consumer proves it has applied deletion/revocation before a restore or before a stale read path is allowed. “Invalidation confirmation unavailable” must fail closed, but the required confirmation is not defined.
- Recommendation: define a durable tombstone containing tenant, document/version, action, source epoch, publication/deletion sequence, policy epoch and event ID. Consumers apply it idempotently and record the applied sequence/generation. Restore and read paths require the authoritative epoch plus projection/revocation barrier; missing, out-of-order or unknown acknowledgment remains unavailable/fail-closed.

### ING-MISSING-007 — Checksum validation lacks an explicit duplicate-upload policy

- Severity: `MEDIUM`
- Exact location: `docs/contracts/document.md` `DocumentVersion.sha256`; `docs/contracts/ingestion.md` “Owner-provided ingestion limits”; `docs/architecture/workflows/admin-ingestion.md` step 3.
- Baseline evidence: actual bytes, MIME/magic bytes and checksum are validated, and idempotency applies to upload events.
- Problem: the contract does not state whether a same-tenant upload with identical SHA-256 creates a new version, returns the existing version/job, or creates a new review request. It also does not define the behavior when the same idempotency key is reused with a different payload/checksum beyond the general idempotency rule.
- Recommendation: define duplicate checksum semantics separately from request idempotency. Bind the idempotency fingerprint to tenant, document target, byte length and SHA-256; reject a reused key with a different checksum, and make same-checksum behavior explicit without bypassing review or ACL validation.

### ING-MISSING-008 — Review-event independence lacks an event-level uniqueness schema

- Severity: `MEDIUM`
- Exact location: `docs/contracts/v1-baseline.md` section 7; `docs/contracts/document.md` review rules; `docs/contracts/ingestion.md` approval endpoint.
- Baseline evidence: each review is an independent authenticated, authorized, timestamped and idempotent event; same-admin review is allowed.
- Problem: the contract does not specify the unique key and immutable fields that prevent a retry or duplicate request from mutating an already-recorded review decision, nor how a review decision is tied to the exact version checksum/attempt and policy epoch.
- Recommendation: require a unique review event ID/idempotency key scoped to `(tenant_id, version_id, review_stage, reviewer_id, decision_request)` and bind it to the exact version/checksum and current policy epoch. Duplicate identical requests return the original decision; conflicting decisions require a new review event and never overwrite history.

## Historical first-review severity summary (superseded by FINAL RECHECK)

| Severity | Findings |
|---|---|
| BLOCKER | `ING-MISSING-003` atomic cross-store publication protocol |
| HIGH | `ING-MISSING-001`, `ING-MISSING-004`, `ING-MISSING-005`, `ING-MISSING-006` |
| MEDIUM | `ING-MISSING-002`, `ING-MISSING-007`, `ING-MISSING-008` |

## Historical Main Agent integration recommendation

1. Keep ingestion implementation blocked until `ING-MISSING-003` is converted into a versioned publication/reconciliation protocol.
2. Resolve the HIGH findings in the same contract revision, because stale attempts, ACL derivative gaps, maintenance fencing and tombstone ordering can expose revoked/unapproved data or strand service state.
3. Ask Backend, RAG/index and Operations agents for compatibility comments on the proposed protocol; this handoff is ingestion-only and does not substitute for those reviews.
4. After an approved contract revision, add negative tests for stale attempt completion, partial index publication, missing/broader ACL derivative, stale maintenance release, delayed tombstone and restore-before-acknowledgment.

## Evidence and limitations

- `python3 scripts/validate_harness.py` passed with exit status `0`: `HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles`.
- The validator checks harness scaffolding only; it does not prove application behavior, database transactions, index atomicity, cache invalidation or authorization correctness.
- No provider, API key, cloud account, external document or runtime service was used.
- No code, contract, task registry or existing handoff was modified.
