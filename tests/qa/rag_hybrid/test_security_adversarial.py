from dataclasses import replace
from uuid import UUID, uuid4

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
from backend.app.models.policy import DataClassification
from backend.app.rag.dense import (
    DenseRetriever,
    DeterministicEmbeddingAdapter,
    InMemoryDenseVectorIndex,
)
from backend.app.rag.hybrid import (
    DeterministicRerankerAdapter,
    HybridRetriever,
    InMemoryBM25Index,
)
from backend.tests.test_dense_retrieval import _active_document, _principal, _resource
from backend.tests.test_hybrid_retrieval import _gateway, _make_retriever


class _FailingEmbeddingAdapter:
    def embed(self, request, *, route, timeout_seconds):
        raise RuntimeError("embedding provider secret")


class _FailingRerankerAdapter:
    def rerank(self, request, *, route, timeout_seconds):
        raise RuntimeError("reranker provider secret")


def _gateway_with_failure(*, embedding=False, reranker=False) -> ModelGateway:
    base = _gateway()
    return ModelGateway(
        base.policy,
        embedding_adapters={
            "deterministic-local": (
                _FailingEmbeddingAdapter() if embedding else DeterministicEmbeddingAdapter()
            )
        },
        reranker_adapters={
            "deterministic-local": (
                _FailingRerankerAdapter()
                if reranker
                else DeterministicRerankerAdapter()
            )
        },
    )


def _catalog(records):
    tenant_a = records[0][0]
    ingestion = IngestionService()
    gateway = _gateway()
    dense_index = InMemoryDenseVectorIndex(gateway)
    bm25_index = InMemoryBM25Index()
    resources = {}
    chunks = []
    departments = []
    first_department_id = None
    for tenant_id, text, acl, index_state, version_status in records:
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        chunk = chunk.model_copy(update={"index_state": index_state})
        dense_index.upsert(chunk, text, classification=DataClassification.INTERNAL)
        bm25_index.upsert(chunk, text)
        resources[str(document_id)] = _resource(
            document_id,
            version_id,
            tenant_id,
            department_id,
            acl=acl,
            version_status=version_status,
        )
        chunks.append((chunk, document_id, version_id, department_id))
        if tenant_id == tenant_a:
            departments.append(str(department_id))
            first_department_id = first_department_id or department_id
    principal = _principal(tenant_a, first_department_id)
    principal = principal.model_copy(update={"department_ids": departments})
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
    hybrid = HybridRetriever(dense=dense, bm25=bm25_index, model_gateway=gateway)
    return hybrid, principal, chunks


def test_cross_tenant_candidates_are_absent_from_dense_and_bm25():
    tenant_a, tenant_b = uuid4(), uuid4()
    hybrid, principal, chunks = _catalog(
        [
            (tenant_a, "tenant a policy", (), "ACTIVE", "ACTIVE"),
            (tenant_b, "tenant b classified secret", (), "ACTIVE", "ACTIVE"),
        ]
    )

    dense = hybrid._dense.search("classified secret", principal, policy_epoch=7, top_k=5)
    bm25 = hybrid._bm25_search("classified secret", principal, 7, 5)

    assert all(
        item.citation.chunk_id != str(chunks[1][0].chunk_id)
        for item in dense.evidence
    )
    assert bm25 == ()
    assert all(item[0].chunk_id != str(chunks[1][0].chunk_id) for item in bm25)


def test_acl_denied_candidates_are_absent_from_dense_and_bm25():
    hybrid, principal, _, _, chunks = _make_retriever(["acl denied secret"])
    deny = AccessGrant(
        action=Action.DOCUMENT_READ.value,
        effect=Effect.DENY.value,
        user_id=principal.user_id,
    )
    document_id = str(chunks[0][1][0])
    hybrid._dense._documents[document_id] = replace(
        hybrid._dense._documents[document_id], acl=(deny,)
    )

    dense = hybrid._dense.search("acl denied", principal, policy_epoch=7, top_k=5)
    bm25 = hybrid._bm25_search("acl denied", principal, 7, 5)

    assert dense.evidence == ()
    assert bm25 == ()


