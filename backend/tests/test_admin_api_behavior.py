from __future__ import annotations

from uuid import UUID

import pytest

from backend.app.api import admin as admin_api
from backend.tests._admin_api_fixtures import (
    auth,
    key,
    prepare_review_two,
    publish,
    request,
    reset,
    upload,
)


@pytest.fixture(autouse=True)
def clean_state():
    reset()


def test_manager_provisions_inactive_employee():
    headers, _ = auth("website_manager")
    response = request("POST", "/api/v1/accounts", headers={**headers, **key()}, json={"email": "new@example.com", "password": "pw"})
    assert response.status_code == 201
    assert response.json()["active"] is False
    assert response.json()["roles"] == ["employee"]


def test_manager_activates_provisioned_account():
    headers, _ = auth("website_manager")
    created = request("POST", "/api/v1/accounts", headers={**headers, **key("create-account")}, json={"email": "activate@example.com", "password": "pw"})
    user_id = created.json()["user_id"]
    activated = request("POST", f"/api/v1/accounts/{user_id}/activate", headers={**headers, **key("activate-account")})
    assert activated.status_code == 200
    assert activated.json()["active"] is True


def test_manager_uploads_into_quarantine():
    headers, _ = auth("website_manager")
    response = upload(headers)
    assert response.status_code == 202
    assert response.json()["state"] == "QUEUED"
    assert response.json()["current_stage"] == "QUARANTINE"


def test_review_one_requires_clean_scan():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    response = request(
        "POST",
        f"/api/v1/documents/{uploaded['document_id']}/versions/{uploaded['version_id']}/approve",
        headers={**headers, **key("review-before-scan")},
        json={"stage": 1},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "SCAN_REQUIRED"


def test_second_review_is_separate_from_first_review():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = prepare_review_two(headers)
    record = admin_api.ingestion_service.get_version(version_id, admin_api._tenant_uuid(admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])))
    assert [approval.stage for approval in record.approvals] == [1]
    response = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/approve",
        headers={**headers, **key("review-two")},
        json={"stage": 2},
    )
    assert response.status_code == 200
    assert [item["stage"] for item in response.json()["approvals"]] == [1, 2]


def test_publish_requires_acknowledged_index():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    document_id, version_id = UUID(uploaded["document_id"]), UUID(uploaded["version_id"])
    principal = admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
    tenant_id = admin_api._tenant_uuid(principal)
    from backend.app.ingestion.lifecycle import ScanReport, ScanVerdict
    from backend.app.knowledge.models import ChunkMetadata, SourceSpan
    from uuid import uuid4

    admin_api.ingestion_service.scan(version_id, tenant_id, ScanReport(ScanVerdict.CLEAN))
    request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/approve", headers={**headers, **key("r1")}, json={"stage": 1})
    chunk = ChunkMetadata(chunk_id=uuid4(), document_id=document_id, version_id=version_id, tenant_id=tenant_id, chunk_index=0, source_span=SourceSpan(start=0, end=3), acl_policy_ref="acl", text_hash="c" * 64)
    admin_api.ingestion_service.process(version_id, tenant_id, (chunk,))
    request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/approve", headers={**headers, **key("r2")}, json={"stage": 2})
    response = request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/publish", headers={**headers, **key("publish-without-ack")}, json={})
    assert response.status_code == 409
    assert response.json()["code"] == "INDEX_NOT_ACKED"


def test_manager_completes_two_review_publication():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = publish(headers)
    response = request("GET", f"/api/v1/documents/{document_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["current_version_id"] == str(version_id)
    assert response.json()["status"] == "ACTIVE"


def test_version_history_is_available_to_manager():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    response = request("GET", f"/api/v1/documents/{document_id}/versions", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_soft_delete_removes_management_read():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    deleted = request("DELETE", f"/api/v1/documents/{document_id}", headers=headers)
    assert deleted.status_code == 204
    unavailable = request("GET", f"/api/v1/documents/{document_id}", headers=headers)
    assert unavailable.status_code == 404


def test_permanent_delete_honors_legal_hold():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    assert request("DELETE", f"/api/v1/documents/{document_id}", headers=headers).status_code == 204
    response = request("POST", f"/api/v1/documents/{document_id}/permanent-delete", headers={**headers, **key("legal-hold-delete")}, json={"retention_expired": True, "legal_hold": True})
    assert response.status_code == 409
    assert response.json()["code"] == "LEGAL_HOLD"
