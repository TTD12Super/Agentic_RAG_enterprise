# Non-Functional Requirements — Enterprise Agentic RAG

**Document ID:** NFRD-001  
**Version:** 1.0 — Owner Review Draft  
**Approval status:** `PENDING PROJECT OWNER APPROVAL`  
**Source of requirements:** `GOALS.md`; Project Owner responses to questions 52–77; owner-delegated recommendations for questions 71 and 78–84; and previously agreed MVP boundaries in `functional-requirements.md`.  
**Applies to:** Initial single-enterprise MVP, unless marked `DEFERRED`.

## 1. Purpose, scope, and authority

This document specifies the **quality attributes and operational constraints** the Enterprise Agentic RAG MVP must satisfy: performance, availability, security, resilience, maintainability, cost efficiency, data protection, monitoring, deployment, and quality assurance.

It does **not** select an LLM vendor, cloud vendor, message-broker product, database design, application framework, or detailed algorithms. Those choices belong in Project Owner-approved architecture, ADRs, and contracts. A technology category explicitly requested by the Project Owner (such as **Cloud deployment**, **external LLM API**, and a **prioritized message queue**) is recorded here as a constraint, not an authorization for development agents to choose its implementation.

**Authority and approval:**

- The Project Owner alone approves the resulting requirements baseline and any architecture/contract changes.
- `OWNER`: a decision explicitly stated by the Project Owner. `DELEGATED`: a recommendation the Owner asked the assistant to select; it remains subject to review of this document. `PENDING`: a quantitative or policy decision not yet approved.
- Development agents must not fill `PENDING` requirements with invented values or expand the MVP. They may propose options for separate Owner review.
- Security, correctness, and authorized-source restrictions in `GOALS.md` and the functional requirements remain in force even where this document records a minimal option chosen in a questionnaire.
- Target metrics are **requirements to test**, not claims that the implementation already achieves them.

### 1.1 Requirement notation

`MUST` indicates a mandatory MVP requirement; `SHOULD` indicates a preferred behavior whose absence must be justified and approved; `DEFERRED` is out of MVP scope. Each requirement has a stable ID and a verification approach. Specific thresholds not yet defined appear as **`PENDING`**, not as implicit defaults.

## 2. Performance and user-perceived responsiveness

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-PERF-001** | The chatbot **MUST** offer a smooth and understandable waiting experience. No fixed time-to-first-token target is set for MVP. | UI presents meaningful waiting/processing states; no invented TTFT SLA. | OWNER — Q52.D |
| **NFR-PERF-002** | The **target** processing time for a **simple** question is **under 10 seconds**. | Benchmark records processing duration by question type; pass/fail measurement population and percentile remain `PENDING`. | OWNER — Q53.A |
| **NFR-PERF-003** | The **target** processing time for a **complex** question is **under 30 seconds**. | Benchmark records processing duration for controlled multi-step requests; percentile remains `PENDING`. | OWNER — Q53.A |
| **NFR-PERF-004** | The MVP **MUST NOT** stream answer tokens to the chat UI. It displays a complete answer after response generation finishes. | User does not receive an incremental token stream; processing states may update independently. | OWNER — Q54.B |
| **NFR-PERF-005** | The system **MUST** measure **processing time** separately from **message-queue waiting time** and **maintenance waiting time**. The 10s/30s processing targets exclude queue and maintenance waits, but the user-visible end-to-end latency must also be monitored. | Telemetry reports processing, queue wait, maintenance wait, and end-to-end time separately where applicable. | DELEGATED — earlier performance clarification |
| **NFR-PERF-006** | The MVP **MUST** show `queued`, `processing`, and completed/failed states as applicable, with queue position while queued. | UI states correspond to backend task status; queue position may change under priority scheduling. | OWNER — Q62.C |

**Measurement notes:** Benchmarks must use documented question categories, corpus characteristics, concurrent load, and model/API conditions. Durations from external LLM calls are included in **processing time**; only the time **before processing starts** and explicit **maintenance suspension** are excluded. No percentile (mean/p95/p99), measurement sample size, or load threshold has yet been approved.

