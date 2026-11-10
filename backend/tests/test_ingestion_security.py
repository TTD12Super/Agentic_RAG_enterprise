import pytest
from uuid import uuid4

from backend.app.ingestion import (
    DerivedIndexFailure,
    InvalidInput,
    NotFound,
    PublicationBlocked,
    RetentionBlocked,
    ScanReport,
    ScanVerdict,
    StagedIndex,
)
from backend.app.knowledge.models import ChunkMetadata, inherit_acl
from backend.tests._ingestion_fixtures import active, make_chunks, make_manifest, new_service, quarantine, staged


def test_cross_tenant_version_lookup_is_denied():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    with pytest.raises(NotFound):
        service.get_version(manifest.version_id, uuid4())


def test_root_chunk_without_acl_fails_closed():
    service, _, _ = new_service()
    manifest, _ = __import__("backend.tests._ingestion_fixtures", fromlist=["quarantine"]).quarantine(service)
    service.approve_review1(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="r1")
    chunk = ChunkMetadata(
        chunk_id=uuid4(), tenant_id=manifest.tenant_id, document_id=manifest.document_id,
        version_id=manifest.version_id, chunk_index=0, text_hash="a" * 64,
    )
    with pytest.raises(InvalidInput):
        service.process(manifest.version_id, manifest.tenant_id, (chunk,))


def test_staging_index_cannot_be_retrieved():
    service, _, _ = new_service()
    manifest, _, _, record = staged(service)
    assert service.retrievable_chunks(record.metadata.document_id, record.metadata.tenant_id) == ()


def test_rejected_version_cannot_be_retrieved():
    service, _, _ = new_service()
    manifest = make_manifest()
    service.quarantine_upload(manifest, idempotency_key="u")
    service.scan(manifest.version_id, manifest.tenant_id, ScanReport(ScanVerdict.SUSPICIOUS))
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()

def test_revoked_version_cannot_be_retrieved_from_derived_state():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.revoke_version(manifest.version_id, manifest.tenant_id)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()
def test_superseded_version_is_removed_from_derived_state():
    service, _, _ = new_service()
    first, _, _ = active(service)
    second = make_manifest(tenant_id=first.tenant_id, document_id=first.document_id, version_number=2, sha256="d" * 64)
    active(service, second)
    first_record = service.get_version(first.version_id, first.tenant_id)
    assert first_record.metadata.status == "SUPERSEDED"
    assert all(chunk.index_state == "REMOVED" for chunk in first_record.chunks)


def test_derived_index_cannot_authorize_non_active_version():
    service, _, _ = new_service()
    manifest, _, _, record = staged(service)
    assert record.publication is not None
    service.derived_index.publish(record.publication.publication_id)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_child_acl_broadening_is_denied():
    parent, child = make_chunks(make_manifest())
    broadened = child.model_copy(update={"acl_policy_ref": "broader"})
    with pytest.raises(ValueError):
        inherit_acl(parent, broadened)


def test_legal_hold_blocks_permanent_delete():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.soft_delete_document(manifest.document_id, manifest.tenant_id)
    with pytest.raises(RetentionBlocked):
        service.permanently_delete_document(manifest.document_id, manifest.tenant_id, retention_expired=True, legal_hold=True)


def test_derived_cleanup_failure_still_denies_retrieval():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.derived_index.fail_next = "remove"
    service.revoke_version(manifest.version_id, manifest.tenant_id)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()
