"""Scoped conversation-memory boundary.

The durable implementation belongs behind ``ConversationMemoryRepository``
and PostgreSQL remains authoritative.  This adapter is intentionally only a
bounded, expiring local test double.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Protocol

from ..cache.scoped import (
    CacheScope,
    InvalidationEvent,
    InvalidationReason,
    ScopedCacheKey,
    StaleScopeError,
)


AUTHENTICATED_MEMORY_TTL = timedelta(days=180)
ANONYMOUS_IDLE_TTL = timedelta(minutes=30)
ANONYMOUS_MAX_AGE = timedelta(hours=24)
ANONYMOUS_RETENTION = timedelta(days=7)


@dataclass(frozen=True, slots=True, repr=False)
class ConversationMessage:
    """A body-bearing message that is returned only through the memory boundary."""

    role: str
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.role, str) or not self.role.strip():
            raise ValueError("message role is required")
        if not isinstance(self.content, str) or not self.content:
            raise ValueError("message content is required")

    def __repr__(self) -> str:
        return f"ConversationMessage(role={self.role!r}, content=<redacted>)"


@dataclass(frozen=True, slots=True, repr=False)
class ConversationMemory:
    conversation_id: str
    scope: CacheScope
    messages: tuple[ConversationMessage, ...]
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime

    def __repr__(self) -> str:
        return (
            f"ConversationMemory(conversation_id={self.conversation_id!r}, "
            f"message_count={len(self.messages)}, expires_at={self.expires_at!r})"
        )


class ConversationMemoryRepository(Protocol):
    """Durable repository contract; production implementations use PostgreSQL."""

    def read(
        self,
        scope: CacheScope,
        conversation_id: str,
        *,
        current_scope: CacheScope,
    ) -> ConversationMemory | None: ...

    def append(
        self,
        scope: CacheScope,
        conversation_id: str,
        message: ConversationMessage,
        *,
        now: datetime | None = None,
    ) -> ConversationMemory: ...

    def delete(self, scope: CacheScope, conversation_id: str) -> bool: ...

    def invalidate(self, event: InvalidationEvent) -> None: ...


class InMemoryConversationMemory:
    """Thread-safe bounded memory adapter with fail-closed scope checks."""

    def __init__(
        self,
        *,
        max_messages: int = 32,
        max_message_bytes: int = 16_000,
        max_total_bytes: int = 64_000,
        authenticated_ttl: timedelta = AUTHENTICATED_MEMORY_TTL,
        anonymous_idle_ttl: timedelta = ANONYMOUS_IDLE_TTL,
        anonymous_max_age: timedelta = ANONYMOUS_MAX_AGE,
        anonymous_retention: timedelta = ANONYMOUS_RETENTION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if min(max_messages, max_message_bytes, max_total_bytes) <= 0:
            raise ValueError("memory limits must be positive")
        if min(authenticated_ttl, anonymous_idle_ttl, anonymous_max_age, anonymous_retention) <= timedelta(0):
            raise ValueError("memory TTLs must be positive")
        self.max_messages = max_messages
        self.max_message_bytes = max_message_bytes
        self.max_total_bytes = max_total_bytes
        self.authenticated_ttl = authenticated_ttl
        self.anonymous_idle_ttl = anonymous_idle_ttl
        self.anonymous_max_age = anonymous_max_age
        self.anonymous_retention = anonymous_retention
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._entries: dict[str, ConversationMemory] = {}
        self._invalidations: list[InvalidationEvent] = []
        self._deleted: set[tuple[str, str, str]] = set()
        self._lock = RLock()

    def read(
        self,
        scope: CacheScope,
        conversation_id: str,
        *,
        current_scope: CacheScope,
    ) -> ConversationMemory | None:
        if scope != current_scope:
            return None
        key = ScopedCacheKey.for_conversation(scope, conversation_id)
        now = self._clock()
        with self._lock:
            if self._is_invalidated(key, conversation_id) or self._is_deleted(scope, conversation_id):
                self._entries.pop(key.as_string(), None)
                return None
            memory = self._entries.get(key.as_string())
            if memory is None:
                return None
            if now >= memory.expires_at:
                self._entries.pop(key.as_string(), None)
                return None
            return memory

    def set_clock(self, clock: Callable[[], datetime]) -> None:
        """Allow the owning local service to provide one deterministic clock."""

        self._clock = clock

    def append(
        self,
        scope: CacheScope,
        conversation_id: str,
        message: ConversationMessage,
        *,
        now: datetime | None = None,
    ) -> ConversationMemory:
        if not isinstance(message, ConversationMessage):
            raise TypeError("message must be a ConversationMessage")
        if len(message.content.encode("utf-8")) > self.max_message_bytes:
            raise ValueError("conversation message exceeds the configured byte limit")
        key = ScopedCacheKey.for_conversation(scope, conversation_id)
        now = now or self._clock()
        with self._lock:
            if self._is_invalidated(key, conversation_id) or self._is_deleted(scope, conversation_id):
                raise StaleScopeError("conversation scope is stale, revoked or deleted")
            previous = self._entries.get(key.as_string())
            messages = () if previous is None or now >= previous.expires_at else previous.messages
            messages = messages + (message,)
            if len(messages) > self.max_messages:
                raise ValueError("conversation exceeds the configured message limit")
            total_bytes = sum(
                len(item.role.encode("utf-8")) + len(item.content.encode("utf-8"))
                for item in messages
            )
            if total_bytes > self.max_total_bytes:
                raise ValueError("conversation exceeds the configured byte limit")
            created_at = previous.created_at if previous is not None and messages[:-1] else now
            expires_at = self._expires_at(scope, created_at, now)
            memory = ConversationMemory(
                conversation_id=conversation_id,
                scope=scope,
                messages=messages,
                created_at=created_at,
                last_activity_at=now,
                expires_at=expires_at,
            )
            self._entries[key.as_string()] = memory
            return memory

    def delete(self, scope: CacheScope, conversation_id: str) -> bool:
        deleted = False
        with self._lock:
            for cache_key, memory in tuple(self._entries.items()):
                if (
                    memory.conversation_id == conversation_id
                    and memory.scope.tenant_id == scope.tenant_id
                    and memory.scope.principal_id == scope.principal_id
                ):
                    self._entries.pop(cache_key, None)
                    deleted = True
            self._deleted.add((scope.tenant_id, scope.principal_id, conversation_id))
            return deleted

    def invalidate(self, event: InvalidationEvent) -> None:
        with self._lock:
            self._invalidations.append(event)
            for cache_key, memory in tuple(self._entries.items()):
                key = ScopedCacheKey.for_conversation(memory.scope, memory.conversation_id)
                if self._event_matches(key, memory.conversation_id, event):
                    self._entries.pop(cache_key, None)
                    if event.reason is InvalidationReason.DELETED and event.resource_id == memory.conversation_id:
                        self._deleted.add(
                            (memory.scope.tenant_id, memory.scope.principal_id, memory.conversation_id)
                        )

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

    def _expires_at(self, scope: CacheScope, created_at: datetime, now: datetime) -> datetime:
        if scope.principal_id.startswith("anonymous:"):
            return min(
                now + self.anonymous_idle_ttl,
                created_at + self.anonymous_max_age,
                created_at + self.anonymous_retention,
            )
        return now + self.authenticated_ttl

    def _is_invalidated(self, key: ScopedCacheKey, conversation_id: str) -> bool:
        return any(
            self._event_matches(key, conversation_id, event) for event in self._invalidations
        )

    def _is_deleted(self, scope: CacheScope, conversation_id: str) -> bool:
        return (scope.tenant_id, scope.principal_id, conversation_id) in self._deleted

    @staticmethod
    def _event_matches(
        key: ScopedCacheKey, conversation_id: str, event: InvalidationEvent
    ) -> bool:
        scope = key.scope
        if scope.tenant_id != event.tenant_id:
            return False
        if event.principal_id is not None and scope.principal_id != event.principal_id:
            return False
        if event.document_version_id is not None and scope.document_version_id != event.document_version_id:
            return False
        if event.resource_id is not None and event.resource_id == conversation_id:
            return True
        if event.reason is InvalidationReason.POLICY_CHANGED:
            return event.policy_epoch is None or scope.policy_epoch < event.policy_epoch
        return True
