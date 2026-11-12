from __future__ import annotations

import asyncio
from datetime import timedelta

import httpx
import pytest

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.app.api import identity as identity_api
from backend.app.core.chat import AnswerState, CitationArtifact, QueryCompletion
from backend.app.main import app
from backend.app.observability import InMemoryAuditSink
from backend.tests._admin_api_fixtures import auth, publish


class HttpExecutor:
    def __init__(self, result: object, on_run=None) -> None:
        self.result = result
        self.on_run = on_run
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        if self.on_run is not None:
            self.on_run(request)
        return self.result


def request(method: str, path: str, **kwargs: object) -> httpx.Response:
    async def run() -> httpx.Response:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(run())


@pytest.fixture(autouse=True)
def reset_api_state():
    admin_api.reset_state()
    identity_api.audit_sink = InMemoryAuditSink()
    chat_api.reset_state()


def anonymous_conversation() -> tuple[str, str]:
    response = request("POST", "/api/v1/conversations")
    assert response.status_code == 201, response.text
    token = response.cookies.get(chat_api.ANONYMOUS_SESSION_COOKIE)
    assert token
    return response.json()["conversation_id"], token


def sign_in(user_id: str) -> dict[str, str]:
    email = f"{user_id}@example.test"
    identity_api.identity_store.add_identity(
        user_id=user_id,
        tenant_id="tenant-e2e",
        email=email,
        password="correct-password",
        roles=["employee"],
    )
    response = request(
        "POST",
        "/api/v1/auth/sign-in",
        json={"email": email, "password": "correct-password"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_http_anonymous_lifecycle_and_session_isolation():
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "e2e-lifecycle-001"},
        json={"query": "hello"},
    )
    completed = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token},
    )
    other_conversation, other_token = anonymous_conversation()
    history = request("GET", f"/api/v1/conversations/{conversation_id}", headers={"X-Anonymous-Session": token})
    denied = request("GET", f"/api/v1/conversations/{conversation_id}", headers={"X-Anonymous-Session": other_token})

    assert other_conversation != conversation_id
    assert submitted.status_code == 202
    assert completed.status_code == 200 and completed.json()["state"] == "COMPLETED"
    assert [message["role"] for message in history.json()["messages"]] == ["user", "assistant"]
    assert denied.status_code == 404


def test_http_authenticated_history_and_job_are_owner_only():
    owner_headers = sign_in("e2e-owner")
    other_headers = sign_in("e2e-other")
    created = request("POST", "/api/v1/conversations", headers=owner_headers)
    conversation_id = created.json()["conversation_id"]
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={**owner_headers, "Idempotency-Key": "qa-e2e-owner-001"},
        json={"query": "owner only"},
    )
    job_id = submitted.json()["job_id"]

    history = request("GET", f"/api/v1/conversations/{conversation_id}", headers=other_headers)
    job = request("GET", f"/api/v1/query-jobs/{job_id}", headers=other_headers)

    assert created.status_code == 201 and submitted.status_code == 202
    assert history.status_code == job.status_code == 404
    assert history.json()["code"] == job.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_http_idempotent_and_changed_replay_are_distinct():
    conversation_id, token = anonymous_conversation()
    headers = {"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-replay-001"}
    first = request("POST", f"/api/v1/conversations/{conversation_id}/messages", headers=headers, json={"query": "same"})
    replay = request("POST", f"/api/v1/conversations/{conversation_id}/messages", headers=headers, json={"query": "same"})
    changed = request("POST", f"/api/v1/conversations/{conversation_id}/messages", headers=headers, json={"query": "changed"})

    assert first.status_code == replay.status_code == 202
    assert first.json()["job_id"] == replay.json()["job_id"]
    assert changed.status_code == 409
    assert changed.json()["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_http_deadline_failure_is_safe_and_has_no_answer():
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-timeout-001"},
        json={"query": "will time out"},
    )
    original_clock = chat_api.chat_service.clock
    chat_api.chat_service.clock = lambda: original_clock() + timedelta(seconds=61)
    failed = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token},
    )

    assert failed.status_code == 200
    assert failed.json()["state"] == "FAILED"
    assert failed.json()["error"] == {"code": "TIMEOUT"}
    assert "answer" not in failed.json()


def test_http_maintenance_blocks_admission_then_allows_new_work():
    conversation_id, token = anonymous_conversation()
    window = admin_api.ingestion_service.start_maintenance(admin_api._tenant_uuid("public"), reason="qa")
    blocked = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-maint-001"},
        json={"query": "blocked"},
    )
    admin_api.ingestion_service.finish_maintenance(window.window_id, window.tenant_id)
    admitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-maint-002"},
        json={"query": "allowed after maintenance"},
    )

    assert blocked.status_code == 503
    assert blocked.json()["code"] == "MAINTENANCE_ACTIVE"
    assert blocked.json()["retryable"] is True
    assert admitted.status_code == 202


