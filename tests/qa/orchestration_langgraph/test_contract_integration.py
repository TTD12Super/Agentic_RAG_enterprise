from datetime import datetime, timedelta, timezone

from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.tools import (
    AuthorizedScope,
    GetDocumentMetadataArguments,
    MVP_TOOLS,
    ReadAuthorizedChunkArguments,
    SearchDocumentsArguments,
    TOOL_MANIFEST,
    ToolCall,
    ToolGateway,
    ToolStatus,
)


class Clock:
    value = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)

    def __call__(self):
        return self.value


class Resolvers:
    def __init__(self, principal, scope):
        self.principal = principal
        self.scope = scope

    def resolve(self, reference):
        if reference == "principal-1":
            return self.principal
        if reference == "scope-1":
            return self.scope
        return None


class Policy:
    def __init__(self, epoch=7, allowed=True):
        self.epoch = epoch
        self.allowed = allowed

    def current_policy_epoch(self):
        return self.epoch

    def authorize_tool(self, principal, *, tenant_id, policy_epoch):
        return self.allowed


class Backend:
    def __init__(self, payload=None):
        self.payload = payload or {"evidence": []}
        self.calls = []

    def execute(self, tool, arguments, principal, scope, *, timeout_seconds):
        self.calls.append((tool, arguments, principal, scope, timeout_seconds))
        return self.payload


def principal(tenant="tenant-a"):
    return AuthenticatedPrincipal(
        user_id="user-1", tenant_id=tenant, roles=["employee"],
        department_ids=["department-1"], session_id="session-1",
        auth_time="2026-11-11T00:00:00Z",
    )


def gateway(*, principal_value=None, scope=None, policy=None, backend=None, clock=None):
    clock = clock or Clock()
    scope = scope or AuthorizedScope("scope-1", "tenant-a", 7, clock.value + timedelta(minutes=5))
    return ToolGateway(
        principals=Resolvers(principal_value or principal(), None),
        scopes=Resolvers(None, scope),
        policy=policy or Policy(),
        backend=backend or Backend(),
        clock=clock,
    ), clock


def call(clock, *, tool="search_documents", arguments=None, **overrides):
    values = {
        "tool": tool,
        "arguments": arguments or {"query": "warranty", "top_k": 3},
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


def test_manifest_is_exactly_the_read_only_mvp_allowlist():
    assert MVP_TOOLS == {"search_documents", "read_authorized_chunk", "get_document_metadata"}
    assert set(TOOL_MANIFEST) == set(MVP_TOOLS)


def test_search_contract_delivers_typed_arguments_to_backend():
    backend = Backend()
    tool_gateway, clock = gateway(backend=backend)

    result = tool_gateway.execute(call(clock))

    assert result.status is ToolStatus.SUCCESS
    assert isinstance(backend.calls[0][1], SearchDocumentsArguments)
    assert backend.calls[0][1].query == "warranty"
    assert backend.calls[0][1].top_k == 3


def test_chunk_read_contract_accepts_only_chunk_id_shape():
    backend = Backend({"chunk_id": "chunk-1", "text": "authorized"})
    tool_gateway, clock = gateway(backend=backend)

    result = tool_gateway.execute(call(
        clock, tool="read_authorized_chunk", arguments={"chunk_id": "chunk-1"}
    ))

    assert result.status is ToolStatus.SUCCESS
    assert isinstance(backend.calls[0][1], ReadAuthorizedChunkArguments)
    assert backend.calls[0][1].chunk_id == "chunk-1"


def test_document_metadata_contract_accepts_document_id_shape():
    backend = Backend({"document_id": "doc-1", "status": "ACTIVE"})
    tool_gateway, clock = gateway(backend=backend)

    result = tool_gateway.execute(call(
        clock, tool="get_document_metadata", arguments={"document_id": "doc-1"}
    ))

    assert result.status is ToolStatus.SUCCESS
    assert isinstance(backend.calls[0][1], GetDocumentMetadataArguments)
    assert backend.calls[0][1].document_id == "doc-1"


def test_unregistered_tool_is_rejected_before_backend():
    backend = Backend()
    tool_gateway, clock = gateway(backend=backend)

    result = tool_gateway.execute(call(clock, tool="delete_document", arguments={}))

    assert result.status is ToolStatus.INVALID_ARGUMENTS
    assert result.error_code == "TOOL_NOT_ALLOWED"
    assert backend.calls == []


def test_unresolvable_scope_is_denied_without_execution():
    backend = Backend()
    tool_gateway, clock = gateway(backend=backend)

    result = tool_gateway.execute(call(clock, authorized_scope_ref="missing"))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "SCOPE_DENIED"
    assert backend.calls == []


def test_principal_and_scope_tenant_mismatch_is_denied():
    backend = Backend()
    tool_gateway, clock = gateway(principal_value=principal("tenant-b"), backend=backend)

    result = tool_gateway.execute(call(clock))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "TENANT_MISMATCH"
    assert backend.calls == []


def test_policy_epoch_mismatch_makes_scope_stale():
    backend = Backend()
    tool_gateway, clock = gateway(policy=Policy(epoch=8), backend=backend)

    result = tool_gateway.execute(call(clock))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "SCOPE_STALE"
    assert backend.calls == []


def test_policy_explicit_deny_is_distinct_from_bad_arguments():
    tool_gateway, clock = gateway(policy=Policy(allowed=False))

    result = tool_gateway.execute(call(clock))

    assert result.status is ToolStatus.DENIED
    assert result.error_code == "TOOL_DENIED"


def test_same_tool_call_id_is_idempotent_and_executes_once():
    backend = Backend({"ok": True})
    tool_gateway, clock = gateway(backend=backend)
    request = call(clock)

    first = tool_gateway.execute(request)
    second = tool_gateway.execute(request)

    assert first == second
    assert len(backend.calls) == 1
