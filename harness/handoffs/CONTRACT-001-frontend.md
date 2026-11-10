# CONTRACT-001 Frontend Compatibility Review

**Reviewer:** Frontend Compatibility Reviewer (`role=frontend`)
**Contract reviewed:** `docs/contracts/v1-baseline.md` v1.0
**Review scope:** OpenAPI/API v1 usage, error envelope, job states, maintenance UI, citation preview/download distinction, role restrictions and anonymous flow.
**Review mode:** Independent review; this handoff does not approve the contract and does not change UI design, code, contracts or tasks.

**Final recheck status:** `FINAL RECHECK: PASS` — contract/database mapping is compatible; frontend implementation evidence is deferred to downstream tasks.

## Evidence inspected

- `frontend/AGENTS.md`
- `frontend/README.md`
- `docs/contracts/v1-baseline.md`
- `docs/contracts/chat-and-jobs.md`
- `docs/contracts/admin-management.md`
- `docs/contracts/identity-and-policy.md`
- `docs/contracts/answer-and-citation.md`
- `docs/design/UI:UX reference/enterprise_knowledge_ai/DESIGN.md`
- All static UI references under `docs/design/UI:UX reference/`
- `python3 scripts/validate_harness.py` — exit status `0`

Validator output:

```text
HARNESS VALID: 17 blocks, 8 agents, 32 tasks; no dependency cycles
Note: this validates scaffolding only, not application functionality, permissions or the Codex runtime.
```

## Recheck summary

The current contract hardening and database mapping resolve the API-side semantics for access requests, no-streaming MVP, canonical roles, maintenance status and citation evidence binding. Static UI references still contain legacy cues, but the normative contract explicitly declares `docs/design` visual-only and supersedes those legacy labels for implementation.

1. The maintenance reference contains legacy `PAUSED_MAINTENANCE` text.
2. The IAM reference contains legacy `manager`/`admin` values and omits Chairman from the visual sample.
3. The chat reference contains legacy SSE/WebSocket and `429 / 202` text.

These are implementation-deferred documentation cues, not current normative contract contradictions, because `docs/contracts/v1-baseline.md:190-193` makes the authoritative replacement explicit. The access-request contract is present, and citation preview/download, anonymous flow and error-envelope rules are compatible subject to the implementation guards below.

## Recheck result by finding

| Finding | Status | Current evidence | Blocker? |
|---|---|---|---|
| F-01 maintenance state | **PASS — IMPLEMENTATION_DEFERRED** | Contract and DB mapping define canonical job states and separate maintenance mode at `docs/contracts/v1-baseline.md:137,144-146,190-193` and `docs/database/database.md:1025-1029`; legacy UI text is explicitly superseded. | No contract blocker. |
| F-02 role identifiers | **PASS — IMPLEMENTATION_DEFERRED** | Canonical roles are explicit at `docs/contracts/v1-baseline.md:57,191-192`, `docs/contracts/identity-and-policy.md:11`, and `docs/database/database.md:509,1023-1024`; legacy visual values are not API authority. | No contract blocker. |
| F-03 access request | **PASS** | `POST /api/v1/access-requests` is defined at `docs/contracts/v1-baseline.md:147` and `docs/contracts/admin-management.md:11`; the existing `RequestAccess()` affordance at `.../kh_ng_gian_tr_chuy_n_rag_tr_ng_th_i_x_l/code.html:552-554` now has a contract target. | No. |
| F-04 streaming/queue | **PASS — IMPLEMENTATION_DEFERRED** | Contract and DB mapping require durable-job polling and separate `429`/`503` handling at `docs/contracts/v1-baseline.md:190,193`, `docs/contracts/chat-and-jobs.md:12,20-22`, and `docs/database/database.md:538-545,1025-1029`; legacy visual text is explicitly superseded. | No contract blocker. |
| F-05 citation preview/download | **PASS** | Version/evidence binding and separate checks at `docs/contracts/v1-baseline.md:107` and `docs/contracts/answer-and-citation.md:12-16,24`; UI has separate preview and `can_download_original` affordances at `.../code.html:164-169,327-332,608-628`. | No, if capability remains server-driven. |
| F-06 anonymous flow | **PASS** | Server-issued anonymous session and ownership at `docs/contracts/chat-and-jobs.md:9-14`; PUBLIC-only rule at `docs/contracts/identity-and-policy.md:11` and `docs/contracts/v1-baseline.md:57`. | No contract blocker. |
| F-07 error envelope | **PASS** | Safe envelope at `docs/contracts/v1-baseline.md:31-39`; maintenance/queue semantics at `.../v1-baseline.md:147-151` and `docs/contracts/chat-and-jobs.md:20-22`; frontend guidance remains in `frontend/AGENTS.md`. | No contract blocker. |

## Findings

### F-01 — Maintenance UI uses a non-contract job state — **FINAL RECHECK: PASS / IMPLEMENTATION_DEFERRED**

