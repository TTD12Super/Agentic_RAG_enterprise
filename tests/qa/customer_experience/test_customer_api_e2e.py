from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.app.api import identity as identity_api
from backend.app.authorization import AnonymousPrincipal
from backend.app.core.config import get_settings
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.main import app
from backend.app.observability import InMemoryAuditSink
from backend.app.rag.runtime import LocalRagExecutor


def request(method: str, path: str, **kwargs: object) -> httpx.Response:
    """Exercise the real HTTP boundary in-process, without a live provider."""

    async def run() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://customer-qa"
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(run())


@pytest.fixture(autouse=True)
def isolated_local_runtime(monkeypatch: pytest.MonkeyPatch):
    """Reset process-local stores so each customer journey starts from zero."""

    monkeypatch.delenv("BACKEND_GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    get_settings.cache_clear()
    admin_api.reset_state()
    identity_api.audit_sink = InMemoryAuditSink()
    chat_api.reset_state()
    chat_api.chat_service.executor = LocalRagExecutor()


def anonymous_conversation() -> tuple[str, str]:
    response = request("POST", "/api/v1/conversations")
    assert response.status_code == 201, response.text
    token = response.cookies.get(chat_api.ANONYMOUS_SESSION_COOKIE)
    assert token
    return response.json()["conversation_id"], token


def parse_sse(body: str) -> list[tuple[str, dict[str, object]]]:
    events: list[tuple[str, dict[str, object]]] = []
    for block in body.strip().split("\n\n"):
        lines = block.splitlines()
        if not lines:
            continue
        event = next(line.split(":", 1)[1].strip() for line in lines if line.startswith("event:"))
        raw_data = "\n".join(line.split(":", 1)[1].lstrip() for line in lines if line.startswith("data:"))
        events.append((event, json.loads(raw_data)))
    return events


def stream_public_question() -> tuple[str, str, list[tuple[str, dict[str, object]]]]:
    conversation_id, token = anonymous_conversation()
    response = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages/stream",
        headers={
            "X-Anonymous-Session": token,
            "Idempotency-Key": "customer-qa-stream-001",
        },
        json={"query": "What approval is needed for equipment purchases above 5,000 USD?"},
    )
    assert response.status_code == 200, response.text
    return conversation_id, token, parse_sse(response.text)


def test_citation_preview_returns_a_non_empty_authorized_excerpt():
    """Repro: ask a public question, open citations, click Preview."""

    _, token, events = stream_public_question()
    done = next(data for name, data in events if name == "done")
    answer = done["answer"]
    citation = answer["citations"][0]

    preview = request(
        "GET",
        f"/api/v1/answers/{answer['answer_id']}/citations/{citation['citation_id']}/preview",
        headers={"X-Anonymous-Session": token},
    )

    assert preview.status_code == 200, preview.text
    assert isinstance(preview.json().get("preview"), str)
    assert preview.json()["preview"].strip(), "Preview button must return source text"


def test_reloading_conversation_preserves_answer_citations():
    """Repro: reload a completed chat, then keep citation actions available."""

    conversation_id, token, events = stream_public_question()
    done = next(data for name, data in events if name == "done")
    answer = done["answer"]

    restored = request(
        "GET",
        f"/api/v1/conversations/{conversation_id}",
        headers={"X-Anonymous-Session": token},
    )

    assert restored.status_code == 200, restored.text
    assistant = next(message for message in restored.json()["messages"] if message["role"] == "assistant")
    assert assistant["answer_id"] == answer["answer_id"]
    assert assistant["citations"] == answer["citations"]


def test_stream_events_are_ordered_and_have_one_terminal_done():
    """Repro: send a question and observe every SSE event in arrival order."""

    _, _, events = stream_public_question()
    names = [name for name, _ in events]

    assert names[0] == "message_start"
    assert names.count("message_start") == 1
    assert names.count("done") == 1
    assert names[-1] == "done"
    assert "citation" in names
    assert "token" in names
    assert max(index for index, name in enumerate(names) if name == "citation") < min(
        index for index, name in enumerate(names) if name == "token"
    )


