import pytest
from uuid import uuid4

from backend.app.ingestion import (
    IngestionError,
    JobState,
    MaintenanceBlocked,
    MaintenanceStatus,
    PublicationBlocked,
)
from backend.tests._ingestion_fixtures import active, make_manifest, new_service, quarantine, staged, validated


def test_upload_idempotency_replays_same_job():
    service, _, _ = new_service()
    manifest = make_manifest()
    first = service.quarantine_upload(manifest, idempotency_key="same")
    second = service.quarantine_upload(manifest, idempotency_key="same")
    assert first.job_id == second.job_id


def test_upload_idempotency_conflict_is_rejected():
    service, _, _ = new_service()
    first = make_manifest()
    service.quarantine_upload(first, idempotency_key="same")
    second = make_manifest(tenant_id=first.tenant_id, document_id=first.document_id, version_id=uuid4(), sha256="b" * 64)
    with pytest.raises(IngestionError) as error:
        service.quarantine_upload(second, idempotency_key="same")
    assert error.value.code == "IDEMPOTENCY_KEY_REUSED"


def test_retry_is_bounded_and_preserves_checksum():
    service, _, _ = new_service()
    manifest, job = quarantine(service)
    service.fail_processing(manifest.version_id, manifest.tenant_id, error_code="TEMPORARY", retryable=True)
    retried = service.retry_job(job.job_id, manifest.tenant_id, content_sha256=manifest.sha256)
    assert retried.attempt == 2 and retried.attempt_id != job.attempt_id


def test_retry_with_changed_checksum_is_denied():
    service, _, _ = new_service()
    manifest, job = quarantine(service)
    service.fail_processing(manifest.version_id, manifest.tenant_id, error_code="TEMPORARY", retryable=True)
    with pytest.raises(IngestionError) as error:
        service.retry_job(job.job_id, manifest.tenant_id, content_sha256="f" * 64)
    assert error.value.code == "CHECKSUM_CHANGED"


def test_non_retryable_failure_is_terminal():
    service, _, _ = new_service()
    manifest, job = quarantine(service)
    failed = service.fail_processing(manifest.version_id, manifest.tenant_id, error_code="INVALID", retryable=False)
    assert failed.state is JobState.FAILED


def test_only_one_maintenance_window_is_active():
    service, _, _ = new_service()
    tenant = make_manifest().tenant_id
    service.start_maintenance(tenant, reason="upload")
    with pytest.raises(MaintenanceBlocked):
        service.start_maintenance(tenant, reason="second")


def test_watchdog_expiry_does_not_auto_approve():
    service, clock, _ = new_service()
    manifest, _ = quarantine(service)
    window = service.start_maintenance(manifest.tenant_id, reason="upload", watchdog_seconds=1)
    clock.advance(seconds=2)
    expired = service.expire_maintenance(window.window_id, manifest.tenant_id)
    assert expired.status is MaintenanceStatus.EXPIRED
    assert service.get_version(manifest.version_id, manifest.tenant_id).metadata.status == "QUARANTINED"


def test_failed_maintenance_can_be_recovered_after_cleanup():
    service, _, _ = new_service()
    tenant = make_manifest().tenant_id
    window = service.start_maintenance(tenant, reason="upload")
    failed = service.fail_maintenance(window.window_id, tenant)
    recovered = service.recover_maintenance(window.window_id, tenant)
    assert failed.status is MaintenanceStatus.FAILED
    assert recovered.status is MaintenanceStatus.RELEASED


def test_audit_sink_receives_lifecycle_events_without_content():
    service, _, sink = new_service(with_audit=True)
    manifest, _, _ = active(service)
    assert sink is not None
    assert any(event.event == "DOCUMENT_PUBLISHED" for event in sink.events)
    assert manifest.sha256 not in repr(sink.events)


def test_publication_failure_keeps_previous_active_version():
    service, _, _ = new_service()
    first, _, _ = active(service)
    second = make_manifest(tenant_id=first.tenant_id, document_id=first.document_id, version_number=2, sha256="d" * 64)
    staged(service, second)
    service.approve_review2(second.version_id, second.tenant_id, uuid4(), idempotency_key="r2")
    service.fail_next_publication()
    with pytest.raises(PublicationBlocked):
        service.publish(second.version_id, second.tenant_id)
    assert service.get_document(first.document_id, first.tenant_id).current_version_id == first.version_id
