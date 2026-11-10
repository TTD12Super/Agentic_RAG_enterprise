import hashlib
import json
from datetime import datetime, timedelta, timezone

from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.knowledge.models import DOCXLocator, PDFLocator, SourceSpan, XLSXLocator
from backend.app.models.policy import DataClassification
from backend.app.rag import Citation, DirectAnswerPipeline, GeneratedAnswer, HybridEvidence, HybridRetrievalResult
from backend.tests.test_hybrid_retrieval import _make_parent_child_retriever, _make_retriever


class _StaticRetriever:
    def __init__(self, evidence, expanded=()):
        self.result = HybridRetrievalResult(tuple(evidence), "OK", tuple(expanded))

    def search(self, query, principal, *, policy_epoch, top_k=8):
        return self.result


class _Model:
    def __init__(self, text: str, citation_id="c-1"):
        self.text = text
        self.citation_id = citation_id
        self.messages = ()

    def generate(self, messages, *, classification):
        self.messages = messages
        assert classification is DataClassification.INTERNAL
        return GeneratedAnswer(self.text, (Claim("claim-1", self.text, (self.citation_id,)),))


def _principal(tenant="tenant-a"):
    return AuthenticatedPrincipal(
        user_id="user-1",
        tenant_id=tenant,
        roles=["employee"],
        department_ids=["department-1"],
        session_id="session-1",
        auth_time="2026-11-10T00:00:00Z",
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


def _locator(kind):
    if kind == "PDF":
        return PDFLocator(page=3, source_span=SourceSpan(start=4, end=25))
    if kind == "DOCX":
        return DOCXLocator(heading="Operations", paragraph=4)
    return XLSXLocator(sheet="Revenue", cell_range="B4:F12")


def _answer(locator, text="retention is thirty days", *, audience="answer-client", expires_at=None):
    citation = Citation(
        "chunk-1",
        "doc-1",
        "v-2",
        "tenant-a",
        42,
        locator,
        audience=audience,
        expires_at=expires_at,
    )
    model = _Model(text)
    pipeline = DirectAnswerPipeline(
        retriever=_StaticRetriever((HybridEvidence(citation, 1.0, text, 1.0, 1.0),)),
        model_gateway=model,
        authorize_citation=_allow,
    )
    return pipeline.answer("retention", _principal(), policy_epoch=42), model


def test_full_hybrid_workflow_returns_ranked_child_and_parent_context():
    hybrid, principal, parent_id, child_id = _make_parent_child_retriever()

    result = hybrid.search("warranty coverage", principal, policy_epoch=7, top_k=1)

    assert result.status == "OK"
    assert result.evidence[0].citation.chunk_id == child_id
    assert result.expanded_context[0].citation.chunk_id == parent_id


def test_answer_workflow_consumes_parent_context_without_ranking_parent():
    hybrid, principal, _, child_id = _make_parent_child_retriever()
    model = _Model("Warranty coverage applies for twelve months.")
    pipeline = DirectAnswerPipeline(
        retriever=hybrid,
        model_gateway=model,
        authorize_citation=_allow,
        top_k=1,
    )

    result = pipeline.answer("warranty coverage", principal, policy_epoch=7)

    rendered = "\n".join(message["content"] for message in model.messages)
    assert result.status == "ANSWERED"
    assert child_id in rendered
    assert "General policy context for chapter seven." in rendered


def test_pdf_answer_citation_is_typed_and_version_bound():
    result, _ = _answer(_locator("PDF"))

    assert result.status == "ANSWERED"
    assert result.citations[0].locator.kind == "PDF"
    assert result.citations[0].version_id == "v-2"


def test_docx_answer_citation_is_typed_and_serializable():
    result, _ = _answer(_locator("DOCX"))

    assert result.citations[0].locator.kind == "DOCX"
    assert json.loads(result.citations[0].to_json())["locator"]["heading"] == "Operations"


def test_xlsx_answer_citation_is_typed_and_serializable():
    result, _ = _answer(_locator("XLSX"))

    assert result.citations[0].locator.kind == "XLSX"
    assert result.citations[0].to_dict()["locator"]["cell_range"] == "B4:F12"


def test_expired_citation_is_not_delivered_to_answer_client():
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)

    result, _ = _answer(_locator("PDF"), expires_at=expired)

    assert result.citations == ()
    assert result.status.value == "INSUFFICIENT_EVIDENCE"


def test_audience_and_expiry_survive_citation_delivery():
    expires = datetime.now(timezone.utc) + timedelta(minutes=5)

    result, _ = _answer(_locator("PDF"), audience="employee-web", expires_at=expires)

    output = result.citations[0]
    assert output.audience == "employee-web"
    assert output.expires_at == expires


def test_evidence_snapshot_hash_matches_exact_authorized_text():
    text = "retention is thirty days"
    result, _ = _answer(_locator("PDF"), text)

    assert result.citations[0].evidence_snapshot_hash == hashlib.sha256(text.encode()).hexdigest()


def test_reranker_failure_returns_safe_error_without_context():
    hybrid, principal, _, _ = _make_parent_child_retriever()
    hybrid._model_gateway = object()

    result = hybrid.search("warranty coverage", principal, policy_epoch=7, top_k=1)

    assert result.status == "ERROR"
    assert result.evidence == ()
    assert result.expanded_context == ()


def test_policy_outage_fails_closed_then_recovers_deterministically():
    hybrid, principal, _, _, _ = _make_retriever(["recoverable policy evidence"])
    hybrid._dense._pep.evaluator.policy_store.available = False

    unavailable = hybrid.search("recoverable evidence", principal, policy_epoch=7)
    hybrid._dense._pep.evaluator.policy_store.available = True
    recovered = hybrid.search("recoverable evidence", principal, policy_epoch=7)

    assert unavailable.evidence == ()
    assert recovered.status == "OK"
    assert recovered.evidence[0].text == "recoverable policy evidence"
