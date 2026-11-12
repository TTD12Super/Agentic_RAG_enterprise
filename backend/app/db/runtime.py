"""Small PostgreSQL runtime adapters for the API boundary.

The migration schema is authoritative. This module persists the runtime
repositories that have complete contracts; identity credentials use the
separate PostgreSQL identity adapter and document lifecycle remains behind
its existing in-memory adapter until its worker/storage fields are durable.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import re
from typing import Iterator
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from ..cache import CacheScope, StaleScopeError
from ..core.chat import (
    ANONYMOUS_SESSION_IDLE,
    ANONYMOUS_SESSION_MAX_AGE,
    ActorKind,
    AnonymousSession,
    CitationArtifact,
    ConversationMessage,
    ConversationRecord,
    ConversationSummary,
    ConversationView,
    JobCheckpoint,
    JobState,
    MessageRecord,
    QueryCompletion,
    QueryJob,
    AnswerState,
    _utc_z,
)
from ..identity.errors import IdentityError


RUNTIME_NAMESPACE = UUID("7e0b38b7-9bd4-4c7a-9be4-dc3f4e2e0a17")
_SLUG_SAFE = re.compile(r"[^a-z0-9-]+")


class RuntimeDatabaseUnavailable(IdentityError):
    """Safe public error raised when the configured database cannot serve a request."""

    def __init__(self) -> None:
        super().__init__(
            code="DATABASE_UNAVAILABLE",
            status_code=503,
            message="The data service is temporarily unavailable.",
            retryable=True,
            retry_after=5,
        )


def normalize_database_url(value: str) -> str:
    """Accept Neon/SQLAlchemy URLs while giving psycopg a native URL."""

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1].strip()
    if value.startswith("postgresql+psycopg://"):
        return "postgresql://" + value.removeprefix("postgresql+psycopg://")
    if value.startswith("postgres://"):
        return "postgresql://" + value.removeprefix("postgres://")
    return value


def stable_uuid(kind: str, value: str) -> UUID:
    return uuid5(RUNTIME_NAMESPACE, f"{kind}:{value}")


def tenant_uuid(tenant_id: str) -> UUID:
    try:
        return UUID(tenant_id)
    except ValueError:
        return stable_uuid("tenant", tenant_id)


def user_uuid(user_id: str) -> UUID:
    try:
        return UUID(user_id)
    except ValueError:
        return stable_uuid("user", user_id)


def _membership_uuid(tenant_id: str, user_id: str) -> UUID:
    return stable_uuid("membership", f"{tenant_id}:{user_id}")


def _department_uuid(tenant_id: str, department_id: str) -> UUID:
    try:
        return UUID(department_id)
    except ValueError:
        return stable_uuid("department", f"{tenant_id}:{department_id}")


def _tenant_slug(tenant_id: str) -> str:
    slug = _SLUG_SAFE.sub("-", tenant_id.strip().lower()).strip("-")
    return (slug or "tenant")[:120]


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _parse_uuid(value: str) -> UUID | None:
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        return None


def _answer_status(value: object) -> AnswerState:
    try:
        return AnswerState(str(value))
    except ValueError:
        return AnswerState.ANSWERED


def _jsonb(value: object) -> object:
    """Mark JSON values explicitly for psycopg instead of implicit adaptation."""

    from psycopg.types.json import Jsonb

    return Jsonb(value)


class _PostgresAdapter:
    def __init__(self, database_url: str) -> None:
        if not database_url.strip():
            raise ValueError("database_url must not be empty")
        self.database_url = normalize_database_url(database_url)

    @contextmanager
    def connection(self) -> Iterator[object]:
        try:
            import psycopg
            from psycopg.rows import dict_row

            with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
                yield connection
        except RuntimeDatabaseUnavailable:
            raise
        except Exception as error:
            raise RuntimeDatabaseUnavailable() from error

    @staticmethod
    def ensure_tenant(cursor: object, tenant_id: str) -> UUID:
        tenant_id_uuid = tenant_uuid(tenant_id)
        cursor.execute(
            """
            INSERT INTO tenants (id, slug, name)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (tenant_id_uuid, _tenant_slug(tenant_id), tenant_id[:160] or "Tenant"),
        )
        return tenant_id_uuid

    @staticmethod
    def ensure_user_scope(cursor: object, tenant_id: str, app_user_id: str) -> tuple[UUID, UUID]:
        tenant_id_uuid = _PostgresAdapter.ensure_tenant(cursor, tenant_id)
        persisted_user_id = user_uuid(app_user_id)
        membership_id = _membership_uuid(tenant_id, app_user_id)
        synthetic_email = f"runtime-{persisted_user_id.hex}@invalid.local"
        cursor.execute(
            """
            INSERT INTO users (id, email, display_name, status)
            VALUES (%s, %s, %s, 'ACTIVE')
            ON CONFLICT (id) DO UPDATE SET status = 'ACTIVE', updated_at = now()
            """,
            (persisted_user_id, synthetic_email, app_user_id[:160] or "Runtime user"),
        )
        cursor.execute(
            """
            INSERT INTO tenant_memberships (id, tenant_id, user_id, status)
            VALUES (%s, %s, %s, 'ACTIVE')
            ON CONFLICT (tenant_id, id) DO UPDATE SET status = 'ACTIVE', revoked_at = NULL
            """,
            (membership_id, tenant_id_uuid, persisted_user_id),
        )
        cursor.execute(
            """
            INSERT INTO membership_roles (membership_id, role_id)
            VALUES (%s, '00000000-0000-0000-0000-000000000003')
            ON CONFLICT DO NOTHING
            """,
            (membership_id,),
        )
        return persisted_user_id, membership_id


