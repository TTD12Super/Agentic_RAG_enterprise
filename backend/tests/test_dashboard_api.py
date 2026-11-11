from __future__ import annotations

from uuid import uuid4

import pytest

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.tests._admin_api_fixtures import auth, request, reset


@pytest.fixture(autouse=True)
def clean_state():
    reset()
    chat_api.reset_state()


@pytest.mark.parametrize("role", ["system_admin", "website_manager"])
def test_management_roles_can_read_empty_dashboard_and_feedback(role: str):
    headers, _ = auth(role, tenant=f"tenant-dashboard-{uuid4().hex}")

    dashboard = request("GET", "/api/v1/dashboard", headers=headers)
    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert {"users", "documents", "usage", "ingestion", "latency", "cost", "evaluation"} <= set(payload)
    assert payload["documents"]["value"]["total"] == 0
    assert payload["usage"]["value"]["requests"] == 0
    assert payload["latency"]["status"] == "UNAVAILABLE"
    assert payload["cost"]["status"] == "UNAVAILABLE"
    assert payload["evaluation"]["status"] == "UNAVAILABLE"
    for metric in payload.values():
        if isinstance(metric, dict) and "status" in metric:
            assert "provenance" in metric
            assert "measurement_period" in metric
            assert "is_estimate" in metric

    feedback = request("GET", "/api/v1/feedback?limit=1", headers=headers)
    assert feedback.status_code == 200
    assert feedback.json()["items"] == []
    assert feedback.json()["pagination"] == {"limit": 1, "offset": 0, "total": 0, "has_more": False}


@pytest.mark.parametrize("role", ["chairman", "employee"])
def test_non_management_roles_are_denied_dashboard_and_feedback(role: str):
    headers, _ = auth(role, tenant=f"tenant-dashboard-deny-{uuid4().hex}")
    assert request("GET", "/api/v1/dashboard", headers=headers).status_code == 404
    assert request("GET", "/api/v1/feedback", headers=headers).status_code == 404


def test_anonymous_is_denied_dashboard_and_feedback():
    assert request("GET", "/api/v1/dashboard").status_code == 401
    assert request("GET", "/api/v1/feedback").status_code == 401


def test_policy_outage_fails_closed_for_both_management_reads():
    headers, _ = auth("website_manager", tenant=f"tenant-dashboard-outage-{uuid4().hex}")
    admin_api.policy_store.available = False
    try:
        dashboard = request("GET", "/api/v1/dashboard", headers=headers)
        feedback = request("GET", "/api/v1/feedback", headers=headers)
    finally:
        admin_api.policy_store.available = True
    assert dashboard.status_code == feedback.status_code == 503
    assert dashboard.json()["code"] == feedback.json()["code"] == "AUTH_UNAVAILABLE"


def test_feedback_review_is_private_bounded_and_replay_does_not_duplicate():
    created = request("POST", "/api/v1/conversations")
    token = created.cookies.get(chat_api.ANONYMOUS_SESSION_COOKIE)
    submitted = request(
        "POST",
        f"/api/v1/conversations/{created.json()['conversation_id']}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "dashboard-feedback-query"},
        json={"query": "private conversation body"},
    )
    answer = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers={"X-Anonymous-Session": token},
    ).json()["answer"]["answer_id"]
    feedback_headers = {
        "X-Anonymous-Session": token,
        "Idempotency-Key": "dashboard-feedback-submit",
    }
    first = request(
        "POST",
        f"/api/v1/answers/{answer}/feedback",
        headers=feedback_headers,
        json={"rating": "POSITIVE", "comment": "private reviewer comment"},
    )
    replay = request(
        "POST",
        f"/api/v1/answers/{answer}/feedback",
        headers=feedback_headers,
        json={"rating": "POSITIVE", "comment": "private reviewer comment"},
    )
    assert first.status_code == 201
    assert replay.status_code == 200

    manager_headers, _ = auth("website_manager", tenant="public")
    review = request("GET", "/api/v1/feedback/review?limit=1&rating=positive", headers=manager_headers)
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload["pagination"] == {"limit": 1, "offset": 0, "total": 1, "has_more": False}
    assert len(review_payload["items"]) == 1
    assert set(review_payload["items"][0]) == {"feedback_id", "answer_id", "rating", "created_at"}
    assert "private reviewer comment" not in review.text
    assert "private conversation body" not in review.text

    other_manager_headers, _ = auth("website_manager", tenant=f"tenant-dashboard-review-{uuid4().hex}")
    other_tenant = request("GET", "/api/v1/feedback", headers=other_manager_headers)
    assert other_tenant.status_code == 200
    assert other_tenant.json()["items"] == []

    empty = request("GET", "/api/v1/feedback?rating=negative", headers=manager_headers)
    assert empty.status_code == 200
    assert empty.json()["items"] == []
