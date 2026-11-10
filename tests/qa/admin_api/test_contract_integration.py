from __future__ import annotations

from uuid import uuid4

import pytest

from backend.tests._admin_api_fixtures import auth, key, request, reset, upload


@pytest.fixture(autouse=True)
def clean_state():
    reset()


def _upload_body(document_id: str, version_id: str, sha256: str) -> dict[str, object]:
    return {
        "document_id": document_id,
        "version_id": version_id,
        "title": "Synthetic contract document",
        "filename": "contract.pdf",
        "sha256": sha256,
        "classification": "PUBLIC",
    }


def test_upload_returns_async_job_envelope():
    headers, _ = auth("website_manager")
    response = upload(headers)
    assert response.status_code == 202
    assert set(response.json()) == {
        "job_id",
        "document_id",
        "version_id",
        "state",
        "current_stage",
        "attempt",
        "error_code",
    }


def test_upload_idempotency_replays_the_same_job():
    headers, _ = auth("website_manager")
    document_id, version_id = str(uuid4()), str(uuid4())
    body = _upload_body(document_id, version_id, "a" * 64)
    request_headers = {**headers, **key("contract-upload-replay")}
    first = request("POST", "/api/v1/documents", headers=request_headers, json=body)
    second = request("POST", "/api/v1/documents", headers=request_headers, json=body)
    assert first.status_code == second.status_code == 202
    assert first.json() == second.json()


def test_upload_idempotency_rejects_a_different_fingerprint():
    headers, _ = auth("website_manager")
    document_id, version_id = str(uuid4()), str(uuid4())
    request_headers = {**headers, **key("contract-upload-conflict")}
    first = request(
        "POST",
        "/api/v1/documents",
        headers=request_headers,
        json=_upload_body(document_id, version_id, "a" * 64),
    )
    second = request(
        "POST",
        "/api/v1/documents",
        headers=request_headers,
        json=_upload_body(document_id, version_id, "b" * 64),
    )
    assert first.status_code == 202
    assert second.status_code == 409
    assert second.json()["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_mutating_post_requires_idempotency_key():
    headers, _ = auth("website_manager")
    response = request(
        "POST",
        "/api/v1/accounts",
        headers=headers,
        json={"email": f"missing-key-{uuid4().hex}@example.com", "password": "pw"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "REQUEST_INVALID"


def test_upload_accepts_docx_mime_inference():
    headers, _ = auth("website_manager")
    response = request(
        "POST",
        "/api/v1/documents",
        headers={**headers, **key("contract-docx")},
        json={
            "title": "Word",
            "filename": "word.docx",
            "sha256": "d" * 64,
            "classification": "PUBLIC",
        },
    )
    assert response.status_code == 202


def test_upload_accepts_xlsx_mime_inference():
    headers, _ = auth("website_manager")
    response = request(
        "POST",
        "/api/v1/documents",
        headers={**headers, **key("contract-xlsx")},
        json={
            "title": "Sheet",
            "filename": "sheet.xlsx",
            "sha256": "e" * 64,
            "classification": "PUBLIC",
        },
    )
    assert response.status_code == 202


def test_account_response_does_not_return_password():
    headers, _ = auth("website_manager")
    secret = f"do-not-return-{uuid4().hex}"
    response = request(
        "POST",
        "/api/v1/accounts",
        headers={**headers, **key("contract-account")},
        json={"email": f"safe-{uuid4().hex}@example.com", "password": secret},
    )
    assert response.status_code == 201
    assert "password" not in response.json()
    assert secret not in response.text


def test_approval_schema_requires_explicit_stage():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    response = request(
        "POST",
        f"/api/v1/documents/{uploaded['document_id']}/versions/{uploaded['version_id']}/approve",
        headers={**headers, **key("contract-missing-stage")},
        json={},
    )
    assert response.status_code == 422


def test_job_status_contains_redacted_progress_only():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    response = request("GET", f"/api/v1/ingestion-jobs/{uploaded['job_id']}", headers=headers)
    assert response.status_code == 200
    assert "source_text" not in response.text
    assert set(response.json()) == {
        "job_id",
        "document_id",
        "version_id",
        "state",
        "current_stage",
        "attempt",
        "error_code",
    }


def test_version_history_contains_provenance_without_file_content():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    response = request("GET", f"/api/v1/documents/{uploaded['document_id']}/versions", headers=headers)
    assert response.status_code == 200
    assert "source_uri" in response.json()[0]
    assert "content" not in response.text.lower()
