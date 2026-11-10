# CONTRACT-001 RAG Compatibility Review

**Reviewer:** RAG Engineer
**Role:** `rag_engineer`
**Contract reviewed:** `docs/contracts/v1-baseline.md` v1.0
**Review type:** independent compatibility review; does not approve the contract
**Scope:** retrieval freshness and authorization, hybrid dense+sparse filtering, parent expansion, PDF/DOCX/XLSX citations, source/download reauthorization, stale versions and cache epochs

**Recheck status:** `FINAL RECHECK: PASS` on 2026-11-10 against current contract and database mapping after Main Agent hardening.

## Executive result

No critical security contradiction was found between the v1 baseline and the RAG role instructions. The core behavior is compatible: both dense and BM25 branches are tenant/ACTIVE-version/ACL filtered, authorization is rechecked at fusion/reranking, parent expansion, citation and source delivery, and stale or unavailable policy fails closed.

The following issues should be resolved before implementation is considered contract-compatible. They are mostly schema and terminology gaps; they do not authorize this reviewer to change the contract.

## Findings

### RAG-001 — Citation locator schema is underspecified for DOCX/XLSX

- **Classification:** Missing invariant / schema gap
- **Severity:** Medium
- **Exact locations:**
  - `docs/contracts/v1-baseline.md`, §4 Retrieval and citations, “Citation locations are version-bound”
  - `docs/contracts/answer-and-citation.md`, `Answer` response example
  - `docs/contracts/retrieval.md`, `Response` example
- **Evidence:** The baseline defines PDF page+character span, DOCX section/paragraph+span and XLSX sheet+cell range/value span. The response examples only expose `page_start`, `page_end`, `page` and generic `source_span`; they do not define a discriminated locator for DOCX or XLSX.
- **Recommendation:** Define a format-discriminated citation locator schema (`pdf`, `docx`, `xlsx`) with required fields per format and reject a locator that does not match the immutable document MIME/format. Keep the version-bound fields mandatory for every variant.

### RAG-002 — Trace/correlation field terminology conflicts with the v1 envelope

- **Classification:** Mismatch
- **Severity:** Medium
- **Exact locations:**
  - `docs/contracts/v1-baseline.md`, §1 Versioning and envelope
  - `docs/contracts/retrieval.md`, `Internal request` and `Response` examples (`trace_id`)
  - `docs/contracts/answer-and-citation.md`, `Answer` response example (`trace_id`)
- **Evidence:** v1 requires `request_id` and W3C `traceparent` in the normative envelope. The focused retrieval and answer examples use `trace_id` without defining whether it is an alias, a domain query identifier, or an additional required field.
- **Recommendation:** Use `request_id` and `traceparent` in transport envelopes; reserve `query_id` for the retrieval/answer operation. If `trace_id` is retained for compatibility, define it as a non-authoritative derived field and specify its mapping to `traceparent`.

### RAG-003 — Policy epoch/version naming is not normalized

- **Classification:** Mismatch / implementation ambiguity
- **Severity:** Medium
- **Exact locations:**
  - `docs/contracts/v1-baseline.md`, §2.2 `AuthorizedScope`, §5 Cache and revocation
  - `docs/contracts/identity-and-policy.md`, `PolicyDecision` and `Retrieval scope`
  - `docs/contracts/cache-and-memory.md`, `Cache`
- **Evidence:** The baseline makes `policy_epoch` the freshness value and requires it in cache keys and scope checks. The focused identity/cache documents use `policy_version` in equivalent places. Without an explicit equivalence rule, a cache or retriever can compare different identifiers and serve stale data.
- **Recommendation:** Choose one normative name (`policy_epoch` is the v1 baseline choice), define its type and monotonicity, and explicitly map or deprecate `policy_version`. Cache keys, scope records, policy decisions and rechecks must use the same value.

### RAG-004 — Answer contract lacks an explicit evidence-snapshot binding

- **Classification:** Missing invariant
- **Severity:** Medium
- **Exact locations:**
  - `docs/contracts/answer-and-citation.md`, `Answer` and `Verification`
  - `docs/rag/retrieval-design.md`, Steps 7–8
  - `docs/contracts/v1-baseline.md`, §4 Retrieval and citations and §5 Cache and revocation
- **Evidence:** The documents require claim grounding and fresh authorization, but the answer payload does not carry an evidence-set/snapshot identifier or the policy/corpus/index epochs used to generate the answer. A long-running generation can therefore finish after ACL/publication changes unless the implementation has an implicit but undocumented snapshot/recheck boundary.
- **Recommendation:** Define the answer-generation boundary: bind the answer and citations to an immutable evidence snapshot containing `policy_epoch`, corpus/index epoch and document-version IDs; recheck that snapshot before returning the answer and downgrade to a safe unavailable/insufficient result if it is stale.

