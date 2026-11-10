"""Provider-neutral document ingestion and publication lifecycle.

The in-memory stores are deterministic test doubles.  A PostgreSQL adapter can
persist the same atomic transitions; the derived index is never authoritative.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import hashlib
import re
from threading import RLock
from typing import Final, Protocol
from uuid import UUID, uuid4

from ..knowledge.models import (
    ChunkMetadata,
    DocumentVersionMetadata,
    inherit_acl,
)
from ..observability.audit import AuditSink, append_audit_event
from ..observability.context import CorrelationContext
from ..models.policy import DataClassification


MAX_UPLOAD_BYTES: Final = 200_000_000
APPROVAL_TTL: Final = timedelta(minutes=30)
MAX_ATTEMPTS: Final = 3
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


class ProcessingStatus(StrEnum):
    QUARANTINED = "QUARANTINED"
    REVIEW_1_APPROVED = "REVIEW_1_APPROVED"
    PROCESSING = "PROCESSING"
    PROCESS_VALIDATED = "PROCESS_VALIDATED"
    PENDING_REVIEW_2 = "PENDING_REVIEW_2"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class PublicationStatus(StrEnum):
    NOT_PUBLISHED = "NOT_PUBLISHED"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REVOKED = "REVOKED"
    SOFT_DELETED = "SOFT_DELETED"


class JobState(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"


class JobStage(StrEnum):
    QUARANTINE = "QUARANTINE"
    SCAN = "SCAN"
    REVIEW_1 = "REVIEW_1"
    PARSING = "PARSING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    VECTOR_INDEXING = "VECTOR_INDEXING"
    INDEX_VALIDATION = "INDEX_VALIDATION"
    REVIEW_2 = "REVIEW_2"
    PUBLICATION = "PUBLICATION"
    CLEANUP = "CLEANUP"


class ScanVerdict(StrEnum):
    CLEAN = "CLEAN"
    MALWARE = "MALWARE"
    SUSPICIOUS = "SUSPICIOUS"
    INVALID = "INVALID"


class IndexPublicationStatus(StrEnum):
    STAGING = "STAGING"
    ACKED = "ACKED"
    PUBLISHED = "PUBLISHED"
    REMOVED = "REMOVED"


class MaintenanceStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class IngestionError(Exception):
    """Safe, typed lifecycle failure; messages never contain source content."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


class InvalidInput(IngestionError):
    pass


class NotFound(IngestionError):
    pass


class InvalidTransition(IngestionError):
    pass


class ApprovalBlocked(IngestionError):
    pass


class PublicationBlocked(IngestionError):
    pass


class MaintenanceBlocked(IngestionError):
    pass


class RetentionBlocked(IngestionError):
    pass


class IdempotencyConflict(IngestionError):
    pass


class DerivedIndexFailure(IngestionError):
    pass


@dataclass(frozen=True, slots=True)
class UploadManifest:
    tenant_id: UUID
    document_id: UUID
    version_id: UUID
    version_number: int
    title: str
    filename: str
    source_uri: str
    sha256: str
    size_bytes: int
    mime_type: str
    classification: DataClassification
    owner_department_id: UUID | None = None
    magic_valid: bool = True

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "classification", DataClassification(self.classification))
        except ValueError as error:
            raise ValueError("classification is invalid") from error
        if self.version_number <= 0 or not self.title.strip() or not self.filename.strip():
            raise ValueError("invalid upload identity")
        if not self.source_uri.startswith("private://"):
            raise ValueError("source_uri must be private")
        if not _SHA256.fullmatch(self.sha256):
            raise ValueError("sha256 must be hexadecimal")
        if not 0 <= self.size_bytes <= MAX_UPLOAD_BYTES:
            raise ValueError("upload exceeds the approved size limit")
        if self.classification is DataClassification.INTERNAL and self.owner_department_id is None:
            raise ValueError("internal uploads require an owner department")
        suffix = self.filename.rsplit(".", 1)[-1].lower() if "." in self.filename else ""
        allowed_mimes = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        if suffix not in allowed_mimes or self.mime_type != allowed_mimes[suffix]:
            raise ValueError("unsupported or mismatched document format")
        if not self.magic_valid:
            raise ValueError("document signature is invalid")


@dataclass(frozen=True, slots=True)
class ScanReport:
    verdict: ScanVerdict
    signature_valid: bool = True
    malware_clean: bool = True
    scan_id: str = "scan-local"

    @property
    def passed(self) -> bool:
        return (
            self.verdict is ScanVerdict.CLEAN
            and self.signature_valid
            and self.malware_clean
        )


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    stage: int
    reviewer_id: UUID
    decision: str
    idempotency_key: str
    attempt_number: int
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class IndexManifest:
    content_sha256: str
    expected_chunk_count: int
    chunk_digest: str
    acl_digest: str
    index_generation: str


@dataclass(frozen=True, slots=True)
class StagedIndex:
    publication_id: str
    tenant_id: UUID
    version_id: UUID
    chunks: tuple[ChunkMetadata, ...]
    manifest: IndexManifest

    @classmethod
    def from_chunks(
        cls,
        *,
        publication_id: str,
        tenant_id: UUID,
        version_id: UUID,
        content_sha256: str,
        chunks: tuple[ChunkMetadata, ...],
        index_generation: str = "local-1",
    ) -> "StagedIndex":
        chunk_digest = _chunk_digest(chunks)
        acl_digest = _acl_digest(chunks)
        return cls(
            publication_id=publication_id,
            tenant_id=tenant_id,
            version_id=version_id,
            chunks=chunks,
            manifest=IndexManifest(
                content_sha256=content_sha256,
                expected_chunk_count=len(chunks),
                chunk_digest=chunk_digest,
                acl_digest=acl_digest,
                index_generation=index_generation,
            ),
        )


