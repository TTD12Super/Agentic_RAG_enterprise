from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
import pytest

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.app.api import identity as identity_api
from backend.app.core.chat import AnswerState, CitationArtifact, QueryCompletion
from backend.app.main import app
from backend.app.observability import InMemoryAuditSink


def request(method: str, path: str, **kwargs: object) -> httpx.Response:
    async def run() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(run())


class StubExecutor:
    def __init__(self, result: object) -> None:
        self.result = result
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return self.result


@pytest.fixture(autouse=True)
def clean_state():
    admin_api.reset_state()
    identity_api.audit_sink = InMemoryAuditSink()
    chat_api.reset_state()


def anonymous_conversation() -> tuple[str, str]:
    response = request("POST", "/api/v1/conversations")
    assert response.status_code == 201, response.text
    return response.json()["conversation_id"], response.cookies.get(chat_api.ANONYMOUS_SESSION_COOKIE)


def authenticated_headers(role: str = "employee") -> tuple[dict[str, str], str]:
    email = f"{role}-{uuid4().hex}@example.com"
    user_id = f"{role}-{uuid4().hex}"
    identity_api.identity_store.add_identity(
        user_id=user_id,
        tenant_id="tenant-chat-tests",
        email=email,
        password="correct-password",
        roles=[role],
        mfa_code="123456" if role in {"chairman", "website_manager", "system_admin"} else None,
    )
    response = request(
        "POST",
        "/api/v1/auth/sign-in",
        json={
            "email": email,
            "password": "correct-password",
            **({"mfa_code": "123456"} if role in {"chairman", "website_manager", "system_admin"} else {}),
        },
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}, user_id


def test_anonymous_submit_status_completion_and_history_are_session_scoped():
    conversation_id, token = anonymous_conversation()
    headers = {"X-Anonymous-Session": token, "Idempotency-Key": "anonymous-submit-001"}

    submitted = request(
        "POST", f"/api/v1/conversations/{conversation_id}/messages", headers=headers, json={"query": "hello"}
    )
    assert submitted.status_code == 202
    job_id = submitted.json()["job_id"]

    status = request("GET", f"/api/v1/query-jobs/{job_id}", headers={"X-Anonymous-Session": token})
    assert status.status_code == 200
    assert status.json()["state"] == "COMPLETED"
    assert status.json()["answer"]["status"] == "INSUFFICIENT_EVIDENCE"

    history = request("GET", f"/api/v1/conversations/{conversation_id}", headers={"X-Anonymous-Session": token})
    assert history.status_code == 200
    assert [message["role"] for message in history.json()["messages"]] == ["user", "assistant"]

    other_conversation, other_token = anonymous_conversation()
    denied = request(
        "GET", f"/api/v1/conversations/{conversation_id}", headers={"X-Anonymous-Session": other_token}
    )
    assert denied.status_code == 404
    assert other_conversation != conversation_id


def test_submission_replay_is_idempotent_and_changed_replay_is_denied():
    conversation_id, token = anonymous_conversation()
    headers = {"X-Anonymous-Session": token, "Idempotency-Key": "anonymous-replay-001"}
    first = request(
        "POST", f"/api/v1/conversations/{conversation_id}/messages", headers=headers, json={"query": "same"}
    )
    replay = request(
        "POST", f"/api/v1/conversations/{conversation_id}/messages", headers=headers, json={"query": "same"}
    )
    changed = request(
        "POST", f"/api/v1/conversations/{conversation_id}/messages", headers=headers, json={"query": "changed"}
    )
    assert first.status_code == replay.status_code == 202
    assert first.json()["job_id"] == replay.json()["job_id"]
    assert changed.status_code == 409
    assert changed.json()["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_authenticated_history_is_owner_only_and_revocation_denies_reuse():
    owner_headers, owner_id = authenticated_headers()
    other_headers, _ = authenticated_headers()
    created = request("POST", "/api/v1/conversations", headers=owner_headers)
    conversation_id = created.json()["conversation_id"]
    denied = request("GET", f"/api/v1/conversations/{conversation_id}", headers=other_headers)
    assert denied.status_code == 404

    admin_api.policy_store.revoked_principals.add(("tenant-chat-tests", owner_id))
    revoked = request("GET", f"/api/v1/conversations/{conversation_id}", headers=owner_headers)
    assert revoked.status_code == 404


def test_maintenance_blocks_new_work_and_existing_job_resumes():
    conversation_id, token = anonymous_conversation()
    window = admin_api.ingestion_service.start_maintenance(
        admin_api._tenant_uuid("public"), reason="synthetic maintenance"
    )
    blocked = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "maintenance-submit-001"},
        json={"query": "blocked"},
    )
    assert blocked.status_code == 503
    assert blocked.json()["code"] == "MAINTENANCE_ACTIVE"

    admin_api.ingestion_service.finish_maintenance(window.window_id, window.tenant_id)
    admitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "maintenance-submit-002"},
        json={"query": "resumed"},
    )
    assert admitted.status_code == 202
    result = request(
        "GET", f"/api/v1/query-jobs/{admitted.json()['job_id']}", headers={"X-Anonymous-Session": token}
    )
    assert result.json()["state"] == "COMPLETED"


