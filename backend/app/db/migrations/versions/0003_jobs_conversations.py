"""Create durable jobs, conversations and maintenance coordination."""

from alembic import op

revision = "0003_jobs_conversations"
down_revision = "0002_documents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE maintenance_windows (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            started_by_membership_id uuid NOT NULL,
            lease_id text NOT NULL,
            fencing_token bigint NOT NULL CHECK (fencing_token >= 0),
            lease_expires_at timestamptz NOT NULL,
            status text NOT NULL DEFAULT 'ACTIVE'
                CHECK (status IN ('ACTIVE', 'RELEASED', 'EXPIRED', 'CANCELLED')),
            reason text NOT NULL CHECK (btrim(reason) <> ''),
            started_at timestamptz NOT NULL DEFAULT now(),
            ended_at timestamptz,
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, lease_id),
            FOREIGN KEY (tenant_id, started_by_membership_id)
                REFERENCES tenant_memberships(tenant_id, id) ON DELETE RESTRICT,
            CHECK (status = 'ACTIVE' OR ended_at IS NOT NULL),
            CHECK (status = 'ACTIVE' OR lease_expires_at >= started_at)
        );
        CREATE UNIQUE INDEX uq_maintenance_windows_active
            ON maintenance_windows (tenant_id) WHERE status = 'ACTIVE';

        CREATE TABLE ingestion_jobs (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            version_id uuid NOT NULL,
            status text NOT NULL DEFAULT 'QUEUED'
                CHECK (status IN ('QUEUED', 'RUNNING', 'PAUSED', 'RETRY_SCHEDULED', 'COMPLETED', 'FAILED', 'CANCELLED')),
            current_stage text NOT NULL DEFAULT 'FILE_VALIDATION'
                CHECK (current_stage IN ('FILE_VALIDATION', 'STORED', 'PARSING', 'CHUNKING', 'EMBEDDING', 'VECTOR_INDEXING', 'INDEX_VALIDATION')),
            attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0 AND attempt_count <= 3),
            attempt_id text NOT NULL,
            content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-fA-F]{64}$'),
            lease_id text,
            fencing_token bigint NOT NULL DEFAULT 0 CHECK (fencing_token >= 0),
            expected_chunk_count integer CHECK (expected_chunk_count IS NULL OR expected_chunk_count >= 0),
            chunk_digest text,
            acl_digest text,
            index_generation text,
            checkpoint jsonb,
            error_code text,
            created_at timestamptz NOT NULL DEFAULT now(),
            started_at timestamptz,
            completed_at timestamptz,
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, attempt_id),
            FOREIGN KEY (tenant_id, version_id)
                REFERENCES document_versions(tenant_id, id) ON DELETE RESTRICT,
            CHECK (status <> 'RUNNING' OR lease_id IS NOT NULL),
            CHECK (status NOT IN ('COMPLETED', 'FAILED', 'CANCELLED') OR completed_at IS NOT NULL)
        );
        CREATE UNIQUE INDEX uq_ingestion_jobs_active_version
            ON ingestion_jobs (tenant_id, version_id)
            WHERE status IN ('QUEUED', 'RUNNING', 'PAUSED', 'RETRY_SCHEDULED');

        CREATE TABLE conversations (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            user_id uuid REFERENCES users(id) ON DELETE RESTRICT,
            anonymous_session_hash text,
            status text NOT NULL DEFAULT 'ACTIVE'
                CHECK (status IN ('ACTIVE', 'ARCHIVED', 'DELETED')),
            created_at timestamptz NOT NULL DEFAULT now(),
            last_activity_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, anonymous_session_hash)
                REFERENCES anonymous_sessions(tenant_id, session_hash) ON DELETE RESTRICT,
            CHECK ((user_id IS NULL) = (anonymous_session_hash IS NOT NULL))
        );
        CREATE TABLE messages (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            conversation_id uuid NOT NULL,
            role text NOT NULL CHECK (role IN ('USER', 'ASSISTANT', 'SYSTEM', 'TOOL')),
            content text NOT NULL,
            answer_status text,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, conversation_id, id),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, conversation_id)
                REFERENCES conversations(tenant_id, id) ON DELETE RESTRICT,
            CHECK (answer_status IS NULL OR answer_status IN ('DRAFT', 'COMPLETED', 'FAILED', 'BLOCKED'))
        );
        CREATE INDEX ix_messages_conversation_created
            ON messages (tenant_id, conversation_id, created_at, id);

        CREATE TABLE query_jobs (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            conversation_id uuid NOT NULL,
            request_message_id uuid NOT NULL,
            response_message_id uuid,
            maintenance_window_id uuid,
            status text NOT NULL DEFAULT 'QUEUED'
                CHECK (status IN ('QUEUED', 'RUNNING', 'PAUSED', 'RETRY_SCHEDULED', 'COMPLETED', 'FAILED', 'CANCELLED')),
            priority integer NOT NULL DEFAULT 100 CHECK (priority > 0),
            attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
            max_attempts integer NOT NULL DEFAULT 3 CHECK (max_attempts > 0),
            revision bigint NOT NULL DEFAULT 0 CHECK (revision >= 0),
            checkpoint jsonb,
            checkpoint_schema_version text,
            worker_id text,
            lease_id text,
            fencing_token bigint NOT NULL DEFAULT 0 CHECK (fencing_token >= 0),
            heartbeat_at timestamptz,
            lease_expires_at timestamptz,
            workflow_deadline_at timestamptz NOT NULL,
            queued_at timestamptz NOT NULL DEFAULT now(),
            next_retry_at timestamptz,
            idempotency_key text CHECK (idempotency_key IS NULL OR length(idempotency_key) >= 16),
            created_at timestamptz NOT NULL DEFAULT now(),
            completed_at timestamptz,
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, conversation_id, request_message_id),
            FOREIGN KEY (tenant_id, conversation_id)
                REFERENCES conversations(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, conversation_id, request_message_id)
                REFERENCES messages(tenant_id, conversation_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, conversation_id, response_message_id)
                REFERENCES messages(tenant_id, conversation_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, maintenance_window_id)
                REFERENCES maintenance_windows(tenant_id, id) ON DELETE RESTRICT,
            CHECK (response_message_id IS NULL OR response_message_id <> request_message_id),
            CHECK ((checkpoint IS NULL) = (checkpoint_schema_version IS NULL)),
            CHECK (status <> 'RUNNING' OR lease_id IS NOT NULL),
            CHECK (status NOT IN ('COMPLETED', 'FAILED', 'CANCELLED') OR completed_at IS NOT NULL)
        );
        CREATE UNIQUE INDEX uq_query_jobs_idempotency
            ON query_jobs (tenant_id, idempotency_key)
            WHERE idempotency_key IS NOT NULL;

        CREATE TABLE agent_execution_steps (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            query_job_id uuid NOT NULL,
            step_number integer NOT NULL CHECK (step_number >= 0),
            attempt_number integer NOT NULL CHECK (attempt_number > 0),
            step_type text NOT NULL,
            status text NOT NULL CHECK (status IN ('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'SKIPPED')),
            provider_code text,
            model_name text,
            safe_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
            error_code text,
            started_at timestamptz,
            completed_at timestamptz,
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, query_job_id, step_number, attempt_number),
            FOREIGN KEY (tenant_id, query_job_id)
                REFERENCES query_jobs(tenant_id, id) ON DELETE RESTRICT
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE agent_execution_steps;
        DROP TABLE query_jobs;
        DROP TABLE messages;
        DROP TABLE conversations;
        DROP TABLE ingestion_jobs;
        DROP TABLE maintenance_windows;
        """
    )
