from __future__ import annotations

import pytest

from backend.app.api import chat as chat_api
from backend.app.api import identity as identity_api
from backend.tests._admin_api_fixtures import auth, request, reset


@pytest.fixture(autouse=True)
def clean_state():
    reset()
    chat_api.reset_state()


def _feedback(tenant: str, marker: str, rating: str, comment: str = "private note") -> tuple[dict[str, str], str]:
    headers, _ = auth("employee", tenant=tenant)
    created = request("POST", "/api/v1/conversations", headers=headers)
    conversation_id = created.json()["conversation_id"]
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={**headers, "Idempotency-Key": f"contract-query-{marker}"},
        json={"query": f"private body {marker}"},
    )
    answer = request(
        "GET",
        f"/api/v1/query-jobs/{submitted.json()['job_id']}",
        headers=headers,
    ).json()["answer"]["answer_id"]
    response = request(
        "POST",
        f"/api/v1/answers/{answer}/feedback",
        headers={**headers, "Idempotency-Key": f"contract-feedback-{marker}"},
        json={"rating": rating, "comment": comment},
    )
    assert response.status_code == 201
    return headers, answer


def test_dashboard_contract_is_versioned_and_every_metric_has_a_common_envelope():
    headers, _ = auth("website_manager", tenant="qa-dash-contract-envelope")

    response = request("GET", "/api/v1/dashboard", headers=headers)
    payload = response.json()

    assert response.status_code == 200
    assert payload["schema_version"] == "1.0"
    assert {"users", "documents", "usage", "ingestion", "cache_hit_rate", "latency", "cost", "evaluation"} <= set(payload)
    for metric in payload.values():
        if isinstance(metric, dict) and "status" in metric:
            assert {"value", "unit", "status", "available", "is_estimate", "provenance", "measurement_period"} <= set(metric)


def test_dashboard_contract_exposes_users_documents_usage_and_ingestion_shapes():
    tenant = "qa-dash-contract-aggregates"
    headers, _ = auth("website_manager", tenant=tenant)

    response = request("GET", "/api/v1/dashboard", headers=headers)
    payload = response.json()

    assert response.status_code == 200
    assert set(payload["users"]["value"]) == {"total", "active", "by_role"}
    assert set(payload["documents"]["value"]) == {"total", "by_status", "current_versions"}
    assert set(payload["usage"]["value"]) == {"requests", "by_state"}
    assert set(payload["ingestion"]["value"]) == {"jobs", "by_state", "failed"}


def test_dashboard_contract_labels_unavailable_telemetry_with_reason_and_provenance():
    headers, _ = auth("website_manager", tenant="qa-dash-contract-unavailable")

    payload = request("GET", "/api/v1/dashboard", headers=headers).json()

    for name, reason in {
        "cache_hit_rate": "CACHE_TELEMETRY_UNAVAILABLE",
        "latency": "LATENCY_TELEMETRY_UNAVAILABLE",
        "cost": "PROVIDER_COST_UNAVAILABLE",
        "evaluation": "EVALUATION_UNAVAILABLE",
    }.items():
        metric = payload[name]
        assert metric["status"] == "UNAVAILABLE"
        assert metric["available"] is False
        assert metric["value"] is None
        assert metric["is_estimate"] is False
        assert metric["reason"] == reason
        assert metric["provenance"]
        assert metric["measurement_period"]["label"] == "request_snapshot"


def test_feedback_contract_returns_a_minimized_projection():
    tenant = "qa-dash-contract-projection"
    _, answer = _feedback(tenant, "projection", "positive", "contract-private-comment")
    manager, _ = auth("website_manager", tenant=tenant)

    response = request("GET", "/api/v1/feedback/review", headers=manager)
    item = response.json()["items"][0]

    assert response.status_code == 200
    assert set(item) == {"feedback_id", "answer_id", "rating", "created_at"}
    assert item["answer_id"] == answer
    assert "contract-private-comment" not in response.text
    assert "actor_id" not in response.text


def test_feedback_rating_filter_is_case_insensitive_and_echoed():
    tenant = "qa-dash-contract-filter"
    _feedback(tenant, "positive", "positive")
    _feedback(tenant, "negative", "negative")
    manager, _ = auth("website_manager", tenant=tenant)

    response = request("GET", "/api/v1/feedback?rating=PoSiTiVe", headers=manager)
    payload = response.json()

    assert response.status_code == 200
    assert payload["filter"] == {"rating": "POSITIVE"}
    assert payload["pagination"]["total"] == 1
    assert [item["rating"] for item in payload["items"]] == ["POSITIVE"]


def test_feedback_pagination_contract_reports_total_offset_limit_and_has_more():
    tenant = "qa-dash-contract-pagination"
    for marker in ("one", "two", "three"):
        _feedback(tenant, marker, "positive")
    manager, _ = auth("website_manager", tenant=tenant)

    response = request("GET", "/api/v1/feedback?limit=1&offset=1", headers=manager)
    pagination = response.json()["pagination"]

    assert response.status_code == 200
    assert pagination == {"limit": 1, "offset": 1, "total": 3, "has_more": True}
    assert len(response.json()["items"]) == 1


def test_feedback_pagination_contract_rejects_unbounded_limit_and_offset():
    headers, _ = auth("website_manager", tenant="qa-dash-contract-bounds")

    too_many = request("GET", "/api/v1/feedback?limit=101", headers=headers)
    too_far = request("GET", "/api/v1/feedback?offset=10001", headers=headers)

    assert too_many.status_code == 422
    assert too_far.status_code == 422
    assert "traceback" not in too_many.text.lower()
    assert "traceback" not in too_far.text.lower()


def test_feedback_contract_rejects_unknown_rating_with_a_safe_error():
    headers, _ = auth("website_manager", tenant="qa-dash-contract-invalid-filter")

    response = request("GET", "/api/v1/feedback?rating=maybe", headers=headers)

    assert response.status_code == 400
    assert response.json()["code"] == "REQUEST_INVALID"
    assert response.json()["message"] == "The request is invalid."
    assert "maybe" not in response.text


def test_management_contract_propagates_bounded_correlation_headers():
    headers, _ = auth("website_manager", tenant="qa-dash-contract-correlation")
    request_id = "qa-dashboard-request-001"
    traceparent = "00-11111111111111111111111111111111-2222222222222222-01"

    response = request(
        "GET",
        "/api/v1/dashboard",
        headers={**headers, "X-Request-ID": request_id, "traceparent": traceparent},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id
    assert response.headers["traceparent"] == traceparent


def test_management_audit_contract_contains_tenant_principal_action_and_safe_metadata():
    tenant = "qa-dash-contract-audit"
    headers, user_id = auth("website_manager", tenant=tenant)
    response = request(
        "GET",
        "/api/v1/dashboard",
        headers={**headers, "X-Request-ID": "qa-dashboard-audit-001"},
    )

    assert response.status_code == 200
    event = next(event for event in identity_api.audit_sink.events if event.code == "DASHBOARD_READ")
    assert event.event == "ADMIN_SUCCESS"
    assert event.action == "admin:dashboard:read"
    assert event.principal_id == user_id
    assert event.tenant_id == tenant
    assert event.request_id == "qa-dashboard-audit-001"
    assert event.safe_metadata == {"route": "admin:dashboard:read", "status_code": 200}
