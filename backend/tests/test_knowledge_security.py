from uuid import uuid4

import pytest

from backend.app.knowledge.models import ChunkMetadata, inherit_acl, to_qdrant_payload


def make_parent():
    return ChunkMetadata(
        chunk_id=uuid4(), tenant_id=uuid4(), document_id=uuid4(), version_id=uuid4(),
        chunk_index=0, acl_policy_ref="policy-1", text_hash="a" * 64
    )


def make_child(parent, **overrides):
    values = {
        "chunk_id": uuid4(), "tenant_id": parent.tenant_id, "document_id": parent.document_id,
        "version_id": parent.version_id, "parent_chunk_id": parent.chunk_id,
        "chunk_index": 1, "text_hash": "b" * 64,
    }
    values.update(overrides)
    return ChunkMetadata(**values)


def test_tenant_mismatch_is_denied():
    parent = make_parent()
    with pytest.raises(ValueError):
        inherit_acl(parent, make_child(parent, tenant_id=uuid4()))


def test_document_mismatch_is_denied():
    parent = make_parent()
    with pytest.raises(ValueError):
        inherit_acl(parent, make_child(parent, document_id=uuid4()))


def test_version_mismatch_is_denied():
    parent = make_parent()
    with pytest.raises(ValueError):
        inherit_acl(parent, make_child(parent, version_id=uuid4()))


def test_wrong_parent_reference_is_denied():
    parent = make_parent()
    with pytest.raises(ValueError):
        inherit_acl(parent, make_child(parent, parent_chunk_id=uuid4()))


def test_conflicting_child_acl_is_denied():
    parent = make_parent()
    with pytest.raises(ValueError):
        inherit_acl(parent, make_child(parent, acl_policy_ref="broader-policy"))


def test_missing_child_acl_is_inherited():
    parent = make_parent()
    assert inherit_acl(parent, make_child(parent)).acl_policy_ref == "policy-1"


def test_matching_child_acl_is_preserved():
    parent = make_parent()
    assert inherit_acl(parent, make_child(parent, acl_policy_ref="policy-1")).acl_policy_ref == "policy-1"


def test_qdrant_projection_requires_acl():
    parent = make_parent()
    with pytest.raises(ValueError):
        to_qdrant_payload(make_child(parent))


def test_qdrant_projection_keeps_tenant_boundary():
    parent = make_parent()
    payload = to_qdrant_payload(parent)
    assert payload["tenant_id"] == str(parent.tenant_id)


def test_qdrant_projection_does_not_claim_authority():
    payload = to_qdrant_payload(make_parent())
    assert "policy_decision" not in payload
    assert "authorized_scope" not in payload
