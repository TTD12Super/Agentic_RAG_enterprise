# Database Architecture V2 — Enterprise Agentic RAG

**Document ID:** DB-ARCH-V2-001  
**Status:** PROPOSED — design only, pending Project Owner approval  
**Version:** 2.0  
**Date:** 2026-11-09  
**Target:** PostgreSQL authoritative relational store

> This document is an implementation-ready database design proposal. It does not create migrations, ORM models, RLS policies, queues, or production resources.

## 1. Scope and decisions

This design upgrades the current repository scaffold for:

- Multi-tenant identity and membership.
- Conversations, messages and anonymous-session isolation.
- Durable query jobs and agent execution steps.
- Two-stage document review, versioning and publication.
- Separate ingestion jobs and staged vector indexing.
- Document-level grants, audit events, citations and feedback.
- Maintenance pause/resume and cross-system consistency.

The current product architecture remains:

- One enterprise per MVP deployment, but the schema is tenant-aware for reuse and isolation.
- Modular Core plus independent Python RAG and ingestion workers.
- PostgreSQL is authoritative for identity, policy, document lifecycle, jobs, conversations and audit.
- Qdrant/search indexes are derived projections.
- Original files remain in private object storage.
- Queue, cache/checkpoint store and cloud topology remain separate architecture decisions.

No task status is changed by this document. Current database implementation is not started: migrations, ORM models, repositories and database tests are absent.

## 2. Gap analysis

| Existing component | Current state | Identified gap | Database V2 response |
|---|---|---|---|
| backend/app/db/migrations | Only .gitkeep | No schema or migration framework in the repository | Define migration order and constraints without fabricating completed migrations |
| Architecture overview | Defines Core, workers, jobs, maintenance and data ownership | No relational ERD or database invariants | Add tenant, job, lifecycle, checkpoint and consistency design |
| Contracts | Proposal-level identity, document, ingestion, retrieval, cache and audit contracts | No complete relational ownership or composite tenant rules | Map each contract to authoritative tables and constraints |
| Tasks | ARCH-001 READY; CONTRACT-001 and INFRA-001 PLANNED | Database work depends on architecture and contract approval | Keep design proposal separate from implementation completion |
| Worker workflows | Async RAG and ingestion flows are documented | No durable job lease, checkpoint, idempotency or outbox model | Add QUERY_JOBS, INGESTION_JOBS, AGENT_EXECUTION_STEPS and OUTBOX_EVENTS |
| Tests | Only placeholders and guidance | No executable database/integration tests | Define required tests; report them as NOT RUN |
| Current ERD/database docs | No database/database.md exists | No single source of truth for relational structure | This file is the proposed Database V2 source |

## 3. Design principles and security invariants

### 3.1 Tenant model

- USERS is a global identity table and intentionally has no tenant_id.
- TENANT_MEMBERSHIPS connects a user to a tenant and carries tenant-specific status, department and roles.
- Every tenant-owned resource has tenant_id.
- Child-to-parent relations use composite foreign keys containing tenant_id where both sides are tenant-owned.
- Anonymous conversations are tenant-bound by trusted deployment/host routing; a client cannot choose an arbitrary tenant.
- The MVP may deploy one tenant per installation, but the database must not rely on a global singleton tenant.

### 3.2 Authorization

- PostgreSQL stores policy inputs and grants; the trusted backend PDP remains the authorization authority.
- Qdrant, queue payloads, LLM output, browser input and retrieved text never grant access.
- PostgreSQL Row-Level Security is a proposed defense-in-depth layer, not a replacement for PDP/PEP checks.
- Unknown tenant, membership, classification, policy version or scope fails closed.
- Source, citation, cache, queued-job resume and conversation reads recheck current authorization.

### 3.3 Lifecycle and provenance

- Only a successfully processed and approved ACTIVE document version is eligible for retrieval.
- A document version is immutable after publication except for lifecycle state changes.
- Historical citations point to an immutable chunk and version; later versions do not rewrite old citations.
- Failed or partial indexing is never served.
- Original binaries are not stored in PostgreSQL. They use private object storage references.
- Chunk text is bounded extracted content for retrieval/citation; original files remain the source artifact.
- No chain-of-thought or unrestricted raw model reasoning is stored.

### 3.4 Consistency

- Database-to-queue and database-to-worker events use a transactional outbox.
- Job claims use row locking or compare-and-swap plus a lease; a worker identity alone is not a lock.
- Final answer persistence is idempotent and linked to one request message and one query job.
- Vector/index state is derived and reconciled against PostgreSQL; distributed transactions are not used.

## 4. Updated logical ERD

The diagram shows physical tables proposed for V2. The 15 entities in the task are included; extra tables are justified for RBAC, approvals, sessions, maintenance, outbox and workflow durability.

