import asyncio

import httpx

from backend.app.api import identity as identity_api
from backend.app.main import app
from backend.app.observability import InMemoryAuditSink


def _request(method: str, path: str, **kwargs: object) -> httpx.Response:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(run())


def _add_identity(email: str) -> None:
    identity_api.identity_store.add_identity(
        user_id=f"user-{email.split('@', 1)[0]}",
        tenant_id="tenant-audit",
        email=email,
        password="correct-password",
        roles=["employee"],
    )


def test_sign_in_emits_correlated_success_event(monkeypatch) -> None:
    _add_identity("audit-happy@example.com")
    sink = InMemoryAuditSink()
    monkeypatch.setattr(identity_api, "audit_sink", sink)

    response = _request(
        "POST",
        "/api/v1/auth/sign-in",
        headers={
            "X-Request-ID": "req-audit-happy",
            "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        },
        json={
            "email": "audit-happy@example.com",
            "password": "correct-password",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-audit-happy"
    assert len(sink.events) == 1
    event = sink.events[0]
    assert event.event == "AUTH_SUCCESS"
    assert event.outcome == "SUCCESS"
    assert event.action == "identity:sign_in"
    assert event.request_id == "req-audit-happy"
    assert event.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert event.principal_id == "user-audit-happy"


def test_sign_in_denial_emits_no_credentials_or_body(monkeypatch) -> None:
    _add_identity("audit-denial@example.com")
    sink = InMemoryAuditSink()
    monkeypatch.setattr(identity_api, "audit_sink", sink)

    response = _request(
        "POST",
        "/api/v1/auth/sign-in",
        headers={"X-Request-ID": "req-audit-denial"},
        json={
            "email": "audit-denial@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_INVALID"
    assert len(sink.events) == 1
    event = sink.events[0]
    payload = event.as_dict()
    assert event.outcome == "DENY"
    assert event.code == "AUTH_INVALID"
    assert "wrong-password" not in repr(payload)
    assert "audit-denial@example.com" not in repr(payload)


def test_sign_in_fails_closed_when_audit_sink_is_unavailable(monkeypatch) -> None:
    _add_identity("audit-unavailable@example.com")
    monkeypatch.setattr(
        identity_api,
        "audit_sink",
        InMemoryAuditSink(available=False),
    )

    response = _request(
        "POST",
        "/api/v1/auth/sign-in",
        headers={"X-Request-ID": "req-audit-unavailable"},
        json={
            "email": "audit-unavailable@example.com",
            "password": "correct-password",
        },
    )

    assert response.status_code == 503
    assert response.json()["code"] == "AUTH_UNAVAILABLE"
