# CONTRACT-001 DevOps Compatibility Review

**Reviewer:** DevOps Compatibility Reviewer (`role=devops`)
**Contract reviewed:** `docs/contracts/v1-baseline.md` v1.0
**Review type:** independent compatibility review; does not approve the contract
**Provider/API-key scope:** no provider selected, no secret used, no provisioning or deployment performed

## Evidence read

- `docs/contracts/v1-baseline.md`
- `infra/AGENTS.md`
- `infra/README.md`
- `docs/operations/deployment-runbook.md`
- `docs/operations/incident-response.md`
- `docs/architecture/blocks/15-observability-audit.md` (monitoring service architecture)

Validation command:

```text
python3 scripts/validate_harness.py
```

Exit status: `0`

Output: `HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles`.

The validator checks harness scaffolding only; it does not prove runtime compatibility, security behavior, backup recovery or deployment readiness.

## Compatible findings

| Area | Evidence | Result |
|---|---|---|
| Provider independence | Contract §10 keeps cloud/provider, model and trace/log backend decisions pending. `infra/README.md` keeps production topology pending and separates student/demo profiles from production. | Compatible. No provider-specific API or secret is required by the contract baseline. |
| TLS and service identity direction | Contract §2.3 requires TLS and short-lived asymmetric-signed service JWTs, with issuer/audience/expiry/job/tenant binding and fail-closed rejection. This matches `infra/AGENTS.md` least privilege and secure service integration. | Compatible at policy level. Operational rotation details are missing (see findings). |
| Trace context | Contract §1 and §3 require W3C `traceparent`, unchanged parent propagation, child spans at service boundaries, and separate `request_id`. Monitoring block §39–§46 assigns application instrumentation to `AUDIT-001` and platform collection to `INFRA-003`. | Compatible. Ownership and propagation rule are clear. |
| Privacy-safe telemetry | Contract §3 and §8 exclude raw prompts, answers, source text, secrets, tokens and conversation bodies. Monitoring block §100–§112 and the runbooks require redacted operational telemetry and private, role-limited monitoring. | Compatible baseline. Metric-label and retention invariants still need to be made explicit. |
| Durable source/cache boundary | Contract §5 makes PostgreSQL/object storage authoritative, Qdrant an index projection and Redis non-authoritative. `infra/README.md` and deployment runbook state the same boundary. | Compatible. |
| Transactional invalidation intent | Contract §5 requires epoch advancement with the source-of-truth change and an outbox invalidation event in the same durable transaction. This aligns with the runbook's cache/index invalidation requirement. | Compatible intent. Delivery, retry and replay mechanics are underspecified. |
| Backup model direction | Deployment runbook specifies PostgreSQL base backup plus WAL/PITR, object-storage versioning/backup, and Qdrant snapshot or rebuild from source. Incident runbook requires tombstone replay after restore. | Compatible direction. Restore ordering, evidence and provider-neutral acceptance criteria are missing from the contract. |
| Deployment boundary | Contract does not select a cloud provider. Infra docs require private networks/storage, isolated environments, secret management, migration/rollback evidence and no unauthorized production deployment. | Compatible. The contract does not silently authorize provisioning or deployment. |

## Mismatches / missing invariants

Severity uses `BLOCKER` for an implementation/release-stopping contract gap, `HIGH` for a security or recovery gap that must be resolved before integration/release, and `MEDIUM` for an operationally important but bounded gap.

### DEVOPS-01 — TLS and JWT key/certificate rotation is not executable

- **Severity:** `HIGH`
- **Exact location:** `docs/contracts/v1-baseline.md` §2.3 `Worker authentication`; related operational ownership in `infra/README.md` §4 and monitoring/deployment boundaries.
- **Finding:** The contract requires TLS and asymmetric service JWTs but does not define minimum TLS policy, certificate identity validation, clock-skew tolerance, signing-key algorithm/strength, JWKS/key distribution, rotation overlap, revocation/retirement behavior, or what happens when the key/certificate source is unavailable.
- **Recommendation:** Add a provider-neutral operational invariant: TLS 1.2+ (or an approved stronger baseline), hostname/service identity verification, synchronized clocks, an approved asymmetric algorithm, key IDs, dual-key overlap for rotation, bounded JWKS/cache lifetime, immediate retirement of compromised keys, and fail-closed behavior when trust material is unavailable or stale. Define certificate/key rotation without changing authorization semantics.

