import hashlib

from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.models.policy import DataClassification
from backend.app.rag import DirectAnswerPipeline, GeneratedAnswer
from backend.tests.test_hybrid_retrieval import _make_parent_child_retriever, _make_retriever


class _Model:
    def __init__(self, text: str) -> None:
        self.text = text

    def generate(self, messages, *, classification):
        assert classification is DataClassification.INTERNAL
        return GeneratedAnswer(self.text, (Claim("claim-1", self.text, ("c-1",)),))


class _CapturingModel(_Model):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.messages = ()

    def generate(self, messages, *, classification):
        self.messages = messages
        return super().generate(messages, classification=classification)


def test_real_hybrid_path_propagates_pdf_schema_end_to_end():
    text = "Product A warranty coverage applies for twelve months."
    retriever, principal, _, tenant_id, _ = _make_retriever([text])

    def authorize(record):
        return AuthorizationDecision(
            allowed=True,
            tenant_id=record.tenant_id,
            document_id=record.document_id,
            version_id=record.version_id,
            current_version_id=record.version_id,
            status="ACTIVE",
        )

    result = DirectAnswerPipeline(
        retriever=retriever,
        model_gateway=_Model(text),
        authorize_citation=authorize,
    ).answer("Product A warranty coverage", principal, policy_epoch=7)

    assert result.status == "ANSWERED"
    citation = result.citations[0]
    assert citation.tenant_id == str(tenant_id)
    assert citation.policy_epoch == 7
    assert citation.document_id
    assert citation.version_id
    assert citation.chunk_id
    assert citation.locator.kind == "PDF"
    assert citation.page == 2
    assert citation.source_span == (4, 28)
    assert citation.evidence_snapshot_hash == hashlib.sha256(text.encode()).hexdigest()
    assert citation.to_dict()["locator"] == {
        "kind": "PDF",
        "page": 2,
        "source_span": {"start": 4, "end": 28},
    }


def test_direct_answer_context_includes_authorized_parent_runtime():
    retriever, principal, _, _ = _make_parent_child_retriever()
    text = "Warranty coverage applies for twelve months."
    model = _CapturingModel(text)

    def authorize(record):
        return AuthorizationDecision(
            allowed=True,
            tenant_id=record.tenant_id,
            document_id=record.document_id,
            version_id=record.version_id,
            current_version_id=record.version_id,
            status="ACTIVE",
        )

    result = DirectAnswerPipeline(
        retriever=retriever,
        model_gateway=model,
        authorize_citation=authorize,
    ).answer("Warranty coverage", principal, policy_epoch=7)

    assert result.status == "ANSWERED"
    rendered = "\n".join(message["content"] for message in model.messages)
    assert "General policy context for chapter seven." in rendered
