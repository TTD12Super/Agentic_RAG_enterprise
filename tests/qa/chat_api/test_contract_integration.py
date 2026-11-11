from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.app.api import identity as identity_api
from backend.app.authorization import AuthorizationEvaluator, InMemoryPolicyStore, PolicyEnforcementPoint
from backend.app.core.chat import (
    AnswerState,
    CitationArtifact,
    ChatService,
    InMemoryChatRepository,
    JobState,
    QueryCompletion,
    job_payload,
)
from backend.app.identity.errors import IdentityError
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.main import app
from backend.app.observability import InMemoryAuditSink


ROOT = Path(__file__).resolve().parents[3]
BASELINE = (ROOT / "docs" / "contracts" / "v1-baseline.md").read_text(encoding="utf-8")
CHAT_CONTRACT = (ROOT / "docs" / "contracts" / "chat-and-jobs.md").read_text(encoding="utf-8")
NOW = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)


class Clock:
    def __init__(self) -> None:
        self.now = NOW

    def __call__(self) -> datetime:
        return self.now


class Maintenance:
    def __init__(self) -> None:
        self.window_id: str | None = None

    def __call__(self, tenant_id: str) -> str | None:
        return self.window_id


class Executor:
    def __init__(self, result: object, on_run=None) -> None:
        self.result = result
        self.on_run = on_run
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        if self.on_run is not None:
            self.on_run(request)
        return self.result


class RecordingPep:
    def __init__(self, store: InMemoryPolicyStore) -> None:
        self.actions = []
        self._real = PolicyEnforcementPoint(AuthorizationEvaluator(store))

    def enforce(self, principal, action, resource=None):
        self.actions.append(action)
        return self._real.enforce(principal, action, resource)


def principal(user_id: str = "user-a", tenant_id: str = "tenant-a") -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=["employee"],
        department_ids=["dept-a"],
        session_id=f"session-{user_id}",
        auth_time="2026-11-11T12:00:00Z",
    )


def make_service(*, result: object | None = None, on_run=None, document_state_provider=None, maintenance=None):
    store = InMemoryPolicyStore(policy_epoch=7)
    clock = Clock()
    current_maintenance = maintenance or Maintenance()
    executor = Executor(result or QueryCompletion(AnswerState.ANSWERED, "contract answer"), on_run=on_run)
    repository = InMemoryChatRepository()
    service = ChatService(
        repository=repository,
        executor=executor,
        policy_store=store,
        pep=PolicyEnforcementPoint(AuthorizationEvaluator(store)),
        clock=clock,
        maintenance_probe=current_maintenance,
        document_state_provider=document_state_provider,
    )
    return service, repository, clock, current_maintenance, executor, store


def authenticated_conversation(service: ChatService, user_id: str = "user-a"):
    actor, _ = service.actor_for_create(principal(user_id), None)
    return actor, service.create_conversation(actor)


def anonymous_conversation(service: ChatService):
    actor, created = service.actor_for_create(None, None)
    assert created and actor.session_token
    return actor, service.create_conversation(actor)


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


def test_contract_routes_are_versioned_and_complete():
    routes = {
        (f"/api/v1{route.path}", method)
        for route in chat_api.router.routes
        for method in getattr(route, "methods", set())
    }
    expected = {
        ("/api/v1/conversations", "POST"),
        ("/api/v1/conversations/{conversation_id}", "GET"),
        ("/api/v1/conversations/{conversation_id}/messages", "POST"),
        ("/api/v1/query-jobs/{job_id}", "GET"),
        ("/api/v1/query-jobs/{job_id}/completion", "GET"),
        ("/api/v1/answers/{answer_id}/citations/{citation_id}/preview", "GET"),
        ("/api/v1/answers/{answer_id}/citations/{citation_id}/download", "GET"),
        ("/api/v1/answers/{answer_id}/feedback", "POST"),
    }

    assert expected <= routes
    assert "REST/HTTP JSON under `/api/v1`" in BASELINE


def test_contract_job_payload_has_version_deadline_and_safe_state():
    service, _, _, _, _, _ = make_service()
    actor, conversation = authenticated_conversation(service)
    job = service.submit(actor, conversation.conversation_id, "contract envelope", idempotency_key="contract-envelope-001")
    payload = job_payload(job)

    assert payload["schema_version"] == "1.0"
    assert payload["state"] == "QUEUED"
    assert payload["maintenance"] is None
    assert payload["workflow_deadline_at"].endswith("Z")
    assert set(("job_id", "conversation_id", "attempt", "revision", "workflow_deadline_at")) <= payload.keys()


def test_contract_requires_a_nontrivial_idempotency_key():
    service, _, _, _, _, _ = make_service()
    actor, conversation = authenticated_conversation(service)

    with pytest.raises(IdentityError) as missing:
        service.submit(actor, conversation.conversation_id, "missing key", idempotency_key=None)
    with pytest.raises(IdentityError) as short:
        service.submit(actor, conversation.conversation_id, "short key", idempotency_key="short")

    assert missing.value.code == short.value.code == "IDEMPOTENCY_REQUIRED"
    assert missing.value.status_code == short.value.status_code == 400
    assert "idempotency key" in CHAT_CONTRACT.lower()


def test_contract_changed_replay_has_stable_conflict_code():
    service, _, _, _, _, _ = make_service()
    service.auto_process = False
    actor, conversation = authenticated_conversation(service)
    key = "contract-replay-001"
    first = service.submit(actor, conversation.conversation_id, "original", idempotency_key=key)
    same = service.submit(actor, conversation.conversation_id, "original", idempotency_key=key)
    with pytest.raises(IdentityError) as changed:
        service.submit(actor, conversation.conversation_id, "different", idempotency_key=key)

    assert first.job_id == same.job_id
    assert changed.value.code == "IDEMPOTENCY_KEY_REUSED"
    assert changed.value.status_code == 409


