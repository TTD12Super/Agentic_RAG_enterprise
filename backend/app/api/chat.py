"""Versioned chat, query-job, citation and feedback HTTP boundary."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Header, Request, Response
from fastapi.responses import JSONResponse, Response as RawResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..core.chat import (
    ANONYMOUS_SESSION_COOKIE,
    ANONYMOUS_SESSION_HEADER,
    ActorKind,
    CitationArtifact,
    ChatService,
    JobState,
    job_payload,
)
from ..feedback import FeedbackService
from ..identity.errors import IdentityError
from ..identity.models import AuthenticatedPrincipal
from . import identity as identity_api


class MessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=4_000)


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: str = Field(min_length=1, max_length=16)
    comment: str | None = Field(default=None, max_length=4_000)


router = APIRouter(tags=["chat"])
chat_service = ChatService()
feedback_service = FeedbackService()


def _maintenance_probe(tenant_id: str) -> str | None:
    try:
        from . import admin as admin_api

        tenant_uuid = admin_api._tenant_uuid(tenant_id)
        window_id = admin_api.admin_state.ingestion._active_maintenance.get(tenant_uuid)  # type: ignore[attr-defined]
        return str(window_id) if window_id is not None else None
    except Exception:
        return None


def _document_state(artifact: CitationArtifact) -> CitationArtifact:
    try:
        from . import admin as admin_api

        document_id = UUID(artifact.document_id)
        tenant_id = admin_api._tenant_uuid(artifact.tenant_id)
        document = admin_api.admin_state.ingestion.get_document(document_id, tenant_id)
        current = str(document.current_version_id) if document.current_version_id else None
        version_status = artifact.version_status
        if current:
            version = admin_api.admin_state.ingestion.get_version(UUID(current), tenant_id)
            version_status = version.metadata.status
        grants = admin_api.admin_state.document_grants.get((artifact.tenant_id, artifact.document_id), ())
        return CitationArtifact(
            citation=artifact.citation,
            preview=artifact.preview,
            download=artifact.download,
            classification=document.classification.value,
            status=document.status,
            version_status=version_status,
            current_version_id=current,
            acl=tuple(grants),
        )
    except Exception:
        return artifact


chat_service.maintenance_probe = _maintenance_probe
chat_service.document_state_provider = _document_state


def reset_state() -> None:
    global chat_service, feedback_service
    chat_service = ChatService(
        policy_store=chat_service.policy_store,
        maintenance_probe=_maintenance_probe,
        document_state_provider=_document_state,
    )
    feedback_service = FeedbackService()


def _optional_principal(authorization: str | None) -> AuthenticatedPrincipal | None:
    from . import admin as admin_api

    chat_service.set_authorization(admin_api.policy_store, admin_api.pep)
    if authorization is None:
        return None
    return identity_api.identity_service.resolve_bearer(identity_api._bearer_token(authorization))


def _anonymous_token(cookie: str | None, header: str | None) -> str | None:
    return header or cookie


async def _body(request: Request, model: type[BaseModel]) -> BaseModel:
    try:
        return model.model_validate(await request.json())
    except (ValueError, ValidationError) as error:
        raise IdentityError("REQUEST_INVALID", 400, "The request is invalid.") from error


def _context(request: Request, response: Response):
    return identity_api._request_context(request, response)


def _safe_audit(context, *, action: str, principal: AuthenticatedPrincipal | None, code: str) -> None:
    identity_api._record(
        context,
        event="CHAT_SUCCESS",
        action=action,
        outcome="SUCCESS",
        decision="ALLOW",
        principal=principal,
        code=code,
        metadata={"route": action, "status_code": 200},
    )


@router.post("/conversations", status_code=201)
async def create_conversation(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> dict[str, object]:
    context = _context(request, response)
    principal = _optional_principal(authorization)
    actor, created_session = chat_service.actor_for_create(
        principal, _anonymous_token(anonymous_session, anonymous_header)
    )
    conversation = chat_service.create_conversation(actor)
    if created_session and actor.session_token:
        response.set_cookie(
            ANONYMOUS_SESSION_COOKIE,
            actor.session_token,
            max_age=24 * 60 * 60,
            httponly=True,
            samesite="lax",
        )
    _safe_audit(context, action="chat:conversation:create", principal=principal, code="CONVERSATION_CREATED")
    return {
        "schema_version": "1.0",
        "conversation_id": conversation.conversation_id,
        "tenant_id": conversation.tenant_id,
        "session_id": actor.actor_id if actor.kind is ActorKind.ANONYMOUS else None,
        "expires_at": conversation.expires_at.isoformat().replace("+00:00", "Z"),
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> dict[str, object]:
    context = _context(request, response)
    principal = _optional_principal(authorization)
    actor = chat_service.actor_for_existing(principal, _anonymous_token(anonymous_session, anonymous_header))
    view = chat_service.conversation(actor, conversation_id)
    _safe_audit(context, action="chat:conversation:read", principal=principal, code="CONVERSATION_READ")
    return {
        "schema_version": "1.0",
        "conversation_id": conversation_id,
        "messages": [
            {
                "message_id": meta.message_id,
                "role": meta.role,
                "content": body.content,
                "created_at": meta.created_at.isoformat().replace("+00:00", "Z"),
            }
            for meta, body in view.messages
        ],
    }


@router.post("/conversations/{conversation_id}/messages", status_code=202)
async def submit_message(
    conversation_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> dict[str, object]:
    context = _context(request, response)
    principal = _optional_principal(authorization)
    actor = chat_service.actor_for_existing(principal, _anonymous_token(anonymous_session, anonymous_header))
    body = await _body(request, MessageRequest)
    job = chat_service.submit(actor, conversation_id, body.query, idempotency_key=idempotency_key)
    _safe_audit(context, action="chat:query:submit", principal=principal, code="QUERY_QUEUED")
    return {**job_payload(job), "request_id": context.request_id}


async def _job_status(
    job_id: str,
    request: Request,
    response: Response,
    authorization: str | None,
    anonymous_session: str | None,
    anonymous_header: str | None,
) -> dict[str, object]:
    context = _context(request, response)
    principal = _optional_principal(authorization)
    actor = chat_service.actor_for_existing(principal, _anonymous_token(anonymous_session, anonymous_header))
    job = chat_service.status(actor, job_id)
    _safe_audit(context, action="chat:query:status", principal=principal, code="QUERY_STATUS_READ")
    return {**job_payload(job, maintenance=chat_service.maintenance_probe(actor.tenant_id)), "request_id": context.request_id}


@router.get("/query-jobs/{job_id}")
async def get_query_job(
    job_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> dict[str, object]:
    return await _job_status(job_id, request, response, authorization, anonymous_session, anonymous_header)


@router.get("/query-jobs/{job_id}/completion")
async def get_query_completion(
    job_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> dict[str, object]:
    payload = await _job_status(job_id, request, response, authorization, anonymous_session, anonymous_header)
    if "answer" not in payload:
        raise IdentityError("QUERY_NOT_COMPLETE", 409, "The query is not complete.", retryable=True)
    return payload


@router.get("/answers/{answer_id}/citations/{citation_id}/preview")
async def preview_citation(
    answer_id: str,
    citation_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> dict[str, object]:
    principal = _optional_principal(authorization)
    actor = chat_service.actor_for_existing(principal, _anonymous_token(anonymous_session, anonymous_header))
    artifact = chat_service.citation(actor, answer_id, citation_id, download=False)
    return {"schema_version": "1.0", "citation": artifact.as_dict(), "preview": artifact.preview}


@router.get("/answers/{answer_id}/citations/{citation_id}/download")
async def download_citation(
    answer_id: str,
    citation_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> RawResponse:
    principal = _optional_principal(authorization)
    actor = chat_service.actor_for_existing(principal, _anonymous_token(anonymous_session, anonymous_header))
    artifact = chat_service.citation(actor, answer_id, citation_id, download=True)
    return RawResponse(content=artifact.download, media_type="application/octet-stream")


@router.post("/answers/{answer_id}/feedback")
async def submit_feedback(
    answer_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> JSONResponse:
    context = _context(request, response)
    principal = _optional_principal(authorization)
    actor = chat_service.actor_for_existing(principal, _anonymous_token(anonymous_session, anonymous_header))
    chat_service.feedback_target(actor, answer_id)
    body = await _body(request, FeedbackRequest)
    record, replay = feedback_service.submit(
        answer_id=answer_id,
        actor_id=actor.actor_id,
        rating=body.rating,
        comment=body.comment,
        idempotency_key=idempotency_key,
        tenant_id=actor.tenant_id,
    )
    identity_api._record(
        context,
        event="FEEDBACK_SUBMITTED",
        action="feedback:create",
        outcome="SUCCESS",
        decision="ALLOW",
        principal=principal,
        code="FEEDBACK_REPLAYED" if replay else "FEEDBACK_CREATED",
        metadata={"route": "feedback:create", "status_code": 200},
    )
    return JSONResponse(
        status_code=200 if replay else 201,
        content={
            "schema_version": "1.0",
            "feedback_id": record.feedback_id,
            "answer_id": record.answer_id,
            "rating": record.rating,
            "created_at": record.created_at.isoformat().replace("+00:00", "Z"),
        },
    )


__all__ = ["chat_service", "feedback_service", "reset_state", "router"]
