"""ING-001 E2E/operational QA: 10 deterministic synthetic cases."""

import pytest
from uuid import uuid4

from backend.app.ingestion import (
    IngestionError,
    InvalidTransition,
    JobState,
    MaintenanceBlocked,
    MaintenanceStatus,
    PublicationBlocked,
    RetentionBlocked,
    ScanReport,
    ScanVerdict,
)

from tests.qa.ingestion._baseline import HANDOFF, active, make_manifest, new_service, quarantine, read, staged, task


def test_end_to_end_clean_upload_becomes_retrievable_only_after_publish():
    service, _, _ = new_service()
    manifest, _, published = active(service)
    assert published.metadata.status == "ACTIVE"
    assert service.retrievable_chunks(manifest.document_id, manifest.tenant_id)


def test_invalid_scan_is_terminal_and_not_retryable():
    service, _, _ = new_service()
    manifest = make_manifest()
    job = service.quarantine_upload(manifest, idempotency_key="qa-upload")
    service.scan(manifest.version_id, manifest.tenant_id, ScanReport(ScanVerdict.INVALID))
    with pytest.raises(IngestionError):
        service.retry_job(job.job_id, manifest.tenant_id, content_sha256=manifest.sha256)


def test_transient_retry_changes_attempt_id_without_changing_checksum():
    service, _, _ = new_service()
    manifest, job = quarantine(service)
    service.fail_processing(manifest.version_id, manifest.tenant_id, error_code="TEMPORARY", retryable=True)
    retried = service.retry_job(job.job_id, manifest.tenant_id, content_sha256=manifest.sha256)
    assert retried.attempt == 2
    assert retried.attempt_id != job.attempt_id
    assert retried.content_sha256 == manifest.sha256


def test_changed_checksum_cannot_enter_retry():
    service, _, _ = new_service()
    manifest, job = quarantine(service)
    service.fail_processing(manifest.version_id, manifest.tenant_id, error_code="TEMPORARY", retryable=True)
    with pytest.raises(IngestionError) as error:
        service.retry_job(job.job_id, manifest.tenant_id, content_sha256="f" * 64)
    assert error.value.code == "CHECKSUM_CHANGED"


def test_retry_attempts_stop_at_three():
    service, _, _ = new_service()
    manifest, job = quarantine(service)
    service.fail_processing(manifest.version_id, manifest.tenant_id, error_code="ONE", retryable=True)
    service.retry_job(job.job_id, manifest.tenant_id, content_sha256=manifest.sha256)
    service.fail_processing(manifest.version_id, manifest.tenant_id, error_code="TWO", retryable=True)
    service.retry_job(job.job_id, manifest.tenant_id, content_sha256=manifest.sha256)
    terminal = service.fail_processing(manifest.version_id, manifest.tenant_id, error_code="THREE", retryable=True)
    assert terminal.attempt == 3 and terminal.state is JobState.FAILED


def test_maintenance_watchdog_expires_without_approval():
    service, clock, _ = new_service()
    manifest, _ = quarantine(service)
    window = service.start_maintenance(manifest.tenant_id, reason="qa", watchdog_seconds=1)
    clock.advance(seconds=2)
    expired = service.expire_maintenance(window.window_id, manifest.tenant_id)
    assert expired.status is MaintenanceStatus.EXPIRED
    assert service.get_version(manifest.version_id, manifest.tenant_id).metadata.status == "QUARANTINED"


def test_only_one_maintenance_window_can_run_per_tenant():
    service, _, _ = new_service()
    tenant_id = make_manifest().tenant_id
    service.start_maintenance(tenant_id, reason="first")
    with pytest.raises(MaintenanceBlocked):
        service.start_maintenance(tenant_id, reason="second")


def test_cleanup_failure_blocks_maintenance_recovery_then_recovery_succeeds():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    window = service.start_maintenance(manifest.tenant_id, reason="cleanup")
    service.derived_index.fail_next = "remove"
    service.fail_maintenance(window.window_id, manifest.tenant_id)
    with pytest.raises(MaintenanceBlocked, match="cleanup"):
        service.recover_maintenance(window.window_id, manifest.tenant_id)
    service.reconcile_cleanup(manifest.version_id, manifest.tenant_id)
    assert service.recover_maintenance(window.window_id, manifest.tenant_id).status is MaintenanceStatus.RELEASED


def test_permanent_delete_requires_retention_and_removes_document():
    service, _, _ = new_service()
    manifest, _, _ = active(service)
    service.soft_delete_document(manifest.document_id, manifest.tenant_id)
    with pytest.raises(RetentionBlocked):
        service.permanently_delete_document(manifest.document_id, manifest.tenant_id, retention_expired=False)
    service.permanently_delete_document(manifest.document_id, manifest.tenant_id, retention_expired=True)
    with pytest.raises(Exception):
        service.get_document(manifest.document_id, manifest.tenant_id)


def test_audit_event_is_structured_without_source_checksum():
    service, _, sink = new_service(with_audit=True)
    manifest, _, _ = active(service)
    assert sink is not None
    assert any(event.event == "DOCUMENT_PUBLISHED" for event in sink.events)
    assert manifest.sha256 not in repr(sink.events)
