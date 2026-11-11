from datetime import datetime, timedelta, timezone

import pytest

from backend.app.cache import (
    CacheScope,
    InMemoryScopedCache,
    ScopedCacheKey,
    StaleScopeError,
)
from backend.app.memory import ConversationMessage, InMemoryConversationMemory


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.now


def scope(
    *,
    tenant: str = "tenant-a",
    principal: str = "user-a",
    epoch: int = 7,
    version: str | None = "version-1",
) -> CacheScope:
    return CacheScope(tenant, principal, epoch, version)


def response_key(value: CacheScope, query: str = "private question") -> ScopedCacheKey:
    return ScopedCacheKey.for_query(
        value,
        query=query,
        model_config={"model": "local", "revision": "1"},
        prompt_version="answer-v1",
    )


def test_cache_key_contains_security_scope_but_not_raw_query() -> None:
    key = response_key(scope(), query="conversation secret: do not put me in a key")

    rendered = key.as_string()
    assert "tenant-a" in rendered
    assert "user-a" in rendered
    assert ":7:" in rendered
    assert "version-1" in rendered
    assert "conversation secret" not in rendered


def test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal() -> None:
    cache = InMemoryScopedCache()
    owner_scope = scope()
    key = response_key(owner_scope)
    cache.set(key, {"answer": "authorized"}, ttl_seconds=60)

    assert cache.get(key, current_scope=owner_scope) == {"answer": "authorized"}
    assert cache.get(key, current_scope=scope(epoch=8)) is None
    assert cache.get(key, current_scope=scope(tenant="tenant-b")) is None
    assert cache.get(key, current_scope=scope(principal="user-b")) is None


def test_cache_expires_and_rejects_unbounded_ttl_or_value() -> None:
    clock = Clock()
    cache = InMemoryScopedCache(
        max_value_bytes=8,
        max_ttl_seconds=10,
        clock=clock,
    )
    key = response_key(scope())

    with pytest.raises(ValueError):
        cache.set(key, "too large", ttl_seconds=1)
    with pytest.raises(ValueError):
        cache.set(key, "ok", ttl_seconds=11)

    cache.set(key, "ok", ttl_seconds=10)
    clock.now += timedelta(seconds=10)
    assert cache.get(key, current_scope=scope()) is None


@pytest.mark.parametrize(
    ("hook", "affected", "unaffected"),
    [
        ("acl", scope(), scope(version="version-2")),
        ("principal", scope(), scope(principal="user-b")),
        ("version", scope(), scope(version="version-2")),
    ],
)
def test_cache_invalidation_hooks_remove_only_matching_scope(hook, affected, unaffected) -> None:
    cache = InMemoryScopedCache()
    affected_key = response_key(affected)
    unaffected_key = response_key(unaffected)
    cache.set(affected_key, "affected", ttl_seconds=60)
    cache.set(unaffected_key, "unaffected", ttl_seconds=60)

    if hook == "acl":
        cache.on_acl_change(tenant_id="tenant-a", document_version_id="version-1")
    elif hook == "principal":
        cache.on_principal_revoked(tenant_id="tenant-a", principal_id="user-a")
    else:
        cache.on_document_version_change(tenant_id="tenant-a", document_version_id="version-1")

    assert cache.get(affected_key, current_scope=affected) is None
    assert cache.get(unaffected_key, current_scope=unaffected) == "unaffected"


def test_policy_invalidation_is_fail_closed_for_old_epoch_but_allows_new_epoch() -> None:
    cache = InMemoryScopedCache()
    old_scope = scope(epoch=7)
    new_scope = scope(epoch=8)
    old_key = response_key(old_scope)
    new_key = response_key(new_scope)
    cache.set(old_key, "old", ttl_seconds=60)
    cache.on_policy_change(tenant_id="tenant-a", policy_epoch=8)

    assert cache.get(old_key, current_scope=old_scope) is None
    with pytest.raises(StaleScopeError):
        cache.set(old_key, "must not return", ttl_seconds=60)
    cache.set(new_key, "new", ttl_seconds=60)
    assert cache.get(new_key, current_scope=new_scope) == "new"


def test_document_change_invalidates_broad_corpus_cache_but_not_other_version() -> None:
    cache = InMemoryScopedCache()
    broad_scope = scope(version=None)
    other_version = scope(version="version-2")
    broad_key = response_key(broad_scope)
    other_key = response_key(other_version)
    cache.set(broad_key, "broad", ttl_seconds=60)
    cache.set(other_key, "other", ttl_seconds=60)

    cache.on_document_version_change(tenant_id="tenant-a", document_version_id="version-1")

    assert cache.get(broad_key, current_scope=broad_scope) is None
    assert cache.get(other_key, current_scope=other_version) == "other"


def test_cache_delete_is_explicit() -> None:
    cache = InMemoryScopedCache()
    current = scope()
    key = response_key(current)
    cache.set(key, "value", ttl_seconds=60)

    assert cache.delete(key) is True
    assert cache.delete(key) is False
    assert cache.get(key, current_scope=current) is None


def test_conversation_memory_is_scoped_bounded_and_repr_redacts_body() -> None:
    current = scope()
    memory = InMemoryConversationMemory(max_total_bytes=64)
    message = ConversationMessage("user", "conversation secret")

    saved = memory.append(current, "conversation-1", message)

    assert memory.read(current, "conversation-1", current_scope=current) == saved
    assert "conversation secret" not in repr(saved)
    assert "conversation secret" not in repr(message)
    assert memory.read(scope(principal="user-b"), "conversation-1", current_scope=scope(principal="user-b")) is None

    with pytest.raises(ValueError):
        memory.append(current, "conversation-1", ConversationMessage("user", "x" * 64))


def test_conversation_memory_expires_anonymous_sessions_and_revocation_is_fail_closed() -> None:
    clock = Clock()
    anonymous = scope(principal="anonymous:session-1")
    memory = InMemoryConversationMemory(clock=clock)
    memory.append(anonymous, "conversation-1", ConversationMessage("user", "hello"))

    clock.now += timedelta(minutes=30)
    assert memory.read(anonymous, "conversation-1", current_scope=anonymous) is None

    memory.append(anonymous, "conversation-2", ConversationMessage("user", "hello"))
    memory.on_principal_revoked(tenant_id="tenant-a", principal_id="anonymous:session-1")
    assert memory.read(anonymous, "conversation-2", current_scope=anonymous) is None


def test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() -> None:
    current = scope()
    memory = InMemoryConversationMemory()
    memory.append(current, "conversation-1", ConversationMessage("user", "private"))

    assert memory.delete(current, "conversation-1") is True
    assert memory.read(current, "conversation-1", current_scope=current) is None
    with pytest.raises(StaleScopeError):
        memory.append(current, "conversation-1", ConversationMessage("user", "private again"))
