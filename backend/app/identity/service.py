"""Authentication service: validate credentials, then construct a principal."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Callable

from .errors import (
    AUTH_INVALID,
    AUTH_UNAVAILABLE,
    MFA_REQUIRED,
    rate_limited,
)
from .models import AuthenticatedPrincipal, IdentityRecord, SessionRecord, utc_z
from .store import IdentityStore, verify_secret

SESSION_MAX_AGE = timedelta(hours=8)
SESSION_IDLE_TIMEOUT = timedelta(minutes=30)
LOCK_RETRY_AFTER = 900


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class AuthenticationService:
    """Provider-neutral authn boundary with fail-closed store error handling."""

    def __init__(
        self,
        store: IdentityStore,
        *,
        clock: Callable[[], datetime] = now_utc,
    ) -> None:
        self.store = store
        self.clock = clock

    def sign_in(
        self,
        *,
        email: str,
        password: str,
        mfa_code: str | None,
    ) -> tuple[str, SessionRecord, AuthenticatedPrincipal]:
        normalized_email = email.strip().lower()
        now = self.clock()
        try:
            locked_until = self.store.is_locked(normalized_email, now)
            if locked_until is not None:
                raise rate_limited(LOCK_RETRY_AFTER)
            identity = self.store.find_by_email(normalized_email)
            if identity is None or not identity.active:
                self._failed(normalized_email, now)
                raise AUTH_INVALID
            if not verify_secret(password, identity.password_hash):
                self._failed(normalized_email, now)
                raise AUTH_INVALID
            if identity.requires_mfa:
                if not mfa_code or not identity.mfa_code_hash:
                    raise MFA_REQUIRED
                if not verify_secret(mfa_code, identity.mfa_code_hash):
                    self._failed(normalized_email, now)
                    raise AUTH_INVALID
            self.store.clear_failures(normalized_email)
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode("ascii")).hexdigest()
            session = self.store.create_session(
                user_id=identity.user_id,
                tenant_id=identity.tenant_id,
                token_hash=token_hash,
                auth_time=now,
                expires_at=now + SESSION_MAX_AGE,
            )
            return token, session, self._principal(identity, session)
        except (IdentityErrorPassthrough,):
            raise
        except Exception as exc:
            if isinstance(exc, type(AUTH_INVALID)):
                raise
            raise AUTH_UNAVAILABLE from exc

    def resolve_bearer(self, token: str) -> AuthenticatedPrincipal:
        if not token or len(token) > 4096 or any(char.isspace() for char in token):
            raise AUTH_INVALID
        now = self.clock()
        try:
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
            session = self.store.find_session(token_hash)
            if (
                session is None
                or session.revoked_at is not None
                or session.expires_at <= now
                or now - session.last_seen_at > SESSION_IDLE_TIMEOUT
            ):
                raise AUTH_INVALID
            identity = self.store.find_by_user(session.user_id, session.tenant_id)
            if identity is None or not identity.active:
                raise AUTH_INVALID
            self.store.touch_session(session.session_id, now)
            return self._principal(identity, session)
        except Exception as exc:
            if isinstance(exc, type(AUTH_INVALID)):
                raise
            raise AUTH_UNAVAILABLE from exc

    def revoke(self, principal: AuthenticatedPrincipal) -> None:
        try:
            self.store.revoke_session(principal.session_id, self.clock())
        except Exception as exc:
            raise AUTH_UNAVAILABLE from exc

    def _failed(self, email: str, now: datetime) -> None:
        locked_until = self.store.record_failure(email, now)
        if locked_until is not None:
            raise rate_limited(LOCK_RETRY_AFTER)

    @staticmethod
    def _principal(
        identity: IdentityRecord, session: SessionRecord
    ) -> AuthenticatedPrincipal:
        return AuthenticatedPrincipal(
            user_id=identity.user_id,
            tenant_id=identity.tenant_id,
            roles=list(identity.roles),
            groups=list(identity.groups),
            department_ids=list(identity.department_ids),
            session_id=session.session_id,
            auth_time=utc_z(session.auth_time),
        )


class IdentityErrorPassthrough(Exception):
    """Marker kept private so expected dataclass errors are not masked."""