### DEVOPS-02 — `jti` replay storage lacks durability and failure semantics

- **Severity:** `HIGH`
- **Exact location:** `docs/contracts/v1-baseline.md` §2.3, sentence ending `one-time jti replay state`.
- **Finding:** “Replay state” is required but its authoritative store, atomic consume operation, TTL, scope, replication/availability behavior, and crash/retry semantics are not defined. A process-local or best-effort cache could accept a replay after failover, while an unavailable store could accidentally allow traffic.
- **Recommendation:** Specify a durable, shared replay store or equivalent atomic `check-and-consume(jti, issuer, audience, expiry)` operation. TTL must cover token lifetime plus bounded clock skew; entries must be tenant/job/attempt scoped as applicable; duplicate consume and store-unavailable paths must reject; cleanup must not permit reuse before expiry. The implementation may choose the store later, but not the safety semantics.

### DEVOPS-03 — `traceparent` propagation lacks boundary and failure invariants

- **Severity:** `MEDIUM`
- **Exact location:** `docs/contracts/v1-baseline.md` §1 and §3; `docs/architecture/blocks/15-observability-audit.md` §39–§46.
- **Finding:** Propagation is defined, but the contract does not state behavior for malformed or oversized trace headers, whether `tracestate` is preserved/filtered, how asynchronous queue/checkpoint hops link spans, or that telemetry export failure must never block authorization or business processing.
- **Recommendation:** Define bounded W3C header parsing with invalid input replaced by a new server context, explicit `tracestate` handling, span links/parent relation across queue and retry boundaries, and a non-blocking redacted telemetry pipeline with bounded buffering/drop counters. Keep `request_id` separate and never use trace data for authorization.

### DEVOPS-04 — Outbox invalidation has no delivery protocol

- **Severity:** `HIGH`
- **Exact location:** `docs/contracts/v1-baseline.md` §5, sentence requiring an outbox invalidation event in the same durable transaction.
- **Finding:** The contract requires an outbox event but does not define event identity, claim/lease, retry/backoff, deduplication, ordering, poison-event handling, dead-letter behavior, or the transaction boundary for marking delivery. “Invalidation confirmation unavailable” is fail-closed for readers, but no reliable way to obtain that confirmation is specified.
- **Recommendation:** Define a provider-neutral outbox invariant: event ID and aggregate/epoch key are unique; insert is in the source transaction; dispatcher claims with a lease; delivery is at-least-once and idempotent; retries are bounded but durable; poison events are quarantined and alerted; readers fail closed until the relevant epoch is observed by the cache/index consumer. Define replay/reconciliation after dispatcher or cache outage.

### DEVOPS-05 — Cache invalidation confirmation is not operationally measurable

- **Severity:** `HIGH`
- **Exact location:** `docs/contracts/v1-baseline.md` §5 `Readers compare epochs before serving` and `invalidation confirmation is unavailable`.
- **Finding:** The contract does not define the confirmation source, freshness/timeout, required epoch dimensions, behavior for partial consumer lag, or an operator-visible signal. Without these, fail-closed may be inconsistently implemented and revocation recovery cannot be demonstrated.
- **Recommendation:** Define the authoritative epoch tuple and a durable consumer watermark/reconciliation check. Specify bounded freshness/timeout and fail-closed behavior for unknown or lagging partitions. Require metrics/alerts for outbox age, consumer lag, invalidation failures and stale-read prevention, with tenant/user/document identifiers excluded from labels.

### DEVOPS-06 — Metrics/privacy controls do not constrain labels, exemplars or retention enough

