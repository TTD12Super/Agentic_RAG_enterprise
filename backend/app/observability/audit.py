"""Append-only, privacy-safe audit events with a future adapter boundary."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from threading import RLock
from typing import Protocol
from uuid import uuid4

from .context import CorrelationContext


SAFE_METADATA_KEYS = frozenset(
    {
        "component",
        "dependency",
        "duration_ms",
        "error_code",
        "http_status",
        "method",
        "retryable",
        "route",
        "stage",
        "status_code",
    }
)
_SAFE_METADATA_TEXT = re.compile(r"^[A-Za-z0-9_./:-]{1,128}$")


def redact_metadata(metadata: Mapping[str, object] | None) -> dict[str, object]:
    """Keep only bounded operational fields; content and secrets are dropped."""

    if not metadata:
        return {}

    redacted: dict[str, object] = {}
    for key, value in metadata.items():
        if not isinstance(key, str) or key.lower() not in SAFE_METADATA_KEYS:
            continue
        normalized_key = key.lower()
        if isinstance(value, bool):
            redacted[normalized_key] = value
        elif (
            isinstance(value, int)
            and not isinstance(value, bool)
            and normalized_key in {"duration_ms", "http_status", "status_code"}
            and 0 <= value <= 600_000
        ):
            redacted[normalized_key] = value
        elif (
            isinstance(value, float)
            and normalized_key == "duration_ms"
            and 0 <= value <= 600_000
        ):
            redacted[normalized_key] = value
        elif isinstance(value, str) and _SAFE_METADATA_TEXT.fullmatch(value):
            redacted[normalized_key] = value
    return redacted


def _safe_identifier(value: str | None) -> str | None:
    if value is None or not 0 < len(value) <= 256 or any(ord(char) < 0x20 for char in value):
        return None
    return value


def _safe_code(value: str | None) -> str | None:
    if value is None or not 0 < len(value) <= 64:
        return None
    if not all(char.isalnum() or char in "._:-" for char in value):
        return None
    return value


def _utc_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """An immutable event containing identifiers and redacted metadata only."""

    event: str
    action: str
    outcome: str
    request_id: str
    traceparent: str
    trace_id: str
    occurred_at: str
    decision: str | None = None
    principal_id: str | None = None
    tenant_id: str | None = None
    code: str | None = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    safe_metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "safe_metadata", redact_metadata(self.safe_metadata))

    def as_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "event": self.event,
            "action": self.action,
            "outcome": self.outcome,
            "decision": self.decision,
            "request_id": self.request_id,
            "traceparent": self.traceparent,
            "trace_id": self.trace_id,
            "principal_id": self.principal_id,
            "tenant_id": self.tenant_id,
            "code": self.code,
            "occurred_at": self.occurred_at,
            "safe_metadata": dict(self.safe_metadata),
        }


class AuditSink(Protocol):
    """Small adapter contract for a later durable database/WORM sink."""

    def append(self, event: AuditEvent) -> None: ...


class AuditSinkUnavailable(RuntimeError):
    """Raised when telemetry cannot be accepted by its configured sink."""


class InMemoryAuditSink:
    """Thread-safe append-only sink for local runtime and deterministic tests."""

    def __init__(self, *, available: bool = True) -> None:
        self.available = available
        self._events: list[AuditEvent] = []
        self._lock = RLock()

    def append(self, event: AuditEvent) -> None:
        if not self.available:
            raise AuditSinkUnavailable("audit sink unavailable")
        with self._lock:
            self._events.append(event)

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        with self._lock:
            return tuple(self._events)


def append_audit_event(
    sink: AuditSink,
    *,
    context: CorrelationContext,
    event: str,
    action: str,
    outcome: str,
    decision: str | None = None,
    principal_id: str | None = None,
    tenant_id: str | None = None,
    code: str | None = None,
    metadata: Mapping[str, object] | None = None,
    occurred_at: datetime | None = None,
) -> AuditEvent:
    """Redact first, then append one immutable event to the injected sink."""

    audit_event = AuditEvent(
        event=event,
        action=action,
        outcome=outcome,
        decision=decision,
        request_id=context.request_id,
        traceparent=context.traceparent,
        trace_id=context.trace_id,
        principal_id=_safe_identifier(principal_id),
        tenant_id=_safe_identifier(tenant_id),
        code=_safe_code(code),
        occurred_at=_utc_z(occurred_at or datetime.now(timezone.utc)),
        safe_metadata=redact_metadata(metadata),
    )
    sink.append(audit_event)
    return audit_event