def test_contract_scope_and_worker_fields_are_server_bound():
    service, _, _, _, executor, _ = make_service()
    actor, conversation = authenticated_conversation(service)
    submitted = service.submit(actor, conversation.conversation_id, "scope-bound question", idempotency_key="contract-scope-001")
    completed = service.status(actor, submitted.job_id)
    worker_request = executor.requests[0]

    assert completed.state is JobState.COMPLETED
    assert worker_request.principal_ref == actor.actor_id
    assert worker_request.job_id == submitted.job_id
    assert worker_request.attempt_id == submitted.attempt_id
    assert worker_request.authorized_scope_ref != "scope-bound question"
    assert worker_request.traceparent.startswith("00-")
    assert "never accepted from the browser" in BASELINE


def test_contract_maintenance_is_mode_not_a_job_state():
    service, _, _, maintenance, _, _ = make_service()
    service.auto_process = True
    actor, conversation = anonymous_conversation(service)
    submitted = service.submit(actor, conversation.conversation_id, "queued before maintenance", idempotency_key="contract-maint-001")
    maintenance.window_id = "window-1"

    status = service.status(actor, submitted.job_id)
    payload = job_payload(status, maintenance=maintenance.window_id)

    assert status.state is JobState.QUEUED
    assert payload["state"] == "QUEUED"
    assert payload["maintenance"] == "window-1"
    assert "MAINTENANCE_ACTIVE" in CHAT_CONTRACT and "not a job state" in BASELINE


def test_contract_pause_resume_rejects_a_stale_policy_scope():
    maintenance = Maintenance()

    def pause_after_provider(_request):
        maintenance.window_id = "window-2"

    service, _, _, _, _, store = make_service(on_run=pause_after_provider, maintenance=maintenance)
    service.auto_process = False
    actor, conversation = authenticated_conversation(service)
    submitted = service.submit(actor, conversation.conversation_id, "pause boundary", idempotency_key="contract-pause-001")
    paused = service.process(actor, submitted.job_id)
    assert paused.state is JobState.PAUSED and paused.checkpoint is not None

    store.policy_epoch = 8
    with pytest.raises(IdentityError) as error:
        service.status(actor, submitted.job_id)

    assert error.value.status_code == 404
    assert paused.checkpoint.stage == "PAUSED"
    assert paused.checkpoint.policy_epoch == 7
    assert "fresh principal, tenant, ACL, policy epoch" in BASELINE


def test_contract_citation_delivery_revalidates_current_version():
    state = {"artifact": CitationArtifact(
        {"citation_id": "c-1", "tenant_id": "public", "document_id": "doc-1", "version_id": "v-1"},
        preview="preview",
        download=b"download",
        classification="PUBLIC",
        current_version_id="v-1",
    )}
    service, repository, _, _, _, _ = make_service(document_state_provider=lambda artifact: state["artifact"])
    actor, conversation = anonymous_conversation(service)
    submitted = service.submit(actor, conversation.conversation_id, "citation contract", idempotency_key="contract-cite-001")
    completed = service.status(actor, submitted.job_id)
    assert completed.response_message_id is not None
    repository.add_citation(completed.response_message_id, state["artifact"])

    assert service.citation(actor, completed.response_message_id, "c-1", download=False).preview == "preview"
    state["artifact"] = CitationArtifact(
        state["artifact"].citation,
        preview="stale",
        download=b"stale",
        classification="PUBLIC",
        version_status="SUPERSEDED",
        current_version_id="v-1",
    )
    with pytest.raises(IdentityError) as error:
        service.citation(actor, completed.response_message_id, "c-1", download=True)

    assert error.value.status_code == 404
    assert "fresh `document:read` check" in BASELINE
    assert "separate `source:download` check" in BASELINE


def test_contract_feedback_response_omits_comment_and_replays_safely():
    created = request("POST", "/api/v1/conversations")
    assert created.status_code == 201
    token = created.cookies.get(chat_api.ANONYMOUS_SESSION_COOKIE)
    conversation_id = created.json()["conversation_id"]
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "contract-http-feedback-001"},
        json={"query": "feedback"},
    )
    answer = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token},
    ).json()["answer"]["answer_id"]
    headers = {"X-Anonymous-Session": token, "Idempotency-Key": "contract-http-feedback-002"}

    first = request("POST", f"/api/v1/answers/{answer}/feedback", headers=headers, json={"rating": "POSITIVE", "comment": "do not echo"})
    replay = request("POST", f"/api/v1/answers/{answer}/feedback", headers=headers, json={"rating": "POSITIVE", "comment": "do not echo"})

    assert first.status_code == 201 and replay.status_code == 200
    assert first.json()["feedback_id"] == replay.json()["feedback_id"]
    assert "comment" not in first.json()
    assert "do not echo" not in first.text


def test_contract_checkpoint_and_request_keep_protocol_metadata_only():
    service, _, _, _, executor, _ = make_service()
    actor, conversation = authenticated_conversation(service)
    raw_query = "RAW PROMPT SHOULD NOT ENTER CHECKPOINT"
    submitted = service.submit(actor, conversation.conversation_id, raw_query, idempotency_key="contract-protocol-001")
    completed = service.status(actor, submitted.job_id)
    request_metadata = executor.requests[0]

    assert completed.checkpoint is not None
    assert raw_query not in repr(completed.checkpoint)
    assert request_metadata.deadline_at == submitted.workflow_deadline_at
    assert request_metadata.attempt_id == submitted.attempt_id
    assert request_metadata.principal_ref == actor.actor_id
    assert "metadata only" in BASELINE
    assert "never contain conversation bodies" in BASELINE