- **Severity:** `MEDIUM`
- **Exact location:** `docs/contracts/v1-baseline.md` §3 (`Traces, logs and events contain metadata only`) and §8; `docs/architecture/blocks/15-observability-audit.md` §88–§121.
- **Finding:** Raw content exclusion is clear, but the contract does not prohibit high-cardinality or sensitive labels such as user IDs, document IDs, query hashes, tenant names, token values or authorization decisions that reveal private data. It also does not define metric retention/access/audit controls or whether exemplars may contain trace IDs.
- **Recommendation:** Add an observability schema invariant: metrics use bounded service/route/status/class labels only; no user, document, conversation, raw query, token, secret or unrestricted tenant identifiers; exemplars contain only opaque trace IDs; telemetry export is redacted before leaving the trust boundary; retention and access follow the selected backend policy; export failure is non-blocking and auditable.

### DEVOPS-07 — Backup/restore ordering and acceptance evidence are outside the contract

- **Severity:** `HIGH`
- **Exact location:** `docs/contracts/v1-baseline.md` §5 and §6; `docs/operations/deployment-runbook.md` §7 and Owner-provided operating baseline; `docs/operations/incident-response.md` §23.
- **Finding:** The runbooks describe backups and tombstone replay, but v1.0 does not define a restore invariant across PostgreSQL, object storage, Qdrant, cache and outbox. It does not require encryption/key availability, integrity verification, version compatibility, restore ordering, cache/index quarantine, or evidence that revocations are replayed before retrieval is enabled. The runbook correctly labels RPO/RTO as unproven, so this is a missing contract acceptance rule rather than a contradiction.
- **Recommendation:** Add provider-neutral restore gates: restore PostgreSQL/source documents first; verify integrity and schema compatibility; replay tombstones/revocations and outbox reconciliation; rebuild or restore Qdrant only from authorized ACTIVE versions; keep retrieval disabled until policy/index/cache watermarks converge; invalidate Redis; then run smoke/security checks and record measured RPO/RTO. Require encrypted backups and a documented key-restore dependency without naming a provider.

### DEVOPS-08 — Deployment assumptions omit time sync, health gates and configuration parity

- **Severity:** `MEDIUM`
- **Exact location:** `docs/contracts/v1-baseline.md` §2.3 and §6; `infra/README.md` §2/§5; `docs/operations/deployment-runbook.md` §1–§6.
- **Finding:** The provider-independent wording is compatible, but JWT expiry/replay and distributed leases require synchronized clocks. The contract also does not require readiness to prove schema/index/epoch compatibility, startup to fail closed on missing trust material, or dev/staging/prod configuration parity for security-relevant settings.
- **Recommendation:** Add deployment invariants for bounded clock synchronization and skew monitoring, fail-closed startup/readiness when required trust/configuration is absent, explicit migration/index/epoch compatibility checks before traffic, and separate environment credentials/data with a redacted configuration inventory. Keep provider, region and managed-service choices pending.

## Overall assessment

**Result:** `COMPATIBLE_WITH_REQUIRED_HARDENING`; not an approval.

The v1.0 contract is directionally compatible with the infrastructure role and provider-independent deployment constraints. It has no finding requiring a cloud/provider choice or API key, and no evidence of an immediate contradiction with the reviewed role/runbooks. However, `DEVOPS-01`, `DEVOPS-02`, `DEVOPS-04`, `DEVOPS-05` and `DEVOPS-07` are `HIGH` and should be resolved before contract integration/release evidence. Until then, TLS/JWT trust rotation, replay protection, invalidation delivery and restore safety are policy intentions rather than executable operational invariants.

This review does not approve `CONTRACT-001` and does not change any contract, task or provider decision.

---

## Re-review — `RECHECKED`

**Re-check scope:** only the eight findings above, against the current contract and focused contract/monitoring files. No contract, code or `tasks.json` was changed.

Validator re-run:

```text
python3 scripts/validate_harness.py
```

Exit status: `0`
Output: `HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles`.

### Finding status

