from datetime import datetime, timedelta, timezone

import pytest

from backend.app.cache import (
    CacheScope,
    InMemoryScopedCache,
    InvalidationEvent,
    InvalidationReason,
    ScopedCacheKey,
    StaleScopeError,
)
from backend.app.memory import (
    ConversationMemory,
    ConversationMemoryRepository,
    ConversationMessage,
    InMemoryConversationMemory,
)


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, delta: timedelta) -> None:
        self.now += delta


class FakeInvalidationBus:
    def __init__(self) -> None:
        self.pending: list[InvalidationEvent] = []

    def publish(self, event: InvalidationEvent) -> None:
        self.pending.append(event)

    def drain(self, *targets: object) -> None:
        event = self.pending.pop(0)
        for target in targets:
            target.invalidate(event)  # type: ignore[attr-defined]


class FakeMemoryRepository:
    def __init__(self, clock: Clock) -> None:
        self.backend = InMemoryConversationMemory(clock=clock)

    def read(
        self,
        scope: CacheScope,
        conversation_id: str,
        *,
        current_scope: CacheScope,
    ) -> ConversationMemory | None:
        return self.backend.read(scope, conversation_id, current_scope=current_scope)

    def append(
        self,
        scope: CacheScope,
        conversation_id: str,
        message: ConversationMessage,
        *,
        now: datetime | None = None,
    ) -> ConversationMemory:
        return self.backend.append(scope, conversation_id, message, now=now)

    def delete(self, scope: CacheScope, conversation_id: str) -> bool:
        return self.backend.delete(scope, conversation_id)

    def invalidate(self, event: InvalidationEvent) -> None:
        self.backend.invalidate(event)


def make_scope(
    *,
    tenant: str = "tenant-a",
    principal: str = "user-a",
    epoch: int = 7,
    version: str | None = "version-1",
    corpus: int = 0,
    index: str = "current",
    entitlements: str = "default",
) -> CacheScope:
    return CacheScope(tenant, principal, epoch, version, corpus, index, entitlements)


def make_key(scope: CacheScope) -> ScopedCacheKey:
    return ScopedCacheKey.for_query(
        scope,
        query="operational synthetic question",
        model_config={"model": "fake-model"},
        prompt_version="prompt-v1",
    )


def test_query_and_conversation_round_trip_through_fake_boundaries() -> None:
    clock = Clock()
    owner = make_scope()
    cache = InMemoryScopedCache(clock=clock)
    repository: ConversationMemoryRepository = FakeMemoryRepository(clock)
    saved = repository.append(owner, "conversation-1", ConversationMessage("user", "synthetic request"))
    cache.set(make_key(owner), {"answer": "synthetic response"}, ttl_seconds=60)

    assert repository.read(owner, "conversation-1", current_scope=owner) == saved
    assert cache.get(make_key(owner), current_scope=owner) == {"answer": "synthetic response"}


def test_resume_requires_exact_tenant_principal_policy_version_scope() -> None:
    clock = Clock()
    owner = make_scope()
    cache = InMemoryScopedCache(clock=clock)
    repository = FakeMemoryRepository(clock)
    key = make_key(owner)
    cache.set(key, "authorized", ttl_seconds=60)
    repository.append(owner, "conversation-1", ConversationMessage("user", "private"))

    mismatches = (
        make_scope(tenant="tenant-b"),
        make_scope(principal="user-b"),
        make_scope(epoch=8),
        make_scope(version="version-2"),
    )
    for current in mismatches:
        assert cache.get(key, current_scope=current) is None
        assert repository.read(owner, "conversation-1", current_scope=current) is None


def test_revocation_event_is_delivered_before_cache_or_memory_resume() -> None:
    clock = Clock()
    owner = make_scope()
    cache = InMemoryScopedCache(clock=clock)
    repository = FakeMemoryRepository(clock)
    key = make_key(owner)
    cache.set(key, "authorized", ttl_seconds=60)
    repository.append(owner, "conversation-1", ConversationMessage("user", "private"))
    bus = FakeInvalidationBus()
    bus.publish(
        InvalidationEvent(
            tenant_id="tenant-a",
            reason=InvalidationReason.PRINCIPAL_REVOKED,
            principal_id="user-a",
        )
    )

    bus.drain(cache, repository)

    assert cache.get(key, current_scope=owner) is None
    assert repository.read(owner, "conversation-1", current_scope=owner) is None
    with pytest.raises(StaleScopeError):
        cache.set(key, "replayed", ttl_seconds=60)
    with pytest.raises(StaleScopeError):
        repository.append(owner, "conversation-1", ConversationMessage("user", "replayed"))


