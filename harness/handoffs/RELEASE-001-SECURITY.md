# RELEASE-001 — Security Review Handoff

- **Review agent:** Security
- **Review status:** **BLOCKED — NO-GO FOR RELEASE**
- **Scope:** Local, read-only security review of `/Users/trantrungdung/Downloads/enterprise-agentic-rag-harness`.
- **Repository revision reviewed:** `7a9ccdc2b3cfbe8b1b6a239abc3597df4a7344fb` (`integrate frontend with backend data APIs`).
- **Changes made by this review:** This handoff file only. No backend, frontend, infrastructure, task, migration, or test files were modified.
- **Security claim:** This report does **not** claim production security and does **not** mark the release DONE.

## Executive verdict

The repository contains useful security contracts and several effective local checks for tenant filtering, ACL enforcement, safe audit metadata, and fail-closed retrieval behavior. The selected security suites do not establish production readiness, however. The current runtime still has release-blocking authorization and state-consistency gaps, and the RAG executor is explicitly a local development adapter rather than a production worker trust boundary.

The release must remain **NO-GO** until the high-risk findings below are fixed and re-tested against the durable multi-instance deployment path.

## Review method and evidence

### Graphify-first orientation

The first repository query was:

```text
graphify query "Trace authorization, privacy, secrets handling, audit logging, tenant isolation, and cross-tenant data flows. Identify security-sensitive entrypoints, stores, guards, and tests." --context 12 --budget 12000
```

Graphify indexed `graphify-out/graph.json` and surfaced the relevant security entrypoints and tests, including authorization adversarial tests, audit tests, database baseline tests, tenant-isolation tests, policy-outage tests, privacy-safe invalidation metadata, `tenant_uuid`, `_audit`, `secrets`, and logging configuration. The query was used for orientation; findings below are supported by source and test evidence.

### Contracts and code inspected

The review inspected the security README/test cases, authorization matrix, data-protection and threat-model documents, identity/policy, events/audit, admin-management, retrieval, answer/citation, and v1 baseline contracts. Relevant implementation areas included:

- authentication and admin APIs;
- policy evaluation and explicit-deny precedence;
- chat/citation authorization and state refresh;
- PostgreSQL runtime adapters and migrations;
- local RAG execution and context binding;
- frontend token handling;
- security/adversarial QA suites.

The v1 baseline requires server-issued authorization scope, repeated tenant/policy/ACL/version checks at admission, retrieval, parent expansion, citation, and source download; signed worker identity with replay/fencing; durable revocation state; and privacy-safe checkpoints/audit records. Those requirements are used as the comparison baseline here.

## Ranked findings

### SEC-001 — HIGH — Explicit DENY is bypassed for manager document catalog listing

**Release impact:** **NO-GO.**

**Evidence:** `backend/app/api/admin.py:624-646` computes `management` for `SYSTEM_ADMIN` and `WEBSITE_MANAGER` and skips `_enforce_document(...)` for those roles. The endpoint therefore appends document metadata without evaluating document-level ACLs or explicit denies for those roles.

I reproduced this locally using the existing admin fixtures: a `WEBSITE_MANAGER` was given an explicit `DENY` for `document:read`; the ACL update returned `200`, and `GET /api/v1/documents` still returned the denied document ID with `200`.

**Impact:** The manager can still learn that a denied document exists and can receive its catalog metadata. This conflicts with the documented rule that explicit DENY overrides role ALLOW and with the contract that the catalog is policy-filtered. The repro demonstrates metadata exposure; it does not by itself demonstrate source-content exposure.

**Required disposition:** Apply the same effective policy evaluation to catalog visibility for every role, or document and separately authorize a deliberately metadata-only capability. Preserve explicit-deny precedence and add a regression test for the exact manager/system-admin case.

### SEC-002 — HIGH — Citation preview/download does not enforce `expires_at`

**Release impact:** **NO-GO.**

**Evidence:** `backend/app/rag/answer.py:164` creates a five-minute citation expiry and `:307` filters expired citations inside the answer pipeline. But the HTTP citation path in `backend/app/core/chat.py:883-917` retrieves the citation, reauthorizes the document, checks only whether preview/download bytes exist, and returns the artifact; it never checks `artifact.expires_at`. The PostgreSQL repository path `backend/app/db/runtime.py:784-791` reconstructs the citation from the job completion without an expiry check.

The existing citation tests verify expiry during answer construction (`tests/qa/rag_v4_citation/test_e2e_operational.py:133-150`), but the HTTP preview/download path has no equivalent expired-reference test. The existing chat API test verifies revocation reauthorization, not expiry enforcement.