| Finding | Status | Current evidence / exact location | Reason if not passed |
|---|---|---|---|
| DEVOPS-01 TLS/JWT key and certificate rotation | **FAIL** | `docs/contracts/v1-baseline.md:82-86` still requires TLS, asymmetric JWT validation, replay state and authoritative replay/fencing, but does not specify TLS minimum, certificate identity verification, clock-skew budget, algorithm/key ID, JWKS/key distribution, rotation overlap or trust-material outage behavior. `docs/operations/cloud-secrets-readiness.md:95-103` gives operational rotation guidance, but does not make these contract invariants. | Rotation remains non-executable as a provider-independent contract. |
| DEVOPS-02 `jti` replay storage | **FAIL** | `docs/contracts/v1-baseline.md:86` now proves replay state and lease fencing are persisted in the authoritative store and binds `worker_jti`, job/attempt, tenant, document version, `policy_epoch` and `fencing_token`. However, it still does not define an atomic check-and-consume operation, replay-entry TTL, bounded clock-skew allowance, duplicate-consume result or store-unavailable behavior. | Durability and binding passed; atomicity and fail-closed failure semantics remain unspecified. |
| DEVOPS-03 trace propagation and export failure | **FAIL** | `docs/contracts/v1-baseline.md:37,95` retains unchanged `traceparent`, child-span and metadata-only rules. `docs/contracts/README.md:50-53` confirms W3C trace context. Monitoring block `docs/architecture/blocks/15-observability-audit.md:107-112` adds redaction and role-limited monitoring. | No current contract section defines malformed/oversized header handling, `tracestate`, queue/retry span links, or that telemetry export failure is non-blocking with bounded drop accounting. |
| DEVOPS-04 outbox invalidation delivery | **FAIL** | `docs/contracts/v1-baseline.md:113-115` now includes ordered outbox invalidation, `sequence`, `attempts` and `acknowledgement`; `:135` adds publication ID, checksum, fencing token and tombstone/repair event. | Event identity/uniqueness, dispatcher lease/claim, retry/backoff, deduplication, poison-event quarantine/dead-letter and replay/reconciliation are still absent. The delivery protocol cannot yet be implemented consistently from the contract. |
| DEVOPS-05 cache invalidation confirmation | **FAIL** | `docs/contracts/v1-baseline.md:113-115` now defines `policy_epoch`, `corpus_epoch`, `index_generation`, all-epoch comparison and fail-closed behavior for missing acknowledgement. `docs/contracts/cache-and-memory.md:19-21` confirms ordered outbox and fail-closed restore/resume. | No authoritative consumer watermark, freshness/timeout rule, partial-lag behavior, or required outbox/consumer-lag/stale-read metrics is defined. Confirmation is safer, but not operationally measurable. |
| DEVOPS-06 metrics/privacy | **PASS** | `docs/architecture/blocks/15-observability-audit.md:105-112` prohibits keys/tokens/passwords/signed URLs/raw content, bans raw user/document/query labels, separates audit from metrics, sets 30-day log/2-year audit targets, restricts monitoring access and limits alert payloads. `docs/contracts/v1-baseline.md:143` independently excludes sensitive event content. | The original label/privacy/retention gap is resolved for the reviewed baseline. Exemplar-specific behavior is not separately defined, but no exemplar contract is currently required by the reviewed files; this is not counted as a blocker. |
| DEVOPS-07 backup/restore ordering and evidence | **FAIL** | `docs/operations/deployment-runbook.md:17-18,34` and `docs/operations/incident-response.md:23` state backups, restore verification and tombstone replay. `docs/contracts/cache-and-memory.md:19-21` requires tombstone/revocation replay before serving and fail-closed acknowledgement. | The contract still lacks a complete provider-neutral restore gate covering source-first ordering, integrity/schema/key verification, Qdrant quarantine/rebuild, outbox reconciliation, Redis invalidation, retrieval enablement criteria and measured RPO/RTO evidence. Runbook guidance is not sufficient contract acceptance evidence. |
| DEVOPS-08 deployment assumptions | **FAIL** | `docs/contracts/v1-baseline.md:82,124` requires expiry, replay and lease/fencing behavior; `docs/operations/deployment-runbook.md:1-7` requires migration/index/health checks; `infra/README.md:50` keeps provider production choices pending. | No explicit clock synchronization/skew monitoring, fail-closed startup/readiness on missing trust material, schema/index/epoch compatibility gate, or security-configuration parity invariant is present. Provider independence remains compatible, but deployment safety is incomplete. |

