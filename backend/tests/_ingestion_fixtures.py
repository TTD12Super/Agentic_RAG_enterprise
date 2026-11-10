from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from backend.app.ingestion import (
    DataClassification,
    IngestionService,
    ScanReport,
    ScanVerdict,
    StagedIndex,
    UploadManifest,
)
from backend.app.knowledge.models import ChunkMetadata
from backend.app.observability.audit import InMemoryAuditSink


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 11, 10, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, **kwargs: int) -> None:
        self.value += timedelta(**kwargs)


def new_service(*, with_audit: bool = False) -> tuple[IngestionService, Clock, InMemoryAuditSink | None]:
    clock = Clock()
    sink = InMemoryAuditSink() if with_audit else None
    return IngestionService(clock=clock, audit_sink=sink), clock, sink


def make_manifest(
    *,
    tenant_id: UUID | None = None,
    document_id: UUID | None = None,
    version_id: UUID | None = None,
    version_number: int = 1,
    classification: DataClassification = DataClassification.PUBLIC,
    owner_department_id: UUID | None = None,
    filename: str = "policy.pdf",
    sha256: str = "a" * 64,
) -> UploadManifest:
    return UploadManifest(
        tenant_id=tenant_id or uuid4(),
        document_id=document_id or uuid4(),
        version_id=version_id or uuid4(),
        version_number=version_number,
        title="Policy",
        filename=filename,
        source_uri="private://documents/version",
        sha256=sha256,
        size_bytes=1024,
        mime_type={
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }.get(filename.rsplit(".", 1)[-1], "application/octet-stream"),
        classification=classification,
        owner_department_id=owner_department_id,
    )


def make_chunks(manifest: UploadManifest, *, acl: str = "policy-1") -> tuple[ChunkMetadata, ...]:
    parent_id = uuid4()
    parent = ChunkMetadata(
        chunk_id=parent_id,
        document_id=manifest.document_id,
        version_id=manifest.version_id,
        tenant_id=manifest.tenant_id,
        chunk_index=0,
        acl_policy_ref=acl,
        text_hash="b" * 64,
    )
    child = ChunkMetadata(
        chunk_id=uuid4(),
        document_id=manifest.document_id,
        version_id=manifest.version_id,
        tenant_id=manifest.tenant_id,
        parent_chunk_id=parent_id,
        chunk_index=1,
        text_hash="c" * 64,
    )
    return parent, child


def quarantine(service: IngestionService, manifest: UploadManifest | None = None):
    manifest = manifest or make_manifest()
    job = service.quarantine_upload(manifest, idempotency_key=f"upload-{manifest.version_id}")
    service.scan(manifest.version_id, manifest.tenant_id, ScanReport(ScanVerdict.CLEAN))
    return manifest, job


def validated(service: IngestionService, manifest: UploadManifest | None = None):
    manifest, job = quarantine(service, manifest)
    reviewer = uuid4()
    service.approve_review1(
        manifest.version_id,
        manifest.tenant_id,
        reviewer,
        idempotency_key=f"review-1-{manifest.version_id}",
    )
    record = service.process(manifest.version_id, manifest.tenant_id, make_chunks(manifest))
    return manifest, job, reviewer, record


def staged(service: IngestionService, manifest: UploadManifest | None = None):
    manifest, job, reviewer, record = validated(service, manifest)
    index = StagedIndex.from_chunks(
        publication_id=f"publication-{manifest.version_id}",
        tenant_id=manifest.tenant_id,
        version_id=manifest.version_id,
        content_sha256=manifest.sha256,
        chunks=record.chunks,
    )
    service.stage_index(manifest.version_id, manifest.tenant_id, index)
    service.acknowledge_index(manifest.version_id, manifest.tenant_id)
    return manifest, job, reviewer, service.get_version(manifest.version_id, manifest.tenant_id)


def active(service: IngestionService, manifest: UploadManifest | None = None):
    manifest, job, reviewer, record = staged(service, manifest)
    service.approve_review2(
        manifest.version_id,
        manifest.tenant_id,
        reviewer,
        idempotency_key=f"review-2-{manifest.version_id}",
    )
    return manifest, job, service.publish(manifest.version_id, manifest.tenant_id)
