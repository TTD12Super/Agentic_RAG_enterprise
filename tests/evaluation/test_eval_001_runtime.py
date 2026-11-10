"""Runtime evidence for EVAL-001; all fixtures and model seams are synthetic/local."""

from __future__ import annotations

from backend.app.rag import AnswerStatus
from tests.evaluation.eval_001_runner import _make_case, evaluation_snapshot
from tests.evaluation._evaluation_harness import load_validated_records


def test_all_golden_cases_run_through_v1_v3():
    result = evaluation_snapshot()
    assert all(result["versions"][version]["cases"] == 200 for version in ("V1", "V2", "V3"))


def test_v1_v3_have_zero_forbidden_source_leakage():
    result = evaluation_snapshot()
    assert result["security"]["forbidden_source_leakage_cases"] == {"V1": 0, "V2": 0, "V3": 0}


def test_dataset_contains_permission_negative_and_cross_tenant_cases():
    result = evaluation_snapshot()
    assert result["security"]["permission_negative_cases"] >= 50
    assert result["security"]["cross_tenant_cases"] > 0


def test_answered_case_keeps_citation_version_and_tenant_binding():
    record = next(item for item in load_validated_records() if item["expected_status"] == "ANSWERED")
    case = _make_case(record)
    result = case.pipelines["V3"].answer(record["query"], case.principal, policy_epoch=7)
    assert result.status is AnswerStatus.ANSWERED
    assert all(citation.version_id == case.chunk_to_scope[citation.chunk_id][2] for citation in result.citations)
    assert all(case.chunk_to_span[citation.chunk_id]["tenant_id"] == record["tenant_id"] for citation in result.citations)


def test_permission_negative_case_returns_safe_no_answer_without_evidence():
    record = next(item for item in load_validated_records() if "permission-negative" in item["tags"])
    case = _make_case(record)
    result = case.pipelines["V3"].answer(record["query"], case.principal, policy_epoch=7)
    assert result.status is AnswerStatus.INSUFFICIENT_EVIDENCE
    assert result.citations == ()
    assert result.answer == "Insufficient evidence to answer this question."


def test_unanswerable_case_abstains_without_model_answer():
    record = next(item for item in load_validated_records() if "unanswerable" in item["tags"])
    case = _make_case(record)
    result = case.pipelines["V3"].answer(record["query"], case.principal, policy_epoch=7)
    assert result.status is AnswerStatus.INSUFFICIENT_EVIDENCE
    assert result.citations == ()


def test_empty_query_is_denied_before_retrieval():
    record = load_validated_records()[0]
    case = _make_case(record)
    result = case.pipelines["V3"].answer("", case.principal, policy_epoch=7)
    assert result.status is AnswerStatus.ACCESS_DENIED
    assert result.reason_codes == ("empty_input",)


def test_repeatability_has_stable_quality_metrics():
    result = evaluation_snapshot()
    for version in ("V1", "V2", "V3"):
        assert result["repeatability"][version] is True


def test_v4_is_explicitly_not_run_instead_of_inventing_metrics():
    assert evaluation_snapshot()["v4"]["status"] == "NOT_RUN"


def test_allowed_answer_has_no_unauthorized_retrieval_marker():
    result = evaluation_snapshot()
    for version in ("V1", "V2", "V3"):
        assert result["versions"][version]["unauthorized_retrieval_rate"] == 0.0


def test_model_failure_returns_error_without_source_or_answer():
    record = next(item for item in load_validated_records() if item["expected_status"] == "ANSWERED")
    case = _make_case(record)

    class FailingAnswerModel:
        def generate(self, messages, *, classification):
            raise RuntimeError("synthetic provider failure")

    pipeline = case.pipelines["V3"]
    pipeline._model_gateway = FailingAnswerModel()
    result = pipeline.answer(record["query"], case.principal, policy_epoch=7)
    assert result.status is AnswerStatus.ERROR
    assert result.answer == ""
    assert result.citations == ()