### RAG-005 — Cache epoch taxonomy and invalidation completion are not machine-checkable

- **Classification:** Missing invariant
- **Severity:** Medium
- **Exact locations:**
  - `docs/contracts/v1-baseline.md`, §5 Cache and revocation
  - `docs/contracts/cache-and-memory.md`, `Cache` and `Owner-provided lifecycle baseline`
- **Evidence:** v1 correctly requires durable epoch advancement with the source-of-truth transaction, outbox invalidation and fail-closed reads when stale. It does not define the exact epoch set, the resource scope of each epoch, or the condition that constitutes “invalidation confirmation” for every cache tier.
- **Recommendation:** Specify a small epoch registry (at minimum policy, document/publication, corpus/index), ownership, monotonic update rule, cache-key inclusion and the read-side comparison/ack condition. Make absence or rollback of any required epoch a cache miss/fail-closed path.

### RAG-006 — Parent expansion authorization is compatible but the result invariant should be explicit

- **Classification:** Missing invariant
- **Severity:** Low
- **Exact locations:**
  - `backend/app/rag/AGENTS.md`, parent expansion and citation fetch instruction
  - `docs/rag/retrieval-design.md`, Step 5
  - `docs/contracts/document.md`, `ChildChunk`
  - `docs/contracts/v1-baseline.md`, §4 Retrieval and citations
- **Evidence:** All sources require authorization before parent expansion and state that parent ACL cannot be broader than the source. They do not explicitly state that an unauthorized parent must be omitted without changing the child’s authorization result, rank features, or citation metadata.
- **Recommendation:** Add an implementation invariant: parent expansion is an optional, separately authorized enrichment; denial or absence of the parent never broadens access, leaks existence, changes the child’s authorization decision, or creates a parent citation.

## Compatibility matrix

| Requirement | Contract v1.0 | RAG/identity evidence | Result |
|---|---|---|---|
| Tenant + ACTIVE version filtering | Baseline §2.1, §4 | `retrieval-design.md` Step 3; `retrieval.md` Algorithm 1–2 | Compatible |
| Dense and BM25 filtering | Baseline §4 | `backend/app/rag/AGENTS.md`; `retrieval-design.md` Step 3 | Compatible |
| Recheck after fusion/rerank | Baseline §4 | `retrieval.md` Algorithm 3–4 | Compatible |
| Parent expansion | Baseline §4 | `retrieval-design.md` Step 5; `document.md` ChildChunk | Compatible; clarify RAG-006 |
| PDF/DOCX/XLSX citation locations | Baseline §4 | `answer-and-citation.md` verification | Compatible semantically; schema gap RAG-001 |
| Preview/download reauthorization | Baseline §4 | `answer-and-citation.md` Verification; `document.md` upload baseline | Compatible |
| Stale/superseded version handling | Baseline §4, §7 | `answer-and-citation.md` Verification; `document.md` lifecycle | Compatible |
| Cache policy/corpus epochs | Baseline §5 | `cache-and-memory.md` Cache | Compatible intent; naming/taxonomy gaps RAG-003/RAG-005 |
| Fail closed on PDP/policy failure | Baseline §2.1, §5 | `retrieval-design.md` Failure handling; `identity-and-policy.md` PolicyDecision | Compatible |
| Retrieval limits and reranking | Baseline §4, §9 | `retrieval-design.md` Steps and execution bounds | Compatible |

## Evidence and limitations

- `python3 scripts/validate_harness.py` completed with exit status `0`:

  ```text
  HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles
  ```

- This validator checks harness scaffolding only; it does not prove runtime authorization, citation correctness, cache invalidation, or application behavior.
- No provider, API key, cloud service or external corpus was used.
- No code, contract, task registry or test file was modified by this review.

## Recheck of original findings (historical recheck; superseded below)

### RAG-001 — Citation locator schema for DOCX/XLSX: `FAIL`

- **Current evidence:** `docs/contracts/v1-baseline.md`, §4 now requires format-specific locator semantics and an `evidence_snapshot_hash`; however, `docs/contracts/retrieval.md`, `Response` and `docs/contracts/answer-and-citation.md`, `Answer` still show only the generic/page-shaped example (`page`, `page_start`, `page_end`, `source_span`). No discriminated `pdf`/`docx`/`xlsx` schema or MIME-to-locator validation rule is present.
- **Reason:** The semantic requirement exists, but the machine-checkable response contract is still insufficient to prevent a DOCX/XLSX citation from being represented with an invalid PDF-style locator.
- **Required follow-up:** Define the format-discriminated locator schema and reject format-incompatible locators. This remains an implementation-integration blocker for citation contract completeness, not a newly discovered security contradiction.

