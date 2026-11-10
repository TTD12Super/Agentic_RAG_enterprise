"""Create authoritative identity and tenant tables."""

from alembic import op

revision = "0001_identity_tenants"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE tenants (
            id uuid PRIMARY KEY,
            slug text NOT NULL UNIQUE CHECK (slug = lower(btrim(slug)) AND slug <> ''),
            name text NOT NULL CHECK (btrim(name) <> ''),
            status text NOT NULL DEFAULT 'ACTIVE'
                CHECK (status IN ('ACTIVE', 'SUSPENDED', 'DELETED')),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE TABLE users (
            id uuid PRIMARY KEY,
            email text NOT NULL CHECK (email = lower(btrim(email)) AND email <> ''),
            display_name text NOT NULL CHECK (btrim(display_name) <> ''),
            status text NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING', 'ACTIVE', 'SUSPENDED', 'DELETED')),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (email)
        );
        CREATE TABLE departments (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            code text NOT NULL CHECK (code = lower(btrim(code)) AND code <> ''),
            name text NOT NULL CHECK (btrim(name) <> ''),
            status text NOT NULL DEFAULT 'ACTIVE'
                CHECK (status IN ('ACTIVE', 'INACTIVE')),
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, code)
        );
        CREATE TABLE tenant_memberships (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            user_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            department_id uuid,
            status text NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING', 'ACTIVE', 'SUSPENDED', 'REVOKED')),
            joined_at timestamptz NOT NULL DEFAULT now(),
            revoked_at timestamptz,
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, user_id),
            FOREIGN KEY (tenant_id, department_id)
                REFERENCES departments(tenant_id, id) ON DELETE RESTRICT,
            CHECK ((status = 'REVOKED') = (revoked_at IS NOT NULL))
        );
        CREATE TABLE roles (
            id uuid PRIMARY KEY,
            code text NOT NULL UNIQUE
                CHECK (code IN ('system_admin', 'website_manager', 'employee', 'chairman')),
            name text NOT NULL
        );
        CREATE TABLE membership_roles (
            membership_id uuid NOT NULL REFERENCES tenant_memberships(id) ON DELETE RESTRICT,
            role_id uuid NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
            PRIMARY KEY (membership_id, role_id)
        );
        CREATE TABLE auth_sessions (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            user_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            token_hash text NOT NULL UNIQUE,
            auth_time timestamptz NOT NULL DEFAULT now(),
            last_seen_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz NOT NULL,
            revoked_at timestamptz,
            FOREIGN KEY (tenant_id, user_id)
                REFERENCES tenant_memberships(tenant_id, user_id) ON DELETE RESTRICT,
            CHECK (expires_at > auth_time),
            CHECK (revoked_at IS NULL OR revoked_at >= auth_time)
        );
        CREATE TABLE anonymous_sessions (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
            session_hash text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            last_seen_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz NOT NULL,
            revoked_at timestamptz,
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, session_hash),
            CHECK (expires_at > created_at),
            CHECK (revoked_at IS NULL OR revoked_at >= created_at)
        );
        INSERT INTO roles (id, code, name) VALUES
            ('00000000-0000-0000-0000-000000000001', 'system_admin', 'System Admin'),
            ('00000000-0000-0000-0000-000000000002', 'website_manager', 'Website Manager'),
            ('00000000-0000-0000-0000-000000000003', 'employee', 'Employee'),
            ('00000000-0000-0000-0000-000000000004', 'chairman', 'Chairman');
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE auth_sessions;
        DROP TABLE anonymous_sessions;
        DROP TABLE membership_roles;
        DROP TABLE tenant_memberships;
        DROP TABLE departments;
        DROP TABLE roles;
        DROP TABLE users;
        DROP TABLE tenants;
        """
    )
