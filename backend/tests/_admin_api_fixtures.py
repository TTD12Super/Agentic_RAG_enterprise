"""Deterministic HTTP and lifecycle fixtures for ADMIN-API-001 tests."""

from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

import httpx

from backend.app.api import admin as admin_api
from backend.app.api import identity as identity_api
from backend.app.ingestion.lifecycle import ScanReport, ScanVerdict, StagedIndex
from backend.app.knowledge.models import ChunkMetadata, SourceSpan
from backend.app.main import app
from backend.app.observability import InMemoryAuditSink


TENANT = "tenant-admin-tests"


def reset() -> None:
    admin_api.reset_state()
    identity_api.audit_sink = InMemoryAuditSink()


def add_user(role: str, *, tenant: str = TENANT, department_ids: tuple[str, ...] = ()) -> tuple[str, str]:
    suffix = uuid4().hex
    email = f"{role}-{suffix}@example.com"
    user_id = f"{role}-{suffix}"
    identity_api.identity_store.add_identity(
        user_id=user_id,
        tenant_id=tenant,
        email=email,
        password="correct-password",
        roles=[role],
        department_ids=department_ids,
        mfa_code="123456" if role in {"system_admin", "website_manager", "chairman"} else None,
    )
    return email, user_id


def auth(role: str, *, tenant: str = TENANT) -> tuple[dict[str, str], str]:
    email, user_id = add_user(role, tenant=tenant)
    response = request(
        "POST",
        "/api/v1/auth/sign-in",
        json={
            "email": email,
            "password": "correct-password",
            **({"mfa_code": "123456"} if role in {"system_admin", "website_manager", "chairman"} else {}),
        },
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}, user_id


def request(method: str, path: str, **kwargs: object) -> httpx.Response:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(run())


def key(value: str = "admin-api-test-key") -> dict[str, str]:
    return {"Idempotency-Key": value.ljust(16, "-")}


def upload(headers: dict[str, str], *, classification: str = "PUBLIC") -> httpx.Response:
    return request(
        "POST",
        "/api/v1/documents",
        headers={**headers, **key("upload-" + uuid4().hex[:12])},
        json={
            "title": "Synthetic administration document",
            "filename": "admin.pdf",
            "sha256": "a" * 64,
            "classification": classification,
            "owner_department_id": "11111111-1111-1111-1111-111111111111" if classification == "INTERNAL" else None,
        },
    )


def prepare_review_two(headers: dict[str, str]) -> tuple[UUID, UUID, UUID]:
    response = upload(headers)
    assert response.status_code == 202, response.text
    payload = response.json()
    document_id, version_id, job_id = map(UUID, (payload["document_id"], payload["version_id"], payload["job_id"]))
    principal = identity_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
    tenant_id = admin_api._tenant_uuid(principal)
    admin_api.ingestion_service.scan(version_id, tenant_id, ScanReport(ScanVerdict.CLEAN))
    review_1 = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/approve",
        headers={**headers, **key("review-1-" + uuid4().hex[:10])},
        json={"stage": 1},
    )
    assert review_1.status_code == 200, review_1.text
    chunk = ChunkMetadata(
        chunk_id=uuid4(),
        document_id=document_id,
        version_id=version_id,
        tenant_id=tenant_id,
        chunk_index=0,
        source_span=SourceSpan(start=0, end=10),
        acl_policy_ref="acl-synthetic",
        text_hash="b" * 64,
    )
    admin_api.ingestion_service.process(version_id, tenant_id, (chunk,))
    staged = StagedIndex.from_chunks(
        publication_id="publication-" + uuid4().hex,
        tenant_id=tenant_id,
        version_id=version_id,
        content_sha256="a" * 64,
        chunks=(chunk,),
    )
    admin_api.ingestion_service.stage_index(version_id, tenant_id, staged)
    admin_api.ingestion_service.acknowledge_index(version_id, tenant_id)
    return document_id, version_id, job_id


def publish(headers: dict[str, str]) -> tuple[UUID, UUID, UUID]:
    document_id, version_id, job_id = prepare_review_two(headers)
    review_2 = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/approve",
        headers={**headers, **key("review-2-" + uuid4().hex[:10])},
        json={"stage": 2},
    )
    assert review_2.status_code == 200, review_2.text
    published = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/publish",
        headers={**headers, **key("publish-" + uuid4().hex[:10])},
        json={},
    )
    assert published.status_code == 200, published.text
    return document_id, version_id, job_id