def test_timeout_fails_without_answer():
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "timeout-submit-001"},
        json={"query": "timeout"},
    )
    clock = datetime.now(timezone.utc)
    chat_api.chat_service.clock = lambda: clock + timedelta(seconds=61)
    result = request(
        "GET", f"/api/v1/query-jobs/{submitted.json()['job_id']}", headers={"X-Anonymous-Session": token}
    )
    assert result.json()["state"] == "FAILED"
    assert result.json()["error"]["code"] == "TIMEOUT"


def test_citation_preview_and_download_are_separate_fresh_authorization_checks():
    conversation_id, token = anonymous_conversation()
    chat_api.chat_service.executor = StubExecutor(
        QueryCompletion(
            AnswerState.ANSWERED,
            "public answer",
            ({"citation_id": "c-1", "tenant_id": "public", "document_id": "doc-1", "version_id": "v-1"},),
        )
    )
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "citation-submit-001"},
        json={"query": "source"},
    )
    status = request(
        "GET", f"/api/v1/query-jobs/{submitted.json()['job_id']}", headers={"X-Anonymous-Session": token}
    ).json()
    answer_id = status["answer"]["answer_id"]
    artifact = CitationArtifact(
        status["answer"]["citations"][0], preview="public excerpt", download=b"public file", classification="PUBLIC", current_version_id="v-1"
    )
    chat_api.chat_service.repository.add_citation(answer_id, artifact)
    preview = request(
        "GET", f"/api/v1/answers/{answer_id}/citations/c-1/preview", headers={"X-Anonymous-Session": token}
    )
    download = request(
        "GET", f"/api/v1/answers/{answer_id}/citations/c-1/download", headers={"X-Anonymous-Session": token}
    )
    assert preview.status_code == 200 and preview.json()["preview"] == "public excerpt"
    assert download.status_code == 200 and download.content == b"public file"

    chat_api.chat_service.repository.add_citation(
        answer_id,
        CitationArtifact(
            artifact.citation, preview="revoked", download=b"revoked", classification="PUBLIC", status="REVOKED", current_version_id="v-1"
        ),
    )
    revoked = request(
        "GET", f"/api/v1/answers/{answer_id}/citations/c-1/preview", headers={"X-Anonymous-Session": token}
    )
    assert revoked.status_code == 404


def test_feedback_is_private_and_idempotent():
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "feedback-query-001"},
        json={"query": "feedback"},
    )
    answer = request(
        "GET", f"/api/v1/query-jobs/{submitted.json()['job_id']}", headers={"X-Anonymous-Session": token}
    ).json()["answer"]["answer_id"]
    headers = {"X-Anonymous-Session": token, "Idempotency-Key": "feedback-submit-001"}
    first = request("POST", f"/api/v1/answers/{answer}/feedback", headers=headers, json={"rating": "POSITIVE", "comment": "private note"})
    replay = request("POST", f"/api/v1/answers/{answer}/feedback", headers=headers, json={"rating": "POSITIVE", "comment": "private note"})
    changed = request("POST", f"/api/v1/answers/{answer}/feedback", headers={**headers, "Idempotency-Key": "feedback-submit-002"}, json={"rating": "NEGATIVE"})
    assert first.status_code == 201
    assert replay.status_code == 200
    assert first.json()["feedback_id"] == replay.json()["feedback_id"]
    assert changed.status_code == 409
    assert "private note" not in first.text
    assert all("private note" not in repr(event.as_dict()) for event in identity_api.audit_sink.events)
