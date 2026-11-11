"""Permission-scoped, provider-neutral cache primitives.

PostgreSQL remains the source of truth for policy and document state.  This
module only defines a replaceable cache boundary; the in-memory adapter is a
deterministic test/local implementation, not durable authority.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import hashlib
import json
from threading import RLock
from typing import Protocol
from urllib.parse import quote


DEFAULT_MAX_VALUE_BYTES = 256_000
DEFAULT_MAX_TTL_SECONDS = 3_600


class StaleScopeError(ValueError):
    """Raised when a caller tries to write under a revoked/stale scope."""


def _identifier(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(char) < 0x20 for char in value):
        raise ValueError(f"{field} must be a non-empty safe identifier")
    return value.strip()


def _component(value: str | None) -> str:
    return "-" if value is None else quote(value, safe="._~-")


def _digest(value: object) -> str:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as error:
        raise ValueError("cache fingerprint inputs must be JSON serializable") from error
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _serialized_size(value: object) -> int:
    if isinstance(value, bytes):
        return len(value)
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as error:
        raise ValueError("cache values must be JSON serializable, text or bytes") from error
    return len(encoded.encode("utf-8"))


@dataclass(frozen=True, slots=True)
class CacheScope:
    """The authorization and corpus scope that must match on every read."""

    tenant_id: str
    principal_id: str
    policy_epoch: int
    document_version_id: str | None
    corpus_epoch: int = 0
    index_generation: str = "current"
    entitlement_fingerprint: str = "default"

    def __post_init__(self) -> None:
        for field in ("tenant_id", "principal_id", "index_generation", "entitlement_fingerprint"):
            _identifier(getattr(self, field), field)
        if isinstance(self.policy_epoch, bool) or not isinstance(self.policy_epoch, int) or self.policy_epoch < 0:
            raise ValueError("policy_epoch must be a non-negative integer")
        if isinstance(self.corpus_epoch, bool) or not isinstance(self.corpus_epoch, int) or self.corpus_epoch < 0:
            raise ValueError("corpus_epoch must be a non-negative integer")
        if self.document_version_id is not None:
            _identifier(self.document_version_id, "document_version_id")

    def key_prefix(self) -> str:
        """Return an inspectable scope prefix without query or conversation text."""

        return ":".join(
            (
                _component(self.tenant_id),
                _component(self.principal_id),
                str(self.policy_epoch),
                _component(self.document_version_id),
                str(self.corpus_epoch),
                _component(self.index_generation),
                _component(self.entitlement_fingerprint),
            )
        )


@dataclass(frozen=True, slots=True)
class ScopedCacheKey:
    """A cache key whose request-specific portion is hashed."""

    namespace: str
    scope: CacheScope
    fingerprint: str

    def __post_init__(self) -> None:
        _identifier(self.namespace, "namespace")
        if len(self.fingerprint) != 64 or any(
            char not in "0123456789abcdef" for char in self.fingerprint
        ):
            raise ValueError("fingerprint must be a lowercase SHA-256 digest")

    @classmethod
    def for_query(
        cls,
        scope: CacheScope,
        *,
        query: str,
        model_config: Mapping[str, object] | str,
        prompt_version: str,
        namespace: str = "response",
    ) -> "ScopedCacheKey":
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        _identifier(prompt_version, "prompt_version")
        return cls(
            namespace,
            scope,
            _digest(
                {
                    "query": query.strip(),
                    "model_config": model_config,
                    "prompt_version": prompt_version,
                }
            ),
        )

    @classmethod
    def for_conversation(
        cls, scope: CacheScope, conversation_id: str
    ) -> "ScopedCacheKey":
        _identifier(conversation_id, "conversation_id")
        return cls("conversation", scope, _digest({"conversation_id": conversation_id}))

    def as_string(self) -> str:
        return f"scoped:v1:{_component(self.namespace)}:{self.scope.key_prefix()}:{self.fingerprint}"

    def __str__(self) -> str:
        return self.as_string()


class InvalidationReason(StrEnum):
    ACL_CHANGED = "ACL_CHANGED"
    PRINCIPAL_REVOKED = "PRINCIPAL_REVOKED"
    POLICY_CHANGED = "POLICY_CHANGED"
    DOCUMENT_VERSION_CHANGED = "DOCUMENT_VERSION_CHANGED"
    DELETED = "DELETED"


@dataclass(frozen=True, slots=True)
class InvalidationEvent:
    """Privacy-safe invalidation metadata; it never carries cached content."""

    tenant_id: str
    reason: InvalidationReason
    principal_id: str | None = None
    document_version_id: str | None = None
    policy_epoch: int | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.tenant_id, "tenant_id")
        object.__setattr__(self, "reason", InvalidationReason(self.reason))
        for field in ("principal_id", "document_version_id", "resource_id"):
            value = getattr(self, field)
            if value is not None:
                _identifier(value, field)
        if self.policy_epoch is not None and (
            isinstance(self.policy_epoch, bool)
            or not isinstance(self.policy_epoch, int)
            or self.policy_epoch < 0
        ):
            raise ValueError("policy_epoch must be a non-negative integer")
        if self.reason is InvalidationReason.PRINCIPAL_REVOKED and self.principal_id is None:
            raise ValueError("principal revocation requires principal_id")
        if self.reason is InvalidationReason.DOCUMENT_VERSION_CHANGED and self.document_version_id is None:
            raise ValueError("document version invalidation requires document_version_id")


class ScopedCacheAdapter(Protocol):
    """Replaceable cache interface for Redis or another non-authoritative backend."""

    def get(self, key: ScopedCacheKey, *, current_scope: CacheScope) -> object | None: ...

    def set(self, key: ScopedCacheKey, value: object, *, ttl_seconds: int) -> None: ...

    def delete(self, key: ScopedCacheKey) -> bool: ...

    def invalidate(self, event: InvalidationEvent) -> None: ...


@dataclass(frozen=True, slots=True)
class _CacheEntry:
    value: object
    expires_at: datetime


class InMemoryScopedCache:
    """Bounded TTL cache for local use and deterministic tests."""

    def __init__(
        self,
        *,
        max_value_bytes: int = DEFAULT_MAX_VALUE_BYTES,
        max_ttl_seconds: int = DEFAULT_MAX_TTL_SECONDS,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if max_value_bytes <= 0 or max_ttl_seconds <= 0:
            raise ValueError("cache limits must be positive")
        self.max_value_bytes = max_value_bytes
        self.max_ttl_seconds = max_ttl_seconds
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._entries: dict[str, tuple[ScopedCacheKey, _CacheEntry]] = {}
        self._invalidations: list[InvalidationEvent] = []
        self._lock = RLock()

    def get(self, key: ScopedCacheKey, *, current_scope: CacheScope) -> object | None:
        if key.scope != current_scope:
            return None
        now = self._clock()
        with self._lock:
            if self._is_invalidated(key):
                self._entries.pop(key.as_string(), None)
                return None
            stored = self._entries.get(key.as_string())
            if stored is None:
                return None
            _, entry = stored
            if now >= entry.expires_at:
                self._entries.pop(key.as_string(), None)
                return None
            return deepcopy(entry.value)

    def set(self, key: ScopedCacheKey, value: object, *, ttl_seconds: int) -> None:
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int):
            raise ValueError("ttl_seconds must be an integer")
        if not 0 < ttl_seconds <= self.max_ttl_seconds:
            raise ValueError("ttl_seconds exceeds the configured cache limit")
        if _serialized_size(value) > self.max_value_bytes:
            raise ValueError("cache value exceeds the configured byte limit")
        with self._lock:
            if self._is_invalidated(key):
                raise StaleScopeError("cache scope is stale or revoked")
            expires_at = self._clock() + timedelta(seconds=ttl_seconds)
            self._entries[key.as_string()] = (
                key,
                _CacheEntry(deepcopy(value), expires_at),
            )

    def delete(self, key: ScopedCacheKey) -> bool:
        with self._lock:
            return self._entries.pop(key.as_string(), None) is not None

    def invalidate(self, event: InvalidationEvent) -> None:
        with self._lock:
            self._invalidations.append(event)
            for cache_key, _ in tuple(self._entries.values()):
                if self._event_matches(cache_key, event):
                    self._entries.pop(cache_key.as_string(), None)

    def on_acl_change(
        self, *, tenant_id: str, document_version_id: str | None = None, principal_id: str | None = None
    ) -> None:
        self.invalidate(
            InvalidationEvent(
                tenant_id=tenant_id,
                reason=InvalidationReason.ACL_CHANGED,
                document_version_id=document_version_id,
                principal_id=principal_id,
            )
        )

    def on_principal_revoked(self, *, tenant_id: str, principal_id: str) -> None:
        self.invalidate(
            InvalidationEvent(
                tenant_id=tenant_id,
                reason=InvalidationReason.PRINCIPAL_REVOKED,
                principal_id=principal_id,
            )
        )

    def on_policy_change(self, *, tenant_id: str, policy_epoch: int | None = None) -> None:
        self.invalidate(
            InvalidationEvent(
                tenant_id=tenant_id,
                reason=InvalidationReason.POLICY_CHANGED,
                policy_epoch=policy_epoch,
            )
        )

    def on_document_version_change(self, *, tenant_id: str, document_version_id: str) -> None:
        self.invalidate(
            InvalidationEvent(
                tenant_id=tenant_id,
                reason=InvalidationReason.DOCUMENT_VERSION_CHANGED,
                document_version_id=document_version_id,
            )
        )

    def on_deleted(
        self,
        *,
        tenant_id: str,
        document_version_id: str | None = None,
        principal_id: str | None = None,
        resource_id: str | None = None,
    ) -> None:
        self.invalidate(
            InvalidationEvent(
                tenant_id=tenant_id,
                reason=InvalidationReason.DELETED,
                document_version_id=document_version_id,
                principal_id=principal_id,
                resource_id=resource_id,
            )
        )

    def _is_invalidated(self, key: ScopedCacheKey) -> bool:
        return any(self._event_matches(key, event) for event in self._invalidations)

    @staticmethod
    def _event_matches(key: ScopedCacheKey, event: InvalidationEvent) -> bool:
        scope = key.scope
        if scope.tenant_id != event.tenant_id:
            return False
        if event.principal_id is not None and scope.principal_id != event.principal_id:
            return False
        if event.document_version_id is not None and scope.document_version_id not in (
            None,
            event.document_version_id,
        ):
            return False
        if event.reason is InvalidationReason.POLICY_CHANGED:
            return event.policy_epoch is None or scope.policy_epoch < event.policy_epoch
        return True
