import asyncio

import httpx

from backend.app.main import app


def test_application_shell_has_expected_metadata() -> None:
    assert app.title == "Enterprise Agentic RAG Backend"
    assert app.version == "0.1.0"


def test_healthz_is_local_liveness_only() -> None:
    async def request_healthz() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/healthz")

    response = asyncio.run(request_healthz())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_vercel_origin_can_use_cookie_authenticated_api() -> None:
    async def request_preflight() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.options(
                "/api/v1/conversations",
                headers={
                    "Origin": "https://agentic-rag-enterprise.vercel.app",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type,idempotency-key",
                },
            )

    response = asyncio.run(request_preflight())

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://agentic-rag-enterprise.vercel.app"
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "POST" in response.headers["access-control-allow-methods"]


def test_identity_requires_bearer_credentials() -> None:
    async def request_me() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/api/v1/auth/me", headers={"X-Request-ID": "req-1"})

    response = asyncio.run(request_me())

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.headers["X-Request-ID"] == "req-1"
    assert len(response.headers["traceparent"].split("-")) == 4
    assert response.json() == {
        "code": "AUTH_REQUIRED",
        "message": "Authentication required.",
        "request_id": "req-1",
        "retryable": False,
    }
