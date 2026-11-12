from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.authorization import (
    AccessGrant,
    Action,
    AuthorizationEvaluator,
    DocumentResource,
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
)
from backend.app.identity.errors import IdentityError
from backend.app.identity.models import AuthenticatedPrincipal


NOW = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)


class Clock:
    def __call__(self) -> datetime:
        return NOW


class Maintenance:
    def __call__(self, tenant_id: str) -> str | None:
        return None


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


def principal(user_id: str, tenant_id: str = "tenant-a") -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=["employee"],
        department_ids=["dept-a"],
        session_id=f"session-{user_id}",
        auth_time="2026-11-11T12:00:00Z",
    )


def make_service(*, store: InMemoryPolicyStore | None = None, result: object | None = None, on_run=None):
    policy_store = store or InMemoryPolicyStore(policy_epoch=7)
    executor = Executor(result or QueryCompletion(AnswerState.ANSWERED, "safe answer"), on_run=on_run)
    repository = InMemoryChatRepository()
    service = ChatService(
        repository=repository,
        executor=executor,
        policy_store=policy_store,
        pep=PolicyEnforcementPoint(AuthorizationEvaluator(policy_store)),
        clock=Clock(),
        maintenance_probe=Maintenance(),
    )
    return service, repository, executor, policy_store


def authenticated_conversation(service: ChatService, user_id: str, tenant_id: str = "tenant-a"):
    actor, _ = service.actor_for_create(principal(user_id, tenant_id), None)
    return actor, service.create_conversation(actor)


def anonymous_conversation(service: ChatService):
    actor, created = service.actor_for_create(None, None)
    assert created and actor.session_token
    return actor, service.create_conversation(actor)


def public_document(**overrides) -> DocumentResource:
    values = {
        "document_id": "doc-1",
        "tenant_id": "tenant-a",
        "classification": "PUBLIC",
        "current_version_id": "v-1",
        "version_id": "v-1",
    }
    values.update(overrides)
    return DocumentResource(**values)


def test_cross_tenant_conversation_access_is_denied_without_existence_leakage():
    service, _, _, _ = make_service()
    owner, conversation = authenticated_conversation(service, "user-a", "tenant-a")
    foreigner, _ = authenticated_conversation(service, "user-b", "tenant-b")

    with pytest.raises(IdentityError) as error:
        service.conversation(foreigner, conversation.conversation_id)

    assert error.value.status_code == 404
    assert error.value.code == "NOT_FOUND_OR_FORBIDDEN"
    assert conversation.conversation_id not in error.value.message
    assert owner.tenant_id != foreigner.tenant_id


def test_anonymous_token_substitution_and_unknown_tokens_are_denied():
    service, _, _, _ = make_service()
    owner, conversation = anonymous_conversation(service)
    other, _ = anonymous_conversation(service)

    with pytest.raises(IdentityError) as substitution:
        service.conversation(other, conversation.conversation_id)
    with pytest.raises(IdentityError) as unknown:
        service.actor_for_existing(None, "not-issued-by-server")

    assert substitution.value.status_code == unknown.value.status_code == 404
    assert substitution.value.code == unknown.value.code == "NOT_FOUND_OR_FORBIDDEN"
    assert owner.session_token != other.session_token


def test_authenticated_and_anonymous_owners_cannot_cross_read_each_other():
    service, _, _, _ = make_service()
    authenticated, authenticated_record = authenticated_conversation(service, "user-a")
    anonymous, anonymous_record = anonymous_conversation(service)

    with pytest.raises(IdentityError):
        service.conversation(anonymous, authenticated_record.conversation_id)
    with pytest.raises(IdentityError):
        service.conversation(authenticated, anonymous_record.conversation_id)


def test_invalid_principal_shape_fails_closed_at_the_policy_boundary():
    store = InMemoryPolicyStore(policy_epoch=7)
    decision = AuthorizationEvaluator(store).evaluate(
        object(), Action.DOCUMENT_READ, public_document()
    )

    assert not decision.allowed
    assert decision.reason_code == "INVALID_PRINCIPAL"


def test_explicit_source_download_deny_overrides_employee_role_allow():
    store = InMemoryPolicyStore(
        policy_epoch=7,
        grants={"tenant-a": (AccessGrant(Action.SOURCE_DOWNLOAD, "DENY", role="employee"),)},
    )
    user = principal("user-a")
    decision = AuthorizationEvaluator(store).evaluate(user, Action.SOURCE_DOWNLOAD, public_document())

    assert not decision.allowed
    assert decision.reason_code == "EXPLICIT_DENY"


