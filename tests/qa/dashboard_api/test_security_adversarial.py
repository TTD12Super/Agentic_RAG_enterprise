from __future__ import annotations

import pytest

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.app.api import identity as identity_api
from backend.tests._admin_api_fixtures import auth, request, reset, upload


@pytest.fixture(autouse=True)
def clean_state():
    reset()
    chat_api.reset_state()


def _feedback(tenant: str, marker: str) -> dict[str, str]:
    headers, _ = auth("employee", tenant=tenant)
    created = request("POST", "/api/v1/conversations", headers=headers)
    conversation_id = created.json()["conversation_id"]
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={**headers, "Idempotency-Key": f"security-query-{marker}"},
        json={"query": f"body-{marker}"},
    )
    answer = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers=headers,
    ).json()["answer"]["answer_id"]
    feedback = request(
        "POST",
        f"/api/v1/answers/{answer}/feedback",
        headers={**headers, "Idempotency-Key": f"security-feedback-{marker}"},
        json={"rating": "negative", "comment": f"comment-{marker}"},
    )
    assert feedback.status_code == 201
    return headers


def test_employee_cannot_read_dashboard_management_data():
    headers, _ = auth("employee", tenant="qa-dash-security-employee")

    response = request("GET", "/api/v1/dashboard", headers=headers)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"
    assert "users" not in response.text


def test_chairman_cannot_read_feedback_review_management_data():
    headers, _ = auth("chairman", tenant="qa-dash-security-chairman")

    response = request("GET", "/api/v1/feedback/review", headers=headers)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"
    assert "items" not in response.text


def test_anonymous_cannot_read_dashboard_or_feedback_review():
    dashboard = request("GET", "/api/v1/dashboard")
    feedback = request("GET", "/api/v1/feedback/review")

    assert dashboard.status_code == feedback.status_code == 401
    assert dashboard.json()["code"] == feedback.json()["code"] == "AUTH_REQUIRED"


def test_policy_outage_fails_closed_for_dashboard_and_feedback():
    headers, _ = auth("website_manager", tenant="qa-dash-security-outage")
    admin_api.policy_store.available = False
    try:
        dashboard = request("GET", "/api/v1/dashboard", headers=headers)
        feedback = request("GET", "/api/v1/feedback", headers=headers)
    finally:
        admin_api.policy_store.available = True

    assert dashboard.status_code == feedback.status_code == 503
    assert dashboard.json()["code"] == feedback.json()["code"] == "AUTH_UNAVAILABLE"
    assert dashboard.json()["retryable"] is feedback.json()["retryable"] is True


def test_dashboard_aggregates_cannot_cross_tenant_boundaries():
    tenant_a = "qa-dash-security-tenant-a"
    tenant_b = "qa-dash-security-tenant-b"
    manager_a, _ = auth("website_manager", tenant=tenant_a)
    employee_a, _ = auth("employee", tenant=tenant_a)
    assert upload(manager_a).status_code == 202
    conversation = request("POST", "/api/v1/conversations", headers=employee_a)
    assert request(
        "POST",
        f"/api/v1/conversations/{conversation.json()['conversation_id']}/messages",
        headers={**employee_a, "Idempotency-Key": "security-tenant-query"},
        json={"query": "tenant-a usage"},
    ).status_code == 202
    manager_b, _ = auth("website_manager", tenant=tenant_b)

    payload = request("GET", "/api/v1/dashboard", headers=manager_b).json()

    assert payload["users"]["value"]["total"] == 1
    assert payload["documents"]["value"]["total"] == 0
    assert payload["ingestion"]["value"]["jobs"] == 0
    assert payload["usage"]["value"]["requests"] == 0


def test_feedback_review_cannot_cross_tenant_boundaries():
    tenant_a = "qa-dash-security-feedback-a"
    _feedback(tenant_a, "foreign")
    manager_b, _ = auth("website_manager", tenant="qa-dash-security-feedback-b")

    response = request("GET", "/api/v1/feedback", headers=manager_b)

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["pagination"]["total"] == 0


def test_feedback_review_does_not_return_comment_body_or_actor_identity():
    tenant = "qa-dash-security-minimize"
    _feedback(tenant, "secret-marker")
    manager, _ = auth("website_manager", tenant=tenant)

    response = request("GET", "/api/v1/feedback/review", headers=manager)

    assert response.status_code == 200
    assert "comment-secret-marker" not in response.text
    assert "body-secret-marker" not in response.text
    assert "actor_id" not in response.text
    assert all(set(item) == {"feedback_id", "answer_id", "rating", "created_at"} for item in response.json()["items"])


def test_client_supplied_tenant_filter_cannot_select_another_tenant():
    tenant_a = "qa-dash-security-selector-a"
    _feedback(tenant_a, "selector")
    manager_b, _ = auth("website_manager", tenant="qa-dash-security-selector-b")

    response = request("GET", "/api/v1/feedback?tenant_id=qa-dash-security-selector-a", headers=manager_b)

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert "qa-dash-security-selector-a" not in response.text


def test_invalid_pagination_is_rejected_before_any_cross_tenant_projection():
    headers, _ = auth("website_manager", tenant="qa-dash-security-pagination")

    zero_limit = request("GET", "/api/v1/feedback?limit=0", headers=headers)
    negative_offset = request("GET", "/api/v1/feedback?offset=-1", headers=headers)

    assert zero_limit.status_code == negative_offset.status_code == 422
    assert "feedback_id" not in zero_limit.text
    assert "feedback_id" not in negative_offset.text


def test_feedback_review_audit_metadata_excludes_sensitive_feedback_content():
    tenant = "qa-dash-security-audit"
    _feedback(tenant, "audit-secret")
    manager, _ = auth("website_manager", tenant=tenant)

    response = request(
        "GET",
        "/api/v1/feedback/review",
        headers={**manager, "X-Request-ID": "qa-dashboard-security-audit-001"},
    )

    assert response.status_code == 200
    events = [event for event in identity_api.audit_sink.events if event.code == "FEEDBACK_REVIEWED"]
    assert len(events) == 1
    event = events[0]
    assert event.tenant_id == tenant
    assert event.request_id == "qa-dashboard-security-audit-001"
    assert event.safe_metadata == {"route": "admin:feedback:review", "status_code": 200}
    assert "audit-secret" not in repr(event.as_dict())
