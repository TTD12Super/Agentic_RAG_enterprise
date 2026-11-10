from __future__ import annotations

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


def test_chairman_is_denied_management_api():
    headers, _ = auth("chairman")
    response = request("POST", "/api/v1/accounts", headers={**headers, **key("chairman-management")}, json={"email": "blocked@example.com", "password": "pw"})
    assert response.status_code == 404


def test_employee_is_denied_management_api():
    headers, _ = auth("employee")
    response = request("GET", "/api/v1/accounts", headers=headers)
    assert response.status_code == 404


def test_anonymous_is_denied_management_api():
    response = request("GET", "/api/v1/accounts")
    assert response.status_code == 401


def test_activation_allows_follow_up_sign_in():
    headers, _ = auth("website_manager")
    created = request("POST", "/api/v1/accounts", headers={**headers, **key("integration-create")}, json={"email": "follow-up@example.com", "password": "pw"})
    assert created.status_code == 201
    activated = request("POST", f"/api/v1/accounts/{created.json()['user_id']}/activate", headers={**headers, **key("integration-activate")})
    assert activated.status_code == 200
    signed_in = request("POST", "/api/v1/auth/sign-in", json={"email": "follow-up@example.com", "password": "pw"})
    assert signed_in.status_code == 200


def test_acl_update_advances_policy_epoch():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    before = admin_api.policy_store.policy_epoch
    response = request("POST", f"/api/v1/documents/{document_id}/access", headers={**headers, **key("acl-allow")}, json={"grants": [{"action": "document:read", "effect": "ALLOW", "role": "employee"}]})
    assert response.status_code == 200
    assert admin_api.policy_store.policy_epoch == before + 1


def test_revoke_endpoint_records_non_active_version():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = publish(headers)
    response = request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/revoke", headers={**headers, **key("integration-revoke")})
    assert response.status_code == 200
    assert response.json()["status"] == "REVOKED"


def test_permanent_delete_requires_retention_expiry_but_succeeds_after_it():
    headers, _ = auth("website_manager")
    document_id, _, _ = publish(headers)
    assert request("DELETE", f"/api/v1/documents/{document_id}", headers=headers).status_code == 204
    blocked = request("POST", f"/api/v1/documents/{document_id}/permanent-delete", headers={**headers, **key("retention-blocked")}, json={"retention_expired": False})
    assert blocked.status_code == 409
    deleted = request("POST", f"/api/v1/documents/{document_id}/permanent-delete", headers={**headers, **key("permanent-delete")}, json={"retention_expired": True})
    assert deleted.status_code == 204


def test_admin_mutations_emit_privacy_safe_audit_events():
    headers, _ = auth("website_manager")
    response = request("POST", "/api/v1/accounts", headers={**headers, **key("integration-audit")}, json={"email": "audit-account@example.com", "password": "do-not-log"})
    assert response.status_code == 201
    events = identity_api.audit_sink.events
    assert any(event.event == "ADMIN_SUCCESS" and event.code == "USER_CREATED" for event in events)
    assert all("do-not-log" not in repr(event.as_dict()) for event in events)


def test_publish_idempotency_returns_the_original_safe_result():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = prepare_review_two(headers)
    first_review = request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/approve", headers={**headers, **key("integration-r2")}, json={"stage": 2})
    assert first_review.status_code == 200
    publish_headers = {**headers, **key("integration-publish-same")}
    first = request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/publish", headers=publish_headers, json={})
    second = request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/publish", headers=publish_headers, json={})
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
