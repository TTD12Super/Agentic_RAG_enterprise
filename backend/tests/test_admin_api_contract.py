from __future__ import annotations

import pytest

from backend.tests._admin_api_fixtures import auth, key, request, reset, upload


@pytest.fixture(autouse=True)
def clean_state():
    reset()


def test_existing_sign_in_contract_remains_under_auth_prefix():
    headers, _ = auth("employee")
    assert "Bearer " in headers["Authorization"]


def test_upload_returns_async_job_envelope():
    headers, _ = auth("website_manager")
    response = upload(headers)
    assert response.status_code == 202
    assert set(response.json()) == {"job_id", "document_id", "version_id", "state", "current_stage", "attempt", "error_code"}


def test_mutating_post_requires_idempotency_key():
    headers, _ = auth("website_manager")
    response = request("POST", "/api/v1/accounts", headers=headers, json={"email": "missing-key@example.com", "password": "pw"})
    assert response.status_code == 400
    assert response.json()["code"] == "REQUEST_INVALID"


def test_upload_accepts_docx_mime_inference():
    headers, _ = auth("website_manager")
    response = request("POST", "/api/v1/documents", headers={**headers, **key("docx-upload")}, json={"title": "Word", "filename": "word.docx", "sha256": "d" * 64, "classification": "PUBLIC"})
    assert response.status_code == 202


def test_upload_accepts_xlsx_mime_inference():
    headers, _ = auth("website_manager")
    response = request("POST", "/api/v1/documents", headers={**headers, **key("xlsx-upload")}, json={"title": "Sheet", "filename": "sheet.xlsx", "sha256": "e" * 64, "classification": "PUBLIC"})
    assert response.status_code == 202


def test_account_response_does_not_return_password():
    headers, _ = auth("website_manager")
    response = request("POST", "/api/v1/accounts", headers={**headers, **key("account-contract")}, json={"email": "safe@example.com", "password": "do-not-return"})
    assert response.status_code == 201
    assert "password" not in response.json()
    assert "do-not-return" not in response.text


def test_approval_schema_requires_explicit_stage():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    response = request("POST", f"/api/v1/documents/{uploaded['document_id']}/versions/{uploaded['version_id']}/approve", headers={**headers, **key("missing-stage")}, json={})
    assert response.status_code == 422


def test_job_status_contains_redacted_progress_only():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    response = request("GET", f"/api/v1/ingestion-jobs/{uploaded['job_id']}", headers=headers)
    assert response.status_code == 200
    assert "source_text" not in response.text
    assert set(response.json()) == {"job_id", "document_id", "version_id", "state", "current_stage", "attempt", "error_code"}


def test_version_history_contains_provenance_without_file_content():
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()
    response = request("GET", f"/api/v1/documents/{uploaded['document_id']}/versions", headers=headers)
    assert response.status_code == 200
    assert "source_uri" in response.json()[0]
    assert "content" not in response.text.lower()


def test_problem_response_uses_safe_media_type_for_anonymous_admin_call():
    response = request("POST", "/api/v1/accounts", headers={**key("anonymous-call")}, json={"email": "anonymous@example.com", "password": "pw"})
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")