def test_delete_retries_are_idempotent_and_old_conversation_stays_deleted() -> None:
    clock = Clock()
    owner = make_scope()
    cache = InMemoryScopedCache(clock=clock)
    repository = FakeMemoryRepository(clock)
    key = make_key(owner)
    cache.set(key, "answer", ttl_seconds=60)
    repository.append(owner, "conversation-1", ConversationMessage("user", "private"))

    assert cache.delete(key) is True
    assert cache.delete(key) is False
    assert repository.delete(owner, "conversation-1") is True
    assert repository.delete(owner, "conversation-1") is False
    assert repository.read(owner, "conversation-1", current_scope=owner) is None
    with pytest.raises(StaleScopeError):
        repository.append(owner, "conversation-1", ConversationMessage("user", "replay"))


def test_authenticated_memory_retention_resets_from_last_activity() -> None:
    clock = Clock()
    owner = make_scope()
    memory = InMemoryConversationMemory(clock=clock)
    memory.append(owner, "conversation-1", ConversationMessage("user", "first"))

    clock.advance(timedelta(days=179, hours=23))
    assert memory.read(owner, "conversation-1", current_scope=owner) is not None
    memory.append(owner, "conversation-1", ConversationMessage("user", "activity"))
    clock.advance(timedelta(days=179, hours=23))
    assert memory.read(owner, "conversation-1", current_scope=owner) is not None
    clock.advance(timedelta(hours=1))
    assert memory.read(owner, "conversation-1", current_scope=owner) is None


def test_anonymous_idle_retention_expires_at_boundary() -> None:
    clock = Clock()
    owner = make_scope(principal="anonymous:session-1")
    memory = InMemoryConversationMemory(
        anonymous_idle_ttl=timedelta(minutes=30),
        anonymous_max_age=timedelta(days=2),
        anonymous_retention=timedelta(days=7),
        clock=clock,
    )
    memory.append(owner, "conversation-1", ConversationMessage("user", "anonymous"))

    clock.advance(timedelta(minutes=29, seconds=59))
    assert memory.read(owner, "conversation-1", current_scope=owner) is not None
    clock.advance(timedelta(seconds=1))
    assert memory.read(owner, "conversation-1", current_scope=owner) is None


def test_anonymous_max_age_caps_an_active_session() -> None:
    clock = Clock()
    owner = make_scope(principal="anonymous:session-2")
    memory = InMemoryConversationMemory(
        anonymous_idle_ttl=timedelta(days=2),
        anonymous_max_age=timedelta(days=1),
        anonymous_retention=timedelta(days=7),
        clock=clock,
    )
    memory.append(owner, "conversation-1", ConversationMessage("user", "first"))
    clock.advance(timedelta(hours=12))
    memory.append(owner, "conversation-1", ConversationMessage("user", "activity"))
    clock.advance(timedelta(hours=11, minutes=59))
    assert memory.read(owner, "conversation-1", current_scope=owner) is not None
    clock.advance(timedelta(minutes=1))
    assert memory.read(owner, "conversation-1", current_scope=owner) is None


def test_anonymous_retention_bound_caps_memory_when_other_limits_are_longer() -> None:
    clock = Clock()
    owner = make_scope(principal="anonymous:session-3")
    memory = InMemoryConversationMemory(
        anonymous_idle_ttl=timedelta(days=7),
        anonymous_max_age=timedelta(days=7),
        anonymous_retention=timedelta(days=1),
        clock=clock,
    )
    memory.append(owner, "conversation-1", ConversationMessage("user", "anonymous"))

    clock.advance(timedelta(hours=23, minutes=59))
    assert memory.read(owner, "conversation-1", current_scope=owner) is not None
    clock.advance(timedelta(minutes=1))
    assert memory.read(owner, "conversation-1", current_scope=owner) is None


def test_memory_count_and_byte_limits_stop_growth() -> None:
    clock = Clock()
    owner = make_scope()
    count_limited = InMemoryConversationMemory(max_messages=1, clock=clock)
    count_limited.append(owner, "count", ConversationMessage("user", "one"))
    with pytest.raises(ValueError):
        count_limited.append(owner, "count", ConversationMessage("user", "two"))

    bytes_limited = InMemoryConversationMemory(max_total_bytes=8, clock=clock)
    with pytest.raises(ValueError):
        bytes_limited.append(owner, "bytes", ConversationMessage("user", "12345"))


def test_memory_repository_protocol_is_provider_neutral_and_redacted() -> None:
    clock = Clock()
    owner = make_scope()
    secret = "synthetic secret body"
    repository: ConversationMemoryRepository = FakeMemoryRepository(clock)
    saved = repository.append(owner, "conversation-1", ConversationMessage("user", secret))
    event = InvalidationEvent(
        tenant_id="tenant-a",
        reason=InvalidationReason.DELETED,
        resource_id="conversation-1",
    )

    assert repository.read(owner, "conversation-1", current_scope=owner) == saved
    assert secret not in repr(saved)
    assert secret not in repr(event)
