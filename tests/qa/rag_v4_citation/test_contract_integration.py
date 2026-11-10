import json
from datetime import datetime, timezone

from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.knowledge.models import DOCXLocator, PDFLocator, SourceSpan, XLSXLocator, to_qdrant_payload
from backend.app.models.policy import DataClassification
from backend.app.rag import (
    AnswerCitation,
    Citation,
    DirectAnswerPipeline,
    GeneratedAnswer,
    HybridEvidence,
    HybridRetrievalResult,
)
from backend.app.rag.parent_child import ChildEvidence, ParentRecord, expand_parent_context
from backend.tests.test_hybrid_retrieval import _make_parent_child_retriever, _make_retriever


class _CapturingModel:
    def __init__(self, claim_text: str) -> None:
        self.claim_text = claim_text
        self.messages = ()

    def generate(self, messages, *, classification):
        self.messages = messages
        assert classification is DataClassification.INTERNAL
        return GeneratedAnswer(self.claim_text, (Claim("claim-1", self.claim_text, ("c-1",)),))


class _StaticRetriever:
    def __init__(self, evidence, expanded=()):
        self.result = HybridRetrievalResult(tuple(evidence), "OK", tuple(expanded))

    def search(self, query, principal, *, policy_epoch, top_k=8):
        return self.result


def _principal(tenant="tenant-a"):
    return AuthenticatedPrincipal(
        user_id="user-1",
        tenant_id=tenant,
        roles=["employee"],
        department_ids=["department-1"],
        session_id="session-1",
        auth_time="2026-11-10T00:00:00Z",
    )


def _citation(locator, *, chunk_id="chunk-1", tenant="tenant-a", epoch=42, audience="answer-client", expires_at=None):
    return Citation(
        chunk_id=chunk_id,
        document_id="doc-1",
        version_id="v-2",
        tenant_id=tenant,
        policy_epoch=epoch,
        locator=locator,
        audience=audience,
        expires_at=expires_at,
    )


def _allow(record):
    return AuthorizationDecision(
        allowed=True,
        tenant_id=record.tenant_id,
        document_id=record.document_id,
        version_id=record.version_id,
        current_version_id=record.version_id,
        status="ACTIVE",
    )


def test_retrieval_result_keeps_backward_compatible_empty_parent_context():
    result = HybridRetrievalResult((), "OK")

    assert result.expanded_context == ()


def test_runtime_parent_context_is_separate_from_ranked_evidence():
    hybrid, principal, parent_id, child_id = _make_parent_child_retriever()

    result = hybrid.search("warranty coverage", principal, policy_epoch=7, top_k=1)

    assert [item.citation.chunk_id for item in result.evidence] == [child_id]
    assert [item.citation.chunk_id for item in result.expanded_context] == [parent_id]


def test_parent_expansion_preserves_typed_pdf_locator():
    locator = PDFLocator(page=4, source_span=SourceSpan(start=10, end=30))
    child = ChildEvidence("child", "tenant-a", "doc-1", "v-1", "child text", _citation(locator), "parent")
    parent = ParentRecord("parent", "tenant-a", "doc-1", "v-1", "parent text", locator)

    result = expand_parent_context((child,), (parent,), lambda record: True)

    assert result.parents[0].source_locator == locator
    assert result.parents[0].source_locator.kind == "PDF"


def test_parent_expansion_preserves_typed_docx_locator():
    locator = DOCXLocator(heading="Security policy", paragraph=7)
    child = ChildEvidence("child", "tenant-a", "doc-1", "v-1", "child text", _citation(locator), "parent")
    parent = ParentRecord("parent", "tenant-a", "doc-1", "v-1", "parent text", locator)

    result = expand_parent_context((child,), (parent,), lambda record: True)

    assert result.parents[0].source_locator == locator
    assert result.parents[0].source_locator.kind == "DOCX"


def test_parent_expansion_preserves_typed_xlsx_locator():
    locator = XLSXLocator(sheet="Revenue", cell_range="B4:F12")
    child = ChildEvidence("child", "tenant-a", "doc-1", "v-1", "child text", _citation(locator), "parent")
    parent = ParentRecord("parent", "tenant-a", "doc-1", "v-1", "parent text", locator)

    result = expand_parent_context((child,), (parent,), lambda record: True)

    assert result.parents[0].source_locator == locator
    assert result.parents[0].source_locator.kind == "XLSX"


def test_answer_pipeline_adds_authorized_parent_to_secure_context():
    locator = PDFLocator(page=1, source_span=SourceSpan(start=0, end=10))
    child = HybridEvidence(_citation(locator), 2.0, "child fact", 1.0, 2.0)
    parent = HybridEvidence(
        _citation(locator, chunk_id="parent-1"), 0.0, "parent context", 0.0, 0.0
    )
    model = _CapturingModel("child fact")
    pipeline = DirectAnswerPipeline(
        retriever=_StaticRetriever((child,), (parent,)),
        model_gateway=model,
        authorize_citation=_allow,
    )

    result = pipeline.answer("what is the fact", _principal(), policy_epoch=42)

    context = "\n".join(message["content"] for message in model.messages)
    assert result.status == "ANSWERED"
    assert "child fact" in context
    assert "parent context" in context


def test_answer_citation_serializes_typed_locator_and_bindings():
    locator = DOCXLocator(heading="Retention", paragraph=3)
    output = AnswerCitation(
        citation_id="c-1",
        tenant_id="tenant-a",
        document_id="doc-1",
        version_id="v-2",
        policy_epoch=42,
        audience="answer-client",
        expires_at=datetime(2026, 11, 11, tzinfo=timezone.utc),
        locator=locator,
        evidence_snapshot_hash="a" * 64,
        chunk_id="chunk-1",
    )

    payload = output.to_dict()

    assert payload["locator"] == {"kind": "DOCX", "heading": "Retention", "paragraph": 3}
    assert payload["tenant_id"] == "tenant-a"
    assert payload["policy_epoch"] == 42
    assert json.loads(output.to_json()) == payload


def test_source_fetch_and_search_share_version_bound_citation():
    hybrid, principal, _, _, chunks = _make_retriever(["same version source"])

    result = hybrid.search("same version", principal, policy_epoch=7, top_k=1)
    source = hybrid.fetch_source(chunks[0][0].chunk_id, principal, policy_epoch=7)

    assert source.redacted is False
    assert source.citation == result.evidence[0].citation
    assert source.citation.version_id == result.evidence[0].citation.version_id


def test_policy_epoch_is_propagated_to_ranked_and_expanded_citations():
    hybrid, principal, parent_id, child_id = _make_parent_child_retriever()

    result = hybrid.search("warranty coverage", principal, policy_epoch=7, top_k=1)

    assert result.evidence[0].citation.policy_epoch == 7
    assert result.expanded_context[0].citation.policy_epoch == 7
    assert {result.evidence[0].citation.chunk_id, result.expanded_context[0].citation.chunk_id} == {
        child_id,
        parent_id,
    }


def test_qdrant_projection_contains_discriminated_source_locator():
    _, _, _, _, chunks = _make_retriever(["payload provenance"])

    payload = to_qdrant_payload(chunks[0][0])

    assert payload["source_locator"]["kind"] == "PDF"
    assert payload["source_locator"]["page"] == 2