def test_http_running_job_pauses_and_resumes_with_a_checkpoint():
    window = {}

    def pause_first_run(_request):
        if "record" not in window:
            window["record"] = admin_api.ingestion_service.start_maintenance(
                admin_api._tenant_uuid("public"), reason="qa pause"
            )

    chat_api.chat_service.executor = HttpExecutor(
        QueryCompletion(AnswerState.ANSWERED, "resumed answer"),
        on_run=pause_first_run,
    )
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-pause-001"},
        json={"query": "pause and resume"},
    )
    paused = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token},
    )
    record = window["record"]
    admin_api.ingestion_service.finish_maintenance(record.window_id, record.tenant_id)
    resumed = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token},
    )

    assert paused.status_code == 200
    assert paused.json()["state"] == "PAUSED"
    assert paused.json()["maintenance"] == str(record.window_id)
    assert "checkpoint" not in paused.json()
    assert resumed.json()["state"] == "COMPLETED"


def test_http_citation_preview_and_download_reauthorize_after_revocation():
    manager_headers, _ = auth("website_manager", tenant="public")
    document_id, version_id, _ = publish(manager_headers)
    citation = {"citation_id": "c-1", "tenant_id": "public", "document_id": str(document_id), "version_id": str(version_id)}
    chat_api.chat_service.executor = HttpExecutor(QueryCompletion(AnswerState.ANSWERED, "answer", (citation,)))
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-citation-001"},
        json={"query": "show source"},
    )
    completed = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token},
    ).json()
    answer_id = completed["answer"]["answer_id"]
    chat_api.chat_service.repository.add_citation(
        answer_id,
        CitationArtifact(citation, preview="excerpt", download=b"source", classification="PUBLIC", current_version_id="v-1"),
    )
    preview = request("GET", f"/api/v1/answers/{answer_id}/citations/c-1/preview", headers={"X-Anonymous-Session": token})
    download = request("GET", f"/api/v1/answers/{answer_id}/citations/c-1/download", headers={"X-Anonymous-Session": token})
    revoked_version = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/revoke",
        headers={**manager_headers, "Idempotency-Key": "qa-e2e-citation-revoke-001"},
        json={},
    )
    assert revoked_version.status_code == 200
    revoked = request("GET", f"/api/v1/answers/{answer_id}/citations/c-1/download", headers={"X-Anonymous-Session": token})

    assert preview.status_code == 200 and preview.json()["preview"] == "excerpt"
    assert download.status_code == 200 and download.content == b"source"
    assert revoked.status_code == 404


def test_http_feedback_is_private_idempotent_and_changed_replay_is_denied():
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-feedback-001"},
        json={"query": "feedback"},
    )
    answer_id = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token},
    ).json()["answer"]["answer_id"]
    headers = {"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-feedback-002"}
    first = request("POST", f"/api/v1/answers/{answer_id}/feedback", headers=headers, json={"rating": "POSITIVE", "comment": "private"})
    replay = request("POST", f"/api/v1/answers/{answer_id}/feedback", headers=headers, json={"rating": "POSITIVE", "comment": "private"})
    changed = request(
        "POST",
        f"/api/v1/answers/{answer_id}/feedback",
        headers={**headers, "Idempotency-Key": "qa-e2e-feedback-003"},
        json={"rating": "NEGATIVE"},
    )

    assert first.status_code == 201 and replay.status_code == 200
    assert first.json()["feedback_id"] == replay.json()["feedback_id"]
    assert "private" not in first.text
    assert changed.status_code == 409
    assert changed.json()["code"] == "FEEDBACK_ALREADY_RECORDED"
    assert all("private" not in repr(event.as_dict()) for event in identity_api.audit_sink.events)


def test_http_errors_are_safe_problem_envelopes():
    missing = request("GET", "/api/v1/conversations/not-a-real-id")
    conversation_id, token = anonymous_conversation()
    malformed = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "qa-e2e-error-001", "X-Request-ID": "qa-request-001"},
        content=b"not-json",
    )

    assert missing.status_code == 404
    assert set(("code", "message", "request_id", "retryable")) <= missing.json().keys()
    assert malformed.status_code == 400
    assert malformed.headers["content-type"].startswith("application/problem+json")
    assert malformed.json()["code"] == "REQUEST_INVALID"
    assert "Traceback" not in malformed.text
    assert "not-json" not in malformed.text


def test_http_protocol_boundary_returns_correlation_without_checkpoint_or_query():
    conversation_id, token = anonymous_conversation()
    query = "protocol boundary question"
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={
            "X-Anonymous-Session": token,
            "Idempotency-Key": "qa-e2e-protocol-001",
            "X-Request-ID": "qa-request-002",
        },
        json={"query": query},
    )
    status = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token, "X-Request-ID": "qa-request-003"},
    )

    assert submitted.json()["request_id"] == "qa-request-002"
    assert status.json()["request_id"] == "qa-request-003"
    assert query not in submitted.text
    assert "checkpoint" not in status.json()
    assert "traceparent" not in status.json()
