from hashlib import sha256

import pytest

from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.models.policy import DataClassification
from backend.app.rag import (
    AnswerStatus,
    DirectAnswerPipeline,
    GeneratedAnswer,
)
from backend.app.rag.hybrid import HybridRetrievalResult
from backend.tests.test_hybrid_retrieval import _make_retriever


TEXT = "Product A warranty coverage applies for twelve months."


class FakeModelGateway:
    def __init__(self, generated=None, error=None):
        self.generated = generated
        self.error = error
        self.calls = []

    def generate(self, messages, *, classification):
        self.calls.append((messages, classification))
        if self.error is not None:
            raise self.error
        return self.generated


class RaisingRetriever:
    def search(self, *args, **kwargs):
        raise RuntimeError("synthetic retrieval failure")


class StaticRetriever:
    def __init__(self, result):
        self.result = result

    def search(self, *args, **kwargs):
        return self.result


class RaisingVerifier:
    def verify(self, request):
        raise RuntimeError("synthetic verifier failure")


def _authorization(tenant_id, *, allowed=True, **updates):
    def authorize(citation):
        return AuthorizationDecision(
            allowed=allowed,
            tenant_id=updates.get("tenant_id", tenant_id),
            document_id=updates.get("document_id", citation.document_id),
            version_id=updates.get("version_id", citation.version_id),
            current_version_id=updates.get("current_version_id", citation.version_id),
            status=updates.get("status", "ACTIVE"),
            revoked=updates.get("revoked", False),
        )

    return authorize


def _pipeline(text=TEXT, *, generated=None, authorize=None, model=None):
    retriever, principal, _, tenant_id, _ = _make_retriever([text])
    if model is None:
        model = FakeModelGateway(
            generated or GeneratedAnswer(text, (Claim("claim-1", text, ("c-1",)),))
        )
    pipeline = DirectAnswerPipeline(
        retriever=retriever,
        model_gateway=model,
        authorize_citation=authorize or _authorization(str(tenant_id)),
    )
    return pipeline, principal, model, str(tenant_id)


def test_supported_answer_returns_answered_and_text():
    pipeline, principal, _, _ = _pipeline()

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ANSWERED
    assert result.answer == TEXT


def test_supported_answer_exposes_bound_hash_and_provenance():
    pipeline, principal, _, _ = _pipeline()

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    citation = result.citations[0]
    assert citation.citation_id == "c-1"
    assert citation.document_id and citation.version_id and citation.chunk_id
    assert citation.page == 2
    assert citation.source_span[1] > citation.source_span[0]
    assert citation.evidence_snapshot_hash == sha256(TEXT.encode()).hexdigest()


def test_mixed_claims_return_partial_with_only_supported_citations():
    model = FakeModelGateway(
        GeneratedAnswer(
            f"{TEXT} Return window requires more evidence.",
            (Claim("supported", TEXT, ("c-1",)), Claim("unknown", "Return window is seven days.")),
        )
    )
    pipeline, principal, _, _ = _pipeline(model=model)

    result = pipeline.answer("warranty and return window", principal, policy_epoch=7)

    assert result.status is AnswerStatus.PARTIAL
    assert [item.citation_id for item in result.citations] == ["c-1"]


def test_empty_retrieval_returns_insufficient_without_model_call():
    _, principal, _, tenant_id = _pipeline()
    model = FakeModelGateway()
    pipeline = DirectAnswerPipeline(
        retriever=StaticRetriever(HybridRetrievalResult((), "INSUFFICIENT_EVIDENCE")),
        model_gateway=model,
        authorize_citation=_authorization(tenant_id),
    )

    result = pipeline.answer("unmatched question", principal, policy_epoch=7)

    assert result.status is AnswerStatus.INSUFFICIENT_EVIDENCE
    assert result.answer == "Insufficient evidence to answer this question."
    assert result.citations == ()
    assert model.calls == []


def test_denied_citation_returns_insufficient_without_context_or_answer():
    pipeline, principal, model, tenant_id = _pipeline()
    pipeline._authorize_citation = _authorization(tenant_id, allowed=False)

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.INSUFFICIENT_EVIDENCE
    assert result.answer == "Insufficient evidence to answer this question."
    assert result.citations == ()
    assert model.calls == []


def test_retrieval_exception_returns_error_without_output():
    _, principal, _, tenant_id = _pipeline()
    model = FakeModelGateway()
    pipeline = DirectAnswerPipeline(
        retriever=RaisingRetriever(),
        model_gateway=model,
        authorize_citation=_authorization(tenant_id),
    )

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ERROR
    assert result.answer == ""
    assert result.citations == ()


def test_model_exception_returns_error_without_output():
    model = FakeModelGateway(error=RuntimeError("synthetic model outage"))
    pipeline, principal, _, _ = _pipeline(model=model)

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ERROR
    assert result.reason_codes == ("model_failed",)
    assert result.answer == ""
    assert result.citations == ()


def test_verifier_exception_returns_error_without_output():
    pipeline, principal, _, _ = _pipeline()
    pipeline._verifier = RaisingVerifier()

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ERROR
    assert result.reason_codes == ("evidence_verification_failed",)
    assert result.answer == ""
    assert result.citations == ()


def test_non_generated_model_value_is_rejected():
    pipeline, principal, _, _ = _pipeline(model=FakeModelGateway(generated={"answer": TEXT}))

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ERROR
    assert result.reason_codes == ("invalid_model_response",)
    assert result.answer == ""
    assert result.citations == ()


def test_model_receives_internal_secure_context():
    pipeline, principal, model, _ = _pipeline()

    pipeline.answer("Product A warranty", principal, policy_epoch=7)

    messages, classification = model.calls[0]
    assert classification is DataClassification.INTERNAL
    assert len(messages) == 3
    assert "<<<TRUSTED_SYSTEM_INSTRUCTIONS>>>" in messages[0]["content"]
    assert "<<<UNTRUSTED_RETRIEVED_CONTENT>>>" in messages[2]["content"]
    assert "Product A warranty" in messages[1]["content"]


def test_same_inputs_produce_identical_result():
    pipeline, principal, _, _ = _pipeline()

    first = pipeline.answer("Product A warranty", principal, policy_epoch=7)
    second = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert first == second


def test_constructor_rejects_non_positive_top_k():
    retriever, _, _, tenant_id, _ = _make_retriever([TEXT])

    with pytest.raises(ValueError, match="top_k"):
        DirectAnswerPipeline(
            retriever=retriever,
            model_gateway=FakeModelGateway(),
            authorize_citation=_authorization(str(tenant_id)),
            top_k=0,
        )
