"""PostgreSQL-backed identity store for configured deployments."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable
from uuid import UUID, uuid4

from ..db.runtime import (
    _PostgresAdapter,
    _as_utc,
    _department_uuid,
    _membership_uuid,
    tenant_uuid,
    user_uuid,
)
from .models import DepartmentRecord, IdentityRecord, SessionRecord, normalize_roles
from .store import FAILED_WINDOW, LOCK_DURATION, IdentityStore, hash_secret


class PostgresIdentityStore(_PostgresAdapter, IdentityStore):
    """Durable implementation of the existing provider-neutral identity contract."""

    def _identity(self, cursor: object, row: dict[str, object]) -> IdentityRecord:
        cursor.execute(
            """
            SELECT r.code
            FROM membership_roles mr
            JOIN roles r ON r.id = mr.role_id
            WHERE mr.membership_id = %s
            ORDER BY r.code
            """,
            (row["membership_id"],),
        )
        roles = tuple(result["code"] for result in cursor.fetchall())
        department_id = row.get("department_id")
        return IdentityRecord(
            user_id=str(row["user_id"]),
            tenant_id=str(row["tenant_id"]),
            email=str(row["email"]),
            password_hash=str(row.get("password_hash") or ""),
            roles=normalize_roles(roles),
            department_ids=(str(department_id),) if department_id else (),
            active=row["user_status"] == "ACTIVE" and row["membership_status"] == "ACTIVE",
            mfa_code_hash=str(row["mfa_code_hash"]) if row.get("mfa_code_hash") else None,
        )

    @staticmethod
    def _identity_query() -> str:
        return """
            SELECT u.id AS user_id, u.email, u.password_hash, u.mfa_code_hash,
                   u.status AS user_status, tm.id AS membership_id,
                   tm.tenant_id, tm.department_id, tm.status AS membership_status
            FROM users u
            JOIN tenant_memberships tm ON tm.user_id = u.id
            WHERE {where}
            ORDER BY tm.tenant_id
            LIMIT 1
        """

    def find_by_email(self, email: str) -> IdentityRecord | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(self._identity_query().format(where="u.email = %s"), (email,))
                row = cursor.fetchone()
                return self._identity(cursor, row) if row else None

    def find_by_user(self, user_id: str, tenant_id: str) -> IdentityRecord | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self._identity_query().format(where="u.id = %s AND tm.tenant_id = %s"),
                    (user_uuid(user_id), tenant_uuid(tenant_id)),
                )
                row = cursor.fetchone()
                return self._identity(cursor, row) if row else None

    def find_all(self, tenant_id: str) -> tuple[IdentityRecord, ...]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self._identity_query().replace("LIMIT 1", "")
                    .format(where="tm.tenant_id = %s")
                    .replace("ORDER BY tm.tenant_id", "ORDER BY u.email"),
                    (tenant_uuid(tenant_id),),
                )
                return tuple(self._identity(cursor, row) for row in cursor.fetchall())

    def add_identity(
        self,
        *,
        user_id: str,
        tenant_id: str,
        email: str,
        password: str,
        roles: Iterable[str],
        groups: Iterable[str] = (),
        department_ids: Iterable[str] = (),
        mfa_code: str | None = None,
        active: bool = True,
    ) -> IdentityRecord:
        del groups  # Groups are not part of the approved relational identity schema yet.
        normalized_email = email.strip().lower()
        role_codes = normalize_roles(roles)
        tenant_value = tenant_uuid(tenant_id)
        persisted_user = user_uuid(user_id)
        membership = _membership_uuid(tenant_id, user_id)
        department_values = tuple(department_ids)
        department_value = _department_uuid(tenant_id, department_values[0]) if department_values else None
        with self.connection() as connection:
            with connection.cursor() as cursor:
                self.ensure_tenant(cursor, tenant_id)
                if department_value is not None:
                    cursor.execute(
                        """
                        INSERT INTO departments (id, tenant_id, code, name)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (department_value, tenant_value, f"dept-{department_value.hex[:20]}", department_values[0][:160]),
                    )
                cursor.execute(
                    """
                    INSERT INTO users (id, email, display_name, status, password_hash, mfa_code_hash)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        email = EXCLUDED.email,
                        display_name = EXCLUDED.display_name,
                        status = EXCLUDED.status,
                        password_hash = EXCLUDED.password_hash,
                        mfa_code_hash = EXCLUDED.mfa_code_hash,
                        updated_at = now()
                    """,
                    (
                        persisted_user,
                        normalized_email,
                        normalized_email.split("@", 1)[0][:160],
                        "ACTIVE" if active else "SUSPENDED",
                        hash_secret(password),
                        hash_secret(mfa_code) if mfa_code is not None else None,
                    ),
                )
                cursor.execute(
                    """
                    INSERT INTO tenant_memberships (id, tenant_id, user_id, department_id, status, revoked_at)
                    VALUES (%s, %s, %s, %s, %s, NULL)
                    ON CONFLICT (tenant_id, user_id) DO UPDATE SET
                        department_id = EXCLUDED.department_id,
                        status = EXCLUDED.status,
                        revoked_at = NULL
                    """,
                    (membership, tenant_value, persisted_user, department_value, "ACTIVE" if active else "SUSPENDED"),
                )
                cursor.execute("DELETE FROM membership_roles WHERE membership_id = %s", (membership,))
                for role in role_codes:
                    cursor.execute(
                        """
                        INSERT INTO membership_roles (membership_id, role_id)
                        SELECT %s, id FROM roles WHERE code = %s
                        """,
                        (membership, role),
                    )
                record = self._find_by_user_cursor(cursor, persisted_user, tenant_value)
                if record is None:
                    raise RuntimeError("identity was not persisted")
                return record

    def _find_by_user_cursor(self, cursor: object, user_id: UUID, tenant_id: UUID) -> IdentityRecord | None:
        cursor.execute(
            self._identity_query().format(where="u.id = %s AND tm.tenant_id = %s"),
            (user_id, tenant_id),
        )
        row = cursor.fetchone()
        return self._identity(cursor, row) if row else None

    def update_identity(
        self,
        *,
        user_id: str,
        tenant_id: str,
        roles: Iterable[str] | None = None,
        department_ids: Iterable[str] | None = None,
        active: bool | None = None,
    ) -> IdentityRecord | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                persisted_user = user_uuid(user_id)
                persisted_tenant = tenant_uuid(tenant_id)
                membership = _membership_uuid(tenant_id, user_id)
                cursor.execute(
                    "SELECT 1 FROM tenant_memberships WHERE id = %s AND tenant_id = %s AND user_id = %s",
                    (membership, persisted_tenant, persisted_user),
                )
                if cursor.fetchone() is None:
                    return None
                if department_ids is not None:
                    values = tuple(department_ids)
                    department_value = _department_uuid(tenant_id, values[0]) if values else None
                    if department_value is not None:
                        cursor.execute(
                            """
                            INSERT INTO departments (id, tenant_id, code, name)
                            VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING
                            """,
                            (department_value, persisted_tenant, f"dept-{department_value.hex[:20]}", values[0][:160]),
                        )
                    cursor.execute(
                        "UPDATE tenant_memberships SET department_id = %s WHERE id = %s AND tenant_id = %s",
                        (department_value, membership, persisted_tenant),
                    )
                if active is not None:
                    cursor.execute(
                        "UPDATE tenant_memberships SET status = %s, revoked_at = CASE WHEN %s THEN NULL ELSE now() END WHERE id = %s AND tenant_id = %s",
                        ("ACTIVE" if active else "SUSPENDED", active, membership, persisted_tenant),
                    )
                if roles is not None:
                    cursor.execute("DELETE FROM membership_roles WHERE membership_id = %s", (membership,))
                    for role in normalize_roles(roles):
                        cursor.execute(
                            "INSERT INTO membership_roles (membership_id, role_id) SELECT %s, id FROM roles WHERE code = %s",
                            (membership, role),
                        )
                return self._find_by_user_cursor(cursor, persisted_user, persisted_tenant)

    def is_locked(self, email: str, now: datetime) -> datetime | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT locked_until FROM auth_failures WHERE email = %s", (email,))
                row = cursor.fetchone()
                locked_until = row["locked_until"] if row else None
                return _as_utc(locked_until) if locked_until and _as_utc(locked_until) > _as_utc(now) else None

    def record_failure(self, email: str, now: datetime) -> datetime | None:
        now = _as_utc(now)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT attempts, window_started_at FROM auth_failures WHERE email = %s FOR UPDATE", (email,))
                row = cursor.fetchone()
                if not row or now - _as_utc(row["window_started_at"]) >= FAILED_WINDOW:
                    attempts = 1
                    window_started = now
                else:
                    attempts = int(row["attempts"]) + 1
                    window_started = row["window_started_at"]
                locked_until = now + LOCK_DURATION if attempts >= 5 else None
                cursor.execute(
                    """
                    INSERT INTO auth_failures (email, attempts, window_started_at, locked_until)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET attempts = EXCLUDED.attempts,
                        window_started_at = EXCLUDED.window_started_at,
                        locked_until = EXCLUDED.locked_until
                    """,
                    (email, attempts, window_started, locked_until),
                )
                return locked_until

    def clear_failures(self, email: str) -> None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM auth_failures WHERE email = %s", (email,))

    def create_session(
        self, *, user_id: str, tenant_id: str, token_hash: str, auth_time: datetime, expires_at: datetime
    ) -> SessionRecord:
        session_id = uuid4()
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO auth_sessions (id, tenant_id, user_id, token_hash, auth_time, last_seen_at, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (session_id, tenant_uuid(tenant_id), user_uuid(user_id), token_hash, auth_time, auth_time, expires_at),
                )
        return SessionRecord(str(session_id), user_id, tenant_id, token_hash, auth_time, auth_time, expires_at)

    def find_session(self, token_hash: str) -> SessionRecord | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, tenant_id, token_hash, auth_time, last_seen_at, expires_at, revoked_at
                    FROM auth_sessions WHERE token_hash = %s
                    """,
                    (token_hash,),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return SessionRecord(
                    str(row["id"]), str(row["user_id"]), str(row["tenant_id"]), row["token_hash"],
                    _as_utc(row["auth_time"]), _as_utc(row["last_seen_at"]), _as_utc(row["expires_at"]),
                    _as_utc(row["revoked_at"]) if row["revoked_at"] else None,
                )

    def touch_session(self, session_id: str, last_seen_at: datetime) -> None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE auth_sessions SET last_seen_at = %s WHERE id = %s", (_as_utc(last_seen_at), UUID(session_id)))

    def revoke_session(self, session_id: str, revoked_at: datetime) -> None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE auth_sessions SET revoked_at = %s WHERE id = %s", (_as_utc(revoked_at), UUID(session_id)))

    def set_active(self, email: str, active: bool) -> None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET status = %s, updated_at = now() WHERE email = %s", ("ACTIVE" if active else "SUSPENDED", email))

    def create_department(self, *, tenant_id: str, name: str, department_id: str) -> DepartmentRecord:
        value = _department_uuid(tenant_id, department_id)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                tenant_value = self.ensure_tenant(cursor, tenant_id)
                cursor.execute(
                    "INSERT INTO departments (id, tenant_id, code, name) VALUES (%s, %s, %s, %s)",
                    (value, tenant_value, f"dept-{value.hex[:20]}", name.strip()),
                )
        return DepartmentRecord(str(value), tenant_id, name.strip())

    def list_departments(self, tenant_id: str) -> tuple[DepartmentRecord, ...]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, status FROM departments WHERE tenant_id = %s ORDER BY name", (tenant_uuid(tenant_id),))
                return tuple(DepartmentRecord(str(row["id"]), tenant_id, row["name"], row["status"] == "ACTIVE") for row in cursor.fetchall())

    def update_department(self, *, tenant_id: str, department_id: str, name: str | None = None, active: bool | None = None) -> DepartmentRecord | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                if name is not None:
                    cursor.execute("UPDATE departments SET name = %s WHERE id = %s AND tenant_id = %s", (name.strip(), _department_uuid(tenant_id, department_id), tenant_uuid(tenant_id)))
                if active is not None:
                    cursor.execute("UPDATE departments SET status = %s WHERE id = %s AND tenant_id = %s", ("ACTIVE" if active else "INACTIVE", _department_uuid(tenant_id, department_id), tenant_uuid(tenant_id)))
                cursor.execute("SELECT id, name, status FROM departments WHERE id = %s AND tenant_id = %s", (_department_uuid(tenant_id, department_id), tenant_uuid(tenant_id)))
                row = cursor.fetchone()
                return DepartmentRecord(str(row["id"]), tenant_id, row["name"], row["status"] == "ACTIVE") if row else None


__all__ = ["PostgresIdentityStore"]