def test_long_equipment_answer_contains_every_policy_condition():
    """Repro: request a detailed checklist, not only the first matching claim."""

    executor = LocalRagExecutor()
    executor.bind_context("anonymous:long-answer", AnonymousPrincipal("public", "long-answer"), 1)
    events = list(
        executor.stream(
            SimpleNamespace(
                principal_ref="anonymous:long-answer",
                query=(
                    "Give me a complete checklist for equipment purchases above 5,000 USD, "
                    "including every approval condition."
                ),
            )
        )
    )
    complete = next(item["data"] for item in events if item["event"] == "complete")
    answer = complete["answer"]

    assert complete["status"] == "ANSWERED"
    assert "department" in answer.casefold()
    assert "5,000 usd" in answer.casefold()
    assert "finance" in answer.casefold()


def test_public_and_internal_acl_are_enforced_by_local_rag():
    """Repro: anonymous asks for internal data; owning department asks the same question."""

    executor = LocalRagExecutor()
    executor.bind_context("anonymous:acl", AnonymousPrincipal("public", "acl-anon"), 1)
    anonymous_events = list(
        executor.stream(
            SimpleNamespace(
                principal_ref="anonymous:acl",
                query="How long are security audit logs retained?",
            )
        )
    )
    anonymous_complete = next(item["data"] for item in anonymous_events if item["event"] == "complete")
    assert anonymous_complete["status"] == "INSUFFICIENT_EVIDENCE"
    assert anonymous_complete["citations"] == []

    principal = AuthenticatedPrincipal(
        user_id="acl-employee",
        tenant_id="public",
        roles=["employee"],
        department_ids=["bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"],
        session_id="acl-session",
        auth_time="2026-11-12T00:00:00Z",
    )
    executor.bind_context("employee:acl", principal, 1)
    employee_events = list(
        executor.stream(
            SimpleNamespace(
                principal_ref="employee:acl",
                query="How long are security audit logs retained?",
            )
        )
    )
    employee_complete = next(item["data"] for item in employee_events if item["event"] == "complete")
    assert employee_complete["status"] == "ANSWERED"
    assert "30 calendar days" in employee_complete["answer"]
    assert employee_complete["citations"]


def test_backend_outage_exposes_retryable_problem_contract():
    """Repro: begin a request while tenant maintenance/outage blocks admission."""

    conversation_id, token = anonymous_conversation()
    window = admin_api.ingestion_service.start_maintenance(
        admin_api._tenant_uuid("public"), reason="customer-qa-outage"
    )
    try:
        response = request(
            "POST",
            f"/api/v1/conversations/{conversation_id}/messages",
            headers={
                "X-Anonymous-Session": token,
                "Idempotency-Key": "customer-qa-outage-001",
            },
            json={"query": "retry after outage"},
        )
    finally:
        admin_api.ingestion_service.finish_maintenance(window.window_id, window.tenant_id)
    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["retryable"] is True
    assert response.json()["code"] == "MAINTENANCE_ACTIVE"


def test_access_request_is_recorded_without_granting_access():
    """Repro: submit onboarding form and show a truthful pending status."""

    response = request(
        "POST",
        "/api/v1/access-requests",
        headers={"Idempotency-Key": "customer-qa-access-001"},
        json={
            "full_name": "Example Employee",
            "email": "employee@example.com",
            "department": "Finance",
            "reason": "Need access to the finance knowledge base.",
            "consent": True,
        },
    )

    assert response.status_code == 202, response.text
    assert response.json()["status"] == "PENDING_ADMIN_REVIEW"
    assert response.json()["email_confirmation"] == "NOT_CONFIGURED"


def test_access_request_idempotency_returns_the_original_request():
    """Repro: browser retries the same onboarding submission."""

    payload = {
        "full_name": "Example Employee",
        "email": "employee@example.com",
        "department": "Finance",
        "reason": "Need access to the finance knowledge base.",
        "consent": True,
    }
    headers = {"Idempotency-Key": "customer-qa-access-002"}
    first = request("POST", "/api/v1/access-requests", headers=headers, json=payload)
    second = request("POST", "/api/v1/access-requests", headers=headers, json=payload)

    assert first.status_code == 202, first.text
    assert second.status_code == 202, second.text
    assert second.json() == first.json()


def test_access_request_requires_consent():
    """Repro: onboarding cannot be submitted without explicit consent."""

    response = request(
        "POST",
        "/api/v1/access-requests",
        headers={"Idempotency-Key": "customer-qa-access-003"},
        json={
            "full_name": "Example Employee",
            "email": "employee@example.com",
            "department": "Finance",
            "reason": "Need access.",
            "consent": False,
        },
    )

    assert response.status_code == 400, response.text
    assert response.json()["code"] == "REQUEST_INVALID"
