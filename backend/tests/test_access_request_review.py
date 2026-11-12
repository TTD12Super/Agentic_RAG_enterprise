from __future__ import annotations

from uuid import uuid4

import pytest

from backend.app.api import identity as identity_api
from backend.app.core.config import get_settings
from backend.tests._admin_api_fixtures import auth, key, request, reset


@pytest.fixture(autouse=True)
def clean_state():
    reset()


def create_request(*, headers: dict[str, str] | None = None, marker: str | None = None) -> dict[str, object]:
    email = f"access-{marker or uuid4().hex}@example.com"
    response = request(
        "POST",
        "/api/v1/access-requests",
        headers={**(headers or {}), **key(f"create-{marker or uuid4().hex}")},
        json={
            "full_name": "Synthetic Applicant",
            "email": email,
            "department": "Finance",
            "reason": "Need access to the finance policy.",
            "consent": True,
        },
    )
    assert response.status_code == 202, response.text
    return {**response.json(), "email": email}


def test_manager_lists_same_tenant_pending_requests_as_safe_metadata_only():
    created = create_request(marker="safe")
    manager, _ = auth("website_manager", tenant="public")

    response = request("GET", "/api/v1/access-requests", headers=manager)

    assert response.status_code == 200
    item = next(item for item in response.json()["items"] if item["request_id"] == created["request_id"])
    assert set(item) == {
        "request_id",
        "status",
        "full_name",
        "email",
        "department",
        "reason",
        "created_at",
        "reviewed_at",
        "reviewed_by",
        "access_granted",
    }
    assert item["status"] == "PENDING_ADMIN_REVIEW"
    assert item["access_granted"] is False
    assert item["email"] == created["email"]
    assert item["full_name"] == "Synthetic Applicant"
    assert item["reason"] == "Need access to the finance policy."


def test_manager_cannot_list_or_review_another_tenant_request():
    requester, _ = auth("employee", tenant="tenant-b")
    created = create_request(headers=requester, marker="tenant-b")
    manager_a, _ = auth("website_manager", tenant="tenant-a")

    listed = request("GET", "/api/v1/access-requests", headers=manager_a)
    reviewed = request(
        "POST",
        f"/api/v1/access-requests/{created['request_id']}/review",
        headers={**manager_a, **key("cross-tenant-review")},
        json={"decision": "APPROVE"},
    )

    assert listed.status_code == 200
    assert listed.json()["items"] == []
    assert reviewed.status_code == 404


def test_anonymous_request_uses_server_configured_tenant(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(get_settings(), "access_request_tenant_id", "tenant-a")
    created = create_request(marker="configured-tenant")
    manager, _ = auth("website_manager", tenant="tenant-a")

    listed = request("GET", "/api/v1/access-requests", headers=manager)

    assert listed.status_code == 200
    assert any(item["request_id"] == created["request_id"] for item in listed.json()["items"])


@pytest.mark.parametrize("role", ["employee", "chairman"])
def test_only_managers_can_review_access_requests(role: str):
    created = create_request(marker=f"deny-{role}")
    headers, _ = auth(role, tenant="public")

    listed = request("GET", "/api/v1/access-requests", headers=headers)
    reviewed = request(
        "POST",
        f"/api/v1/access-requests/{created['request_id']}/review",
        headers={**headers, **key(f"deny-review-{role}")},
        json={"decision": "REJECT"},
    )

    assert listed.status_code == 404
    assert reviewed.status_code == 404


def test_approve_is_idempotent_and_does_not_grant_access():
    created = create_request(marker="approve")
    manager, manager_id = auth("website_manager", tenant="public")
    headers = {**manager, **key("approve-review")}

    first = request(
        "POST",
        f"/api/v1/access-requests/{created['request_id']}/review",
        headers=headers,
        json={"decision": "APPROVE"},
    )
    replay = request(
        "POST",
        f"/api/v1/access-requests/{created['request_id']}/review",
        headers=headers,
        json={"decision": "APPROVE"},
    )

    assert first.status_code == replay.status_code == 200
    assert first.json() == replay.json()
    assert first.json()["status"] == "APPROVED_PENDING_PROVISIONING"
    assert first.json()["reviewed_by"] == manager_id
    assert first.json()["access_granted"] is False
    assert identity_api.identity_store.find_by_email(str(created["email"])) is None


def test_review_rejects_key_reuse_and_conflicting_decision():
    created = create_request(marker="conflict")
    manager, _ = auth("website_manager", tenant="public")
    headers = {**manager, **key("conflict-review")}

    first = request(
        "POST",
        f"/api/v1/access-requests/{created['request_id']}/review",
        headers=headers,
        json={"decision": "REJECT"},
    )
    reused = request(
        "POST",
        f"/api/v1/access-requests/{created['request_id']}/review",
        headers=headers,
        json={"decision": "APPROVE"},
    )
    conflicting = request(
        "POST",
        f"/api/v1/access-requests/{created['request_id']}/review",
        headers={**manager, **key("conflict-review-2")},
        json={"decision": "APPROVE"},
    )

    assert first.status_code == 200
    assert reused.status_code == 409
    assert reused.json()["code"] == "IDEMPOTENCY_KEY_REUSED"
    assert conflicting.status_code == 409
    assert conflicting.json()["code"] == "REQUEST_CONFLICT"


def test_review_requires_idempotency_and_valid_request_id():
    manager, _ = auth("website_manager", tenant="public")

    missing_key = request(
        "POST",
        f"/api/v1/access-requests/{uuid4()}/review",
        headers=manager,
        json={"decision": "APPROVE"},
    )
    invalid_id = request(
        "POST",
        "/api/v1/access-requests/not-a-uuid/review",
        headers={**manager, **key("invalid-id")},
        json={"decision": "APPROVE"},
    )

    assert missing_key.status_code == 400
    assert missing_key.json()["code"] == "IDEMPOTENCY_REQUIRED"
    assert invalid_id.status_code == 400
    assert invalid_id.json()["code"] == "REQUEST_INVALID"
