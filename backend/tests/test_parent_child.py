from dataclasses import replace

from backend.app.rag.parent_child import (
    ChildEvidence,
    ParentRecord,
    expand_parent_context,
)


def child(name="child-1", *, tenant="tenant-a", document="doc-1", version="v-1", parent="parent-1"):
    return ChildEvidence(
        chunk_id=name,
        tenant_id=tenant,
        document_id=document,
        version_id=version,
        text=f"child text {name}",
        citation={"chunk_id": name, "page": 2},
        parent_chunk_id=parent,
    )


def parent(name="parent-1", *, tenant="tenant-a", document="doc-1", version="v-1", text="parent text", **states):
    return ParentRecord(
        chunk_id=name,
        tenant_id=tenant,
        document_id=document,
        version_id=version,
        text=text,
        **states,
    )


def test_expands_authorized_parent_and_preserves_child_citation():
    evidence = child()
    result = expand_parent_context((evidence,), (parent(),), lambda record: True)

    assert result.children == (evidence,)
    assert result.parents[0].text == "parent text"
    assert result.parents[0].child_chunk_ids == ("child-1",)
    assert result.parents[0].child_citations == (evidence.citation,)
    assert result.context == (evidence, result.parents[0])


def test_missing_parent_keeps_authorized_child():
    evidence = child()
    result = expand_parent_context((evidence,), (), lambda record: True)

    assert result.children == (evidence,)
    assert result.parents == ()


def test_cross_tenant_parent_is_never_authorized_or_returned():
    evidence = child()
    calls = []
    result = expand_parent_context(
        (evidence,),
        (parent(tenant="tenant-b"),),
        lambda record: calls.append(record.chunk_id) or True,
    )

    assert result.parents == ()
    assert calls == []


def test_version_mismatch_parent_is_omitted():
    evidence = child()
    result = expand_parent_context((evidence,), (parent(version="v-2"),), lambda record: True)

    assert result.children == (evidence,)
    assert result.parents == ()


def test_denied_parent_does_not_change_child_result():
    evidence = child()
    result = expand_parent_context((evidence,), (parent(),), lambda record: False)

    assert result.children == (evidence,)
    assert result.parents == ()


def test_revoked_or_stale_parent_is_omitted():
    evidence = child()
    revoked = parent("parent-revoked", status="REVOKED")
    stale = parent("parent-stale", version_status="SUPERSEDED")
    result = expand_parent_context(
        (replace(evidence, parent_chunk_id="parent-revoked"),),
        (revoked, stale),
        lambda record: True,
    )
    stale_result = expand_parent_context(
        (replace(evidence, parent_chunk_id="parent-stale"),),
        (revoked, stale),
        lambda record: True,
    )

    assert result.parents == ()
    assert stale_result.parents == ()


def test_duplicate_children_and_parents_are_deduplicated_with_all_provenance():
    first = child("child-1")
    second = child("child-2")
    result = expand_parent_context(
        (first, first, second),
        (parent(),),
        lambda record: True,
    )

    assert result.children == (first, second)
    assert len(result.parents) == 1
    assert result.parents[0].child_chunk_ids == ("child-1", "child-2")
    assert result.parents[0].child_citations == (first.citation, second.citation)


def test_parent_and_character_bounds_are_hard_limits():
    children = tuple(child(f"child-{name}", parent=f"parent-{name}") for name in "abc")
    parents = tuple(
        parent(f"parent-{name}", text=text)
        for name, text in (("a", "1234"), ("b", "12345"), ("c", "123456"))
    )
    result = expand_parent_context(
        children,
        parents,
        lambda record: True,
        max_parents=2,
        max_characters=9,
    )

    assert [item.parent_chunk_id for item in result.parents] == ["parent-a", "parent-b"]
    assert sum(len(item.text) for item in result.parents) <= 9
    assert len(result.parents) <= 2


def test_callback_failure_fails_closed_for_parent_only():
    evidence = child()

    def broken(record):
        raise RuntimeError("policy unavailable")

    result = expand_parent_context((evidence,), (parent(),), broken)

    assert result.children == (evidence,)
    assert result.parents == ()


def test_malformed_parent_metadata_fails_closed():
    evidence = child()
    malformed = {
        "chunk_id": "parent-1",
        "tenant_id": "tenant-a",
        "document_id": "doc-1",
        "version_id": "v-1",
        "text": "must not leak",
        # Missing status is intentionally malformed.
    }
    result = expand_parent_context((evidence,), (malformed,), lambda record: True)

    assert result.children == (evidence,)
    assert result.parents == ()


def test_parent_order_follows_first_child_reference_deterministically():
    first = child("child-b", parent="parent-b")
    second = child("child-a", parent="parent-a")
    calls = []
    result = expand_parent_context(
        (first, second),
        {"parent-a": parent("parent-a"), "parent-b": parent("parent-b")},
        lambda record: calls.append(record.chunk_id) or True,
    )

    assert [item.parent_chunk_id for item in result.parents] == ["parent-b", "parent-a"]
    assert calls == ["parent-b", "parent-a"]
