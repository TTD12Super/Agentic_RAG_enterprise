"""Create document lifecycle, ACL and chunk tables."""

from alembic import op

revision = "0002_documents"
down_revision = "0001_identity_tenants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE documents (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            owner_department_id uuid,
            created_by_membership_id uuid NOT NULL,
            title text NOT NULL CHECK (btrim(title) <> ''),
            classification text NOT NULL CHECK (classification IN ('PUBLIC', 'INTERNAL')),
            status text NOT NULL DEFAULT 'ACTIVE'
                CHECK (status IN ('ACTIVE', 'SOFT_DELETED', 'PURGED')),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, owner_department_id)
                REFERENCES departments(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, created_by_membership_id)
                REFERENCES tenant_memberships(tenant_id, id) ON DELETE RESTRICT
        );
        CREATE TABLE document_versions (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            document_id uuid NOT NULL,
            version_number integer NOT NULL CHECK (version_number > 0),
            source_uri text NOT NULL CHECK (source_uri LIKE 'private://%'),
            sha256 text NOT NULL CHECK (sha256 ~ '^[0-9a-fA-F]{64}$'),
            processing_status text NOT NULL DEFAULT 'UPLOADED'
                CHECK (processing_status IN (
                    'UPLOADED', 'QUARANTINED', 'REVIEW_1_APPROVED', 'PROCESSING',
                    'PROCESS_VALIDATED', 'PENDING_REVIEW_2', 'FAILED', 'REJECTED', 'CANCELLED'
                )),
            publication_status text NOT NULL DEFAULT 'NOT_PUBLISHED'
                CHECK (publication_status IN (
                    'NOT_PUBLISHED', 'ACTIVE', 'SUPERSEDED', 'REVOKED', 'SOFT_DELETED'
                )),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            activated_at timestamptz,
            superseded_at timestamptz,
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, document_id, id),
            UNIQUE (tenant_id, document_id, version_number),
            FOREIGN KEY (tenant_id, document_id)
                REFERENCES documents(tenant_id, id) ON DELETE RESTRICT,
            CHECK (publication_status <> 'ACTIVE' OR processing_status = 'PROCESS_VALIDATED'),
            CHECK (publication_status = 'ACTIVE' OR activated_at IS NULL OR activated_at <= now())
        );
        CREATE TABLE document_heads (
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            document_id uuid NOT NULL,
            active_version_id uuid,
            corpus_epoch bigint NOT NULL DEFAULT 0 CHECK (corpus_epoch >= 0),
            index_generation text NOT NULL DEFAULT '0',
            fencing_token bigint NOT NULL DEFAULT 0 CHECK (fencing_token >= 0),
            updated_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (tenant_id, document_id),
            FOREIGN KEY (tenant_id, document_id)
                REFERENCES documents(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, document_id, active_version_id)
                REFERENCES document_versions(tenant_id, document_id, id) ON DELETE RESTRICT
        );
        CREATE TABLE document_approvals (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            version_id uuid NOT NULL,
            reviewer_membership_id uuid NOT NULL,
            stage smallint NOT NULL CHECK (stage IN (1, 2)),
            attempt_number integer NOT NULL CHECK (attempt_number > 0),
            idempotency_key text NOT NULL,
            decision text NOT NULL CHECK (decision IN ('APPROVE', 'REJECT')),
            safe_note text,
            decided_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, version_id, stage, attempt_number),
            UNIQUE (tenant_id, version_id, stage, idempotency_key),
            FOREIGN KEY (tenant_id, version_id)
                REFERENCES document_versions(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, reviewer_membership_id)
                REFERENCES tenant_memberships(tenant_id, id) ON DELETE RESTRICT
        );
        CREATE TABLE document_access_grants (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            document_id uuid NOT NULL,
            membership_id uuid,
            role_id uuid,
            department_id uuid,
            action text NOT NULL CHECK (action IN ('DOCUMENT_READ', 'SOURCE_DOWNLOAD')),
            effect text NOT NULL CHECK (effect IN ('ALLOW', 'DENY')),
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, document_id)
                REFERENCES documents(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, membership_id)
                REFERENCES tenant_memberships(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, department_id)
                REFERENCES departments(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
            CHECK (((membership_id IS NOT NULL)::integer +
                    (role_id IS NOT NULL)::integer +
                    (department_id IS NOT NULL)::integer) = 1)
        );
        CREATE TABLE chunks (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            version_id uuid NOT NULL,
            parent_chunk_id uuid,
            chunk_index integer NOT NULL CHECK (chunk_index >= 0),
            content_text text NOT NULL CHECK (length(content_text) <= 200000),
            content_hash text NOT NULL CHECK (content_hash ~ '^[0-9a-fA-F]{64}$'),
            page_start integer,
            page_end integer,
            source_locator jsonb NOT NULL DEFAULT '{}'::jsonb,
            vector_point_id text,
            index_version text,
            index_status text NOT NULL DEFAULT 'STAGING'
                CHECK (index_status IN ('STAGING', 'ACTIVE', 'REMOVED')),
            UNIQUE (tenant_id, version_id, id),
            UNIQUE (tenant_id, version_id, chunk_index),
            FOREIGN KEY (tenant_id, version_id)
                REFERENCES document_versions(tenant_id, id) ON DELETE RESTRICT,
            FOREIGN KEY (tenant_id, version_id, parent_chunk_id)
                REFERENCES chunks(tenant_id, version_id, id) ON DELETE RESTRICT,
            CHECK (parent_chunk_id IS NULL OR parent_chunk_id <> id),
            CHECK (page_start IS NULL OR page_start > 0),
            CHECK (page_end IS NULL OR page_end >= COALESCE(page_start, page_end)),
            CHECK (index_status <> 'ACTIVE' OR (vector_point_id IS NOT NULL AND index_version IS NOT NULL))
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE chunks;
        DROP TABLE document_access_grants;
        DROP TABLE document_approvals;
        DROP TABLE document_heads;
        DROP TABLE document_versions;
        DROP TABLE documents;
        """
    )
