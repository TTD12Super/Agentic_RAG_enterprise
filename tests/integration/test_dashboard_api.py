from __future__ import annotations

from uuid import uuid4

from backend.tests._admin_api_fixtures import auth, request, reset, upload


def test_dashboard_integration_reports_authorized_document_and_ingestion_aggregates():
    reset()
    headers, _ = auth("website_manager", tenant=f"tenant-dashboard-integration-{uuid4().hex}")
    uploaded = upload(headers)

    assert uploaded.status_code == 202
    dashboard = request("GET", "/api/v1/dashboard", headers=headers)
    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["documents"]["value"]["total"] == 1
    assert payload["ingestion"]["value"]["jobs"] == 1
    assert payload["ingestion"]["value"]["by_state"] == {"QUEUED": 1}
