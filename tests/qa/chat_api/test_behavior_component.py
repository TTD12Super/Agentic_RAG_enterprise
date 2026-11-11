from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.authorization import (
    Action,
    AuthorizationEvaluator,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.core.chat import (
    AnswerState,
    CitationArtifact,
    ChatService,
    InMemoryChatRepository,
    JobState,
    QueryCompletion,
    QUERY_TIMEOUT,
)
from backend.app.feedback import FeedbackService, InMemoryFeedbackRepository
from backend.app.identity.errors import IdentityError
from backend.app.identity.models import AuthenticatedPrincipal


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
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class RecordingPep:
    def __init__(self, policy_store: InMemoryPolicyStore) -> None:
        self.actions = []
        self._real = PolicyEnforcementPoint(AuthorizationEvaluator(policy_store))

    def enforce(self, principal, action, resource=None):
        self.actions.append(action)
        return self._real.enforce(principal, action, resource)


def principal(user_id: str, tenant_id: str = "tenant-a") -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=["employee"],
        department_ids=["dept-a"],
        session_id=f"session-{user_id}",
        auth_time="2026-11-11T12:00:00Z",
    )


def make_service(
    *,
    result: object | None = None,
    policy_store: InMemoryPolicyStore | None = None,
    pep=None,
    clock: Clock | None = None,
    maintenance: Maintenance | None = None,
    on_run=None,
):
    store = policy_store or InMemoryPolicyStore(policy_epoch=7)
    current_clock = clock or Clock()
    current_maintenance = maintenance or Maintenance()
    executor = Executor(
        result or QueryCompletion(AnswerState.ANSWERED, "synthetic answer"),
        on_run=on_run,
    )
    repository = InMemoryChatRepository()
    service = ChatService(
        repository=repository,
        executor=executor,
        pep=pep or PolicyEnforcementPoint(AuthorizationEvaluator(store)),
        policy_store=store,
        clock=current_clock,
        maintenance_probe=current_maintenance,
    )
    return service, repository, current_clock, current_maintenance, executor, store


def authenticated_conversation(service: ChatService, user_id: str = "user-a"):
    actor, _ = service.actor_for_create(principal(user_id), None)
    conversation = service.create_conversation(actor)
    return actor, conversation


def anonymous_conversation(service: ChatService):
    actor, created = service.actor_for_create(None, None)
    assert created and actor.session_token
    conversation = service.create_conversation(actor)
    return actor, conversation


def test_authenticated_owner_history_and_completion():
    service, _, _, _, _, _ = make_service()
    actor, conversation = authenticated_conversation(service)

    job = service.submit(actor, conversation.conversation_id, "owned question", idempotency_key="behavior-owned-001")
    completed = service.status(actor, job.job_id)
    history = service.conversation(actor, conversation.conversation_id)

    assert completed.state is JobState.COMPLETED
    assert completed.completion is not None
    assert completed.completion.status is AnswerState.ANSWERED
    assert [message.content for _, message in history.messages] == ["owned question", "synthetic answer"]


def test_anonymous_sessions_are_isolated_for_history_and_job():
    service, _, _, _, _, _ = make_service()
    owner, conversation = anonymous_conversation(service)
    other, _ = anonymous_conversation(service)
    job = service.submit(owner, conversation.conversation_id, "private anonymous question", idempotency_key="behavior-anon-001")

    with pytest.raises(IdentityError) as history_error:
        service.conversation(other, conversation.conversation_id)
    with pytest.raises(IdentityError) as job_error:
        service.status(other, job.job_id)

    assert history_error.value.status_code == 404
    assert job_error.value.status_code == 404
    assert history_error.value.code == job_error.value.code == "NOT_FOUND_OR_FORBIDDEN"


def test_authenticated_job_is_owner_only():
    service, _, _, _, _, _ = make_service()
    owner, conversation = authenticated_conversation(service, "user-a")
    other, _ = authenticated_conversation(service, "user-b")
    job = service.submit(owner, conversation.conversation_id, "owner job", idempotency_key="behavior-job-001")

    with pytest.raises(IdentityError) as error:
        service.status(other, job.job_id)

    assert error.value.status_code == 404
    assert error.value.message == "The requested resource is unavailable."


def test_idempotent_replay_returns_same_job_and_changed_query_fails():
    service, repository, _, _, _, _ = make_service()
    service.auto_process = False
    actor, conversation = authenticated_conversation(service)
    key = "behavior-replay-001"

    first = service.submit(actor, conversation.conversation_id, "same query", idempotency_key=key)
    replay = service.submit(actor, conversation.conversation_id, "same query", idempotency_key=key)
    with pytest.raises(IdentityError) as error:
        service.submit(actor, conversation.conversation_id, "changed query", idempotency_key=key)

    history = service.conversation(actor, conversation.conversation_id)
    assert first.job_id == replay.job_id
    assert len(history.messages) == 1
    assert len(repository._jobs) == 1
    assert error.value.code == "IDEMPOTENCY_KEY_REUSED"


