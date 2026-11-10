"""ING-001 behavior/component QA: 10 deterministic synthetic cases."""

import pytest
from uuid import uuid4

from backend.app.ingestion import (
    ApprovalBlocked,
    ProcessingStatus,
    PublicationStatus,
    ScanReport,
    ScanVerdict,
)

from tests.qa.ingestion._baseline import active, make_chunks, make_manifest, new_service, quarantine, staged, validated


def test_upload_is_quarantined_and_invisible():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    assert service.get_version(manifest.version_id, manifest.tenant_id).metadata.status == ProcessingStatus.QUARANTINED
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_malware_scan_is_terminal():
    service, _, _ = new_service()
    manifest = make_manifest()
    service.quarantine_upload(manifest, idempotency_key="upload")
    result = service.scan(
        manifest.version_id,
        manifest.tenant_id,
        ScanReport(ScanVerdict.MALWARE, malware_clean=False),
    )
    assert result.metadata.status == ProcessingStatus.REJECTED
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_review_one_requires_clean_scan():
    service, _, _ = new_service()
    manifest = make_manifest()
    service.quarantine_upload(manifest, idempotency_key="upload")
    with pytest.raises(ApprovalBlocked):
        service.approve_review1(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="review-1")


def test_review_one_and_processing_require_parent_acl():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    service.approve_review1(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="review-1")
    parent, child = make_chunks(manifest)
    result = service.process(manifest.version_id, manifest.tenant_id, (parent, child))
    assert result.metadata.status == ProcessingStatus.PENDING_REVIEW_2
    assert result.chunks[1].acl_policy_ref == result.chunks[0].acl_policy_ref


def test_empty_processing_input_is_rejected():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    service.approve_review1(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="review-1")
    with pytest.raises(Exception) as error:
        service.process(manifest.version_id, manifest.tenant_id, ())
    assert getattr(error.value, "code", None) == "CHUNKS_EMPTY"


def test_staging_is_not_retrievable_before_ack_and_publish():
    service, _, _ = new_service()
    manifest, _, _, record = staged(service)
    assert record.publication is not None
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_second_review_is_required_after_index_ack():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    from backend.app.ingestion import StagedIndex

    service.stage_index(
        manifest.version_id,
        manifest.tenant_id,
        StagedIndex.from_chunks(
            publication_id="qa-review-2",
            tenant_id=manifest.tenant_id,
            version_id=manifest.version_id,
            content_sha256=manifest.sha256,
            chunks=record.chunks,
        ),
    )
    service.acknowledge_index(manifest.version_id, manifest.tenant_id)
    with pytest.raises(ApprovalBlocked):
        service.publish(manifest.version_id, manifest.tenant_id)


def test_publish_activates_authoritative_version_and_chunks():
    service, _, _ = new_service()
    manifest, _, published = active(service)
    assert published.metadata.status == PublicationStatus.ACTIVE
    assert all(chunk.index_state == "ACTIVE" for chunk in published.chunks)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id)


def test_new_active_version_supersedes_previous_version():
    service, _, _ = new_service()
    first, _, _ = active(service)
    second = make_manifest(
        tenant_id=first.tenant_id,
        document_id=first.document_id,
        version_number=2,
        sha256="d" * 64,
    )
    active(service, second)
    assert service.get_version(first.version_id, first.tenant_id).metadata.status == PublicationStatus.SUPERSEDED
    assert service.get_document(first.document_id, first.tenant_id).current_version_id == second.version_id


def test_approval_expiry_blocks_processing():
    service, clock, _ = new_service()
    manifest, _ = quarantine(service)
    service.approve_review1(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="review-1")
    clock.advance(minutes=31)
    with pytest.raises(ApprovalBlocked) as error:
        service.process(manifest.version_id, manifest.tenant_id, make_chunks(manifest))
    assert error.value.code == "APPROVAL_EXPIRED"
