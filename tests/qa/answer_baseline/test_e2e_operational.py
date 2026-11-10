from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.integrations.model_gateway import ModelEgressDenied
from backend.app.models.policy import DataClassification
from backend.app.rag import AnswerStatus, DirectAnswerPipeline, GeneratedAnswer
from backend.tests.test_hybrid_retrieval import _make_retriever


TEXT = "Product A warranty coverage applies for twelve months."


class FakeAnswerGateway:
    def __init__(self, generated=None, error=None):
        self.generated = generated
        self.error = error
        self.calls = []

    def generate(self, messages, *, classification):
        self.calls.append((messages, classification))
        if self.error is not None:
            raise self.error
        return self.generated


class FailingReranker:
    def rerank(self, *args, **kwargs):
        raise RuntimeError("synthetic reranker outage")


class FailingEmbedder:
    def embed(self, *args, **kwargs):
        raise RuntimeError("synthetic embedding outage")


def _allow(tenant_id):
    def authorize(citation):
        return AuthorizationDecision(
            allowed=True,
            tenant_id=tenant_id,
            document_id=citation.document_id,
            version_id=citation.version_id,
            current_version_id=citation.version_id,
            status="ACTIVE",
            revoked=False,
        )

    return authorize


def _setup(texts=(TEXT,), *, generated=None, error=None):
    retriever, principal, _, tenant_id, _ = _make_retriever(list(texts))
    model = FakeAnswerGateway(
        generated or GeneratedAnswer(TEXT, (Claim("claim-1", TEXT, ("c-1",)),)),
        error=error,
    )
    pipeline = DirectAnswerPipeline(
        retriever=retriever,
        model_gateway=model,
        authorize_citation=_allow(str(tenant_id)),
    )
    return pipeline, principal, model, retriever, str(tenant_id)


def test_operational_supported_path_returns_answer_and_citation():
    pipeline, principal, _, _, _ = _setup()

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ANSWERED
    assert result.answer == TEXT
    assert len(result.citations) == 1


def test_operational_partial_path_preserves_supported_evidence_only():
    generated = GeneratedAnswer(
        f"{TEXT} Return window is not established.",
        (Claim("supported", TEXT, ("c-1",)), Claim("unknown", "Return window is seven days.")),
    )
    pipeline, principal, _, _, _ = _setup(generated=generated)

    result = pipeline.answer("warranty and return window", principal, policy_epoch=7)

    assert result.status is AnswerStatus.PARTIAL
    assert [item.citation_id for item in result.citations] == ["c-1"]


def test_operational_abstention_is_insufficient_evidence():
    generated = GeneratedAnswer("Insufficient evidence to answer this question.", ())
    pipeline, principal, _, _, _ = _setup(generated=generated)

    result = pipeline.answer("unrelated question", principal, policy_epoch=7)

    assert result.status is AnswerStatus.INSUFFICIENT_EVIDENCE
    assert result.answer == "Insufficient evidence to answer this question."
    assert result.citations == ()


def test_operational_reauthorization_revocation_returns_access_denied():
    pipeline, principal, model, _, tenant_id = _setup()
    calls = 0

    def revoke_after_retrieval(citation):
        nonlocal calls
        calls += 1
        return AuthorizationDecision(
            allowed=calls == 1,
            tenant_id=tenant_id,
            document_id=citation.document_id,
            version_id=citation.version_id,
            current_version_id=citation.version_id,
            status="ACTIVE",
            revoked=calls > 1,
        )

    pipeline._authorize_citation = revoke_after_retrieval
    pipeline._verifier._authorize = revoke_after_retrieval

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ACCESS_DENIED
    assert result.answer == ""
    assert result.citations == ()
    assert calls == 2
    assert len(model.calls) == 1


def test_operational_reranker_failure_returns_error_without_evidence():
    pipeline, principal, model, retriever, _ = _setup()
    retriever._model_gateway._reranker_adapters = {
        "deterministic-local": FailingReranker()
    }

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ERROR
    assert result.reason_codes == ("retrieval_failed",)
    assert result.answer == ""
    assert result.citations == ()
    assert model.calls == []


def test_operational_embedding_failure_does_not_fallback_to_bm25():
    pipeline, principal, model, retriever, _ = _setup()
    retriever._dense._model_gateway._embedding_adapters = {
        "deterministic-local": FailingEmbedder()
    }

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ERROR
    assert result.reason_codes == ("retrieval_failed",)
    assert result.answer == ""
    assert result.citations == ()
    assert model.calls == []


def test_operational_model_egress_failure_is_fail_closed():
    error = ModelEgressDenied("synthetic-external", DataClassification.INTERNAL)
    pipeline, principal, _, _, _ = _setup(error=error)

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ERROR
    assert result.reason_codes == ("model_failed",)
    assert result.answer == ""
    assert result.citations == ()


def test_operational_conflicting_evidence_is_not_harmonized():
    generated = GeneratedAnswer(
        "Product A warranty is 12 months.",
        (Claim("conflict", "Product A warranty is 12 months.", ("c-1", "c-2")),),
    )
    pipeline, principal, _, _, _ = _setup(
        texts=(
            "Product A warranty is 12 months.",
            "Product A warranty is 6 months.",
        ),
        generated=generated,
    )

    result = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert result.status is AnswerStatus.ERROR
    assert result.reason_codes == ("conflicting_evidence",)
    assert result.answer == ""
    assert result.citations == ()


def test_operational_repeatability_holds_for_answer_and_metadata():
    pipeline, principal, _, _, _ = _setup()

    first = pipeline.answer("Product A warranty", principal, policy_epoch=7)
    second = pipeline.answer("Product A warranty", principal, policy_epoch=7)

    assert first == second


def test_operational_oversized_query_is_bounded_and_denied():
    pipeline, principal, model, _, _ = _setup()

    result = pipeline.answer("x" * 8_001, principal, policy_epoch=7)

    assert result.status is AnswerStatus.ACCESS_DENIED
    assert result.answer == ""
    assert result.citations == ()
    assert model.calls == []


def test_operational_denied_content_never_appears_in_failure_result():
    denied = "CONFIDENTIAL DENIED TENANT PAYROLL SECRET"
    pipeline, principal, _, _, tenant_id = _setup(texts=(denied,))

    def deny(citation):
        return AuthorizationDecision(
            allowed=False,
            tenant_id=tenant_id,
            document_id=citation.document_id,
            version_id=citation.version_id,
            current_version_id=citation.version_id,
            status="ACTIVE",
            revoked=False,
        )

    pipeline._authorize_citation = deny
    result = pipeline.answer("payroll", principal, policy_epoch=7)

    assert result.status is AnswerStatus.INSUFFICIENT_EVIDENCE
    assert result.answer == "Insufficient evidence to answer this question."
    assert result.citations == ()
    assert denied not in repr(result)
