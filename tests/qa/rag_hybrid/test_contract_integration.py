from dataclasses import replace
from pathlib import Path

import pytest

from backend.app.authorization.policy import AccessGrant, Action, Effect
from backend.app.rag.hybrid import HybridRetrievalConfig, InMemoryBM25Index
from backend.tests.test_hybrid_retrieval import _make_retriever


ROOT = Path(__file__).resolve().parents[3]


def test_hybrid_config_matches_contract_defaults():
    config = HybridRetrievalConfig()

    assert (config.branch_top_k, config.rrf_k, config.rerank_top_k) == (20, 60, 20)


def test_hybrid_config_rejects_nonpositive_branch_limit():
    with pytest.raises(ValueError):
        HybridRetrievalConfig(branch_top_k=0)


def test_hybrid_config_rejects_negative_rrf_constant():
    with pytest.raises(ValueError):
        HybridRetrievalConfig(rrf_k=-1)


def test_bm25_config_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        InMemoryBM25Index(k1=1.5, b=2)


def test_hybrid_search_rejects_nonpositive_top_k():
    hybrid, principal, _, _, _ = _make_retriever(["contract boundary"])

    with pytest.raises(ValueError):
        hybrid.search("contract", principal, policy_epoch=7, top_k=0)


def test_hybrid_search_rejects_empty_query():
    hybrid, principal, _, _, _ = _make_retriever(["contract boundary"])

    with pytest.raises(ValueError):
        hybrid.search("  ", principal, policy_epoch=7)


def test_evidence_carries_version_page_and_source_span_contract_fields():
    hybrid, principal, _, _, _ = _make_retriever(["version-bound evidence"])

    result = hybrid.search("version evidence", principal, policy_epoch=7, top_k=1)
    citation = result.evidence[0].citation

    assert citation.chunk_id and citation.document_id and citation.version_id
    assert citation.page_start == 2
    assert citation.page_end == 2
    assert citation.source_span is not None


def test_source_fetch_rechecks_download_authorization_and_redacts_content():
    hybrid, principal, _, _, chunks = _make_retriever(["download restricted evidence"])
    deny_download = AccessGrant(
        action=Action.SOURCE_DOWNLOAD.value,
        effect=Effect.DENY.value,
        user_id=principal.user_id,
    )
    document_id = str(chunks[0][1][0])
    hybrid._dense._documents[document_id] = replace(
        hybrid._dense._documents[document_id], acl=(deny_download,)
    )

    source = hybrid.fetch_source(chunks[0][0].chunk_id, principal, policy_epoch=7)

    assert source.redacted is True
    assert source.content is None
    assert source.citation is None


def test_retrieval_contract_requires_identical_filters_and_secure_pipeline():
    contract = (ROOT / "docs/contracts/retrieval.md").read_text(encoding="utf-8")

    assert "identical ACL/tenant/active filters in dense and BM25 branches" in contract
    assert "RRF fusion → reranking → deduplication" in contract
    assert "Missing/denied docs remain invisible; failures fail closed" in contract


def test_answer_contract_requires_current_version_and_fresh_source_checks():
    contract = (ROOT / "docs/contracts/answer-and-citation.md").read_text(encoding="utf-8")

    assert "if that version is no longer ACTIVE" in contract
    assert "rechecks `document:read`/`source:download` on each fetch" in contract
    assert "never silently substitute a newer version" in contract