## 3. Capacity, scaling, and workload scheduling

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-SCALE-001** | MVP **MUST** support one enterprise deployment and be reusable for a different company's approved data and configuration without substantial code changes. Shared live multi-tenancy is not an MVP requirement. | A documented fresh-deployment process can configure a different enterprise without company-specific source edits. | OWNER — Q58.C |
| **NFR-SCALE-002** | Initial verification **SHOULD** use a corpus of approximately **100 documents**. This is an initial benchmark scope, **not a permanent product limit**. | Test corpus inventory includes document count, formats, sizes and page/row complexity. | OWNER — Q59.D + clarification |
| **NFR-SCALE-003** | The proposed capacity target is **500 concurrent active sessions**, not 500 simultaneous LLM generations; the system **MUST NOT** claim support before load-test evidence. | Load testing records throughput, queue times, failures and latency at the declared 500-session profile. | OWNER proposal — Q17 |
| **NFR-SCALE-004** | A **message-queue-based** workload scheduler **MUST** support more than one question being processed concurrently and prioritize **Chairman** requests over **Internal User/Employee** requests. | Under a controlled workload, eligible Chairman requests receive the approved scheduling preference without bypassing authorization. | OWNER — Q56, Q61.B |
| **NFR-SCALE-005** | Scheduling **MUST** preserve authorization context and isolate one user's results from another's, including across queueing, execution, retries, and resume. | Concurrent mixed-role tests reveal no cross-user or PUBLIC/INTERNAL disclosure. | Inherited security goal |
| **NFR-SCALE-006** | The system **MUST** expose queue status/position without promising a fixed position under a priority scheduler. | Updated positions are labeled as estimates or current position, rather than guaranteed completion order. | OWNER — Q62.C; derived consistency |

**Owner-provided scheduling proposal:** Priority is Chairman > Website Manager/System Admin > authenticated employee > anonymous, with weighted scheduling, 60-second aging, per-user/tenant rate limits, 20 concurrent RAG tasks, 2 ingestion tasks and 200 waiting query jobs. PostgreSQL-backed leasing is proposed; load validation and cloud autoscaling remain pending.

## 4. Planned maintenance and document publication

Uploading documents is an administrative action. The Project Owner has explicitly required the **entire chatbot to pause** while the upload, processing, and required approval workflow completes. This has an intentional availability impact and must not be silently replaced by zero-downtime ingestion.

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-MAINT-001** | When an authorized Admin begins the document-upload maintenance workflow, the chatbot **MUST** enter **Maintenance Mode** and stop accepting new chat work until the workflow is finished or safely aborted. | New chat requests receive a clear maintenance state and do not start normal processing. | OWNER — Q57, Q63.A |
| **NFR-MAINT-002** | Questions already in progress **MUST** be **logically paused and resumable** after maintenance, without losing their authorization identity or returning an incomplete/incorrect response. | In-flight and queued task tests show safe pause/resume around maintenance. | OWNER — Q74.C |
| **NFR-MAINT-003** | Maintenance **MUST** remain active through both administrative review stages and processing; a new document **MUST NOT** become searchable before final approval and activation. | Pending/rejected material is unavailable to retrieval; chatbot resumes only after a valid completion/abort transition. | OWNER — Q15, Q57, Q63.A |
| **NFR-MAINT-004** | On upload/ingestion failure, the system **MUST** record and surface the failure and provide a safe path to cancel/abort the operation and restore chatbot availability without publishing failed content. | Simulated processing failure does not cause an indefinite unmanageable maintenance lock. | OWNER — Q75.D |
| **NFR-MAINT-005** | Maintenance and task state transitions **MUST** be traceable to approved administrative operations and safe from unauthorized control. | Non-admin maintenance commands are denied; event records show who triggered and ended maintenance. | Security goal; OWNER flow |

**Design caveat:** An external LLM API call generally cannot be paused mid-request and resumed at the exact same token. The proposal allows a call to finish for up to 60 seconds, then checkpoints/cancels safely and repeats only an idempotent read-only step. PostgreSQL is the proposed durable checkpoint store; approval waits 30 minutes and maintenance has a configurable 60-minute watchdog. Provider-specific behavior still requires an approved ADR.