class PostgresChatRepository(_PostgresAdapter):
    """Durable implementation of the existing chat repository protocol."""

    def create_anonymous_session(self, tenant_id: str, *, now: datetime) -> tuple[str, AnonymousSession]:
        token = __import__("secrets").token_urlsafe(32)
        now = _as_utc(now)
        session_id = uuid4()
        session = AnonymousSession(
            session_id=str(session_id),
            tenant_id=tenant_id,
            token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            created_at=now,
            last_seen_at=now,
            expires_at=now + ANONYMOUS_SESSION_MAX_AGE,
        )
        with self.connection() as connection:
            with connection.cursor() as cursor:
                tenant_id_uuid = self.ensure_tenant(cursor, tenant_id)
                cursor.execute(
                    """
                    INSERT INTO anonymous_sessions
                        (id, tenant_id, session_hash, created_at, last_seen_at, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (session_id, tenant_id_uuid, session.token_hash, now, now, session.expires_at),
                )
        return token, session

    def resolve_anonymous_session(self, token: str, tenant_id: str, *, now: datetime) -> AnonymousSession | None:
        if not token or len(token) > 4096 or any(char.isspace() for char in token):
            return None
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        now = _as_utc(now)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                tenant_id_uuid = tenant_uuid(tenant_id)
                cursor.execute(
                    """
                    SELECT id, created_at, last_seen_at, expires_at
                    FROM anonymous_sessions
                    WHERE tenant_id = %s AND session_hash = %s AND revoked_at IS NULL
                    """,
                    (tenant_id_uuid, token_hash),
                )
                row = cursor.fetchone()
                if row is None:
                    return None
                last_seen = _as_utc(row["last_seen_at"])
                expires_at = _as_utc(row["expires_at"])
                if now >= expires_at or now - last_seen > ANONYMOUS_SESSION_IDLE:
                    return None
                cursor.execute(
                    "UPDATE anonymous_sessions SET last_seen_at = %s WHERE id = %s",
                    (now, row["id"]),
                )
                return AnonymousSession(
                    session_id=str(row["id"]),
                    tenant_id=tenant_id,
                    token_hash=token_hash,
                    created_at=_as_utc(row["created_at"]),
                    last_seen_at=now,
                    expires_at=expires_at,
                )

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
        conversation_id = uuid4()
        now = _as_utc(now)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                tenant_id_uuid = self.ensure_tenant(cursor, tenant_id)
                if owner_kind is ActorKind.AUTHENTICATED:
                    persisted_user_id, _ = self.ensure_user_scope(cursor, tenant_id, owner_id)
                    anonymous_hash = None
                else:
                    persisted_user_id = None
                    cursor.execute(
                        "SELECT session_hash FROM anonymous_sessions WHERE id = %s AND tenant_id = %s",
                        (_parse_uuid(owner_id.removeprefix("anonymous:")), tenant_id_uuid),
                    )
                    session_row = cursor.fetchone()
                    if session_row is None:
                        raise StaleScopeError("anonymous session is unavailable")
                    anonymous_hash = session_row["session_hash"]
                cursor.execute(
                    """
                    INSERT INTO conversations
                        (id, tenant_id, user_id, anonymous_session_hash, created_at, last_activity_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (conversation_id, tenant_id_uuid, persisted_user_id, anonymous_hash, now, now),
                )
        return ConversationRecord(
            conversation_id=str(conversation_id),
            tenant_id=tenant_id,
            owner_kind=owner_kind,
            owner_id=owner_id,
            scope=scope,
            created_at=now,
            expires_at=_as_utc(expires_at),
        )

    def _conversation_row(self, cursor: object, conversation_id: str, scope: CacheScope) -> object | None:
        conversation_uuid = _parse_uuid(conversation_id)
        if conversation_uuid is None:
            return None
        tenant_id_uuid = tenant_uuid(scope.tenant_id)
        principal_id = scope.principal_id
        if principal_id.startswith("anonymous:"):
                cursor.execute(
                """
                    SELECT c.*, s.id AS anonymous_session_id FROM conversations c
                JOIN anonymous_sessions s
                  ON s.tenant_id = c.tenant_id AND s.session_hash = c.anonymous_session_hash
                WHERE c.id = %s AND c.tenant_id = %s AND s.id = %s
                """,
                (conversation_uuid, tenant_id_uuid, _parse_uuid(principal_id.removeprefix("anonymous:"))),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM conversations
                WHERE id = %s AND tenant_id = %s AND user_id = %s
                """,
                (conversation_uuid, tenant_id_uuid, user_uuid(principal_id)),
            )
        return cursor.fetchone()

    def get_conversation(self, conversation_id: str, *, current_scope: CacheScope) -> ConversationView | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                row = self._conversation_row(cursor, conversation_id, current_scope)
                if row is None:
                    return None
                created_at = _as_utc(row["created_at"])
                owner_kind = ActorKind.ANONYMOUS if row["user_id"] is None else ActorKind.AUTHENTICATED
                owner_id = (
                    f"anonymous:{row['anonymous_session_id']}"
                    if owner_kind is ActorKind.ANONYMOUS
                    else current_scope.principal_id
                )
                # The row's owner is checked in SQL; the scope is only the current authorization epoch.
                cursor.execute(
                    """
                    SELECT m.id, m.role, m.content, m.created_at,
                           q.response_message_id, q.checkpoint
                    FROM messages m
                    LEFT JOIN query_jobs q
                      ON q.tenant_id = m.tenant_id AND q.response_message_id = m.id
                    WHERE m.tenant_id = %s AND m.conversation_id = %s
                    ORDER BY m.created_at, m.id
                    """,
                    (row["tenant_id"], row["id"]),
                )
                message_rows = cursor.fetchall()
                messages = []
                for item in message_rows:
                    checkpoint = item.get("checkpoint") if hasattr(item, "get") else None
                    completion = checkpoint.get("completion") if isinstance(checkpoint, dict) else None
                    completion = completion if isinstance(completion, dict) else {}
                    raw_citations = completion.get("citations", ())
                    citations = tuple(dict(citation) for citation in raw_citations if isinstance(citation, dict))
                    raw_reasons = completion.get("reason_codes", ())
                    reasons = tuple(str(reason) for reason in raw_reasons)
                    response_id = item.get("response_message_id") if hasattr(item, "get") else None
                    role = str(item["role"]).lower()
                    messages.append(
                        (
                            MessageRecord(
                                str(item["id"]),
                                role,
                                _as_utc(item["created_at"]),
                                answer_id=str(response_id) if response_id else None,
                                status=str(completion.get("status")) if completion.get("status") else None,
                                citations=citations,
                                reason_codes=reasons,
                            ),
                            ConversationMessage(role, item["content"]),
                        )
                    )
                messages = tuple(messages)
                expires_at = created_at + (
                    timedelta(days=7) if owner_kind is ActorKind.ANONYMOUS else timedelta(days=180)
                )
                record = ConversationRecord(
                    conversation_id=str(row["id"]),
                    tenant_id=current_scope.tenant_id,
                    owner_kind=owner_kind,
                    owner_id=owner_id,
                    scope=current_scope,
                    created_at=created_at,
                    expires_at=expires_at,
                )
                if owner_kind is ActorKind.ANONYMOUS and _as_utc(datetime.now(timezone.utc)) >= expires_at:
                    return None
                return ConversationView(record, messages)

    def list_conversations(
        self,
        *,
        current_scope: CacheScope,
        limit: int,
        offset: int,
        search: str | None,
    ) -> tuple[tuple[ConversationSummary, ...], int]:
        """List only owner-scoped conversation metadata; never select message bodies."""

        if current_scope.principal_id.startswith("anonymous:"):
            session_id = _parse_uuid(current_scope.principal_id.removeprefix("anonymous:"))
            if session_id is None:
                return (), 0
            from_sql = """
                FROM conversations c
                JOIN anonymous_sessions s
                  ON s.tenant_id = c.tenant_id AND s.session_hash = c.anonymous_session_hash
            """
            where = ["c.tenant_id = %s", "c.status <> 'DELETED'", "s.id = %s"]
            params: list[object] = [tenant_uuid(current_scope.tenant_id), session_id]
        else:
            from_sql = "FROM conversations c"
            where = ["c.tenant_id = %s", "c.status <> 'DELETED'", "c.user_id = %s"]
            params = [tenant_uuid(current_scope.tenant_id), user_uuid(current_scope.principal_id)]

        if search and search.strip():
            escaped = search.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            where.append(
                "EXISTS (SELECT 1 FROM messages ms WHERE ms.tenant_id = c.tenant_id "
                "AND ms.conversation_id = c.id AND ms.role = 'USER' "
                "AND ms.content ILIKE %s ESCAPE '\\')"
            )
            params.append(f"%{escaped}%")

        predicate = " AND ".join(where)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT count(*) AS total {from_sql} WHERE {predicate}", tuple(params))
                total = int(cursor.fetchone()["total"])
                cursor.execute(
                    f"""
                    SELECT c.id, c.created_at, c.last_activity_at,
                           first_user.content AS first_user_content,
                           counts.message_count
                    {from_sql}
                    LEFT JOIN LATERAL (
                        SELECT m.content
                        FROM messages m
                        WHERE m.tenant_id = c.tenant_id
                          AND m.conversation_id = c.id
                          AND m.role = 'USER'
                        ORDER BY m.created_at, m.id
                        LIMIT 1
                    ) first_user ON TRUE
                    LEFT JOIN LATERAL (
                        SELECT count(*)::int AS message_count
                        FROM messages m
                        WHERE m.tenant_id = c.tenant_id AND m.conversation_id = c.id
                    ) counts ON TRUE
                    WHERE {predicate}
                    ORDER BY c.last_activity_at DESC, c.id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (*params, limit, offset),
                )
                rows = []
                for row in cursor.fetchall():
                    raw_title = str(row["first_user_content"] or "").strip()
                    rows.append(
                        ConversationSummary(
                            conversation_id=str(row["id"]),
                            title=raw_title[:96] or "New conversation",
                            created_at=_as_utc(row["created_at"]),
                            updated_at=_as_utc(row["last_activity_at"]),
                            message_count=int(row["message_count"] or 0),
                        )
                    )
                return tuple(rows), total

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
        message_id = uuid4()
        now = _as_utc(now)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                row = self._conversation_row(cursor, conversation_id, scope)
                if row is None:
                    raise StaleScopeError("conversation scope is stale")
                cursor.execute(
                    """
                    INSERT INTO messages (id, tenant_id, conversation_id, role, content, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (message_id, row["tenant_id"], row["id"], role.upper(), content, now),
                )
                cursor.execute(
                    "UPDATE conversations SET last_activity_at = %s WHERE id = %s",
                    (now, row["id"]),
                )
        return MessageRecord(str(message_id), role, now)

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
        job_id = uuid4()
        now = _as_utc(now)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO query_jobs
                        (id, tenant_id, conversation_id, request_message_id,
                         status, attempt_count, max_attempts, workflow_deadline_at,
                         queued_at, idempotency_key, created_at)
                    VALUES (%s, %s, %s, %s, 'QUEUED', 1, 3, %s, %s, %s, %s)
                    """,
                    (
                        job_id,
                        tenant_uuid(tenant_id),
                        UUID(conversation_id),
                        UUID(request_message_id),
                        _as_utc(deadline),
                        now,
                        idempotency_key,
                        now,
                    ),
                )
        return QueryJob(
            job_id=str(job_id),
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            request_message_id=request_message_id,
            request_message_index=request_message_index,
            response_message_id=None,
            state=JobState.QUEUED,
            attempt=1,
            attempt_id=f"{job_id}:1",
            revision=0,
            created_at=now,
            workflow_deadline_at=_as_utc(deadline),
            idempotency_key=idempotency_key,
        )

    def _load_job(self, cursor: object, row: object, scope: CacheScope) -> QueryJob | None:
        view = self.get_conversation(str(row["conversation_id"]), current_scope=scope)
        if view is None:
            return None
        request_index = next(
            (index for index, (message, _) in enumerate(view.messages) if str(message.message_id) == str(row["request_message_id"])),
            -1,
        )
        if request_index < 0:
            return None
        completion = None
        if row["response_message_id"] is not None:
            cursor.execute(
                "SELECT content, answer_status FROM messages WHERE id = %s AND tenant_id = %s",
                (row["response_message_id"], row["tenant_id"]),
            )
            answer_row = cursor.fetchone()
            checkpoint = row["checkpoint"] if isinstance(row["checkpoint"], dict) else {}
            stored = checkpoint.get("completion") if isinstance(checkpoint, dict) else None
            stored = stored if isinstance(stored, dict) else {}
            status = _answer_status(stored.get("status"))
            if answer_row is not None and not stored:
                status = {
                    "COMPLETED": AnswerState.ANSWERED,
                    "BLOCKED": AnswerState.ACCESS_DENIED,
                    "FAILED": AnswerState.ERROR,
                }.get(answer_row["answer_status"], AnswerState.ANSWERED)
            completion = QueryCompletion(
                status=status,
                answer=answer_row["content"] if answer_row is not None else "",
                citations=tuple(stored.get("citations", ())),
                reason_codes=tuple(str(code) for code in stored.get("reason_codes", ())),
            )
        checkpoint = row["checkpoint"] if isinstance(row["checkpoint"], dict) else None
        job = QueryJob(
            job_id=str(row["id"]),
            tenant_id=scope.tenant_id,
            conversation_id=str(row["conversation_id"]),
            request_message_id=str(row["request_message_id"]),
            request_message_index=request_index,
            response_message_id=(str(row["response_message_id"]) if row["response_message_id"] else None),
            state=JobState(str(row["status"])),
            attempt=int(row["attempt_count"]),
            attempt_id=f"{row['id']}:{row['attempt_count']}",
            revision=int(row["revision"]),
            created_at=_as_utc(row["created_at"]),
            workflow_deadline_at=_as_utc(row["workflow_deadline_at"]),
            idempotency_key=row["idempotency_key"] or "",
            checkpoint=self._checkpoint_from_json(checkpoint),
            completion=completion,
            error_code=row["checkpoint"].get("error_code") if isinstance(row["checkpoint"], dict) else None,
            maintenance_window_id=(str(row["maintenance_window_id"]) if row["maintenance_window_id"] else None),
        )
        return job

    @staticmethod
    def _checkpoint_json(checkpoint: JobCheckpoint, *, completion: dict[str, object] | None = None) -> dict[str, object]:
        value: dict[str, object] = {
            "stage": checkpoint.stage,
            "revision": checkpoint.revision,
            "attempt_id": checkpoint.attempt_id,
            "tenant_id": checkpoint.tenant_id,
            "conversation_id": checkpoint.conversation_id,
            "policy_epoch": checkpoint.policy_epoch,
            "query_hash": checkpoint.query_hash,
            "workflow_deadline_at": _utc_z(checkpoint.workflow_deadline_at),
            "safe_metadata": dict(checkpoint.safe_metadata),
        }
        if completion is not None:
            value["completion"] = completion
        return value

    @staticmethod
    def _checkpoint_from_json(value: object) -> JobCheckpoint | None:
        if not isinstance(value, dict) or not value.get("stage"):
            return None
        try:
            deadline = datetime.fromisoformat(str(value["workflow_deadline_at"]).replace("Z", "+00:00"))
            return JobCheckpoint(
                stage=str(value["stage"]),
                revision=int(value["revision"]),
                attempt_id=str(value["attempt_id"]),
                tenant_id=str(value["tenant_id"]),
                conversation_id=str(value["conversation_id"]),
                policy_epoch=int(value["policy_epoch"]),
                query_hash=str(value["query_hash"]),
                workflow_deadline_at=_as_utc(deadline),
                safe_metadata={str(k): str(v) for k, v in dict(value.get("safe_metadata", {})).items()},
            )
        except (KeyError, TypeError, ValueError):
            return None

    def get_job(self, job_id: str, *, current_scope: CacheScope) -> QueryJob | None:
        job_uuid = _parse_uuid(job_id)
        if job_uuid is None:
            return None
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM query_jobs WHERE id = %s AND tenant_id = %s",
                    (job_uuid, tenant_uuid(current_scope.tenant_id)),
                )
                row = cursor.fetchone()
                return self._load_job(cursor, row, current_scope) if row is not None else None

    def claim_job(self, job_id: str, *, scope: CacheScope, now: datetime) -> QueryJob:
        current = self.get_job(job_id, current_scope=scope)
        if current is None:
            raise StaleScopeError("job scope is stale")
        if current.state not in {JobState.QUEUED, JobState.PAUSED}:
            return current
        next_attempt = current.attempt + (1 if current.state is JobState.PAUSED else 0)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE query_jobs
                    SET status = 'RUNNING', attempt_count = %s, revision = revision + 1,
                        lease_id = %s, worker_id = 'api-runtime', heartbeat_at = %s,
                        lease_expires_at = %s, maintenance_window_id = NULL
                    WHERE id = %s AND tenant_id = %s AND status IN ('QUEUED', 'PAUSED')
                    """,
                    (
                        next_attempt,
                        str(uuid4()),
                        _as_utc(now),
                        _as_utc(now) + timedelta(seconds=60),
                        UUID(job_id),
                        tenant_uuid(scope.tenant_id),
                    ),
                )
        refreshed = self.get_job(job_id, current_scope=scope)
        if refreshed is None:
            raise StaleScopeError("job claim is stale")
        return refreshed

    def save_checkpoint(self, job_id: str, *, scope: CacheScope, checkpoint: JobCheckpoint) -> QueryJob:
        current = self.get_job(job_id, current_scope=scope)
        if current is None or checkpoint.revision != current.revision:
            raise StaleScopeError("stale checkpoint")
        value = self._checkpoint_json(checkpoint)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE query_jobs
                    SET checkpoint = %s, checkpoint_schema_version = '1.0', revision = revision + 1
                    WHERE id = %s AND tenant_id = %s AND revision = %s
                    """,
                    (_jsonb(value), UUID(job_id), tenant_uuid(scope.tenant_id), current.revision),
                )
        refreshed = self.get_job(job_id, current_scope=scope)
        if refreshed is None:
            raise StaleScopeError("stale checkpoint")
        return refreshed

    def pause_job(self, job_id: str, *, scope: CacheScope, maintenance_window_id: str, checkpoint: JobCheckpoint) -> QueryJob:
        current = self.get_job(job_id, current_scope=scope)
        if current is None or current.state is not JobState.RUNNING:
            raise StaleScopeError("job is not pausable")
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE query_jobs
                    SET status = 'PAUSED', checkpoint = %s, checkpoint_schema_version = '1.0',
                        revision = revision + 1, lease_id = NULL, worker_id = NULL,
                        heartbeat_at = NULL, lease_expires_at = NULL
                    WHERE id = %s AND tenant_id = %s AND status = 'RUNNING'
                    """,
                    (_jsonb(self._checkpoint_json(checkpoint)), UUID(job_id), tenant_uuid(scope.tenant_id)),
                )
        refreshed = self.get_job(job_id, current_scope=scope)
        if refreshed is None:
            raise StaleScopeError("job pause is stale")
        return refreshed

    def complete_job(self, job_id: str, *, scope: CacheScope, completion: QueryCompletion) -> QueryJob:
        current = self.get_job(job_id, current_scope=scope)
        if current is None:
            raise StaleScopeError("job scope is stale")
        if current.state is JobState.COMPLETED:
            return current
        if current.state is not JobState.RUNNING:
            raise StaleScopeError("job completion is stale")
        response_id = uuid4()
        answer_status = {
            AnswerState.ANSWERED: "COMPLETED",
            AnswerState.PARTIAL: "COMPLETED",
            AnswerState.INSUFFICIENT_EVIDENCE: "COMPLETED",
            AnswerState.ACCESS_DENIED: "BLOCKED",
            AnswerState.ERROR: "FAILED",
        }[completion.status]
        checkpoint = current.checkpoint or JobCheckpoint(
            stage="RUNNING",
            revision=current.revision,
            attempt_id=current.attempt_id,
            tenant_id=current.tenant_id,
            conversation_id=current.conversation_id,
            policy_epoch=scope.policy_epoch,
            query_hash="",
            workflow_deadline_at=current.workflow_deadline_at,
        )
        checkpoint_json = self._checkpoint_json(
            checkpoint,
            completion={
                "status": completion.status.value,
                "citations": [dict(item) for item in completion.citations],
                "reason_codes": list(completion.reason_codes),
            },
        )
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO messages (id, tenant_id, conversation_id, role, content, answer_status)
                    VALUES (%s, %s, %s, 'ASSISTANT', %s, %s)
                    """,
                    (
                        response_id,
                        tenant_uuid(scope.tenant_id),
                        UUID(current.conversation_id),
                        completion.answer or "Insufficient evidence to answer this question.",
                        answer_status,
                    ),
                )
                cursor.execute(
                    """
                    UPDATE query_jobs
                    SET status = 'COMPLETED', response_message_id = %s, completed_at = now(),
                        checkpoint = %s, checkpoint_schema_version = '1.0', revision = revision + 1,
                        lease_id = NULL, worker_id = NULL, heartbeat_at = NULL, lease_expires_at = NULL
                    WHERE id = %s AND tenant_id = %s AND status = 'RUNNING'
                    """,
                    (response_id, _jsonb(checkpoint_json), UUID(job_id), tenant_uuid(scope.tenant_id)),
                )
        refreshed = self.get_job(job_id, current_scope=scope)
        if refreshed is None:
            raise StaleScopeError("job completion is stale")
        return refreshed

    def fail_job(self, job_id: str, *, scope: CacheScope, error_code: str) -> QueryJob:
        current = self.get_job(job_id, current_scope=scope)
        if current is None:
            raise StaleScopeError("job scope is stale")
        if current.state in {JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED}:
            return current
        checkpoint = self._checkpoint_json(current.checkpoint) if current.checkpoint is not None else {}
        checkpoint["error_code"] = error_code
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE query_jobs
                    SET status = 'FAILED', completed_at = now(), checkpoint = %s,
                        checkpoint_schema_version = '1.0', revision = revision + 1,
                        lease_id = NULL, worker_id = NULL, heartbeat_at = NULL, lease_expires_at = NULL
                    WHERE id = %s AND tenant_id = %s
                    """,
                    (_jsonb(checkpoint), UUID(job_id), tenant_uuid(scope.tenant_id)),
                )
        refreshed = self.get_job(job_id, current_scope=scope)
        if refreshed is None:
            raise StaleScopeError("job failure is stale")
        return refreshed

    def cancel_job(self, job_id: str, *, scope: CacheScope, error_code: str) -> QueryJob:
        current = self.get_job(job_id, current_scope=scope)
        if current is None:
            raise StaleScopeError("job scope is stale")
        if current.state in {JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED}:
            return current
        checkpoint = self._checkpoint_json(current.checkpoint) if current.checkpoint is not None else {}
        checkpoint["error_code"] = error_code
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE query_jobs
                    SET status = 'CANCELLED', completed_at = now(), checkpoint = %s,
                        checkpoint_schema_version = '1.0', revision = revision + 1,
                        lease_id = NULL, worker_id = NULL, heartbeat_at = NULL, lease_expires_at = NULL
                    WHERE id = %s AND tenant_id = %s
                      AND status NOT IN ('COMPLETED', 'FAILED', 'CANCELLED')
                    """,
                    (_jsonb(checkpoint), UUID(job_id), tenant_uuid(scope.tenant_id)),
                )
        refreshed = self.get_job(job_id, current_scope=scope)
        if refreshed is None:
            raise StaleScopeError("job cancellation is stale")
        return refreshed

    def remember_submission(self, *, tenant_id: str, owner_id: str, conversation_id: str, key: str, fingerprint: str, job_id: str) -> None:
        response = {"job_id": job_id, "owner_id": owner_id}
        with self.connection() as connection:
            with connection.cursor() as cursor:
                self.ensure_tenant(cursor, tenant_id)
                cursor.execute(
                    """
                    INSERT INTO idempotency_keys
                        (id, tenant_id, operation, resource_key, idempotency_key,
                         request_fingerprint, response_status, safe_response, expires_at)
                    VALUES (%s, %s, 'chat:submit', %s, %s, %s, 202, %s, now() + interval '1 day')
                    ON CONFLICT (tenant_id, operation, resource_key, idempotency_key)
                    DO UPDATE SET safe_response = EXCLUDED.safe_response
                    """,
                    (uuid4(), tenant_uuid(tenant_id), conversation_id, key, fingerprint, _jsonb(response)),
                )

    def find_submission(self, *, tenant_id: str, owner_id: str, conversation_id: str, key: str) -> tuple[str, str] | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT request_fingerprint, safe_response
                    FROM idempotency_keys
                    WHERE tenant_id = %s AND operation = 'chat:submit'
                      AND resource_key = %s AND idempotency_key = %s
                      AND expires_at > now()
                    """,
                    (tenant_uuid(tenant_id), conversation_id, key),
                )
                row = cursor.fetchone()
                if row is None or not isinstance(row["safe_response"], dict):
                    return None
                if row["safe_response"].get("owner_id") != owner_id:
                    return None
                return str(row["request_fingerprint"]), str(row["safe_response"].get("job_id", ""))

    def add_citation(self, answer_id: str, artifact: CitationArtifact) -> None:
        # Citations are persisted with the answer checkpoint in complete_job.
        return None

    def answer_job(self, answer_id: str, *, current_scope: CacheScope) -> QueryJob | None:
        answer_uuid = _parse_uuid(answer_id)
        if answer_uuid is None:
            return None
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM query_jobs
                    WHERE tenant_id = %s AND (id = %s OR response_message_id = %s)
                    """,
                    (tenant_uuid(current_scope.tenant_id), answer_uuid, answer_uuid),
                )
                row = cursor.fetchone()
                return self._load_job(cursor, row, current_scope) if row is not None else None

    def get_citation(self, answer_id: str, citation_id: str, *, current_scope: CacheScope) -> CitationArtifact | None:
        job = self.answer_job(answer_id, current_scope=current_scope)
        if job is None or job.completion is None:
            return None
        for citation in job.completion.citations:
            if str(citation.get("citation_id", "")) == citation_id:
                return CitationArtifact(citation)
        return None

    def jobs_for_tenant(self, tenant_id: str, *, states: set[JobState]) -> tuple[QueryJob, ...]:
        if not states:
            return ()
        values = tuple(state.value for state in states)
        placeholders = ",".join("%s" for _ in values)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM query_jobs WHERE tenant_id = %s AND status IN ({placeholders}) ORDER BY created_at",
                    (tenant_uuid(tenant_id), *values),
                )
                jobs = []
                for row in cursor.fetchall():
                    # Dashboard usage only needs job metadata. Do not load messages
                    # or completion bodies through this aggregate read.
                    jobs.append(
                        QueryJob(
                            job_id=str(row["id"]),
                            tenant_id=tenant_id,
                            conversation_id=str(row["conversation_id"]),
                            request_message_id=str(row["request_message_id"]),
                            request_message_index=0,
                            response_message_id=(str(row["response_message_id"]) if row["response_message_id"] else None),
                            state=JobState(str(row["status"])),
                            attempt=int(row["attempt_count"]),
                            attempt_id=f"{row['id']}:{row['attempt_count']}",
                            revision=int(row["revision"]),
                            created_at=_as_utc(row["created_at"]),
                            workflow_deadline_at=_as_utc(row["workflow_deadline_at"]),
                            idempotency_key=row["idempotency_key"] or "",
                            error_code=row["checkpoint"].get("error_code") if isinstance(row["checkpoint"], dict) else None,
                        )
                    )
                return tuple(jobs)

    def request_query(self, job: QueryJob, *, scope: CacheScope) -> str | None:
        view = self.get_conversation(job.conversation_id, current_scope=scope)
        if view is None or job.request_message_index >= len(view.messages):
            return None
        message = view.messages[job.request_message_index][1]
        return message.content if message.role == "user" else None


