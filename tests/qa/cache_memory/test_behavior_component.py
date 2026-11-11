from datetime import datetime, timedelta, timezone

import pytest

from backend.app.cache import (
    CacheScope,
    InMemoryScopedCache,
    ScopedCacheAdapter,
    ScopedCacheKey,
    StaleScopeError,
)


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.now


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
    return CacheScope(
        tenant,
        principal,
        epoch,
        version,
        corpus,
        index,
        entitlements,
    )


def make_key(scope: CacheScope, query: str = "private question") -> ScopedCacheKey:
    return ScopedCacheKey.for_query(
        scope,
        query=query,
        model_config={"model": "local", "revision": "1"},
        prompt_version="answer-v1",
    )


class FakeProvider:
    """A provider-neutral fake that still delegates every scope check."""

    def __init__(self) -> None:
        self.backend = InMemoryScopedCache()

    def get(self, key: ScopedCacheKey, *, current_scope: CacheScope) -> object | None:
        return self.backend.get(key, current_scope=current_scope)

    def set(self, key: ScopedCacheKey, value: object, *, ttl_seconds: int) -> None:
        self.backend.set(key, value, ttl_seconds=ttl_seconds)

    def delete(self, key: ScopedCacheKey) -> bool:
        return self.backend.delete(key)

    def invalidate(self, event) -> None:
        self.backend.invalidate(event)


def test_scope_key_is_inspectable_and_request_inputs_are_hashed() -> None:
    current = make_scope(
        corpus=3,
        index="index-9",
        entitlements="department%2Ffinance",
    )
    secret = "conversation secret: do not expose"
    key = make_key(current, query=secret)
    rendered = key.as_string()

    assert "tenant-a" in rendered
    assert "user-a" in rendered
    assert ":7:" in rendered
    assert "version-1" in rendered
    assert ":3:index-9:" in rendered
    assert "department%252Ffinance" in rendered
    assert secret not in rendered
    assert make_key(current, query="different") != key


def test_cache_returns_a_deep_copy_and_isolates_mutations() -> None:
    current = make_scope()
    key = make_key(current)
    cache = InMemoryScopedCache()
    original = {"answer": ["authorized"], "meta": {"source": "v1"}}

    cache.set(key, original, ttl_seconds=60)
    original["answer"].append("mutated after write")
    returned = cache.get(key, current_scope=current)
    assert returned == {"answer": ["authorized"], "meta": {"source": "v1"}}

    returned["meta"]["source"] = "mutated after read"  # type: ignore[index]
    assert cache.get(key, current_scope=current) == {
        "answer": ["authorized"],
        "meta": {"source": "v1"},
    }


def test_cache_rejects_invalid_ttl_and_oversize_values() -> None:
    current = make_scope()
    key = make_key(current)
    cache = InMemoryScopedCache(max_value_bytes=8, max_ttl_seconds=10)

    for ttl in (0, -1, 11, True):
        with pytest.raises(ValueError):
            cache.set(key, "ok", ttl_seconds=ttl)
    with pytest.raises(ValueError):
        cache.set(key, "123456789", ttl_seconds=1)


def test_cache_expires_at_the_exact_ttl_deadline() -> None:
    clock = Clock()
    current = make_scope()
    key = make_key(current)
    cache = InMemoryScopedCache(clock=clock)

    cache.set(key, "value", ttl_seconds=10)
    clock.now += timedelta(seconds=9)
    assert cache.get(key, current_scope=current) == "value"
    clock.now += timedelta(seconds=1)
    assert cache.get(key, current_scope=current) is None


def test_scope_prefix_isolates_corpus_index_and_entitlement_partitions() -> None:
    current = make_scope(corpus=4, index="generation-4", entitlements="finance")
    key = make_key(current)
    cache = InMemoryScopedCache()
    cache.set(key, "authorized", ttl_seconds=60)

    for mismatched in (
        make_scope(corpus=5, index="generation-4", entitlements="finance"),
        make_scope(corpus=4, index="generation-5", entitlements="finance"),
        make_scope(corpus=4, index="generation-4", entitlements="engineering"),
    ):
        assert cache.get(key, current_scope=mismatched) is None


def test_narrow_document_version_invalidation_preserves_other_versions() -> None:
    cache = InMemoryScopedCache()
    broad = make_scope(version=None)
    target = make_scope(version="version-1")
    other = make_scope(version="version-2")
    other_tenant = make_scope(tenant="tenant-b", version="version-1")
    for value_scope, value in (
        (broad, "broad"),
        (target, "target"),
        (other, "other"),
        (other_tenant, "other tenant"),
    ):
        cache.set(make_key(value_scope), value, ttl_seconds=60)

    cache.on_document_version_change(tenant_id="tenant-a", document_version_id="version-1")

    assert cache.get(make_key(broad), current_scope=broad) is None
    assert cache.get(make_key(target), current_scope=target) is None
    assert cache.get(make_key(other), current_scope=other) == "other"
    assert cache.get(make_key(other_tenant), current_scope=other_tenant) == "other tenant"


def test_broad_acl_invalidation_removes_all_versions_in_one_tenant() -> None:
    cache = InMemoryScopedCache()
    tenant_a_v1 = make_scope(version="version-1")
    tenant_a_v2 = make_scope(version="version-2")
    tenant_a_broad = make_scope(version=None)
    tenant_b_v1 = make_scope(tenant="tenant-b", version="version-1")
    for value_scope, value in (
        (tenant_a_v1, "a1"),
        (tenant_a_v2, "a2"),
        (tenant_a_broad, "abroad"),
        (tenant_b_v1, "b1"),
    ):
        cache.set(make_key(value_scope), value, ttl_seconds=60)

    cache.on_acl_change(tenant_id="tenant-a")

    assert cache.get(make_key(tenant_a_v1), current_scope=tenant_a_v1) is None
    assert cache.get(make_key(tenant_a_v2), current_scope=tenant_a_v2) is None
    assert cache.get(make_key(tenant_a_broad), current_scope=tenant_a_broad) is None
    assert cache.get(make_key(tenant_b_v1), current_scope=tenant_b_v1) == "b1"


def test_policy_invalidation_stales_old_epoch_but_allows_new_epoch() -> None:
    cache = InMemoryScopedCache()
    old = make_scope(epoch=7)
    new = make_scope(epoch=8)
    old_key = make_key(old)
    new_key = make_key(new)
    cache.set(old_key, "old", ttl_seconds=60)
    cache.on_policy_change(tenant_id="tenant-a", policy_epoch=8)

    assert cache.get(old_key, current_scope=old) is None
    with pytest.raises(StaleScopeError):
        cache.set(old_key, "replayed", ttl_seconds=60)
    cache.set(new_key, "new", ttl_seconds=60)
    assert cache.get(new_key, current_scope=new) == "new"


def test_explicit_cache_delete_is_idempotent() -> None:
    current = make_scope()
    key = make_key(current)
    cache = InMemoryScopedCache()
    cache.set(key, "value", ttl_seconds=60)

    assert cache.delete(key) is True
    assert cache.delete(key) is False
    assert cache.get(key, current_scope=current) is None


def test_provider_neutral_fake_preserves_exact_scope_checks() -> None:
    owner = make_scope()
    key = make_key(owner)
    adapter: ScopedCacheAdapter = FakeProvider()

    adapter.set(key, "authorized", ttl_seconds=60)

    assert adapter.get(key, current_scope=owner) == "authorized"
    assert adapter.get(key, current_scope=make_scope(principal="user-b")) is None
    assert adapter.get(key, current_scope=make_scope(tenant="tenant-b")) is None
