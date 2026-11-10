# System Architecture Overview — Enterprise Agentic RAG

**Document ID:** ARCH-OVERVIEW-001  
**Status:** APPROVED MVP ARCHITECTURE BASELINE — Project Owner approval recorded 2026-11-10  
**Version:** 0.2  
**Date:** 2026-11-09  
**Scope:** Single-enterprise MVP, designed for reuse in separate enterprise deployments

> This document defines the **proposed system structure, responsibilities, runtime boundaries, and critical workflows**. It does not authorize implementation or replace detailed ADRs, API contracts, database schemas, security policies, deployment specifications, or owner-approved Figma designs.

## 1. Sources, governance, and decision status

This draft incorporates the current `GOALS.md` supplied by the Project Owner, `docs/requirements/functional-requirements.md`, `docs/requirements/non-functional-requirements.md`, and later architecture directions from the Project Owner (Rust exploration, React + TypeScript, independent workers, and a 500-user capacity target).

- **OWNER-CONFIRMED:** A product or architectural direction explicitly selected by the Project Owner.
- **PROPOSED:** A technical recommendation awaiting review, benchmarking, or an ADR.
- **PENDING:** A decision that must not be made autonomously by implementation agents.
- Only the Project Owner may accept architectural decisions or authorize implementation. The Main Agent and development subagents may research, propose, and implement **approved** decisions, but do not approve their own designs.
- All pre-existing ADRs (`ADR-0001`–`ADR-0005`) remain **Proposed** until explicitly accepted. Conflicting sections require revision, not silent reinterpretation.

## 2. Product boundaries and confirmed architecture directions

| Area | Direction | Status |
|---|---|---|
| Product | Enterprise document-grounded chatbot with administration, secure retrieval, and basic Agentic RAG | OWNER-CONFIRMED |
| Deployment model | One enterprise per MVP deployment; reuse for another enterprise by replacing approved configuration, users, permissions, and document collection | OWNER-CONFIRMED |
| Backend architecture | **Modular Monolith Core + independent RAG and ingestion workers**; not 17 microservices | OWNER-CONFIRMED |
| Backend Core language | Use Python/FastAPI for the MVP modular monolith; benchmark Rust as a later replacement candidate | OWNER-PROVIDED PROPOSAL — Rust is not yet approved |
| Rust web/runtime libraries | Axum + Tokio | PROPOSED; no framework approval yet |
| Frontend | React + TypeScript; chat-first user experience; owner designs and approves Figma | OWNER-CONFIRMED |
| RAG/Agentic engine | Python workers; Advanced Hybrid RAG baseline, then bounded single-agent LangGraph workflows | OWNER-CONFIRMED direction; detailed methods PENDING |
| Ingestion | Independent Python worker(s) for PDF, Word, Excel | PROPOSED implementation of approved functions |
| Model access | Cloud-hosted product; LLMs are consumed through external API(s), with bounded retry and approved fallback | OWNER-CONFIRMED |
| Work scheduling | PostgreSQL-backed durable queue with leases, heartbeat, weighted Chairman-first priority and aging | OWNER-PROVIDED PROPOSAL — load validation pending |
| Corpus sizing | About **100 documents** initially; benchmark scaling instead of imposing an arbitrary product limit | OWNER-CONFIRMED |
| Capacity objective | **500 concurrent active sessions**, 30 queries/minute sustained and 60 queries/minute for a five-minute burst | OWNER-PROVIDED TARGET — capacity proof pending |
| Document publication | Two administrative reviews; only latest approved `ACTIVE` version served | OWNER-CONFIRMED |
| Upload maintenance | Any administrator document upload starts chatbot-wide maintenance until processing and final review/approval or safe cancellation/failure completion | OWNER-CONFIRMED |
| Existing questions during maintenance | Preserve and safely resume in-flight question jobs after maintenance | OWNER-CONFIRMED |
| UX response | No token streaming; display queue position, processing status, and final answer; source details hidden until expanded | OWNER-CONFIRMED |

