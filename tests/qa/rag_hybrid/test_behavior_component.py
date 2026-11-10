from backend.app.models.adapters import RerankerRequest
from backend.app.rag.hybrid import (
    DeterministicRerankerAdapter,
    reciprocal_rank_fusion,
)
from backend.tests.test_hybrid_retrieval import _gateway, _make_retriever


def test_bm25_tokenization_casefolds_and_splits_punctuation():
    hybrid, principal, _, _, chunks = _make_retriever(["WARRANTY, Product-A!"])

    record = hybrid._bm25._records[chunks[0][0].chunk_id]
    ranked = hybrid._bm25_search("warranty product a", principal, 7, 5)

    assert record.tokens == ("warranty", "product", "a")
    assert len(ranked) == 1


def test_bm25_repeated_query_term_has_frequency_weight():
    hybrid, principal, _, _, chunks = _make_retriever(
        ["warranty coverage", "warranty warranty coverage"]
    )

    ranked = hybrid._bm25_search("warranty", principal, 7, 5)
    scores = {item[0].chunk_id: item[2] for item in ranked}

    assert scores[str(chunks[1][0].chunk_id)] > scores[str(chunks[0][0].chunk_id)]


def test_bm25_length_normalization_prefers_shorter_equal_match():
    hybrid, principal, _, _, chunks = _make_retriever(
        ["warranty", "warranty " + "noise " * 12]
    )

    ranked = hybrid._bm25_search("warranty", principal, 7, 5)
    scores = {item[0].chunk_id: item[2] for item in ranked}

    assert scores[str(chunks[0][0].chunk_id)] > scores[str(chunks[1][0].chunk_id)]


def test_rrf_deduplicates_repeated_ids_inside_each_branch():
    scores = reciprocal_rank_fusion(
        (("dense-a", "shared", "shared"), ("bm25-b", "shared")),
        rank_constant=1,
    )

    assert scores == {
        "dense-a": 1 / 2,
        "bm25-b": 1 / 2,
        "shared": 1 / 3 + 1 / 3,
    }


def test_rrf_rank_constant_preserves_rank_contributions():
    scores = reciprocal_rank_fusion((("first", "second"),), rank_constant=10)

    assert scores["first"] == 1 / 11
    assert scores["second"] == 1 / 12
    assert scores["first"] > scores["second"]


def test_deterministic_reranker_orders_equal_scores_by_id():
    gateway = _gateway()
    adapter = DeterministicRerankerAdapter()
    request = RerankerRequest(
        query="alpha",
        documents=(("b", "alpha"), ("a", "alpha")),
    )

    first = adapter.rerank(request, route=gateway.policy.reranker, timeout_seconds=1)
    second = adapter.rerank(request, route=gateway.policy.reranker, timeout_seconds=1)

    assert first == second
    assert [item.document_id for item in first.ranked_documents] == ["a", "b"]


def test_deterministic_reranker_counts_query_and_document_overlap():
    gateway = _gateway()
    result = DeterministicRerankerAdapter().rerank(
        RerankerRequest(
            query="alpha alpha beta",
            documents=(("one", "alpha beta"), ("two", "alpha")),
        ),
        route=gateway.policy.reranker,
        timeout_seconds=1,
    )

    assert result.ranked_documents[0].document_id == "one"
    assert result.ranked_documents[0].score == 3.0


def test_hybrid_fusion_deduplicates_a_chunk_shared_by_dense_and_bm25():
    hybrid, principal, _, _, chunks = _make_retriever(["shared hybrid evidence"])

    dense = hybrid._dense.search("shared", principal, policy_epoch=7, top_k=5)
    bm25 = hybrid._bm25_search("shared", principal, 7, 5)
    fused = hybrid._fuse(dense.evidence, bm25)

    assert [item.citation.chunk_id for item in fused] == [str(chunks[0][0].chunk_id)]


def test_hybrid_composition_preserves_rrf_and_rerank_scores():
    hybrid, principal, _, _, _ = _make_retriever(
        ["Product A warranty coverage", "Product A support contact"]
    )

    result = hybrid.search("Product A warranty", principal, policy_epoch=7, top_k=2)

    assert result.status == "OK"
    assert all(item.rrf_score > 0 for item in result.evidence)
    assert all(item.rerank_score == item.score for item in result.evidence)


def test_hybrid_search_is_deterministic_for_same_inputs():
    hybrid, principal, _, _, _ = _make_retriever(
        ["Product A warranty coverage", "Product A support contact"]
    )

    first = hybrid.search("Product A warranty", principal, policy_epoch=7, top_k=2)
    second = hybrid.search("Product A warranty", principal, policy_epoch=7, top_k=2)

    assert first == second
