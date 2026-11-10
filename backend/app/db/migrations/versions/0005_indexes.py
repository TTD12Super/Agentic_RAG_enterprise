"""Add query-path indexes for the authoritative schema."""

from alembic import op

revision = "0005_indexes"
down_revision = "0004_delivery_policy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_memberships_active
            ON tenant_memberships (tenant_id, status, user_id);
        CREATE INDEX ix_memberships_user_tenant
            ON tenant_memberships (user_id, tenant_id);
        CREATE INDEX ix_auth_sessions_user_state
            ON auth_sessions (user_id, revoked_at, expires_at);
        CREATE INDEX ix_documents_catalog
            ON documents (tenant_id, status, updated_at);
        CREATE UNIQUE INDEX uq_document_versions_active
            ON document_versions (tenant_id, document_id)
            WHERE publication_status = 'ACTIVE';
        CREATE INDEX ix_document_versions_reconciliation
            ON document_versions (tenant_id, publication_status, updated_at);
        CREATE INDEX ix_chunks_index_state
            ON chunks (tenant_id, version_id, index_status);
        CREATE UNIQUE INDEX uq_chunks_vector_binding
            ON chunks (tenant_id, vector_point_id, index_version)
            WHERE vector_point_id IS NOT NULL AND index_version IS NOT NULL;
        CREATE INDEX ix_ingestion_queue
            ON ingestion_jobs (tenant_id, status, current_stage, created_at);
        CREATE INDEX ix_query_queue
            ON query_jobs (tenant_id, status, priority DESC, queued_at);
        CREATE INDEX ix_query_lease_recovery
            ON query_jobs (tenant_id, lease_expires_at)
            WHERE status = 'RUNNING';
        CREATE INDEX ix_agent_steps_job
            ON agent_execution_steps (tenant_id, query_job_id, step_number);
        CREATE INDEX ix_conversations_user
            ON conversations (tenant_id, user_id, created_at);
        CREATE INDEX ix_citations_message
            ON answer_citations (tenant_id, assistant_message_id, citation_order);
        CREATE INDEX ix_audit_tenant_time
            ON audit_events (tenant_id, occurred_at);
        CREATE INDEX ix_audit_trace_time
            ON audit_events (trace_id, occurred_at);
        CREATE INDEX ix_outbox_dispatch
            ON outbox_events (status, available_at, created_at);
        CREATE INDEX ix_idempotency_expiry
            ON idempotency_keys (tenant_id, expires_at);
        CREATE INDEX ix_authorized_scopes_validation
            ON authorized_scopes (tenant_id, scope_hash, expires_at, revoked_at);
        CREATE INDEX ix_index_publications_version
            ON index_publications (tenant_id, version_id, status);
        CREATE INDEX ix_revocation_replay
            ON revocation_tombstones (tenant_id, resource_type, resource_id, sequence_no);
        CREATE INDEX ix_watermark_freshness
            ON outbox_consumer_watermarks (tenant_id, freshness_deadline);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX ix_watermark_freshness;
        DROP INDEX ix_revocation_replay;
        DROP INDEX ix_index_publications_version;
        DROP INDEX ix_authorized_scopes_validation;
        DROP INDEX ix_idempotency_expiry;
        DROP INDEX ix_outbox_dispatch;
        DROP INDEX ix_audit_trace_time;
        DROP INDEX ix_audit_tenant_time;
        DROP INDEX ix_citations_message;
        DROP INDEX ix_conversations_user;
        DROP INDEX ix_agent_steps_job;
        DROP INDEX ix_query_lease_recovery;
        DROP INDEX ix_query_queue;
        DROP INDEX ix_ingestion_queue;
        DROP INDEX uq_chunks_vector_binding;
        DROP INDEX ix_chunks_index_state;
        DROP INDEX ix_document_versions_reconciliation;
        DROP INDEX uq_document_versions_active;
        DROP INDEX ix_documents_catalog;
        DROP INDEX ix_auth_sessions_user_state;
        DROP INDEX ix_memberships_user_tenant;
        DROP INDEX ix_memberships_active;
        """
    )
