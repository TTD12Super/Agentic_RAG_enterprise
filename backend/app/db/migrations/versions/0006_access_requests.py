"""Persist employee access requests and their review state."""

from alembic import op

revision = "0006_access_requests"
down_revision = "0005_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE access_requests (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            requester_id text NOT NULL CHECK (btrim(requester_id) <> ''),
            full_name text NOT NULL CHECK (btrim(full_name) <> ''),
            email text NOT NULL CHECK (email = lower(btrim(email)) AND email <> ''),
            department text NOT NULL CHECK (btrim(department) <> ''),
            reason text NOT NULL CHECK (btrim(reason) <> ''),
            consent boolean NOT NULL CHECK (consent),
            status text NOT NULL DEFAULT 'PENDING_ADMIN_REVIEW'
                CHECK (status IN ('PENDING_ADMIN_REVIEW', 'APPROVED_PENDING_PROVISIONING', 'REJECTED')),
            reviewed_at timestamptz,
            reviewed_by text,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CHECK ((status = 'PENDING_ADMIN_REVIEW') = (reviewed_at IS NULL AND reviewed_by IS NULL)),
            CHECK ((status <> 'PENDING_ADMIN_REVIEW') = (reviewed_at IS NOT NULL AND reviewed_by IS NOT NULL))
        );
        CREATE INDEX ix_access_requests_queue
            ON access_requests (tenant_id, status, created_at, id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX ix_access_requests_queue;
        DROP TABLE access_requests;
        """
    )