## 5. Security, identity, and protection against abuse

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-SEC-001** | All protected operations and evidence retrieval **MUST** enforce current backend authorization; the LLM and frontend **MUST NOT** determine privileges. | Role/department/document deny tests pass across retrieval, citations, cache, and source-opening paths. | `GOALS.md`; OWNER — Q65.A, Q67.D |
| **NFR-SEC-002** | Anonymous sessions **MUST** be restricted to approved `PUBLIC` information; authenticated users may access only authorized `INTERNAL` content. | Negative tests for prompt, direct identifier, cache and queued request access do not expose unauthorized content. | Functional requirements |
| **NFR-SEC-003** | API traffic **MUST** be protected in transit (HTTPS/TLS); protected persistent data **MUST** be encrypted at rest. | Deployment review verifies in-transit and at-rest controls in applicable services. | OWNER — Q66.C |
| **NFR-SEC-004** | Passwords, secrets, tokens, LLM API keys and other credentials **MUST** be handled through approved secure storage/configuration and **MUST NOT** be committed to Git or emitted in ordinary logs. Passwords must be stored with appropriate one-way password hashing rather than reversible encryption. | Repository/configuration scans and authentication tests verify secret hygiene. | OWNER — Q66.C; security baseline |
| **NFR-SEC-005** | **Chairman**, **System Admin** and **Website Manager** accounts **MUST** use MFA in addition to approved email/password authentication. Employee activation follows request plus administrator approval; MVP does not require SSO. | Privileged accounts cannot access protected functions without the required second factor. | Owner proposal — Q2/Q28 |
| **NFR-SEC-006** | The system **MUST** implement backend authorization and safeguards against prompt injection and abusive requests; suspicious incidents **MUST** be detectable and recorded without exposing protected data in logs. | Defined injection/unauthorized-tool/privilege-escalation tests are denied or safely handled. | OWNER — Q67.D |
| **NFR-SEC-007** | Agent tool execution **MUST** remain read-only with respect to business data, allowlisted, bounded and authorized. No LLM output may directly authorize side-effecting actions. | Unauthorized or write-capable tool attempts are rejected. | `GOALS.md`; functional scope |
| **NFR-SEC-008** | MVP **MAY** pass **authorized retrieved excerpts** to approved external LLM APIs. There is **no additional mandatory sensitive-field redaction workflow in MVP**, but data transfer remains subject to the company's approved provider/data-handling policy. | Review confirms only authorized contextual excerpts are sent, destinations are approved and data-sharing implications are documented. | OWNER — Q64.A |
| **NFR-SEC-009** | The system **MUST** re-evaluate permissions when serving cached answers, original document links, and resumed queued jobs, including after account/document revocation. | Revoke-access tests block stale cached evidence or resumed unauthorized jobs. | `GOALS.md`; functional access requirements |

**External-API data risk:** Q64.A permits sending authorized internal excerpts off-platform; it does **not** establish a provider contract, data residency, training/retention terms, or consent policy. The enterprise must approve the permitted provider and data handling before using real confidential documents. Detailed controls belong in `docs/security/` and the model-provider ADR.

## 6. Privacy, provenance, and data lifecycle

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-DATA-001** | An authenticated user **MUST** be able to access only their own saved conversation history, except for separately authorized incident/administrative metadata; ordinary admin rights do not automatically allow reading other users' private conversation bodies. | Cross-account conversation-read tests are denied. | OWNER — Q69.A |
| **NFR-DATA-002** | Anonymous chat history **MUST** be scoped to the visitor's temporary session and must not silently become a persistent employee account history. | History from one anonymous session is not exposed to another. | Functional requirements |
| **NFR-DATA-003** | Answer evidence/provenance **MUST** remain traceable to the approved document and version; citations may be hidden by default in the UI but **MUST** be available on request to authorized users. | Source expansion/opening validates current permission and active source version. | OWNER — Q49.A; `GOALS.md` |
| **NFR-DATA-004** | Deleted/revoked/superseded documents **MUST NOT** be returned by retrieval, cached answers, or direct source links once revocation takes effect. | Invalidation and negative retrieval tests pass after lifecycle change. | Functional document lifecycle |
| **NFR-DATA-005** | Operational logs, analytics and LLM diagnostics **MUST** minimize sensitive content and restrict log access by authorized role. | Review shows no unnecessary passwords, API keys, full confidential documents or raw private conversations in ordinary telemetry. | Security and privacy baseline |
| **NFR-DATA-006** | The system **MUST** have a documented retention/deletion policy before production. Owner-proposed values are authenticated conversations 180 days, anonymous session 30 minutes idle/24 hours max, anonymous conversations 7 days, superseded versions 365 days, soft delete 30 days, audit 2 years, application logs 30 days, backups 30 days and feedback 180 days. Legal hold overrides. | An approved policy exists; deletion, tombstone and backup behavior is testable against it. | Owner proposal — Q9 |

