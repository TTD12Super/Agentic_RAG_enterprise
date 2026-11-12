"""Versioned chat, query-job, citation and feedback HTTP boundary."""

from __future__ import annotations

import asyncio
import json
from threading import Event
from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Cookie, Header, Query, Request, Response
from fastapi.responses import JSONResponse, Response as RawResponse, StreamingResponse
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
from ..ingestion.lifecycle import IngestionError, NotFound
from ..rag.runtime import LocalRagExecutor
from ..core.config import get_settings
from ..db.runtime import PostgresChatRepository


class MessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=4_000)


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: str = Field(min_length=1, max_length=16)
    comment: str | None = Field(default=None, max_length=4_000)


router = APIRouter(tags=["chat"])
# Development default: this connects the HTTP chat boundary to the real local
# ingestion/retrieval/citation pipeline. Production replaces it with a worker
# executor backed by approved providers and durable repositories.
_database_url = get_settings().database_url
chat_service = ChatService(
    repository=PostgresChatRepository(_database_url) if _database_url else None,
    executor=LocalRagExecutor(),
)
feedback_service = FeedbackService()
from . import identity as identity_api  # noqa: E402


def _maintenance_probe(tenant_id: str) -> str | None:
    try:
        from . import admin as admin_api

        tenant_uuid = admin_api._tenant_uuid(tenant_id)
        window_id = admin_api.admin_state.ingestion._active_maintenance.get(tenant_uuid)  # type: ignore[attr-defined]
        return str(window_id) if window_id is not None else None
    except Exception:
        return None


def _document_state(artifact: CitationArtifact) -> CitationArtifact | None:
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
            owner_department_id=(
                str(document.owner_department_id) if document.owner_department_id else None
            ),
            acl=tuple(grants),
        )
    except NotFound:
        local_state = getattr(chat_service.executor, "citation_state", None)
        if callable(local_state):
            return local_state(artifact)
        return None
    except IngestionError as error:
        raise IdentityError("AUTH_UNAVAILABLE", 503, "Authorization is temporarily unavailable.", retryable=True) from error
    except Exception as error:
        raise IdentityError("AUTH_UNAVAILABLE", 503, "Authorization is temporarily unavailable.", retryable=True) from error


chat_service.maintenance_probe = _maintenance_probe
chat_service.document_state_provider = _document_state


def reset_state() -> None:
    global chat_service, feedback_service
    chat_service = ChatService(
        repository=PostgresChatRepository(_database_url) if _database_url else None,
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
        cross_origin_https = request.headers.get("origin", "").startswith("https://")
        response.set_cookie(
            ANONYMOUS_SESSION_COOKIE,
            actor.session_token,
            max_age=24 * 60 * 60,
            httponly=True,
            samesite="none" if cross_origin_https else "lax",
            secure=cross_origin_https,
        )
    _safe_audit(context, action="chat:conversation:create", principal=principal, code="CONVERSATION_CREATED")
    return {
        "schema_version": "1.0",
        "conversation_id": conversation.conversation_id,
        "tenant_id": conversation.tenant_id,
        "session_id": actor.actor_id if actor.kind is ActorKind.ANONYMOUS else None,
        "expires_at": conversation.expires_at.isoformat().replace("+00:00", "Z"),
    }


@router.get("/conversations")
async def list_conversations(
    request: Request,
    response: Response,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=10_000)] = 0,
    search: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
    authorization: Annotated[str | None, Header()] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> dict[str, object]:
    context = _context(request, response)
    principal = _optional_principal(authorization)
    actor = chat_service.actor_for_existing(principal, _anonymous_token(anonymous_session, anonymous_header))
    items, total = chat_service.list_conversations(
        actor,
        limit=limit,
        offset=offset,
        search=search,
    )
    _safe_audit(context, action="chat:conversation:list", principal=principal, code="CONVERSATIONS_LISTED")
    return {
        "schema_version": "1.0",
        "items": [
            {
                "conversation_id": item.conversation_id,
                "title": item.title,
                "created_at": item.created_at.isoformat().replace("+00:00", "Z"),
                "updated_at": item.updated_at.isoformat().replace("+00:00", "Z"),
                "message_count": item.message_count,
            }
            for item in items
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": offset + len(items) < total,
        },
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
                "answer_id": meta.answer_id,
                "status": meta.status,
                "citations": [dict(citation) for citation in meta.citations],
                "reason_codes": list(meta.reason_codes),
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


def _sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'), default=str)}\n\n"


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    anonymous_session: Annotated[str | None, Cookie(alias=ANONYMOUS_SESSION_COOKIE)] = None,
    anonymous_header: Annotated[str | None, Header(alias=ANONYMOUS_SESSION_HEADER)] = None,
) -> StreamingResponse:
    context = _context(request, response)
    principal = _optional_principal(authorization)
    actor = chat_service.actor_for_existing(principal, _anonymous_token(anonymous_session, anonymous_header))
    body = await _body(request, MessageRequest)
    job = chat_service.submit(actor, conversation_id, body.query, idempotency_key=idempotency_key)
    _safe_audit(context, action="chat:query:stream", principal=principal, code="QUERY_QUEUED")

    async def events():
        cancelled = Event()
        monitor_done = asyncio.Event()

        async def monitor_disconnect() -> None:
            try:
                while not monitor_done.is_set():
                    if await request.is_disconnected():
                        cancelled.set()
                        return
                    await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                return

        monitor = asyncio.create_task(monitor_disconnect())
        iterator = chat_service.stream(actor, job.job_id, should_cancel=cancelled.is_set)
        completed = False

        def next_event() -> tuple[str, dict[str, object]] | None:
            try:
                return next(iterator)
            except StopIteration:
                return None

        try:
            while True:
                if await request.is_disconnected():
                    cancelled.set()
                    return
                item = await asyncio.to_thread(next_event)
                if item is None or cancelled.is_set():
                    return
                event, data = item
                yield _sse(event, data)
                if event == "done":
                    completed = True
                    return
        finally:
            monitor_done.set()
            monitor.cancel()
            await asyncio.gather(monitor, return_exceptions=True)
            if not completed:
                cancelled.set()
                try:
                    await asyncio.to_thread(chat_service.cancel, actor, job.job_id)
                except Exception:
                    # The stream has already been disconnected; never expose an internal failure.
                    pass

    headers = {
        **context.response_headers,
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(events(), media_type="text/event-stream", headers=headers)


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
    return {
        "schema_version": "1.0",
        "citation": artifact.as_dict(),
        "preview": artifact.preview,
        "title": artifact.title,
        "filename": artifact.filename,
        "location": artifact.location,
    }


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
    filename = artifact.filename or f"citation-{citation_id}.bin"
    safe_filename = filename.replace("\r", "").replace("\n", "").replace("/", "").replace("\\", "")
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(safe_filename, safe='')}"
    }
    return RawResponse(
        content=artifact.download,
        media_type=artifact.mime_type or "application/octet-stream",
        headers=headers,
    )


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
