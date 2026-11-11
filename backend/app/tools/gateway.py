"""Bounded, read-only Tool Gateway for the runtime agent boundary.

The gateway owns request validation, identity/scope resolution, policy freshness,
idempotency and execution budgets.  Tool backends remain adapters behind a
small protocol and must enforce resource-level authorization themselves.
"""

from __future__ import annotations

from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from threading import Lock
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from backend.app.authorization.policy import AnonymousPrincipal
from backend.app.guardrails import validate_tool_request
from backend.app.identity.models import AuthenticatedPrincipal


MVP_TOOLS = frozenset(
    {"search_documents", "read_authorized_chunk", "get_document_metadata"}
)
_TOOL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SAFE_CODE = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")
Principal = AuthenticatedPrincipal | AnonymousPrincipal


class ToolStatus(StrEnum):
    SUCCESS = "SUCCESS"
    DENIED = "DENIED"
    UNAVAILABLE = "UNAVAILABLE"
    INVALID_ARGUMENTS = "INVALID_ARGUMENTS"
    TIMEOUT = "TIMEOUT"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"


class ToolCall(BaseModel):
    """Typed envelope accepted from a planner or graph node.

    ``principal_ref`` and ``authorized_scope_ref`` are opaque server-issued
    references.  No principal, role, tenant or document allow-list is accepted
    in arguments.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = Field(default="1.0", pattern=r"^1\.0$")
    tool: str = Field(min_length=1, max_length=64)
    arguments: dict[str, Any]
    principal_ref: str = Field(min_length=1, max_length=256)
    authorized_scope_ref: str = Field(min_length=1, max_length=256)
    tool_call_id: str = Field(min_length=1, max_length=128)
    job_id: str = Field(min_length=1, max_length=128)
    attempt_id: str = Field(min_length=1, max_length=128)
    traceparent: str = Field(min_length=1, max_length=256)
    deadline_at: datetime

    @field_validator("tool_call_id")
    @classmethod
    def valid_tool_call_id(cls, value: str) -> str:
        if _TOOL_ID.fullmatch(value) is None:
            raise ValueError("tool_call_id is malformed")
        return value

    @field_validator("deadline_at")
    @classmethod
    def aware_deadline(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("deadline_at must be timezone-aware")
        return value.astimezone(timezone.utc)


class SearchDocumentsArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    query: str = Field(min_length=1, max_length=4_000)
    top_k: int = Field(default=8, ge=1, le=20)


class ReadAuthorizedChunkArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    chunk_id: str = Field(min_length=1, max_length=128)


class GetDocumentMetadataArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: str = Field(min_length=1, max_length=128)


@dataclass(frozen=True, slots=True)
class AuthorizedScope:
    """Server-issued scope bound to a tenant and a policy epoch."""

    scope_ref: str
    tenant_id: str
    policy_epoch: int
    expires_at: datetime
    allowed_tools: frozenset[str] = field(default_factory=lambda: MVP_TOOLS)

    def __post_init__(self) -> None:
        if not self.scope_ref.strip() or not self.tenant_id.strip():
            raise ValueError("scope identity is required")
        if isinstance(self.policy_epoch, bool) or not isinstance(self.policy_epoch, int) or self.policy_epoch < 0:
            raise ValueError("policy_epoch must be a non-negative integer")
        if self.expires_at.tzinfo is None:
            raise ValueError("scope expiry must be timezone-aware")
        if not self.allowed_tools <= MVP_TOOLS:
            raise ValueError("scope contains an unregistered tool")


class PrincipalResolver(Protocol):
    def resolve(self, principal_ref: str) -> Principal | None: ...


class ScopeResolver(Protocol):
    def resolve(self, scope_ref: str) -> AuthorizedScope | None: ...


class ToolPolicy(Protocol):
    def current_policy_epoch(self) -> int: ...

    def authorize_tool(
        self,
        principal: Principal,
        *,
        tenant_id: str,
        policy_epoch: int,
    ) -> bool: ...


class ToolBackend(Protocol):
    """Adapter boundary for existing retrieval/metadata services.

    The backend is responsible for document-level authorization and must return
    JSON-serializable, source-scoped data only.  The gateway never imports a
    concrete RAG provider.
    """

    def execute(
        self,
        tool: str,
        arguments: SearchDocumentsArguments | ReadAuthorizedChunkArguments | GetDocumentMetadataArguments,
        principal: Principal,
        scope: AuthorizedScope,
        *,
        timeout_seconds: float,
    ) -> Mapping[str, Any]: ...


@dataclass(frozen=True, slots=True)
class ToolResult:
    status: ToolStatus
    tool: str | None
    tool_call_id: str | None
    payload: Mapping[str, Any] = field(default_factory=dict)
    error_code: str | None = None

    def __post_init__(self) -> None:
        if self.error_code is not None and _SAFE_CODE.fullmatch(self.error_code) is None:
            raise ValueError("error_code must be a safe uppercase code")

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "status": self.status.value,
            "tool": self.tool,
            "tool_call_id": self.tool_call_id,
            "payload": dict(self.payload),
        }
        if self.error_code is not None:
            result["error_code"] = self.error_code
        return result


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    input_schema: str
    output_schema: str
    max_input_bytes: int
    max_output_bytes: int
    timeout_ms: int


TOOL_MANIFEST: Mapping[str, ToolSpec] = {
    "search_documents": ToolSpec(
        "search_documents", "search.v1", "evidence-list.v1", 16_000, 65_536, 10_000
    ),
    "read_authorized_chunk": ToolSpec(
        "read_authorized_chunk", "chunk-read.v1", "evidence.v1", 4_096, 65_536, 5_000
    ),
    "get_document_metadata": ToolSpec(
        "get_document_metadata",
        "document-metadata.v1",
        "document-metadata.v1",
        4_096,
        16_384,
        3_000,
    ),
}


_ARGUMENT_MODELS = {
    "search_documents": SearchDocumentsArguments,
    "read_authorized_chunk": ReadAuthorizedChunkArguments,
    "get_document_metadata": GetDocumentMetadataArguments,
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_tool_result(
    status: ToolStatus,
    call: ToolCall | None,
    *,
    tool: str | None = None,
    error_code: str | None = None,
) -> ToolResult:
    return ToolResult(
        status=status,
        tool=tool if tool is not None else getattr(call, "tool", None),
        tool_call_id=getattr(call, "tool_call_id", None),
        error_code=error_code,
    )


class ToolGateway:
    """Fail-closed, bounded execution boundary for the exact MVP allowlist."""

    def __init__(
        self,
        *,
        principals: PrincipalResolver,
        scopes: ScopeResolver,
        policy: ToolPolicy,
        backend: ToolBackend,
        clock: callable = _utc_now,
    ) -> None:
        self._principals = principals
        self._scopes = scopes
        self._policy = policy
        self._backend = backend
        self._clock = clock
        self._idempotency: dict[str, tuple[str, ToolResult]] = {}
        self._lock = Lock()

    def execute(self, request: ToolCall | Mapping[str, Any]) -> ToolResult:
        call = self._parse_call(request)
        if call is None:
            return _safe_tool_result(ToolStatus.INVALID_ARGUMENTS, None, error_code="INVALID_ARGUMENTS")

        spec = TOOL_MANIFEST.get(call.tool)
        if spec is None:
            return _safe_tool_result(
                ToolStatus.INVALID_ARGUMENTS, call, error_code="TOOL_NOT_ALLOWED"
            )
        validation = validate_tool_request(
            call.tool,
            action="tool:execute",
            arguments=call.arguments,
        )
        if not validation.allowed:
            return _safe_tool_result(
                ToolStatus.INVALID_ARGUMENTS, call, error_code="INVALID_ARGUMENTS"
            )
        arguments = self._parse_arguments(call)
        if arguments is None:
            return _safe_tool_result(
                ToolStatus.INVALID_ARGUMENTS, call, error_code="INVALID_ARGUMENTS"
            )
        if self._encoded_bytes(call.arguments) > spec.max_input_bytes:
            return _safe_tool_result(
                ToolStatus.INVALID_ARGUMENTS, call, error_code="INPUT_LIMIT"
            )

        fingerprint = self._fingerprint(call, arguments)
        with self._lock:
            previous = self._idempotency.get(call.tool_call_id)
            if previous is not None:
                if previous[0] != fingerprint:
                    return _safe_tool_result(
                        ToolStatus.INVALID_ARGUMENTS, call, error_code="REPLAY_DETECTED"
                    )
                return previous[1]

        now = self._clock().astimezone(timezone.utc)
        if call.deadline_at <= now:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.TIMEOUT, call, error_code="DEADLINE_EXCEEDED"
            ))

        try:
            principal = self._principals.resolve(call.principal_ref)
            scope = self._scopes.resolve(call.authorized_scope_ref)
        except Exception:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.UNAVAILABLE, call, error_code="IDENTITY_UNAVAILABLE"
            ))
        if principal is None or scope is None or scope.scope_ref != call.authorized_scope_ref:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.DENIED, call, error_code="SCOPE_DENIED"
            ))
        if getattr(principal, "tenant_id", None) != scope.tenant_id:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.DENIED, call, error_code="TENANT_MISMATCH"
            ))
        if now >= scope.expires_at:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.DENIED, call, error_code="SCOPE_STALE"
            ))
        if call.tool not in scope.allowed_tools:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.DENIED, call, error_code="TOOL_DENIED"
            ))

        try:
            current_epoch = self._policy.current_policy_epoch()
        except Exception:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.UNAVAILABLE, call, error_code="POLICY_UNAVAILABLE"
            ))
        if current_epoch != scope.policy_epoch:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.DENIED, call, error_code="SCOPE_STALE"
            ))
        try:
            allowed = self._policy.authorize_tool(
                principal,
                tenant_id=scope.tenant_id,
                policy_epoch=scope.policy_epoch,
            )
        except Exception:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.UNAVAILABLE, call, error_code="POLICY_UNAVAILABLE"
            ))
        if not allowed:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.DENIED, call, error_code="TOOL_DENIED"
            ))

        remaining = (call.deadline_at - now).total_seconds()
        timeout_seconds = min(remaining, spec.timeout_ms / 1000)
        if timeout_seconds <= 0:
            return self._remember(call, fingerprint, _safe_tool_result(
                ToolStatus.TIMEOUT, call, error_code="DEADLINE_EXCEEDED"
            ))
        result = self._run_backend(call, arguments, principal, scope, timeout_seconds, spec)
        return self._remember(call, fingerprint, result)

    def _run_backend(
        self,
        call: ToolCall,
        arguments: BaseModel,
        principal: Principal,
        scope: AuthorizedScope,
        timeout_seconds: float,
        spec: ToolSpec,
    ) -> ToolResult:
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tool-gateway")
        future = executor.submit(
            self._backend.execute,
            call.tool,
            arguments,
            principal,
            scope,
            timeout_seconds=timeout_seconds,
        )
        try:
            payload = future.result(timeout=timeout_seconds)
        except FutureTimeout:
            future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
            return _safe_tool_result(ToolStatus.TIMEOUT, call, error_code="TOOL_TIMEOUT")
        except PermissionError:
            executor.shutdown(wait=False, cancel_futures=True)
            return _safe_tool_result(ToolStatus.DENIED, call, error_code="RESOURCE_DENIED")
        except TimeoutError:
            executor.shutdown(wait=False, cancel_futures=True)
            return _safe_tool_result(ToolStatus.TIMEOUT, call, error_code="TOOL_TIMEOUT")
        except Exception:
            executor.shutdown(wait=False, cancel_futures=True)
            return _safe_tool_result(ToolStatus.UNAVAILABLE, call, error_code="TOOL_UNAVAILABLE")
        else:
            executor.shutdown(wait=True, cancel_futures=True)

        if not isinstance(payload, Mapping):
            return _safe_tool_result(ToolStatus.UNAVAILABLE, call, error_code="INVALID_TOOL_OUTPUT")
        try:
            bounded = json.loads(json.dumps(dict(payload), default=str, separators=(",", ":")))
            if self._encoded_bytes(bounded) > spec.max_output_bytes:
                return _safe_tool_result(ToolStatus.UNAVAILABLE, call, error_code="OUTPUT_LIMIT")
        except Exception:
            return _safe_tool_result(ToolStatus.UNAVAILABLE, call, error_code="INVALID_TOOL_OUTPUT")
        return ToolResult(ToolStatus.SUCCESS, call.tool, call.tool_call_id, bounded)

    def _remember(self, call: ToolCall, fingerprint: str, result: ToolResult) -> ToolResult:
        with self._lock:
            self._idempotency.setdefault(call.tool_call_id, (fingerprint, result))
            return self._idempotency[call.tool_call_id][1]

    @staticmethod
    def _parse_call(request: ToolCall | Mapping[str, Any]) -> ToolCall | None:
        if isinstance(request, ToolCall):
            return request
        if not isinstance(request, Mapping):
            return None
        try:
            return ToolCall.model_validate(request)
        except ValidationError:
            return None

    @staticmethod
    def _parse_arguments(call: ToolCall) -> BaseModel | None:
        model = _ARGUMENT_MODELS.get(call.tool)
        if model is None:
            return None
        try:
            parsed = model.model_validate(call.arguments)
            if isinstance(parsed, SearchDocumentsArguments):
                from backend.app.guardrails import normalize_user_input

                checked = normalize_user_input(parsed.query)
                if not checked.allowed or checked.value is None:
                    return None
                return parsed.model_copy(update={"query": checked.value})
            return parsed
        except ValidationError:
            return None

    @staticmethod
    def _encoded_bytes(value: object) -> int:
        return len(json.dumps(value, default=str, separators=(",", ":")).encode("utf-8"))

    @staticmethod
    def _fingerprint(call: ToolCall, arguments: BaseModel) -> str:
        material = {
            "tool": call.tool,
            "arguments": arguments.model_dump(mode="json"),
            "principal_ref": call.principal_ref,
            "authorized_scope_ref": call.authorized_scope_ref,
            "job_id": call.job_id,
            "attempt_id": call.attempt_id,
        }
        return hashlib.sha256(
            json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


__all__ = [
    "AuthorizedScope",
    "GetDocumentMetadataArguments",
    "MVP_TOOLS",
    "PrincipalResolver",
    "ReadAuthorizedChunkArguments",
    "ScopeResolver",
    "SearchDocumentsArguments",
    "TOOL_MANIFEST",
    "ToolBackend",
    "ToolCall",
    "ToolGateway",
    "ToolPolicy",
    "ToolResult",
    "ToolSpec",
    "ToolStatus",
]