### RAG-002 — Trace/correlation terminology: `PASS`

- **Evidence:** `docs/contracts/v1-baseline.md`, §1 explicitly requires `request_id` and `traceparent`, and states that `request_id` is not a substitute for `traceparent`. `docs/contracts/retrieval.md`, `Internal request` now carries `traceparent`; `docs/contracts/answer-and-citation.md`, `Answer` now carries `traceparent` and `query_id`. The former ambiguous `trace_id` examples are removed.
- **Result:** Transport correlation is now aligned with the normative v1 envelope; `query_id` is appropriately operation-level.

### RAG-003 — Policy epoch/version naming: `PASS`

- **Evidence:** `docs/contracts/v1-baseline.md`, §1 states that `policy_epoch` is the authoritative numeric freshness value and that legacy/display `policy_version` must not replace it. `docs/contracts/identity-and-policy.md`, `PolicyDecision` and `Retrieval scope`, plus `docs/contracts/cache-and-memory.md`, `Cache`, now use `policy_epoch`. `docs/contracts/retrieval.md`, `Internal request` also carries `policy_epoch`.
- **Result:** The authoritative name and legacy mapping are explicit. Any remaining prose saying “policy version” is non-normative wording and does not change the machine contract.

### RAG-004 — Evidence-snapshot binding: `PASS`

- **Evidence:** `docs/contracts/v1-baseline.md`, §4 requires every citation reference to carry an immutable `evidence_snapshot_hash` together with `document_version_id` and `policy_epoch`. `docs/contracts/answer-and-citation.md`, `Answer` now includes `evidence_snapshot_hash` and `policy_epoch`; its verification still requires current authorization and ACTIVE source-span checks. `docs/contracts/document.md`, lifecycle and `docs/contracts/v1-baseline.md`, §7 bind publication to immutable version/checksum and visibility epochs.
- **Result:** The answer/citation contract now has an explicit immutable evidence binding. Runtime implementation must still verify the hash and freshness before return; that is an implementation acceptance obligation, not an unresolved contract gap.

### RAG-005 — Cache epoch taxonomy and invalidation completion: `PASS`

- **Evidence:** `docs/contracts/v1-baseline.md`, §5 names `policy_epoch`, `corpus_epoch` and `index_generation`, requires all three in retrieval/answer cache keys, durable same-transaction advancement, ordered outbox invalidation, sequence/attempt/ack tracking and fail-closed behavior for missing acknowledgement. §7 adds the two-step publication protocol with `publication_id`, checksum, epochs and fencing token. `docs/contracts/cache-and-memory.md`, `Cache` and lifecycle baseline use the same epoch names and require ordered-outbox acknowledgement.
- **Result:** Epoch ownership/scope and invalidation completion are sufficiently specified for implementation and test design.

### RAG-006 — Parent expansion deny/omission invariant: `FAIL`

- **Current evidence:** `backend/app/rag/AGENTS.md` requires a new authorization check; `docs/rag/retrieval-design.md`, Step 5 requires expansion only if permitted; `docs/contracts/document.md`, `ChildChunk` says parent ACL cannot broaden source and permission must be rechecked; `docs/contracts/v1-baseline.md`, §4 requires reauthorization before parent expansion. None explicitly states that a denied/missing parent must be omitted without changing child authorization, rank features, or citation metadata.
- **Reason:** Authorization-before-expansion is present, but the non-leakage behavior of a denied parent remains implicit. This can create implementation divergence in ranking, snippets or citation construction.
- **Required follow-up:** Add or explicitly accept the invariant that parent expansion is optional enrichment; parent denial/absence never broadens access, leaks existence, changes child authorization/ranking, or creates a parent citation.

## Rechecked disposition

`RECHECKED — 4 PASS, 2 FAIL (RAG-001, RAG-006)`. No critical RAG security contradiction was found. The two remaining failures are precise contract-completeness gaps and should be resolved or explicitly accepted by Main Agent before RAG contract integration. This handoff remains an independent review and is not contract approval.

## FINAL RECHECK

**Status:** `FINAL RECHECK: PASS`
**Implementation status:** `IMPLEMENTATION_DEFERRED` — no runtime application code is present; runtime behavior, schema validation and authorization tests belong to downstream implementation/test tasks and are not treated as contract-text failures here.

The final review covers the two findings that were still open in the previous recheck, plus confirmation that the earlier passing findings remain intact.

### RAG-001 — Citation locator schema for DOCX/XLSX: `PASS`

