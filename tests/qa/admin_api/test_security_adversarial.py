from __future__ import annotations

from uuid import uuid4

import pytest

from backend.app.api import admin as admin_api
from backend.app.authorization.policy import Action, Decision
from backend.app.api import identity as identity_api
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
    response = upload(headers)
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_anonymous_cannot_upload():
    response = request(
        "POST",
        "/api/v1/documents",
        headers=key("security-anonymous-upload"),
        json={
            "title": "No",
            "filename": "no.pdf",
            "sha256": "a" * 64,
            "classification": "PUBLIC",
        },
    )
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")


def test_chairman_cannot_approve():
    manager_headers, _ = auth("website_manager")
    uploaded = upload(manager_headers).json()
    chairman_headers, _ = auth("chairman")
    response = request(
        "POST",
        f"/api/v1/documents/{uploaded['document_id']}/versions/{uploaded['version_id']}/approve",
        headers={**chairman_headers, **key("security-chairman-approve")},
        json={"stage": 1},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_employee_cannot_provision_accounts():
    headers, _ = auth("employee")
    response = request(
        "POST",
        "/api/v1/accounts",
        headers={**headers, **key("security-employee-account")},
        json={"email": f"not-admin-{uuid4().hex}@example.com", "password": "pw"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_cross_tenant_resources_are_not_revealed():
    manager_headers, _ = auth("website_manager", tenant=TENANT)
    uploaded = upload(manager_headers).json()
    other_headers, _ = auth("website_manager", tenant="other-tenant")
    document = request("GET", f"/api/v1/documents/{uploaded['document_id']}", headers=other_headers)
    assert document.status_code == 404
    assert document.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"
    accounts = request("GET", "/api/v1/accounts", headers=other_headers)
    assert accounts.status_code == 200
    assert all(record["tenant_id"] == "other-tenant" for record in accounts.json()["users"])


def test_acl_explicit_deny_overrides_employee_read_allow():
    manager_headers, _ = auth("website_manager")
    employee_email, employee_id = add_user("employee")
    document_id, _, _ = publish(manager_headers)
    updated = request(
        "POST",
        f"/api/v1/documents/{document_id}/access",
        headers={**manager_headers, **key("security-acl-deny")},
        json={
            "grants": [
                {
                    "action": "document:read",
                    "effect": "DENY",
                    "user_id": employee_id,
                }
            ]
        },
    )
    assert updated.status_code == 200
    employee_principal = admin_api.identity_service.sign_in(
        email=employee_email,
        password="correct-password",
        mfa_code=None,
    )[2]
    resource = admin_api._document_resource(employee_principal, document_id)
    decision = admin_api.pep.check(employee_principal, Action.DOCUMENT_READ.value, resource=resource)
    assert decision.decision is Decision.DENY
    assert decision.reason_code == "EXPLICIT_DENY"


def test_revoked_document_fails_current_version_policy_check():
    headers, _ = auth("website_manager")
    document_id, version_id, _ = publish(headers)
    principal = admin_api.identity_service.resolve_bearer(headers["Authorization"].split(" ", 1)[1])
    revoked = request(
        "POST",
        f"/api/v1/documents/{document_id}/versions/{version_id}/revoke",
        headers={**headers, **key("security-revoke-policy")},
    )
    assert revoked.status_code == 200
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
    assert response.json()["retryable"] is True


def test_admin_results_do_not_expose_conversation_or_password_fields():
    headers, _ = auth("website_manager")
    password = f"password-sentinel-{uuid4().hex}"
    created = request(
        "POST",
        "/api/v1/accounts",
        headers={**headers, **key("security-privacy-account")},
        json={"email": f"privacy-{uuid4().hex}@example.com", "password": password},
    )
    assert created.status_code == 201
    document_id, _, _ = publish(headers)
    responses = [
        created,
        request("GET", "/api/v1/accounts", headers=headers),
        request("GET", f"/api/v1/documents/{document_id}/versions", headers=headers),
    ]
    for response in responses:
        assert response.status_code == 200 or response is created
        body = response.text.lower()
        assert password not in response.text
        assert '"password"' not in body
        assert '"conversation"' not in body
        assert '"content"' not in body
    assert all(password not in repr(event.as_dict()) for event in identity_api.audit_sink.events)