def test_revocation_after_admission_denies_history_and_job_reads():
    service, _, _, store = make_service()
    owner, conversation = authenticated_conversation(service, "user-a")
    service.auto_process = False
    submitted = service.submit(owner, conversation.conversation_id, "revoked job", idempotency_key="security-revoke-001")
    store.revoked_principals.add((owner.tenant_id, owner.actor_id))

    with pytest.raises(IdentityError) as history:
        service.conversation(owner, conversation.conversation_id)
    with pytest.raises(IdentityError) as job:
        service.status(owner, submitted.job_id)

    assert history.value.status_code == job.value.status_code == 404
    assert history.value.code == job.value.code == "NOT_FOUND_OR_FORBIDDEN"


def test_policy_change_during_execution_fails_closed_before_result_delivery():
    store = InMemoryPolicyStore(policy_epoch=7)

    def revoke_scope(_request):
        store.policy_epoch = 8

    service, _, executor, _ = make_service(store=store, on_run=revoke_scope)
    service.auto_process = False
    owner, conversation = authenticated_conversation(service, "user-a")
    submitted = service.submit(owner, conversation.conversation_id, "stale result", idempotency_key="security-stale-001")
    failed = service.process(owner, submitted.job_id)

    assert failed.state is JobState.FAILED
    assert failed.error_code == "SCOPE_STALE"
    assert failed.completion is None
    assert len(executor.requests) == 1


def test_revoked_citation_version_is_denied_for_preview_and_download():
    result = QueryCompletion(
        AnswerState.ANSWERED,
        "answer",
        ({"citation_id": "c-1", "tenant_id": "tenant-a", "document_id": "doc-1", "version_id": "v-1"},),
    )
    service, repository, _, _ = make_service(result=result)
    owner, conversation = authenticated_conversation(service, "user-a")
    submitted = service.submit(owner, conversation.conversation_id, "revoked citation", idempotency_key="security-cite-001")
    completed = service.status(owner, submitted.job_id)
    assert completed.response_message_id is not None
    repository.add_citation(
        completed.response_message_id,
        CitationArtifact(
            result.citations[0],
            preview="should not be shown",
            download=b"should not be downloaded",
            classification="PUBLIC",
            status="REVOKED",
            current_version_id="v-1",
        ),
    )

    for download in (False, True):
        with pytest.raises(IdentityError) as error:
            service.citation(owner, completed.response_message_id, "c-1", download=download)
        assert error.value.status_code == 404
        assert error.value.code == "NOT_FOUND_OR_FORBIDDEN"


def test_expired_citation_is_denied_for_preview_and_download():
    result = QueryCompletion(
        AnswerState.ANSWERED,
        "answer",
        ({"citation_id": "c-expired", "tenant_id": "tenant-a", "document_id": "doc-1", "version_id": "v-1"},),
    )
    service, repository, _, _ = make_service(result=result)
    owner, conversation = authenticated_conversation(service, "user-a")
    submitted = service.submit(owner, conversation.conversation_id, "expired citation", idempotency_key="security-cite-expired-001")
    completed = service.status(owner, submitted.job_id)
    assert completed.response_message_id is not None
    repository.add_citation(
        completed.response_message_id,
        CitationArtifact(
            {**result.citations[0], "expires_at": (NOW - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")},
            preview="expired",
            download=b"expired",
            classification="PUBLIC",
            current_version_id="v-1",
        ),
    )

    for download in (False, True):
        with pytest.raises(IdentityError) as error:
            service.citation(owner, completed.response_message_id, "c-expired", download=download)
        assert error.value.status_code == 404
        assert error.value.code == "NOT_FOUND_OR_FORBIDDEN"


def test_feedback_answer_oracle_is_owner_bound_and_private():
    service, _, _, _ = make_service()
    owner, conversation = authenticated_conversation(service, "user-a")
    other, _ = authenticated_conversation(service, "user-b")
    submitted = service.submit(owner, conversation.conversation_id, "private answer", idempotency_key="security-feedback-001")
    completed = service.status(owner, submitted.job_id)
    assert completed.response_message_id is not None

    with pytest.raises(IdentityError) as error:
        service.feedback_target(other, completed.response_message_id)

    assert error.value.status_code == 404
    assert error.value.message == "The requested resource is unavailable."
    assert completed.response_message_id not in error.value.message


def test_oversized_untrusted_query_is_rejected_before_worker_execution():
    service, _, executor, _ = make_service()
    service.auto_process = False
    owner, conversation = authenticated_conversation(service, "user-a")

    with pytest.raises(IdentityError) as error:
        service.submit(owner, conversation.conversation_id, "x" * 4_001, idempotency_key="security-input-001")

    assert error.value.code == "REQUEST_INVALID"
    assert error.value.status_code == 400
    assert executor.requests == []
