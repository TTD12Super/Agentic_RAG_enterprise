# Project Owner Decision Baseline — Q1–Q34

**Status:** OWNER-PROVIDED PROPOSAL — implementation baseline pending explicit approval of the remaining blockers below  
**Date:** 2026-11-09  
**Scope:** Initial single-enterprise deployment with future tenant reuse; `docs/design/` is excluded.

This file records the Project Owner's answers used to align the requirements, architecture, database, contracts, RAG, security, testing and operations documents. It is a decision register, not an implementation authorization. Values marked as targets must be benchmarked before becoming SLAs.

## 1. Product and tenant scope

- The MVP serves one enterprise deployment.
- The data model is tenant-aware so a later enterprise can reuse the code with a separate tenant, users, permissions and document corpus.
- A new enterprise must not see or inherit the previous enterprise's users, documents, indexes, cache entries, conversations or audit data.
- A tenant replacement or offboarding flow must remove or tombstone old data safely before new data is served.

## 2. Identity and authorization

- Employee onboarding is request-based: the employee requests access, then an authorized administrator approves and provisions the account.
- System Admin has all system-management rights except reading the contents of user conversations. Access to sensitive diagnostic material remains audited and time-limited.
- Chairman can read all published company documents, but an explicit deny overrides a role-based allow.
- Authorization combines RBAC, department membership and document-level ACLs with default deny.
- The final policy rule is: explicit deny wins; otherwise an applicable explicit/document/department/role allow may grant access; missing or stale policy denies.
- The same administrator may perform both document reviews.
- Administrative MFA is required for Chairman, Website Manager and System Admin; the implementation preference is TOTP, with provider-managed MFA/WebAuthn allowed if already available.

## 3. Documents and ingestion

- MVP formats: `.pdf`, `.docx`, `.xlsx`; `.doc` and `.xls` are not supported.
- Maximum upload size is 200,000,000 bytes per file. Oversize requests return `413 PAYLOAD_TOO_LARGE`.
- Uploads use streaming/chunked transfer to private object storage, with byte-count, MIME/magic-byte, checksum and malware checks.
- PDF supports text and scanned documents with Vietnamese/English OCR; maximum 2,000 pages.
- DOCX has a two-million extracted-word limit and parser resource limits.
- XLSX has maximum 50 sheets, 200,000 populated rows per workbook and 200 columns per sheet.
- Macros, scripts and executable formulas are not run.
- Citation preview needs `READ`; original-file download needs a separate `DOWNLOAD` permission and a short-lived signed URL.
- Ingestion retry is limited to three attempts for an unchanged `document_version_id`; each attempt has its own attempt ID. A changed file creates a new version.
- A failed version never replaces the current ACTIVE version. Publication is atomic.
- Review rejection records a reason and requires a new review request for resubmission.
- Approval expires after 30 minutes without an action. Maintenance has a configurable 60-minute maximum and a watchdog-safe abort; no automatic approval.

## 4. Data lifecycle

| Data | Proposed retention |
|---|---:|
| Authenticated conversation | 180 days from last activity |
| Anonymous session | 30 minutes idle, maximum 24 hours |
| Anonymous conversation | 7 days |
| Superseded document version | 365 days |
| Soft-deleted document | 30 days before permanent deletion |
| Audit log | 2 years |
| Application log | 30 days |
| Backup | 30 days |
| Citation | Conversation lifetime, maximum 180 days |
| Feedback | 180 days |

Soft delete blocks retrieval and preview immediately, invalidates caches and removes the active index projection, while recovery remains possible for 30 days. Permanent deletion removes online DB, vector, object and cache data under controlled workflow. Immutable backups may retain deleted data until expiry; restore must replay tombstones/revocations before serving data. Legal hold overrides ordinary retention.

## 5. Answers and citations

- Answer in the user's language unless explicitly asked otherwise.
- For conflicting sources, prefer approved, effective sources with the applicable business authority and the newest ACTIVE version within a document. If conflict remains, disclose both sources without inventing a resolution.
- Partial evidence produces a qualified partial answer. No sufficient evidence produces `INSUFFICIENT_EVIDENCE`.
- Citation details are collapsed by default but a visible source indicator remains available for expansion.

