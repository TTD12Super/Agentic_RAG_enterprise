from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from backend.app.api import admin as admin_api
from backend.app.ingestion.lifecycle import ScanReport, ScanVerdict
from backend.app.knowledge.models import ChunkMetadata, SourceSpan
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


def _prepare_review_two_without_index_ack(headers: dict[str, str]) -> tuple[UUID, UUID]:
    uploaded = upload(headers)
    assert uploaded.status_code == 202, uploaded.text
    payload = uploaded.json()
    document_id, version_id = map(UUID, (payload["document_id"], payload["version_id"]))
    principal = admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
    tenant_id = admin_api._tenant_uuid(principal)
    admin_api.ingestion_service.scan(version_id, tenant_id, ScanReport(ScanVerdict.CLEAN))
    review_1 = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/approve",
        headers={**headers, **key("behavior-r1")},
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
    review_2 = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/approve",
        headers={**headers, **key("behavior-r2")},
        json={"stage": 2},
    )
    assert review_2.status_code == 200, review_2.text
    return document_id, version_id


def test_manager_provisions_inactive_employee():
    headers, _ = auth("website_manager")
    email = f"new-{uuid4().hex}@example.com"
    response = request(
        "POST",
        "/api/v1/accounts",
        headers={**headers, **key("behavior-create")},
        json={"email": email, "password": "pw"},
    )
    assert response.status_code == 201
    assert response.json()["active"] is False
    assert response.json()["roles"] == ["employee"]


def test_manager_activates_provisioned_account():
    headers, _ = auth("website_manager")
    email = f"activate-{uuid4().hex}@example.com"
    created = request(
        "POST",
        "/api/v1/accounts",
        headers={**headers, **key("behavior-activate-create")},
        json={"email": email, "password": "pw"},
    )
    assert created.status_code == 201
    user_id = created.json()["user_id"]
    activated = request(
        "POST",
        f"/api/v1/accounts/{user_id}/activate",
        headers={**headers, **key("behavior-activate")},
    )
    assert activated.status_code == 200
    assert activated.json()["active"] is True
    assert request("POST", "/api/v1/auth/sign-in", json={"email": email, "password": "pw"}).status_code == 200


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
        headers={**headers, **key("behavior-before-scan")},
        json={"stage": 1},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "SCAN_REQUIRED"


def test_second_review_is_recorded_separately():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = prepare_review_two(headers)
    record = admin_api.ingestion_service.get_version(
        version_id,
        admin_api._tenant_uuid(
            admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
        ),
    )
    assert [approval.stage for approval in record.approvals] == [1]
    response = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/approve",
        headers={**headers, **key("behavior-review-two")},
        json={"stage": 2},
    )
    assert response.status_code == 200
    assert [item["stage"] for item in response.json()["approvals"]] == [1, 2]


def test_publish_requires_acknowledged_index():
    headers, _ = auth("website_manager")
    document_id, version_id = _prepare_review_two_without_index_ack(headers)
    response = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/publish",
        headers={**headers, **key("behavior-publish-without-ack")},
        json={},
    )
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
    assert response.json()[0]["source_uri"].startswith("private://")


def test_quarantined_document_is_not_readable():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    response = request("GET", f"/api/v1/documents/{uploaded['document_id']}", headers=headers)
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_soft_delete_removes_management_read():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    deleted = request("DELETE", f"/api/v1/documents/{document_id}", headers=headers)
    assert deleted.status_code == 204
    unavailable = request("GET", f"/api/v1/documents/{document_id}", headers=headers)
    assert unavailable.status_code == 404
