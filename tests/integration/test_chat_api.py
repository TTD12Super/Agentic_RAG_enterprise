from __future__ import annotations

from backend.app.api import admin as admin_api
from backend.app.api import chat as chat_api
from backend.tests.test_chat_api import anonymous_conversation, request


def test_chat_api_integration_preserves_anonymous_boundary_and_completion():
    chat_api.reset_state()
    admin_api.reset_state()
    conversation_id, token = anonymous_conversation()
    submitted = request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"X-Anonymous-Session": token, "Idempotency-Key": "integration-chat-001"},
        json={"query": "integration"},
    )
    assert submitted.status_code == 202
    completed = request(
        "GET", f"/api/v1/query-jobs/{submitted.json()['job_id']}", headers={"X-Anonymous-Session": token}
    )
    assert completed.status_code == 200
    assert completed.json()["state"] == "COMPLETED"
    assert request(
        "GET", f"/api/v1/conversations/{conversation_id}", headers={"X-Anonymous-Session": "wrong-session"}
    ).status_code == 404