- **Contract evidence:** `docs/contracts/v1-baseline.md`, §4, lines 105–115 defines a discriminated locator object with explicit `kind` variants for `PDF`, `DOCX` and `XLSX`, including required format-specific fields. The same section binds citations to immutable version, evidence snapshot and policy epoch and requires separate preview/download authorization at line 117.
- **Database evidence:** `docs/database/database.md`, `ANSWER_CITATIONS` definition at lines 318–329 stores `source_locator` and `evidence_snapshot_hash`; the responsibilities at lines 614–620 explicitly require `source_locator` to be a PDF/DOCX/XLSX discriminated locator bound to immutable extracted evidence. The database design also retains chunk/version linkage and a composite version consistency constraint at lines 616–620 and 661.
- **Disposition:** The normative invariant and relational mapping are explicit. The generic page-shaped examples still present in focused retrieval/answer documents are non-normative because those documents defer citation rules to `v1-baseline.md`; downstream API schema/fixture work must use the discriminated baseline shape.

### RAG-002 — Trace/correlation terminology: `PASS`

- **Evidence:** `docs/contracts/v1-baseline.md`, §1 lines 36–38 makes `request_id` and `traceparent` normative and limits legacy `policy_version`; `docs/contracts/retrieval.md`, line 7 uses `traceparent`; `docs/contracts/answer-and-citation.md`, line 7 uses `traceparent`; `docs/database/database.md`, AUDIT_EVENTS responsibilities at lines 628–634 make `traceparent`/`request_id` typed fields and `trace_id` derived metadata only.
- **Disposition:** No contract contradiction remains.

### RAG-003 — Policy epoch/version naming: `PASS`

- **Evidence:** `docs/contracts/v1-baseline.md`, §1 line 38 makes numeric `policy_epoch` authoritative. `docs/contracts/identity-and-policy.md`, `docs/contracts/cache-and-memory.md` and `docs/contracts/retrieval.md` use `policy_epoch`. `docs/database/database.md`, lines 606–612 and 633–634 map policy epoch as an authorization/audit field.
- **Disposition:** Any remaining “policy version” wording is non-normative legacy wording and cannot replace `policy_epoch` in checks.

### RAG-004 — Evidence-snapshot binding: `PASS`

- **Evidence:** `docs/contracts/v1-baseline.md`, §4 lines 105–117 requires immutable evidence snapshot binding, version-bound locators and policy epoch. `docs/contracts/answer-and-citation.md`, line 7 includes `evidence_snapshot_hash`; `docs/database/database.md`, lines 318–329 and 614–620 map the hash and immutable chunk/version citation relation.
- **Disposition:** The contract/database boundary is explicit. Runtime freshness verification before answer delivery remains downstream implementation evidence, as required by this review instruction.

### RAG-005 — Cache epoch taxonomy and invalidation completion: `PASS`

- **Evidence:** `docs/contracts/v1-baseline.md`, §5 lines 125–129 defines `policy_epoch`, `corpus_epoch`, `index_generation`, ordered outbox acknowledgement, sequence/watermark and fail-closed freshness timeout. `docs/database/database.md`, lines 164–172 map corpus/index epochs to `DOCUMENT_HEADS`; lines 408–420 map publication metadata; lines 422–432 map revocation tombstones; lines 493–499 and 648–664 define the durable publication/revocation constraints.
- **Disposition:** Epoch taxonomy and durable mapping are explicit enough for downstream cache/index implementation and tests.

### RAG-006 — Parent expansion deny/omission invariant: `PASS`

- **Contract evidence:** `docs/contracts/v1-baseline.md`, §4 line 119 explicitly requires a denied/stale parent to be omitted and never used for ranking, context or citation; an independently authorized child may remain without broadening or silently altering its authorization decision.
- **Database evidence:** `docs/database/database.md`, `CHUNKS` at lines 586–594 requires same-tenant/version parent linkage and eligible ACTIVE-only retrieval; `DOCUMENT_ACCESS_GRANTS` at lines 606–612 requires explicit DENY precedence and stale-value fail-closed evaluation.
- **Disposition:** The normative non-leakage invariant and DB relationship/authorization inputs are explicit. Parent expansion runtime tests remain downstream evidence.

### Final security/compatibility conclusion

No true contract contradiction or serious RAG security gap remains in the reviewed scope. Dense+sparse tenant/ACTIVE/ACL filtering, scope freshness, parent reauthorization, version-bound citations, preview/download reauthorization, stale-version handling and cache epoch fail-closed rules remain compatible.

## Independent reviewer disposition

Historical initial disposition: `COMPATIBLE_WITH_REMEDIATIONS`. It is superseded by the `RECHECKED` disposition above; Main Agent retains approval authority.
