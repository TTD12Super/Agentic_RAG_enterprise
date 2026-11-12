"""Provider-neutral chat, conversation and query-job boundary.

The repository protocols are the durable Core/worker seam.  The local adapter
uses the existing scoped conversation-memory implementation when no database
repository is configured.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import hashlib
import json
import secrets
from threading import RLock
from typing import Any, Protocol
from uuid import uuid4

from ..authorization import (
    Action,
    AnonymousPrincipal,
    AuthorizationDenied,
    AuthorizationEvaluator,
    ConversationResource,
    DocumentResource,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from ..cache import CacheScope, StaleScopeError
from ..identity.errors import IdentityError
from ..identity.models import AuthenticatedPrincipal
from ..memory import ConversationMessage, InMemoryConversationMemory
from ..orchestration import (
    OrchestrationOutcome,
    OrchestrationRequest,
    OrchestrationStatus,
)
from ..rag import AnswerCitation, AnswerResult, AnswerStatus


CHAT_SCHEMA_VERSION = "1.0"
ANONYMOUS_SESSION_COOKIE = "enterprise_rag_anonymous_session"
ANONYMOUS_SESSION_HEADER = "X-Anonymous-Session"
ANONYMOUS_SESSION_MAX_AGE = timedelta(hours=24)
ANONYMOUS_SESSION_IDLE = timedelta(minutes=30)
QUERY_TIMEOUT = timedelta(seconds=60)
DEFAULT_PUBLIC_TENANT = "public"


class JobState(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ActorKind(StrEnum):
    AUTHENTICATED = "AUTHENTICATED"
    ANONYMOUS = "ANONYMOUS"


class AnswerState(StrEnum):
    ANSWERED = "ANSWERED"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    ACCESS_DENIED = "ACCESS_DENIED"
    ERROR = "ERROR"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _fingerprint(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _citation_expired(artifact: CitationArtifact, *, now: datetime) -> bool:
    raw = artifact.citation.expires_at if isinstance(artifact.citation, AnswerCitation) else artifact.citation.get("expires_at")
    if raw is None:
        return False
    if isinstance(raw, str):
        try:
            raw = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return True
    return not isinstance(raw, datetime) or raw.tzinfo is None or raw <= now


def _error(
    code: str,
    message: str,
    *,
    status: int,
    retryable: bool = False,
) -> IdentityError:
    return IdentityError(code, status, message, retryable=retryable)


@dataclass(frozen=True, slots=True)
class AnonymousSession:
    session_id: str
    tenant_id: str
    token_hash: str
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class ChatActor:
    kind: ActorKind
    tenant_id: str
    actor_id: str
    principal: AuthenticatedPrincipal | AnonymousPrincipal
    scope: CacheScope
    session_token: str | None = None


@dataclass(frozen=True, slots=True)
class MessageRecord:
    message_id: str
    role: str
    created_at: datetime
    answer_id: str | None = None
    status: str | None = None
    citations: tuple[Mapping[str, Any], ...] = ()
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ConversationRecord:
    conversation_id: str
    tenant_id: str
    owner_kind: ActorKind
    owner_id: str
    scope: CacheScope
    created_at: datetime
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class ConversationView:
    record: ConversationRecord
    messages: tuple[tuple[MessageRecord, ConversationMessage], ...]


@dataclass(frozen=True, slots=True)
class ConversationSummary:
    """Metadata-only history row; message bodies never cross this boundary."""

    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


@dataclass(frozen=True, slots=True)
class JobCheckpoint:
    stage: str
    revision: int
    attempt_id: str
    tenant_id: str
    conversation_id: str
    policy_epoch: int
    query_hash: str
    workflow_deadline_at: datetime
    safe_metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class QueryCompletion:
    status: AnswerState
    answer: str = ""
    citations: tuple[Mapping[str, Any], ...] = ()
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "citations", tuple(dict(item) for item in self.citations))
        object.__setattr__(self, "reason_codes", tuple(self.reason_codes))


@dataclass(frozen=True, slots=True)
class QueryJob:
    job_id: str
    tenant_id: str
    conversation_id: str
    request_message_id: str
    request_message_index: int
    response_message_id: str | None
    state: JobState
    attempt: int
    attempt_id: str
    revision: int
    created_at: datetime
    workflow_deadline_at: datetime
    idempotency_key: str
    checkpoint: JobCheckpoint | None = None
    completion: QueryCompletion | None = None
    error_code: str | None = None
    maintenance_window_id: str | None = None


@dataclass(frozen=True, slots=True)
class CitationArtifact:
    """Source material held behind a fresh citation authorization check."""

    citation: AnswerCitation | Mapping[str, Any]
    preview: str | None = None
    download: bytes | None = None
    classification: str = "INTERNAL"
    status: str = "ACTIVE"
    version_status: str = "ACTIVE"
    current_version_id: str | None = None
    acl: tuple[Any, ...] = ()
    title: str | None = None
    filename: str | None = None
    mime_type: str | None = None
    location: Mapping[str, object] | None = None
    owner_department_id: str | None = None

    @property
    def citation_id(self) -> str:
        if isinstance(self.citation, AnswerCitation):
            return self.citation.citation_id
        value = self.citation.get("citation_id")
        return str(value) if value is not None else ""

    @property
    def tenant_id(self) -> str:
        if isinstance(self.citation, AnswerCitation):
            return self.citation.tenant_id
        return str(self.citation.get("tenant_id", ""))

    @property
    def document_id(self) -> str:
        if isinstance(self.citation, AnswerCitation):
            return self.citation.document_id
        return str(self.citation.get("document_id", ""))

    @property
    def version_id(self) -> str:
        if isinstance(self.citation, AnswerCitation):
            return self.citation.version_id
        return str(self.citation.get("version_id", ""))

    def as_dict(self) -> dict[str, Any]:
        payload = (
            self.citation.to_dict()
            if isinstance(self.citation, AnswerCitation)
            else dict(self.citation)
        )
        for name in ("title", "filename", "mime_type"):
            value = getattr(self, name)
            if value is not None:
                payload.setdefault(name, value)
        if self.location is not None:
            payload.setdefault("location", dict(self.location))
        return payload


class ConversationRepository(Protocol):
    def create_anonymous_session(self, tenant_id: str, *, now: datetime) -> tuple[str, AnonymousSession]: ...

    def resolve_anonymous_session(
        self, token: str, tenant_id: str, *, now: datetime
    ) -> AnonymousSession | None: ...

    def create_conversation(
        self,
        *,
        tenant_id: str,
        owner_kind: ActorKind,
        owner_id: str,
        scope: CacheScope,
        now: datetime,
        expires_at: datetime,
    ) -> ConversationRecord: ...

    def get_conversation(self, conversation_id: str, *, current_scope: CacheScope) -> ConversationView | None: ...

    def list_conversations(
        self,
        *,
        current_scope: CacheScope,
        limit: int,
        offset: int,
        search: str | None,
    ) -> tuple[tuple[ConversationSummary, ...], int]: ...

    def append_message(
        self,
        conversation_id: str,
        *,
        scope: CacheScope,
        role: str,
        content: str,
        now: datetime,
    ) -> MessageRecord: ...


class QueryJobRepository(Protocol):
    def create_job(
        self,
        *,
        tenant_id: str,
        conversation_id: str,
        request_message_id: str,
        request_message_index: int,
        idempotency_key: str,
        deadline: datetime,
        now: datetime,
    ) -> QueryJob: ...

    def get_job(self, job_id: str, *, current_scope: CacheScope) -> QueryJob | None: ...

    def claim_job(self, job_id: str, *, scope: CacheScope, now: datetime) -> QueryJob: ...

    def save_checkpoint(self, job_id: str, *, scope: CacheScope, checkpoint: JobCheckpoint) -> QueryJob: ...

    def pause_job(
        self, job_id: str, *, scope: CacheScope, maintenance_window_id: str, checkpoint: JobCheckpoint
    ) -> QueryJob: ...

    def complete_job(self, job_id: str, *, scope: CacheScope, completion: QueryCompletion) -> QueryJob: ...

    def fail_job(self, job_id: str, *, scope: CacheScope, error_code: str) -> QueryJob: ...

    def cancel_job(self, job_id: str, *, scope: CacheScope, error_code: str) -> QueryJob: ...


class CheckpointRepository(Protocol):
    def save_checkpoint(self, job_id: str, *, scope: CacheScope, checkpoint: JobCheckpoint) -> QueryJob: ...


class DurableChatRepository(ConversationRepository, QueryJobRepository, CheckpointRepository, Protocol):
    """PostgreSQL-backed implementations must provide this complete boundary."""

    def remember_submission(
        self, *, tenant_id: str, owner_id: str, conversation_id: str, key: str, fingerprint: str, job_id: str
    ) -> None: ...

    def find_submission(
        self, *, tenant_id: str, owner_id: str, conversation_id: str, key: str
    ) -> tuple[str, str] | None: ...

    def add_citation(self, answer_id: str, artifact: CitationArtifact) -> None: ...

    def get_citation(self, answer_id: str, citation_id: str, *, current_scope: CacheScope) -> CitationArtifact | None: ...

    def answer_job(self, answer_id: str, *, current_scope: CacheScope) -> QueryJob | None: ...

    def jobs_for_tenant(self, tenant_id: str, *, states: set[JobState]) -> tuple[QueryJob, ...]: ...


class InMemoryChatRepository:
    """Bounded local adapter used only when no durable DB adapter is configured."""

    def __init__(
        self,
        *,
        max_conversations: int = 10_000,
        max_jobs: int = 10_000,
        clock: Callable[[], datetime] = _now,
    ) -> None:
        self.memory = InMemoryConversationMemory()
        self._clock = clock
        self.max_conversations = max_conversations
        self.max_jobs = max_jobs
        self._sessions: dict[str, AnonymousSession] = {}
        self._conversations: dict[str, ConversationRecord] = {}
        self._message_meta: dict[str, list[MessageRecord]] = {}
        self._jobs: dict[str, QueryJob] = {}
        self._submissions: dict[tuple[str, str, str, str], tuple[str, str]] = {}
        self._citations: dict[tuple[str, str], CitationArtifact] = {}
        self._lock = RLock()

    def set_clock(self, clock: Callable[[], datetime]) -> None:
        """Keep the bounded adapter's expiry checks on the service clock."""

        self._clock = clock
        self.memory.set_clock(clock)

    def create_anonymous_session(self, tenant_id: str, *, now: datetime) -> tuple[str, AnonymousSession]:
        token = secrets.token_urlsafe(32)
        record = AnonymousSession(
            session_id=secrets.token_urlsafe(18),
            tenant_id=tenant_id,
            token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            created_at=now,
            last_seen_at=now,
            expires_at=now + ANONYMOUS_SESSION_MAX_AGE,
        )
        with self._lock:
            self._sessions[record.token_hash] = record
        return token, record

    def resolve_anonymous_session(self, token: str, tenant_id: str, *, now: datetime) -> AnonymousSession | None:
        if not token or len(token) > 4096 or any(char.isspace() for char in token):
            return None
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with self._lock:
            record = self._sessions.get(token_hash)
            if record is None or record.tenant_id != tenant_id:
                return None
            if now >= record.expires_at or now - record.last_seen_at > ANONYMOUS_SESSION_IDLE:
                return None
            updated = replace(record, last_seen_at=now)
            self._sessions[token_hash] = updated
            return updated

    def create_conversation(
        self,
        *,
        tenant_id: str,
        owner_kind: ActorKind,
        owner_id: str,
        scope: CacheScope,
        now: datetime,
        expires_at: datetime,
    ) -> ConversationRecord:
        with self._lock:
            if len(self._conversations) >= self.max_conversations:
                raise RuntimeError("conversation capacity reached")
            record = ConversationRecord(
                conversation_id=str(uuid4()),
                tenant_id=tenant_id,
                owner_kind=owner_kind,
                owner_id=owner_id,
                scope=scope,
                created_at=now,
                expires_at=expires_at,
            )
            self._conversations[record.conversation_id] = record
            self._message_meta[record.conversation_id] = []
            return record

    def get_conversation(self, conversation_id: str, *, current_scope: CacheScope) -> ConversationView | None:
        with self._lock:
            record = self._conversations.get(conversation_id)
            if record is None or record.scope != current_scope:
                return None
            if current_scope.principal_id.startswith("anonymous:") and self._clock() >= record.expires_at:
                return None
            memory = self.memory.read(current_scope, conversation_id, current_scope=current_scope)
            body = memory.messages if memory is not None else ()
            meta = tuple(self._message_meta.get(conversation_id, ()))
            if len(meta) != len(body):
                return None
            return ConversationView(record, tuple(zip(meta, body)))

    def list_conversations(
        self,
        *,
        current_scope: CacheScope,
        limit: int,
        offset: int,
        search: str | None,
    ) -> tuple[tuple[ConversationSummary, ...], int]:
        normalized_search = search.casefold().strip() if search else ""
        matches: list[ConversationSummary] = []
        with self._lock:
            for record in self._conversations.values():
                if record.scope != current_scope:
                    continue
                if current_scope.principal_id.startswith("anonymous:") and self._clock() >= record.expires_at:
                    continue
                view = self.get_conversation(record.conversation_id, current_scope=current_scope)
                if view is None:
                    continue
                user_message = next(
                    (message.content.strip() for _, message in view.messages if message.role == "user"),
                    "",
                )
                title = user_message[:96] or "New conversation"
                if normalized_search and normalized_search not in title.casefold():
                    continue
                updated_at = max(
                    (meta.created_at for meta, _ in view.messages),
                    default=record.created_at,
                )
                matches.append(
                    ConversationSummary(
                        conversation_id=record.conversation_id,
                        title=title,
                        created_at=record.created_at,
                        updated_at=updated_at,
                        message_count=len(view.messages),
                    )
                )
        matches.sort(key=lambda item: (item.updated_at, item.conversation_id), reverse=True)
        total = len(matches)
        return tuple(matches[offset : offset + limit]), total

    def append_message(
        self,
        conversation_id: str,
        *,
        scope: CacheScope,
        role: str,
        content: str,
        now: datetime,
    ) -> MessageRecord:
        if role not in {"user", "assistant"}:
            raise ValueError("message role is invalid")
        with self._lock:
            view = self.get_conversation(conversation_id, current_scope=scope)
            if view is None:
                raise StaleScopeError("conversation scope is stale")
            message = MessageRecord(str(uuid4()), role, now)
            self.memory.append(scope, conversation_id, ConversationMessage(role, content), now=now)
            self._message_meta[conversation_id].append(message)
            return message

    def create_job(
        self,
        *,
        tenant_id: str,
        conversation_id: str,
        request_message_id: str,
        request_message_index: int,
        idempotency_key: str,
        deadline: datetime,
        now: datetime,
    ) -> QueryJob:
        with self._lock:
            if len(self._jobs) >= self.max_jobs:
                raise RuntimeError("query-job capacity reached")
            job = QueryJob(
                job_id=str(uuid4()),
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                request_message_id=request_message_id,
                request_message_index=request_message_index,
                response_message_id=None,
                state=JobState.QUEUED,
                attempt=1,
                attempt_id=str(uuid4()),
                revision=0,
                created_at=now,
                workflow_deadline_at=deadline,
                idempotency_key=idempotency_key,
            )
            self._jobs[job.job_id] = job
            return job

    def get_job(self, job_id: str, *, current_scope: CacheScope) -> QueryJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            return job if self.get_conversation(job.conversation_id, current_scope=current_scope) else None

    def claim_job(self, job_id: str, *, scope: CacheScope, now: datetime) -> QueryJob:
        with self._lock:
            job = self.get_job(job_id, current_scope=scope)
            if job is None:
                raise StaleScopeError("job scope is stale")
            if job.state not in {JobState.QUEUED, JobState.PAUSED}:
                return job
            claimed = replace(
                job,
                state=JobState.RUNNING,
                attempt_id=str(uuid4()) if job.state is JobState.PAUSED else job.attempt_id,
                revision=job.revision + 1,
                maintenance_window_id=None,
            )
            self._jobs[job_id] = claimed
            return claimed

    def save_checkpoint(self, job_id: str, *, scope: CacheScope, checkpoint: JobCheckpoint) -> QueryJob:
        with self._lock:
            job = self.get_job(job_id, current_scope=scope)
            if job is None or checkpoint.revision != job.revision:
                raise StaleScopeError("stale checkpoint")
            updated = replace(job, checkpoint=checkpoint, revision=job.revision + 1)
            self._jobs[job_id] = updated
            return updated

    def pause_job(
        self, job_id: str, *, scope: CacheScope, maintenance_window_id: str, checkpoint: JobCheckpoint
    ) -> QueryJob:
        with self._lock:
            job = self.get_job(job_id, current_scope=scope)
            if job is None or job.state is not JobState.RUNNING:
                raise StaleScopeError("job is not pausable")
            paused = replace(
                job,
                state=JobState.PAUSED,
                checkpoint=checkpoint,
                revision=job.revision + 1,
                maintenance_window_id=maintenance_window_id,
            )
            self._jobs[job_id] = paused
            return paused

    def complete_job(self, job_id: str, *, scope: CacheScope, completion: QueryCompletion) -> QueryJob:
        with self._lock:
            job = self.get_job(job_id, current_scope=scope)
            if job is None:
                raise StaleScopeError("job scope is stale")
            if job.state is JobState.COMPLETED:
                return job
            if job.state is not JobState.RUNNING:
                raise StaleScopeError("job completion is stale")
            response_id = str(uuid4())
            self.memory.append(
                scope,
                job.conversation_id,
                ConversationMessage("assistant", completion.answer or "Insufficient evidence to answer this question."),
            )
            self._message_meta[job.conversation_id].append(
                MessageRecord(
                    response_id,
                    "assistant",
                    _now(),
                    answer_id=response_id,
                    status=completion.status.value,
                    citations=completion.citations,
                    reason_codes=completion.reason_codes,
                )
            )
            completed = replace(
                job,
                response_message_id=response_id,
                state=JobState.COMPLETED,
                revision=job.revision + 1,
                completion=completion,
            )
            self._jobs[job_id] = completed
            for citation in completion.citations:
                citation_id = str(citation.get("citation_id", ""))
                if citation_id:
                    self._citations[(response_id, citation_id)] = CitationArtifact(citation)
            return completed

    def fail_job(self, job_id: str, *, scope: CacheScope, error_code: str) -> QueryJob:
        with self._lock:
            job = self.get_job(job_id, current_scope=scope)
            if job is None:
                raise StaleScopeError("job scope is stale")
            if job.state in {JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED}:
                return job
            failed = replace(job, state=JobState.FAILED, revision=job.revision + 1, error_code=error_code)
            self._jobs[job_id] = failed
            return failed

    def cancel_job(self, job_id: str, *, scope: CacheScope, error_code: str) -> QueryJob:
        with self._lock:
            job = self.get_job(job_id, current_scope=scope)
            if job is None:
                raise StaleScopeError("job scope is stale")
            if job.state in {JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED}:
                return job
            cancelled = replace(
                job,
                state=JobState.CANCELLED,
                revision=job.revision + 1,
                error_code=error_code,
            )
            self._jobs[job_id] = cancelled
            return cancelled

    def remember_submission(
        self, *, tenant_id: str, owner_id: str, conversation_id: str, key: str, fingerprint: str, job_id: str
    ) -> None:
        with self._lock:
            self._submissions[(tenant_id, owner_id, conversation_id, key)] = (fingerprint, job_id)

    def find_submission(
        self, *, tenant_id: str, owner_id: str, conversation_id: str, key: str
    ) -> tuple[str, str] | None:
        with self._lock:
            return self._submissions.get((tenant_id, owner_id, conversation_id, key))

    def add_citation(self, answer_id: str, artifact: CitationArtifact) -> None:
        with self._lock:
            self._citations[(answer_id, artifact.citation_id)] = artifact

    def answer_job(self, answer_id: str, *, current_scope: CacheScope) -> QueryJob | None:
        with self._lock:
            for job in self._jobs.values():
                if answer_id in {job.job_id, job.response_message_id}:
                    return self.get_job(job.job_id, current_scope=current_scope)
            return None

    def get_citation(self, answer_id: str, citation_id: str, *, current_scope: CacheScope) -> CitationArtifact | None:
        job = self.answer_job(answer_id, current_scope=current_scope)
        if job is None or job.response_message_id is None:
            return None
        with self._lock:
            return self._citations.get((job.response_message_id, citation_id))

    def jobs_for_tenant(self, tenant_id: str, *, states: set[JobState]) -> tuple[QueryJob, ...]:
        with self._lock:
            return tuple(job for job in self._jobs.values() if job.tenant_id == tenant_id and job.state in states)

    def request_query(self, job: QueryJob, *, scope: CacheScope) -> str | None:
        view = self.get_conversation(job.conversation_id, current_scope=scope)
        if view is None or job.request_message_index >= len(view.messages):
            return None
        message = view.messages[job.request_message_index][1]
        return message.content if message.role == "user" else None


