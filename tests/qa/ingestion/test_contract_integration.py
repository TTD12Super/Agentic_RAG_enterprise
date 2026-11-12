"""ING-001 contract/integration QA: 10 deterministic synthetic cases."""

from dataclasses import replace
from uuid import uuid4

import pytest

from backend.app.ingestion import (
    InvalidInput,
    ProcessingStatus,
    PublicationBlocked,
    StagedIndex,
    UploadManifest,
)
from backend.app.models.policy import DataClassification

from tests.qa.ingestion._baseline import HANDOFF, active, make_manifest, new_service, quarantine, validated, read, task


def test_mvp_accepts_only_pdf_docx_and_xlsx():
    assert {make_manifest(filename=name).filename for name in ("a.pdf", "a.docx", "a.xlsx")} == {
        "a.pdf",
        "a.docx",
        "a.xlsx",
    }


def test_legacy_doc_and_xls_are_rejected():
    with pytest.raises(ValueError):
        make_manifest(filename="legacy.doc")
    with pytest.raises(ValueError):
        make_manifest(filename="legacy.xls")


def test_private_object_storage_uri_is_required():
    with pytest.raises(ValueError, match="private"):
        replace(make_manifest(), source_uri="https://public.example/file.pdf")


def test_mime_and_magic_boundaries_are_checked():
    with pytest.raises(ValueError, match="mismatched"):
        replace(make_manifest(), mime_type="text/plain")
    with pytest.raises(ValueError, match="signature"):
        replace(make_manifest(), magic_valid=False)


def test_upload_size_limit_is_enforced_before_processing():
    with pytest.raises(ValueError, match="size limit"):
        replace(make_manifest(), size_bytes=200_000_001)


def test_job_contract_keeps_attempt_and_tenant_scope():
    service, _, _ = new_service()
    manifest = make_manifest()
    job = service.quarantine_upload(manifest, idempotency_key="qa-upload")
    assert job.tenant_id == manifest.tenant_id
    assert job.document_id == manifest.document_id
    assert job.version_id == manifest.version_id
    assert job.attempt == 1 and job.attempt_id


def test_index_contract_requires_exact_chunk_count():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    index = StagedIndex.from_chunks(
        publication_id="qa-count",
        tenant_id=manifest.tenant_id,
        version_id=manifest.version_id,
        content_sha256=manifest.sha256,
        chunks=record.chunks[:1],
    )
    with pytest.raises(PublicationBlocked, match="chunk count"):
        service.stage_index(manifest.version_id, manifest.tenant_id, index)


def test_index_ack_is_required_before_publication():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    index = StagedIndex.from_chunks(
        publication_id="qa-ack",
        tenant_id=manifest.tenant_id,
        version_id=manifest.version_id,
        content_sha256=manifest.sha256,
        chunks=record.chunks,
    )
    service.stage_index(manifest.version_id, manifest.tenant_id, index)
    service.approve_review2(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="qa-review-2")
    with pytest.raises(PublicationBlocked, match="acknowledged"):
        service.publish(manifest.version_id, manifest.tenant_id)


def test_failed_new_publication_preserves_previous_active_version():
    service, _, _ = new_service()
    first, _, _ = active(service)
    second = make_manifest(
        tenant_id=first.tenant_id,
        document_id=first.document_id,
        version_number=2,
        sha256="d" * 64,
    )
    from backend.tests._ingestion_fixtures import staged

    staged(service, second)
    service.approve_review2(second.version_id, second.tenant_id, uuid4(), idempotency_key="qa-review-2")
    service.fail_next_publication()
    with pytest.raises(PublicationBlocked):
        service.publish(second.version_id, second.tenant_id)
    assert service.get_document(first.document_id, first.tenant_id).current_version_id == first.version_id


def test_task_and_handoff_keep_ingestion_provider_neutral():
    item = task("ING-001")
    assert item["phase"] == 2
    assert "CHAT-001 must own query pause/resume" in read(HANDOFF)
    assert "No real object storage" in read(HANDOFF)
    assert item["status"] == "DONE"