**Important capacity interpretation:** The owner-provided proposal defines 500 users as **500 concurrent active sessions**, not 500 simultaneous LLM generations. This remains a load-test target, not a demonstrated benchmark or SLA.

## 3. Logical architecture and runtime deployment boundaries

```text
                         React + TypeScript Web Application
              Anonymous Chat | Employee/Chairman Chat | Admin UI
                                        |
                                  HTTPS / WAF*
                                        |
                   +-----------------------------------------+
                   | PYTHON/FASTAPI MODULAR MONOLITH CORE  |
                   | API / Identity / Authorization (PDP)    |
                   | Admin / Document Lifecycle / Chat Jobs  |
                   | Maintenance / Queue Coordination / Audit|
                   +-------------------+---------------------+
                                       |
                           Trusted job + policy interfaces
                                       |
                     +-----------------+------------------+
                     |                                    |
               Priority Queue*                       Admin ingestion jobs
                     |                                    |
            +--------+---------+                   +------+--------+
            |                  |                   |               |
      Python RAG Worker   Python RAG Worker   Python Ingestion Worker(s)
            |                  |                   |
      Retrieval + AuthZ   Basic LangGraph      Extract / Chunk / Embed
      Tools + Reranking   LLM Routing          Validate / Stage Index
            |                  |                   |
            +--------+---------+-------------------+
                     |
         +-----------+------------+-------------------+
         |                        |                   |
   Metadata/Policy DB*       Vector/Search DB*    Object Storage*
         |                        |                   |
   Identity/ACL/Version     Approved/staging      Original documents
   Job/Conversation/Audit   document indexes      and controlled artifacts
         |
   Cache/Job State Store*  <---- approved, scoped cache/checkpoint strategy
         |
   Observability / audit / alerts across all processes

   * Exact technology, topology and implementation remain subject to ADRs.
   External LLM APIs are called only through the approved Python model gateway.
```

The proposed monitoring plane is OpenTelemetry → Prometheus/Grafana/Alertmanager, with a provider-dependent redacted trace/log backend. It is private, role-limited and operational only; it cannot grant application access or store raw document/conversation content. The implementation is tracked by `INFRA-003`.

**Deployment shape:** A single logical Python/FastAPI backend application may have multiple **replicas** for capacity. Python RAG and ingestion worker processes scale independently within approved limits. Replicas and workers do **not** turn business modules into separately designed microservices. The future Rust benchmark must communicate through the same approved contracts and must not import worker implementation modules.

## 4. The original 17 logical blocks — revised responsibility map

These are **logical capabilities, not 17 network services**. Proposed target directories are illustrative and must be reconciled with actual repository structure before any move or code change.

| Block | Capability | Proposed implementation boundary |
|---|---|---|
| 01 | Presentation | `frontend/` — React/TypeScript, approved Figma |
| 02 | API & Identity | Python/FastAPI Core: `api`, `identity`, `sessions` |
| 03 | Authorization | Python/FastAPI Core trusted policy decision/enforcement service; workers recheck through approved trust interface |
| 04 | Security & Guardrails | Core request controls; Python retrieval/context/output safeguards |
| 05 | Agent Orchestration | Python RAG Worker: bounded LangGraph, read-only tools |
| 06 | Model Management | Python model gateway: approved routing, retries, fallback, usage accounting |
| 07 | Prompt Management | Python versioned prompt runtime; approved instructions and data separation |
| 08 | RAG Engine | Python: authorization-filtered hybrid retrieval, fusion, optional reranking |
| 09 | Evidence Verification | Python: evidence checks and provenance; Core reauthorizes source access |
| 10 | Knowledge Management | Python/FastAPI Core: document metadata, collections, permissions and administration |
| 11 | Document Lifecycle | Python/FastAPI Core: review/publish controls; Python ingestion workers: processing/indexing |
| 12 | Data Governance | Python/FastAPI Core: classification (`PUBLIC`/`INTERNAL`), departments, policy and lifecycle controls |
| 13 | Memory & Caching | Core/Python through approved state/cache interfaces; no cross-user or stale-policy reuse |
| 14 | Integration Layer | Typed Core–worker job/result contracts and external API adapters |
| 15 | Observability & Audit | Shared instrumentation, Core-owned administration/audit visibility and operational alerts |
| 16 | Evaluation & Feedback | Python RAG evaluation; Core API for feedback and authorized dashboard access |
| 17 | Infrastructure & LLMOps | `infra/`: cloud deployment, secrets, monitoring, CI/CD, performance/load testing |

