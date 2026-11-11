from __future__ import annotations

from dataclasses import asdict

import pytest

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.app.feedback import FeedbackService, InMemoryFeedbackRepository
from backend.tests._admin_api_fixtures import auth, request, reset, upload


@pytest.fixture(autouse=True)
def clean_state():
    reset()
    chat_api.reset_state()


def test_measured_metric_keeps_value_provenance_and_measurement_period():
    period = {"label": "qa", "start": "2026-11-11T00:00:00Z", "end": "2026-11-11T01:00:00Z"}

    metric = admin_api._dashboard_metric(
        {"total": 3},
        unit="documents",
        provenance="synthetic.fixture",
        measurement_period=period,
    )

    assert metric == {
        "value": {"total": 3},
        "unit": "documents",
        "status": "MEASURED",
        "available": True,
        "is_estimate": False,
        "provenance": "synthetic.fixture",
        "measurement_period": period,
    }


def test_unavailable_metric_is_explicitly_empty_and_not_an_estimate():
    period = {"label": "qa", "start": "2026-11-11T00:00:00Z", "end": "2026-11-11T00:00:00Z"}

    metric = admin_api._unavailable_metric(
        unit="USD",
        provenance="provider.telemetry",
        measurement_period=period,
        reason="PROVIDER_COST_UNAVAILABLE",
    )

    assert metric["status"] == "UNAVAILABLE"
    assert metric["available"] is False
    assert metric["value"] is None
    assert metric["is_estimate"] is False
    assert metric["reason"] == "PROVIDER_COST_UNAVAILABLE"
    assert metric["provenance"] == "provider.telemetry"


def test_system_admin_can_read_dashboard_through_the_real_pep():
    headers, _ = auth("system_admin", tenant="qa-dash-behavior-admin")

    response = request("GET", "/api/v1/dashboard", headers=headers)

    assert response.status_code == 200
    assert response.json()["schema_version"] == "1.0"


def test_website_manager_can_read_feedback_through_the_real_pep():
    headers, _ = auth("website_manager", tenant="qa-dash-behavior-manager")

    response = request("GET", "/api/v1/feedback", headers=headers)

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_chairman_is_denied_the_management_boundary():
    headers, _ = auth("chairman", tenant="qa-dash-behavior-chairman")

    response = request("GET", "/api/v1/dashboard", headers=headers)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_employee_is_denied_the_management_boundary():
    headers, _ = auth("employee", tenant="qa-dash-behavior-employee")

    response = request("GET", "/api/v1/feedback/review", headers=headers)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND_OR_FORBIDDEN"


def test_anonymous_is_denied_without_a_management_data_or_existence_leak():
    response = request("GET", "/api/v1/dashboard")

    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_REQUIRED"
    assert "documents" not in response.text


def test_feedback_review_projection_has_no_actor_comment_or_body():
    service = FeedbackService(InMemoryFeedbackRepository())
    record, _ = service.submit(
        answer_id="answer-component-1",
        actor_id="actor-private-1",
        rating="positive",
        comment="private component comment",
        idempotency_key="component-feedback-1",
        tenant_id="tenant-component-a",
    )

    reviews, total = service.review(tenant_id="tenant-component-a", limit=10, offset=0)

    assert total == 1
    assert asdict(reviews[0]) == {
        "feedback_id": record.feedback_id,
        "answer_id": "answer-component-1",
        "rating": "POSITIVE",
        "created_at": record.created_at,
    }
    assert "actor_id" not in asdict(reviews[0])
    assert "comment" not in asdict(reviews[0])
    assert "private component comment" not in repr(reviews[0])


def test_feedback_replay_is_idempotent_but_tenant_bound():
    service = FeedbackService(InMemoryFeedbackRepository())
    first, replayed = service.submit(
        answer_id="answer-replay-1",
        actor_id="actor-1",
        rating="positive",
        comment=None,
        idempotency_key="component-replay-1",
        tenant_id="tenant-component-a",
    )
    same, was_replayed = service.submit(
        answer_id="answer-replay-1",
        actor_id="actor-1",
        rating="positive",
        comment=None,
        idempotency_key="component-replay-1",
        tenant_id="tenant-component-a",
    )
    foreign, foreign_replayed = service.submit(
        answer_id="answer-replay-1",
        actor_id="actor-1",
        rating="positive",
        comment=None,
        idempotency_key="component-replay-1",
        tenant_id="tenant-component-b",
    )

    assert not replayed
    assert was_replayed
    assert same.feedback_id == first.feedback_id
    assert not foreign_replayed
    assert foreign.feedback_id != first.feedback_id


def test_dashboard_metrics_aggregate_only_the_current_tenant_snapshot():
    tenant = "qa-dash-behavior-aggregate"
    manager_headers, _ = auth("website_manager", tenant=tenant)
    employee_headers, _ = auth("employee", tenant=tenant)
    uploaded = upload(manager_headers)
    conversation = request("POST", "/api/v1/conversations", headers=employee_headers)
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation.json()['conversation_id']}/messages",
        headers={**employee_headers, "Idempotency-Key": "behavior-aggregate-query"},
        json={"query": "aggregate usage"},
    )
    assert uploaded.status_code == 202
    assert submitted.status_code == 202

    dashboard = request("GET", "/api/v1/dashboard", headers=manager_headers)
    payload = dashboard.json()

    assert dashboard.status_code == 200
    assert payload["users"]["value"]["total"] == 2
    assert payload["documents"]["value"]["total"] == 1
    assert payload["ingestion"]["value"]["jobs"] == 1
    assert payload["usage"]["value"]["requests"] == 1
