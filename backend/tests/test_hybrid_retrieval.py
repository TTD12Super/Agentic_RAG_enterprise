from uuid import uuid4

import pytest

from backend.app.authorization.policy import (
    AccessGrant,
    Action,
    AuthorizationEvaluator,
    Effect,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.ingestion.lifecycle import IngestionService
from backend.app.integrations.model_gateway import ModelGateway
from backend.app.knowledge.models import PDFLocator, SourceSpan
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelRoute,
    ModelTask,
    ProviderPolicy,
)
from backend.app.rag.dense import DenseRetriever, DeterministicEmbeddingAdapter, InMemoryDenseVectorIndex
from backend.app.rag.hybrid import (
    DeterministicRerankerAdapter,
    HybridRetrievalConfig,
    HybridRetriever,
    InMemoryBM25Index,
    reciprocal_rank_fusion,
)
from backend.tests.test_dense_retrieval import _active_document, _principal, _resource
from backend.tests._ingestion_fixtures import active, make_manifest


def _gateway() -> ModelGateway:
    provider = ProviderPolicy(
        provider_id="deterministic-local",
        egress_mode=EgressMode.LOCAL,
        allowed_classifications=frozenset(DataClassification),
        approved=True,
    )
    embedding = ModelRoute(ModelTask.EMBEDDING, provider, "deterministic", "1")
    reranker = ModelRoute(ModelTask.RERANKER, provider, "deterministic", "1")
    return ModelGateway(
        ModelPolicy("hybrid-test-policy", embedding, reranker),
        embedding_adapters={"deterministic-local": DeterministicEmbeddingAdapter()},
        reranker_adapters={"deterministic-local": DeterministicRerankerAdapter()},
    )


def _make_retriever(
    texts: list[str],
) -> tuple[HybridRetriever, object, object, object, list[tuple[object, object]]]:
    tenant_id = uuid4()
    ingestion = IngestionService()
    gateway = _gateway()
    dense_index = InMemoryDenseVectorIndex(gateway)
    bm25_index = InMemoryBM25Index()
    resources = {}
    chunks = []
    for text in texts:
        document_id, version_id, department_id, chunk = _active_document(
            ingestion,
            tenant_id=tenant_id,
        )
        dense_index.upsert(chunk, text, classification=DataClassification.INTERNAL)
        bm25_index.upsert(chunk, text)
        resources[str(document_id)] = _resource(
            document_id,
            version_id,
            tenant_id,
            department_id,
        )
        chunks.append((chunk, (document_id, version_id, department_id)))
    department_id = chunks[0][1][2]
    principal = _principal(tenant_id, department_id).model_copy(
        update={"department_ids": [str(item[1][2]) for item in chunks]}
    )
    pep = PolicyEnforcementPoint(
        AuthorizationEvaluator(policy_store=InMemoryPolicyStore(policy_epoch=7))
    )
    dense = DenseRetriever(
        index=dense_index,
        ingestion=ingestion,
        pep=pep,
        documents=resources,
        model_gateway=gateway,
    )
    hybrid = HybridRetriever(
        dense=dense,
        bm25=bm25_index,
        model_gateway=gateway,
        config=HybridRetrievalConfig(branch_top_k=20, rrf_k=60, rerank_top_k=20),
    )
    return hybrid, principal, ingestion, tenant_id, chunks


def _make_parent_child_retriever() -> tuple[HybridRetriever, object, str, str]:
    tenant_id = uuid4()
    department_id = uuid4()
    ingestion = IngestionService()
    manifest = make_manifest(
        tenant_id=tenant_id,
        classification=DataClassification.INTERNAL,
        owner_department_id=department_id,
    )
    manifest, _, version = active(ingestion, manifest)
    parent, child = version.chunks
    indexed_parent = parent.model_copy(
        update={
            "page_start": 1,
            "source_span": SourceSpan(start=0, end=30),
            "source_locator": PDFLocator(page=1, source_span=SourceSpan(start=0, end=30)),
        }
    )
    indexed_child = child.model_copy(
        update={
            "page_start": 2,
            "source_span": SourceSpan(start=0, end=44),
            "source_locator": PDFLocator(page=2, source_span=SourceSpan(start=0, end=44)),
        }
    )
    gateway = _gateway()
    dense_index = InMemoryDenseVectorIndex(gateway)
    bm25_index = InMemoryBM25Index()
    dense_index.upsert(
        indexed_parent,
        "General policy context for chapter seven.",
        classification=DataClassification.INTERNAL,
    )
    bm25_index.upsert(indexed_parent, "General policy context for chapter seven.")
    dense_index.upsert(
        indexed_child,
        "Warranty coverage applies for twelve months.",
        classification=DataClassification.INTERNAL,
    )
    bm25_index.upsert(indexed_child, "Warranty coverage applies for twelve months.")
    principal = _principal(tenant_id, department_id)
    pep = PolicyEnforcementPoint(
        AuthorizationEvaluator(policy_store=InMemoryPolicyStore(policy_epoch=7))
    )
    dense = DenseRetriever(
        index=dense_index,
        ingestion=ingestion,
        pep=pep,
        documents={
            str(manifest.document_id): _resource(
                manifest.document_id,
                manifest.version_id,
                tenant_id,
                department_id,
            )
        },
        model_gateway=gateway,
    )
    return (
        HybridRetriever(dense=dense, bm25=bm25_index, model_gateway=gateway),
        principal,
        str(parent.chunk_id),
        str(child.chunk_id),
    )


