from datetime import datetime, timedelta, timezone
import time

import pytest

from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.tools import (
    AuthorizedScope,
    ToolCall,
    ToolGateway,
    ToolStatus,
)


class _Clock:
    def __init__(self):
        self.value = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)

    def __call__(self):
        return self.value


class _Resolvers:
    def __init__(self, principal, scope):
        self.principal = principal
        self.scope = scope

    def resolve(self, reference):
        return {"principal-1": self.principal}.get(reference) or {"scope-1": self.scope}.get(reference)


class _Policy:
    def __init__(self, epoch=7, allowed=True):
        self.epoch = epoch
        self.allowed = allowed

    def current_policy_epoch(self):
        return self.epoch

    def authorize_tool(self, principal, *, tenant_id, policy_epoch):
        return self.allowed


class _Backend:
    def __init__(self, *, payload=None, error=None, delay=0):
        self.calls = []
        self.payload = payload or {"evidence": []}
        self.error = error
        self.delay = delay

    def execute(self, tool, arguments, principal, scope, *, timeout_seconds):
        self.calls.append((tool, arguments, principal, scope, timeout_seconds))
        if self.delay:
            time.sleep(self.delay)
        if self.error:
            raise self.error
        return self.payload


def _principal(tenant="tenant-a"):
    return AuthenticatedPrincipal(
        user_id="user-1",
        tenant_id=tenant,
        roles=["employee"],
        department_ids=["department-1"],
        session_id="session-1",
        auth_time="2026-11-11T00:00:00Z",
    )


def _gateway(*, principal=None, scope=None, policy=None, backend=None, clock=None):
    clock = clock or _Clock()
    principal = principal or _principal()
    scope = scope or AuthorizedScope(
        "scope-1", "tenant-a", 7, clock.value + timedelta(minutes=5)
    )
    return ToolGateway(
        principals=_Resolvers(principal, None),
        scopes=_Resolvers(None, scope),
        policy=policy or _Policy(),
        backend=backend or _Backend(),
        clock=clock,
    ), clock, scope


def _call(clock, **overrides):
    values = {
        "tool": "search_documents",
        "arguments": {"query": "warranty", "top_k": 3},
        "principal_ref": "principal-1",
        "authorized_scope_ref": "scope-1",
        "tool_call_id": "call-1",
        "job_id": "job-1",
        "attempt_id": "attempt-1",
        "traceparent": "00-abc-abc-01",
        "deadline_at": clock.value + timedelta(seconds=5),
    }
    values.update(overrides)
    return ToolCall(**values)


def test_successful_call_returns_bounded_payload_and_typed_arguments():
    backend = _Backend(payload={"evidence": [{"chunk_id": "c-1"}]})
    gateway, clock, _ = _gateway(backend=backend)

    result = gateway.execute(_call(clock))

    assert result.status is ToolStatus.SUCCESS
    assert result.payload == {"evidence": [{"chunk_id": "c-1"}]}
    assert backend.calls[0][1].query == "warranty"


@pytest.mark.parametrize(
    ("tool", "expected"),
    [("delete_document", "TOOL_NOT_ALLOWED"), ("", "INVALID_ARGUMENTS")],
)
def test_unknown_or_empty_tool_is_rejected(tool, expected):
    gateway, clock, _ = _gateway()

    request = _call(clock).model_dump(mode="json")
    request["tool"] = tool
    result = gateway.execute(request)

    assert result.status is ToolStatus.INVALID_ARGUMENTS
    assert result.error_code == expected


def test_extra_argument_and_untrusted_scope_argument_are_rejected():
    gateway, clock, _ = _gateway()

    extra = gateway.execute(_call(clock, arguments={"query": "x", "unexpected": 1}))
    auth = gateway.execute(_call(clock, arguments={"query": "x", "tenant_id": "tenant-b"}, tool_call_id="call-2"))

    assert extra.error_code == "INVALID_ARGUMENTS"
    assert auth.error_code == "INVALID_ARGUMENTS"


def test_missing_scope_is_denied_without_backend_call():
    backend = _Backend()
    gateway, clock, _ = _gateway(backend=backend)

    result = gateway.execute(_call(clock, authorized_scope_ref="missing"))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "SCOPE_DENIED"
    assert backend.calls == []


def test_tenant_mismatch_is_denied():
    gateway, clock, _ = _gateway(principal=_principal("tenant-b"))

    result = gateway.execute(_call(clock))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "TENANT_MISMATCH"


def test_stale_policy_epoch_is_denied():
    gateway, clock, _ = _gateway(policy=_Policy(epoch=8))

    result = gateway.execute(_call(clock))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "SCOPE_STALE"


def test_policy_denial_is_distinct_from_argument_denial():
    gateway, clock, _ = _gateway(policy=_Policy(allowed=False))

    result = gateway.execute(_call(clock))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "TOOL_DENIED"


def test_same_tool_call_id_replays_identical_result_without_execution():
    backend = _Backend(payload={"ok": True})
    gateway, clock, _ = _gateway(backend=backend)
    call = _call(clock)

    first = gateway.execute(call)
    second = gateway.execute(call)

    assert first == second
    assert len(backend.calls) == 1


def test_reused_tool_call_id_with_different_arguments_is_rejected():
    backend = _Backend()
    gateway, clock, _ = _gateway(backend=backend)

    gateway.execute(_call(clock))
    result = gateway.execute(_call(clock, arguments={"query": "different"}))

    assert result.status is ToolStatus.INVALID_ARGUMENTS
    assert result.error_code == "REPLAY_DETECTED"
    assert len(backend.calls) == 1


def test_expired_deadline_returns_timeout_without_execution():
    backend = _Backend()
    gateway, clock, _ = _gateway(backend=backend)

    result = gateway.execute(_call(clock, deadline_at=clock.value - timedelta(seconds=1)))

    assert result.status is ToolStatus.TIMEOUT
    assert result.error_code == "DEADLINE_EXCEEDED"
    assert backend.calls == []


def test_backend_permission_error_is_denied():
    gateway, clock, _ = _gateway(backend=_Backend(error=PermissionError()))

    result = gateway.execute(_call(clock))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "RESOURCE_DENIED"


def test_backend_timeout_is_bounded():
    backend = _Backend(delay=0.05)
    gateway, clock, _ = _gateway(backend=backend)

    result = gateway.execute(_call(clock, deadline_at=clock.value + timedelta(milliseconds=1)))

    assert result.status is ToolStatus.TIMEOUT
    assert result.error_code in {"TOOL_TIMEOUT", "DEADLINE_EXCEEDED"}


def test_backend_exception_is_unavailable_without_raw_error():
    gateway, clock, _ = _gateway(backend=_Backend(error=RuntimeError("/private/path secret")))

    result = gateway.execute(_call(clock))

    assert result.status is ToolStatus.UNAVAILABLE
    assert result.error_code == "TOOL_UNAVAILABLE"
    assert "/private/path" not in repr(result)


def test_expired_scope_is_denied():
    clock = _Clock()
    scope = AuthorizedScope("scope-1", "tenant-a", 7, clock.value - timedelta(seconds=1))
    gateway, _, _ = _gateway(scope=scope, clock=clock)

    result = gateway.execute(_call(clock))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "SCOPE_STALE"


def test_tool_result_does_not_accept_unsafe_error_code():
    from backend.app.tools import ToolResult

    with pytest.raises(ValueError):
        ToolResult(ToolStatus.DENIED, "x", "c", error_code="raw path")