Document lifecycle must retain the Owner's **Soft Delete** and **Permanent Delete** distinction. Permanent deletion behavior in backups and audit trails requires a separate approved data-retention policy; no silent assurance of instantaneous deletion from every backup is made here.

## 7. Reliability, failure handling, and backup/recovery

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-REL-001** | On transient LLM API failure, the system **MUST** attempt bounded retry and then use an **approved fallback model/provider** when possible. | Simulated primary-provider failure yields controlled retry/fallback, or a clear error when all options fail. | OWNER — Q72.D |
| **NFR-REL-002** | If an ordinary Agentic RAG task fails and the approved LLM-specific recovery path cannot resolve it, the user **MUST** receive an understandable failure and be asked to retry. | An unrecoverable workflow error does not produce fabricated success or misleading completed state. | OWNER — Q73.A |
| **NFR-REL-003** | Maintenance-related pause/resume is a **specific exception** to NFR-REL-002 and must preserve task state across an approved maintenance window. | A test pauses a valid question and resumes it safely after maintenance. | OWNER — Q74.C |
| **NFR-REL-004** | The platform **MUST** create **periodic backups of the authoritative database and uploaded document files** and maintain a documented recovery procedure. | Backup schedule and restore steps are documented and backup artifacts are observable. | OWNER — Q76.B |
| **NFR-REL-005** | The recovery strategy **MUST** prioritize minimizing enterprise data loss. Proposed targets are **RPO ≤1 hour** and **RTO ≤4 hours**, and must be demonstrated by restore drills before guarantees. | Documented recovery plan identifies protected datasets, expected paths and measured RPO/RTO. | Owner proposal — Q32 |
| **NFR-REL-006** | The system **MUST** handle ingestion failure and cache/index publication failures without exposing unapproved document versions or leaving an unresolvable maintenance state. | Failure-injection tests keep only approved data available after safe recovery. | OWNER workflow/security goal |

**Boundary:** The proposal sets primary retry to at most two transient attempts, then an approved fallback; PostgreSQL daily base backup plus WAL/PITR; 30-day backup retention and quarterly restore drills. Provider, topology and final HA behavior remain pending approval.

## 8. Availability and cloud deployment

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-AVAIL-001** | MVP **MUST** be operable and monitored, but has **no fixed monthly uptime SLA** yet. Availability must be measured before an SLA is proposed. | Uptime/downtime reports distinguish scheduled maintenance from unplanned outages. | DELEGATED — Q71.A |
| **NFR-AVAIL-002** | Authorized document-upload maintenance **MUST** be visible as planned chatbot unavailability and accurately communicated to users. | During maintenance, chat requests show an explicit unavailable/maintenance state. | OWNER — Q63.A |
| **NFR-DEP-001** | Deploy the application on **Cloud infrastructure**, using **external LLM API services**, not mandatory self-hosted LLM inference in MVP. | Deployment documentation identifies cloud components and approved external API dependencies. | OWNER — Q60 |
| **NFR-DEP-002** | Configuration **MUST** be externalized from application code, using approved configuration files and environment variables; secrets must use protected storage rather than committed files. | An environment can be configured without source modifications or embedded secrets. | DELEGATED — Q84.A |
| **NFR-DEP-003** | Different development, testing and production configurations **MUST** be supportable without source edits, although separate full cloud environments are not automatically required for MVP. | Deployment manifests or runbooks identify environment-specific settings. | DELEGATED — Q84.A clarification |
| **NFR-DEP-004** | Deployment, rollback, incident response, and recovery procedures **MUST** be documented before production operation. Actual cloud vendor, infrastructure topology and rollout process require approval. | Runbooks cover deployment, failure response and rollback at an operational level. | `GOALS.md`; operations requirements |