The original block specifications in `docs/architecture/blocks/` remain important inputs. Their current Python repository ownership remains valid for the MVP; a later Rust replacement would require benchmark evidence, an ADR and a migration plan.

Downloadable Mermaid source for the overall system and all 17 block diagrams: [`diagram.md`](../../diagram.md). A rendered FigJam copy is available in the linked board in that file.

## 5. Identity, roles, authorization, and trust boundaries

- **Anonymous External User:** no sign-in; public chatbot only; reads published `PUBLIC` evidence; chat history is temporary and session-scoped.
- **Internal Employee:** admin-provisioned account, email activation and email/password sign-in; can read published `INTERNAL` content according to department and per-document permissions and their own saved conversations.
- **Chairman:** employee chat capabilities plus read access to all approved company documents across departments; **no implicit upload, deletion, approval, or developer privileges**.
- **Website Manager:** user/document business administration, including upload, both reviews, publishing, versioning, permission management and business audit visibility.
- **System Admin:** same business management capabilities as Website Manager, plus **separately specified** developer/system operations.
- **Chairman, Website Manager and System Admin use MFA.** SSO, public registration of employees and per-account token quotas are outside this MVP.

Two top-level document classifications: `PUBLIC` and `INTERNAL`; internal documents include department information and document-specific access rules. Do not infer department grants, ACL precedence, Chairman exceptions, or administrator technical permissions beyond an approved authorization matrix.

**Authoritative policy:** Only the trusted Python/FastAPI Core policy service in the MVP decides access. The LLM, browser, vector index, cached answer, queue message, and retrieved document text cannot grant privilege. Verify identity and authorization when accepting a job, retrieving each evidence set/source, expanding source citations, serving a cached response, and resuming or delivering a queued job. Stale policy, inactive source, missing principal or policy-service failure must fail closed.

**Inter-process trust:** Jobs carry trusted identifiers, scoped policy references and trace/correlation IDs; **client-supplied roles and document IDs are not authorization proof**. Python workers obtain current decisions through the approved Core trust interface; the exact implementation remains a contract/security review item. Read-only tools require typed arguments, server-side validation and independent authorization checks.

## 6. User question flow (chat data plane)

1. React chat sends a question. Anonymous questions are restricted to public content; authenticated requests use verified server-side identity.
2. The Python/FastAPI Core validates request/session, enforces relevant access and abuse controls, and checks the global maintenance state.
3. If maintenance is active, new chat work is not processed; the UI shows an explicit maintenance state. Existing approved work is paused for later continuation.
4. Otherwise, create an auditable question job; place it into the approved priority queue. The UI can show `QUEUED`, queue position and `PROCESSING`; positions may change as higher-priority work arrives.
5. The scheduler favors Chairman jobs, then Website Manager/System Admin, then authenticated employees, then anonymous users, while supporting multiple concurrent workers. The proposal adds 60-second aging, per-user/tenant limits, 20 RAG workers, 2 ingestion workers and 200 waiting query jobs; load validation remains pending.
6. A Python worker revalidates the authorized scope. Check **permission-aware** retrieval and identical-question/answer caches against current source versions and access rules.
7. For a simple question, use standard Advanced Hybrid RAG and an approved lower-cost LLM path. For an eligible complex question or insufficient first retrieval, invoke **bounded single-agent LangGraph** with read-only retrieval tools. No multi-agent runtime, autonomous email, or autonomous document edits.
8. Retrieval uses approved dense + lexical search, with authorization filters in **every** retrieval branch, then approved fusion, optional reranking and a second authorization check when fetching source content. Embeddings or index metadata do not replace the authoritative policy store.
9. Only authorized, approved, latest `ACTIVE` document versions form the context. Retrieved text is untrusted data, never system instructions. The Python model gateway sends only authorized relevant excerpts to **approved external LLM APIs**, with bounded retry and approved fallback on provider failure.
10. Verify answer provenance and current permissions. If evidence is insufficient, report it rather than inventing company facts; if partially supported, return only the supported part and identify the gap. Record source references for on-demand viewing.
11. The result is delivered **in full, without token streaming**. The UI shows the final answer with an optional collapsed source section; opening original documents rechecks current authorization. Update permitted conversation history, usage telemetry and audited events.
12. If normal workflow processing fails irrecoverably, return a clear failure and let the user resubmit. **Maintenance resume is a separate exception** and must preserve progress or safely replay an unfinished read-only step.