**Impact:** A citation reference that was valid when an answer was produced can remain usable after its intended TTL, subject only to the other checks that still pass. This violates the citation lifecycle expectation and weakens containment of stale source access.

**Required disposition:** Reject expired citations before preview or download, use a timezone-aware comparison, return the existing non-disclosing not-found/forbidden response, and add endpoint tests for both preview and download after expiry.

### SEC-003 — HIGH — Fresh citation authorization falls back to stale artifact state on lookup errors

**Release impact:** **NO-GO for durable/multi-instance deployment.**

**Evidence:** `backend/app/api/chat.py:66-90` refreshes document state from `admin_state` but catches `Exception` and returns the original `CitationArtifact`. `backend/app/core/chat.py:891-908` then builds the PEP resource from that artifact and authorizes it. In the PostgreSQL path, `backend/app/db/runtime.py:784-791` obtains citation data from the job completion rather than the authoritative `answer_citations`/document/ACL state tables.

**Impact:** A restart, state miss, adapter failure, or stale process-local state can cause the citation check to proceed using answer-time metadata. A later ACL revocation, document replacement, tombstone, or policy change may not be reflected reliably. The broad exception also makes the failure mode difficult to distinguish from a legitimate current state.

**Required disposition:** Make authoritative document/version/ACL state durable and tenant-scoped, fail closed when it cannot be read, and reauthorize from that state at preview/download. Add restart, multi-instance, revocation, version replacement, tombstone, and policy-outage tests.

### SEC-004 — HIGH — Identity, ACL/document lifecycle, policy, and related authorization state remain in memory

**Release impact:** **NO-GO for production or any multi-instance claim.**

**Evidence:** `backend/app/api/identity.py:38-41` initializes `InMemoryIdentityStore`; `backend/app/api/admin.py` uses in-memory policy/admin state for identities, grants, document versions, and idempotency. `backend/app/db/runtime.py:3-7` explicitly states that the PostgreSQL adapter persists chat/jobs and the audit sink while identity and document lifecycle remain behind in-memory adapters.

The migrations provide durable tables for tenants, users, memberships, sessions, documents, ACLs, policy delivery, authorized scopes, replay nonces, and audit events, but the current API path does not use those tables as the authoritative authorization source.

**Impact:** Process restart or a second application instance can lose or disagree on users, role changes, ACLs, revocations, document state, and idempotency. Durable chat records can therefore outlive the authorization state that must protect them.

**Required disposition:** Choose and implement one authoritative durable identity/document/policy path before release, including transaction boundaries, tenant scoping, cache invalidation, revocation epochs, and multi-instance tests. Do not represent the current in-memory path as production authorization.

### SEC-005 — HIGH — RAG execution is a local adapter, not the required production worker trust boundary

**Release impact:** **NO-GO for production RAG deployment.**

**Evidence:** `backend/app/rag/runtime.py:87-109` constructs process-local contexts, policy/index state, a fixture document, and a deterministic local model. `:186-225` binds a principal and policy epoch in a local dictionary and runs without signed worker JWT validation, durable authorized-scope lookup, replay nonce handling, or fencing.

The v1 baseline requires signed service identity with issuer/audience/expiry/JTI checks, replay protection, scope validation, and fencing at the worker boundary. The implementation's own local executor design is consistent with a development adapter, not with those production requirements.

**Impact:** Cross-service tenant isolation, policy freshness, worker identity, replay prevention, and revocation cannot be established for a deployed RAG service from this path.

**Required disposition:** Keep this adapter explicitly local-only. Implement the production worker boundary and test signed identity, authorized scopes, policy epochs, replay/fencing, tenant mismatch, timeout, and retry behavior before release.

### SEC-006 — MEDIUM/HIGH — Browser bearer token is stored in `sessionStorage`

**Release impact:** **NO-GO unless accepted as an explicit demo-only boundary.**

**Evidence:** `frontend/src/api/client.ts:153-163` reads and writes the bearer token in `window.sessionStorage`; `:188-194` sends it as an `Authorization` header. `backend/app/api/identity.py:32-39` returns the token in the JSON sign-in response.

**Impact:** Any JavaScript executing in the application origin, including a future XSS or compromised third-party script, can read and exfiltrate the bearer token. The review did not identify an XSS exploit, so this is a hardening and deployment-boundary finding, not a claim that an XSS is present.