## 9. Cost optimization and maintainability

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-COST-001** | The system **MUST** support routing simple questions to an approved lower-cost LLM path and complex questions to an appropriate higher-capability path when needed. | Tests demonstrate policy-based routing without relying on a single expensive default path for all requests. | DELEGATED — Q78.D |
| **NFR-COST-002** | The system **MUST** minimize unnecessary LLM API token usage by limiting supplied context to relevant, authorized evidence while preserving answer quality. | Token usage and answer quality are measured on representative Golden Dataset questions. | DELEGATED — Q78.D |
| **NFR-COST-003** | The MVP **MUST** support permission-aware **retrieval caching** and **identical-question/answer caching** where safe; semantic similarity caching is `DEFERRED`. | Cache tests show reusable results for qualifying requests and no unauthorized/stale reuse. | DELEGATED — Q79 (B + invalidation) |
| **NFR-COST-004** | Cache entries **MUST** be invalidated or bypassed when source documents, versions, permissions or relevant generation policies make them stale. | Updated/revoked content cannot be served through old cache entries. | DELEGATED — Q79; security requirement |
| **NFR-COST-005** | The integration boundary **MUST** support multiple external LLM API providers, including approved fallback paths, without forcing product-level changes to each consuming module. | Provider substitution/fallback is demonstrated with an approved test double or configured provider. | DELEGATED — Q80.C; OWNER — Q72.D |
| **NFR-COST-006** | Admin observability **MUST** report token usage and estimated API cost by model, task type and day/week/month where provider telemetry permits. No per-user token quota is required in MVP. | Cost dashboards reconcile available usage records and label estimated values appropriately. | DELEGATED — Q81.C; functional dashboard |
| **NFR-MAIN-001** | Company-specific document collections, department definitions, user data and basic enterprise configuration **MUST** be changeable without editing core source code. | A fresh company deployment is configured through data and approved configuration, not hard-coded company rules. | DELEGATED — Q82.B |
| **NFR-MAIN-002** | Major functional components **MUST** be modular and interact through versioned/approved interfaces/contracts so that LLM or retrieval components can be replaced without broad rewrites. | Contract checks and architecture review identify documented component boundaries. | DELEGATED — Q83.D |
| **NFR-MAIN-003** | Runtime behavior that materially changes permissions, document visibility or allowed tools **MUST NOT** be changed by ad hoc environment settings without approved review. | Configuration/security tests reject or flag unsafe settings. | Owner-governed system design |

Cost efficiency is an optimization **subject to correctness, security, authorization and answer-quality gates**. The MVP does not implement per-account token allocation, budget resets, or usage blocking; those are `DEFERRED` product features.

## 10. Observability, audit and operational notifications

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-OBS-001** | Audit records **MUST** cover authentication/security events and document upload, approval, update and deletion with attributable actor, outcome and time where applicable. | Representative security and document actions emit reviewable events. | OWNER — Q40.B |
| **NFR-OBS-002** | **System Admin** may inspect authorized system-level logs; **Website Manager** may inspect business-administration audit logs, without automatically gaining developer-only diagnostic access. | Permission tests distinguish the roles' log visibility. | OWNER — Q41.B |
| **NFR-OBS-003** | Dashboard **MUST** provide available counts and operational measurements for users, documents, chat requests, ingestion states, failures, token/cost usage, cache hit rate, latency and evaluation results. | Authorized management UI shows the available measurements with units and measurement periods. | OWNER — Q42.D |
| **NFR-OBS-004** | Observability **MUST** be sufficient to correlate a question/task with queueing, retrieval, model request, fallback, maintenance and completion/error at an operational level without exposing internal LLM reasoning or unnecessary confidential text. | Diagnostic review can identify failure stage using non-sensitive identifiers/events. | Supporting implementation quality |
| **NFR-OBS-005** | Severe incidents **MUST** produce dashboard alerts and **system-generated email notifications**, including ingestion failure, LLM service unavailability and major security events according to approved alert rules. | Tests trigger an operational notice to approved recipients without granting autonomous email capability to AI agents. | OWNER — Q45.D, Q70.B |
| **NFR-OBS-006** | Admin-visible quality results **MUST** distinguish measured Golden Dataset evaluation results from unverified quality claims. | Dashboard labels dataset, evaluation version, timestamp and evaluated measure where supported. | OWNER — Q44.B |

