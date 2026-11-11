from fastapi.testclient import TestClient

from backend.app.api import chat as chat_api
from backend.app.core.chat import ChatService
from backend.app.main import app
from backend.app.rag.runtime import LocalRagExecutor


def test_http_chat_reaches_local_rag_and_returns_verified_citation(monkeypatch) -> None:
    monkeypatch.setattr(chat_api, "chat_service", ChatService(executor=LocalRagExecutor()))
    client = TestClient(app)
    created = client.post("/api/v1/conversations")
    assert created.status_code == 201

    conversation_id = created.json()["conversation_id"]
    submitted = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"Idempotency-Key": "runtime-integration-test"},
        json={"query": "Quy định mua sắm thiết bị như thế nào?"},
    )
    assert submitted.status_code == 202

    job = client.get(f"/api/v1/query-jobs/{submitted.json()['job_id']}")
    payload = job.json()
    assert job.status_code == 200
    assert payload["state"] == "COMPLETED"
    assert payload["answer"]["status"] == "ANSWERED"
    assert payload["answer"]["citations"][0]["tenant_id"] == "public"