### Re-check conclusion

**Overall status: `RECHECKED — FAIL`**

`DEVOPS-06` passes. `DEVOPS-02`, `DEVOPS-04` and `DEVOPS-05` are materially improved by the hardening (authoritative replay/fencing, ordered outbox/acknowledgement, explicit epoch comparison and publication fencing), but remain `FAIL` because the exact operational invariants listed above are still absent. `DEVOPS-01`, `DEVOPS-03`, `DEVOPS-07` and `DEVOPS-08` remain unresolved.

Current blockers are contract-level, not provider/API-key blockers. This re-review does not approve the contract and does not authorize implementation, provisioning or deployment.

---

## Final re-review — `FINAL RECHECK`

**Review basis:** current `docs/contracts/v1-baseline.md`, focused contracts, `docs/database/database.md`, monitoring block and operations runbooks. This section supersedes the earlier re-check for current status. No contract, code, `tasks.json` or other handoff was modified.

Validator:

```text
python3 scripts/validate_harness.py
```

Exit status: `0`
Output: `HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles`.

### Final status by previous finding

| Finding | Final status | Evidence | Remaining work / reason |
|---|---|---|---|
| DEVOPS-01 TLS/JWT key and certificate rotation | **IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:88-90` now defines `kid`, authenticated key-set publication, rotation overlap, revoked/unknown key failure, TLS 1.3/TLS 1.2 cipher policy, certificate identity verification, RS256-or-stronger algorithms, 30-second clock skew and fail-closed trust-material/readiness behavior. | The invariant is contract-complete. Runtime key/certificate rotation and readiness tests remain downstream DevOps implementation/release evidence. No provider choice is required. |
| DEVOPS-02 `jti` replay storage | **IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:131,133` defines durable replay records, atomic compare-and-insert, `REPLAY_DETECTED`, `AUTH_UNAVAILABLE` fail-closed behavior and expiry after token lifetime plus skew. DB mapping: `docs/database/database.md:400-406,652,690,723` (`WORKER_REPLAY_NONCES`, unique hash, expiry and atomic-consume index). | Contract and DB mapping are explicit. Runtime concurrency/failover tests remain downstream implementation evidence. |
| DEVOPS-03 trace propagation and export failure | **IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:37,99` makes W3C `traceparent`, child-span propagation, separate `request_id` and metadata-only telemetry normative. `docs/architecture/blocks/15-observability-audit.md:105-112` defines redaction, bounded labels, retention and private access. DB mapping: `docs/database/database.md:342-358,633` stores `traceparent`/derived `trace_id` as audit metadata and keeps conversation bodies out of audit paths. | Malformed-header handling, async span-link implementation and exporter-drop tests are downstream observability work; no authorization contradiction or serious privacy gap is present in the current contract. |
| DEVOPS-04 outbox invalidation delivery | **IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:125-131,153,157` defines ordered invalidation, unique event key, lease claim, bounded retry, deduplication, dead-letter audit, watermark ordering, reconciliation and publication fencing. DB mapping: `docs/database/database.md:361-374,653,688,720,813-821` defines `OUTBOX_EVENTS`, sequence/attempt/status/ack fields, transactional insertion, lease publishing, retry and dead-letter behavior. | Contract and DB mapping are explicit. Dispatcher/consumer runtime tests and failure drills remain downstream implementation evidence. |
| DEVOPS-05 cache invalidation confirmation | **FAIL** | Contract `docs/contracts/v1-baseline.md:127-131` now requires per-tenant/aggregate consumer watermark, 60-second freshness timeout, reconciliation and fail-closed reads. However, DB mapping `docs/database/database.md:361-374` only has one `acknowledged_at` on `OUTBOX_EVENTS`; there is no durable per-consumer, tenant/aggregate watermark/ack table or equivalent mapped columns. | A global outbox acknowledgement cannot prove that every cache/index consumer has applied the required sequence. This is a real mapping gap affecting stale/revoked-content safety. The contract invariant is explicit, but the authoritative DB representation is not. |
| DEVOPS-06 metrics/privacy | **PASS** | `docs/architecture/blocks/15-observability-audit.md:105-112` prohibits secrets/raw content and unbounded user/document/query labels, separates audit from metrics, defines retention/access and redacted alerts. `docs/contracts/v1-baseline.md:165` independently excludes sensitive event content. | No contract contradiction or serious remaining privacy gap found. Runtime redaction and dashboard tests remain normal implementation evidence. |
| DEVOPS-07 backup/restore ordering and evidence | **IMPLEMENTATION_DEFERRED** | The safety invariant is distributed across `docs/contracts/v1-baseline.md:153,157`, `docs/contracts/cache-and-memory.md:19-21`, `docs/operations/deployment-runbook.md:15-18` and `docs/operations/incident-response.md:23`: former ACTIVE remains served until publication verifies, tombstones/revocations replay before reads, PostgreSQL is authoritative, Qdrant is rebuildable, and RPO/RTO are explicitly unclaimed until drills. DB mapping includes `REVOCATION_TOMBSTONES` and `OUTBOX_EVENTS` at `docs/database/database.md:361-374,422-433,688,813-842`. | Restore encryption/key custody, actual ordering checks and measured RPO/RTO are release/operations evidence, not a contract contradiction. Production remains NO-GO until restore drills pass. |
| DEVOPS-08 deployment assumptions | **IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:90,142,153,159` defines clock skew, trust-material readiness, leases/fencing and publication/index compatibility gates. `docs/operations/deployment-runbook.md:3-9,15-20` defines isolated environments, migrations, health checks and pending RPO/RTO. DB mapping covers durable heads, leases, publications and epochs at `docs/database/database.md:648,705,712,718-725`. | Clock monitoring, startup/readiness checks and environment configuration-parity tests remain downstream DevOps implementation evidence. Provider/region remains correctly pending. |

### Final conclusion

**Overall status: `FINAL RECHECK — FAIL`**

Seven findings are now either `PASS` at contract level or `IMPLEMENTATION_DEFERRED` because the normative invariant and its database/operations mapping are explicit. `DEVOPS-05` remains the only true current blocker: the contract requires per-consumer invalidation watermarks, but the database design maps only a global outbox acknowledgement. This is a serious stale-read/revocation-safety gap and must be resolved by the owning Main Agent/Database task before integration is considered complete.

No runtime code was treated as a contract failure. No provider/API key, provisioning, deployment or approval decision was made in this review.

---

## Final recheck — DEVOPS-05 only

**Status: `PASS`**

Current contract evidence:

- `docs/contracts/v1-baseline.md:127-129` requires all-epoch comparison, fail-closed reads when confirmation is missing, per-consumer applied sequence/watermark per tenant and aggregate, out-of-order wait/reconciliation, and a measurable 60-second freshness timeout with stale-read/consumer-lag metrics.

Current database mapping evidence:

- `docs/database/database.md:403-412` defines `OUTBOX_CONSUMER_WATERMARKS` with `tenant_id`, `consumer_name`, `aggregate_type`, `aggregate_id`, `applied_sequence_no`, `last_acknowledged_at` and `freshness_deadline`.
- `docs/database/database.md:497` maps tenant ownership to the table.
- `docs/database/database.md:515` states that global acknowledgement is insufficient for cache safety.
- `docs/database/database.md:748` defines the unique key `(tenant_id, consumer_name, aggregate_type, aggregate_id)` for per-consumer invalidation freshness.

The previous mapping gap is resolved. The contract’s per-consumer sequence/freshness invariant now has an explicit durable database representation. Runtime consumer lag, reconciliation and fail-closed behavior remain downstream implementation and release evidence, not a contract-text failure.

Validator re-run: exit `0`, `HARNESS VALID: 17 blocks, 8 agents, 32 tasks; no dependency cycles`.