Audit trails (accountability) and diagnostic telemetry (operations/performance) are different data classes. The selection of Q40.B does **not** mandate storing full user prompts, full model outputs or every agent step in a permanent audit log. Event schema, recipient lists, retention periods and access details remain contract/security design decisions.

## 11. Testing, evidence, and release quality

| ID | Requirement | Verification / acceptance | Basis |
|---|---|---|---|
| **NFR-QA-001** | RAG quality **MUST** be evaluated using an approved **Golden Dataset** that tests retrieval and answer quality. | Reproducible evaluation produces per-measure results with dataset/model/configuration identification. | OWNER — Q44.B |
| **NFR-QA-002** | MVP test coverage **MUST** include correct PUBLIC/INTERNAL separation, Chairman access, department/document ACLs, revocation, session privacy and agent/tool authorization. | Security test suite includes allowed and denied scenarios; required security gates pass. | `GOALS.md`; owner authorization policy |
| **NFR-QA-003** | Functional and integration testing **MUST** cover document two-stage approval, latest ACTIVE version, maintenance pause/resume, ingestion failure, queue priority, retries/fallback, caching and source opening. | Tests exercise normal and failure paths before the feature is declared ready. | Owner-approved functional/NFR behavior |
| **NFR-QA-004** | Performance/capacity claims **MUST** be supported by benchmark reports identifying corpus size/complexity, question mix, load, model settings, cloud conditions and measurement definition. | Evidence is linked from an approved review/task; untested capacity figures are not represented as verified. | OWNER — Q55.E, Q59.D |
| **NFR-QA-005** | The delivery process **MUST** keep implementation requirements traceable to tests and approved tasks; approval gates remain under Project Owner control. | Tasks reference requirement IDs and verification evidence; no agent self-approves a design or release. | Owner governance |
| **NFR-QA-006** | The MVP **MUST** not claim zero hallucinations or absolute security; insufficient-evidence behavior and known limitations must be documented and testable. | Evaluation includes unsupported questions and security-negative cases. | `GOALS.md` |

**Not required yet:** Automatic scheduled evaluation, CI/CD evaluation on every commit, advanced ML quality dashboards, and an unapproved numeric quality threshold. Detailed metrics and acceptance thresholds must be approved in `docs/rag/evaluation-plan.md` and `docs/testing/quality-gates.md`.

## 12. MVP exclusions and deferred enhancements

The following are **not part of the approved MVP scope** and must not be added by development agents without a change request:

- Per-account **token quota assignment**, token reset periods, out-of-quota rules, and an anonymous quota product feature. **Token/cost reporting remains in scope.**
- Similarity-based/semantic **answer caching** beyond safe exact-question caching.
- Live shared **multi-tenant administration**, advanced autoscaling, and a contractual uptime SLA.
- Self-hosted LLM serving as a mandatory deployment mode.
- Admin screens to freely change models, retrieval policies or infrastructure configuration; configuration is handled through approved deployment settings initially.
- Automatic scheduled/CI RAG evaluation unless separately approved.
- Runtime multi-agent collaboration, production GraphRAG, CRM/ERP live integrations, autonomous agent email sending or autonomous AI document modification/deletion (as excluded by `GOALS.md`).

## 13. Open decisions and design dependencies

The table below identifies matters that are **not approved merely because an implementation is technically possible**.

