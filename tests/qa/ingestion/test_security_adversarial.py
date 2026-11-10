"""ING-001 security/adversarial QA: 10 deterministic synthetic cases."""

import pytest
from uuid import uuid4

from backend.app.ingestion import (
    DerivedIndexFailure,
    InvalidInput,
    NotFound,
    RetentionBlocked,
)
from backend.app.knowledge.models import ChunkMetadata, inherit_acl

from tests.qa.ingestion._baseline import (
    RuntimeFailureOnRemove,
    active,
    make_chunks,
    make_manifest,
    new_service,
    quarantine,
    service_with_index,
    staged,
)


def test_cross_tenant_version_lookup_is_denied():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    with pytest.raises(NotFound):
        service.get_version(manifest.version_id, uuid4())


def test_cross_tenant_job_lookup_is_denied():
    service, _, _ = new_service()
    manifest, job = quarantine(service)
    with pytest.raises(NotFound):
        service.get_job(job.job_id, uuid4())


def test_cross_tenant_document_lookup_is_denied():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    with pytest.raises(NotFound):
        service.get_document(manifest.document_id, uuid4())


def test_cross_tenant_chunk_scope_is_rejected():
    service, _, _ = new_service()
    manifest, _ = quarantine(service)
    service.approve_review1(manifest.version_id, manifest.tenant_id, uuid4(), idempotency_key="review-1")
    parent, child = make_chunks(manifest)
    foreign_child = child.model_copy(update={"tenant_id": uuid4()})
    with pytest.raises(InvalidInput):
        service.process(manifest.version_id, manifest.tenant_id, (parent, foreign_child))


def test_child_acl_cannot_be_broader_than_parent():
    parent, child = make_chunks(make_manifest())
    with pytest.raises(ValueError):
        inherit_acl(parent, child.model_copy(update={"acl_policy_ref": "broader-policy"}))


def test_derived_staging_state_cannot_authorize_retrieval():
    service, _, _ = new_service()
    manifest, _, _, record = staged(service)
    assert record.publication is not None
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_revoked_authority_denies_even_when_cleanup_is_temporarily_failed():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.derived_index.fail_next = "remove"
    service.revoke_version(manifest.version_id, manifest.tenant_id)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_soft_deleted_document_denies_all_retrieval():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.soft_delete_document(manifest.document_id, manifest.tenant_id)
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id) == ()


def test_legal_hold_blocks_permanent_delete():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.soft_delete_document(manifest.document_id, manifest.tenant_id)
    with pytest.raises(RetentionBlocked):
        service.permanently_delete_document(
            manifest.document_id,
            manifest.tenant_id,
            retention_expired=True,
            legal_hold=True,
        )


def test_cleanup_backend_error_is_wrapped_without_secret_leakage():
    service, _ = service_with_index(RuntimeFailureOnRemove())
    manifest, _, _ = active(service)
    with pytest.raises(DerivedIndexFailure) as error:
        service.revoke_version(manifest.version_id, manifest.tenant_id)
    assert "synthetic-secret-index-error" not in str(error.value)
