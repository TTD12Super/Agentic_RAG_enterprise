"""Provider-neutral account and document administration boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated, Literal
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from fastapi import APIRouter, Header, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..authorization import (
    AccessGrant,
    Action,
    AuthorizationDenied,
    AuthorizationEvaluator,
    DocumentResource,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from ..identity import Role
from ..identity.errors import IdentityError
from ..identity.models import AuthenticatedPrincipal, DepartmentRecord, IdentityRecord, MFA_ROLES
from ..ingestion import (
    ApprovalBlocked,
    IngestionError,
    IngestionJob,
    IngestionService,
    InvalidInput,
    NotFound,
    PublicationBlocked,
    RetentionBlocked,
    UploadManifest,
)
from ..models.policy import DataClassification

router = APIRouter(tags=["administration"])
from . import identity as identity_api


class _RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserCreateRequest(_RequestModel):
    email: str = Field(min_length=3, max_length=320)
    password: str | None = Field(default=None, min_length=1, max_length=1024)
    temporary_password: str | None = Field(default=None, min_length=1, max_length=1024)
    roles: list[str] = Field(default_factory=lambda: [Role.EMPLOYEE.value], min_length=1)
    department_ids: list[str] = Field(default_factory=list)
    user_id: str | None = Field(default=None, min_length=1, max_length=128)
    mfa_code: str | None = Field(default=None, min_length=1, max_length=128)


class UserUpdateRequest(_RequestModel):
    active: bool | None = None
    roles: list[str] | None = None
    department_ids: list[str] | None = None


class DepartmentRequest(_RequestModel):
    name: str = Field(min_length=1, max_length=160)
    active: bool = True


class AccessGrantRequest(_RequestModel):
    action: Literal["document:read", "source:download"]
    effect: Literal["ALLOW", "DENY"]
    user_id: str | None = None
    role: str | None = None
    group: str | None = None
    department_id: str | None = None


class AccessRequest(_RequestModel):
    grants: list[AccessGrantRequest]


class UploadRequest(_RequestModel):
    document_id: UUID | None = None
    version_id: UUID | None = None
    version_number: int = Field(default=1, gt=0)
    title: str = Field(min_length=1, max_length=512)
    filename: str = Field(min_length=1, max_length=512)
    source_uri: str | None = Field(default=None, min_length=10, max_length=2048)
    sha256: str = Field(min_length=64, max_length=64)
    size_bytes: int = Field(default=1024, ge=0, le=200_000_000)
    mime_type: str | None = Field(default=None, min_length=1, max_length=256)
    classification: DataClassification
    owner_department_id: UUID | None = None
    magic_valid: bool = True


class ReviewRequest(_RequestModel):
    stage: Literal[1, 2]
    decision: Literal["APPROVE", "REJECT"] = "APPROVE"


class PermanentDeleteRequest(_RequestModel):
    retention_expired: bool = False
    legal_hold: bool = False


@dataclass
class AdminApiState:
    ingestion: IngestionService
    policy_store: InMemoryPolicyStore
    pep: PolicyEnforcementPoint
    document_grants: dict[tuple[str, str], tuple[AccessGrant, ...]]
    document_versions: dict[tuple[str, str], list[UUID]]
    idempotency: dict[tuple[str, str, str], tuple[str, str, dict[str, object]]]


policy_store = InMemoryPolicyStore(policy_epoch=1)
admin_state = AdminApiState(
    ingestion=IngestionService(audit_sink=identity_api.audit_sink),
    policy_store=policy_store,
    pep=PolicyEnforcementPoint(AuthorizationEvaluator(policy_store)),
    document_grants={},
    document_versions={},
    idempotency={},
)
ingestion_service = admin_state.ingestion
pep = admin_state.pep
identity_store = identity_api.identity_store
identity_service = identity_api.identity_service


def reset_state() -> None:
    """Reset only the provider-neutral in-memory admin boundary for tests."""

    global ingestion_service
    admin_state.ingestion = IngestionService(audit_sink=identity_api.audit_sink)
    admin_state.document_grants.clear()
    admin_state.document_versions.clear()
    admin_state.idempotency.clear()
    admin_state.policy_store.policy_epoch = 1
    admin_state.policy_store.grants.clear()
    admin_state.policy_store.revoked_principals.clear()
    admin_state.policy_store.available = True
    ingestion_service = admin_state.ingestion


def _problem(
    code: str,
    message: str,
    *,
    status_code: int = 400,
    retryable: bool = False,
) -> IdentityError:
    return IdentityError(code, status_code, message, retryable=retryable)


def _utc_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _tenant_uuid(tenant_id: str | AuthenticatedPrincipal) -> UUID:
    if isinstance(tenant_id, AuthenticatedPrincipal):
        tenant_id = tenant_id.tenant_id
    try:
        return UUID(tenant_id)
    except ValueError:
        return uuid5(NAMESPACE_URL, f"enterprise-agentic-rag:tenant:{tenant_id}")


def _stable_uuid(kind: str, value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError:
        return uuid5(NAMESPACE_URL, f"enterprise-agentic-rag:{kind}:{value}")


def _parse_uuid(value: str, *, label: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as error:
        raise _problem("REQUEST_INVALID", f"{label} is invalid.") from error


async def _body(
    request: Request, model: type[BaseModel], *, invalid_status: int = 400
) -> BaseModel:
    try:
        raw = await request.json()
        return model.model_validate(raw)
    except (ValueError, ValidationError) as error:
        raise _problem("REQUEST_INVALID", "The request is invalid.", status_code=invalid_status) from error


def _resolve(
    request: Request,
    response: Response,
    authorization: str | None,
    *,
    action: str,
) -> tuple[object, AuthenticatedPrincipal]:
    context = identity_api._request_context(request, response)
    try:
        principal = identity_api.identity_service.resolve_bearer(
            identity_api._bearer_token(authorization)
        )
    except IdentityError as error:
        identity_api._record_identity_error(context, error, action=action)
        raise
    return context, principal


def _require_manager(context: object, principal: AuthenticatedPrincipal, *, action: str) -> None:
    resource = DocumentResource(
        document_id=f"admin:{action}",
        tenant_id=principal.tenant_id,
        classification=DataClassification.PUBLIC.value,
        current_version_id="admin",
        version_id="admin",
    )
    try:
        admin_state.pep.enforce(principal, Action.DOCUMENT_UPDATE, resource)
    except AuthorizationDenied as error:
        if error.decision.reason_code == "POLICY_UNAVAILABLE":
            raise IdentityError(
                "AUTH_UNAVAILABLE",
                503,
                "Authorization is temporarily unavailable.",
                retryable=True,
            ) from error
        denied = _problem(
            "NOT_FOUND_OR_FORBIDDEN",
            "The requested administration action is not permitted.",
            status_code=404,
        )
        identity_api._record(
            context,  # type: ignore[arg-type]
            event="ADMIN_DENIED",
            action=action,
            outcome="DENY",
            decision="DENY",
            principal=principal,
            code=denied.code,
            metadata={"route": action, "status_code": denied.status_code},
        )
        raise denied from error


def _record_success(context: object, principal: AuthenticatedPrincipal, *, action: str, code: str) -> None:
    identity_api._record(
        context,  # type: ignore[arg-type]
        event="ADMIN_SUCCESS",
        action=action,
        outcome="SUCCESS",
        decision="ALLOW",
        principal=principal,
        code=code,
        metadata={"route": action, "status_code": 200},
    )


def _bump_policy_epoch() -> None:
    admin_state.policy_store.policy_epoch += 1


def _identity_payload(record: IdentityRecord) -> dict[str, object]:
    return {
        "user_id": record.user_id,
        "tenant_id": record.tenant_id,
        "email": record.email,
        "roles": list(record.roles),
        "department_ids": list(record.department_ids),
        "active": record.active,
    }


def _department_payload(record: DepartmentRecord) -> dict[str, object]:
    return {
        "department_id": record.department_id,
        "tenant_id": record.tenant_id,
        "name": record.name,
        "active": record.active,
    }


def _document_payload(document: object) -> dict[str, object]:
    return {
        "document_id": str(document.document_id),  # type: ignore[attr-defined]
        "title": document.title,  # type: ignore[attr-defined]
        "classification": document.classification.value,  # type: ignore[attr-defined]
        "status": document.status,  # type: ignore[attr-defined]
        "owner_department_id": (
            str(document.owner_department_id)  # type: ignore[attr-defined]
            if document.owner_department_id  # type: ignore[attr-defined]
            else None
        ),
        "current_version_id": (
            str(document.current_version_id)  # type: ignore[attr-defined]
            if document.current_version_id  # type: ignore[attr-defined]
            else None
        ),
    }


def _job_payload(job: IngestionJob) -> dict[str, object]:
    return {
        "job_id": str(job.job_id),
        "document_id": str(job.document_id),
        "version_id": str(job.version_id),
        "state": job.state.value,
        "current_stage": job.current_stage.value,
        "attempt": job.attempt,
        "error_code": job.error_code,
    }


def _version_payload(record: object) -> dict[str, object]:
    metadata = record.metadata  # type: ignore[attr-defined]
    return {
        "document_id": str(metadata.document_id),
        "version_id": str(metadata.version_id),
        "version_number": metadata.version_number,
        "status": metadata.status,
        "sha256": metadata.sha256,
        "source_uri": metadata.source_uri,
        "job_id": str(record.job_id),  # type: ignore[attr-defined]
        "approvals": [
            {
                "stage": approval.stage,
                "decision": approval.decision,
                "reviewer_id": str(approval.reviewer_id),
                "expires_at": _utc_z(approval.expires_at),
            }
            for approval in record.approvals  # type: ignore[attr-defined]
        ],
    }


def _document_resource(principal: AuthenticatedPrincipal, document_id: UUID) -> DocumentResource:
    try:
        document = admin_state.ingestion.get_document(document_id, _tenant_uuid(principal.tenant_id))
    except NotFound as error:
        raise _problem("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status_code=404) from error
    version = None
    if document.current_version_id is not None:
        try:
            version = admin_state.ingestion.get_version(
                document.current_version_id, _tenant_uuid(principal.tenant_id)
            )
        except NotFound:
            raise _problem("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status_code=404)
    return DocumentResource(
        document_id=str(document.document_id),
        tenant_id=principal.tenant_id,
        classification=document.classification.value,
        status=document.status,
        current_version_id=(str(document.current_version_id) if document.current_version_id else None),
        version_id=(str(version.metadata.version_id) if version else None),
        version_status=(version.metadata.status if version else "QUARANTINED"),
        owner_department_id=(str(document.owner_department_id) if document.owner_department_id else None),
        acl=admin_state.document_grants.get((principal.tenant_id, str(document_id)), ()),
    )


def _enforce_document(
    context: object,
    principal: AuthenticatedPrincipal,
    action: Action,
    document_id: UUID,
) -> DocumentResource:
    resource = _document_resource(principal, document_id)
    try:
        admin_state.pep.enforce(principal, action, resource)
    except AuthorizationDenied as error:
        if error.decision.reason_code == "POLICY_UNAVAILABLE":
            raise IdentityError(
                "AUTH_UNAVAILABLE",
                503,
                "Authorization is temporarily unavailable.",
                retryable=True,
            ) from error
        denied = _problem(
            "NOT_FOUND_OR_FORBIDDEN",
            "The requested administration action is not permitted.",
            status_code=404,
        )
        identity_api._record(
            context,  # type: ignore[arg-type]
            event="ADMIN_DENIED",
            action=action.value,
            outcome="DENY",
            decision="DENY",
            principal=principal,
            code=denied.code,
            metadata={"route": action.value, "status_code": denied.status_code},
        )
        raise denied from error
    except Exception as error:
        raise IdentityError(
            "AUTH_UNAVAILABLE",
            503,
            "Authorization is temporarily unavailable.",
            retryable=True,
        ) from error
    return resource


def _raise_ingestion(error: IngestionError) -> None:
    if isinstance(error, NotFound):
        status = 404
        code = "NOT_FOUND_OR_FORBIDDEN"
    elif isinstance(error, (InvalidInput,)):
        status = 400
        code = error.code
    elif isinstance(error, (RetentionBlocked,)):
        status = 409
        code = error.code
    elif error.retryable:
        status = 503
        code = error.code
    else:
        status = 409
        code = error.code
    raise _problem(code, error.message, status_code=status, retryable=error.retryable) from error


def _grant_payload(grant: AccessGrant) -> dict[str, object]:
    return {
        "action": grant.action,
        "effect": grant.effect,
        "user_id": grant.user_id,
        "role": grant.role,
        "group": grant.group,
        "department_id": grant.department_id,
    }


def _dashboard_metric(
    value: object,
    *,
    unit: str,
    provenance: str,
    measurement_period: dict[str, str],
    available: bool = True,
    is_estimate: bool = False,
    reason: str | None = None,
) -> dict[str, object]:
    metric = {
        "value": value,
        "unit": unit,
        "status": "MEASURED" if available else "UNAVAILABLE",
        "available": available,
        "is_estimate": is_estimate,
        "provenance": provenance,
        "measurement_period": measurement_period,
    }
    if reason is not None:
        metric["reason"] = reason
    return metric


def _unavailable_metric(
    *,
    unit: str,
    provenance: str,
    measurement_period: dict[str, str],
    reason: str,
) -> dict[str, object]:
    return _dashboard_metric(
        None,
        unit=unit,
        provenance=provenance,
        measurement_period=measurement_period,
        available=False,
        reason=reason,
    )


def _counts(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _dashboard_metrics(principal: AuthenticatedPrincipal) -> dict[str, object]:
    now = datetime.now(timezone.utc)
    measurement_period = {
        "label": "request_snapshot",
        "start": _utc_z(now),
        "end": _utc_z(now),
    }

    users = identity_store.find_all(principal.tenant_id)
    metrics: dict[str, object] = {
        "users": _dashboard_metric(
            {
                "total": len(users),
                "active": sum(record.active for record in users),
                "by_role": _counts([role for record in users for role in record.roles]),
            },
            unit="users",
            provenance="identity_store",
            measurement_period=measurement_period,
        )
    }

    tenant_uuid = _tenant_uuid(principal.tenant_id)
    documents = []
    ingestion_jobs = []
    for tenant_id, document_id in admin_state.document_versions:
        if tenant_id != principal.tenant_id:
            continue
        try:
            document = admin_state.ingestion.get_document(UUID(document_id), tenant_uuid)
        except IngestionError:
            continue
        documents.append(document)
        for version_id in admin_state.document_versions[(tenant_id, document_id)]:
            try:
                version = admin_state.ingestion.get_version(version_id, tenant_uuid)
                ingestion_jobs.append(admin_state.ingestion.get_job(version.job_id, tenant_uuid))
            except IngestionError:
                continue
    metrics["documents"] = _dashboard_metric(
        {
            "total": len(documents),
            "by_status": _counts([str(document.status) for document in documents]),
            "current_versions": sum(document.current_version_id is not None for document in documents),
        },
        unit="documents",
        provenance="admin_state + ingestion.lifecycle",
        measurement_period=measurement_period,
    )

    try:
        from ..core.chat import JobState
        from . import chat as chat_api

        chat_jobs = chat_api.chat_service.repository.jobs_for_tenant(
            principal.tenant_id,
            states=set(JobState),
        )
        metrics["usage"] = _dashboard_metric(
            {
                "requests": len(chat_jobs),
                "by_state": _counts([str(job.state) for job in chat_jobs]),
            },
            unit="requests",
            provenance="chat.repository",
            measurement_period=measurement_period,
        )
        metrics["cache_hit_rate"] = _unavailable_metric(
            unit="ratio",
            provenance="cache.telemetry",
            measurement_period=measurement_period,
            reason="CACHE_TELEMETRY_UNAVAILABLE",
        )
    except Exception:
        metrics["usage"] = _unavailable_metric(
            unit="requests",
            provenance="chat.repository",
            measurement_period=measurement_period,
            reason="USAGE_PROVIDER_UNAVAILABLE",
        )
        metrics["cache_hit_rate"] = _unavailable_metric(
            unit="ratio",
            provenance="cache.telemetry",
            measurement_period=measurement_period,
            reason="CACHE_TELEMETRY_UNAVAILABLE",
        )

    metrics["ingestion"] = _dashboard_metric(
        {
            "jobs": len(ingestion_jobs),
            "by_state": _counts([str(job.state) for job in ingestion_jobs]),
            "failed": sum(str(job.state) == "FAILED" for job in ingestion_jobs),
        },
        unit="jobs",
        provenance="admin_state + ingestion.lifecycle",
        measurement_period=measurement_period,
    )

    metrics["latency"] = _unavailable_metric(
        unit="milliseconds",
        provenance="observability.telemetry",
        measurement_period=measurement_period,
        reason="LATENCY_TELEMETRY_UNAVAILABLE",
    )
    metrics["cost"] = _unavailable_metric(
        unit="USD",
        provenance="provider.telemetry",
        measurement_period=measurement_period,
        reason="PROVIDER_COST_UNAVAILABLE",
    )
    metrics["evaluation"] = _unavailable_metric(
        unit="score",
        provenance="evaluation.provider",
        measurement_period=measurement_period,
        reason="EVALUATION_UNAVAILABLE",
    )
    return metrics


@router.get("/dashboard")
async def get_dashboard(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:dashboard:read")
    _require_manager(context, principal, action="admin:dashboard:read")
    _record_success(context, principal, action="admin:dashboard:read", code="DASHBOARD_READ")
    return {"schema_version": "1.0", **_dashboard_metrics(principal)}


@router.get("/documents")
async def list_documents(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=10_000),
) -> dict[str, object]:
    """Return a policy-filtered document catalog for the real UI boundary."""

    context, principal = _resolve(request, response, authorization, action="admin:document:list")
    management = bool({Role.SYSTEM_ADMIN.value, Role.WEBSITE_MANAGER.value} & set(principal.roles))
    tenant_uuid = _tenant_uuid(principal.tenant_id)
    documents: list[dict[str, object]] = []
    seen: set[str] = set()
    for tenant_id, document_id in sorted(admin_state.document_versions):
        if tenant_id != principal.tenant_id or document_id in seen:
            continue
        seen.add(document_id)
        try:
            document = admin_state.ingestion.get_document(UUID(document_id), tenant_uuid)
        except IngestionError:
            continue
        if not management:
            if document.status != "ACTIVE" or document.current_version_id is None:
                continue
            try:
                _enforce_document(context, principal, Action.DOCUMENT_READ, UUID(document_id))
            except IdentityError as error:
                if error.code == "AUTH_UNAVAILABLE":
                    raise
                continue
        documents.append(_document_payload(document))
    page = documents[offset : offset + limit]
    _record_success(context, principal, action="admin:document:list", code="DOCUMENTS_LISTED")
    return {
        "schema_version": "1.0",
        "items": page,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": len(documents),
            "has_more": offset + len(page) < len(documents),
        },
    }


@router.get("/approvals")
@router.get("/documents/approval-queue")
async def list_approval_queue(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=10_000),
) -> dict[str, object]:
    """Expose review work without exposing source content."""

    context, principal = _resolve(request, response, authorization, action="admin:approval:list")
    _require_manager(context, principal, action="admin:approval:list")
    tenant_uuid = _tenant_uuid(principal.tenant_id)
    items: list[dict[str, object]] = []
    for tenant_id, document_id in sorted(admin_state.document_versions):
        if tenant_id != principal.tenant_id:
            continue
        for version_id in admin_state.document_versions[(tenant_id, document_id)]:
            try:
                version = admin_state.ingestion.get_version(version_id, tenant_uuid)
            except IngestionError:
                continue
            if version.metadata.status not in {"QUARANTINED", "PENDING_REVIEW_2"}:
                continue
            items.append(_version_payload(version))
    page = items[offset : offset + limit]
    _record_success(context, principal, action="admin:approval:list", code="APPROVALS_LISTED")
    return {
        "schema_version": "1.0",
        "items": page,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": len(items),
            "has_more": offset + len(page) < len(items),
        },
    }


@router.get("/audit")
async def list_audit_events(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=10_000),
) -> dict[str, object]:
    """Return metadata-only audit events; conversation bodies never enter this path."""

    context, principal = _resolve(request, response, authorization, action="admin:audit:read")
    _require_manager(context, principal, action="admin:audit:read")
    sink = identity_api.audit_sink
    list_events = getattr(sink, "list_events", None)
    if callable(list_events):
        items = list(list_events(tenant_id=principal.tenant_id, limit=limit, offset=offset))
        count_events = getattr(sink, "count_events", None)
        total = int(count_events(tenant_id=principal.tenant_id)) if callable(count_events) else offset + len(items) + (1 if len(items) == limit else 0)
    else:
        events = [event.as_dict() for event in getattr(sink, "events", ()) if event.tenant_id == principal.tenant_id]
        total = len(events)
        items = events[offset : offset + limit]
    _record_success(context, principal, action="admin:audit:read", code="AUDIT_READ")
    return {
        "schema_version": "1.0",
        "items": items,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": offset + len(items) < total,
        },
    }


@router.get("/feedback/review")
@router.get("/feedback")
async def review_feedback(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=10_000),
    rating: str | None = Query(default=None, min_length=1, max_length=8),
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:feedback:review")
    _require_manager(context, principal, action="admin:feedback:review")
    normalized_rating = rating.strip().upper() if rating is not None else None
    if normalized_rating is not None and normalized_rating not in {"POSITIVE", "NEGATIVE"}:
        raise _problem("REQUEST_INVALID", "The request is invalid.")
    from . import chat as chat_api

    records, total = chat_api.feedback_service.review(
        tenant_id=principal.tenant_id,
        limit=limit,
        offset=offset,
        rating=normalized_rating,
    )
    _record_success(context, principal, action="admin:feedback:review", code="FEEDBACK_REVIEWED")
    return {
        "schema_version": "1.0",
        "items": [
            {
                "feedback_id": record.feedback_id,
                "answer_id": record.answer_id,
                "rating": record.rating,
                "created_at": _utc_z(record.created_at),
            }
            for record in records
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": offset + len(records) < total,
        },
        "filter": {"rating": normalized_rating},
    }


@router.get("/users")
@router.get("/accounts")
async def list_users(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:user:list")
    _require_manager(context, principal, action="admin:user:list")
    return {"users": [_identity_payload(record) for record in identity_api.identity_store.find_all(principal.tenant_id)]}


@router.post("/users", status_code=201)
@router.post("/accounts", status_code=201)
async def create_user(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    if not idempotency_key or not idempotency_key.strip():
        raise _problem("REQUEST_INVALID", "The request is invalid.")
    context, principal = _resolve(request, response, authorization, action="admin:user:create")
    _require_manager(context, principal, action="admin:user:create")
    body = await _body(request, UserCreateRequest)
    if Role.SYSTEM_ADMIN.value in body.roles and Role.SYSTEM_ADMIN.value not in principal.roles:
        raise _problem("NOT_FOUND_OR_FORBIDDEN", "The requested administration action is not permitted.", status_code=403)
    if set(body.roles) & MFA_ROLES and not body.mfa_code:
        raise _problem("MFA_REQUIRED", "Privileged accounts require MFA enrollment.")
    if identity_api.identity_store.find_by_email(body.email.strip().lower()) is not None:
        raise _problem("REQUEST_INVALID", "The request is invalid.")
    user_id = body.user_id or f"user-{uuid4()}"
    if any(record.user_id == user_id for record in identity_api.identity_store.find_all(principal.tenant_id)):
        raise _problem("REQUEST_INVALID", "The request is invalid.")
    password = body.password or body.temporary_password
    if password is None:
        raise _problem("REQUEST_INVALID", "The request is invalid.")
    try:
        record = identity_api.identity_store.add_identity(
            user_id=user_id,
            tenant_id=principal.tenant_id,
            email=body.email,
            password=password,
            roles=body.roles,
            department_ids=body.department_ids,
            mfa_code=body.mfa_code,
            active=False,
        )
    except ValueError as error:
        raise _problem("REQUEST_INVALID", "The request is invalid.") from error
    _record_success(context, principal, action="admin:user:create", code="USER_CREATED")
    return _identity_payload(record)


@router.patch("/users/{user_id}")
@router.patch("/accounts/{user_id}")
async def update_user(
    user_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:user:update")
    _require_manager(context, principal, action="admin:user:update")
    body = await _body(request, UserUpdateRequest)
    if not body.model_fields_set:
        raise _problem("REQUEST_INVALID", "The request is invalid.")
    if body.roles and Role.SYSTEM_ADMIN.value in body.roles and Role.SYSTEM_ADMIN.value not in principal.roles:
        raise _problem("NOT_FOUND_OR_FORBIDDEN", "The requested administration action is not permitted.", status_code=403)
    record = identity_api.identity_store.update_identity(
        user_id=user_id,
        tenant_id=principal.tenant_id,
        roles=body.roles,
        department_ids=body.department_ids,
        active=body.active,
    )
    if record is None:
        raise _problem("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status_code=404)
    if record.active:
        admin_state.policy_store.revoked_principals.discard((principal.tenant_id, record.user_id))
    else:
        admin_state.policy_store.revoked_principals.add((principal.tenant_id, record.user_id))
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:user:update", code="USER_UPDATED")
    return {"user": _identity_payload(record)}


@router.post("/users/{user_id}/activate")
@router.post("/accounts/{user_id}/activate")
async def activate_user(
    user_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:user:activate")
    _require_manager(context, principal, action="admin:user:activate")
    if not idempotency_key or not idempotency_key.strip():
        raise _problem("REQUEST_INVALID", "The request is invalid.")
    record = identity_api.identity_store.update_identity(
        user_id=user_id, tenant_id=principal.tenant_id, active=True
    )
    if record is None:
        raise _problem("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status_code=404)
    admin_state.policy_store.revoked_principals.discard((principal.tenant_id, record.user_id))
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:user:activate", code="USER_ACTIVATED")
    return _identity_payload(record)


@router.get("/departments")
async def list_departments(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:department:list")
    _require_manager(context, principal, action="admin:department:list")
    return {
        "departments": [
            _department_payload(record)
            for record in identity_api.identity_store.list_departments(principal.tenant_id)
        ]
    }


@router.post("/departments", status_code=201)
async def create_department(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:department:create")
    _require_manager(context, principal, action="admin:department:create")
    body = await _body(request, DepartmentRequest)
    department = identity_api.identity_store.create_department(
        tenant_id=principal.tenant_id,
        department_id=str(uuid4()),
        name=body.name,
    )
    if not body.active:
        department = identity_api.identity_store.update_department(
            tenant_id=principal.tenant_id, department_id=department.department_id, active=False
        ) or department
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:department:create", code="DEPARTMENT_CREATED")
    return {"department": _department_payload(department)}


@router.patch("/departments/{department_id}")
async def update_department(
    department_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:department:update")
    _require_manager(context, principal, action="admin:department:update")
    body = await _body(request, DepartmentRequest)
    department = identity_api.identity_store.update_department(
        tenant_id=principal.tenant_id,
        department_id=department_id,
        name=body.name,
        active=body.active,
    )
    if department is None:
        raise _problem("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status_code=404)
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:department:update", code="DEPARTMENT_UPDATED")
    return {"department": _department_payload(department)}


@router.post("/documents/{document_id}/access")
@router.put("/documents/{document_id}/access")
async def update_document_access(
    document_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:document:access")
    _require_manager(context, principal, action="admin:document:access")
    if not idempotency_key or not idempotency_key.strip():
        raise _problem("IDEMPOTENCY_REQUIRED", "An idempotency key is required.")
    parsed_document_id = _parse_uuid(document_id, label="document_id")
    _enforce_document(context, principal, Action.DOCUMENT_UPDATE, parsed_document_id)
    body = await _body(request, AccessRequest)
    grants: list[AccessGrant] = []
    try:
        for item in body.grants:
            grants.append(
                AccessGrant(
                    action=item.action,
                    effect=item.effect,
                    tenant_id=principal.tenant_id,
                    user_id=item.user_id,
                    role=item.role,
                    group=item.group,
                    department_id=item.department_id,
                )
            )
    except ValueError as error:
        raise _problem("REQUEST_INVALID", "The request is invalid.") from error
    admin_state.document_grants[(principal.tenant_id, str(parsed_document_id))] = tuple(grants)
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:document:access", code="DOCUMENT_ACCESS_UPDATED")
    return {"document_id": document_id, "grants": [_grant_payload(grant) for grant in grants]}


@router.post("/documents", status_code=202)
async def upload_document(
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:document:create")
    _require_manager(context, principal, action="admin:document:create")
    if not idempotency_key or not idempotency_key.strip():
        raise _problem("IDEMPOTENCY_REQUIRED", "An idempotency key is required.")
    body = await _body(request, UploadRequest)
    try:
        document_id = body.document_id or uuid4()
        version_id = body.version_id or uuid4()
        extension = body.filename.rsplit(".", 1)[-1].lower() if "." in body.filename else ""
        mime_type = body.mime_type or {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }.get(extension, "application/octet-stream")
        manifest = UploadManifest(
            tenant_id=_tenant_uuid(principal.tenant_id),
            document_id=document_id,
            version_id=version_id,
            version_number=body.version_number,
            title=body.title,
            filename=body.filename,
            source_uri=body.source_uri or f"private://documents/{document_id}/{version_id}",
            sha256=body.sha256,
            size_bytes=body.size_bytes,
            mime_type=mime_type,
            classification=body.classification,
            owner_department_id=body.owner_department_id,
            magic_valid=body.magic_valid,
        )
        job = admin_state.ingestion.quarantine_upload(manifest, idempotency_key=idempotency_key)
        versions = admin_state.document_versions.setdefault(
            (principal.tenant_id, str(document_id)), []
        )
        if version_id not in versions:
            versions.append(version_id)
    except ValueError as error:
        raise _problem("REQUEST_INVALID", "The request is invalid.") from error
    except IngestionError as error:
        _raise_ingestion(error)
    _record_success(context, principal, action="admin:document:create", code="DOCUMENT_QUARANTINED")
    return _job_payload(job)


@router.get("/ingestion-jobs/{job_id}")
async def get_ingestion_job(
    job_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:ingestion:read")
    _require_manager(context, principal, action="admin:ingestion:read")
    parsed_job_id = _parse_uuid(job_id, label="job_id")
    try:
        job = admin_state.ingestion.get_job(parsed_job_id, _tenant_uuid(principal.tenant_id))
    except IngestionError as error:
        _raise_ingestion(error)
    return _job_payload(job)


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:document:read")
    _require_manager(context, principal, action="admin:document:read")
    parsed_document_id = _parse_uuid(document_id, label="document_id")
    try:
        document = admin_state.ingestion.get_document(parsed_document_id, _tenant_uuid(principal.tenant_id))
    except IngestionError as error:
        _raise_ingestion(error)
    if document.status != "ACTIVE" or document.current_version_id is None:
        raise _problem("NOT_FOUND_OR_FORBIDDEN", "The requested resource is unavailable.", status_code=404)
    return _document_payload(document)


@router.get("/documents/{document_id}/versions")
async def list_document_versions(
    document_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> list[dict[str, object]]:
    context, principal = _resolve(request, response, authorization, action="admin:document:versions")
    _require_manager(context, principal, action="admin:document:versions")
    parsed_document_id = _parse_uuid(document_id, label="document_id")
    try:
        admin_state.ingestion.get_document(parsed_document_id, _tenant_uuid(principal.tenant_id))
    except IngestionError as error:
        _raise_ingestion(error)
    records: list[dict[str, object]] = []
    for version_id in admin_state.document_versions.get((principal.tenant_id, document_id), []):
        try:
            version = admin_state.ingestion.get_version(version_id, _tenant_uuid(principal.tenant_id))
        except NotFound:
            continue
        records.append(_version_payload(version))
    return records


@router.post("/documents/{document_id}/versions/{version_id}/approve")
async def approve_document_version(
    document_id: str,
    version_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:document:approve")
    _require_manager(context, principal, action="admin:document:approve")
    if not idempotency_key or not idempotency_key.strip():
        raise _problem("IDEMPOTENCY_REQUIRED", "An idempotency key is required.")
    parsed_document_id = _parse_uuid(document_id, label="document_id")
    parsed_version_id = _parse_uuid(version_id, label="version_id")
    _enforce_document(context, principal, Action.DOCUMENT_APPROVE, parsed_document_id)
    body = await _body(request, ReviewRequest, invalid_status=422)
    try:
        version = admin_state.ingestion.get_version(parsed_version_id, _tenant_uuid(principal.tenant_id))
        if version.metadata.document_id != parsed_document_id:
            raise NotFound("VERSION_NOT_FOUND", "document version is unavailable")
        if body.decision == "REJECT":
            version = admin_state.ingestion.reject_review(
                parsed_version_id,
                _tenant_uuid(principal.tenant_id),
                _stable_uuid("user", principal.user_id),
                stage=body.stage,
                idempotency_key=idempotency_key,
            )
        elif body.stage == 1:
            version = admin_state.ingestion.approve_review1(
                parsed_version_id,
                _tenant_uuid(principal.tenant_id),
                _stable_uuid("user", principal.user_id),
                idempotency_key=idempotency_key,
            )
        else:
            version = admin_state.ingestion.approve_review2(
                parsed_version_id,
                _tenant_uuid(principal.tenant_id),
                _stable_uuid("user", principal.user_id),
                idempotency_key=idempotency_key,
            )
    except IngestionError as error:
        _raise_ingestion(error)
    _record_success(context, principal, action="admin:document:approve", code="DOCUMENT_REVIEW_RECORDED")
    return _version_payload(version)


@router.post("/documents/{document_id}/versions/{version_id}/publish")
async def publish_document_version(
    document_id: str,
    version_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:document:publish")
    _require_manager(context, principal, action="admin:document:publish")
    if not idempotency_key or not idempotency_key.strip():
        raise _problem("IDEMPOTENCY_REQUIRED", "An idempotency key is required.")
    parsed_document_id = _parse_uuid(document_id, label="document_id")
    parsed_version_id = _parse_uuid(version_id, label="version_id")
    idempotency_entry = admin_state.idempotency.get(
        (principal.tenant_id, "document:publish", idempotency_key)
    )
    if idempotency_entry is not None:
        if idempotency_entry[:2] != (document_id, version_id):
            raise _problem("IDEMPOTENCY_KEY_REUSED", "The idempotency key was already used.", status_code=409)
        return dict(idempotency_entry[2])
    _enforce_document(context, principal, Action.DOCUMENT_PUBLISH, parsed_document_id)
    try:
        version = admin_state.ingestion.get_version(parsed_version_id, _tenant_uuid(principal.tenant_id))
        if version.metadata.document_id != parsed_document_id:
            raise NotFound("VERSION_NOT_FOUND", "document version is unavailable")
        version = admin_state.ingestion.publish(parsed_version_id, _tenant_uuid(principal.tenant_id))
    except IngestionError as error:
        _raise_ingestion(error)
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:document:publish", code="DOCUMENT_PUBLISHED")
    payload = _version_payload(version)
    admin_state.idempotency[(principal.tenant_id, "document:publish", idempotency_key)] = (
        document_id,
        version_id,
        payload,
    )
    return payload


@router.post("/documents/{document_id}/versions/{version_id}/revoke")
async def revoke_document_version(
    document_id: str,
    version_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    context, principal = _resolve(request, response, authorization, action="admin:document:revoke")
    _require_manager(context, principal, action="admin:document:revoke")
    if not idempotency_key or not idempotency_key.strip():
        raise _problem("IDEMPOTENCY_REQUIRED", "An idempotency key is required.")
    parsed_document_id = _parse_uuid(document_id, label="document_id")
    parsed_version_id = _parse_uuid(version_id, label="version_id")
    _enforce_document(context, principal, Action.DOCUMENT_DELETE, parsed_document_id)
    try:
        version = admin_state.ingestion.get_version(parsed_version_id, _tenant_uuid(principal.tenant_id))
        if version.metadata.document_id != parsed_document_id:
            raise NotFound("VERSION_NOT_FOUND", "document version is unavailable")
        version = admin_state.ingestion.revoke_version(parsed_version_id, _tenant_uuid(principal.tenant_id))
    except IngestionError as error:
        _raise_ingestion(error)
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:document:revoke", code="DOCUMENT_VERSION_REVOKED")
    return _version_payload(version)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    context, principal = _resolve(request, response, authorization, action="admin:document:delete")
    _require_manager(context, principal, action="admin:document:delete")
    parsed_document_id = _parse_uuid(document_id, label="document_id")
    _enforce_document(context, principal, Action.DOCUMENT_DELETE, parsed_document_id)
    try:
        document = admin_state.ingestion.soft_delete_document(
            parsed_document_id, _tenant_uuid(principal.tenant_id)
        )
    except IngestionError as error:
        _raise_ingestion(error)
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:document:delete", code="DOCUMENT_SOFT_DELETED")


@router.post("/documents/{document_id}/permanent-delete", status_code=204)
async def permanently_delete_document(
    document_id: str,
    request: Request,
    response: Response,
    authorization: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> None:
    context, principal = _resolve(request, response, authorization, action="admin:document:permanent-delete")
    _require_manager(context, principal, action="admin:document:permanent-delete")
    if not idempotency_key or not idempotency_key.strip():
        raise _problem("IDEMPOTENCY_REQUIRED", "An idempotency key is required.")
    parsed_document_id = _parse_uuid(document_id, label="document_id")
    body = await _body(request, PermanentDeleteRequest)
    try:
        admin_state.ingestion.permanently_delete_document(
            parsed_document_id,
            _tenant_uuid(principal.tenant_id),
            retention_expired=body.retention_expired,
            legal_hold=body.legal_hold,
        )
    except IngestionError as error:
        _raise_ingestion(error)
    admin_state.document_versions.pop((principal.tenant_id, document_id), None)
    admin_state.document_grants.pop((principal.tenant_id, document_id), None)
    _bump_policy_epoch()
    _record_success(context, principal, action="admin:document:permanent-delete", code="DOCUMENT_PERMANENTLY_DELETED")
