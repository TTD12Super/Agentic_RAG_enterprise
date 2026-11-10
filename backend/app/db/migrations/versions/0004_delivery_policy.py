"""Create provenance, policy scope, outbox and revocation tables."""

from alembic import op

revision = "0004_delivery_policy"
down_revision = "0003_jobs_conversations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE answer_citations (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            assistant_message_id uuid NOT NULL,
            chunk_id uuid NOT NULL,
            version_id uuid NOT NULL,
            citation_order integer NOT NULL CHECK (citation_order >= 0),
            claim_order integer NOT NULL CHECK (claim_order >= 0),
            source_locator jsonb NOT NULL,
            evidence_snapshot_hash text NOT NULL CHECK (evidence_snapshot_hash ~ '^[0-9a-fA-F]{64}$'),
            source_quote text,
            policy_epoch bigint NOT NULL CHECK (policy_epoch >= 0),
            audience text NOT NULL,
            expires_at timestamptz,
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, assistant_message_id, citation_order),
            FOREIGN KEY (tenant_id, assistant_message_id)
                REFERENCES messages(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, version_id, chunk_id)
                REFERENCES chunks(tenant_id, version_id, id) ON DELETE RESTRICT,
            CHECK (source_quote IS NULL OR length(source_quote) <= 12000)
        );
        CREATE TABLE feedback (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            message_id uuid NOT NULL,
            membership_id uuid,
            anonymous_session_hash text,
            rating text NOT NULL CHECK (rating IN ('POSITIVE', 'NEGATIVE')),
            comment text,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, message_id)
                REFERENCES messages(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, membership_id)
                REFERENCES tenant_memberships(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, anonymous_session_hash)
                REFERENCES anonymous_sessions(tenant_id, session_hash) ON DELETE RESTRICT,
            CHECK (((membership_id IS NOT NULL)::integer +
                    (anonymous_session_hash IS NOT NULL)::integer) = 1)
        );
        CREATE UNIQUE INDEX uq_feedback_membership_message
            ON feedback (tenant_id, message_id, membership_id)
            WHERE membership_id IS NOT NULL;
        CREATE UNIQUE INDEX uq_feedback_anonymous_message
            ON feedback (tenant_id, message_id, anonymous_session_hash)
            WHERE anonymous_session_hash IS NOT NULL;

        CREATE TABLE audit_events (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            actor_membership_id uuid,
            actor_service text,
            event_type text NOT NULL,
            resource_type text,
            resource_id uuid,
            outcome text NOT NULL CHECK (outcome IN ('ALLOW', 'DENY', 'SUCCESS', 'FAILURE')),
            request_id text NOT NULL,
            action text NOT NULL,
            decision text,
            traceparent text,
            policy_epoch bigint CHECK (policy_epoch IS NULL OR policy_epoch >= 0),
            trace_id text,
            safe_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
            occurred_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, actor_membership_id)
                REFERENCES tenant_memberships(tenant_id, id) ON DELETE RESTRICT,
            CHECK (actor_membership_id IS NOT NULL OR actor_service IS NOT NULL),
            CHECK (decision IS NULL OR decision IN ('ALLOW', 'DENY'))
        );

        CREATE TABLE outbox_events (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            aggregate_type text NOT NULL,
            aggregate_id uuid NOT NULL,
            event_type text NOT NULL,
            payload jsonb NOT NULL,
            sequence_no bigint NOT NULL CHECK (sequence_no > 0),
            status text NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING', 'PUBLISHED', 'DEAD_LETTER')),
            attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
            available_at timestamptz NOT NULL DEFAULT now(),
            claimed_by text,
            lease_expires_at timestamptz,
            published_at timestamptz,
            acknowledged_at timestamptz,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, aggregate_type, aggregate_id, event_type, sequence_no),
            CHECK (status <> 'PUBLISHED' OR published_at IS NOT NULL)
        );

        CREATE TABLE idempotency_keys (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            operation text NOT NULL,
            resource_key text NOT NULL,
            idempotency_key text NOT NULL CHECK (length(idempotency_key) >= 16),
            request_fingerprint text NOT NULL CHECK (length(request_fingerprint) >= 16),
            response_status integer CHECK (response_status IS NULL OR response_status BETWEEN 100 AND 599),
            safe_response jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz NOT NULL,
            UNIQUE (tenant_id, operation, resource_key, idempotency_key),
            CHECK (expires_at > created_at),
            CHECK ((response_status IS NULL) = (safe_response IS NULL))
        );

        CREATE TABLE authorized_scopes (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            scope_hash text NOT NULL,
            audience text NOT NULL,
            principal_id uuid,
            policy_epoch bigint NOT NULL CHECK (policy_epoch >= 0),
            classification_max text NOT NULL CHECK (classification_max IN ('PUBLIC', 'INTERNAL')),
            document_version_filter jsonb NOT NULL,
            policy_decision_ref text NOT NULL,
            issued_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz NOT NULL,
            revoked_at timestamptz,
            UNIQUE (tenant_id, id),
            CHECK (expires_at > issued_at),
            CHECK (revoked_at IS NULL OR revoked_at >= issued_at)
        );
        CREATE UNIQUE INDEX uq_authorized_scopes_active_hash
            ON authorized_scopes (scope_hash) WHERE revoked_at IS NULL;

        CREATE TABLE worker_replay_nonces (
            id uuid PRIMARY KEY,
            worker_jti_hash text NOT NULL UNIQUE,
            worker_id text NOT NULL,
            expires_at timestamptz NOT NULL,
            first_seen_at timestamptz NOT NULL DEFAULT now(),
            CHECK (expires_at > first_seen_at)
        );

        CREATE TABLE index_publications (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            version_id uuid NOT NULL,
            publication_id text NOT NULL,
            content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-fA-F]{64}$'),
            expected_chunk_count integer NOT NULL CHECK (expected_chunk_count >= 0),
            chunk_digest text NOT NULL,
            acl_digest text NOT NULL,
            index_generation text NOT NULL,
            status text NOT NULL DEFAULT 'PREPARING'
                CHECK (status IN ('PREPARING', 'READY', 'PUBLISHED', 'FAILED', 'REVOKED')),
            fencing_token bigint NOT NULL CHECK (fencing_token >= 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            published_at timestamptz,
            UNIQUE (tenant_id, publication_id),
            FOREIGN KEY (tenant_id, version_id)
                REFERENCES document_versions(tenant_id, id) ON DELETE RESTRICT,
            CHECK (status <> 'PUBLISHED' OR published_at IS NOT NULL)
        );

        CREATE TABLE revocation_tombstones (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            revocation_id text NOT NULL,
            resource_type text NOT NULL,
            resource_id uuid NOT NULL,
            version_id uuid,
            epoch bigint NOT NULL CHECK (epoch >= 0),
            sequence_no bigint NOT NULL CHECK (sequence_no > 0),
            reason text NOT NULL,
            issued_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, revocation_id),
            UNIQUE (tenant_id, resource_type, resource_id, sequence_no),
            FOREIGN KEY (tenant_id, version_id)
                REFERENCES document_versions(tenant_id, id) ON DELETE RESTRICT
        );

        CREATE TABLE outbox_consumer_watermarks (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            consumer_name text NOT NULL,
            aggregate_type text NOT NULL,
            aggregate_id uuid NOT NULL,
            applied_sequence_no bigint NOT NULL DEFAULT 0 CHECK (applied_sequence_no >= 0),
            last_acknowledged_at timestamptz,
            freshness_deadline timestamptz NOT NULL,
            UNIQUE (tenant_id, consumer_name, aggregate_type, aggregate_id)
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE outbox_consumer_watermarks;
        DROP TABLE revocation_tombstones;
        DROP TABLE index_publications;
        DROP TABLE worker_replay_nonces;
        DROP TABLE authorized_scopes;
        DROP TABLE idempotency_keys;
        DROP TABLE outbox_events;
        DROP TABLE audit_events;
        DROP TABLE feedback;
        DROP TABLE answer_citations;
        """
    )