class QueryExecutor(Protocol):
    def run(self, request: OrchestrationRequest) -> object: ...


class NoopQueryExecutor:
    """Safe local result when no retrieval/model worker is configured."""

    def run(self, request: OrchestrationRequest) -> OrchestrationOutcome:
        return OrchestrationOutcome(
            status=OrchestrationStatus.INSUFFICIENT_EVIDENCE,
            reason_codes=("NO_PROVIDER_CONFIGURED",),
        )


class ChatService:
    def __init__(
        self,
        *,
        repository: DurableChatRepository | None = None,
        executor: QueryExecutor | None = None,
        pep: PolicyEnforcementPoint | None = None,
        policy_store: InMemoryPolicyStore | None = None,
        tenant_id: str = DEFAULT_PUBLIC_TENANT,
        clock: Callable[[], datetime] = _now,
        maintenance_probe: Callable[[str], str | None] | None = None,
        document_state_provider: Callable[[CitationArtifact], CitationArtifact | None] | None = None,
    ) -> None:
        self.repository = repository or InMemoryChatRepository()
        self.executor = executor or NoopQueryExecutor()
        self.policy_store = policy_store or InMemoryPolicyStore(policy_epoch=1)
        self.pep = pep or PolicyEnforcementPoint(self._evaluator())
        self.tenant_id = tenant_id
        self.clock = clock
        set_clock = getattr(self.repository, "set_clock", None)
        if callable(set_clock):
            set_clock(clock)
        self.maintenance_probe = maintenance_probe or (lambda tenant: None)
        self.document_state_provider = document_state_provider or (lambda artifact: artifact)
        self.auto_process = True

    def set_authorization(self, policy_store: InMemoryPolicyStore, pep: PolicyEnforcementPoint) -> None:
        self.policy_store = policy_store
        self.pep = pep

    def _evaluator(self):
        return AuthorizationEvaluator(self.policy_store)

    def _scope(self, tenant_id: str, principal_id: str) -> CacheScope:
        try:
            epoch = self.policy_store.current_policy_epoch()
        except Exception as exc:
            raise _error("AUTH_UNAVAILABLE", "Authorization is temporarily unavailable.", status=503, retryable=True) from exc
        return CacheScope(tenant_id, principal_id, epoch, None)

    def actor_for_create(
        self, principal: AuthenticatedPrincipal | None, token: str | None
    ) -> tuple[ChatActor, bool]:
        now = self.clock()
        if principal is not None:
            return (
                ChatActor(
                    ActorKind.AUTHENTICATED,
                    principal.tenant_id,
                    principal.user_id,
                    principal,
                    self._scope(principal.tenant_id, principal.user_id),
                ),
                False,
            )
        if token:
            session = self.repository.resolve_anonymous_session(token, self.tenant_id, now=now)
            if session is not None:
                return self._anonymous_actor(session, token), False
            # Creating a new conversation cannot expose an old conversation; recover
            # from an expired in-memory demo cookie while existing-resource reads remain deny-by-default.
            raw, session = self.repository.create_anonymous_session(self.tenant_id, now=now)
            return self._anonymous_actor(session, raw), True
        raw, session = self.repository.create_anonymous_session(self.tenant_id, now=now)
        return self._anonymous_actor(session, raw), True

    def actor_for_existing(
        self, principal: AuthenticatedPrincipal | None, token: str | None
    ) -> ChatActor:
        if principal is not None:
            return ChatActor(
                ActorKind.AUTHENTICATED,
                principal.tenant_id,
                principal.user_id,
                principal,
                self._scope(principal.tenant_id, principal.user_id),
            )
        if not token:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        session = self.repository.resolve_anonymous_session(token, self.tenant_id, now=self.clock())
        if session is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        return self._anonymous_actor(session, token)

    def _anonymous_actor(self, session: AnonymousSession, token: str) -> ChatActor:
        principal = AnonymousPrincipal(session.tenant_id, session.session_id)
        return ChatActor(
            ActorKind.ANONYMOUS,
            session.tenant_id,
            f"anonymous:{session.session_id}",
            principal,
            self._scope(session.tenant_id, f"anonymous:{session.session_id}"),
            token,
        )

    def create_conversation(self, actor: ChatActor) -> ConversationRecord:
        if self.maintenance_probe(actor.tenant_id):
            raise _error("MAINTENANCE_ACTIVE", "Chat is temporarily unavailable for maintenance.", status=503, retryable=True)
        now = self.clock()
        expires = now + timedelta(days=180) if actor.kind is ActorKind.AUTHENTICATED else now + timedelta(days=7)
        return self.repository.create_conversation(
            tenant_id=actor.tenant_id,
            owner_kind=actor.kind,
            owner_id=actor.actor_id,
            scope=actor.scope,
            now=now,
            expires_at=expires,
        )

    def _authorize_conversation(self, actor: ChatActor, conversation: ConversationRecord) -> None:
        if conversation.tenant_id != actor.tenant_id or conversation.owner_kind is not actor.kind or conversation.owner_id != actor.actor_id:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        if actor.kind is ActorKind.AUTHENTICATED:
            resource = ConversationResource(
                conversation.conversation_id,
                conversation.tenant_id,
                conversation.owner_id,
                policy_epoch=actor.scope.policy_epoch,
            )
            try:
                self.pep.enforce(actor.principal, Action.CONVERSATION_READ, resource)
            except AuthorizationDenied as exc:
                if exc.decision.reason_code == "POLICY_UNAVAILABLE":
                    raise _error("AUTH_UNAVAILABLE", "Authorization is temporarily unavailable.", status=503, retryable=True) from exc
                raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404) from exc

    def conversation(self, actor: ChatActor, conversation_id: str) -> ConversationView:
        view = self.repository.get_conversation(conversation_id, current_scope=actor.scope)
        if view is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        self._authorize_conversation(actor, view.record)
        return view

    def list_conversations(
        self,
        actor: ChatActor,
        *,
        limit: int,
        offset: int,
        search: str | None,
    ) -> tuple[tuple[ConversationSummary, ...], int]:
        rows, total = self.repository.list_conversations(
            current_scope=actor.scope,
            limit=limit,
            offset=offset,
            search=search,
        )
        if actor.kind is ActorKind.ANONYMOUS:
            return rows, total

        # The repository scopes by owner, while the PDP still owns the final
        # conversation-read decision. Denied rows are omitted without leaking
        # their existence; policy outages remain errors from the PEP.
        if not rows:
            return rows, total
        first = rows[0]
        record = ConversationRecord(
            conversation_id=first.conversation_id,
            tenant_id=actor.tenant_id,
            owner_kind=ActorKind.AUTHENTICATED,
            owner_id=actor.actor_id,
            scope=actor.scope,
            created_at=first.created_at,
            expires_at=first.updated_at,
        )
        try:
            self._authorize_conversation(actor, record)
        except IdentityError as error:
            if error.code == "AUTH_UNAVAILABLE":
                raise
            return (), 0
        return rows, total

    def submit(
        self,
        actor: ChatActor,
        conversation_id: str,
        query: str,
        *,
        idempotency_key: str | None,
    ) -> QueryJob:
        if self.maintenance_probe(actor.tenant_id):
            raise _error("MAINTENANCE_ACTIVE", "Chat is temporarily unavailable for maintenance.", status=503, retryable=True)
        if not idempotency_key or len(idempotency_key.strip()) < 16:
            raise _error("IDEMPOTENCY_REQUIRED", "An idempotency key is required.", status=400)
        if not isinstance(query, str) or not query.strip() or len(query) > 4_000:
            raise _error("REQUEST_INVALID", "The request is invalid.", status=400)
        view = self.conversation(actor, conversation_id)
        key = idempotency_key.strip()
        fingerprint = _fingerprint({"conversation_id": conversation_id, "query": query.strip()})
        existing = self.repository.find_submission(
            tenant_id=actor.tenant_id,
            owner_id=actor.actor_id,
            conversation_id=conversation_id,
            key=key,
        )
        if existing is not None:
            if existing[0] != fingerprint:
                raise _error("IDEMPOTENCY_KEY_REUSED", "The idempotency key was already used.", status=409)
            job = self.repository.get_job(existing[1], current_scope=actor.scope)
            if job is not None:
                return job
            raise _error("SCOPE_STALE", "The request scope is no longer current.", status=409)
        message = self.repository.append_message(
            conversation_id,
            scope=actor.scope,
            role="user",
            content=query.strip(),
            now=self.clock(),
        )
        job = self.repository.create_job(
            tenant_id=actor.tenant_id,
            conversation_id=conversation_id,
            request_message_id=message.message_id,
            request_message_index=len(view.messages),
            idempotency_key=key,
            deadline=self.clock() + QUERY_TIMEOUT,
            now=self.clock(),
        )
        self.repository.remember_submission(
            tenant_id=actor.tenant_id,
            owner_id=actor.actor_id,
            conversation_id=conversation_id,
            key=key,
            fingerprint=fingerprint,
            job_id=job.job_id,
        )
        return job

    def status(self, actor: ChatActor, job_id: str) -> QueryJob:
        job = self._job_for_actor(actor, job_id)
        if self.auto_process and job.state in {JobState.QUEUED, JobState.PAUSED} and not self.maintenance_probe(actor.tenant_id):
            return self.process(actor, job_id)
        return job

    def _job_for_actor(self, actor: ChatActor, job_id: str) -> QueryJob:
        job = self.repository.get_job(job_id, current_scope=actor.scope)
        if job is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        view = self.repository.get_conversation(job.conversation_id, current_scope=actor.scope)
        if view is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        self._authorize_conversation(actor, view.record)
        return job

    def process(self, actor: ChatActor, job_id: str) -> QueryJob:
        job = self._job_for_actor(actor, job_id)
        if job.state in {JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED}:
            return job
        if self.maintenance_probe(actor.tenant_id):
            return job
        if self.clock() >= job.workflow_deadline_at:
            return self.repository.fail_job(job_id, scope=actor.scope, error_code="TIMEOUT")
        running = self.repository.claim_job(job_id, scope=actor.scope, now=self.clock())
        query = self.repository.request_query(running, scope=actor.scope)
        if query is None:
            return self.repository.fail_job(job_id, scope=actor.scope, error_code="REQUEST_UNAVAILABLE")
        checkpoint = JobCheckpoint(
            stage="RUNNING",
            revision=running.revision,
            attempt_id=running.attempt_id,
            tenant_id=actor.tenant_id,
            conversation_id=running.conversation_id,
            policy_epoch=actor.scope.policy_epoch,
            query_hash=_fingerprint(query),
            workflow_deadline_at=running.workflow_deadline_at,
        )
        try:
            self.repository.save_checkpoint(job_id, scope=actor.scope, checkpoint=checkpoint)
            request = OrchestrationRequest(
                query=query,
                principal_ref=actor.actor_id,
                authorized_scope_ref=_fingerprint(actor.scope.key_prefix()),
                job_id=running.job_id,
                attempt_id=running.attempt_id,
                traceparent="00-" + secrets.token_hex(16) + "-" + secrets.token_hex(8) + "-01",
                deadline_at=running.workflow_deadline_at,
            )
            bind_context = getattr(self.executor, "bind_context", None)
            if callable(bind_context):
                bind_context(request.principal_ref, actor.principal, actor.scope.policy_epoch)
            raw = self.executor.run(request)
        except TimeoutError:
            return self.repository.fail_job(job_id, scope=actor.scope, error_code="TIMEOUT")
        except Exception:
            return self.repository.fail_job(job_id, scope=actor.scope, error_code="QUERY_FAILED")
        if self.maintenance_probe(actor.tenant_id):
            window_id = self.maintenance_probe(actor.tenant_id) or "maintenance"
            return self.repository.pause_job(
                job_id,
                scope=actor.scope,
                maintenance_window_id=window_id,
                checkpoint=replace(checkpoint, revision=running.revision + 1, stage="PAUSED"),
            )
        # A policy/tenant change during work cannot deliver the old result.
        fresh_scope = self._scope(actor.tenant_id, actor.actor_id)
        if fresh_scope != actor.scope:
            return self.repository.fail_job(job_id, scope=actor.scope, error_code="SCOPE_STALE")
        completion = self._completion(raw)
        if completion.status is AnswerState.ERROR:
            return self.repository.fail_job(job_id, scope=actor.scope, error_code=completion.reason_codes[0] if completion.reason_codes else "QUERY_FAILED")
        return self.repository.complete_job(job_id, scope=actor.scope, completion=completion)

    def stream(
        self,
        actor: ChatActor,
        job_id: str,
        *,
        should_cancel: Callable[[], bool] | None = None,
    ) -> Iterator[tuple[str, dict[str, Any]]]:
        """Run a queued job through an executor's streaming seam and persist it."""

        job = self._job_for_actor(actor, job_id)
        yield (
            "message_start",
            {"job_id": job.job_id, "conversation_id": job.conversation_id},
        )
        if job.state is JobState.COMPLETED:
            yield ("done", job_payload(job))
            return
        if job.state in {JobState.FAILED, JobState.CANCELLED}:
            yield ("error", {"code": job.error_code or "QUERY_FAILED"})
            return
        if self.maintenance_probe(actor.tenant_id):
            yield ("error", {"code": "MAINTENANCE_ACTIVE"})
            return
        if self.clock() >= job.workflow_deadline_at:
            failed = self.repository.fail_job(job_id, scope=actor.scope, error_code="TIMEOUT")
            yield ("error", {"code": failed.error_code or "TIMEOUT"})
            return

        try:
            running = self.repository.claim_job(job_id, scope=actor.scope, now=self.clock())
            query = self.repository.request_query(running, scope=actor.scope)
            if query is None:
                failed = self.repository.fail_job(job_id, scope=actor.scope, error_code="REQUEST_UNAVAILABLE")
                yield ("error", {"code": failed.error_code or "REQUEST_UNAVAILABLE"})
                return
            checkpoint = JobCheckpoint(
                stage="RUNNING",
                revision=running.revision,
                attempt_id=running.attempt_id,
                tenant_id=actor.tenant_id,
                conversation_id=running.conversation_id,
                policy_epoch=actor.scope.policy_epoch,
                query_hash=_fingerprint(query),
                workflow_deadline_at=running.workflow_deadline_at,
            )
            self.repository.save_checkpoint(job_id, scope=actor.scope, checkpoint=checkpoint)
            request = OrchestrationRequest(
                query=query,
                principal_ref=actor.actor_id,
                authorized_scope_ref=_fingerprint(actor.scope.key_prefix()),
                job_id=running.job_id,
                attempt_id=running.attempt_id,
                traceparent="00-" + secrets.token_hex(16) + "-" + secrets.token_hex(8) + "-01",
                deadline_at=running.workflow_deadline_at,
            )
            bind_context = getattr(self.executor, "bind_context", None)
            if callable(bind_context):
                bind_context(request.principal_ref, actor.principal, actor.scope.policy_epoch)
            stream_executor = getattr(self.executor, "stream", None)
            if not callable(stream_executor):
                raise RuntimeError("streaming executor is unavailable")
            completion: QueryCompletion | None = None
            for raw in stream_executor(request):
                if should_cancel is not None and should_cancel():
                    self.repository.cancel_job(
                        job_id, scope=actor.scope, error_code="CLIENT_DISCONNECTED"
                    )
                    return
                if not isinstance(raw, Mapping):
                    continue
                event = str(raw.get("event", ""))
                data = raw.get("data")
                if not isinstance(data, Mapping):
                    continue
                if event in {"token", "citation"}:
                    yield (event, dict(data))
                elif event == "error":
                    code = str(data.get("code", "QUERY_FAILED"))
                    failed = self.repository.fail_job(job_id, scope=actor.scope, error_code=code)
                    yield ("error", {"code": failed.error_code or "QUERY_FAILED"})
                    return
                elif event == "complete":
                    if should_cancel is not None and should_cancel():
                        self.repository.cancel_job(
                            job_id, scope=actor.scope, error_code="CLIENT_DISCONNECTED"
                        )
                        return
                    try:
                        completion = QueryCompletion(
                            AnswerState(str(data.get("status", "ERROR"))),
                            str(data.get("answer", "")),
                            tuple(item for item in data.get("citations", ()) if isinstance(item, Mapping)),
                            tuple(str(item) for item in data.get("reason_codes", ())),
                        )
                    except (TypeError, ValueError):
                        completion = QueryCompletion(AnswerState.ERROR, reason_codes=("INVALID_QUERY_RESULT",))
            if completion is None:
                failed = self.repository.fail_job(job_id, scope=actor.scope, error_code="QUERY_FAILED")
                yield ("error", {"code": failed.error_code or "QUERY_FAILED"})
                return
            if completion.status is AnswerState.ERROR:
                failed = self.repository.fail_job(
                    job_id,
                    scope=actor.scope,
                    error_code=completion.reason_codes[0] if completion.reason_codes else "QUERY_FAILED",
                )
                yield ("error", {"code": failed.error_code or "QUERY_FAILED"})
                return
            if should_cancel is not None and should_cancel():
                self.repository.cancel_job(
                    job_id, scope=actor.scope, error_code="CLIENT_DISCONNECTED"
                )
                return
            fresh_scope = self._scope(actor.tenant_id, actor.actor_id)
            if fresh_scope != actor.scope:
                failed = self.repository.fail_job(job_id, scope=actor.scope, error_code="SCOPE_STALE")
                yield ("error", {"code": failed.error_code or "SCOPE_STALE"})
                return
            completed = self.repository.complete_job(job_id, scope=actor.scope, completion=completion)
            yield ("done", job_payload(completed))
        except TimeoutError:
            failed = self.repository.fail_job(job_id, scope=actor.scope, error_code="TIMEOUT")
            yield ("error", {"code": failed.error_code or "TIMEOUT"})
        except Exception:
            try:
                failed = self.repository.fail_job(job_id, scope=actor.scope, error_code="QUERY_FAILED")
                code = failed.error_code or "QUERY_FAILED"
            except Exception:
                code = "QUERY_FAILED"
            yield ("error", {"code": code})

    def cancel(self, actor: ChatActor, job_id: str, *, error_code: str = "CLIENT_DISCONNECTED") -> QueryJob:
        """Cancel an in-flight stream without creating an assistant message."""

        self._job_for_actor(actor, job_id)
        return self.repository.cancel_job(job_id, scope=actor.scope, error_code=error_code)

    def pause_for_maintenance(self, tenant_id: str, window_id: str) -> tuple[QueryJob, ...]:
        paused: list[QueryJob] = []
        for job in self.repository.jobs_for_tenant(tenant_id, states={JobState.RUNNING}):
            scope = self._scope(tenant_id, self._owner_id(job))
            checkpoint = JobCheckpoint(
                stage="PAUSED",
                revision=job.revision,
                attempt_id=job.attempt_id,
                tenant_id=tenant_id,
                conversation_id=job.conversation_id,
                policy_epoch=scope.policy_epoch,
                query_hash="",
                workflow_deadline_at=job.workflow_deadline_at,
            )
            try:
                paused.append(self.repository.pause_job(job.job_id, scope=scope, maintenance_window_id=window_id, checkpoint=checkpoint))
            except StaleScopeError:
                continue
        return tuple(paused)

    def _owner_id(self, job: QueryJob) -> str:
        repository = self.repository
        record = getattr(repository, "_conversations", {}).get(job.conversation_id)
        return record.owner_id if record is not None else "unknown"

    def citation(self, actor: ChatActor, answer_id: str, citation_id: str, *, download: bool) -> CitationArtifact:
        job = self.repository.answer_job(answer_id, current_scope=actor.scope)
        if job is None or job.completion is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        view = self.repository.get_conversation(job.conversation_id, current_scope=actor.scope)
        if view is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        self._authorize_conversation(actor, view.record)
        artifact = self.repository.get_citation(answer_id, citation_id, current_scope=actor.scope)
        if artifact is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        artifact = self.document_state_provider(artifact)
        if artifact is None or _citation_expired(artifact, now=self.clock()):
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        action = Action.SOURCE_DOWNLOAD if download else Action.DOCUMENT_READ
        resource = DocumentResource(
            document_id=artifact.document_id,
            tenant_id=artifact.tenant_id,
            classification=artifact.classification,
            status=artifact.status,
            current_version_id=artifact.current_version_id or artifact.version_id,
            version_id=artifact.version_id,
            version_status=artifact.version_status,
                owner_department_id=artifact.owner_department_id,
            acl=tuple(artifact.acl),
            policy_epoch=None,
        )
        try:
            self.pep.enforce(actor.principal, action, resource)
        except AuthorizationDenied as exc:
            if exc.decision.reason_code == "POLICY_UNAVAILABLE":
                raise _error("AUTH_UNAVAILABLE", "Authorization is temporarily unavailable.", status=503, retryable=True) from exc
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404) from exc
        if download and artifact.download is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        if not download and artifact.preview is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        return artifact

    def feedback_target(self, actor: ChatActor, answer_id: str) -> QueryJob:
        job = self.repository.answer_job(answer_id, current_scope=actor.scope)
        if job is None or job.completion is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        view = self.repository.get_conversation(job.conversation_id, current_scope=actor.scope)
        if view is None:
            raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404)
        self._authorize_conversation(actor, view.record)
        if actor.kind is ActorKind.AUTHENTICATED:
            try:
                self.pep.enforce(actor.principal, Action.FEEDBACK_CREATE)
            except AuthorizationDenied as exc:
                raise _error("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status=404) from exc
        return job

    @staticmethod
    def _completion(raw: object) -> QueryCompletion:
        if isinstance(raw, QueryCompletion):
            return raw
        if isinstance(raw, AnswerResult):
            return QueryCompletion(
                AnswerState(raw.status.value),
                raw.answer,
                tuple(citation.to_dict() for citation in raw.citations),
                raw.reason_codes,
            )
        if isinstance(raw, OrchestrationOutcome):
            mapping = {
                OrchestrationStatus.SUPPORTED: AnswerState.ANSWERED,
                OrchestrationStatus.PARTIAL: AnswerState.PARTIAL,
                OrchestrationStatus.INSUFFICIENT_EVIDENCE: AnswerState.INSUFFICIENT_EVIDENCE,
                OrchestrationStatus.ERROR: AnswerState.ERROR,
            }
            return QueryCompletion(mapping[raw.status], raw.answer, raw.citations, raw.reason_codes)
        if isinstance(raw, Mapping):
            try:
                return QueryCompletion(
                    AnswerState(str(raw.get("status", "ERROR"))),
                    str(raw.get("answer", "")),
                    tuple(item for item in raw.get("citations", ()) if isinstance(item, Mapping)),
                    tuple(str(item) for item in raw.get("reason_codes", ())),
                )
            except (TypeError, ValueError):
                pass
        return QueryCompletion(AnswerState.ERROR, reason_codes=("INVALID_QUERY_RESULT",))


def job_payload(job: QueryJob, *, maintenance: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": CHAT_SCHEMA_VERSION,
        "job_id": job.job_id,
        "conversation_id": job.conversation_id,
        "state": job.state.value,
        "attempt": job.attempt,
        "revision": job.revision,
        "workflow_deadline_at": _utc_z(job.workflow_deadline_at),
        "maintenance": maintenance,
    }
    if job.completion is not None:
        payload["answer"] = {
            "answer_id": job.response_message_id,
            "status": job.completion.status.value,
            "text": job.completion.answer or "Insufficient evidence to answer this question.",
            "citations": [dict(item) for item in job.completion.citations],
            "reason_codes": list(job.completion.reason_codes),
        }
    if job.error_code is not None:
        payload["error"] = {"code": job.error_code}
    return payload


__all__ = [
    "ActorKind",
    "ANONYMOUS_SESSION_COOKIE",
    "ANONYMOUS_SESSION_HEADER",
    "AnswerState",
    "ChatActor",
    "ChatService",
    "CitationArtifact",
    "ConversationRecord",
    "ConversationRepository",
    "ConversationView",
    "DurableChatRepository",
    "InMemoryChatRepository",
    "JobCheckpoint",
    "JobState",
    "QueryCompletion",
    "QueryJob",
    "QueryJobRepository",
    "CheckpointRepository",
    "job_payload",
]
