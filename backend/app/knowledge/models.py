"""Small, immutable knowledge metadata models.

PostgreSQL remains authoritative for lifecycle and authorization.  These models
validate the boundary used by ingestion and expose only a derived Qdrant
payload; they do not make authorization decisions.
"""

from __future__ import annotations

from datetime import datetime
import re
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Classification = Literal["PUBLIC", "INTERNAL"]
DocumentStatus = Literal["ACTIVE", "SOFT_DELETED", "PURGED"]
VersionStatus = Literal[
    "UPLOADED",
    "QUARANTINED",
    "REVIEW_1_APPROVED",
    "PROCESSING",
    "PROCESS_VALIDATED",
    "PENDING_REVIEW_2",
    "FAILED",
    "REJECTED",
    "CANCELLED",
    "ACTIVE",
    "SUPERSEDED",
    "REVOKED",
    "SOFT_DELETED",
]
IndexState = Literal["STAGING", "ACTIVE", "REMOVED"]


class _ImmutableModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceSpan(_ImmutableModel):
    """Half-open character offsets into the extracted source."""

    start: int = Field(ge=0)
    end: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_order(self) -> "SourceSpan":
        if self.end <= self.start:
            raise ValueError("source span end must be greater than start")
        return self


class PDFLocator(_ImmutableModel):
    kind: Literal["PDF"] = "PDF"
    page: int = Field(gt=0)
    source_span: SourceSpan


