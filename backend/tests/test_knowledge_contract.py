from uuid import uuid4

from backend.app.knowledge.models import (
    ChunkMetadata,
    DocumentMetadata,
    DocumentVersionMetadata,
    SourceSpan,
    inherit_acl,
    to_qdrant_payload,
)


def make_parent():
    return ChunkMetadata(
        chunk_id=uuid4(),
        tenant_id=uuid4(),
        document_id=uuid4(),
        version_id=uuid4(),
        chunk_index=0,
        acl_policy_ref="policy-1",
        text_hash="a" * 64,
    )


def make_child(parent, acl_policy_ref=None):
    return ChunkMetadata(
        chunk_id=uuid4(),
        tenant_id=parent.tenant_id,
        document_id=parent.document_id,
        version_id=parent.version_id,
        parent_chunk_id=parent.chunk_id,
        chunk_index=1,
        acl_policy_ref=acl_policy_ref,
        text_hash="b" * 64,
    )


def test_document_metadata_contract_fields():
    value = DocumentMetadata(
        tenant_id=uuid4(), document_id=uuid4(), classification="PUBLIC", status="ACTIVE",
        current_version_id=uuid4(), created_by=uuid4()
    )
    assert value.model_dump().keys() >= {"tenant_id", "document_id", "classification", "status"}


def test_version_contract_has_immutable_version_number():
    value = DocumentVersionMetadata(
        tenant_id=uuid4(), document_id=uuid4(), version_id=uuid4(), version_number=1,
        source_uri="private://documents/v1", sha256="a" * 64, status="UPLOADED"
    )
    assert value.version_number == 1


def test_version_contract_supports_publication_states():
    value = DocumentVersionMetadata(
        tenant_id=uuid4(), document_id=uuid4(), version_id=uuid4(), version_number=1,
        source_uri="private://documents/v1", sha256="a" * 64, status="PROCESS_VALIDATED"
    )
    assert value.status == "PROCESS_VALIDATED"


def test_parent_child_contract_keeps_same_scope():
    parent = make_parent()
    child = inherit_acl(parent, make_child(parent))
    assert (child.tenant_id, child.document_id, child.version_id) == (
        parent.tenant_id, parent.document_id, parent.version_id
    )


def test_acl_inheritance_populates_child_reference():
    parent = make_parent()
    child = inherit_acl(parent, make_child(parent))
    assert child.acl_policy_ref == parent.acl_policy_ref


def test_qdrant_projection_contains_scope_keys():
    payload = to_qdrant_payload(make_parent())
    assert {"tenant_id", "document_id", "version_id", "chunk_id"} <= payload.keys()


def test_qdrant_projection_contains_index_state():
    payload = to_qdrant_payload(make_parent())
    assert payload["index_state"] == "STAGING"


def test_qdrant_projection_does_not_store_chunk_text():
    payload = to_qdrant_payload(make_parent())
    assert "content_text" not in payload


def test_qdrant_projection_preserves_source_span():
    parent = make_parent()
    values = parent.model_dump()
    values["source_span"] = SourceSpan(start=2, end=8)
    parent = ChunkMetadata(**values)
    assert to_qdrant_payload(parent)["source_span"] == {"start": 2, "end": 8}


def test_qdrant_projection_preserves_parent_reference():
    parent = make_parent()
    child = inherit_acl(parent, make_child(parent))
    assert to_qdrant_payload(child)["parent_chunk_id"] == str(parent.chunk_id)
