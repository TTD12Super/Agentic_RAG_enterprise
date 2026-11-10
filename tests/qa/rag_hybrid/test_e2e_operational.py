import json
from pathlib import Path
from uuid import uuid4

from backend.app.authorization.policy import (
    AuthorizationEvaluator,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.ingestion.lifecycle import IngestionService
from backend.app.models.policy import DataClassification
from backend.app.rag.dense import DenseRetriever, InMemoryDenseVectorIndex
from backend.app.rag.hybrid import HybridRetrievalConfig, HybridRetriever, InMemoryBM25Index
from backend.tests.test_dense_retrieval import _active_document, _principal, _resource
from backend.tests.test_hybrid_retrieval import _gateway, _make_retriever
from tests.evaluation._evaluation_harness import (
    mean_reciprocal_rank,
    ndcg_at_k,
    recall_at_k,
)


ROOT = Path(__file__).resolve().parents[3]


def _single_hybrid(*, index_state: str = "ACTIVE", version_status: str = "ACTIVE"):
    tenant_id = uuid4()
    ingestion = IngestionService()
    gateway = _gateway()
    document_id, version_id, department_id, active_chunk = _active_document(
        ingestion, tenant_id=tenant_id
    )
    chunk = active_chunk.model_copy(update={"index_state": index_state})
    dense_index = InMemoryDenseVectorIndex(gateway)
    bm25_index = InMemoryBM25Index()
    text = "operational hybrid evidence"
    dense_index.upsert(chunk, text, classification=DataClassification.INTERNAL)
    bm25_index.upsert(chunk, text)
    resource = _resource(
        document_id,
        version_id,
        tenant_id,
        department_id,
        version_status=version_status,
    )
    pep = PolicyEnforcementPoint(
        AuthorizationEvaluator(policy_store=InMemoryPolicyStore(policy_epoch=7))
    )
    dense = DenseRetriever(
        index=dense_index,
        ingestion=ingestion,
        pep=pep,
        documents={str(document_id): resource},
        model_gateway=gateway,
    )
    hybrid = HybridRetriever(
        dense=dense,
        bm25=bm25_index,
        model_gateway=gateway,
        config=HybridRetrievalConfig(branch_top_k=20, rrf_k=60, rerank_top_k=20),
    )
    return hybrid, _principal(tenant_id, department_id), ingestion, tenant_id, chunk


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


def test_complete_ingestion_to_hybrid_retrieval_returns_authorized_evidence():
    hybrid, principal, _, _, _ = _make_retriever(["approved operational evidence"])

    result = hybrid.search("approved evidence", principal, policy_epoch=7, top_k=1)

    assert result.status == "OK"
    assert len(result.evidence) == 1
    assert result.evidence[0].text == "approved operational evidence"


def test_end_to_end_pipeline_runs_dense_bm25_rrf_and_rerank_in_order():
    hybrid, principal, _, _, chunks = _make_retriever(
        ["Product A warranty coverage", "Product A support contact"]
    )

    dense = hybrid._dense.search("Product A warranty", principal, policy_epoch=7, top_k=20)
    bm25 = hybrid._bm25_search("Product A warranty", principal, 7, 20)
    result = hybrid.search("Product A warranty", principal, policy_epoch=7, top_k=2)

    assert dense.evidence and bm25
    assert result.evidence[0].citation.chunk_id == str(chunks[0][0].chunk_id)
    assert result.evidence[0].rrf_score > 0
    assert result.evidence[0].rerank_score >= result.evidence[1].rerank_score


def test_source_fetch_returns_the_same_version_bound_citation_as_search():
    hybrid, principal, _, _, chunks = _make_retriever(["version bound operational source"])

    result = hybrid.search("version bound", principal, policy_epoch=7, top_k=1)
    source = hybrid.fetch_source(chunks[0][0].chunk_id, principal, policy_epoch=7)

    assert source.redacted is False
    assert source.citation == result.evidence[0].citation
    assert source.content == result.evidence[0].text


def test_revocation_removes_hybrid_search_and_source_access():
    hybrid, principal, ingestion, tenant_id, chunks = _make_retriever(["revocable source"])
    ingestion.revoke_version(chunks[0][1][1], tenant_id)

    result = hybrid.search("revocable", principal, policy_epoch=7)
    source = hybrid.fetch_source(chunks[0][0].chunk_id, principal, policy_epoch=7)

    assert result.evidence == ()
    assert source.redacted is True
    assert source.content is None


def test_superseded_version_is_absent_from_both_search_branches():
    hybrid, principal, _, _, _ = _single_hybrid(version_status="SUPERSEDED")

    dense = hybrid._dense.search("operational", principal, policy_epoch=7, top_k=5)
    bm25 = hybrid._bm25_search("operational", principal, 7, 5)

    assert dense.evidence == ()
    assert bm25 == ()


def test_staging_index_is_absent_from_both_search_branches():
    hybrid, principal, _, _, _ = _single_hybrid(index_state="STAGING")

    dense = hybrid._dense.search("operational", principal, policy_epoch=7, top_k=5)
    bm25 = hybrid._bm25_search("operational", principal, 7, 5)

    assert dense.evidence == ()
    assert bm25 == ()


def test_stale_policy_epoch_is_absent_from_both_search_branches():
    hybrid, principal, _, _, _ = _single_hybrid()

    dense = hybrid._dense.search("operational", principal, policy_epoch=6, top_k=5)
    bm25 = hybrid._bm25_search("operational", principal, 6, 5)

    assert dense.evidence == ()
    assert bm25 == ()


def test_hybrid_metrics_regressions_remain_at_perfect_tiny_corpus_baseline():
    hybrid, principal, _, tenant_id, chunks = _make_retriever(
        [
            "Product A warranty coverage applies for twelve months.",
            "Product A support contact and maintenance schedule.",
            "Product B warranty exclusions require manager approval.",
        ]
    )
    expected = [_span(hybrid.fetch_source(chunks[0][0].chunk_id, principal, policy_epoch=7).citation, str(tenant_id))]
    result = hybrid.search("Product A warranty coverage", principal, policy_epoch=7, top_k=5)
    retrieved = [_span(item.citation, str(tenant_id)) for item in result.evidence]

    assert recall_at_k(expected, retrieved, 5) == 1.0
    assert ndcg_at_k(expected, retrieved, 5) == 1.0
    assert mean_reciprocal_rank(expected, retrieved) == 1.0


def test_repeated_operational_runs_have_identical_ranked_evidence():
    hybrid, principal, _, _, _ = _make_retriever(
        ["stable operational ranking", "stable support reference"]
    )

    first = hybrid.search("stable operational", principal, policy_epoch=7, top_k=2)
    second = hybrid.search("stable operational", principal, policy_epoch=7, top_k=2)

    assert first == second


def test_rag002_task_registry_keeps_retrieval_validation_and_scope():
    tasks = json.loads((ROOT / "harness/tasks/tasks.json").read_text(encoding="utf-8"))
    task = next(item for item in tasks["tasks"] if item["id"] == "RAG-002")

    assert "pytest backend/tests tests/evaluation -k retrieval" in task["validation"]
    assert task["scope"]["write_paths"] == [
        "backend/app/rag",
        "backend/tests",
        "tests/evaluation",
        "harness/handoffs",
    ]
    assert {"backend/app/authorization", "frontend", "infra"} <= set(
        task["scope"]["forbidden_paths"]
    )
