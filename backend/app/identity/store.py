"""Small in-memory identity store used by the boundary and deterministic tests."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import threading
from dataclasses import replace
from datetime import datetime, timedelta
from typing import Iterable, Protocol

from .models import DepartmentRecord, IdentityRecord, SessionRecord, normalize_roles

PASSWORD_ITERATIONS = 120_000
FAILED_WINDOW = timedelta(minutes=15)
LOCK_DURATION = timedelta(minutes=15)


def hash_secret(secret: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", secret.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_secret(secret: str, encoded: str | None) -> bool:
    if not encoded:
        return False
    try:
        algorithm, iteration_text, salt_text, digest_text = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iteration_text)
        if iterations <= 0:
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256", secret.encode("utf-8"), salt, iterations
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, UnicodeError):
        return False


class IdentityStore(Protocol):
    """Persistence contract for a future PostgreSQL/IdP adapter."""

    def find_by_email(self, email: str) -> IdentityRecord | None: ...

    def find_by_user(self, user_id: str, tenant_id: str) -> IdentityRecord | None: ...

    def is_locked(self, email: str, now: datetime) -> datetime | None: ...

    def record_failure(self, email: str, now: datetime) -> datetime | None: ...

    def clear_failures(self, email: str) -> None: ...

    def create_session(
        self,
        *,
        user_id: str,
        tenant_id: str,
        token_hash: str,
        auth_time: datetime,
        expires_at: datetime,
    ) -> SessionRecord: ...

    def find_session(self, token_hash: str) -> SessionRecord | None: ...

    def touch_session(self, session_id: str, last_seen_at: datetime) -> None: ...

    def revoke_session(self, session_id: str, revoked_at: datetime) -> None: ...

    def find_all(self, tenant_id: str) -> tuple[IdentityRecord, ...]: ...

    def update_identity(
        self,
        *,
        user_id: str,
        tenant_id: str,
        roles: Iterable[str] | None = None,
        department_ids: Iterable[str] | None = None,
        active: bool | None = None,
    ) -> IdentityRecord | None: ...


class InMemoryIdentityStore:
    """Synthetic store for the API shell; production persistence is downstream."""

    def __init__(self) -> None:
        self._identities: dict[str, IdentityRecord] = {}
        self._departments: dict[tuple[str, str], DepartmentRecord] = {}
        self._sessions: dict[str, SessionRecord] = {}
        self._failed: dict[str, list[datetime]] = {}
        self._locked_until: dict[str, datetime] = {}
        self._lock = threading.RLock()

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
        """Add synthetic test data while storing only one-way secret hashes."""

        normalized_email = email.strip().lower()
        record = IdentityRecord(
            user_id=user_id,
            tenant_id=tenant_id,
            email=normalized_email,
            password_hash=hash_secret(password),
            roles=normalize_roles(roles),
            groups=tuple(sorted(set(groups))),
            department_ids=tuple(sorted(set(department_ids))),
            active=active,
            mfa_code_hash=hash_secret(mfa_code) if mfa_code is not None else None,
        )
        with self._lock:
            self._identities[normalized_email] = record
        return record

    def find_by_email(self, email: str) -> IdentityRecord | None:
        with self._lock:
            return self._identities.get(email)

    def find_by_user(self, user_id: str, tenant_id: str) -> IdentityRecord | None:
        with self._lock:
            return next(
                (
                    record
                    for record in self._identities.values()
                    if record.user_id == user_id and record.tenant_id == tenant_id
                ),
                None,
            )

    def find_all(self, tenant_id: str) -> tuple[IdentityRecord, ...]:
        with self._lock:
            return tuple(
                sorted(
                    (record for record in self._identities.values() if record.tenant_id == tenant_id),
                    key=lambda record: record.user_id,
                )
            )

    def update_identity(
        self,
        *,
        user_id: str,
        tenant_id: str,
        roles: Iterable[str] | None = None,
        department_ids: Iterable[str] | None = None,
        active: bool | None = None,
    ) -> IdentityRecord | None:
        with self._lock:
            email, record = next(
                (
                    (email, value)
                    for email, value in self._identities.items()
                    if value.user_id == user_id and value.tenant_id == tenant_id
                ),
                (None, None),
            )
            if record is None or email is None:
                return None
            updated = replace(
                record,
                roles=record.roles if roles is None else normalize_roles(roles),
                department_ids=(
                    record.department_ids
                    if department_ids is None
                    else tuple(sorted(set(department_ids)))
                ),
                active=record.active if active is None else active,
            )
            self._identities[email] = updated
            return updated

    def set_active(self, email: str, active: bool) -> None:
        with self._lock:
            record = self._identities[email]
            self._identities[email] = replace(record, active=active)

    def create_department(self, *, tenant_id: str, name: str, department_id: str) -> DepartmentRecord:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("department name must not be empty")
        department = DepartmentRecord(department_id, tenant_id, normalized_name)
        with self._lock:
            key = (tenant_id, department_id)
            if key in self._departments:
                raise ValueError("department already exists")
            self._departments[key] = department
        return department

    def list_departments(self, tenant_id: str) -> tuple[DepartmentRecord, ...]:
        with self._lock:
            return tuple(
                sorted(
                    (department for department in self._departments.values() if department.tenant_id == tenant_id),
                    key=lambda department: department.department_id,
                )
            )

    def update_department(
        self, *, tenant_id: str, department_id: str, name: str | None = None, active: bool | None = None
    ) -> DepartmentRecord | None:
        with self._lock:
            key = (tenant_id, department_id)
            department = self._departments.get(key)
            if department is None:
                return None
            if name is not None and not name.strip():
                raise ValueError("department name must not be empty")
            updated = replace(
                department,
                name=department.name if name is None else name.strip(),
                active=department.active if active is None else active,
            )
            self._departments[key] = updated
            return updated

    def is_locked(self, email: str, now: datetime) -> datetime | None:
        with self._lock:
            locked_until = self._locked_until.get(email)
            if locked_until is not None and locked_until > now:
                return locked_until
            if locked_until is not None:
                self._locked_until.pop(email, None)
            return None

    def record_failure(self, email: str, now: datetime) -> datetime | None:
        with self._lock:
            attempts = [
                value
                for value in self._failed.get(email, [])
                if now - value < FAILED_WINDOW
            ]
            attempts.append(now)
            self._failed[email] = attempts
            if len(attempts) >= 5:
                locked_until = now + LOCK_DURATION
                self._locked_until[email] = locked_until
                return locked_until
            return None

    def clear_failures(self, email: str) -> None:
        with self._lock:
            self._failed.pop(email, None)
            self._locked_until.pop(email, None)

    def create_session(
        self,
        *,
        user_id: str,
        tenant_id: str,
        token_hash: str,
        auth_time: datetime,
        expires_at: datetime,
    ) -> SessionRecord:
        session = SessionRecord(
            session_id=secrets.token_urlsafe(18),
            user_id=user_id,
            tenant_id=tenant_id,
            token_hash=token_hash,
            auth_time=auth_time,
            last_seen_at=auth_time,
            expires_at=expires_at,
        )
        with self._lock:
            self._sessions[token_hash] = session
        return session

    def find_session(self, token_hash: str) -> SessionRecord | None:
        with self._lock:
            return self._sessions.get(token_hash)

    def touch_session(self, session_id: str, last_seen_at: datetime) -> None:
        with self._lock:
            for session in self._sessions.values():
                if session.session_id == session_id:
                    session.last_seen_at = last_seen_at
                    return

    def revoke_session(self, session_id: str, revoked_at: datetime) -> None:
        with self._lock:
            for session in self._sessions.values():
                if session.session_id == session_id:
                    session.revoked_at = revoked_at
                    return