## 7. Document upload, approval, publication, and maintenance

**Only Website Manager and System Admin can upload and administer documents.** MVP formats are `.pdf`, `.docx` and `.xlsx`, with a 200,000,000-byte limit; `.doc` and `.xls` are rejected. Scanned PDFs use Vietnamese/English OCR within parser/page limits.

```text
Admin requests upload
  -> Enable global chat maintenance; stop admitting new chat work
  -> Quiesce/checkpoint existing RAG question jobs (do not lose them)
  -> Store submitted file in restricted, non-searchable intake
  -> Admin review #1: approve/reject document for processing
  -> Python ingestion: validate -> extract -> chunk -> embed -> staging index
  -> Validate extracted content, ownership, metadata, source spans and permissions
  -> Admin review #2: approve/reject processed result
  -> On approval: publish latest approved ACTIVE version atomically
  -> Invalidate affected retrieval/answer caches
  -> On rejection/failure/cancel: preserve former ACTIVE version; log reason
  -> End maintenance safely -> recheck identity/policy -> resume paused jobs
```

- No uploaded, staged, rejected, failed, superseded, soft-deleted or permanently deleted document may become chatbot evidence. Ordinary chat reads only the current authorized `ACTIVE` version.
- Review #1 and #2 are distinct decisions; the owner-provided proposal allows the same administrator to approve both stages.
- Document management supports version history, metadata/ACL updates, **Soft Delete** and administrator-controlled **Permanent Delete** subject to approved retention safeguards.
- A failed upload/ingestion must not permanently lock the chatbot. The administrator must be informed; safe cancellation or fault completion releases maintenance according to an approved state machine.
- Pausing an external LLM call **mid-token** is not assumed possible. The proposal allows an in-flight call up to 60 seconds, then checkpoints/cancels safely and resumes or repeats an idempotent read-only operation. Maintenance has a configurable 60-minute watchdog and approval waits 30 minutes; provider-specific behavior remains pending.
- Both public and employee chat become unavailable while upload maintenance is active, as explicitly requested by the Project Owner. **This is a product trade-off**, not a technical necessity, and must be represented in availability metrics and UX.

## 8. State and data ownership (technology candidates, not final decisions)

