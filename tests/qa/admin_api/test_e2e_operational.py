from __future__ import annotations

from uuid import uuid4

import pytest

from backend.app.api import admin as admin_api
from backend.app.api import identity as identity_api
from backend.tests._admin_api_fixtures import (
    auth,
    key,
    prepare_review_two,
    publish,
    request,
    reset,
)


@pytest.fixture(autouse=True)
def clean_state():
    reset()


def test_manager_completes_http_lifecycle_with_worker_boundary():
    headers, _ = auth("website_manager")
    document_id, version_id, job_id = publish(headers)
    document = request("GET", f"/api/v1/documents/{document_id}", headers=headers)
    assert document.status_code == 200
    assert document.json()["current_version_id"] == str(version_id)
    job = request("GET", f"/api/v1/ingestion-jobs/{job_id}", headers=headers)
    assert job.status_code == 200
    assert job.json()["version_id"] == str(version_id)


def test_activation_allows_follow_up_sign_in():
    headers, _ = auth("website_manager")
    email = f"follow-up-{uuid4().hex}@example.com"
    created = request(
        "POST",
        "/api/v1/accounts",
        headers={**headers, **key("e2e-create")},
        json={"email": email, "password": "pw"},
    )
    assert created.status_code == 201
    activated = request(
        "POST",
        f"/api/v1/accounts/{created.json()['user_id']}/activate",
        headers={**headers, **key("e2e-activate")},
    )
    assert activated.status_code == 200
    signed_in = request("POST", "/api/v1/auth/sign-in", json={"email": email, "password": "pw"})
    assert signed_in.status_code == 200


def test_two_review_lifecycle_retains_approval_provenance():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    response = request("GET", f"/api/v1/documents/{document_id}/versions", headers=headers)
    assert response.status_code == 200
    approvals = response.json()[0]["approvals"]
    assert [approval["stage"] for approval in approvals] == [1, 2]
    assert all(approval["reviewer_id"] for approval in approvals)


def test_acl_update_advances_policy_epoch():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    before = admin_api.policy_store.policy_epoch
    response = request(
        "POST",
        f"/api/v1/documents/{document_id}/access",
        headers={**headers, **key("e2e-acl")},
        json={"grants": [{"action": "document:read", "effect": "ALLOW", "role": "employee"}]},
    )
    assert response.status_code == 200
    assert admin_api.policy_store.policy_epoch == before + 1


def test_revoke_endpoint_records_revoked_version():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = publish(headers)
    response = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/revoke",
        headers={**headers, **key("e2e-revoke-status")},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "REVOKED"


def test_revoke_removes_retrievable_chunks():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = publish(headers)
    principal = admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
    tenant_id = admin_api._tenant_uuid(principal)
    assert admin_api.ingestion_service.retrievable_chunks(document_id, tenant_id)
    response = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/revoke",
        headers={**headers, **key("e2e-revoke-index")},
    )
    assert response.status_code == 200
    assert not admin_api.ingestion_service.retrievable_chunks(document_id, tenant_id)


def test_permanent_delete_requires_retention_then_succeeds():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    assert request("DELETE", f"/api/v1/documents/{document_id}", headers=headers).status_code == 204
    blocked = request(
        "POST",
        f"/api/v1/documents/{document_id}/permanent-delete",
        headers={**headers, **key("e2e-retention-blocked")},
        json={"retention_expired": False},
    )
    assert blocked.status_code == 409
    assert blocked.json()["code"] == "RETENTION_ACTIVE"
    deleted = request(
        "POST",
        f"/api/v1/documents/{document_id}/permanent-delete",
        headers={**headers, **key("e2e-permanent-delete")},
        json={"retention_expired": True},
    )
    assert deleted.status_code == 204


def test_publish_idempotency_returns_the_original_safe_result():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = prepare_review_two(headers)
    review = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/approve",
        headers={**headers, **key("e2e-review-two")},
        json={"stage": 2},
    )
    assert review.status_code == 200
    publish_headers = {**headers, **key("e2e-publish-same")}
    first = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/publish",
        headers=publish_headers,
        json={},
    )
    second = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/publish",
        headers=publish_headers,
        json={},
    )
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()


def test_admin_mutations_emit_privacy_safe_audit_events():
    headers, _ = auth("website_manager")
    secret = f"do-not-log-{uuid4().hex}"
    response = request(
        "POST",
        "/api/v1/accounts",
        headers={**headers, **key("e2e-audit")},
        json={"email": f"audit-{uuid4().hex}@example.com", "password": secret},
    )
    assert response.status_code == 201
    events = identity_api.audit_sink.events
    assert any(event.event == "ADMIN_SUCCESS" and event.code == "USER_CREATED" for event in events)
    assert all(secret not in repr(event.as_dict()) for event in events)


def test_failed_publication_returns_retryable_problem_and_no_chunks():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = prepare_review_two(headers)
    review = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/approve",
        headers={**headers, **key("e2e-failure-review")},
        json={"stage": 2},
    )
    assert review.status_code == 200
    admin_api.ingestion_service.fail_next_publication()
    failed = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/publish",
        headers={**headers, **key("e2e-failure-publish")},
        json={},
    )
    assert failed.status_code == 503
    assert failed.json()["code"] == "PUBLICATION_FAILED"
    principal = admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
    assert not admin_api.ingestion_service.retrievable_chunks(document_id, admin_api._tenant_uuid(principal))