| ID | Remaining decision (`PENDING`) | Why it must be resolved |
|---|---|---|
| **P-NFR-01** | Define performance measurement percentile/sample, load conditions, and what qualifies as `simple` versus `complex`. | Makes 10s/30s targets objectively testable. |
| **P-NFR-02** | Set concurrent-user/throughput acceptance target after baseline benchmark. | Prevents invented scale guarantees. |
| **P-NFR-03** | Define priorities for Anonymous User, Website Manager and System Admin; fairness, queue capacity and processing concurrency limits. | Completes priority scheduler behavior. |
| **P-NFR-04** | Approve maintenance checkpoint/resume semantics, in-flight LLM API handling, pause duration and stalled-admin/review recovery. | Makes full-chat maintenance safe and technically implementable. |
| **P-NFR-05** | Select/approve message broker and durable workload execution architecture through an ADR. | Implementation technology and state behavior cannot be selected by agents. |
| **P-NFR-06** | Approve cloud vendor, deployment topology, regions and provider/data-handling terms for external LLM API. | Needed for real confidential enterprise data. |
| **P-NFR-07** | Set LLM retry count/backoff/timeouts, fallback order and permitted models/providers. | Makes error-handling deterministic and cost-bounded. |
| **P-NFR-08** | Approve backup cadence, recovery procedure details, numeric RPO/RTO and backup retention. | Makes recovery objectives testable. |
| **P-NFR-09** | Approve chat/log/document/backup retention and permanent-deletion effects, including privacy roles. | Prevents inconsistent data lifecycle behavior. |
| **P-NFR-10** | Approve Golden Dataset, quality metrics, thresholds and security release gates. | Allows objective owner acceptance. |
| **P-NFR-11** | Define incident severity, email recipients, alert noise limits and escalation. | Prevents noisy, unauthorized or missing alerts. |
| **P-NFR-12** | Define cost accounting accuracy, rate tables and cost-reporting source of truth. | Distinguishes usage estimates from billed provider amounts. |

Where one of these is required to implement a feature safely, **block that dependent implementation task** until the applicable decision has been approved. A `PENDING` row does not block unrelated work.

## 14. Traceability and approval

**Requirements flow:**  
`GOALS.md → Functional Requirements → Non-Functional Requirements → Owner-approved Architecture / ADRs → Contracts → Tasks → Tests → Owner Acceptance`

**Related documents:**

- `functional-requirements.md` (intended repository path: `docs/requirements/functional-requirements.md`)
- `docs/architecture/overview.md`
- `docs/architecture/workflows/admin-ingestion.md`
- `docs/architecture/workflows/user-query.md`
- `docs/contracts/identity-and-policy.md`
- `docs/contracts/retrieval.md`
- `docs/contracts/answer-and-citation.md`
- `docs/contracts/events-and-audit.md`
- `docs/security/threat-model.md`
- `docs/security/authorization-matrix.md`
- `docs/rag/evaluation-plan.md`
- `docs/testing/quality-gates.md`
- `docs/operations/deployment-runbook.md`
- `docs/operations/incident-response.md`
- `harness/tasks/tasks.json` — sole authoritative task-state file.

**Project Owner approval:** `PENDING`  
**Approved baseline:** None yet  
**Next step:** Review owner/delegated selections, resolve high-impact architectural prerequisites, and explicitly approve the baseline before dependent implementation work.

## 15. Owner-provided proposal alignment

The Q1–Q34 proposal baseline is recorded in [`owner-decision-baseline.md`](owner-decision-baseline.md). It supplies proposed values for upload limits, retention, queue behavior, maintenance checkpoints, API conventions, security controls, recovery targets and load/evaluation profiles. The following remain conditional and are not yet production guarantees:

- Cloud provider, region and data-residency boundary.
- Primary/fallback LLM providers and provider retention terms.
- Confirmation of the 500-concurrent-session definition.
- Benchmark approval of latency, cost and quality thresholds.
- Actual incident alert recipients.
- Evidence that the 60-minute maintenance ceiling is sufficient for 200 MB/OCR/XLSX workloads.

## 16. Student deployment boundary

Vercel + Azure for Students or Vercel + Oracle Always Free may be used for development and controlled demos. These profiles MUST NOT be treated as satisfying production availability, backup, compliance, data-residency, performance or 500-session requirements. External LLM usage remains separately metered and governed.