| Data / concern | Logical authority | Candidate technology / pending decision |
|---|---|---|
| Accounts, departments, roles, ACL, document versions, lifecycle, jobs, conversation metadata | Relational authoritative store, accessed through approved backend/data interfaces | PostgreSQL 17 **OWNER-PROVIDED PROPOSAL** |
| Original uploaded files, immutable version artifacts | Private object/file storage with authorization-controlled access | Cloud Object Storage **PROPOSED** |
| Dense/lexical retrieval indexes and evidence references | Search index; never the authoritative permissions database | Qdrant dense+sparse/BM25 + RRF **OWNER-PROVIDED PROPOSAL** |
| Caching, short-lived session state, queue-position views, permitted workflow state | Approved shared cache/state mechanisms; recoverable critical state cannot exist only in volatile cache | Redis optional for cache/rate-limit state; not checkpoint authority |
| Message delivery, priority scheduling, worker acknowledgements | Queue/scheduler; jobs are authenticated, traceable, deduplicated or idempotent | PostgreSQL durable queue with lease/heartbeat/`SKIP LOCKED` **PROPOSED** |
| Checkpoints for maintenance pause/resume | Durable, restart-safe workflow checkpoint authority | PostgreSQL JSONB checkpoint state **PROPOSED** |
| Audit and operational metrics | Tamper-resistant operational/audit record with role-limited visibility | Log/metrics services **PENDING** |

No actual database, broker, cloud vendor, vector technology, or Rust framework becomes approved merely because it appears as a candidate here. Event schemas, ownership and API contracts require approval **before** parallel Rust/Python implementation.

## 9. Reliability, scalability, cost, and operations

### Reliability and cost
- Retry failed LLM API requests within approved bounds, then try an approved fallback model/provider. Report a clear error if all permitted paths fail.
- Use permission-aware retrieval caching and exact-question caching when safe; invalidate/bypass on content, ACTIVE-version, permission or policy changes. **Semantic cache is deferred**.
- Route qualifying simple questions to a lower-cost approved LLM and more complex tasks to a more capable approved model. Limit supplied context to relevant authorized excerpts.
- Retain enough job progress and checkpoints to resume questions after upload maintenance. Distinguish ordinary processing errors (ask user to resubmit) from maintenance interruptions (resume).
- Back up the authoritative database and original documents periodically; the proposal is daily base backup plus WAL/PITR, 30-day retention, RPO ≤1 hour and RTO ≤4 hours, subject to restore-drill evidence.
- Measure token consumption and estimated cost by model, task and time period. **Per-account token quota enforcement is deferred**.

### Cloud and 500-user readiness
- Deploy the Python/FastAPI Core, Python RAG workers, Python ingestion workers, storage and queue on **cloud infrastructure**. Rust remains a benchmark-gated future candidate. The precise provider, network boundary, isolation and deployment topology are `PENDING`.
- Design request handling and independent worker scaling for a **500-user capacity target**, without assuming 500 simultaneous LLM inference jobs. Rate limits and provider quotas are part of capacity planning.
- Before the 500-user claim is accepted, run load tests with a **defined workload**: concurrent sessions, query arrival rate, simple/complex ratio, cache hit rate, document size/corpus, permission mix, Chairman priority, LLM API quotas and maintenance frequency.
- Report throughput, queue wait, end-to-end response time, RAG execution time, p50/p95 latency, error rate, cloud cost and model/token consumption. Normal processing targets remain **<10 s for simple** and **<30 s for complex**; the peak-load proposal adds p95 ≤30/90 seconds and requires queue/maintenance/processing time to be reported separately.
- Show `QUEUED`, queue position, `PROCESSING`, `MAINTENANCE`, `ANSWERED` or controlled failure status as applicable; **no token streaming**.
- There is no approved monthly uptime SLA yet. Report planned upload maintenance separately from unplanned downtime.

### Security and monitoring
- Use HTTPS, encrypted storage, cloud-managed secrets, least-privilege runtime access and MFA for both admin roles.
- Prevent prompt injection from escalating privileges, escaping the read-only tool allowlist, or treating document text as executable instructions; apply abuse detection and approved mitigations.
- Emit authentication/security and document lifecycle audit events. System Admin can see authorized technical audit; Website Manager can see business-operation audit. Do not expose private conversation text merely through administrative role.
- Provide dashboard metrics for users, documents, chatbot volume, ingestion failures, queue/latency, token/cost, cache and approved RAG evaluation. Offer thumbs up/down, text feedback and report-answer actions.
- Trigger **system-generated** dashboard/email alerts for approved severe incidents; this does not authorize the chatbot to send emails autonomously.
- Evaluate retrieval and answer quality against an approved Golden Dataset; report measured results rather than invented quality claims.

