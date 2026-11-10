"""Authoritative document metadata and immutable chunk boundaries."""

from .models import (
    ChunkMetadata,
    Classification,
    DocumentMetadata,
    DocumentVersionMetadata,
    SourceSpan,
    inherit_acl,
    to_qdrant_payload,
)

__all__ = [
    "ChunkMetadata",
    "Classification",
    "DocumentMetadata",
    "DocumentVersionMetadata",
    "SourceSpan",
    "inherit_acl",
    "to_qdrant_payload",
]