class DOCXLocator(_ImmutableModel):
    kind: Literal["DOCX"] = "DOCX"
    heading: str = Field(min_length=1)
    paragraph: int = Field(gt=0)

    @field_validator("heading")
    @classmethod
    def valid_heading(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("heading must not be empty")
        return value


class XLSXLocator(_ImmutableModel):
    kind: Literal["XLSX"] = "XLSX"
    sheet: str = Field(min_length=1)
    cell_range: str = Field(min_length=1)

    @field_validator("sheet")
    @classmethod
    def valid_sheet(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("sheet must not be empty")
        return value

    @field_validator("cell_range")
    @classmethod
    def valid_cell_range(cls, value: str) -> str:
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{1,3}[1-9][0-9]*(?::[A-Z]{1,3}[1-9][0-9]*)?", value):
            raise ValueError("cell_range must be a bounded A1-style range")
        return value


SourceLocator = Annotated[PDFLocator | DOCXLocator | XLSXLocator, Field(discriminator="kind")]


class DocumentMetadata(_ImmutableModel):
    """Tenant-scoped stable document identity and current-head metadata."""

    document_id: UUID
    tenant_id: UUID
    owner_department_id: UUID | None = None
    classification: Classification
    status: DocumentStatus
    current_version_id: UUID | None = None
    created_by: UUID

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "DocumentMetadata":
        if self.classification == "INTERNAL" and self.owner_department_id is None:
            raise ValueError("internal documents require an owner department")
        if self.status == "ACTIVE" and self.current_version_id is None:
            raise ValueError("active documents require a current version")
        return self


class DocumentVersionMetadata(_ImmutableModel):
    """Immutable identity and provenance for one document version."""

    version_id: UUID
    document_id: UUID
    tenant_id: UUID
    version_number: int = Field(gt=0)
    source_uri: str
    sha256: str
    effective_at: datetime | None = None
    status: VersionStatus
    approval_id: UUID | None = None

    @field_validator("source_uri")
    @classmethod
    def private_source_uri(cls, value: str) -> str:
        if not value.startswith("private://"):
            raise ValueError("source_uri must reference private object storage")
        return value

    @field_validator("sha256")
    @classmethod
    def valid_sha256(cls, value: str) -> str:
        if len(value) != 64 or any(char not in "0123456789abcdefABCDEF" for char in value):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        return value.lower()

    @property
    def identity(self) -> tuple[UUID, UUID, UUID, int]:
        """The immutable tenant/document/version identity tuple."""

        return (self.tenant_id, self.document_id, self.version_id, self.version_number)


class ChunkMetadata(_ImmutableModel):
    """One immutable extracted chunk, bounded to one tenant and version."""

    chunk_id: UUID
    document_id: UUID
    version_id: UUID
    tenant_id: UUID
    parent_chunk_id: UUID | None = None
    chunk_index: int = Field(ge=0)
    page_start: int | None = Field(default=None, gt=0)
    page_end: int | None = Field(default=None, gt=0)
    source_span: SourceSpan | None = None
    source_locator: SourceLocator | None = None
    acl_policy_ref: str | None = Field(default=None, min_length=1)
    text_hash: str = Field(min_length=64, max_length=64)
    index_state: IndexState = "STAGING"

    @field_validator("text_hash")
    @classmethod
    def valid_text_hash(cls, value: str) -> str:
        if any(char not in "0123456789abcdefABCDEF" for char in value):
            raise ValueError("text_hash must be hexadecimal")
        return value.lower()

    @model_validator(mode="after")
    def validate_chunk_bounds(self) -> "ChunkMetadata":
        if self.parent_chunk_id == self.chunk_id:
            raise ValueError("a chunk cannot be its own parent")
        if self.page_start is not None and self.page_end is not None and self.page_end < self.page_start:
            raise ValueError("page_end must be greater than or equal to page_start")
        if self.index_state == "ACTIVE" and self.acl_policy_ref is None:
            raise ValueError("an active chunk must carry inherited ACL metadata")
        if self.source_locator is None and self.page_start is not None and self.source_span is not None:
            object.__setattr__(
                self,
                "source_locator",
                PDFLocator(page=self.page_start, source_span=self.source_span),
            )
        if isinstance(self.source_locator, PDFLocator):
            if self.page_start is not None and self.page_start != self.source_locator.page:
                raise ValueError("PDF locator page must match page_start")
            if self.source_span is not None and self.source_span != self.source_locator.source_span:
                raise ValueError("PDF locator source_span must match source_span")
        return self


def inherit_acl(parent: ChunkMetadata, child: ChunkMetadata) -> ChunkMetadata:
    """Copy the parent's ACL reference without permitting child broadening."""

    if child.parent_chunk_id != parent.chunk_id:
        raise ValueError("child must reference the supplied parent")
    if (
        child.tenant_id,
        child.document_id,
        child.version_id,
    ) != (parent.tenant_id, parent.document_id, parent.version_id):
        raise ValueError("parent and child must share tenant, document and version")
    if child.acl_policy_ref not in (None, parent.acl_policy_ref):
        raise ValueError("child ACL cannot differ from its parent's ACL")
    return ChunkMetadata(
        **child.model_dump(exclude={"acl_policy_ref"}),
        acl_policy_ref=parent.acl_policy_ref,
    )


def to_qdrant_payload(chunk: ChunkMetadata) -> dict[str, object]:
    """Build a derived, tenant/version-scoped Qdrant payload."""

    if chunk.acl_policy_ref is None:
        raise ValueError("Qdrant projection requires inherited ACL metadata")
    payload: dict[str, object] = {
        "tenant_id": str(chunk.tenant_id),
        "document_id": str(chunk.document_id),
        "version_id": str(chunk.version_id),
        "chunk_id": str(chunk.chunk_id),
        "chunk_index": chunk.chunk_index,
        "index_state": chunk.index_state,
        "acl_policy_ref": chunk.acl_policy_ref,
        "text_hash": chunk.text_hash,
    }
    if chunk.parent_chunk_id is not None:
        payload["parent_chunk_id"] = str(chunk.parent_chunk_id)
    if chunk.page_start is not None:
        payload["page_start"] = chunk.page_start
    if chunk.page_end is not None:
        payload["page_end"] = chunk.page_end
    if chunk.source_span is not None:
        payload["source_span"] = chunk.source_span.model_dump()
    if chunk.source_locator is not None:
        payload["source_locator"] = chunk.source_locator.model_dump(mode="json")
    return payload
