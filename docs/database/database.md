# Database Architecture V2 — Enterprise Agentic RAG

**Document ID:** DB-ARCH-V2-001  
**Status:** APPROVED BASELINE — DB-001 migration implementation ready for integration review
**Version:** 2.0  
**Date:** 2026-11-09  
**Target:** PostgreSQL authoritative relational store

> This document is the approved relational source of truth for DB-001. Alembic migrations implement the authoritative schema; ORM models, RLS runtime policy, queues and production resources remain separate concerns.

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

DB-001 now provides the Backend-owned Alembic migration baseline. ORM models, repositories, runtime RLS policy and database QA remain separate implementation/integration concerns. The seven ordered Alembic revisions include durable employee onboarding requests (`0006_access_requests`) and local credential/rate-limit state (`0007_identity_credentials`).

## 2. Gap analysis

| Existing component | Current state | Identified gap | Database V2 response |
|---|---|---|---|
| backend/app/db/migrations | Seven ordered Alembic revisions | Migration baseline must remain Backend-owned and reversible | Implement and test migration order, constraints and rollback |
| Architecture overview | Defines Core, workers, jobs, maintenance and data ownership | No relational ERD or database invariants | Add tenant, job, lifecycle, checkpoint and consistency design |
| Contracts | Proposal-level identity, document, ingestion, retrieval, cache and audit contracts | No complete relational ownership or composite tenant rules | Map each contract to authoritative tables and constraints |
| Tasks | ARCH-001, CONTRACT-001, DB-001 and DB-QA-001 DONE | Runtime repositories, policy enforcement and RLS remain downstream | Keep migration ownership in Backend and review QA separately |
| Worker workflows | Async RAG and ingestion flows are documented | No durable job lease, checkpoint, idempotency or outbox model | Add QUERY_JOBS, INGESTION_JOBS, AGENT_EXECUTION_STEPS and OUTBOX_EVENTS |
| Tests | Migration upgrade/rollback evidence and DB-QA-001 evidence exist | Runtime authorization/RLS and full integration still need downstream evidence | Keep migration, schema and security QA reproducible |
| Current ERD/database docs | This file is the approved relational source | Runtime repositories and policy enforcement are downstream | Keep this file synchronized with Backend-owned revisions |

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

    ANONYMOUS_SESSIONS {
        uuid id PK
        uuid tenant_id FK
        string session_hash
        timestamptz created_at
        timestamptz last_seen_at
        timestamptz expires_at
        timestamptz revoked_at
    }

    ACCESS_REQUESTS {
        uuid id PK
        uuid tenant_id FK
        string requester_id
        string full_name
        string email
        string department
        string reason
        boolean consent
        string status
        string reviewed_by
        timestamptz reviewed_at
        timestamptz created_at
    }

    DOCUMENTS {
        uuid id PK
        uuid tenant_id FK
        uuid owner_department_id FK
        uuid created_by_membership_id FK
        string title
        string classification
        string status
        timestamptz created_at
        timestamptz updated_at
    }

    DOCUMENT_HEADS {
        uuid tenant_id PK, FK
        uuid document_id PK, FK
        uuid active_version_id FK
        bigint corpus_epoch
        string index_generation
        bigint fencing_token
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
        string attempt_id
        string content_sha256
        string lease_id
        bigint fencing_token
        int expected_chunk_count
        string chunk_digest
        string acl_digest
        string index_generation
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
        string lease_id
        bigint fencing_token
        timestamptz heartbeat_at
        timestamptz lease_expires_at
        timestamptz workflow_deadline_at
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
        string lease_id
        bigint fencing_token
        timestamptz lease_expires_at
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
        jsonb source_locator
        string evidence_snapshot_hash
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
        string request_id
        string action
        string decision
        string traceparent
        bigint policy_epoch
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
        bigint sequence_no
        timestamptz acknowledged_at
        string status
        int attempt_count
        timestamptz available_at
        timestamptz published_at
    }

    IDEMPOTENCY_KEYS {
        uuid id PK
        uuid tenant_id FK
        string operation
        string resource_key
        string idempotency_key
        string request_fingerprint
        int response_status
        jsonb safe_response
        timestamptz expires_at
    }

    AUTHORIZED_SCOPES {
        uuid id PK
        uuid tenant_id FK
        string scope_hash
        string audience
        uuid principal_id FK
        bigint policy_epoch
        string classification_max
        jsonb document_version_filter
        string policy_decision_ref
        timestamptz issued_at
        timestamptz expires_at
        timestamptz revoked_at
    }

    OUTBOX_CONSUMER_WATERMARKS {
        uuid id PK
        uuid tenant_id FK
        string consumer_name
        string aggregate_type
        uuid aggregate_id FK
        bigint applied_sequence_no
        timestamptz last_acknowledged_at
        timestamptz freshness_deadline
    }

    WORKER_REPLAY_NONCES {
        uuid id PK
        string worker_jti_hash
        string worker_id
        timestamptz expires_at
        timestamptz first_seen_at
    }

    INDEX_PUBLICATIONS {
        uuid id PK
        uuid tenant_id FK
        uuid version_id FK
        string publication_id
        string content_sha256
        int expected_chunk_count
        string chunk_digest
        string acl_digest
        string index_generation
        string status
        bigint fencing_token
    }

    REVOCATION_TOMBSTONES {
        uuid id PK
        uuid tenant_id FK
        string revocation_id
        string resource_type
        uuid resource_id
        uuid version_id FK
        bigint epoch
        bigint sequence_no
        string reason
        timestamptz issued_at
    }

    TENANTS ||--o{ DEPARTMENTS : contains
    TENANTS ||--o{ TENANT_MEMBERSHIPS : has
    USERS ||--o{ TENANT_MEMBERSHIPS : joins
    DEPARTMENTS o|--o{ TENANT_MEMBERSHIPS : assigns
    TENANT_MEMBERSHIPS ||--o{ MEMBERSHIP_ROLES : receives
    ROLES ||--o{ MEMBERSHIP_ROLES : grants
    USERS ||--o{ AUTH_SESSIONS : opens
    TENANTS ||--o{ AUTH_SESSIONS : scopes
    TENANTS ||--o{ ANONYMOUS_SESSIONS : scopes
    TENANTS ||--o{ ACCESS_REQUESTS : receives

    TENANTS ||--o{ DOCUMENTS : owns
    DEPARTMENTS o|--o{ DOCUMENTS : owns
    TENANT_MEMBERSHIPS ||--o{ DOCUMENTS : creates
    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : versions
    DOCUMENTS ||--o| DOCUMENT_HEADS : owns
    DOCUMENT_HEADS ||--o| DOCUMENT_VERSIONS : points_to_active
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
    TENANTS ||--o{ IDEMPOTENCY_KEYS : owns
    TENANTS ||--o{ AUTHORIZED_SCOPES : issues
    TENANTS ||--o{ INDEX_PUBLICATIONS : publishes
    TENANTS ||--o{ REVOCATION_TOMBSTONES : revokes
    TENANTS ||--o{ OUTBOX_CONSUMER_WATERMARKS : tracks
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
| IDEMPOTENCY_KEYS | Persist request fingerprints and safe replay responses across API/worker retries. |
| AUTHORIZED_SCOPES | Store opaque, expiring, audience-bound retrieval capabilities and policy epochs. |
| WORKER_REPLAY_NONCES | Reject replayed worker JWT identifiers without retaining raw tokens. |
| INDEX_PUBLICATIONS | Gate cross-system publication with checksum, ACL digest, chunk manifest and fencing. |
| REVOCATION_TOMBSTONES | Replay ordered revocations before retrieval, cache or source delivery. |
| OUTBOX_CONSUMER_WATERMARKS | Track per-consumer applied sequence and freshness; global acknowledgement is insufficient for cache safety. |

## 5. Table responsibilities and key columns

### 5.1 Identity and tenant management

- TENANTS: immutable tenant identity, deployment status and configuration boundary.
- USERS: global login identity. Email is normalized and unique. No tenant_id. Local password/MFA hashes are stored only in the backend database when local authentication is enabled; raw credentials are never returned.
- DEPARTMENTS: tenant-owned department catalog.
- TENANT_MEMBERSHIPS: user-to-tenant relationship, membership status, primary department, activation/revocation timestamps.
- ROLES: controlled role catalog such as employee, chairman, website_manager and system_admin.
- MEMBERSHIP_ROLES: many-to-many tenant role assignments.
- AUTH_SESSIONS: hashed session/token records, expiry, revocation and last-use metadata. Store no raw token.
- AUTH_FAILURES: durable bounded failed-attempt and lockout state keyed by normalized email.

Security rule: a user is authorized in a tenant only through an active TENANT_MEMBERSHIPS row. Anonymous users have no membership and can use only the trusted public tenant route.

ANONYMOUS_SESSIONS:

- `session_hash` is server-issued and unique per tenant; clients never choose a tenant or raw session identifier.
- `last_seen_at` and `expires_at` enforce 30-minute idle expiry and the configured maximum lifetime; revoked sessions fail closed.
- Conversation rows reference the session hash/session record and cannot be rebound silently to an authenticated user.

ACCESS_REQUESTS:

- Stores employee onboarding requests durably inside the requested tenant boundary.
- `status` is `PENDING_ADMIN_REVIEW`, `APPROVED_PENDING_PROVISIONING` or `REJECTED`; approval does not itself create an identity or grant document access.
- Applicant details are visible only through the manager-authorized review API; conversation bodies are never part of this table.
- Idempotency for create/review mutations is recorded in `IDEMPOTENCY_KEYS` with the tenant and operation namespace.

### 5.2 Conversations and execution

CONVERSATIONS:

- tenant_id is mandatory.
- user_id is nullable only for anonymous conversations.
- anonymous_session_hash/session reference is required when user_id is null.
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
- lease_id, fencing_token and heartbeat_at reject stale workers; workflow_deadline_at is immutable for the job.
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
- The dedicated DOCUMENT_HEADS row is the authoritative current-version pointer and stores corpus/index epochs; it is nullable only during initial upload.

DOCUMENT_VERSIONS:

- version_number is unique per document.
- source_uri points to private object storage; PostgreSQL does not hold original PDF/Word/Excel binaries.
- sha256 identifies the uploaded source.
- processing_status and publication_status are separate so a parsed version cannot be mistaken for a published version.
- A version is immutable after activation except for controlled lifecycle transitions.

DOCUMENT_APPROVALS:

- stage is 1 or 2.
- Each decision records reviewer membership, attempt number, decision, time and safe note.
- The same reviewer may perform both stages in MVP, but each stage is an independent authorized, idempotent decision; one request cannot auto-approve both stages.

CHUNKS:

- One immutable extracted chunk belongs to exactly one document version and tenant.
- chunk_index is unique within a version.
- parent_chunk_id must reference a chunk in the same tenant and version.
- content_text is bounded extracted text for retrieval/citation; original files remain in object storage.
- vector_point_id, index_version and index_status map the relational chunk to a derived Qdrant/search projection.
- Only chunks belonging to eligible ACTIVE versions may be returned by retrieval.
- Each staged index has a manifest with expected chunk count, chunk digest, ACL digest, checksum and index generation; publication is blocked until it matches.

INGESTION_JOBS:

- One or more attempts may process a version, but only one active attempt may hold the processing lease.
- current_stage records the last durable stage.
- checkpoint is resumable stage metadata, not an assumption of full workflow recovery.
- Failed, cancelled or superseded jobs must clean or quarantine derived artifacts before any publication.
- Retry policy is stage-aware: invalid input is terminal, transient processing may retry up to three times for the unchanged checksum, review is never auto-retried, and publication/cleanup use ordered outbox reconciliation.

### 5.4 Authorization, provenance and quality

DOCUMENT_ACCESS_GRANTS:

- Exactly one subject is set: membership, role or department.
- action is explicit, for example DOCUMENT_READ or SOURCE_DOWNLOAD.
- effect is ALLOW or DENY.
- Grants are tenant-scoped and must never cross a document’s tenant.
- PDP/PEP evaluates grants with role, department, document status, classification and policy epoch; explicit DENY overrides every ALLOW and unknown/stale values deny.

AUTHORIZED_SCOPES:

- `scope_hash` is the stored hash of the opaque scope reference; the raw reference is never persisted in logs.
- `classification_max`, `document_version_filter` and `policy_decision_ref` are required scope constraints produced by the authoritative policy store.
- A scope without a current policy decision reference, classification bound or version filter is invalid and denies.

ANSWER_CITATIONS:

- Links an assistant message to an immutable chunk and version.
- citation_order controls presentation; claim_order supports claim-level verification.
- The redundant version_id is enforced against CHUNKS with a composite foreign key.
- source_quote is optional, bounded and must come from the authorized chunk.
- source_locator is a PDF/DOCX/XLSX discriminated locator and evidence_snapshot_hash binds the citation to the immutable extracted evidence.

FEEDBACK:

- Links to an assistant message and optionally an active membership or anonymous session.
- rating is constrained to the approved set, for example POSITIVE or NEGATIVE.
- MVP rule: one feedback record per authenticated membership/message and one per anonymous session/message; identical repeats replay the original result and changed repeats are rejected.

AUDIT_EVENTS:

- Append-only by application policy.
- actor_membership_id is nullable for system events; actor_service identifies the trusted service.
- safe_metadata excludes passwords, tokens, raw confidential documents, full prompts and unnecessary personal data.
- traceparent and policy_epoch are first-class fields; trace_id is derived metadata only. Conversation body is never queryable through admin/operations audit paths.
- request_id, action and decision are typed columns; `safe_metadata` is bounded redacted operational context, not a substitute for authorization/audit fields.
- Retention and protected access are policy decisions, not database cascade behavior.

## 6. Constraints and referential behavior

### 6.1 Required constraints

- UUID primary key on all durable entities.
- Normalized lowercase unique USERS.email.
- Unique TENANTS.slug.
- Unique TENANT_MEMBERSHIPS(tenant_id, user_id).
- Unique ANONYMOUS_SESSIONS(tenant_id, session_hash).
- Unique DEPARTMENTS(tenant_id, code).
- Unique DOCUMENT_VERSIONS(tenant_id, document_id, version_number).
- Exactly one DOCUMENT_HEADS row per tenant/document and at most one ACTIVE DOCUMENT_VERSION per document; DB-001 must update the head and publication state in one transaction.
- Unique CHUNKS(tenant_id, version_id, chunk_index).
- Unique IDEMPOTENCY_KEYS(tenant_id, operation, resource_key, idempotency_key) and request fingerprint.
- Unique AUTHORIZED_SCOPES(scope_hash) while active; expiry/revocation is checked on every use.
- Unique WORKER_REPLAY_NONCES(worker_jti_hash) until expiry.
- Unique INDEX_PUBLICATIONS(tenant_id, publication_id) and REVOCATION_TOMBSTONES(tenant_id, revocation_id).
- Unique QUERY_JOBS(tenant_id, request_message_id).
- Unique AGENT_EXECUTION_STEPS(tenant_id, query_job_id, step_number, attempt_number).
- Exactly one non-null subject column in DOCUMENT_ACCESS_GRANTS.
- DOCUMENT_APPROVALS.stage in 1..2.
- Positive priority, attempt counts and version numbers.
- ended_at is null while a maintenance window is active.
- response_message_id cannot point to a message in another tenant or conversation.
- ANSWER_CITATIONS.version_id must match the cited CHUNKS.version_id.
- IDEMPOTENCY_KEYS.response_status and safe_response are immutable after first completion; a fingerprint mismatch is rejected.
- REVIEW_1 and REVIEW_2 events are independently idempotent; the same action cannot create two decisions.
- INDEX_PUBLICATIONS cannot become PUBLISHED unless checksum, chunk count/digest, ACL digest and index generation match.

### 6.2 Tenant-consistency constraints

Use composite foreign keys where parent and child are tenant-owned:

- (tenant_id, document_id) → DOCUMENTS(tenant_id, id).
- (tenant_id, version_id) → DOCUMENT_VERSIONS(tenant_id, id).
- (tenant_id, conversation_id) → CONVERSATIONS(tenant_id, id).
- (tenant_id, query_job_id) → QUERY_JOBS(tenant_id, id).
- (tenant_id, message_id) → MESSAGES(tenant_id, id).
- (tenant_id, membership_id) → TENANT_MEMBERSHIPS(tenant_id, id).
- (tenant_id, version_id) → INDEX_PUBLICATIONS(tenant_id, version_id) and REVOCATION_TOMBSTONES(tenant_id, version_id) where the version is present.

The database must not accept a valid UUID from a different tenant merely because the referenced row exists.

### 6.3 Delete behavior

- TENANTS: RESTRICT while any tenant-owned data exists.
- USERS: RESTRICT while memberships or sessions exist; use account deactivation instead of deletion by default.
- TENANT_MEMBERSHIPS: RESTRICT when referenced by audit, approval or historical records; revoke status instead.
- DOCUMENTS and DOCUMENT_VERSIONS: RESTRICT; use lifecycle states and controlled permanent-delete workflows.
- CHUNKS, citations and audit records: preserve historical evidence until approved retention/deletion policy permits removal.
- Sessions: revoke or expire; cascade deletion is acceptable only for non-audit session rows.
- Outbox events: retain until published or dead-lettered according to operational policy.
- IDEMPOTENCY_KEYS: expire after 24 hours unless an operation-specific contract requires a shorter bounded lifetime.
- WORKER_REPLAY_NONCES: expire after the token lifetime plus clock-skew allowance; store hashes only.

## 7. Index plan

Indexes should be added only for declared query patterns.

| Table | Index | Query purpose |
|---|---|---|
| TENANT_MEMBERSHIPS | (tenant_id, status, user_id) | Resolve active membership |
| TENANT_MEMBERSHIPS | (user_id, tenant_id) | List a user’s tenant memberships |
| AUTH_SESSIONS | (user_id, revoked_at, expires_at) | Session validation/revocation |
| ANONYMOUS_SESSIONS | UNIQUE (tenant_id, session_hash) | Anonymous session binding/expiry |
| ACCESS_REQUESTS | (tenant_id, status, created_at, id) | Manager review queue and tenant isolation |
| DOCUMENTS | (tenant_id, status, updated_at) | Current tenant catalog |
| DOCUMENT_VERSIONS | UNIQUE (tenant_id, document_id, version_number) | Version lookup |
| DOCUMENT_VERSIONS | Partial UNIQUE (tenant_id, document_id) WHERE publication_status = ACTIVE | One active version |
| DOCUMENT_HEADS | PRIMARY KEY (tenant_id, document_id) | Atomic active-version/epoch head |
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
| IDEMPOTENCY_KEYS | UNIQUE (tenant_id, operation, resource_key, idempotency_key) | Durable mutation replay |
| AUTHORIZED_SCOPES | (tenant_id, scope_hash, expires_at, revoked_at) | Scope validation/revocation |
| WORKER_REPLAY_NONCES | UNIQUE (worker_jti_hash) | Atomic worker replay consume |
| INDEX_PUBLICATIONS | UNIQUE (tenant_id, publication_id) | Cross-store publication gate |
| REVOCATION_TOMBSTONES | UNIQUE (tenant_id, revocation_id) | Ordered revocation replay |
| OUTBOX_CONSUMER_WATERMARKS | UNIQUE (tenant_id, consumer_name, aggregate_type, aggregate_id) | Per-consumer invalidation freshness |

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

DB-001 implements the following ordered, reversible Alembic sequence under `backend/app/db/migrations/versions`:

1. 001_identity_tenants: TENANTS, USERS, DEPARTMENTS, TENANT_MEMBERSHIPS, ROLES, MEMBERSHIP_ROLES, AUTH_SESSIONS.
2. 002_documents: DOCUMENTS, DOCUMENT_VERSIONS, DOCUMENT_APPROVALS, DOCUMENT_ACCESS_GRANTS, CHUNKS.
3. 003_jobs_and_conversations: CONVERSATIONS, MESSAGES, QUERY_JOBS, AGENT_EXECUTION_STEPS, MAINTENANCE_WINDOWS.
4. 004_audit_and_delivery: AUDIT_EVENTS, OUTBOX_EVENTS, ANSWER_CITATIONS, FEEDBACK.
5. 005_indexes: approved query-path indexes and uniqueness constraints. RLS remains a separate defense-in-depth decision.
6. 006_access_requests: durable employee access requests, manager review state and tenant/status queue index.
7. 007_identity_credentials: durable local password/MFA hashes and authentication rate-limit state; provider/SSO adapters remain separate.

Migration rules:

- Do not modify an already-applied migration.
- Add forward-compatible columns before enforcing non-null constraints on existing data.
- Backfill tenant/membership ownership before enabling composite foreign keys.
- Validate constraints before making them fully enforced.
- Do not drop old columns or purge data without an approved retention/backfill plan.
- Upgrade and downgrade have been executed on disposable PostgreSQL. This is not production rollback certification.

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
| Database migration execution | PASS — DB-001 upgrade 0001→0006 and downgrade to base |
| PostgreSQL schema execution | PASS — disposable PostgreSQL execution |
| RLS test | NOT RUN — no RLS policy exists |
| Database integration tests | PASS — DB-QA-001 four-family package, 40 cases |
| Production readiness | NOT CLAIMED |

## 13. Remaining implementation risks and approval blockers

1. Tenant scope: current product deployment is single-enterprise, while this schema is multi-tenant-ready. Owner must confirm whether shared multi-tenant runtime is out of MVP while tenant-aware storage remains required.
2. Policy precedence: v1 contract fixes Chairman, department, role and document-grant precedence; AUTH-001 and DB-QA-001 must verify the runtime boundary.
3. RLS: choose between RLS defense-in-depth, application-only policy, or both; application enforcement is mandatory either way.
4. Maintenance: v1 contract fixes global chatbot pause, durable owner/fencing and checkpoint/resume semantics; runtime integration remains downstream.
5. Queue: broker, priority fairness and worker concurrency remain implementation/benchmark decisions; PostgreSQL durable jobs remain the MVP authority.
6. Database technology: PostgreSQL is the target and Alembic is the owner-provided migration-tool proposal; the exact driver and deployment topology remain pending.
7. Vector/search: Qdrant and lexical index ownership/reconciliation details require an approved contract.
8. Retention: v1 contract fixes the current baseline retention/legal-hold behavior; DB-QA-001 and later lifecycle tasks must verify tombstone and permanent-delete safeguards.
9. Feedback: v1 contract fixes one feedback record per membership/message or anonymous session/message.
10. Active-version head: v2 chooses the dedicated DOCUMENT_HEADS table; DB-QA-001 and KNOW-001 must verify its composite key, fencing and one-active-version invariant.

## 14. Dependency-aware next steps

1. ARCH-001 and CONTRACT-001 are accepted; the v1.0 contract is the migration input.
2. INFRA-002 remains the cloud/secrets readiness boundary without creating accounts, keys or paid resources.
3. INFRA-BOOT-001 provides the isolated temporary PostgreSQL service; DB-001 defines and executes the Backend-owned migrations.
4. DB-QA-001 completed the four-family schema/migration QA package; DB-001 is DONE.
5. INFRA-001 wires the Backend-owned migrations into reproducible development services; its implementation and QA are DONE.
7. KNOW-001 adds document/version/chunk models and ACL inheritance tests. Any later schema changes require a new Backend-owned migration task; DB-001 remains a completed historical task.
8. AUTH-001 adds policy enforcement against the approved membership/grant model.
9. ING-001 adds quarantine-to-ACTIVE processing and vector reconciliation.
10. Keep application authorization, RLS and production rollback evidence in their owning downstream tasks.

## 15. Change summary

### Created

- database/database.md — approved Database Architecture V2 and relational source of truth.

### Modified

- DB-001 added the Backend-owned Alembic migration baseline and disposable execution evidence.

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

- No ORM model.
- No database repository/service.
- No Qdrant schema change.
- No queue deployment.
- No production deployment or RLS rollout claim.

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

