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


def _feedback(tenant: str, marker: str, rating: str = "positive", comment: str = "operational private note") -> tuple[dict[str, str], str, dict[str, str]]:
    headers, _ = auth("employee", tenant=tenant)
    created = request("POST", "/api/v1/conversations", headers=headers)
    conversation_id = created.json()["conversation_id"]
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={**headers, "Idempotency-Key": f"e2e-query-{marker}"},
        json={"query": f"operational body {marker}"},
    )
    answer = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers=headers,
    ).json()["answer"]["answer_id"]
    feedback_headers = {**headers, "Idempotency-Key": f"e2e-feedback-{marker}"}
    feedback = request(
        "POST",
        f"/api/v1/answers/{answer}/feedback",
        headers=feedback_headers,
        json={"rating": rating, "comment": comment},
    )
    assert feedback.status_code == 201
    return headers, answer, feedback_headers


def test_document_upload_flows_into_dashboard_document_and_ingestion_counts():
    manager, _ = auth("website_manager", tenant="qa-dash-e2e-document")

    uploaded = upload(manager)
    dashboard = request("GET", "/api/v1/dashboard", headers=manager)

    assert uploaded.status_code == 202
    assert dashboard.status_code == 200
    assert dashboard.json()["documents"]["value"]["total"] == 1
    assert dashboard.json()["ingestion"]["value"] == {
        "jobs": 1,
        "by_state": {"QUEUED": 1},
        "failed": 0,
    }


def test_completed_chat_query_flows_into_the_usage_aggregate():
    tenant = "qa-dash-e2e-usage"
    manager, _ = auth("website_manager", tenant=tenant)
    employee, _ = auth("employee", tenant=tenant)
    conversation = request("POST", "/api/v1/conversations", headers=employee)
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation.json()['conversation_id']}/messages",
        headers={**employee, "Idempotency-Key": "e2e-usage-query-001"},
        json={"query": "count this request"},
    )
    status = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers=employee,
    )

    dashboard = request("GET", "/api/v1/dashboard", headers=manager)

    assert status.status_code == 200
    assert status.json()["state"] == "COMPLETED"
    assert dashboard.json()["usage"]["value"] == {"requests": 1, "by_state": {"COMPLETED": 1}}


def test_feedback_replay_is_operationally_idempotent_and_review_has_one_item():
    tenant = "qa-dash-e2e-feedback-replay"
    _, answer, feedback_headers = _feedback(tenant, "replay")
    replay = request(
        "POST",
        f"/api/v1/answers/{answer}/feedback",
        headers=feedback_headers,
        json={"rating": "positive", "comment": "operational private note"},
    )
    manager, _ = auth("website_manager", tenant=tenant)
    review = request("GET", "/api/v1/feedback/review", headers=manager)

    assert replay.status_code == 200
    assert replay.json()["feedback_id"] == review.json()["items"][0]["feedback_id"]
    assert review.json()["pagination"] == {"limit": 50, "offset": 0, "total": 1, "has_more": False}


def test_feedback_filter_and_page_walk_are_operationally_bounded():
    tenant = "qa-dash-e2e-feedback-pages"
    _feedback(tenant, "page-positive-1", "positive")
    _feedback(tenant, "page-negative", "negative")
    _feedback(tenant, "page-positive-2", "positive")
    manager, _ = auth("website_manager", tenant=tenant)

    filtered = request("GET", "/api/v1/feedback?rating=negative&limit=1", headers=manager)
    page = request("GET", "/api/v1/feedback?limit=2&offset=2", headers=manager)

    assert filtered.status_code == 200
    assert filtered.json()["pagination"] == {"limit": 1, "offset": 0, "total": 1, "has_more": False}
    assert [item["rating"] for item in filtered.json()["items"]] == ["NEGATIVE"]
    assert page.status_code == 200
    assert page.json()["pagination"] == {"limit": 2, "offset": 2, "total": 3, "has_more": False}
    assert len(page.json()["items"]) == 1


def test_system_admin_operational_read_sees_its_tenant_document_snapshot():
    headers, _ = auth("system_admin", tenant="qa-dash-e2e-system-admin")
    assert upload(headers).status_code == 202

    dashboard = request("GET", "/api/v1/dashboard", headers=headers)

    assert dashboard.status_code == 200
    assert dashboard.json()["documents"]["value"]["total"] == 1


def test_website_manager_operational_read_sees_feedback_without_sensitive_fields():
    tenant = "qa-dash-e2e-website-manager"
    _feedback(tenant, "manager-review", comment="manager-private-comment")
    manager, _ = auth("website_manager", tenant=tenant)

    review = request("GET", "/api/v1/feedback", headers=manager)

    assert review.status_code == 200
    assert review.json()["pagination"]["total"] == 1
    assert "manager-private-comment" not in review.text
    assert "actor_id" not in review.text


def test_policy_outage_recovery_restores_management_reads():
    headers, _ = auth("website_manager", tenant="qa-dash-e2e-recovery")
    admin_api.policy_store.available = False
    try:
        unavailable = request("GET", "/api/v1/dashboard", headers=headers)
    finally:
        admin_api.policy_store.available = True
    recovered = request("GET", "/api/v1/dashboard", headers=headers)

    assert unavailable.status_code == 503
    assert unavailable.json()["code"] == "AUTH_UNAVAILABLE"
    assert recovered.status_code == 200
    assert recovered.json()["schema_version"] == "1.0"


def test_operational_dashboard_explains_unavailable_metrics_instead_of_inventing_values():
    headers, _ = auth("website_manager", tenant="qa-dash-e2e-telemetry")

    payload = request("GET", "/api/v1/dashboard", headers=headers).json()

    for name in ("latency", "cost", "evaluation"):
        metric = payload[name]
        assert metric["status"] == "UNAVAILABLE"
        assert metric["value"] is None
        assert metric["is_estimate"] is False
        assert metric["provenance"]
        assert metric["measurement_period"]["start"] == metric["measurement_period"]["end"]


def test_feedback_review_records_operational_correlation_metadata():
    tenant = "qa-dash-e2e-audit"
    _feedback(tenant, "audit-review")
    manager, user_id = auth("website_manager", tenant=tenant)
    request_id = "qa-dashboard-e2e-audit-001"
    review = request(
        "GET",
        "/api/v1/feedback/review",
        headers={**manager, "X-Request-ID": request_id},
    )

    assert review.status_code == 200
    event = next(event for event in identity_api.audit_sink.events if event.code == "FEEDBACK_REVIEWED")
    assert event.event == "ADMIN_SUCCESS"
    assert event.action == "admin:feedback:review"
    assert event.principal_id == user_id
    assert event.tenant_id == tenant
    assert event.request_id == request_id
    assert event.safe_metadata["status_code"] == 200


def test_denied_operational_read_is_a_safe_problem_with_correlation():
    headers, _ = auth("employee", tenant="qa-dash-e2e-safe-error")

    response = request(
        "GET",
        "/api/v1/dashboard",
        headers={**headers, "X-Request-ID": "qa-dashboard-e2e-denied-001"},
    )

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json() == {
        "code": "NOT_FOUND_OR_FORBIDDEN",
        "message": "The requested administration action is not permitted.",
        "request_id": "qa-dashboard-e2e-denied-001",
        "retryable": False,
    }
    assert "tenant_id" not in response.text
