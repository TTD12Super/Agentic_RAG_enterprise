"""Minimal provider-neutral identity endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from ..identity.errors import AUTH_REQUIRED, IdentityError
from ..identity.models import AuthenticatedPrincipal
from ..identity.service import AuthenticationService
from ..identity.store import InMemoryIdentityStore
from ..observability import (
    AuditSink,
    CorrelationContext,
    InMemoryAuditSink,
    append_audit_event,
)


class SignInRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)
    mfa_code: str | None = Field(default=None, min_length=1, max_length=128)


class SignInResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    principal: AuthenticatedPrincipal


identity_store = InMemoryIdentityStore()
identity_service = AuthenticationService(identity_store)
audit_sink: AuditSink = InMemoryAuditSink()
router = APIRouter(prefix="/auth", tags=["identity"])


def _request_context(request: Request, response: Response) -> CorrelationContext:
    context = CorrelationContext.from_headers(request.headers)
    response.headers.update(context.response_headers)
    return context


def _record(
    context: CorrelationContext,
    *,
    event: str,
    action: str,
    outcome: str,
    decision: str | None = None,
    principal: AuthenticatedPrincipal | None = None,
    code: str | None = None,
    metadata: dict[str, object] | None = None,
) -> None:
    try:
        append_audit_event(
            audit_sink,
            context=context,
            event=event,
            action=action,
            outcome=outcome,
            decision=decision,
            principal_id=principal.user_id if principal else None,
            tenant_id=principal.tenant_id if principal else None,
            code=code,
            metadata=metadata,
        )
    except Exception as exc:
        # Authentication results are not returned when their audit outcome cannot be recorded.
        from ..identity.errors import AUTH_UNAVAILABLE

        raise AUTH_UNAVAILABLE from exc


def _record_identity_error(
    context: CorrelationContext,
    error: IdentityError,
    *,
    action: str,
) -> None:
    unavailable = error.code == "AUTH_UNAVAILABLE"
    _record(
        context,
        event="AUTH_FAILURE" if unavailable else "AUTH_DENIED",
        action=action,
        outcome="FAILURE" if unavailable else "DENY",
        decision=None if unavailable else "DENY",
        code=error.code,
        metadata={
            "route": action,
            "status_code": error.status_code,
            "retryable": error.retryable,
        },
    )


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise AUTH_REQUIRED
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise AUTH_REQUIRED
    return token


@router.post("/sign-in", response_model=SignInResponse)
async def sign_in(
    request: SignInRequest,
    http_request: Request,
    response: Response,
) -> SignInResponse:
    context = _request_context(http_request, response)
    try:
        token, _, principal = identity_service.sign_in(
            email=request.email,
            password=request.password,
            mfa_code=request.mfa_code,
        )
    except IdentityError as error:
        _record_identity_error(context, error, action="identity:sign_in")
        raise
    try:
        _record(
            context,
            event="AUTH_SUCCESS",
            action="identity:sign_in",
            outcome="SUCCESS",
            decision="ALLOW",
            principal=principal,
            code="AUTHENTICATED",
            metadata={"route": "identity:sign_in", "status_code": 200},
        )
    except IdentityError:
        try:
            identity_service.revoke(principal)
        except IdentityError:
            pass
        raise
    return SignInResponse(
        access_token=token,
        principal=principal,
    )


@router.get("/me", response_model=AuthenticatedPrincipal)
async def current_identity(
    http_request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedPrincipal:
    context = _request_context(http_request, response)
    try:
        principal = identity_service.resolve_bearer(_bearer_token(authorization))
    except IdentityError as error:
        _record_identity_error(context, error, action="identity:me")
        raise
    _record(
        context,
        event="AUTH_SUCCESS",
        action="identity:me",
        outcome="SUCCESS",
        decision="ALLOW",
        principal=principal,
        code="IDENTITY_RESOLVED",
        metadata={"route": "identity:me", "status_code": 200},
    )
    return principal


@router.post("/sign-out", status_code=204)
async def sign_out(
    http_request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    context = _request_context(http_request, response)
    try:
        principal = identity_service.resolve_bearer(_bearer_token(authorization))
        identity_service.revoke(principal)
    except IdentityError as error:
        _record_identity_error(context, error, action="identity:sign_out")
        raise
    _record(
        context,
        event="AUTH_SUCCESS",
        action="identity:sign_out",
        outcome="SUCCESS",
        decision="ALLOW",
        principal=principal,
        code="SESSION_REVOKED",
        metadata={"route": "identity:sign_out", "status_code": 204},
    )