## 10. API/contracts, repository targets, and dependencies

**Contract-first boundary:** Core ↔ Python job/request/results, policy checks, source identifiers, lifecycle events, pause/resume events, cost/usage records and error states must use **versioned schemas**. The owner-provided transport proposal is REST/HTTP JSON + OpenAPI 3.1 for APIs and JSON Schema payloads over the PostgreSQL queue; acceptance remains pending contract review.

**Proposed repository layout (target only, do not assume folders already exist):**

```text
frontend/                 # React + TypeScript; owner-approved Figma
backend/                  # Python/FastAPI modular monolith for MVP
  app/{api,identity,authorization,admin,documents,chat,maintenance,scheduler}/
workers/
  rag/                    # Python: retrieval, evidence, LangGraph, model gateway
  ingestion/              # Python: PDF/Word/Excel processing and staging
infra/                    # Cloud, queue, secrets, deployment and observability
contracts/                # Cross-runtime schemas (location subject to repo approval)
docs/                     # Requirements, architecture, ADRs, policies, workflows
harness/tasks/            # Owner-approved executable task plan
```

Until an approved repo migration plan exists, the **current repository layout remains authoritative**. This file does not move or rename directories.

Related specifications to review/update before coding:
- `docs/architecture/decisions/ADR-0001.md`: retain the FastAPI MVP and document Rust only as a benchmark-gated replacement candidate.
- `docs/architecture/decisions/ADR-0002.md`: trusted authorization across Rust/Python and all retrieval/cache/source boundaries.
- `docs/architecture/decisions/ADR-0003.md`: authorized Hybrid RAG baseline and measured enhancement path.
- `docs/architecture/decisions/ADR-0004.md`: two approvals, publication, versioning, maintenance and safe recovery.
- `docs/architecture/decisions/ADR-0005.md`: owner approval and contract-first multi-agent development.
- **New ADR(s) needed:** Rust-vs-Python boundary; queue/scheduler and priority policy; durable pause/resume; selected data technologies and cloud topology where not covered by the existing ADRs.
- `docs/contracts/` and `docs/architecture/workflows/` currently represent **proposals** and must be reconciled with confirmed role policy, Rust/Python boundaries, and maintenance behavior.
- `docs/design/`: Figma screens, components, interaction states and design-system decisions **remain exclusively under Project Owner review**. No agent may autonomously choose the product's final UI layout.

## 11. Open architectural decisions and blocking questions

| ID | Decision | Why it blocks design or acceptance | Decision register |
|---|---|---|---|
| ARCH-P01 | Confirm Rust Core as final backend runtime versus a benchmark-gated trial; approve framework and Rust/Python ownership | Updates ADR-0001 and repository/module ownership | `DEC-008` |
| ARCH-P02 | Define **500 users** precisely: active connections, simultaneous requests and/or LLM concurrency; approve load profile | Capacity acceptance, DevOps sizing and cost | `DEC-006` |
| ARCH-P03 | Choose cloud provider, environments, deployment layout, autoscaling/capacity limits and service security boundary | Infrastructure implementation | `DEC-002` |
| ARCH-P04 | Choose broker, priority scheduler, Chairman/Admin/Employee/Anonymous ordering, fairness, worker concurrency and queue overflow rules | Reliable scheduling and visible queue position | `DEC-006` |
| ARCH-P05 | Approve durable pause/resume state machine for upload maintenance, checkpoints, in-flight LLM calls, upload failure and stalled approval | Prevent lost work and indefinite chatbot downtime | `DEC-007` |
| ARCH-P06 | Approve authoritative database, vector/lexical search engine, object storage, cache/checkpoint stores and exact data ownership | Persistence and safe retrieval | `DEC-009` |
| ARCH-P07 | Approve cross-language transport, versioned job/result schema, authentication of workers and revocation-aware policy enforcement | Rust/Python integration and protected data flow | `DEC-010` |
| ARCH-P08 | Specify role/department/document ACL precedence, Chairman/Admin exceptions, source access and signed/validated scope design | Fail-closed access enforcement | `DEC-011` |
| ARCH-P09 | Approve model providers, fallback order, model routing, RAG evaluation thresholds, retry/time/tool budgets and caching rules | Cost, reliability and correctness | `DEC-001`, `DEC-006` |
| ARCH-P10 | Specify exact upload validation, file formats, metadata, two-review actor rules, retention and permanent-delete safeguards | Safe document lifecycle | `DEC-005`, `DEC-012` |
| ARCH-P11 | Define response target measurement (queue wait included or not), Golden Dataset gates, numeric RPO/RTO and operational alerts | Verifiable acceptance criteria | `DEC-003`, `DEC-004`, `DEC-006`, `DEC-013` |
| ARCH-P12 | Approve target repository layout/migration and revise existing contracts, ADRs, module ownership and harness task dependencies | Prevent unapproved implementation drift | `DEC-008`, `DEC-010`, `DEC-014` |