## 6. Runtime and data platform

- MVP backend: Python/FastAPI modular monolith with separate RAG and ingestion workers.
- Rust Core is a benchmark candidate only; migration requires evidence of better throughput, p95 latency, resource use and operational complexity.
- PostgreSQL 17 is authoritative for relational data, jobs, queue state and durable checkpoints.
- MVP queue uses PostgreSQL leasing/heartbeat/`SKIP LOCKED`; Kafka/RabbitMQ are deferred.
- Qdrant provides dense and sparse/BM25 retrieval with RRF fusion. OpenSearch/Elasticsearch are not used in MVP.
- S3-compatible private object storage holds original/version artifacts.
- Redis is optional for cache, rate limit and short-lived state; it is not an authoritative checkpoint store.
- Alembic owns Git-managed migrations. A future Rust migration must use the same single migration owner.
- Dev, staging and production have separate secrets, databases and buckets; production data is not copied to development without approval and de-identification.

## 7. Queue and maintenance behavior

- Query priority is Chairman > Website Manager/System Admin > authenticated employee > anonymous user.
- Scheduling uses weighted priority, 60-second aging and per-user/per-tenant rate limits.
- Initial configurable limits: 20 concurrent RAG tasks, 2 concurrent ingestion tasks and 200 waiting query jobs.
- Queue saturation returns `503` with `Retry-After`; rate limiting returns `429`; saturation is not represented as maintenance.
- New queries during maintenance receive `503 MAINTENANCE_ACTIVE`. Existing work becomes `PAUSED`.
- An in-flight LLM call may finish within 60 seconds. Otherwise the worker checkpoints safely, cancels when supported and evaluates an idempotent retry on resume.
- Checkpoints include workflow stage, job ID, source/version IDs, policy version, attempt and timestamps in PostgreSQL.
- Resume always rechecks tenant, ACL, policy and document version. Ordinary terminal failures do not resume automatically.

## 8. RAG and model policy

- Embedding baseline: `BAAI/bge-m3`.
- Reranker baseline: `BAAI/bge-reranker-v2-m3`.
- Structure-aware child chunks target 500–800 tokens with 10–15% overlap, capped near 120 tokens; parent sections target a maximum of 2,000 tokens.
- Excel provenance includes workbook, sheet, table/row group, headers and `cell_range`.
- Simple/complex routing is rule-first, with evidence assessment and an LLM classifier only when ambiguous.
- Limits: two retrieval rounds, four subqueries, eight tool calls; simple budget 16k input/2k output; complex budget 32k input/4k output.
- Cost targets are at most $0.05/simple and $0.20/complex, subject to benchmark.
- Primary and fallback LLM providers remain pending provider, region, quality, latency, price and data-processing review.
- Provider contracts must prohibit training on enterprise data and use the lowest available request retention, preferably zero retention.

## 9. API, contracts and prompts

- Public API is REST/HTTP JSON with OpenAPI 3.1 and JSON Schema/Pydantic models.
- API version is `/api/v1`; breaking changes use `/api/v2`.
- Worker payloads include `schema_version`; communication uses REST for clients and the durable PostgreSQL queue for jobs.
- Service identities use short-lived credentials and least privilege.
- Errors use a safe Problem Details-like envelope with code, message, request ID and redacted details.
- Correlation uses `X-Request-ID` and W3C `traceparent`; timestamps are UTC/RFC 3339.
- Upload/retry/mutation requests use idempotency keys; list APIs use cursor pagination with default 20 and maximum 100.
- Job states are `QUEUED`, `RUNNING`, `PAUSED`, `RETRY_SCHEDULED`, `COMPLETED`, `FAILED`, `CANCELLED`. `MAINTENANCE` is a system mode, not a job state.
- Prompts are versioned in Git. The database stores active-version metadata and audit references. Answers record prompt, model, retrieval-config and policy versions.
- Planner, router and tool outputs validate dedicated JSON Schemas before rendering.

