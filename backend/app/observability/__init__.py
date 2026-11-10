"""Provider-neutral, privacy-safe application telemetry primitives."""

from .audit import (
    AuditEvent,
    AuditSink,
    AuditSinkUnavailable,
    InMemoryAuditSink,
    append_audit_event,
    redact_metadata,
)
from .context import CorrelationContext

__all__ = [
    "AuditEvent",
    "AuditSink",
    "AuditSinkUnavailable",
    "CorrelationContext",
    "InMemoryAuditSink",
    "append_audit_event",
    "redact_metadata",
]