## 12. MVP exclusions and approval gate

Out of initial MVP: production multi-tenant shared control plane, runtime multi-agent system, GraphRAG/knowledge graph, live CRM/ERP integrations, autonomous AI email/document mutation, semantic similarity caching, per-account token quotas, and full administrative LLM-configuration UI. Future extensibility is desirable but is **not** permission to implement deferred features.

**Acceptance order:** Owner approves requirements and architecture/ADRs → approves security/data/contracts and Figma → updates approved task plan → agents implement and test bounded tasks → owner reviews results and separately authorizes Git/deployment actions. No commit, push, merge or deploy is implied by approving this draft.

**Approval status:** `PENDING PROJECT OWNER APPROVAL`.

## 13. Owner-provided proposal alignment

The cross-document proposal baseline is recorded in [`../requirements/owner-decision-baseline.md`](../requirements/owner-decision-baseline.md). The current MVP architecture direction is therefore:

- Python/FastAPI modular monolith plus separate RAG and ingestion workers; Rust remains a benchmark-gated alternative.
- PostgreSQL 17 is the authoritative store, durable queue and checkpoint store. Qdrant is the dense/sparse retrieval projection, private S3-compatible storage holds source files, and Redis is non-authoritative cache/rate-limit state.
- The queue uses PostgreSQL leases, heartbeat and `SKIP LOCKED`, with Chairman-first weighted scheduling, aging and bounded concurrency.
- Upload maintenance pauses new chat work, checkpoints/resumes existing work only after tenant/ACL/version rechecks, and uses a 60-minute watchdog ceiling subject to validation.
- Public API and worker payloads use versioned HTTP/JSON contracts with idempotency, correlation IDs and safe error envelopes.
- The initial capacity test targets 500 active sessions, 30 queries/minute sustained and 60 queries/minute burst with a 70/30 simple/complex mix.

These are owner-provided proposal inputs. Cloud provider, data residency, model providers, benchmark thresholds, alert recipients and the final maintenance ceiling remain approval blockers. `docs/design/` remains outside this update.

### 13.1 Student/demo deployment options

For learning and MVP demonstration, the owner may choose one of these non-production profiles:

1. **Managed student profile:** Vercel Free frontend, Azure for Students container runtime for FastAPI/RAG/ingestion, Qdrant Cloud Free and development-tier managed storage. Azure student credit and service availability must be checked at signup.
2. **Always-free self-managed profile:** Vercel Free frontend plus an Oracle Always Free VM running Docker containers for the API, RAG worker, ingestion worker and development data services. This profile has a single-VM failure boundary and requires manual backup/restore.

Render Free may be used for a short-lived API preview only; it is not a durable database or production RAG profile. Student credits do not cover external LLM API usage automatically. Production remains a separate managed-cloud decision.
