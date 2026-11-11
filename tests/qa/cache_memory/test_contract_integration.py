from datetime import datetime, timezone

import pytest

from backend.app.cache import (
    CacheScope,
    InMemoryScopedCache,
    InvalidationEvent,
    InvalidationReason,
    ScopedCacheKey,
)
from backend.app.memory import (
    ConversationMemory,
    ConversationMemoryRepository,
    ConversationMessage,
    InMemoryConversationMemory,
)


NOW = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)


def make_scope(
    *,
    tenant: str = "tenant-a",
    principal: str = "user-a",
    epoch: int = 42,
    version: str | None = "version-7",
    corpus: int = 3,
    index: str = "generation-9",
    entitlements: str = "finance",
) -> CacheScope:
    return CacheScope(tenant, principal, epoch, version, corpus, index, entitlements)


def make_key(scope: CacheScope, query: str = "approved query") -> ScopedCacheKey:
    return ScopedCacheKey.for_query(
        scope,
        query=query,
        model_config={"provider": "fake", "model": "qa-model"},
        prompt_version="prompt-v2",
    )


class FakeMemoryRepository:
    """A durable-boundary fake; authorization still belongs to the adapter."""

    def __init__(self) -> None:
        self.backend = InMemoryConversationMemory(clock=lambda: NOW)

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


def test_contract_scope_carries_every_authorization_and_corpus_partition() -> None:
    current = make_scope()
    key = make_key(current)

    assert key.scope == current
    assert key.scope.key_prefix() == "tenant-a:user-a:42:version-7:3:generation-9:finance"


def test_contract_request_fingerprint_changes_for_query_model_and_prompt() -> None:
    current = make_scope()
    query_key = make_key(current, query="question one")
    different_query = make_key(current, query="question two")
    different_model = ScopedCacheKey.for_query(
        current,
        query="question one",
        model_config={"provider": "fake", "model": "other-model"},
        prompt_version="prompt-v2",
    )
    different_prompt = ScopedCacheKey.for_query(
        current,
        query="question one",
        model_config={"provider": "fake", "model": "qa-model"},
        prompt_version="prompt-v3",
    )

    assert len({query_key.fingerprint, different_query.fingerprint, different_model.fingerprint, different_prompt.fingerprint}) == 4


def test_contract_policy_epoch_change_requires_a_new_scope_for_reuse() -> None:
    cache = InMemoryScopedCache()
    old = make_scope(epoch=42)
    new = make_scope(epoch=43)
    old_key = make_key(old)
    new_key = make_key(new)
    cache.set(old_key, "old answer", ttl_seconds=60)

    assert cache.get(old_key, current_scope=new) is None
    cache.on_policy_change(tenant_id="tenant-a", policy_epoch=43)
    assert cache.get(old_key, current_scope=old) is None
    cache.set(new_key, "new answer", ttl_seconds=60)
    assert cache.get(new_key, current_scope=new) == "new answer"


def test_contract_principal_revocation_is_limited_to_tenant_and_principal() -> None:
    cache = InMemoryScopedCache()
    target = make_scope()
    same_tenant_other_user = make_scope(principal="user-b")
    other_tenant_same_user = make_scope(tenant="tenant-b")
    for value_scope, value in (
        (target, "target"),
        (same_tenant_other_user, "other user"),
        (other_tenant_same_user, "other tenant"),
    ):
        cache.set(make_key(value_scope), value, ttl_seconds=60)

    cache.on_principal_revoked(tenant_id="tenant-a", principal_id="user-a")

    assert cache.get(make_key(target), current_scope=target) is None
    assert cache.get(make_key(same_tenant_other_user), current_scope=same_tenant_other_user) == "other user"
    assert cache.get(make_key(other_tenant_same_user), current_scope=other_tenant_same_user) == "other tenant"


def test_contract_acl_change_can_target_one_principal_and_version() -> None:
    cache = InMemoryScopedCache()
    target = make_scope(principal="user-a", version="version-1")
    other_version = make_scope(principal="user-a", version="version-2")
    other_principal = make_scope(principal="user-b", version="version-1")
    for value_scope, value in (
        (target, "target"),
        (other_version, "other version"),
        (other_principal, "other principal"),
    ):
        cache.set(make_key(value_scope), value, ttl_seconds=60)

    cache.on_acl_change(tenant_id="tenant-a", document_version_id="version-1", principal_id="user-a")

    assert cache.get(make_key(target), current_scope=target) is None
    assert cache.get(make_key(other_version), current_scope=other_version) == "other version"
    assert cache.get(make_key(other_principal), current_scope=other_principal) == "other principal"


def test_contract_document_change_invalidates_broad_scope_and_selected_version() -> None:
    cache = InMemoryScopedCache()
    broad = make_scope(version=None)
    selected = make_scope(version="version-7")
    other = make_scope(version="version-8")
    for value_scope, value in ((broad, "broad"), (selected, "selected"), (other, "other")):
        cache.set(make_key(value_scope), value, ttl_seconds=60)

    cache.on_document_version_change(tenant_id="tenant-a", document_version_id="version-7")

    assert cache.get(make_key(broad), current_scope=broad) is None
    assert cache.get(make_key(selected), current_scope=selected) is None
    assert cache.get(make_key(other), current_scope=other) == "other"


def test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach() -> None:
    cache = InMemoryScopedCache()
    target = make_scope(version="version-7")
    other_version = make_scope(version="version-8")
    other_tenant = make_scope(tenant="tenant-b", version="version-7")
    for value_scope, value in (
        (target, "target"),
        (other_version, "other version"),
        (other_tenant, "other tenant"),
    ):
        cache.set(make_key(value_scope), value, ttl_seconds=60)

    cache.on_deleted(tenant_id="tenant-a", document_version_id="version-7")

    assert cache.get(make_key(target), current_scope=target) is None
    assert cache.get(make_key(other_version), current_scope=other_version) == "other version"
    assert cache.get(make_key(other_tenant), current_scope=other_tenant) == "other tenant"


def test_contract_memory_read_requires_the_authoritative_current_scope() -> None:
    memory = InMemoryConversationMemory(clock=lambda: NOW)
    owner = make_scope()
    memory.append(owner, "conversation-1", ConversationMessage("user", "synthetic"))

    assert memory.read(owner, "conversation-1", current_scope=owner) is not None
    assert memory.read(owner, "conversation-1", current_scope=make_scope(epoch=43)) is None
    other = make_scope(principal="user-b")
    assert memory.read(other, "conversation-1", current_scope=other) is None


def test_contract_fake_repository_implements_provider_neutral_memory_boundary() -> None:
    repository: ConversationMemoryRepository = FakeMemoryRepository()
    owner = make_scope()
    saved = repository.append(owner, "conversation-1", ConversationMessage("user", "synthetic request"), now=NOW)

    assert repository.read(owner, "conversation-1", current_scope=owner) == saved
    assert repository.read(owner, "conversation-1", current_scope=make_scope(tenant="tenant-b")) is None


def test_contract_invalid_event_shapes_fail_closed_at_the_boundary() -> None:
    with pytest.raises(ValueError):
        InvalidationEvent(tenant_id="tenant-a", reason=InvalidationReason.PRINCIPAL_REVOKED)
    with pytest.raises(ValueError):
        InvalidationEvent(tenant_id="tenant-a", reason=InvalidationReason.DOCUMENT_VERSION_CHANGED)