def test_superseded_version_candidates_are_absent_from_dense_and_bm25():
    hybrid, principal, _ = _catalog(
        [(uuid4(), "superseded secret", (), "ACTIVE", "SUPERSEDED")]
    )

    assert hybrid._dense.search("superseded", principal, policy_epoch=7, top_k=5).evidence == ()
    assert hybrid._bm25_search("superseded", principal, 7, 5) == ()


def test_staging_index_candidates_are_absent_from_dense_and_bm25():
    hybrid, principal, _ = _catalog(
        [(uuid4(), "staging secret", (), "STAGING", "ACTIVE")]
    )

    assert hybrid._dense.search("staging", principal, policy_epoch=7, top_k=5).evidence == ()
    assert hybrid._bm25_search("staging", principal, 7, 5) == ()


def test_stale_policy_candidates_are_absent_from_dense_and_bm25():
    hybrid, principal, _ = _catalog(
        [(uuid4(), "stale policy secret", (), "ACTIVE", "ACTIVE")]
    )

    assert hybrid._dense.search("stale policy", principal, policy_epoch=6, top_k=5).evidence == ()
    assert hybrid._bm25_search("stale policy", principal, 6, 5) == ()


def test_policy_store_outage_fails_closed_without_candidate_metadata():
    hybrid, principal, _, _, chunks = _make_retriever(["policy outage secret"])
    hybrid._dense._pep.evaluator.policy_store.available = False

    result = hybrid.search("policy outage", principal, policy_epoch=7)

    assert result.evidence == ()
    assert "policy outage secret" not in repr(result)
    assert str(chunks[0][0].chunk_id) not in repr(result)


def test_reranker_failure_returns_error_without_evidence():
    hybrid, principal, _, _, _ = _make_retriever(["reranker failure secret"])
    hybrid._model_gateway = _gateway_with_failure(reranker=True)

    result = hybrid.search("reranker failure", principal, policy_epoch=7)

    assert result.status == "ERROR"
    assert result.evidence == ()
    assert "reranker failure secret" not in repr(result)


def test_embedding_failure_fails_closed_without_bm25_fallback_leak():
    hybrid, principal, _, _, _ = _make_retriever(["embedding failure secret"])
    hybrid._dense._model_gateway = _gateway_with_failure(embedding=True)

    result = hybrid.search("embedding failure", principal, policy_epoch=7)

    assert result.status == "ERROR"
    assert result.evidence == ()


def test_source_fetch_redacts_acl_denied_content_and_citation():
    hybrid, principal, _, _, chunks = _make_retriever(["download denied secret"])
    deny = AccessGrant(
        action=Action.SOURCE_DOWNLOAD.value,
        effect=Effect.DENY.value,
        user_id=principal.user_id,
    )
    document_id = str(chunks[0][1][0])
    hybrid._dense._documents[document_id] = replace(
        hybrid._dense._documents[document_id], acl=(deny,)
    )

    source = hybrid.fetch_source(chunks[0][0].chunk_id, principal, policy_epoch=7)

    assert source.redacted is True
    assert source.content is None
    assert source.citation is None
    assert "download denied secret" not in repr(source)


def test_bm25_filters_unauthorized_high_frequency_candidates_before_scoring():
    hybrid, principal, _, _, chunks = _make_retriever(
        ["authorized secret", "secret secret secret classified payload"]
    )
    deny = AccessGrant(
        action=Action.DOCUMENT_READ.value,
        effect=Effect.DENY.value,
        user_id=principal.user_id,
    )
    denied_document_id = str(chunks[1][1][0])
    hybrid._dense._documents[denied_document_id] = replace(
        hybrid._dense._documents[denied_document_id], acl=(deny,)
    )

    ranked = hybrid._bm25_search("secret", principal, 7, 5)

    assert [item[0].chunk_id for item in ranked] == [str(chunks[0][0].chunk_id)]
    assert "classified payload" not in repr(ranked)