@dataclass(frozen=True, slots=True)
class IndexPublication:
    publication_id: str
    tenant_id: UUID
    version_id: UUID
    manifest: IndexManifest
    status: IndexPublicationStatus
    fencing_token: int


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    tenant_id: UUID
    document_id: UUID
    title: str
    classification: DataClassification
    owner_department_id: UUID | None
    status: str
    current_version_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class IngestionJob:
    job_id: UUID
    tenant_id: UUID
    document_id: UUID
    version_id: UUID
    content_sha256: str
    state: JobState
    current_stage: JobStage
    attempt: int
    attempt_id: UUID
    error_code: str | None = None


@dataclass(frozen=True, slots=True)
class VersionRecord:
    metadata: DocumentVersionMetadata
    job_id: UUID
    scan: ScanReport | None = None
    approvals: tuple[ApprovalRecord, ...] = ()
    chunks: tuple[ChunkMetadata, ...] = ()
    publication: IndexPublication | None = None


@dataclass(frozen=True, slots=True)
class MaintenanceWindow:
    window_id: UUID
    tenant_id: UUID
    status: MaintenanceStatus
    reason: str
    started_at: datetime
    watchdog_at: datetime
    ended_at: datetime | None = None


class DerivedIndex(Protocol):
    """Qdrant/search projection boundary; it cannot decide retrieval eligibility."""

    def stage(self, publication: IndexPublication, chunks: tuple[ChunkMetadata, ...]) -> None: ...

    def acknowledge(self, publication_id: str) -> None: ...

    def publish(self, publication_id: str) -> None: ...

    def remove(self, publication_id: str) -> None: ...


@dataclass(frozen=True, slots=True)
class DerivedIndexRecord:
    publication: IndexPublication
    chunks: tuple[ChunkMetadata, ...]


class InMemoryDerivedIndex:
    """Deterministic Qdrant stand-in with injectable failure points."""

    def __init__(self) -> None:
        self.records: dict[str, DerivedIndexRecord] = {}
        self.fail_next: str | None = None

    def _fail_if_requested(self, operation: str) -> None:
        if self.fail_next == operation:
            self.fail_next = None
            raise DerivedIndexFailure("INDEX_UNAVAILABLE", "derived index operation failed", retryable=True)

    def stage(self, publication: IndexPublication, chunks: tuple[ChunkMetadata, ...]) -> None:
        self._fail_if_requested("stage")
        existing = self.records.get(publication.publication_id)
        if existing is not None and existing.publication.version_id != publication.version_id:
            raise DerivedIndexFailure("INDEX_PUBLICATION_CONFLICT", "publication identifier is already in use")
        self.records[publication.publication_id] = DerivedIndexRecord(publication, chunks)

    def acknowledge(self, publication_id: str) -> None:
        self._fail_if_requested("acknowledge")
        record = self.records.get(publication_id)
        if record is None:
            raise DerivedIndexFailure("INDEX_NOT_FOUND", "derived index publication is unavailable")
        self.records[publication_id] = replace(
            record,
            publication=replace(record.publication, status=IndexPublicationStatus.ACKED),
        )

    def publish(self, publication_id: str) -> None:
        self._fail_if_requested("publish")
        record = self.records.get(publication_id)
        if record is None or record.publication.status is not IndexPublicationStatus.ACKED:
            raise DerivedIndexFailure("INDEX_NOT_READY", "derived index publication is not acknowledged")
        self.records[publication_id] = replace(
            record,
            publication=replace(record.publication, status=IndexPublicationStatus.PUBLISHED),
            chunks=tuple(_chunk_state(chunk, "ACTIVE") for chunk in record.chunks),
        )

    def remove(self, publication_id: str) -> None:
        self._fail_if_requested("remove")
        record = self.records.get(publication_id)
        if record is None:
            return
        self.records[publication_id] = replace(
            record,
            publication=replace(record.publication, status=IndexPublicationStatus.REMOVED),
            chunks=tuple(_chunk_state(chunk, "REMOVED") for chunk in record.chunks),
        )


def _chunk_digest(chunks: tuple[ChunkMetadata, ...]) -> str:
    material = "|".join(
        f"{chunk.chunk_index}:{chunk.chunk_id}:{chunk.text_hash}:{chunk.acl_policy_ref or ''}"
        for chunk in sorted(chunks, key=lambda item: item.chunk_index)
    )
    return hashlib.sha256(material.encode()).hexdigest()


def _acl_digest(chunks: tuple[ChunkMetadata, ...]) -> str:
    material = "|".join(
        f"{chunk.chunk_index}:{chunk.acl_policy_ref or ''}"
        for chunk in sorted(chunks, key=lambda item: item.chunk_index)
    )
    return hashlib.sha256(material.encode()).hexdigest()


def _status(metadata: DocumentVersionMetadata, status: str) -> DocumentVersionMetadata:
    return metadata.model_copy(update={"status": status})


def _chunk_state(chunk: ChunkMetadata, state: str) -> ChunkMetadata:
    return chunk.model_copy(update={"index_state": state})