- **Classification:** mismatch
- **Severity:** High (contract/state handling)
- **Evidence:** `docs/design/UI:UX reference/ph_duy_t_n_p_t_i_li_u/code.html:102` displays `PAUSED_MAINTENANCE` as the response status for users querying during ingestion maintenance.
- **Normative contract:** `docs/contracts/v1-baseline.md:113-125` says `job_state` is only `QUEUED`, `RUNNING`, `PAUSED`, `RETRY_SCHEDULED`, `COMPLETED`, `FAILED`, `CANCELLED`; maintenance is a system mode and new chat admission returns `503 MAINTENANCE_ACTIVE`. `docs/contracts/chat-and-jobs.md:20-22` repeats this.
- **Impact:** A frontend that parses `PAUSED_MAINTENANCE` as a job state will diverge from the API enum and may show a resumable job when the server actually rejected new admission.
- **Final recheck:** The contract-side fix and DB mapping are present at `docs/contracts/v1-baseline.md:137,144-146,190-193` and `docs/database/database.md:1025-1029`. The legacy token at `docs/design/UI:UX reference/ph_duy_t_n_p_t_i_li_u/code.html:102` is explicitly non-authoritative and superseded for implementation. No contract failure remains; downstream frontend work must implement the normative state mapping.
- **Recommendation:** Render maintenance from `MAINTENANCE_ACTIVE`/HTTP `503` for newly submitted work. For existing jobs, render canonical `PAUSED` plus a separate maintenance indicator. Do not add `PAUSED_MAINTENANCE` to `job_state`.

### F-02 — Role selector does not match canonical role identifiers and omits Chairman — **FINAL RECHECK: PASS / IMPLEMENTATION_DEFERRED**

- **Classification:** mismatch / missing invariant
- **Severity:** High (authorization boundary)
- **Evidence:** `docs/design/UI:UX reference/qu_n_l_ng_i_d_ng_ph_n_quy_n/code.html:621-645` presents `Employee`, `Website Mgr` with value `manager`, and `System Admin` with value `admin`; there is no `chairman` option.
- **Normative contract:** `docs/contracts/v1-baseline.md:43-56` and `docs/contracts/identity-and-policy.md` define canonical roles `system_admin`, `website_manager`, `employee`, `chairman`, plus anonymous public access. The browser cannot choose or grant roles.
- **Impact:** Reusing the design values as API payloads creates an ambiguous role mapping and can omit a required product role. UI labels are presentation-only; the backend must receive server-authorized canonical identifiers.
- **Final recheck:** Canonical role values and server authority are explicit at `docs/contracts/v1-baseline.md:57,191-192`, `docs/contracts/identity-and-policy.md:11,26`, and `docs/database/database.md:509,608-612`. The old visual sample at `.../qu_n_l_ng_i_d_ng_ph_n_quy_n/code.html:621-645` is not API authority and is explicitly superseded for implementation. No contract/security gap remains; the role-aware UI correction is deferred to the frontend task.
- **Recommendation:** Bind labels to `employee`, `website_manager`, `system_admin`, and `chairman`; treat server role data as authoritative and never use a client-selected role as proof of privilege.

### F-03 — `RequestAccess()` is not a v1 public API capability — **FINAL RECHECK: PASS**

- **Classification:** resolved contract gap
- **Severity:** Pass
- **Evidence:** `docs/design/UI:UX reference/kh_ng_gian_tr_chuy_n_rag_tr_ng_th_i_x_l/code.html:538-555` shows an `ACCESS_DENIED` card with a `RequestAccess()` affordance.
- **Normative contract:** `docs/contracts/v1-baseline.md:187` and `docs/contracts/admin-management.md:11` now define `POST /api/v1/access-requests`, with server-derived identity/session, no access grant, and separate authorized idempotent approval/provisioning.
- **Recheck evidence:** The existing affordance at `.../kh_ng_gian_tr_chuy_n_rag_tr_ng_th_i_x_l/code.html:552-554` now has a contract target. Frontend must still avoid rendering denied-resource details and must use the server response, but no contract blocker remains.

### F-04 — Static chat reference mentions streaming contrary to MVP contract — **FINAL RECHECK: PASS / IMPLEMENTATION_DEFERRED**

- **Classification:** mismatch
- **Severity:** Medium
- **Evidence:** `docs/design/UI:UX reference/kh_ng_gian_tr_chuy_n_rag_tr_ng_th_i_x_l/code.html:558-575` says the client should listen to WebSocket or SSE streaming and labels the response `429 / 202`.
- **Normative contract:** `docs/contracts/chat-and-jobs.md:9-12` says asynchronous admission returns `202` with an opaque job ID and explicitly states there is no token streaming in MVP; `:20-22` defines `429` for rate limits and `503` for saturation/maintenance.
- **Impact:** A frontend implementation could depend on an unapproved transport and misclassify a queued response as rate-limited.
- **Final recheck:** The contract and DB mapping are explicit at `docs/contracts/v1-baseline.md:190,193`, `docs/contracts/chat-and-jobs.md:12,20-22`, and `docs/database/database.md:538-545,1025-1029`. The legacy visual text at `.../kh_ng_gian_tr_chuy_n_rag_tr_ng_th_i_x_l/code.html:558-575` is non-authoritative and superseded for implementation. No contract failure remains; polling and status mapping are deferred to the frontend task.
- **Recommendation:** Use `202` plus polling `GET /api/v1/query-jobs/{job_id}` in MVP. Render `429` only for rate limiting and `503` with `Retry-After` for saturation.

