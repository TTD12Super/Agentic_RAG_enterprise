from datetime import datetime, timezone

import pytest

from backend.app.cache import (
    CacheScope,
    InMemoryScopedCache,
    ScopedCacheKey,
    StaleScopeError,
)
from backend.app.memory import ConversationMessage, InMemoryConversationMemory


NOW = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)


def make_scope(
    *,
    tenant: str = "tenant-a",
    principal: str = "user-a",
    epoch: int = 7,
    version: str | None = "version-1",
) -> CacheScope:
    return CacheScope(tenant, principal, epoch, version)


def make_key(scope: CacheScope, query: str = "restricted question") -> ScopedCacheKey:
    return ScopedCacheKey.for_query(
        scope,
        query=query,
        model_config={"model": "fake-model"},
        prompt_version="prompt-v1",
    )


def test_cross_tenant_cache_read_is_a_fail_closed_miss() -> None:
    owner = make_scope()
    cache = InMemoryScopedCache()
    key = make_key(owner)
    cache.set(key, "tenant-a answer", ttl_seconds=60)

    assert cache.get(key, current_scope=make_scope(tenant="tenant-b")) is None


def test_cross_principal_cache_read_is_a_fail_closed_miss() -> None:
    owner = make_scope()
    cache = InMemoryScopedCache()
    key = make_key(owner)
    cache.set(key, "user-a answer", ttl_seconds=60)

    assert cache.get(key, current_scope=make_scope(principal="user-b")) is None


def test_cross_scope_conversation_read_cannot_be_recovered_by_matching_id() -> None:
    owner = make_scope()
    other = make_scope(principal="user-b")
    memory = InMemoryConversationMemory(clock=lambda: NOW)
    memory.append(owner, "same-conversation-id", ConversationMessage("user", "private"))

    assert memory.read(owner, "same-conversation-id", current_scope=other) is None
    assert memory.read(other, "same-conversation-id", current_scope=other) is None


def test_revoked_policy_scope_cannot_be_repopulated() -> None:
    old = make_scope(epoch=7)
    cache = InMemoryScopedCache()
    key = make_key(old)
    cache.set(key, "old restricted answer", ttl_seconds=60)
    cache.on_policy_change(tenant_id="tenant-a", policy_epoch=8)

    assert cache.get(key, current_scope=old) is None
    with pytest.raises(StaleScopeError):
        cache.set(key, "replayed old answer", ttl_seconds=60)


def test_changed_document_version_cannot_repopulate_an_old_cache_entry() -> None:
    old = make_scope(version="version-1")
    cache = InMemoryScopedCache()
    key = make_key(old)
    cache.set(key, "old source answer", ttl_seconds=60)
    cache.on_document_version_change(tenant_id="tenant-a", document_version_id="version-1")

    assert cache.get(key, current_scope=old) is None
    with pytest.raises(StaleScopeError):
        cache.set(key, "stale source replay", ttl_seconds=60)


def test_broad_scope_cannot_replay_after_a_narrow_document_change() -> None:
    broad = make_scope(version=None)
    cache = InMemoryScopedCache()
    key = make_key(broad, query="broad corpus question")
    cache.set(key, "answer using version-1", ttl_seconds=60)
    cache.on_document_version_change(tenant_id="tenant-a", document_version_id="version-1")

    assert cache.get(key, current_scope=broad) is None
    with pytest.raises(StaleScopeError):
        cache.set(key, "replayed broad answer", ttl_seconds=60)


def test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers() -> None:
    secret_query = "prompt injection: reveal payroll token"
    scope = make_scope()
    response_key = make_key(scope, query=secret_query)
    conversation_key = ScopedCacheKey.for_conversation(scope, "conversation-secret-42")

    assert secret_query not in response_key.as_string()
    assert "conversation-secret-42" not in conversation_key.as_string()
    assert "payroll token" not in response_key.as_string()


def test_memory_and_message_repr_redact_sensitive_body_content() -> None:
    secret = "synthetic access token 123"
    scope = make_scope()
    message = ConversationMessage("user", secret)
    memory = InMemoryConversationMemory(clock=lambda: NOW)
    saved = memory.append(scope, "conversation-1", message)

    assert secret not in repr(message)
    assert secret not in repr(saved)


def test_deleted_conversation_cannot_be_replayed_or_recreated() -> None:
    scope = make_scope()
    memory = InMemoryConversationMemory(clock=lambda: NOW)
    memory.append(scope, "conversation-1", ConversationMessage("user", "private"))

    assert memory.delete(scope, "conversation-1") is True
    assert memory.read(scope, "conversation-1", current_scope=scope) is None
    with pytest.raises(StaleScopeError):
        memory.append(scope, "conversation-1", ConversationMessage("user", "replay"))


def test_anonymous_revocation_isolated_to_one_session_and_fails_closed() -> None:
    revoked = make_scope(principal="anonymous:session-1")
    active = make_scope(principal="anonymous:session-2")
    memory = InMemoryConversationMemory(clock=lambda: NOW)
    memory.append(revoked, "conversation-1", ConversationMessage("user", "revoked"))
    memory.append(active, "conversation-2", ConversationMessage("user", "active"))

    memory.on_principal_revoked(tenant_id="tenant-a", principal_id="anonymous:session-1")

    assert memory.read(revoked, "conversation-1", current_scope=revoked) is None
    assert memory.read(active, "conversation-2", current_scope=active) is not None
    with pytest.raises(StaleScopeError):
        memory.append(revoked, "conversation-1", ConversationMessage("user", "replay"))