class IngestionService:
    """Fail-closed lifecycle service backed by an in-memory authority double."""

    def __init__(
        self,
        *,
        derived_index: DerivedIndex | None = None,
        audit_sink: AuditSink | None = None,
        context: CorrelationContext | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.derived_index = derived_index or InMemoryDerivedIndex()
        self.audit_sink = audit_sink
        self.context = context or CorrelationContext.from_headers({})
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self._documents: dict[tuple[UUID, UUID], DocumentRecord] = {}
        self._versions: dict[UUID, VersionRecord] = {}
        self._jobs: dict[UUID, IngestionJob] = {}
        self._idempotency: dict[tuple[UUID, str], tuple[str, UUID]] = {}
        self._maintenance: dict[UUID, MaintenanceWindow] = {}
        self._active_maintenance: dict[UUID, UUID] = {}
        self._cleanup_pending: set[UUID] = set()
        self._deleted_documents: set[tuple[UUID, UUID]] = set()
        self._fencing = 0
        self._fail_next_publication = False
        self._lock = RLock()

    def quarantine_upload(self, manifest: UploadManifest, *, idempotency_key: str) -> IngestionJob:
        """Create a non-searchable version before any parser or model work."""

        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise InvalidInput("IDEMPOTENCY_REQUIRED", "upload idempotency key is required")
        fingerprint = self._upload_fingerprint(manifest)
        with self._lock:
            previous = self._idempotency.get((manifest.tenant_id, idempotency_key))
            if previous is not None:
                if previous[0] != fingerprint:
                    raise IdempotencyConflict("IDEMPOTENCY_CONFLICT", "upload idempotency key was reused")
                return self._jobs[previous[1]]
            document_key = (manifest.tenant_id, manifest.document_id)
            if document_key in self._deleted_documents:
                raise InvalidTransition("DOCUMENT_PURGED", "document cannot be recreated")
            document = self._documents.get(document_key)
            if document is None:
                document = DocumentRecord(
                    tenant_id=manifest.tenant_id,
                    document_id=manifest.document_id,
                    title=manifest.title,
                    classification=manifest.classification,
                    owner_department_id=manifest.owner_department_id,
                    status="ACTIVE",
                )
                self._documents[document_key] = document
            elif document.classification is not manifest.classification:
                raise InvalidInput("CLASSIFICATION_MISMATCH", "document classification cannot change in upload")
            if any(
                record.metadata.tenant_id == manifest.tenant_id
                and record.metadata.document_id == manifest.document_id
                and record.metadata.version_number == manifest.version_number
                for record in self._versions.values()
            ):
                raise IdempotencyConflict("VERSION_EXISTS", "document version already exists")
            try:
                metadata = DocumentVersionMetadata(
                    version_id=manifest.version_id,
                    document_id=manifest.document_id,
                    tenant_id=manifest.tenant_id,
                    version_number=manifest.version_number,
                    source_uri=manifest.source_uri,
                    sha256=manifest.sha256,
                    status=ProcessingStatus.QUARANTINED.value,
                )
            except ValueError as error:
                raise InvalidInput("UPLOAD_INVALID", "upload metadata is invalid") from error
            job_id = uuid4()
            job = IngestionJob(
                job_id=job_id,
                tenant_id=manifest.tenant_id,
                document_id=manifest.document_id,
                version_id=manifest.version_id,
                content_sha256=manifest.sha256.lower(),
                state=JobState.QUEUED,
                current_stage=JobStage.QUARANTINE,
                attempt=1,
                attempt_id=uuid4(),
            )
            self._versions[manifest.version_id] = VersionRecord(metadata=metadata, job_id=job_id)
            self._jobs[job_id] = job
            self._idempotency[(manifest.tenant_id, idempotency_key)] = (fingerprint, job_id)
            self._audit("DOCUMENT_UPLOAD_QUARANTINED", "document:create", manifest.tenant_id, manifest.version_id)
            return job

    def scan(self, version_id: UUID, tenant_id: UUID, report: ScanReport) -> VersionRecord:
        with self._lock:
            record = self._version(version_id, tenant_id)
            self._require_status(record, ProcessingStatus.QUARANTINED.value)
            job = self._jobs[record.job_id]
            if not report.passed:
                rejected = replace(
                    record,
                    metadata=_status(record.metadata, ProcessingStatus.REJECTED.value),
                    scan=report,
                )
                self._versions[version_id] = rejected
                self._jobs[job.job_id] = replace(
                    job,
                    state=JobState.FAILED,
                    current_stage=JobStage.SCAN,
                    error_code="SCAN_REJECTED",
                )
                self._audit("DOCUMENT_SCAN_REJECTED", "document:scan", tenant_id, version_id, code="SCAN_REJECTED")
                return rejected
            updated = replace(record, scan=report)
            self._versions[version_id] = updated
            self._jobs[job.job_id] = replace(job, current_stage=JobStage.REVIEW_1)
            self._audit("DOCUMENT_SCAN_PASSED", "document:scan", tenant_id, version_id)
            return updated

    def approve_review1(
        self,
        version_id: UUID,
        tenant_id: UUID,
        reviewer_id: UUID,
        *,
        idempotency_key: str,
    ) -> VersionRecord:
        return self._approve(version_id, tenant_id, reviewer_id, stage=1, idempotency_key=idempotency_key)

    def approve_review2(
        self,
        version_id: UUID,
        tenant_id: UUID,
        reviewer_id: UUID,
        *,
        idempotency_key: str,
    ) -> VersionRecord:
        return self._approve(version_id, tenant_id, reviewer_id, stage=2, idempotency_key=idempotency_key)

    def reject_review(
        self,
        version_id: UUID,
        tenant_id: UUID,
        reviewer_id: UUID,
        *,
        stage: int,
        idempotency_key: str,
    ) -> VersionRecord:
        if stage not in {1, 2}:
            raise InvalidInput("APPROVAL_STAGE_INVALID", "approval stage is invalid")
        with self._lock:
            record = self._version(version_id, tenant_id)
            expected = ProcessingStatus.QUARANTINED.value if stage == 1 else ProcessingStatus.PENDING_REVIEW_2.value
            self._require_status(record, expected)
            approval = ApprovalRecord(stage, reviewer_id, "REJECT", idempotency_key, 1, self._now())
            updated = replace(record, metadata=_status(record.metadata, ProcessingStatus.REJECTED.value), approvals=record.approvals + (approval,))
            self._versions[version_id] = updated
            self._remove_publication(updated)
            job = self._jobs[record.job_id]
            self._jobs[job.job_id] = replace(job, state=JobState.FAILED, error_code="REVIEW_REJECTED")
            self._audit("DOCUMENT_REVIEW_REJECTED", "document:approve", tenant_id, version_id, code="REVIEW_REJECTED")
            return updated

    def process(self, version_id: UUID, tenant_id: UUID, chunks: tuple[ChunkMetadata, ...]) -> VersionRecord:
        with self._lock:
            record = self._version(version_id, tenant_id)
            self._require_status(record, ProcessingStatus.REVIEW_1_APPROVED.value)
            self._require_approval_live(record, 1)
            job = self._jobs[record.job_id]
            self._versions[version_id] = replace(record, metadata=_status(record.metadata, ProcessingStatus.PROCESSING.value))
            self._jobs[job.job_id] = replace(job, state=JobState.RUNNING, current_stage=JobStage.PARSING)
            try:
                normalized = self._validate_chunks(record, chunks)
            except IngestionError:
                failed = replace(
                    self._versions[version_id],
                    metadata=_status(self._versions[version_id].metadata, ProcessingStatus.FAILED.value),
                )
                self._versions[version_id] = failed
                self._jobs[job.job_id] = replace(
                    self._jobs[job.job_id],
                    state=JobState.FAILED,
                    current_stage=JobStage.INDEX_VALIDATION,
                    error_code="INVALID_CHUNKS",
                )
                self._audit("INGESTION_FAILED", "document:process", tenant_id, version_id, code="INVALID_CHUNKS")
                raise
            updated = replace(
                self._versions[version_id],
                metadata=_status(self._versions[version_id].metadata, ProcessingStatus.PENDING_REVIEW_2.value),
                chunks=normalized,
            )
            self._versions[version_id] = updated
            self._jobs[job.job_id] = replace(
                self._jobs[job.job_id],
                state=JobState.COMPLETED,
                current_stage=JobStage.INDEX_VALIDATION,
            )
            self._audit("INGESTION_VALIDATED", "document:process", tenant_id, version_id)
            return updated

    def stage_index(self, version_id: UUID, tenant_id: UUID, staged: StagedIndex) -> IndexPublication:
        with self._lock:
            record = self._version(version_id, tenant_id)
            self._require_status(record, ProcessingStatus.PENDING_REVIEW_2.value)
            if record.publication is not None and record.publication.status is not IndexPublicationStatus.REMOVED:
                raise PublicationBlocked("INDEX_ALREADY_STAGED", "an index is already staged for this version")
            if staged.tenant_id != tenant_id or staged.version_id != version_id:
                raise InvalidInput("INDEX_SCOPE_MISMATCH", "staged index scope is invalid")
            self._validate_manifest(record, staged)
            self._fencing += 1
            publication = IndexPublication(
                publication_id=staged.publication_id,
                tenant_id=tenant_id,
                version_id=version_id,
                manifest=staged.manifest,
                status=IndexPublicationStatus.STAGING,
                fencing_token=self._fencing,
            )
            try:
                self.derived_index.stage(publication, record.chunks)
            except IngestionError:
                raise
            except Exception as error:
                raise DerivedIndexFailure("INDEX_UNAVAILABLE", "derived index operation failed", retryable=True) from error
            updated = replace(record, publication=publication)
            self._versions[version_id] = updated
            self._jobs[record.job_id] = replace(self._jobs[record.job_id], current_stage=JobStage.INDEX_VALIDATION)
            self._audit("INDEX_STAGED", "document:index", tenant_id, version_id)
            return publication

    def acknowledge_index(self, version_id: UUID, tenant_id: UUID) -> IndexPublication:
        with self._lock:
            record = self._version(version_id, tenant_id)
            publication = record.publication
            if publication is None or publication.status is not IndexPublicationStatus.STAGING:
                raise PublicationBlocked("INDEX_NOT_STAGED", "index publication is not staged")
            try:
                self.derived_index.acknowledge(publication.publication_id)
            except IngestionError:
                raise
            except Exception as error:
                raise DerivedIndexFailure("INDEX_UNAVAILABLE", "derived index operation failed", retryable=True) from error
            publication = replace(publication, status=IndexPublicationStatus.ACKED)
            self._versions[version_id] = replace(record, publication=publication)
            self._jobs[record.job_id] = replace(self._jobs[record.job_id], current_stage=JobStage.REVIEW_2)
            self._audit("INDEX_ACKNOWLEDGED", "document:index", tenant_id, version_id)
            return publication

    def publish(self, version_id: UUID, tenant_id: UUID) -> VersionRecord:
        with self._lock:
            record = self._version(version_id, tenant_id)
            self._require_status(record, ProcessingStatus.PENDING_REVIEW_2.value)
            self._require_approval_live(record, 2)
            publication = record.publication
            if publication is None or publication.status is not IndexPublicationStatus.ACKED:
                raise PublicationBlocked("INDEX_NOT_ACKED", "publication requires an acknowledged index")
            try:
                self.derived_index.publish(publication.publication_id)
                if self._fail_next_publication:
                    self._fail_next_publication = False
                    raise RuntimeError("synthetic publication failure")
                document_key = (tenant_id, record.metadata.document_id)
                document = self._documents[document_key]
                old_id = document.current_version_id
                if old_id is not None:
                    old = self._versions[old_id]
                    self._versions[old_id] = replace(
                        old,
                        metadata=_status(old.metadata, PublicationStatus.SUPERSEDED.value),
                        chunks=tuple(_chunk_state(chunk, "REMOVED") for chunk in old.chunks),
                        publication=replace(old.publication, status=IndexPublicationStatus.REMOVED) if old.publication else None,
                    )
                active = replace(
                    record,
                    metadata=_status(record.metadata, PublicationStatus.ACTIVE.value),
                    chunks=tuple(_chunk_state(chunk, "ACTIVE") for chunk in record.chunks),
                    publication=replace(publication, status=IndexPublicationStatus.PUBLISHED),
                )
                self._versions[version_id] = active
                self._documents[document_key] = replace(document, status="ACTIVE", current_version_id=version_id)
                self._jobs[record.job_id] = replace(self._jobs[record.job_id], current_stage=JobStage.PUBLICATION)
                if old_id is not None:
                    old_publication = self._versions[old_id].publication
                    if old_publication is not None:
                        try:
                            self.derived_index.remove(old_publication.publication_id)
                        except IngestionError:
                            self._cleanup_pending.add(old_id)
                self._audit("DOCUMENT_PUBLISHED", "document:publish", tenant_id, version_id)
                return active
            except IngestionError:
                self._safe_remove(publication.publication_id, version_id)
                self._mark_failed(version_id, "PUBLICATION_FAILED")
                raise
            except Exception as error:
                self._safe_remove(publication.publication_id, version_id)
                self._mark_failed(version_id, "PUBLICATION_FAILED")
                raise PublicationBlocked("PUBLICATION_FAILED", "publication failed", retryable=True) from error

    def revoke_version(self, version_id: UUID, tenant_id: UUID) -> VersionRecord:
        with self._lock:
            record = self._version(version_id, tenant_id)
            if record.metadata.status in {PublicationStatus.REVOKED.value, PublicationStatus.SOFT_DELETED.value}:
                return record
            if record.metadata.status in {ProcessingStatus.REJECTED.value, ProcessingStatus.FAILED.value, ProcessingStatus.CANCELLED.value}:
                raise InvalidTransition("VERSION_TERMINAL", "version is already terminal")
            updated = replace(
                record,
                metadata=_status(record.metadata, PublicationStatus.REVOKED.value),
                chunks=tuple(_chunk_state(chunk, "REMOVED") for chunk in record.chunks),
                publication=replace(record.publication, status=IndexPublicationStatus.REMOVED) if record.publication else None,
            )
            self._versions[version_id] = updated
            document = self._documents[(tenant_id, record.metadata.document_id)]
            if document.current_version_id == version_id:
                self._documents[(tenant_id, record.metadata.document_id)] = replace(
                    document, status="SOFT_DELETED", current_version_id=None
                )
            self._safe_remove(record.publication.publication_id if record.publication else None, version_id)
            self._audit("DOCUMENT_VERSION_REVOKED", "document:revoke", tenant_id, version_id)
            return updated

    def soft_delete_document(self, document_id: UUID, tenant_id: UUID) -> DocumentRecord:
        with self._lock:
            document = self._documents.get((tenant_id, document_id))
            if document is None:
                raise NotFound("DOCUMENT_NOT_FOUND", "document is unavailable")
            for version_id, record in tuple(self._versions.items()):
                if record.metadata.tenant_id != tenant_id or record.metadata.document_id != document_id:
                    continue
                if record.metadata.status not in {PublicationStatus.REVOKED.value, ProcessingStatus.FAILED.value, ProcessingStatus.REJECTED.value}:
                    updated = replace(
                        record,
                        metadata=_status(record.metadata, PublicationStatus.SOFT_DELETED.value),
                        chunks=tuple(_chunk_state(chunk, "REMOVED") for chunk in record.chunks),
                        publication=replace(record.publication, status=IndexPublicationStatus.REMOVED) if record.publication else None,
                    )
                    self._versions[version_id] = updated
                    self._safe_remove(record.publication.publication_id if record.publication else None, version_id)
            deleted = replace(document, status="SOFT_DELETED", current_version_id=None)
            self._documents[(tenant_id, document_id)] = deleted
            self._audit("DOCUMENT_SOFT_DELETED", "document:delete", tenant_id, document_id)
            return deleted

    def permanently_delete_document(
        self,
        document_id: UUID,
        tenant_id: UUID,
        *,
        retention_expired: bool,
        legal_hold: bool = False,
    ) -> None:
        with self._lock:
            if legal_hold:
                raise RetentionBlocked("LEGAL_HOLD", "legal hold blocks permanent deletion")
            if not retention_expired:
                raise RetentionBlocked("RETENTION_ACTIVE", "retention policy blocks permanent deletion")
            document = self._documents.get((tenant_id, document_id))
            if document is None:
                raise NotFound("DOCUMENT_NOT_FOUND", "document is unavailable")
            for version_id, record in tuple(self._versions.items()):
                if record.metadata.tenant_id == tenant_id and record.metadata.document_id == document_id:
                    if record.publication is not None:
                        try:
                            self.derived_index.remove(record.publication.publication_id)
                        except Exception as error:
                            raise PublicationBlocked("CLEANUP_REQUIRED", "derived cleanup is incomplete", retryable=True) from error
                    self._versions.pop(version_id)
            self._documents.pop((tenant_id, document_id))
            self._deleted_documents.add((tenant_id, document_id))
            self._audit("DOCUMENT_PERMANENTLY_DELETED", "document:delete", tenant_id, document_id)

    def start_maintenance(
        self,
        tenant_id: UUID,
        *,
        reason: str,
        watchdog_seconds: int = 3600,
    ) -> MaintenanceWindow:
        if not reason.strip() or not 0 < watchdog_seconds <= 3600:
            raise InvalidInput("MAINTENANCE_INVALID", "maintenance settings are invalid")
        with self._lock:
            if tenant_id in self._active_maintenance:
                raise MaintenanceBlocked("MAINTENANCE_ACTIVE", "maintenance is already active")
            now = self._now()
            window = MaintenanceWindow(uuid4(), tenant_id, MaintenanceStatus.ACTIVE, reason, now, now + timedelta(seconds=watchdog_seconds))
            self._maintenance[window.window_id] = window
            self._active_maintenance[tenant_id] = window.window_id
            self._audit("MAINTENANCE_STARTED", "maintenance:start", tenant_id, window.window_id)
            return window

    def finish_maintenance(self, window_id: UUID, tenant_id: UUID) -> MaintenanceWindow:
        with self._lock:
            window = self._maintenance_for(window_id, tenant_id)
            if window.status is not MaintenanceStatus.ACTIVE:
                raise MaintenanceBlocked("MAINTENANCE_NOT_ACTIVE", "maintenance is not active")
            finished = replace(window, status=MaintenanceStatus.RELEASED, ended_at=self._now())
            self._maintenance[window_id] = finished
            self._active_maintenance.pop(tenant_id, None)
            self._audit("MAINTENANCE_RELEASED", "maintenance:finish", tenant_id, window_id)
            return finished

    def fail_maintenance(self, window_id: UUID, tenant_id: UUID, *, code: str = "MAINTENANCE_FAILED") -> MaintenanceWindow:
        with self._lock:
            window = self._maintenance_for(window_id, tenant_id)
            if window.status is not MaintenanceStatus.ACTIVE:
                raise MaintenanceBlocked("MAINTENANCE_NOT_ACTIVE", "maintenance is not active")
            failed = replace(window, status=MaintenanceStatus.FAILED, ended_at=self._now())
            self._maintenance[window_id] = failed
            self._active_maintenance.pop(tenant_id, None)
            self._cleanup_tenant(tenant_id)
            self._audit("MAINTENANCE_FAILED", "maintenance:fail", tenant_id, window_id, code=code)
            return failed

    def expire_maintenance(self, window_id: UUID, tenant_id: UUID) -> MaintenanceWindow:
        with self._lock:
            window = self._maintenance_for(window_id, tenant_id)
            if window.status is not MaintenanceStatus.ACTIVE or self._now() < window.watchdog_at:
                raise MaintenanceBlocked("MAINTENANCE_NOT_EXPIRED", "maintenance watchdog has not expired")
            expired = replace(window, status=MaintenanceStatus.EXPIRED, ended_at=self._now())
            self._maintenance[window_id] = expired
            self._active_maintenance.pop(tenant_id, None)
            self._cleanup_tenant(tenant_id)
            self._audit("MAINTENANCE_EXPIRED", "maintenance:expire", tenant_id, window_id, code="WATCHDOG_EXPIRED")
            return expired

    def recover_maintenance(self, window_id: UUID, tenant_id: UUID) -> MaintenanceWindow:
        with self._lock:
            window = self._maintenance_for(window_id, tenant_id)
            if window.status not in {MaintenanceStatus.FAILED, MaintenanceStatus.EXPIRED}:
                raise MaintenanceBlocked("MAINTENANCE_NOT_RECOVERABLE", "maintenance is not awaiting recovery")
            if any(
                version_id in self._cleanup_pending
                and self._versions[version_id].metadata.tenant_id == tenant_id
                for version_id in self._versions
            ):
                raise MaintenanceBlocked("CLEANUP_REQUIRED", "derived cleanup is incomplete", retryable=True)
            recovered = replace(window, status=MaintenanceStatus.RELEASED, ended_at=self._now())
            self._maintenance[window_id] = recovered
            self._audit("MAINTENANCE_RECOVERED", "maintenance:recover", tenant_id, window_id)
            return recovered

    def retry_job(self, job_id: UUID, tenant_id: UUID, *, content_sha256: str) -> IngestionJob:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None or job.tenant_id != tenant_id:
                raise NotFound("JOB_NOT_FOUND", "ingestion job is unavailable")
            if job.state is not JobState.RETRY_SCHEDULED:
                raise InvalidTransition("RETRY_NOT_SCHEDULED", "job is not retryable")
            if content_sha256.lower() != job.content_sha256:
                raise InvalidInput("CHECKSUM_CHANGED", "retry checksum does not match the immutable version")
            if job.attempt >= MAX_ATTEMPTS:
                raise InvalidTransition("RETRY_EXHAUSTED", "retry limit reached")
            retried = replace(
                job,
                state=JobState.QUEUED,
                current_stage=JobStage.PARSING,
                attempt=job.attempt + 1,
                attempt_id=uuid4(),
                error_code=None,
            )
            self._jobs[job_id] = retried
            record = self._versions[job.version_id]
            self._versions[job.version_id] = replace(record, metadata=_status(record.metadata, ProcessingStatus.REVIEW_1_APPROVED.value))
            self._audit("INGESTION_RETRY_SCHEDULED", "document:retry", tenant_id, job.version_id)
            return retried

    def fail_processing(
        self,
        version_id: UUID,
        tenant_id: UUID,
        *,
        error_code: str,
        retryable: bool,
    ) -> IngestionJob:
        """Record a bounded worker failure without touching the prior ACTIVE version."""

        with self._lock:
            record = self._version(version_id, tenant_id)
            job = self._jobs[record.job_id]
            if job.state in {JobState.COMPLETED, JobState.CANCELLED}:
                raise InvalidTransition("JOB_TERMINAL", "job cannot be failed from its terminal state")
            self._versions[version_id] = replace(
                record,
                metadata=_status(record.metadata, ProcessingStatus.FAILED.value),
            )
            next_state = JobState.RETRY_SCHEDULED if retryable and job.attempt < MAX_ATTEMPTS else JobState.FAILED
            updated = replace(job, state=next_state, current_stage=JobStage.CLEANUP, error_code=error_code)
            self._jobs[job.job_id] = updated
            self._audit(
                "INGESTION_RETRY_SCHEDULED" if next_state is JobState.RETRY_SCHEDULED else "INGESTION_FAILED",
                "document:process",
                tenant_id,
                version_id,
                code=error_code,
            )
            return updated

    def reconcile_cleanup(self, version_id: UUID, tenant_id: UUID) -> None:
        with self._lock:
            record = self._version(version_id, tenant_id)
            if record.publication is not None:
                try:
                    self.derived_index.remove(record.publication.publication_id)
                except IngestionError:
                    raise
                except Exception as error:
                    raise DerivedIndexFailure("INDEX_UNAVAILABLE", "derived cleanup failed", retryable=True) from error
            self._cleanup_pending.discard(version_id)

    def retrievable_chunks(self, document_id: UUID, tenant_id: UUID) -> tuple[ChunkMetadata, ...]:
        """Return only the DB-approved current ACTIVE projection."""

        with self._lock:
            document = self._documents.get((tenant_id, document_id))
            if document is None or document.status != "ACTIVE" or document.current_version_id is None:
                return ()
            record = self._versions.get(document.current_version_id)
            if record is None or record.metadata.status != PublicationStatus.ACTIVE.value:
                return ()
            if record.publication is None or record.publication.status is not IndexPublicationStatus.PUBLISHED:
                return ()
            if any(chunk.index_state != "ACTIVE" for chunk in record.chunks):
                return ()
            return record.chunks

    def get_version(self, version_id: UUID, tenant_id: UUID) -> VersionRecord:
        with self._lock:
            return self._version(version_id, tenant_id)

    def get_job(self, job_id: UUID, tenant_id: UUID) -> IngestionJob:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None or job.tenant_id != tenant_id:
                raise NotFound("JOB_NOT_FOUND", "ingestion job is unavailable")
            return job

    def get_document(self, document_id: UUID, tenant_id: UUID) -> DocumentRecord:
        with self._lock:
            document = self._documents.get((tenant_id, document_id))
            if document is None:
                raise NotFound("DOCUMENT_NOT_FOUND", "document is unavailable")
            return document

    def fail_next_publication(self) -> None:
        self._fail_next_publication = True

    def _approve(self, version_id: UUID, tenant_id: UUID, reviewer_id: UUID, *, stage: int, idempotency_key: str) -> VersionRecord:
        if not idempotency_key.strip():
            raise InvalidInput("IDEMPOTENCY_REQUIRED", "approval idempotency key is required")
        with self._lock:
            record = self._version(version_id, tenant_id)
            expected = ProcessingStatus.QUARANTINED.value if stage == 1 else ProcessingStatus.PENDING_REVIEW_2.value
            self._require_status(record, expected)
            if stage == 1 and (record.scan is None or not record.scan.passed):
                raise ApprovalBlocked("SCAN_REQUIRED", "clean scan is required before review")
            if stage == 2 and not record.chunks:
                raise ApprovalBlocked("PROCESSING_REQUIRED", "validated chunks are required before review")
            for approval in record.approvals:
                if approval.stage == stage and approval.idempotency_key == idempotency_key:
                    if approval.reviewer_id != reviewer_id or approval.decision != "APPROVE":
                        raise IdempotencyConflict("APPROVAL_CONFLICT", "approval idempotency key was reused")
                    return record
            approval = ApprovalRecord(stage, reviewer_id, "APPROVE", idempotency_key, 1, self._now() + APPROVAL_TTL)
            status = ProcessingStatus.REVIEW_1_APPROVED.value if stage == 1 else ProcessingStatus.PENDING_REVIEW_2.value
            updated = replace(record, metadata=_status(record.metadata, status), approvals=record.approvals + (approval,))
            self._versions[version_id] = updated
            job = self._jobs[record.job_id]
            self._jobs[job.job_id] = replace(job, current_stage=JobStage.PARSING if stage == 1 else JobStage.PUBLICATION)
            self._audit("DOCUMENT_REVIEW_APPROVED", "document:approve", tenant_id, version_id)
            return updated

    def _validate_chunks(self, record: VersionRecord, chunks: tuple[ChunkMetadata, ...]) -> tuple[ChunkMetadata, ...]:
        if not chunks:
            raise InvalidInput("CHUNKS_EMPTY", "validated processing requires chunks")
        by_id = {chunk.chunk_id: chunk for chunk in chunks}
        normalized: list[ChunkMetadata] = []
        for chunk in chunks:
            if (chunk.tenant_id, chunk.document_id, chunk.version_id) != (
                record.metadata.tenant_id,
                record.metadata.document_id,
                record.metadata.version_id,
            ):
                raise InvalidInput("CHUNK_SCOPE_MISMATCH", "chunk scope is invalid")
            if chunk.index_state != "STAGING":
                raise InvalidInput("CHUNK_NOT_STAGING", "chunks must enter through staging")
            if chunk.parent_chunk_id is None:
                if chunk.acl_policy_ref is None:
                    raise InvalidInput("CHUNK_ACL_MISSING", "chunk ACL metadata is required")
                normalized.append(chunk)
                continue
            parent = by_id.get(chunk.parent_chunk_id)
            if parent is None:
                raise InvalidInput("PARENT_CHUNK_MISSING", "parent chunk is unavailable")
            try:
                normalized.append(inherit_acl(parent, chunk))
            except ValueError as error:
                raise InvalidInput("CHUNK_ACL_INVALID", "child ACL is broader than its parent") from error
        return tuple(sorted(normalized, key=lambda item: item.chunk_index))

    def _validate_manifest(self, record: VersionRecord, staged: StagedIndex) -> None:
        manifest = staged.manifest
        if manifest.content_sha256.lower() != record.metadata.sha256.lower():
            raise PublicationBlocked("CONTENT_CHECKSUM_MISMATCH", "index checksum does not match the version")
        if manifest.expected_chunk_count != len(record.chunks):
            raise PublicationBlocked("CHUNK_COUNT_MISMATCH", "index chunk count does not match the version")
        if manifest.chunk_digest != _chunk_digest(record.chunks) or manifest.acl_digest != _acl_digest(record.chunks):
            raise PublicationBlocked("INDEX_MANIFEST_MISMATCH", "index manifest does not match the version")
        if tuple(chunk.chunk_id for chunk in staged.chunks) != tuple(chunk.chunk_id for chunk in record.chunks):
            raise PublicationBlocked("INDEX_CHUNK_MISMATCH", "index chunks do not match the version")
        if not manifest.index_generation.strip():
            raise PublicationBlocked("INDEX_GENERATION_MISSING", "index generation is required")

    def _require_approval_live(self, record: VersionRecord, stage: int) -> None:
        approvals = [approval for approval in record.approvals if approval.stage == stage and approval.decision == "APPROVE"]
        if not approvals:
            raise ApprovalBlocked("APPROVAL_REQUIRED", "required approval is missing")
        if approvals[-1].expires_at <= self._now():
            raise ApprovalBlocked("APPROVAL_EXPIRED", "required approval has expired")

    def _require_status(self, record: VersionRecord, expected: str) -> None:
        if record.metadata.status != expected:
            raise InvalidTransition("LIFECYCLE_TRANSITION_DENIED", "version is not in the required lifecycle state")

    def _version(self, version_id: UUID, tenant_id: UUID) -> VersionRecord:
        record = self._versions.get(version_id)
        if record is None or record.metadata.tenant_id != tenant_id:
            raise NotFound("VERSION_NOT_FOUND", "document version is unavailable")
        return record

    def _maintenance_for(self, window_id: UUID, tenant_id: UUID) -> MaintenanceWindow:
        window = self._maintenance.get(window_id)
        if window is None or window.tenant_id != tenant_id:
            raise NotFound("MAINTENANCE_NOT_FOUND", "maintenance window is unavailable")
        return window

    def _remove_publication(self, record: VersionRecord) -> None:
        if record.publication is not None:
            self._safe_remove(record.publication.publication_id, record.metadata.version_id)

    def _safe_remove(self, publication_id: str | None, version_id: UUID) -> None:
        if publication_id is None:
            return
        try:
            self.derived_index.remove(publication_id)
        except IngestionError:
            self._cleanup_pending.add(version_id)
        except Exception as error:
            self._cleanup_pending.add(version_id)
            raise DerivedIndexFailure(
                "INDEX_UNAVAILABLE",
                "derived cleanup failed",
                retryable=True,
            ) from error

    def _mark_failed(self, version_id: UUID, error_code: str) -> None:
        record = self._versions[version_id]
        self._versions[version_id] = replace(
            record,
            metadata=_status(record.metadata, ProcessingStatus.FAILED.value),
        )
        job = self._jobs[record.job_id]
        self._jobs[job.job_id] = replace(job, state=JobState.FAILED, current_stage=JobStage.CLEANUP, error_code=error_code)

    def _cleanup_tenant(self, tenant_id: UUID) -> None:
        for version_id, record in tuple(self._versions.items()):
            if record.metadata.tenant_id != tenant_id or record.publication is None:
                continue
            self._safe_remove(record.publication.publication_id, version_id)

    def _upload_fingerprint(self, manifest: UploadManifest) -> str:
        return hashlib.sha256(
            f"{manifest.document_id}:{manifest.version_id}:{manifest.version_number}:{manifest.sha256}".encode()
        ).hexdigest()

    def _now(self) -> datetime:
        value = self.clock()
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _audit(
        self,
        event: str,
        action: str,
        tenant_id: UUID,
        resource_id: UUID,
        *,
        code: str | None = None,
    ) -> None:
        if self.audit_sink is None:
            return
        append_audit_event(
            self.audit_sink,
            context=self.context,
            event=event,
            action=action,
            outcome="SUCCESS" if code is None else "DENY",
            decision="ALLOW" if code is None else "DENY",
            tenant_id=str(tenant_id),
            code=code,
            metadata={"component": "ingestion", "stage": event.lower()},
        )


__all__ = [
    "APPROVAL_TTL",
    "MAX_ATTEMPTS",
    "MAX_UPLOAD_BYTES",
    "ApprovalRecord",
    "ApprovalBlocked",
    "DataClassification",
    "DerivedIndex",
    "DerivedIndexFailure",
    "DocumentRecord",
    "IndexManifest",
    "IndexPublication",
    "IndexPublicationStatus",
    "IngestionError",
    "IngestionJob",
    "IngestionService",
    "IdempotencyConflict",
    "InvalidInput",
    "InvalidTransition",
    "JobStage",
    "JobState",
    "MaintenanceStatus",
    "MaintenanceBlocked",
    "MaintenanceWindow",
    "NotFound",
    "ProcessingStatus",
    "PublicationBlocked",
    "PublicationStatus",
    "RetentionBlocked",
    "ScanReport",
    "ScanVerdict",
    "StagedIndex",
    "UploadManifest",
    "VersionRecord",
    "InMemoryDerivedIndex",
]