### F-05 — Citation preview/download distinction is compatible but must be server-driven — **FINAL RECHECK: PASS**

- **Classification:** compatible with implementation guard
- **Severity:** Pass
- **Evidence:** The chat reference separates “Xem trích đoạn gốc” at `.../code.html:164-169`, shows `can_download_original` at `.../code.html:327-332`, and renders a read-only preview at `.../code.html:608-628` with `can_download_original: false`. `docs/design/UI:UX reference/enterprise_knowledge_ai/DESIGN.md:267` specifies a citation/source drawer.
- **Normative contract:** `docs/contracts/v1-baseline.md:93-103` requires version-bound citation locations, fresh `document:read` for preview, separate `source:download` for originals, and safe unavailable responses for revoked/superseded sources. `docs/contracts/answer-and-citation.md` requires current authorization on each fetch.
- **Recheck evidence:** The hardening adds `evidence_snapshot_hash` and retains immutable version binding at `docs/contracts/v1-baseline.md:107` and `docs/contracts/answer-and-citation.md:7,12-16,24`. The UI reference already distinguishes preview and original download. Keep all capability checks server-driven and separate.

### F-06 — Anonymous flow is contract-compatible but needs explicit UI state — **FINAL RECHECK: PASS**

- **Classification:** compatible / missing UI invariant
- **Severity:** Medium
- **Evidence:** No static UI reference defines an anonymous-session entry, expiry, or authenticated-only history boundary.
- **Normative contract:** `docs/contracts/chat-and-jobs.md:9-14` allows a server-issued anonymous session and limits history to that bound session; `docs/contracts/identity-and-policy.md` limits anonymous access to PUBLIC documents; `docs/contracts/v1-baseline.md:56` makes anonymous access PUBLIC-only.
- **Recheck evidence:** `docs/contracts/chat-and-jobs.md:9-14` and `docs/contracts/identity-and-policy.md:9-11,22-26` now give the frontend the required server-issued session, ownership, PUBLIC-only and fail-closed rules. No contract blocker remains; the UI implementation still needs explicit session-expiry/empty states.

### F-07 — Error envelope usage is compatible; UI mapping is not yet evidenced — **FINAL RECHECK: PASS**

- **Classification:** compatible / implementation requirement
- **Severity:** Low/Medium
- **Evidence:** `frontend/AGENTS.md` requires meaningful `403/empty` states. The baseline at `docs/contracts/v1-baseline.md:31-39` defines safe HTTP errors with `code`, safe `message`, `request_id`, optional redacted `details` and `retryable`; the references show `403` and partial/access-denied visual states, for example `kh_ng_gian_tr_chuy_n_rag_tr_ng_th_i_x_l/code.html:518-555`.
- **Recheck evidence:** The baseline still normatively defines the safe envelope at `docs/contracts/v1-baseline.md:31-39`, while focused chat/admin contracts now expose the applicable `202/429/503`, authorization and idempotency behavior. Frontend should map stable codes and preserve `request_id`; no contract blocker remains.

## Compatibility decisions by requested area

| Area | Result | Notes |
|---|---|---|
| `/api/v1` usage | Compatible | Use REST paths and server-issued IDs; no invented client authority. Exact OpenAPI schemas are still needed before code integration. |
| Error envelope | Compatible | Baseline shape is sufficient; frontend must map stable error codes and preserve correlation IDs. |
| Job states | Pass / implementation deferred | Canonical enum and DB mapping are explicit; legacy visual states are superseded. |
| Maintenance UI | Pass / implementation deferred | Use system-mode/503 semantics for new work; `PAUSED` only for existing jobs. |
| Citation preview/download | Compatible with guard | Separate calls and fresh authorization; server capability response wins. |
| Role restrictions | Pass / implementation deferred | Canonical role identifiers and Chairman restrictions are explicit; legacy visual values are superseded. |
| Anonymous flow | Compatible / implementation deferred | Implement server-issued anonymous session and PUBLIC-only behavior; do not infer or expose scope client-side. |

## Independent review conclusion

`CONTRACT-001` is **FINAL RECHECK: PASS** for frontend contract compatibility. F-01 through F-07 pass; F-01, F-02 and F-04 are marked `IMPLEMENTATION_DEFERRED` because the remaining legacy UI text is explicitly superseded by the normative contract. No true contract contradiction or serious frontend security gap remains in the current files. This review does not approve the contract or claim runtime implementation completion.