~~~mermaid
erDiagram
    TENANTS {
        uuid id PK
        string slug UK
        string name
        string status
        timestamptz created_at
    }

    USERS {
        uuid id PK
        string email UK
        string display_name
        string status
        timestamptz created_at
    }

    DEPARTMENTS {
        uuid id PK
        uuid tenant_id FK
        string code
        string name
        string status
    }

    TENANT_MEMBERSHIPS {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        uuid department_id FK
        string status
        timestamptz joined_at
        timestamptz revoked_at
    }

    ROLES {
        uuid id PK
        string code UK
        string name
    }

    MEMBERSHIP_ROLES {
        uuid membership_id PK, FK
        uuid role_id PK, FK
    }

    AUTH_SESSIONS {
        uuid id PK
        uuid user_id FK
        uuid tenant_id FK
        string token_hash
        timestamptz expires_at
        timestamptz revoked_at
    }

    DOCUMENTS {
        uuid id PK
        uuid tenant_id FK
        uuid owner_department_id FK
        uuid created_by_membership_id FK
        uuid current_active_version_id FK
        string title
        string classification
        string status
        timestamptz created_at
        timestamptz updated_at
    }

    DOCUMENT_VERSIONS {
        uuid id PK
        uuid tenant_id FK
        uuid document_id FK
        int version_number
        string source_uri
        string sha256
        string processing_status
        string publication_status
        timestamptz created_at
        timestamptz activated_at
    }

    DOCUMENT_APPROVALS {
        uuid id PK
        uuid tenant_id FK
        uuid version_id FK
        uuid reviewer_membership_id FK
        int stage
        int attempt_number
        string decision
        timestamptz decided_at
    }

    DOCUMENT_ACCESS_GRANTS {
        uuid id PK
        uuid tenant_id FK
        uuid document_id FK
        uuid membership_id FK
        uuid role_id FK
        uuid department_id FK
        string action
        string effect
    }

    CHUNKS {
        uuid id PK
        uuid tenant_id FK
        uuid version_id FK
        uuid parent_chunk_id FK
        int chunk_index
        text content_text
        string content_hash
        int page_start
        int page_end
        string vector_point_id
        string index_version
        string index_status
    }

    INGESTION_JOBS {
        uuid id PK
        uuid tenant_id FK
        uuid version_id FK
        string status
        string current_stage
        int attempt_count
        jsonb checkpoint
        string error_code
        timestamptz started_at
        timestamptz completed_at
    }

    CONVERSATIONS {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        string anonymous_session_hash
        string status
        timestamptz created_at
    }

    MESSAGES {
        uuid id PK
        uuid tenant_id FK
        uuid conversation_id FK
        string role
        text content
        string answer_status
        timestamptz created_at
    }

    QUERY_JOBS {
        uuid id PK
        uuid tenant_id FK
        uuid conversation_id FK
        uuid request_message_id FK
        uuid response_message_id FK
        uuid maintenance_window_id FK
        string status
        int priority
        int attempt_count
        int max_attempts
        bigint revision
        jsonb checkpoint
        int checkpoint_schema_version
        string worker_id
        timestamptz lease_expires_at
        timestamptz queued_at
        timestamptz next_retry_at
        string idempotency_key
    }

    AGENT_EXECUTION_STEPS {
        uuid id PK
        uuid tenant_id FK
        uuid query_job_id FK
        int step_number
        int attempt_number
        string step_type
        string status
        string provider_code
        string model_name
        jsonb safe_metadata
        string error_code
        timestamptz started_at
        timestamptz completed_at
    }

    MAINTENANCE_WINDOWS {
        uuid id PK
        uuid tenant_id FK
        uuid started_by_membership_id FK
        string status
        string reason
        timestamptz started_at
        timestamptz ended_at
    }

    ANSWER_CITATIONS {
        uuid id PK
        uuid tenant_id FK
        uuid assistant_message_id FK
        uuid chunk_id FK
        uuid version_id FK
        int citation_order
        int claim_order
        text source_quote
    }

    FEEDBACK {
        uuid id PK
        uuid tenant_id FK
        uuid message_id FK
        uuid membership_id FK
        string anonymous_session_hash
        string rating
        text comment
        timestamptz created_at
    }

    AUDIT_EVENTS {
        uuid id PK
        uuid tenant_id FK
        uuid actor_membership_id FK
        string actor_service
        string event_type
        string resource_type
        uuid resource_id
        string outcome
        string trace_id
        jsonb safe_metadata
        timestamptz occurred_at
    }

    OUTBOX_EVENTS {
        uuid id PK
        uuid tenant_id FK
        string aggregate_type
        uuid aggregate_id
        string event_type
        jsonb payload
        string status
        int attempt_count
        timestamptz available_at
        timestamptz published_at
    }

    TENANTS ||--o{ DEPARTMENTS : contains
    TENANTS ||--o{ TENANT_MEMBERSHIPS : has
    USERS ||--o{ TENANT_MEMBERSHIPS : joins
    DEPARTMENTS o|--o{ TENANT_MEMBERSHIPS : assigns
    TENANT_MEMBERSHIPS ||--o{ MEMBERSHIP_ROLES : receives
    ROLES ||--o{ MEMBERSHIP_ROLES : grants
    USERS ||--o{ AUTH_SESSIONS : opens
    TENANTS ||--o{ AUTH_SESSIONS : scopes

    TENANTS ||--o{ DOCUMENTS : owns
    DEPARTMENTS o|--o{ DOCUMENTS : owns
    TENANT_MEMBERSHIPS ||--o{ DOCUMENTS : creates
    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : versions
    DOCUMENTS o|--o| DOCUMENT_VERSIONS : points_to_active
    DOCUMENT_VERSIONS ||--o{ DOCUMENT_APPROVALS : requires
    TENANT_MEMBERSHIPS ||--o{ DOCUMENT_APPROVALS : reviews
    DOCUMENTS ||--o{ DOCUMENT_ACCESS_GRANTS : protects
    TENANT_MEMBERSHIPS o|--o{ DOCUMENT_ACCESS_GRANTS : member_subject
    ROLES o|--o{ DOCUMENT_ACCESS_GRANTS : role_subject
    DEPARTMENTS o|--o{ DOCUMENT_ACCESS_GRANTS : department_subject
    DOCUMENT_VERSIONS ||--o{ CHUNKS : contains
    CHUNKS o|--o{ CHUNKS : parent_of
    DOCUMENT_VERSIONS ||--o{ INGESTION_JOBS : processes

    TENANTS ||--o{ CONVERSATIONS : owns
    USERS o|--o{ CONVERSATIONS : starts
    CONVERSATIONS ||--o{ MESSAGES : contains
    CONVERSATIONS ||--o{ QUERY_JOBS : runs
    MESSAGES ||--o{ QUERY_JOBS : requests_or_answers
    QUERY_JOBS ||--o{ AGENT_EXECUTION_STEPS : records
    MAINTENANCE_WINDOWS o|--o{ QUERY_JOBS : pauses
    MESSAGES ||--o{ ANSWER_CITATIONS : cites
    CHUNKS ||--o{ ANSWER_CITATIONS : supports
    DOCUMENT_VERSIONS ||--o{ ANSWER_CITATIONS : preserves
    MESSAGES ||--o{ FEEDBACK : receives
    TENANT_MEMBERSHIPS o|--o{ FEEDBACK : submits

    TENANTS ||--o{ MAINTENANCE_WINDOWS : scopes
    TENANT_MEMBERSHIPS ||--o{ MAINTENANCE_WINDOWS : starts
    TENANTS ||--o{ AUDIT_EVENTS : records
    TENANT_MEMBERSHIPS o|--o{ AUDIT_EVENTS : acts
    TENANTS ||--o{ OUTBOX_EVENTS : emits
~~~

### 4.1 Why the extra physical tables exist

| Table | Justification |
|---|---|
| DEPARTMENTS | Requirements use department-based access and document ownership. |
| ROLES, MEMBERSHIP_ROLES | Tenant-scoped RBAC requires role assignments independent of global users. |
| AUTH_SESSIONS | Activation, expiry, revocation and admin MFA need durable session state. |
| DOCUMENT_APPROVALS | Two distinct review stages and auditability cannot be represented by one approval_id. |
| MAINTENANCE_WINDOWS | Global/per-tenant maintenance and safe query resume need durable coordination. |
| OUTBOX_EVENTS | Avoid losing queue/index/lifecycle events after a committed PostgreSQL transaction. |

## 5. Table responsibilities and key columns

### 5.1 Identity and tenant management

- TENANTS: immutable tenant identity, deployment status and configuration boundary.
- USERS: global login identity. Email is normalized and unique. No tenant_id.
- DEPARTMENTS: tenant-owned department catalog.
- TENANT_MEMBERSHIPS: user-to-tenant relationship, membership status, primary department, activation/revocation timestamps.
- ROLES: controlled role catalog such as employee, chairman, website_manager and system_admin.
- MEMBERSHIP_ROLES: many-to-many tenant role assignments.
- AUTH_SESSIONS: hashed session/token records, expiry, revocation and last-use metadata. Store no raw token.

Security rule: a user is authorized in a tenant only through an active TENANT_MEMBERSHIPS row. Anonymous users have no membership and can use only the trusted public tenant route.

### 5.2 Conversations and execution

CONVERSATIONS:

- tenant_id is mandatory.
- user_id is nullable only for anonymous conversations.
- anonymous_session_hash is required when user_id is null.
- One conversation cannot switch from anonymous to an employee account silently.
- A user may read only their own conversations unless a separate approved incident-access policy exists.

MESSAGES:

- role is constrained to USER, ASSISTANT, SYSTEM or TOOL.
- Store final user/assistant content needed for product history according to retention policy.
- Do not store hidden reasoning as a message.
- An assistant message may be referenced by ANSWER_CITATIONS and FEEDBACK.

QUERY_JOBS:

- request_message_id is mandatory and unique per tenant.
- response_message_id is nullable until a final answer or controlled failure is persisted.
- idempotency_key is unique per tenant when present.
- checkpoint is JSONB only for versioned, safe workflow state; checkpoint_schema_version is mandatory when checkpoint is non-null.
- revision is incremented on every state/checkpoint update.
- worker_id, heartbeat and lease_expires_at support recovery from worker crashes.
- selected provider/model and retry metadata may be stored in safe metadata or execution steps; never store raw hidden reasoning.

AGENT_EXECUTION_STEPS:

- One parent QUERY_JOBS row.
- step_number and attempt_number identify retries.
- safe_metadata contains bounded operational details only.
- provider/model fields support fallback analysis without storing prompts or chain-of-thought.

MAINTENANCE_WINDOWS:

- One active maintenance window per tenant.
- The row records who started it, reason, state and completion.
- QUERY_JOBS link to the maintenance window when pause is requested or performed.
- Every transition emits an AUDIT_EVENTS row.

### 5.3 Knowledge and ingestion

DOCUMENTS:

- Stable document identity across versions.
- classification is PUBLIC or INTERNAL for the MVP; any extra sensitivity classification requires an approved policy.
- status is a summary state such as ACTIVE, SOFT_DELETED or PURGED.
- current_active_version_id is nullable during initial upload and points only to the document’s active version.

DOCUMENT_VERSIONS:

- version_number is unique per document.
- source_uri points to private object storage; PostgreSQL does not hold original PDF/Word/Excel binaries.
- sha256 identifies the uploaded source.
- processing_status and publication_status are separate so a parsed version cannot be mistaken for a published version.
- A version is immutable after activation except for controlled lifecycle transitions.

DOCUMENT_APPROVALS:

- stage is 1 or 2.
- Each decision records reviewer membership, attempt number, decision, time and safe note.
- The owner-provided baseline permits the same reviewer to perform both stages; final policy approval still governs whether the schema must enforce any reviewer-separation rule.

CHUNKS:

- One immutable extracted chunk belongs to exactly one document version and tenant.
- chunk_index is unique within a version.
- parent_chunk_id must reference a chunk in the same tenant and version.
- content_text is bounded extracted text for retrieval/citation; original files remain in object storage.
- vector_point_id, index_version and index_status map the relational chunk to a derived Qdrant/search projection.
- Only chunks belonging to eligible ACTIVE versions may be returned by retrieval.

INGESTION_JOBS:

- One or more attempts may process a version, but only one active attempt may hold the processing lease.
- current_stage records the last durable stage.
- checkpoint is resumable stage metadata, not an assumption of full workflow recovery.
- Failed, cancelled or superseded jobs must clean or quarantine derived artifacts before any publication.

### 5.4 Authorization, provenance and quality

DOCUMENT_ACCESS_GRANTS:

- Exactly one subject is set: membership, role or department.
- action is explicit, for example DOCUMENT_READ or SOURCE_DOWNLOAD.
- effect is ALLOW or DENY.
- Grants are tenant-scoped and must never cross a document’s tenant.
- PDP/PEP evaluates grants with role, department, document status, classification and policy version.

ANSWER_CITATIONS:

- Links an assistant message to an immutable chunk and version.
- citation_order controls presentation; claim_order supports claim-level verification.
- The redundant version_id is enforced against CHUNKS with a composite foreign key.
- source_quote is optional, bounded and must come from the authorized chunk.

FEEDBACK:

- Links to an assistant message and optionally an active membership or anonymous session.
- rating is constrained to the approved set, for example POSITIVE or NEGATIVE.
- Recommended MVP rule: one feedback record per authenticated membership/message, updated rather than duplicated. Anonymous feedback policy remains pending.

AUDIT_EVENTS:

- Append-only by application policy.
- actor_membership_id is nullable for system events; actor_service identifies the trusted service.
- safe_metadata excludes passwords, tokens, raw confidential documents, full prompts and unnecessary personal data.
- Retention and protected access are policy decisions, not database cascade behavior.

## 6. Constraints and referential behavior

### 6.1 Required constraints

- UUID primary key on all durable entities.
- Normalized lowercase unique USERS.email.
- Unique TENANTS.slug.
- Unique TENANT_MEMBERSHIPS(tenant_id, user_id).
- Unique DEPARTMENTS(tenant_id, code).
- Unique DOCUMENT_VERSIONS(tenant_id, document_id, version_number).
- At most one ACTIVE DOCUMENT_VERSION per document using a partial unique index.
- Unique CHUNKS(tenant_id, version_id, chunk_index).
- Unique query idempotency key per tenant.
- Unique QUERY_JOBS(tenant_id, request_message_id).
- Unique AGENT_EXECUTION_STEPS(tenant_id, query_job_id, step_number, attempt_number).
- Exactly one non-null subject column in DOCUMENT_ACCESS_GRANTS.
- DOCUMENT_APPROVALS.stage in 1..2.
- Positive priority, attempt counts and version numbers.
- ended_at is null while a maintenance window is active.
- response_message_id cannot point to a message in another tenant or conversation.
- ANSWER_CITATIONS.version_id must match the cited CHUNKS.version_id.

### 6.2 Tenant-consistency constraints

Use composite foreign keys where parent and child are tenant-owned:

- (tenant_id, document_id) → DOCUMENTS(tenant_id, id).
- (tenant_id, version_id) → DOCUMENT_VERSIONS(tenant_id, id).
- (tenant_id, conversation_id) → CONVERSATIONS(tenant_id, id).
- (tenant_id, query_job_id) → QUERY_JOBS(tenant_id, id).
- (tenant_id, message_id) → MESSAGES(tenant_id, id).
- (tenant_id, membership_id) → TENANT_MEMBERSHIPS(tenant_id, id).

The database must not accept a valid UUID from a different tenant merely because the referenced row exists.

### 6.3 Delete behavior

- TENANTS: RESTRICT while any tenant-owned data exists.
- USERS: RESTRICT while memberships or sessions exist; use account deactivation instead of deletion by default.
- TENANT_MEMBERSHIPS: RESTRICT when referenced by audit, approval or historical records; revoke status instead.
- DOCUMENTS and DOCUMENT_VERSIONS: RESTRICT; use lifecycle states and controlled permanent-delete workflows.
- CHUNKS, citations and audit records: preserve historical evidence until approved retention/deletion policy permits removal.
- Sessions: revoke or expire; cascade deletion is acceptable only for non-audit session rows.
- Outbox events: retain until published or dead-lettered according to operational policy.

## 7. Index plan

Indexes should be added only for declared query patterns.

| Table | Index | Query purpose |
|---|---|---|
| TENANT_MEMBERSHIPS | (tenant_id, status, user_id) | Resolve active membership |
| TENANT_MEMBERSHIPS | (user_id, tenant_id) | List a user’s tenant memberships |
| AUTH_SESSIONS | (user_id, revoked_at, expires_at) | Session validation/revocation |
| DOCUMENTS | (tenant_id, status, updated_at) | Current tenant catalog |
| DOCUMENT_VERSIONS | UNIQUE (tenant_id, document_id, version_number) | Version lookup |
| DOCUMENT_VERSIONS | Partial UNIQUE (tenant_id, document_id) WHERE publication_status = ACTIVE | One active version |
| DOCUMENT_VERSIONS | (tenant_id, publication_status, updated_at) | Retrieval eligibility/reconciliation |
| CHUNKS | UNIQUE (tenant_id, version_id, chunk_index) | Ordered chunk lookup |
| CHUNKS | (tenant_id, version_id, index_status) | Staging/reconciliation |
| CHUNKS | Partial UNIQUE (tenant_id, vector_point_id, index_version) | Prevent duplicate vector binding |
| INGESTION_JOBS | (tenant_id, status, current_stage, created_at) | Worker queue/recovery |
| QUERY_JOBS | (tenant_id, status, priority DESC, queued_at) | Priority job selection |
| QUERY_JOBS | (tenant_id, lease_expires_at) WHERE status = RUNNING | Lease recovery |
| QUERY_JOBS | UNIQUE (tenant_id, idempotency_key) WHERE idempotency_key IS NOT NULL | Duplicate prevention |
| AGENT_EXECUTION_STEPS | (tenant_id, query_job_id, step_number) | Workflow diagnostics |
| CONVERSATIONS | (tenant_id, user_id, created_at) | User history |
| MESSAGES | (tenant_id, conversation_id, created_at) | Conversation loading |
| ANSWER_CITATIONS | (tenant_id, assistant_message_id, citation_order) | Citation display |
| AUDIT_EVENTS | (tenant_id, occurred_at) | Tenant audit queries |
| AUDIT_EVENTS | (trace_id, occurred_at) | Cross-service investigation |
| OUTBOX_EVENTS | (status, available_at) | Publisher polling |

Initial scale is approximately 100 documents and a 500-user target. This does not justify partitioning by default. Reconsider partitioning only after measured audit/job volume, retention and query plans.

## 8. State machines

### 8.1 Document version

~~~mermaid
stateDiagram-v2
    [*] --> UPLOADED
    UPLOADED --> QUARANTINED
    QUARANTINED --> REVIEW_1_APPROVED
    QUARANTINED --> REJECTED
    REVIEW_1_APPROVED --> PROCESSING
    PROCESSING --> PROCESS_VALIDATED
    PROCESSING --> FAILED
    PROCESS_VALIDATED --> PENDING_REVIEW_2
    PENDING_REVIEW_2 --> ACTIVE: recorded review-2 approval and publication checks
    PENDING_REVIEW_2 --> REJECTED
    ACTIVE --> SUPERSEDED
    ACTIVE --> REVOKED
    ACTIVE --> SOFT_DELETED
    FAILED --> CANCELLED
    REJECTED --> [*]
    CANCELLED --> [*]
~~~

Rules:

- Review 1 precedes processing.
- Review 2 follows successful processing.
- Publication atomically changes the eligible version and invalidates affected derived state.
- On failure/rejection, the former ACTIVE version remains the serving version.

### 8.2 Query job

~~~mermaid
stateDiagram-v2
    [*] --> QUEUED
    QUEUED --> RUNNING
    QUEUED --> CANCELLED
    RUNNING --> COMPLETED
    RUNNING --> RETRY_SCHEDULED
    RUNNING --> PAUSED: safe checkpoint after pause request
    RUNNING --> FAILED
    PAUSED --> RUNNING
    PAUSED --> CANCELLED
    RETRY_SCHEDULED --> RUNNING
    RETRY_SCHEDULED --> FAILED
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
~~~

Rules:

- Ordinary FAILED jobs are not silently resumed; the user resubmits.
- Maintenance pause is the explicit exception.
- A pause request is a control flag/event, not a separate public job state; the job stays RUNNING until a safe checkpoint is reached.
- A claim requires a valid lease and revision.
- A stale checkpoint revision cannot overwrite newer state.
- One request message has at most one final response message.

### 8.3 Ingestion job

~~~mermaid
stateDiagram-v2
    [*] --> QUEUED
    QUEUED --> RUNNING
    RUNNING --> COMPLETED
    RUNNING --> RETRY_SCHEDULED
    RETRY_SCHEDULED --> RUNNING
    RETRY_SCHEDULED --> FAILED
    RUNNING --> FAILED
    RUNNING --> PAUSED
    PAUSED --> RUNNING
    QUEUED --> CANCELLED
    RUNNING --> CANCELLED
    PAUSED --> CANCELLED
~~~

The shared job state is separate from `current_stage`: FILE_VALIDATION, STORED, PARSING, CHUNKING, EMBEDDING, VECTOR_INDEXING and INDEX_VALIDATION are stages, not job states. COMPLETED means the staged version is validated; it does not itself grant ACTIVE publication.

## 9. PostgreSQL and external-system consistency

### 9.1 PostgreSQL to queue

Use OUTBOX_EVENTS in the same transaction as the state change:

1. Commit the job/document/maintenance state and outbox event atomically.
2. Publisher claims unpublished outbox rows with a lease.
3. Publish an authenticated, versioned message.
4. Mark the outbox event published.
5. Retry safely; dead-letter after bounded attempts with an audit event.

A queue message is a delivery hint, not the source of truth. Workers read current PostgreSQL state before acting.

### 9.2 Worker crash and duplicate delivery

- QUERY_JOBS and INGESTION_JOBS use lease expiration and heartbeat.
- A second worker can reclaim only an expired lease.
- Worker completion uses revision or lease-token compare-and-swap.
- Duplicate delivery is harmless when idempotency_key and final-answer uniqueness are enforced.
- Checkpoint writes include schema version and expected revision.

### 9.3 Vector/index consistency

1. Create or update a version in a non-searchable state.
2. Ingestion writes chunks and index bindings as STAGING.
3. Worker writes vector points using deterministic vector_point_id.
4. Reconcile vector counts, hashes, version and ACL metadata.
5. Only after validation does PostgreSQL publish the version ACTIVE.
6. Retrieval filters by the PostgreSQL-approved version state.
7. Revocation/deletion emits an outbox event to remove or disable derived points.
8. A reconciliation job finds orphaned vectors, missing vectors and stale ACL/index versions.

No distributed transaction is required. The PostgreSQL publication gate is authoritative.

### 9.4 Object storage consistency

- Create a quarantined version row before accepting the upload.
- Store the file privately and verify checksum.
- Mark the row stored only after the object exists and checksum matches.
- Cleanup orphan objects after failed database finalization.
- Never expose source_uri directly to the client; use an authorized short-lived source reference.

### 9.5 Answer persistence

- Generate and validate the answer in the worker.
- In one database transaction, create the assistant message, citations and query-job completion update.
- Use a unique query-job/request-message guard so a retry cannot create two final answers.
- If the worker crashes before this transaction, lease recovery may retry the safe workflow according to the job state.

## 10. Row-Level Security proposal

RLS is PROPOSED defense-in-depth and requires an ADR/security review.

For tenant-owned tables:

- Set a trusted transaction-local tenant context only after the Core authenticates the request.
- Require the database role to see rows whose tenant_id matches that context.
- Use separate worker roles with least privilege.
- Do not allow a client to set tenant context directly.
- Keep PDP/PEP checks in the application and worker trust interface.
- Test RLS with cross-tenant, anonymous, revoked and worker-service scenarios.

If the chosen deployment uses one database per tenant, retain tenant_id for schema-level invariants and portability; do not silently remove it.

## 11. Migration plan

No migration exists today. The following is a proposed forward-only sequence, not evidence of completed implementation:

1. 001_identity_tenants: TENANTS, USERS, DEPARTMENTS, TENANT_MEMBERSHIPS, ROLES, MEMBERSHIP_ROLES, AUTH_SESSIONS.
2. 002_documents: DOCUMENTS, DOCUMENT_VERSIONS, DOCUMENT_APPROVALS, DOCUMENT_ACCESS_GRANTS, CHUNKS.
3. 003_jobs_and_conversations: CONVERSATIONS, MESSAGES, QUERY_JOBS, AGENT_EXECUTION_STEPS, MAINTENANCE_WINDOWS.
4. 004_audit_and_delivery: AUDIT_EVENTS, OUTBOX_EVENTS, ANSWER_CITATIONS, FEEDBACK.
5. 005_indexes_and_rls: approved indexes, constraints and RLS policies after testing.

Migration rules:

- Do not modify an already-applied migration.
- Add forward-compatible columns before enforcing non-null constraints on existing data.
- Backfill tenant/membership ownership before enabling composite foreign keys.
- Validate constraints before making them fully enforced.
- Do not drop old columns or purge data without an approved retention/backfill plan.
- Test rollback strategy on disposable environments; do not claim production rollback safety from a document.

## 12. Testing plan

The following tests are required before database implementation is considered integrated.

### Schema and data integrity

- Primary/foreign key enforcement.
- Tenant composite-FK mismatch rejection.
- Unique version, chunk, idempotency and citation-order rules.
- Approval stage and lifecycle check constraints.
- Historical citation resolution after a new version is published.

### Tenant and authorization

- Cross-tenant membership, document, conversation, citation and audit reads are rejected.
- Anonymous sessions cannot read internal or another session’s conversation.
- Revoked memberships and document grants affect source/citation/cache paths.
- RLS tests, if approved, cannot be bypassed by client-provided tenant context.

### Query jobs

- Job creation and request-message linkage.
- Concurrent claims allow one active lease.
- Lease expiry recovery.
- Stale revision/checkpoint rejection.
- Retry scheduling and max-attempt failure.
- Idempotent final answer and citation persistence.
- Maintenance pause/resume without false FAILED state.
- Ordinary failed jobs require user resubmission.

### Ingestion and indexing

- Successful staged ingestion and two-review publication.
- Failed/cancelled ingestion cleanup.
- No partial or unapproved version in retrieval scope.
- Deterministic vector-point binding and reconciliation.
- Revoked/superseded version invalidation.

### Audit and privacy

- Append-only event behavior.
- No passwords, tokens, raw confidential files or hidden reasoning in safe_metadata.
- Trace correlation across Core, queue, worker, model and citation actions.

Current verification status:

| Check | Status |
|---|---|
| Repository inspection | PASS — design files and task dependencies inspected |
| Database migration execution | NOT RUN — no migration exists |
| PostgreSQL schema execution | NOT RUN — no schema exists |
| RLS test | NOT RUN — no RLS policy exists |
| Database integration tests | NOT RUN — test directories contain placeholders only |
| Production readiness | NOT CLAIMED |

## 13. Remaining risks and approval blockers

1. Tenant scope: current product deployment is single-enterprise, while this schema is multi-tenant-ready. Owner must confirm whether shared multi-tenant runtime is out of MVP while tenant-aware storage remains required.
2. Policy precedence: Chairman, department, role and document-grant precedence is still pending.
3. RLS: choose between RLS defense-in-depth, application-only policy, or both.
4. Maintenance: confirm global chatbot pause and exact checkpoint/resume semantics.
5. Queue: broker, priority fairness, worker concurrency and delivery semantics remain pending.
6. Database technology: PostgreSQL is the target and Alembic is the owner-provided migration-tool proposal; the exact driver and deployment topology remain pending.
7. Vector/search: Qdrant and lexical index ownership/reconciliation details require an approved contract.
8. Retention: audit, conversations, versions, chunks, backups and permanent deletion require approved retention/legal-hold rules.
9. Feedback: decide whether anonymous or authenticated users may submit multiple feedback records per message.
10. Circular active-version reference: current_active_version_id needs a deferrable composite FK strategy; if the migration tool cannot support it, use a dedicated document-head table rather than weakening the invariant.

## 14. Dependency-aware next steps

1. Owner reviews and approves this Database V2 proposal or records changes.
2. ARCH-001 finalizes architecture/ADR decisions.
3. CONTRACT-001 reviews and proposes identity, document, retrieval, job, citation, audit and cross-runtime schemas; the Project Owner approves them.
4. INFRA-002 produces the cloud/secrets readiness report without creating accounts, keys or paid resources.
5. DevOps completes INFRA-BOOT-001 to prepare an isolated temporary PostgreSQL service for DB-001 before INFRA-001; it requires no production account or data. Backend defines and tests migrations.
6. After DB-001 is DONE, INFRA-001 wires the Backend-owned migrations into reproducible development services.
7. KNOW-001 adds document/version/chunk models and ACL inheritance tests. Any later schema changes require a new Backend-owned migration task; DB-001 remains a completed historical task.
8. AUTH-001 adds policy enforcement against the approved membership/grant model.
9. ING-001 adds quarantine-to-ACTIVE processing and vector reconciliation.
10. Add integration/security tests before marking the database tasks DONE.

## 15. Change summary

### Created

- database/database.md — this proposed Database Architecture V2.

### Modified

- None.

### Tables introduced by this design

- TENANTS
- USERS
- DEPARTMENTS
- TENANT_MEMBERSHIPS
- ROLES
- MEMBERSHIP_ROLES
- AUTH_SESSIONS
- CONVERSATIONS
- MESSAGES
- QUERY_JOBS
- AGENT_EXECUTION_STEPS
- MAINTENANCE_WINDOWS
- DOCUMENTS
- DOCUMENT_VERSIONS
- DOCUMENT_APPROVALS
- CHUNKS
- INGESTION_JOBS
- DOCUMENT_ACCESS_GRANTS
- AUDIT_EVENTS
- OUTBOX_EVENTS
- ANSWER_CITATIONS
- FEEDBACK

### Not introduced

- No PostgreSQL migration.
- No ORM model.
- No database repository/service.
- No Qdrant schema change.
- No queue deployment.
- No task-status update.
- No production claim.

## 16. Owner-provided database alignment

The database design now follows the owner-provided Q1–Q34 proposal baseline:

- The MVP has one enterprise deployment, but every tenant-owned row carries tenant scope so a later enterprise can receive an isolated corpus and identity set.
- PostgreSQL 17 is the target authoritative store. It owns users, memberships, departments, roles, ACL inputs, documents, versions, jobs, queue leases, checkpoints, conversations, citations, feedback and audit metadata.
- `QUERY_JOBS` is also the MVP durable queue. Workers claim work with leases/heartbeat and safe `SKIP LOCKED` semantics; Redis is not authoritative for checkpoints.
- Query priority is Chairman, then Website Manager/System Admin, then authenticated employee, then anonymous. Emergency control jobs use a separate path.
- Initial configurable limits are 20 concurrent RAG jobs, 2 ingestion jobs and 200 queued query jobs. Saturation is represented by API `503`/`Retry-After`, not maintenance mode.
- Job states are `QUEUED`, `RUNNING`, `PAUSED`, `RETRY_SCHEDULED`, `COMPLETED`, `FAILED` and `CANCELLED`. `MAINTENANCE` is a system mode.
- Durable checkpoints store workflow stage, job ID, source/version IDs, policy version, attempt and timestamps. Resume requires tenant, ACL, policy and version rechecks.
- Upload versions accept `.pdf`, `.docx` and `.xlsx`, with a 200,000,000-byte limit. Review approval expires after 30 minutes; maintenance has a configurable 60-minute watchdog and never auto-approves.
- Retry attempts are idempotent and bounded to three attempts per unchanged document version. A failed version cannot replace the prior ACTIVE version.
- Product classification remains `PUBLIC`/`INTERNAL` for MVP. The stricter egress handling for unknown or future higher-sensitivity data belongs to policy metadata and is not silently exposed as a new MVP UI classification.
- Alembic is the single migration owner for the Python/FastAPI MVP. Any future Rust runtime must share the same migration history.