**Required disposition:** Prefer an appropriately scoped, secure, HttpOnly cookie/session design with CSRF protection, or explicitly restrict this token model to a controlled demo and document the residual risk. Add CSP, dependency/script provenance, logout/revocation, and token lifetime tests before production.

### SEC-007 — MEDIUM — Audit table has no database-enforced append-only/immutable control

**Release impact:** **NO-GO for audit-grade production evidence.**

**Evidence:** `backend/app/db/migrations/versions/0004_delivery_policy.py:62-84` creates `audit_events` with constraints and indexes, but no trigger, restricted role, row-level policy, append-only view, or database privilege boundary is defined in the migration. `PostgresAuditSink` writes through the application database connection.

**Impact:** A principal that obtains application/DB write capability may alter or delete audit records without a database-enforced immutability boundary. The application path is privacy-aware and no delete route was found in this review, but absence of a route is not equivalent to tamper resistance.

**Required disposition:** Define the audit trust boundary, separate append credentials/roles, enforce append-only semantics at the database or external WORM sink, and test unauthorized update/delete plus retention/export behavior.

### SEC-008 — MEDIUM — Security QA coverage is incomplete or currently drifts from implementation

**Release impact:** **NO-GO for a clean security gate.**

**Evidence from local runs:**

- Backend security API suite: `30 passed`.
- Selected QA security suites otherwise passed their collected cases, including authorization, audit, database, identity, knowledge, RAG, graphify, orchestration, and citation suites.
- `tests/qa/backend_boot/test_security_adversarial.py`: `10/10` passed on the isolated rerun.
- `tests/qa/frontend_boot/test_security_adversarial.py`: `7 passed, 3 failed`.
- The three frontend failures were `test_backend_authorization_is_declared_authoritative`, a blanket `access_token` payload scan, and a blanket `password:` assignment-pattern scan. These appear to be test drift/false positives around the current authentication integration, but they still leave the security gate red until reconciled.
- `tests/qa/ingestion/test_security_adversarial.py` and `tests/qa/model/test_security_adversarial.py` collected `0` tests in the executed invocation; they must not be counted as passing security coverage.

The first broad pytest invocation also encountered duplicate test-module/import collection conflicts; the suites were subsequently run with their supported isolated discovery/import modes. This is a test-harness execution limitation, not evidence of a product vulnerability.

**Required disposition:** Fix or explicitly retire stale/overbroad assertions, make ingestion and model security suites collect real cases, and require a reproducible CI invocation with no collection errors before release.

## Controls that passed within the tested boundary

These results are bounded to the local code/tests and do not override the NO-GO findings:

- Existing authorization logic models explicit deny precedence and default deny.
- Retrieval security tests covered tenant filtering, ACL filtering, current-version filtering, source reauthorization, and policy-outage behavior.
- Audit/privacy tests passed for safe metadata handling and restricted raw payload fields in the tested paths.
- Database baseline tests passed for the presence of durable security tables and expected schema constraints.
- Citation construction tests passed for typed locators, evidence hashes, audience/expiry serialization, and suppression of already-expired citations during answer construction.
- No hard-coded secret value was found by the executed frontend/security checks; the token-storage finding is about runtime handling of a legitimate bearer token, not a committed credential.

## Explicit no-go risks

Do not approve RELEASE-001 while any of the following remain true:

1. A document-level explicit DENY can be bypassed by a role-specific catalog path.
2. Citation preview/download can return an artifact after its `expires_at`.
3. Citation reauthorization can fall back to stale answer-time state or fail open on state lookup errors.
4. Identity, ACL/document lifecycle, and policy state are process-local while chat data is durable.
5. The deployed RAG path lacks the signed worker/scope/replay/fencing trust boundary required by the contracts.
6. The security gate contains failed or zero-collected adversarial suites.

The browser token and audit immutability findings are additional blockers for a production-security claim unless the deployment explicitly narrows the system to a controlled demo and records the accepted residual risk.

## Remediation order for the next handoff

1. Fix SEC-001 and SEC-002 with regression tests.
2. Replace SEC-003's broad exception/stale fallback with authoritative, fail-closed citation state checks.
3. Complete the durable identity/document/policy path in SEC-004 and verify restart/multi-instance behavior.
4. Implement and test the production worker boundary in SEC-005.
5. Close the security-suite collection and drift problems in SEC-008.
6. Decide the accepted browser-session and audit-integrity architecture, then implement the chosen controls for SEC-006 and SEC-007.

## Final handoff state

**RELEASE-001 SECURITY: BLOCKED / NO-GO.**

This is a local review handoff with evidence and remediation direction. It is not a production security certification, and no release completion approval is granted.
