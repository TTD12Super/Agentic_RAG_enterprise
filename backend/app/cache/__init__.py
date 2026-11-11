"""Provider-neutral scoped cache boundary."""

from .scoped import (
    CacheScope,
    InMemoryScopedCache,
    InvalidationEvent,
    InvalidationReason,
    ScopedCacheAdapter,
    ScopedCacheKey,
    StaleScopeError,
)

__all__ = [
    "CacheScope",
    "InMemoryScopedCache",
    "InvalidationEvent",
    "InvalidationReason",
    "ScopedCacheAdapter",
    "ScopedCacheKey",
    "StaleScopeError",
]