class PostgresAuditSink(_PostgresAdapter):
    """Append-only audit sink that stores only the already-redacted event."""

    def append(self, event: object) -> None:
        from ..observability.audit import AuditEvent

        if not isinstance(event, AuditEvent):
            raise TypeError("event must be an AuditEvent")
        tenant_id = str(event.tenant_id or "public")
        occurred_at = datetime.fromisoformat(event.occurred_at.replace("Z", "+00:00"))
        with self.connection() as connection:
            with connection.cursor() as cursor:
                tenant_id_uuid = self.ensure_tenant(cursor, tenant_id)
                event_id = _parse_uuid(event.event_id) or uuid4()
                cursor.execute(
                    """
                    INSERT INTO audit_events
                        (id, tenant_id, actor_service, event_type, outcome, request_id,
                         action, decision, traceparent, trace_id, safe_metadata, occurred_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        event_id,
                        tenant_id_uuid,
                        "api",
                        event.event,
                        event.outcome,
                        event.request_id,
                        event.action,
                        event.decision,
                        event.traceparent,
                        event.trace_id,
                        _jsonb(dict(event.safe_metadata)),
                        _as_utc(occurred_at),
                    ),
                )

    def list_events(self, *, tenant_id: str, limit: int, offset: int) -> tuple[dict[str, object], ...]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, event_type, action, outcome, decision, request_id,
                           trace_id, occurred_at, safe_metadata
                    FROM audit_events
                    WHERE tenant_id = %s
                    ORDER BY occurred_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (tenant_uuid(tenant_id), limit, offset),
                )
                return tuple(
                    {
                        "event_id": str(row["id"]),
                        "event": row["event_type"],
                        "action": row["action"],
                        "outcome": row["outcome"],
                        "decision": row["decision"],
                        "request_id": row["request_id"],
                        "trace_id": row["trace_id"],
                        "occurred_at": _utc_z(_as_utc(row["occurred_at"])),
                        "safe_metadata": row["safe_metadata"] or {},
                    }
                    for row in cursor.fetchall()
                )

    def count_events(self, *, tenant_id: str) -> int:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) AS total FROM audit_events WHERE tenant_id = %s", (tenant_uuid(tenant_id),))
                return int(cursor.fetchone()["total"])


__all__ = [
    "PostgresAuditSink",
    "PostgresChatRepository",
    "RuntimeDatabaseUnavailable",
    "normalize_database_url",
    "stable_uuid",
]
