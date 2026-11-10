from dataclasses import replace

import pytest

from backend.app.rag.parent_child import ChildEvidence, ParentRecord, expand_parent_context
from backend.tests.test_hybrid_retrieval import _make_parent_child_retriever


def _child(name="child-1", *, parent="parent-1", tenant="tenant-a", document="doc-1", version="v-1"):
    return ChildEvidence(
        chunk_id=name,
        tenant_id=tenant,
        document_id=document,
        version_id=version,
        text=f"child text {name}",
        citation={"chunk_id": name},
        parent_chunk_id=parent,
    )


def _parent(
    name="parent-1",
    *,
    tenant="tenant-a",
    document="doc-1",
    version="v-1",
    text="parent context",
    **states,
):
    return ParentRecord(
        chunk_id=name,
        tenant_id=tenant,
        document_id=document,
        version_id=version,
        text=text,
        **states,
    )


def test_runtime_parent_is_added_after_child_rerank():
    hybrid, principal, parent_id, child_id = _make_parent_child_retriever()

    result = hybrid.search("warranty coverage", principal, policy_epoch=7, top_k=1)

    assert [item.citation.chunk_id for item in result.evidence] == [child_id]
    assert [item.citation.chunk_id for item in result.expanded_context] == [parent_id]
    assert result.evidence[0].rerank_score > result.expanded_context[0].rerank_score


def test_child_without_parent_reference_remains_unchanged():
    child = _child(parent=None)

    result = expand_parent_context((child,), (_parent(),), lambda record: True)

    assert result.children == (child,)
    assert result.parents == ()


def test_duplicate_children_deduplicate_and_merge_parent_provenance():
    first = _child("child-1")
    second = _child("child-2")

    result = expand_parent_context((first, first, second), (_parent(),), lambda record: True)

    assert result.children == (first, second)
    assert result.parents[0].child_chunk_ids == ("child-1", "child-2")
    assert result.parents[0].child_citations == (first.citation, second.citation)


def test_parent_order_follows_first_child_reference():
    first = _child("child-b", parent="parent-b")
    second = _child("child-a", parent="parent-a")
    calls = []

    result = expand_parent_context(
        (first, second),
        {"parent-a": _parent("parent-a"), "parent-b": _parent("parent-b")},
        lambda record: calls.append(record.chunk_id) or True,
    )

    assert [item.parent_chunk_id for item in result.parents] == ["parent-b", "parent-a"]
    assert calls == ["parent-b", "parent-a"]


def test_parent_count_bound_is_hard():
    children = tuple(_child(f"child-{letter}", parent=f"parent-{letter}") for letter in "abc")
    parents = tuple(_parent(f"parent-{letter}") for letter in "abc")

    result = expand_parent_context(children, parents, lambda record: True, max_parents=2)

    assert len(result.parents) == 2


def test_parent_character_bound_is_hard():
    children = tuple(_child(f"child-{letter}", parent=f"parent-{letter}") for letter in "abc")
    parents = tuple(
        _parent(f"parent-{letter}", text=text)
        for letter, text in (("a", "1234"), ("b", "12345"), ("c", "123456"))
    )

    result = expand_parent_context(children, parents, lambda record: True, max_characters=9)

    assert [item.parent_chunk_id for item in result.parents] == ["parent-a", "parent-b"]
    assert sum(len(item.text) for item in result.parents) <= 9


def test_malformed_child_is_omitted_without_dropping_valid_child():
    valid = _child()
    malformed = {"chunk_id": "bad", "tenant_id": "tenant-a"}

    result = expand_parent_context((malformed, valid), (_parent(),), lambda record: True)

    assert result.children == (valid,)
    assert result.parents[0].parent_chunk_id == "parent-1"


def test_invalid_limits_are_rejected_before_expansion():
    with pytest.raises(ValueError):
        expand_parent_context((_child(),), (_parent(),), lambda record: True, max_parents=-1)
    with pytest.raises(ValueError):
        expand_parent_context((_child(),), (_parent(),), lambda record: True, max_characters=True)


def test_authorizer_exception_fails_closed_for_parent_only():
    child = _child()

    def unavailable(record):
        raise RuntimeError("policy unavailable")

    result = expand_parent_context((child,), (_parent(),), unavailable)

    assert result.children == (child,)
    assert result.parents == ()


def test_each_non_active_lifecycle_dimension_omits_parent():
    child = _child()

    for field in ("status", "document_status", "version_status", "index_state"):
        stale = replace(_parent(), **{field: "REVOKED"})
        result = expand_parent_context((child,), (stale,), lambda record: True)
        assert result.parents == (), field
