"""Add durable local credential and rate-limit state to identity tables."""

from alembic import op

revision = "0007_identity_credentials"
down_revision = "0006_access_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE users ADD COLUMN password_hash text;
        ALTER TABLE users ADD COLUMN mfa_code_hash text;
        CREATE TABLE auth_failures (
            email text PRIMARY KEY,
            attempts integer NOT NULL CHECK (attempts >= 0),
            window_started_at timestamptz NOT NULL,
            locked_until timestamptz
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE auth_failures;
        ALTER TABLE users DROP COLUMN mfa_code_hash;
        ALTER TABLE users DROP COLUMN password_hash;
        """
    )