def test_feedback_is_private_and_idempotent_per_actor():
    service, _, _, _, _, _ = make_service()
    owner, conversation = authenticated_conversation(service, "user-a")
    job = service.submit(owner, conversation.conversation_id, "feedback target", idempotency_key="behavior-feedback-001")
    answer = service.status(owner, job.job_id)
    assert answer.response_message_id is not None

    feedback = FeedbackService(InMemoryFeedbackRepository())
    service.feedback_target(owner, answer.response_message_id)
    first, first_replayed = feedback.submit(
        answer_id=answer.response_message_id,
        actor_id=owner.actor_id,
        rating="POSITIVE",
        comment="private note",
        idempotency_key="behavior-feedback-002",
    )
    same, same_replayed = feedback.submit(
        answer_id=answer.response_message_id,
        actor_id=owner.actor_id,
        rating="POSITIVE",
        comment="private note",
        idempotency_key="behavior-feedback-002",
    )
    with pytest.raises(IdentityError) as changed:
        feedback.submit(
            answer_id=answer.response_message_id,
            actor_id=owner.actor_id,
            rating="NEGATIVE",
            comment=None,
            idempotency_key="behavior-feedback-003",
        )
    other, _ = authenticated_conversation(service, "user-b")
    with pytest.raises(IdentityError) as denied:
        service.feedback_target(other, answer.response_message_id)

    assert first.feedback_id == same.feedback_id
    assert not first_replayed and same_replayed and changed.value.code == "FEEDBACK_ALREADY_RECORDED"
    assert denied.value.status_code == 404
    assert first.comment == "private note"


def test_preview_and_download_use_fresh_separate_actions():
    store = InMemoryPolicyStore(policy_epoch=7)
    pep = RecordingPep(store)
    citation = {"citation_id": "citation-1", "tenant_id": "public", "document_id": "doc-1", "version_id": "v-1"}
    service, repository, _, _, _, _ = make_service(
        policy_store=store,
        pep=pep,
        result=QueryCompletion(AnswerState.ANSWERED, "answer", (citation,)),
    )
    actor, conversation = anonymous_conversation(service)
    submitted = service.submit(actor, conversation.conversation_id, "source question", idempotency_key="behavior-citation-001")
    completed = service.status(actor, submitted.job_id)
    assert completed.response_message_id is not None
    repository.add_citation(
        completed.response_message_id,
        CitationArtifact(citation, preview="preview", download=b"source", classification="PUBLIC", current_version_id="v-1"),
    )

    assert service.citation(actor, completed.response_message_id, "citation-1", download=False).preview == "preview"
    assert service.citation(actor, completed.response_message_id, "citation-1", download=True).download == b"source"
    document_actions = [action for action in pep.actions if action in {Action.DOCUMENT_READ, Action.SOURCE_DOWNLOAD}]
    assert document_actions == [Action.DOCUMENT_READ, Action.SOURCE_DOWNLOAD]


def test_deadline_timeout_fails_without_executor_delivery():
    service, _, clock, _, executor, _ = make_service()
    service.auto_process = False
    actor, conversation = authenticated_conversation(service)
    job = service.submit(actor, conversation.conversation_id, "deadline question", idempotency_key="behavior-timeout-001")
    clock.now += QUERY_TIMEOUT + timedelta(seconds=1)

    failed = service.process(actor, job.job_id)

    assert failed.state is JobState.FAILED
    assert failed.error_code == "TIMEOUT"
    assert executor.requests == []


def test_maintenance_blocks_new_admission_without_creating_job():
    service, repository, _, maintenance, _, _ = make_service()
    actor, conversation = anonymous_conversation(service)
    maintenance.window_id = "maintenance-1"

    with pytest.raises(IdentityError) as error:
        service.submit(actor, conversation.conversation_id, "blocked question", idempotency_key="behavior-maint-001")

    assert error.value.code == "MAINTENANCE_ACTIVE"
    assert error.value.status_code == 503
    assert error.value.retryable
    assert repository._jobs == {}


def test_maintenance_pause_checkpoint_resumes_with_new_attempt():
    maintenance = Maintenance()
    runs = {"count": 0}

    def pause_after_provider(_request):
        runs["count"] += 1
        if runs["count"] == 1:
            maintenance.window_id = "maintenance-2"

    service, _, _, _, executor, _ = make_service(maintenance=maintenance, on_run=pause_after_provider)
    service.auto_process = False
    actor, conversation = authenticated_conversation(service)
    submitted = service.submit(actor, conversation.conversation_id, "pause me", idempotency_key="behavior-pause-001")
    paused = service.process(actor, submitted.job_id)

    assert paused.state is JobState.PAUSED
    assert paused.maintenance_window_id == "maintenance-2"
    assert paused.checkpoint is not None
    assert paused.checkpoint.stage == "PAUSED"
    assert paused.checkpoint.safe_metadata == {}
    paused_attempt = paused.attempt_id

    maintenance.window_id = None
    service.auto_process = True
    resumed = service.status(actor, submitted.job_id)

    assert resumed.state is JobState.COMPLETED
    assert resumed.attempt_id != paused_attempt
    assert len(executor.requests) == 2


def test_checkpoint_redacts_raw_query_and_answer():
    secret_query = "raw-question SECRET_PROMPT"
    secret_answer = "SECRET_ANSWER"
    service, _, _, _, _, _ = make_service(result=QueryCompletion(AnswerState.ANSWERED, secret_answer))
    service.auto_process = False
    actor, conversation = authenticated_conversation(service)
    submitted = service.submit(actor, conversation.conversation_id, secret_query, idempotency_key="behavior-redact-001")
    completed = service.process(actor, submitted.job_id)

    assert completed.checkpoint is not None
    assert secret_query not in repr(completed.checkpoint)
    assert secret_answer not in repr(completed.checkpoint)
    assert completed.checkpoint.query_hash != secret_query
    assert completed.checkpoint.safe_metadata == {}
