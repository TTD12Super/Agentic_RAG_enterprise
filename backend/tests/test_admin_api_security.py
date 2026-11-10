from __future__ import annotations

import pytest

from backend.app.api import admin as admin_api
from backend.app.authorization.policy import Action, Decision
from backend.tests._admin_api_fixtures import (
    TENANT,
    add_user,
    auth,
    key,
    publish,
    request,
    reset,
    upload,
)


@pytest.fixture(autouse=True)
def clean_state():
    reset()


def test_chairman_cannot_upload():
    headers, _ = auth("chairman")
    response = upload(headers)
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_employee_cannot_upload():
    headers, _ = auth("employee")
    assert upload(headers).status_code == 404


def test_anonymous_cannot_upload():
    assert request("POST", "/api/v1/documents", headers={**key("anonymous-upload")}, json={"title": "No", "filename": "no.pdf", "sha256": "a" * 64, "classification": "PUBLIC"}).status_code == 401


def test_chairman_cannot_approve():
    manager_headers, _ = auth("website_manager")
    uploaded = upload(manager_headers).json()
    chairman_headers, _ = auth("chairman")
    response = request("POST", f"/api/v1/documents/{uploaded['document_id']}/versions/{uploaded['version_id']}/approve", headers={**chairman_headers, **key("chairman-approve")}, json={"stage": 1})
    assert response.status_code == 404


def test_employee_cannot_provision_accounts():
    headers, _ = auth("employee")
    response = request("POST", "/api/v1/accounts", headers={**headers, **key("employee-account")}, json={"email": "not-admin@example.com", "password": "pw"})
    assert response.status_code == 404


def test_cross_tenant_document_is_not_revealed():
    manager_headers, _ = auth("website_manager", tenant=TENANT)
    uploaded = upload(manager_headers).json()
    other_headers, _ = auth("website_manager", tenant="other-tenant")
    response = request("GET", f"/api/v1/documents/{uploaded['document_id']}", headers=other_headers)
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_acl_explicit_deny_overrides_employee_read_allow():
    manager_headers, _ = auth("website_manager")
    employee_email, employee_id = add_user("employee")
    document_id, _, _ = publish(manager_headers)
    updated = request("POST", f"/api/v1/documents/{document_id}/access", headers={**manager_headers, **key("acl-deny")}, json={"grants": [{"action": "document:read", "effect": "DENY", "user_id": employee_id}]})
    assert updated.status_code == 200
    employee_principal = admin_api.identity_service.sign_in(email=employee_email, password="correct-password", mfa_code=None)[2]
    resource = admin_api._document_resource(employee_principal, document_id)
    decision = admin_api.pep.check(employee_principal, Action.DOCUMENT_READ.value, resource=resource)
    assert decision.decision is Decision.DENY
    assert decision.reason_code == "EXPLICIT_DENY"


def test_revoke_removes_retrievable_chunks():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = publish(headers)
    principal = admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
    assert admin_api.ingestion_service.retrievable_chunks(document_id, admin_api._tenant_uuid(principal))
    response = request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/revoke", headers={**headers, **key("revoke-chunks")})
    assert response.status_code == 200
    assert not admin_api.ingestion_service.retrievable_chunks(document_id, admin_api._tenant_uuid(principal))


def test_revoked_document_fails_current_version_policy_check():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = publish(headers)
    principal = admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
    request("POST", f"/api/v1/documents/{document_id}/versions/{version_id}/revoke", headers={**headers, **key("revoke-policy")})
    resource = admin_api._document_resource(principal, document_id)
    decision = admin_api.pep.check(principal, Action.DOCUMENT_READ.value, resource=resource)
    assert decision.decision is Decision.DENY
    assert decision.reason_code == "RESOURCE_REVOKED"


def test_policy_store_outage_denies_admin_action():
    headers, _ = auth("website_manager")
    admin_api.policy_store.available = False
    try:
        response = upload(headers)
    finally:
        admin_api.policy_store.available = True
    assert response.status_code == 503
    assert response.json()["code"] == "AUTH_UNAVAILABLE"
