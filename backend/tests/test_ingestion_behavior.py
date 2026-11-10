import pytest

from backend.app.ingestion import (
    ApprovalBlocked,
    ProcessingStatus,
    PublicationStatus,
    ScanReport,
    ScanVerdict,
)
from backend.tests._ingestion_fixtures import (
    active,
    make_chunks,
    make_manifest,
    new_service,
    quarantine,
    staged,
    validated,
)


def test_upload_starts_quarantined_and_not_retrievable():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    assert service.get_version(manifest.version_id, manifest.tenant_id).metadata.status == ProcessingStatus.QUARANTINED
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()

def test_review_one_requires_clean_scan():
    service, _, _ = new_service()
    manifest = make_manifest()
    service.quarantine_upload(manifest, idempotency_key="upload")
    with pytest.raises(ApprovalBlocked):
        service.approve_review1(manifest.version_id, manifest.tenant_id, manifest.version_id, idempotency_key="review")


def test_clean_review_one_allows_processing():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    assert record.metadata.status == ProcessingStatus.PENDING_REVIEW_2
    assert len(record.chunks) == 2


def test_processing_inherits_parent_acl():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    assert record.chunks[1].acl_policy_ref == record.chunks[0].acl_policy_ref


def test_acknowledged_index_is_still_not_active():
    service, _, _ = new_service()
    manifest, _, _, record = staged(service)
    assert record.publication is not None
    assert service.retrievable_chunks(record.metadata.document_id, record.metadata.tenant_id) == ()


def test_second_review_and_publish_make_version_active():
    service, _, _ = new_service()
    manifest, _, published = active(service)
    assert published.metadata.status == PublicationStatus.ACTIVE
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id)


def test_publishing_new_version_supersedes_previous_version():
    service, _, _ = new_service()
    first_manifest, _, _ = active(service)
    second_manifest = make_manifest(
        tenant_id=first_manifest.tenant_id,
        document_id=first_manifest.document_id,
        version_id=__import__("uuid").uuid4(),
        version_number=2,
        sha256="d" * 64,
    )
    active(service, second_manifest)
    assert service.get_version(first_manifest.version_id, first_manifest.tenant_id).metadata.status == PublicationStatus.SUPERSEDED
    assert service.get_document(first_manifest.document_id, first_manifest.tenant_id).current_version_id == second_manifest.version_id


def test_rejected_scan_is_terminal_and_not_retrievable():
    service, _, _ = new_service()
    manifest = make_manifest()
    service.quarantine_upload(manifest, idempotency_key="upload")
    rejected = service.scan(manifest.version_id, manifest.tenant_id, ScanReport(ScanVerdict.MALWARE, malware_clean=False))
    assert rejected.metadata.status == ProcessingStatus.REJECTED
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()
def test_revoke_active_version_removes_retrieval():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.revoke_version(manifest.version_id, manifest.tenant_id)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_soft_delete_isolates_all_versions():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    deleted = service.soft_delete_document(manifest.document_id, manifest.tenant_id)
    assert deleted.status == "SOFT_DELETED"
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()