## 10. Security, recovery and quality targets

- Public content may use an approved external provider; INTERNAL content requires an approved provider and data-handling contract; unknown data denies; future CONFIDENTIAL/RESTRICTED egress rules are stricter than INTERNAL.
- Access token target is 15 minutes; refresh/session maximum is 8 hours; idle timeout is 30 minutes. Five failed logins in 15 minutes trigger a 15-minute lock/throttle.
- Audit is append-only, preferably immutable/WORM. Raw prompts, outputs and conversation bodies are not logged by default.
- P0 unauthorized/cross-tenant disclosure alerts Security Owner and System Admin on-call immediately. P1 broad outage alerts Technical Owner and System Admin on-call immediately. P2/P3 follow the documented dashboard/email policy.
- PostgreSQL uses daily base backup plus continuous WAL/PITR. Object storage uses versioning/backup. Qdrant can be rebuilt from authoritative sources.
- Recovery targets are RPO ≤1 hour and RTO ≤4 hours, subject to restore-drill evidence. Restore drills are quarterly.
- Load target: 500 concurrent sessions, 30 queries/minute sustained and 60 queries/minute for a five-minute burst, with 70% simple / 30% complex mix.
- Initial quality targets are Recall@10 ≥90%, citation accuracy ≥95%, answer correctness ≥90%, no-answer accuracy ≥90%, zero unauthorized retrieval and p95 simple/complex latency ≤30/90 seconds at the stated load profile. These remain targets until benchmark approval.

## 11. Remaining approval blockers

1. Cloud provider, region and whether data must remain inside Vietnam.
2. Formal confirmation of the 500-concurrent-session capacity definition.
3. Primary/fallback LLM names, versions and provider request-retention terms.
4. Approval of latency, cost and quality thresholds after benchmark.
5. Actual alert recipients and on-call addresses.
6. Evidence that a 60-minute maintenance window is sufficient for 200 MB uploads, scanned PDFs and complex XLSX files.

Until these are approved, dependent implementation tasks remain design/prototype work and no production SLA is implied.

## 12. Student and low-cost deployment profiles

These profiles are approved as deployment options for learning, development and demo work only. They do not replace the production cloud decision.

### Profile A — managed student cloud

- Frontend: Vercel Free.
- API and workers: Azure for Students using Container Apps/App Service or equivalent container runtime.
- Vector search: Qdrant Cloud Free for development/test.
- Database and object storage: managed services only if the student credit and retention policy cover them; otherwise use a separate development-tier provider.
- Secrets: provider secret store; never Vercel public environment variables or Git.
- LLM calls: separate provider key and spending cap; cloud student credit does not imply free LLM usage.

Azure for Students currently advertises a USD 100 credit for 12 months without a credit card, subject to student eligibility, availability and offer terms. This profile is not a production availability or cost guarantee.

### Profile B — always-free self-managed demo

- Frontend: Vercel Free.
- API, RAG worker and ingestion worker: Docker containers on an Oracle Always Free VM.
- Development PostgreSQL, Qdrant and object storage: self-managed containers or small development services.
- Backups: manual/exported backups are mandatory; no production durability is implied.

This profile minimizes cost but creates operational risk: one VM can fail, resources are limited, capacity may be unavailable, and the operator owns patching, security, restore and monitoring.

### Not a production profile

Render Free is acceptable for a short-lived API/demo, but not for durable RAG data: free services sleep, free Postgres has a short lifetime and no production backup/scaling guarantees. Qdrant Cloud Free is also development/test only. The production profile remains a managed private deployment after cloud, region, provider and data-residency approval.

### Official references

- [Azure for Students offer](https://azure.microsoft.com/en-us/pricing/offers/ms-azr-0170p)
- [Google Cloud education credits](https://docs.cloud.google.com/billing/docs/how-to/edu-grants)
- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/faq/)
- [Render free deployment limits](https://render.com/docs/free)
- [Qdrant Managed Cloud](https://qdrant.tech/documentation/cloud/)