def test_rrf_uses_each_branch_rank_and_deduplicates_within_a_branch():
    scores = reciprocal_rank_fusion(
        (("dense-a", "shared", "shared"), ("bm25-b", "shared")),
        rank_constant=1,
    )

    assert scores["dense-a"] == pytest.approx(1 / 2)
    assert scores["bm25-b"] == pytest.approx(1 / 2)
    assert scores["shared"] == pytest.approx(1 / 3 + 1 / 3)


def test_hybrid_retrieval_composes_bm25_rrf_and_local_reranker():
    hybrid, principal, _, _, chunks = _make_retriever(
        [
            "Product A warranty coverage applies for twelve months.",
            "Product A support contact and maintenance schedule.",
            "Product B warranty exclusions require manager approval.",
        ]
    )

    result = hybrid.search(
        "Product A warranty coverage",
        principal,
        policy_epoch=7,
        top_k=2,
    )

    assert result.status == "OK"
    assert len(result.evidence) == 2
    assert result.evidence[0].text == "Product A warranty coverage applies for twelve months."
    assert result.evidence[0].rrf_score > 0
    assert result.evidence[0].rerank_score >= result.evidence[1].rerank_score
    source = hybrid.fetch_source(chunks[0][0].chunk_id, principal, policy_epoch=7)
    assert source.redacted is False


def test_bm25_branch_filters_tenant_acl_active_and_policy_before_scoring():
    tenant_a, tenant_b = uuid4(), uuid4()
    ingestion = IngestionService()
    gateway = _gateway()
    dense_index = InMemoryDenseVectorIndex(gateway)
    bm25_index = InMemoryBM25Index()
    resources = {}

    allowed = _active_document(ingestion, tenant_id=tenant_a)
    denied = _active_document(ingestion, tenant_id=tenant_a)
    cross_tenant = _active_document(ingestion, tenant_id=tenant_b)
    stale = _active_document(ingestion, tenant_id=tenant_a)
    staged = _active_document(ingestion, tenant_id=tenant_a)
    principal = _principal(tenant_a, allowed[2])
    deny = AccessGrant(
        action=Action.DOCUMENT_READ.value,
        effect=Effect.DENY.value,
        user_id=principal.user_id,
    )

    entries = (
        (allowed, "approved secret alpha", ()),
        (denied, "secret secret alpha denied", (deny,)),
        (cross_tenant, "secret secret alpha cross tenant", ()),
        (stale, "secret alpha superseded", ()),
        (staged, "secret alpha staging", ()),
    )
    for (document_id, version_id, department_id, chunk), text, acl in entries:
        indexed_chunk = (
            chunk.model_copy(update={"index_state": "STAGING"})
            if document_id == staged[0]
            else chunk
        )
        dense_index.upsert(indexed_chunk, text, classification=DataClassification.INTERNAL)
        bm25_index.upsert(indexed_chunk, text)
        resources[str(document_id)] = _resource(
            document_id,
            version_id,
            tenant_a if document_id != cross_tenant[0] else tenant_b,
            department_id,
            acl=acl,
            version_status="SUPERSEDED" if document_id == stale[0] else "ACTIVE",
        )

    pep = PolicyEnforcementPoint(
        AuthorizationEvaluator(policy_store=InMemoryPolicyStore(policy_epoch=7))
    )
    dense = DenseRetriever(
        index=dense_index,
        ingestion=ingestion,
        pep=pep,
        documents=resources,
        model_gateway=gateway,
    )
    hybrid = HybridRetriever(
        dense=dense,
        bm25=bm25_index,
        model_gateway=gateway,
        config=HybridRetrievalConfig(branch_top_k=20, rrf_k=60, rerank_top_k=20),
    )

    result = hybrid.search("secret alpha", principal, policy_epoch=7, top_k=20)

    assert {item.citation.document_id for item in result.evidence} == {str(allowed[0])}
    assert all(item.citation.document_id != str(cross_tenant[0]) for item in result.evidence)
    assert hybrid.fetch_source(denied[3].chunk_id, principal, policy_epoch=7).redacted


def test_hybrid_runtime_expands_authorized_parent_after_reranking():
    hybrid, principal, parent_id, child_id = _make_parent_child_retriever()

    result = hybrid.search(
        "Warranty coverage applies for twelve months",
        principal,
        policy_epoch=7,
        top_k=1,
    )

    assert result.status == "OK"
    assert [item.citation.chunk_id for item in result.evidence] == [child_id]
    assert len(result.expanded_context) == 1
    assert result.expanded_context[0].citation.chunk_id == parent_id
    assert result.expanded_context[0].text == "General policy context for chapter seven."
