import pytest
from uuid import uuid4

from backend.app.ingestion import (
    ApprovalBlocked,
    NotFound,
    PublicationBlocked,
    RetentionBlocked,
    ScanReport,
    ScanVerdict,
    StagedIndex,
)
from backend.tests._ingestion_fixtures import active, make_manifest, new_service, quarantine, staged, validated


def test_ingestion_integration_happy_path():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id)


def test_unscanned_upload_cannot_be_approved():
    service, _, _ = new_service()
    manifest = make_manifest()
    service.quarantine_upload(manifest, idempotency_key="u")
    with pytest.raises(ApprovalBlocked):
        service.approve_review1(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="r1")


def test_staged_version_is_invisible_until_publish():
    service, _, _ = new_service()
    manifest, _, _, _ = staged(service)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_index_ack_is_a_publication_gate():
    service, _, _ = new_service()
    manifest, _, _, record = validated(service)
    staged_index = StagedIndex.from_chunks(
        publication_id="integration-index",
        tenant_id=manifest.tenant_id,
        version_id=manifest.version_id,
        content_sha256=manifest.sha256,
        chunks=record.chunks,
    )
    service.stage_index(manifest.version_id, manifest.tenant_id, staged_index)
    service.approve_review2(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="r2")
    with pytest.raises(PublicationBlocked):
        service.publish(manifest.version_id, manifest.tenant_id)


def test_scan_rejection_is_not_retryable():
    service, _, _ = new_service()
    manifest = make_manifest()
    job = service.quarantine_upload(manifest, idempotency_key="u")
    service.scan(manifest.version_id, manifest.tenant_id, ScanReport(ScanVerdict.MALWARE, malware_clean=False))
    with pytest.raises(Exception):
        service.retry_job(job.job_id, manifest.tenant_id, content_sha256=manifest.sha256)


def test_new_version_failure_keeps_old_active():
    service, _, _ = new_service()
    first, _, _ = active(service)
    second = make_manifest(tenant_id=first.tenant_id, document_id=first.document_id, version_number=2, sha256="d" * 64)
    staged(service, second)
    service.approve_review2(second.version_id, second.tenant_id, uuid4(), idempotency_key="r2")
    service.fail_next_publication()
    with pytest.raises(PublicationBlocked):
        service.publish(second.version_id, second.tenant_id)
    assert service.get_document(first.document_id, first.tenant_id).current_version_id == first.version_id


def test_revocation_isolation_is_immediate():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.revoke_version(manifest.version_id, manifest.tenant_id)
    assert not service.retrievable_chunks(manifest.document_id, manifest.tenant_id)

def test_soft_delete_isolation_is_immediate():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.soft_delete_document(manifest.document_id, manifest.tenant_id)
    assert not service.retrievable_chunks(manifest.document_id, manifest.tenant_id)
def test_tenant_scope_isolation_is_fail_closed():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    with pytest.raises(NotFound):
        service.get_version(manifest.version_id, uuid4())


def test_permanent_delete_requires_retention_and_no_legal_hold():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.soft_delete_document(manifest.document_id, manifest.tenant_id)
    with pytest.raises(RetentionBlocked):
        service.permanently_delete_document(manifest.document_id, manifest.tenant_id, retention_expired=False)
    service.permanently_delete_document(manifest.document_id, manifest.tenant_id, retention_expired=True)
    assert not service.retrievable_chunks(manifest.document_id, manifest.tenant_id)
