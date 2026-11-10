from uuid import uuid4

import pytest

from backend.app.knowledge.models import (
    ChunkMetadata,
    DocumentMetadata,
    DocumentVersionMetadata,
    SourceSpan,
)


def test_document_metadata_is_tenant_scoped():
    tenant_id, document_id, creator = uuid4(), uuid4(), uuid4()
    value = DocumentMetadata(
        tenant_id=tenant_id,
        document_id=document_id,
        owner_department_id=uuid4(),
        classification="INTERNAL",
        status="ACTIVE",
        current_version_id=uuid4(),
        created_by=creator,
    )
    assert value.tenant_id == tenant_id
    assert value.document_id == document_id


def test_document_version_identity_is_stable():
    value = DocumentVersionMetadata(
        tenant_id=uuid4(),
        document_id=uuid4(),
        version_id=uuid4(),
        version_number=2,
        source_uri="private://documents/v2",
        sha256="A" * 64,
        status="PROCESS_VALIDATED",
    )
    assert value.identity == (value.tenant_id, value.document_id, value.version_id, 2)


def test_source_span_requires_forward_offsets():
    assert SourceSpan(start=0, end=4).end == 4
    with pytest.raises(ValueError):
        SourceSpan(start=4, end=4)


def test_document_version_requires_private_source():
    with pytest.raises(ValueError):
        DocumentVersionMetadata(
            tenant_id=uuid4(),
            document_id=uuid4(),
            version_id=uuid4(),
            version_number=1,
            source_uri="https://public.example/file.pdf",
            sha256="a" * 64,
            status="UPLOADED",
        )


def test_hashes_are_normalized():
    version = DocumentVersionMetadata(
        tenant_id=uuid4(),
        document_id=uuid4(),
        version_id=uuid4(),
        version_number=1,
        source_uri="private://documents/v1",
        sha256="B" * 64,
        status="UPLOADED",
    )
    assert version.sha256 == "b" * 64


def test_chunk_rejects_self_parent():
    chunk_id, tenant_id, document_id, version_id = uuid4(), uuid4(), uuid4(), uuid4()
    with pytest.raises(ValueError):
        ChunkMetadata(
            chunk_id=chunk_id,
            tenant_id=tenant_id,
            document_id=document_id,
            version_id=version_id,
            parent_chunk_id=chunk_id,
            chunk_index=0,
            text_hash="a" * 64,
        )


def test_chunk_rejects_reversed_pages():
    with pytest.raises(ValueError):
        ChunkMetadata(
            chunk_id=uuid4(),
            tenant_id=uuid4(),
            document_id=uuid4(),
            version_id=uuid4(),
            chunk_index=0,
            page_start=5,
            page_end=4,
            text_hash="a" * 64,
        )


def test_active_chunk_requires_acl_metadata():
    with pytest.raises(ValueError):
        ChunkMetadata(
            chunk_id=uuid4(),
            tenant_id=uuid4(),
            document_id=uuid4(),
            version_id=uuid4(),
            chunk_index=0,
            text_hash="a" * 64,
            index_state="ACTIVE",
        )


def test_root_chunk_can_have_no_parent():
    value = ChunkMetadata(
        chunk_id=uuid4(),
        tenant_id=uuid4(),
        document_id=uuid4(),
        version_id=uuid4(),
        chunk_index=0,
        text_hash="a" * 64,
    )
    assert value.parent_chunk_id is None


def test_chunk_accepts_source_provenance():
    value = ChunkMetadata(
        chunk_id=uuid4(),
        tenant_id=uuid4(),
        document_id=uuid4(),
        version_id=uuid4(),
        chunk_index=1,
        source_span=SourceSpan(start=10, end=20),
        text_hash="a" * 64,
    )
    assert value.source_span == SourceSpan(start=10, end=20)
