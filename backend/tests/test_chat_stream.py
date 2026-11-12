from __future__ import annotations

import asyncio
import json
import time
from threading import Event
from types import SimpleNamespace

import httpx
import pytest

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.app.api import identity as identity_api
from backend.app.core.config import get_settings
from backend.app.db.runtime import PostgresChatRepository
from backend.app.integrations.gemini import GeminiProviderError, GeminiStreamProvider
from backend.app.authorization import AnonymousPrincipal
from backend.app.main import app
from backend.app.observability import InMemoryAuditSink
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.rag.runtime import (
    LOCAL_DEMO_CHUNK_DELAY_SECONDS,
    LocalRagExecutor,
    PUBLIC_POLICY_TEXT,
)


def request(method: str, path: str, **kwargs: object) -> httpx.Response:
    async def run() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(run())


class _FakeGemini:
    def __init__(self, *chunks: str, error: bool = False) -> None:
        self.chunks = chunks
        self.error = error

    def stream(self, messages):
        assert messages
        if self.error:
            raise GeminiProviderError("provider unavailable")
        yield from self.chunks


@pytest.fixture(autouse=True)
def clean_state(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("BACKEND_GEMINI_API_KEY", raising=False)
    get_settings.cache_clear()
    admin_api.reset_state()
    identity_api.audit_sink = InMemoryAuditSink()
    chat_api.reset_state()
    chat_api.chat_service.executor = LocalRagExecutor()


def anonymous_conversation() -> tuple[str, str]:
    response = request("POST", "/api/v1/conversations")
    assert response.status_code == 201, response.text
    return response.json()["conversation_id"], response.cookies.get(chat_api.ANONYMOUS_SESSION_COOKIE)


def parse_sse(body: str) -> list[tuple[str, dict[str, object]]]:
    events = []
    for block in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        events.append((lines["event"], json.loads(lines["data"])))
    return events


def test_stream_requires_the_same_anonymous_authorization_boundary():
    conversation_id, _ = anonymous_conversation()
    response = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages/stream",
        headers={"Idempotency-Key": "stream-auth-test-001"},
        json={"query": "purchasing policy"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_new_conversation_recovers_from_a_stale_anonymous_session():
    _, stale_token = anonymous_conversation()
    chat_api.reset_state()

    response = request(
        "POST",
        "/api/v1/conversations",
        headers={"X-Anonymous-Session": stale_token},
    )

    assert response.status_code == 201
    assert response.cookies.get(chat_api.ANONYMOUS_SESSION_COOKIE) != stale_token


def test_no_key_stream_runs_local_rag_and_persists_answer():
    conversation_id, token = anonymous_conversation()
    response = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages/stream",
        headers={
            "X-Anonymous-Session": token,
            "Idempotency-Key": "stream-local-test-001",
        },
        json={"query": "What is the purchasing policy for equipment?"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    events = parse_sse(response.text)
    names = [name for name, _ in events]
    assert names[0] == "message_start"
    assert "citation" in names
    assert "token" in names
    assert names[-1] == "done"
    done = events[-1][1]
    assert done["state"] == "COMPLETED"
    assert done["answer"]["status"] == "ANSWERED"
    assert PUBLIC_POLICY_TEXT in done["answer"]["text"]
    assert PUBLIC_POLICY_TEXT not in response.text.split("event: done", 1)[0]

    history = request(
        "GET",
        f"/api/v1/conversations/{conversation_id}",
        headers={"X-Anonymous-Session": token},
    )
    assert history.status_code == 200
    assert history.json()["messages"][-1]["content"] == PUBLIC_POLICY_TEXT


def test_configured_provider_error_never_falls_back_to_local_answer():
    chat_api.chat_service.executor = LocalRagExecutor(
        gemini_provider=_FakeGemini(error=True)  # type: ignore[arg-type]
    )
    conversation_id, token = anonymous_conversation()
    response = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages/stream",
        headers={
            "X-Anonymous-Session": token,
            "Idempotency-Key": "stream-provider-error-001",
        },
        json={"query": "What is the purchasing policy for equipment?"},
    )

    assert response.status_code == 200
    assert "event: error" in response.text
    assert "PROVIDER_ERROR" in response.text
    assert PUBLIC_POLICY_TEXT not in response.text

    message_start = next(data for name, data in parse_sse(response.text) if name == "message_start")
    status = request(
        "GET",
        f"/api/v1/query-jobs/{message_start['job_id']}",
        headers={"X-Anonymous-Session": token},
    )
    assert status.json()["state"] == "FAILED"
    assert status.json()["error"]["code"] == "PROVIDER_ERROR"


def test_local_runtime_answers_from_checked_in_public_sample_document():
    executor = LocalRagExecutor()
    executor.bind_context("sample-anon", AnonymousPrincipal("public", "sample-anon"), 1)

    events = list(
        executor.stream(
            SimpleNamespace(
                principal_ref="sample-anon",
                query="What approval is needed for equipment purchases above 5,000 USD?",
            )
        )
    )

    citation = next(item["data"] for item in events if item["event"] == "citation")
    complete = next(item["data"] for item in events if item["event"] == "complete")
    assert citation["document_id"] == "11111111-1111-4111-8111-111111111111"
    assert complete["status"] == "ANSWERED"
    assert "5,000 USD" in complete["answer"]


def test_local_runtime_applies_department_acl_to_internal_sample_document():
    executor = LocalRagExecutor()
    principal = AuthenticatedPrincipal(
        user_id="sample-employee",
        tenant_id="public",
        roles=["employee"],
        department_ids=["bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"],
        session_id="sample-session",
        auth_time="2026-11-10T00:00:00Z",
    )
    executor.bind_context("sample-employee", principal, 1)

    events = list(
        executor.stream(
            SimpleNamespace(
                principal_ref="sample-employee",
                query="How long are security audit logs retained?",
            )
        )
    )

    citation = next(item["data"] for item in events if item["event"] == "citation")
    complete = next(item["data"] for item in events if item["event"] == "complete")
    assert citation["document_id"] == "22222222-2222-4222-8222-222222222221"
    assert complete["status"] == "ANSWERED"
    assert "30 calendar days" in complete["answer"]


def test_local_sample_citation_preview_returns_safe_metadata_after_fresh_authz():
    conversation_id, token = anonymous_conversation()
    response = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages/stream",
        headers={
            "X-Anonymous-Session": token,
            "Idempotency-Key": "stream-preview-sample-001",
        },
        json={"query": "What approval is needed for equipment purchases above 5,000 USD?"},
    )
    done = next(data for name, data in parse_sse(response.text) if name == "done")
    answer_id = done["answer"]["answer_id"]
    citation_id = done["answer"]["citations"][0]["citation_id"]

    preview = request(
        "GET",
        f"/api/v1/answers/{answer_id}/citations/{citation_id}/preview",
        headers={"X-Anonymous-Session": token},
    )

    assert preview.status_code == 200, preview.text
    payload = preview.json()
    assert "Equipment Purchasing Policy" in payload["title"]
    assert payload["filename"] == "equipment-purchasing-policy.pdf"
    assert payload["location"]["kind"] == "PDF"
    assert "5,000 USD" in payload["preview"]
    assert payload["citation"]["filename"] == payload["filename"]


def test_durable_citation_load_preserves_metadata_for_local_source_state(monkeypatch):
    citation = {
        "citation_id": "c-1",
        "tenant_id": "public",
        "document_id": "11111111-1111-4111-8111-111111111111",
        "version_id": "11111111-1111-4111-8111-111111111112",
        "title": "Equipment Purchasing Policy",
        "filename": "equipment-purchasing-policy.pdf",
        "location": {"kind": "PDF", "page": 1},
    }
    repository = PostgresChatRepository("postgresql://user:password@localhost/runtime")
    monkeypatch.setattr(
        repository,
        "answer_job",
        lambda answer_id, *, current_scope: SimpleNamespace(
            completion=SimpleNamespace(citations=(citation,))
        ),
    )

    artifact = repository.get_citation(
        "11111111-1111-4111-8111-111111111114",
        "c-1",
        current_scope=SimpleNamespace(tenant_id="public"),
    )
    state = LocalRagExecutor().citation_state(artifact)

    assert artifact is not None
    assert state is not None
    assert state.title == "Equipment Purchasing Policy"
    assert state.filename == "equipment-purchasing-policy.pdf"
    assert state.location["kind"] == "PDF"


def test_provider_incomplete_detailed_answer_abstains_before_token_delivery():
    provider = _FakeGemini("The department reviewed the equipment purchase.")
    executor = LocalRagExecutor(gemini_provider=provider)  # type: ignore[arg-type]
    executor.bind_context("provider-incomplete", AnonymousPrincipal("public", "provider-incomplete"), 1)

    events = list(
        executor.stream(
            SimpleNamespace(
                principal_ref="provider-incomplete",
                query="What approval is needed for equipment purchases above 5,000 USD?",
            )
        )
    )

    names = [item["event"] for item in events]
    complete = next(item["data"] for item in events if item["event"] == "complete")
    assert "token" not in names
    assert complete["status"] == "INSUFFICIENT_EVIDENCE"
    assert complete["reason_codes"] == ["incomplete_evidence_coverage"]


def test_local_fallback_streams_incrementally_and_cancels_before_completion():
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={
            "X-Anonymous-Session": token,
            "Idempotency-Key": "stream-disconnect-001",
        },
        json={"query": "What approval is needed for equipment purchases above 5,000 USD?"},
    )
    job_id = submitted.json()["job_id"]
    actor = chat_api.chat_service.actor_for_existing(None, token)
    cancelled = Event()
    stream = chat_api.chat_service.stream(actor, job_id, should_cancel=cancelled.is_set)

    assert next(stream)[0] == "message_start"
    token_events: list[tuple[str, dict[str, object]]] = []
    token_started = time.monotonic()
    while len(token_events) < 2:
        event = next(stream)
        if event[0] == "token":
            token_events.append(event)
    token_elapsed = time.monotonic() - token_started
    assert len(token_events) == 2
    assert token_elapsed >= LOCAL_DEMO_CHUNK_DELAY_SECONDS * 0.80
    cancelled.set()
    assert list(stream) == []

    status = request(
        "GET",
        f"/api/v1/query-jobs/{job_id}",
        headers={"X-Anonymous-Session": token},
    )
    history = request(
        "GET",
        f"/api/v1/conversations/{conversation_id}",
        headers={"X-Anonymous-Session": token},
    )
    assert status.json()["state"] == "CANCELLED"
    assert len(history.json()["messages"]) == 1


def test_gemini_adapter_uses_server_header_and_parses_sse_without_echoing_key():
    captured: dict[str, object] = {}

    class Response:
        def __iter__(self):
            return iter(
                [
                    b'data: {"candidates":[{"content":{"parts":[{"text":"Hello"}]}}]}\n',
                    b'data: {"candidates":[{"content":{"parts":[{"text":" world"}]}}]}\n',
                ]
            )

        def close(self):
            captured["closed"] = True

    def opener(request, *, timeout):
        captured["url"] = request.full_url
        captured["key"] = request.get_header("X-goog-api-key")
        captured["timeout"] = timeout
        return Response()

    key = "unit-test-key-not-returned"
    output = list(
        GeminiStreamProvider(key, "gemini-test", opener=opener).stream(
            ({"role": "user", "content": "safe context"},)
        )
    )
    assert output == ["Hello", " world"]
    assert captured["key"] == key
    assert "alt=sse" in captured["url"]
    assert captured["closed"] is True
