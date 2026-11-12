from __future__ import annotations

from backend.app.db.runtime import normalize_database_url, stable_uuid
from backend.tests._admin_api_fixtures import auth, key, request, reset, upload


def test_runtime_url_normalization_does_not_change_credentials() -> None:
    value = "postgresql+psycopg://user:password@example.test/db?sslmode=require"
    assert normalize_database_url(value) == "postgresql://user:password@example.test/db?sslmode=require"
    assert stable_uuid("tenant", "public") == stable_uuid("tenant", "public")


def test_document_and_approval_catalogs_are_real_api_shapes() -> None:
    reset()
    headers, _ = auth("website_manager")
    uploaded = upload(headers).json()

    documents = request("GET", "/api/v1/documents", headers=headers)
    assert documents.status_code == 200
    assert documents.json()["items"] == []

    approvals = request("GET", "/api/v1/approvals", headers=headers)
    assert approvals.status_code == 200
    assert approvals.json()["items"][0]["version_id"] == uploaded["version_id"]


def test_audit_catalog_is_metadata_only() -> None:
    reset()
    headers, _ = auth("website_manager")
    response = request(
        "POST",
        "/api/v1/accounts",
        headers={**headers, **key("audit-runtime-test")},
        json={"email": "audit-runtime@example.com", "password": "secret-password"},
    )
    assert response.status_code == 201
    audit = request("GET", "/api/v1/audit", headers=headers)
    assert audit.status_code == 200
    assert "secret-password" not in audit.text
    assert "safe_metadata" in audit.json()["items"][0]
