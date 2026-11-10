"""Bounded request correlation and W3C trace context helpers."""

from __future__ import annotations

import re
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from uuid import uuid4


_REQUEST_ID = re.compile(r"^[\x21-\x7e]{1,128}$")
_TRACEPARENT = re.compile(
    r"^(?P<version>[0-9a-f]{2})-(?P<trace_id>[0-9a-f]{32})-"
    r"(?P<span_id>[0-9a-f]{16})-(?P<flags>[0-9a-f]{2})$"
)


def _new_traceparent() -> str:
    return f"00-{uuid4().hex}-{secrets.token_hex(8)}-01"


def _valid_traceparent(value: str | None) -> bool:
    if value is None:
        return False
    match = _TRACEPARENT.fullmatch(value.strip())
    if match is None or match.group("version") == "ff":
        return False
    return (
        set(match.group("trace_id")) != {"0"}
        and set(match.group("span_id")) != {"0"}
    )


def _header(headers: Mapping[str, str], name: str) -> str | None:
    value = headers.get(name)
    if value is not None:
        return value
    lowered = name.lower()
    return next((value for key, value in headers.items() if key.lower() == lowered), None)


@dataclass(frozen=True, slots=True)
class CorrelationContext:
    """The bounded identifiers shared by an API request and its audit events."""

    request_id: str
    traceparent: str
    trace_id: str

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> "CorrelationContext":
        request_id = _header(headers, "X-Request-ID")
        if request_id is None or _REQUEST_ID.fullmatch(request_id) is None:
            request_id = str(uuid4())

        traceparent = _header(headers, "traceparent")
        if traceparent is not None:
            traceparent = traceparent.strip()
        if not _valid_traceparent(traceparent):
            traceparent = _new_traceparent()
        trace_id = traceparent.split("-", 3)[1]
        return cls(request_id=request_id, traceparent=traceparent, trace_id=trace_id)

    def child(self) -> "CorrelationContext":
        """Create a new span ID while preserving the request's trace ID."""

        parts = self.traceparent.split("-")
        return CorrelationContext(
            request_id=self.request_id,
            traceparent=f"{parts[0]}-{self.trace_id}-{secrets.token_hex(8)}-{parts[3]}",
            trace_id=self.trace_id,
        )

    @property
    def response_headers(self) -> dict[str, str]:
        return {
            "X-Request-ID": self.request_id,
            "traceparent": self.traceparent,
        }
