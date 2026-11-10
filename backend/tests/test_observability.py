from datetime import datetime, timezone

import pytest

from backend.app.observability import (
    AuditSinkUnavailable,
    CorrelationContext,
    InMemoryAuditSink,
    append_audit_event,
    redact_metadata,
)


TRACEPARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


def test_correlation_context_preserves_valid_headers_and_creates_child() -> None:
    context = CorrelationContext.from_headers(
        {"X-Request-ID": "req-123", "traceparent": TRACEPARENT}
    )

    assert context.request_id == "req-123"
    assert context.traceparent == TRACEPARENT
    assert context.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"

    child = context.child()
    assert child.request_id == context.request_id
    assert child.trace_id == context.trace_id
    assert child.traceparent != context.traceparent


def test_audit_sink_is_append_only_and_structured() -> None:
    sink = InMemoryAuditSink()
    event = append_audit_event(
        sink,
        context=CorrelationContext.from_headers({"X-Request-ID": "req-1"}),
        event="DOCUMENT_READ_DECISION",
        action="document:read",
        outcome="DENY",
        decision="DENY",
        principal_id="user-1",
        tenant_id="tenant-1",
        code="NOT_FOUND_OR_FORBIDDEN",
        occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    assert sink.events == (event,)
    assert event.as_dict()["request_id"] == "req-1"
    assert event.as_dict()["occurred_at"] == "2026-01-01T00:00:00Z"


def test_unavailable_sink_does_not_accept_an_event() -> None:
    sink = InMemoryAuditSink(available=False)

    with pytest.raises(AuditSinkUnavailable):
        append_audit_event(
            sink,
            context=CorrelationContext.from_headers({}),
            event="AUTH_SUCCESS",
            action="identity:sign_in",
            outcome="SUCCESS",
        )

    assert sink.events == ()


def test_redaction_drops_credentials_and_raw_content() -> None:
    metadata = redact_metadata(
        {
            "route": "identity:sign_in",
            "status_code": 401,
            "password": "correct-password",
            "authorization": "Bearer secret-token",
            "prompt": "raw prompt",
            "answer": "raw answer",
            "document_text": "confidential source text",
            "conversation_body": "private conversation",
            "query": "sensitive query",
        }
    )

    assert metadata == {"route": "identity:sign_in", "status_code": 401}
