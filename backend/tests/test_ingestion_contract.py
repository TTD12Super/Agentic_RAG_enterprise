import pytest
from uuid import uuid4

from backend.app.ingestion import (
    DataClassification,
    InvalidInput,
    PublicationBlocked,
    StagedIndex,
    UploadManifest,
)
from backend.tests._ingestion_fixtures import active, make_chunks, make_manifest, new_service, staged, validated


def test_pdf_is_accepted():
    assert make_manifest(filename="policy.pdf").filename == "policy.pdf"


def test_doc_is_rejected():
    with pytest.raises(ValueError):
        make_manifest(filename="legacy.doc")


def test_xls_is_rejected():
    with pytest.raises(ValueError):
        make_manifest(filename="legacy.xls")


def test_non_private_source_is_rejected():
    with pytest.raises(ValueError):
        UploadManifest(uuid4(), uuid4(), uuid4(), 1, "x", "a.pdf", "https://source", "a" * 64, 1, "application/pdf", DataClassification.PUBLIC)


def test_internal_upload_requires_department():
    with pytest.raises(ValueError):
        make_manifest(classification=DataClassification.INTERNAL)


def test_sha256_must_be_a_digest():
    with pytest.raises(ValueError):
        make_manifest(sha256="not-a-digest")


def test_upload_size_limit_is_enforced():
    with pytest.raises(ValueError):
        UploadManifest(uuid4(), uuid4(), uuid4(), 1, "x", "a.pdf", "private://source", "a" * 64, 200_000_001, "application/pdf", DataClassification.PUBLIC)


def test_manifest_count_mismatch_blocks_staging():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    index = StagedIndex.from_chunks(
        publication_id="p1", tenant_id=manifest.tenant_id, version_id=manifest.version_id,
        content_sha256=manifest.sha256, chunks=record.chunks[:1],
    )
    with pytest.raises(PublicationBlocked):
        service.stage_index(manifest.version_id, manifest.tenant_id, index)


def test_manifest_checksum_mismatch_blocks_staging():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    index = StagedIndex.from_chunks(
        publication_id="p1", tenant_id=manifest.tenant_id, version_id=manifest.version_id,
        content_sha256="f" * 64, chunks=record.chunks,
    )
    with pytest.raises(PublicationBlocked):
        service.stage_index(manifest.version_id, manifest.tenant_id, index)


def test_publication_requires_index_ack():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    index = StagedIndex.from_chunks(
        publication_id="p1", tenant_id=manifest.tenant_id, version_id=manifest.version_id,
        content_sha256=manifest.sha256, chunks=record.chunks,
    )
    service.stage_index(manifest.version_id, manifest.tenant_id, index)
    service.approve_review2(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="r2")
    with pytest.raises(PublicationBlocked):
        service.publish(manifest.version_id, manifest.tenant_id)


def test_approval_expiry_blocks_publication():
    service, clock, _ = new_service()
    manifest, _, reviewer, record = staged(service)
    service.approve_review2(manifest.version_id, manifest.tenant_id, reviewer, idempotency_key="r2")
    clock.advance(minutes=31)
    with pytest.raises(Exception) as error:
        service.publish(manifest.version_id, manifest.tenant_id)
    assert getattr(error.value, "code", None) == "APPROVAL_EXPIRED"
