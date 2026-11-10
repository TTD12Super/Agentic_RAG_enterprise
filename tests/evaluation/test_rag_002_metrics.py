import json

from backend.tests.test_hybrid_retrieval import _make_retriever
from tests.evaluation._evaluation_harness import (
    mean_reciprocal_rank,
    ndcg_at_k,
    recall_at_k,
)


def _span(citation, tenant_id: str) -> dict:
    assert citation.source_span is not None
    return {
        "kind": "PDF",
        "document_id": citation.document_id,
        "version_id": citation.version_id,
        "tenant_id": tenant_id,
        "page": citation.page_start,
        "source_span": {
            "start": citation.source_span.start,
            "end": citation.source_span.end,
        },
    }


def _spans(evidence, tenant_id: str) -> list[dict]:
    return [_span(item.citation, tenant_id) for item in evidence]


def test_rag_002_regression_metrics_on_tiny_in_memory_corpus():
    hybrid, principal, _, tenant_id, chunks = _make_retriever(
        [
            "Product A warranty coverage applies for twelve months.",
            "Product A support contact and maintenance schedule.",
            "Product B warranty exclusions require manager approval.",
        ]
    )
    expected = [_span(hybrid.fetch_source(chunks[0][0].chunk_id, principal, policy_epoch=7).citation, str(tenant_id))]
    dense = hybrid._dense.search(
        "Product A warranty coverage",
        principal,
        policy_epoch=7,
        top_k=5,
    )
    result = hybrid.search(
        "Product A warranty coverage",
        principal,
        policy_epoch=7,
        top_k=5,
    )
    dense_spans = _spans(dense.evidence, str(tenant_id))
    bm25 = hybrid._bm25_search(
        "Product A warranty coverage",
        principal,
        7,
        5,
    )
    rrf = hybrid._fuse(dense.evidence, bm25)
    hybrid_spans = _spans(result.evidence, str(tenant_id))
    bm25_spans = [_span(item[0], str(tenant_id)) for item in bm25]
    rrf_spans = [_span(item.citation, str(tenant_id)) for item in rrf]

    def metrics(retrieved: list[dict]) -> dict[str, float]:
        return {
            "recall_at_5": recall_at_k(expected, retrieved, 5),
            "ndcg_at_5": ndcg_at_k(expected, retrieved, 5),
            "mrr": mean_reciprocal_rank(expected, retrieved),
        }

    dense_metrics = metrics(dense_spans)
    bm25_metrics = metrics(bm25_spans)
    rrf_metrics = metrics(rrf_spans)
    hybrid_metrics = metrics(hybrid_spans)

    print(
        "RAG-002 metrics "
        + json.dumps(
            {
                "corpus": "3 synthetic active chunks, 1 tenant",
                "query": "Product A warranty coverage",
                "embedding_model": "deterministic-32d-hash",
                "bm25_config": {"k1": 1.5, "b": 0.75},
                "rrf_k": 60,
                "reranker": "deterministic-local-token-overlap",
                "top_k": 5,
                "dense": dense_metrics,
                "bm25": bm25_metrics,
                "rrf": rrf_metrics,
                "hybrid_reranked": hybrid_metrics,
            },
            sort_keys=True,
        )
    )
    assert result.status == "OK"
    assert bm25_metrics["recall_at_5"] >= dense_metrics["recall_at_5"]
    assert rrf_metrics["recall_at_5"] >= dense_metrics["recall_at_5"]
    assert hybrid_metrics["recall_at_5"] >= dense_metrics["recall_at_5"]
    assert hybrid_metrics["ndcg_at_5"] >= dense_metrics["ndcg_at_5"]
    assert hybrid_metrics["mrr"] >= dense_metrics["mrr"]
