"""Authoritative document metadata and immutable chunk boundaries."""

from .models import (
    ChunkMetadata,
    Classification,
    DOCXLocator,
    DocumentMetadata,
    DocumentVersionMetadata,
    PDFLocator,
    SourceLocator,
    SourceSpan,
    XLSXLocator,
    inherit_acl,
    to_qdrant_payload,
)

__all__ = [
    "ChunkMetadata",
    "Classification",
    "DOCXLocator",
    "DocumentMetadata",
    "DocumentVersionMetadata",
    "PDFLocator",
    "SourceLocator",
    "SourceSpan",
    "XLSXLocator",
    "inherit_acl",
    "to_qdrant_payload",
]
