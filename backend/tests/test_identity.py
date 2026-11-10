from datetime import datetime, timedelta, timezone

import pytest

from backend.app.identity.errors import IdentityError
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.identity.service import (
    SESSION_MAX_AGE,
    AuthenticationService,
)
from backend.app.identity.store import InMemoryIdentityStore


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_service(*, role: str = "employee", mfa_code: str | None = None):
    store = InMemoryIdentityStore()
    store.add_identity(
        user_id="user-1",
        tenant_id="tenant-1",
        email="User@Example.com",
        password="correct-password",
        roles=[role],
        mfa_code=mfa_code,
    )
    current = [BASE_TIME]
    return store, AuthenticationService(store, clock=lambda: current[0]), current


def test_sign_in_normalizes_email_and_returns_server_principal():
    _, service, _ = make_service()

    token, session, principal = service.sign_in(
        email=" USER@example.com ",
        password="correct-password",
        mfa_code=None,
    )

    assert token
    assert session.user_id == "user-1"
    assert principal.tenant_id == "tenant-1"
    assert principal.roles == ["employee"]


def test_invalid_password_is_safe_auth_error():
    _, service, _ = make_service()

    with pytest.raises(IdentityError) as error:
        service.sign_in(email="user@example.com", password="wrong", mfa_code=None)

    assert error.value.code == "AUTH_INVALID"
    assert "password" not in error.value.message.lower()


def test_unknown_identity_is_indistinguishable_from_invalid_password():
    _, service, _ = make_service()

    with pytest.raises(IdentityError) as error:
        service.sign_in(email="missing@example.com", password="wrong", mfa_code=None)

    assert error.value.code == "AUTH_INVALID"


def test_mfa_is_required_for_privileged_role():
    _, service, _ = make_service(role="chairman", mfa_code="123456")

    with pytest.raises(IdentityError) as error:
        service.sign_in(email="user@example.com", password="correct-password", mfa_code=None)

    assert error.value.code == "MFA_REQUIRED"


def test_wrong_mfa_code_is_rejected():
    _, service, _ = make_service(role="system_admin", mfa_code="123456")

    with pytest.raises(IdentityError) as error:
        service.sign_in(email="user@example.com", password="correct-password", mfa_code="000000")

    assert error.value.code == "AUTH_INVALID"


def test_expired_session_is_rejected():
    _, service, current = make_service()
    token, _, _ = service.sign_in(
        email="user@example.com",
        password="correct-password",
        mfa_code=None,
    )
    current[0] = BASE_TIME + SESSION_MAX_AGE + timedelta(seconds=1)

    with pytest.raises(IdentityError) as error:
        service.resolve_bearer(token)

    assert error.value.code == "AUTH_INVALID"


def test_revoked_session_is_rejected():
    _, service, _ = make_service()
    token, _, principal = service.sign_in(
        email="user@example.com",
        password="correct-password",
        mfa_code=None,
    )
    service.revoke(principal)

    with pytest.raises(IdentityError) as error:
        service.resolve_bearer(token)

    assert error.value.code == "AUTH_INVALID"


def test_store_failure_fails_closed():
    class BrokenStore(InMemoryIdentityStore):
        def find_by_email(self, email: str):
            raise RuntimeError("database unavailable")

    store = BrokenStore()
    service = AuthenticationService(store, clock=lambda: BASE_TIME)

    with pytest.raises(IdentityError) as error:
        service.sign_in(email="user@example.com", password="pw", mfa_code=None)

    assert error.value.code == "AUTH_UNAVAILABLE"
    assert error.value.retryable is True


def test_noncanonical_role_cannot_create_identity():
    store = InMemoryIdentityStore()

    with pytest.raises(ValueError):
        store.add_identity(
            user_id="user-1",
            tenant_id="tenant-1",
            email="user@example.com",
            password="pw",
            roles=["admin"],
        )


def test_principal_rejects_extra_client_claims():
    with pytest.raises(ValueError):
        AuthenticatedPrincipal(
            user_id="user-1",
            tenant_id="tenant-1",
            roles=["employee"],
            session_id="session-1",
            auth_time="2026-01-01T00:00:00Z",
            is_admin=True,
        )
