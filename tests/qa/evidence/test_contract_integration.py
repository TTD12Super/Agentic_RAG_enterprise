import inspect
from pathlib import Path

from backend.app.evidence import (
    AuthorizationDecision,
    Claim,
    CitationRecord,
    EvidenceRecord,
    EvidenceVerifier,
    SourceSpan,
    VerificationOutcome,
    VerificationRequest,
)


ROOT = Path(__file__).resolve().parents[3]
ANSWER_CONTRACT = (ROOT / "docs" / "contracts" / "answer-and-citation.md").read_text(
    encoding="utf-8"
)
RETRIEVAL_CONTRACT = (ROOT / "docs" / "contracts" / "retrieval.md").read_text(
    encoding="utf-8"
)
BASELINE = (ROOT / "docs" / "contracts" / "v1-baseline.md").read_text(
    encoding="utf-8"
)
CHAT_CONTRACT = (ROOT / "docs" / "contracts" / "chat-and-jobs.md").read_text(
    encoding="utf-8"
)


def citation(citation_id="c-1", *, version_id="v-2", tenant_id="tenant-a"):
    return CitationRecord(
        citation_id=citation_id,
        document_id="doc-1",
        version_id=version_id,
        tenant_id=tenant_id,
        source_span=SourceSpan(101, 140),
        page=4,
        chunk_id="chunk-77",
    )


def allow_active(record):
    return AuthorizationDecision(
        allowed=True,
        tenant_id=record.tenant_id,
        document_id=record.document_id,
        version_id=record.version_id,
        current_version_id=record.version_id,
        status="ACTIVE",
    )


def test_answer_contract_names_all_first_class_verification_outcomes():
    for status in ("ANSWERED", "PARTIAL", "INSUFFICIENT_EVIDENCE", "ACCESS_DENIED", "ERROR"):
        assert status in ANSWER_CONTRACT


def test_contract_requires_version_bound_snapshot_and_source_locator():
    assert "immutable evidence snapshot hash" in BASELINE
    assert "document_version_id" in BASELINE
    assert "source locator" in BASELINE
    assert "source_span" in ANSWER_CONTRACT


def test_retrieval_contract_exposes_citation_provenance_fields():
    for field in ("chunk_id", "document_id", "version_id", "page_start", "source_span", "citation_token"):
        assert field in RETRIEVAL_CONTRACT


def test_contract_requires_active_filters_and_revalidation_before_delivery():
    assert "current ACTIVE version" in RETRIEVAL_CONTRACT
    assert "Revalidate each chunk/document" in RETRIEVAL_CONTRACT
    assert "current principal may view it" in ANSWER_CONTRACT


def test_contract_forbids_stale_citation_substitution():
    assert "no longer ACTIVE" in ANSWER_CONTRACT
    assert "never silently substitute a newer version" in ANSWER_CONTRACT
    assert "never substitutes a newer version" in BASELINE


def test_contract_makes_conflict_partial_and_insufficient_results_explicit():
    assert "disclosed conflict" in ANSWER_CONTRACT
    assert "PARTIAL" in ANSWER_CONTRACT
    assert "INSUFFICIENT_EVIDENCE" in ANSWER_CONTRACT


def test_verifier_requires_a_server_supplied_authorization_callback():
    parameters = inspect.signature(EvidenceVerifier.__init__).parameters

    assert "authorize" in parameters
    assert parameters["authorize"].default is inspect.Parameter.empty


def test_duplicate_evidence_ids_are_a_malformed_fail_closed_result():
    calls = []

    def authorize(record):
        calls.append(record.citation_id)
        return allow_active(record)

    duplicate = citation("same-id")
    result = EvidenceVerifier(authorize).verify(
        VerificationRequest(
            "tenant-a",
            (Claim("claim-1", "The retention period is 30 days."),),
            (
                EvidenceRecord(duplicate, "The retention period is 30 days."),
                EvidenceRecord(duplicate, "The retention period is 90 days."),
            ),
        )
    )

    assert result.outcome is VerificationOutcome.ACCESS_DENIED
    assert result.claims[0].reason_code == "MALFORMED_EVIDENCE"
    assert calls == []


def test_supported_result_round_trips_tenant_document_version_and_span():
    record = citation()
    result = EvidenceVerifier(allow_active).verify(
        VerificationRequest(
            "tenant-a",
            (Claim("claim-1", "The retention period is 30 days."),),
            (EvidenceRecord(record, "The retention period is 30 days."),),
        )
    )

    assert result.outcome is VerificationOutcome.SUPPORTED
    assert record.tenant_id == "tenant-a"
    assert record.document_id == "doc-1"
    assert record.version_id == "v-2"
    assert record.source_span.start == 101
    assert record.source_span.end == 140


def test_chat_001_owns_preview_download_reauthorization_recheck():
    assert "citation preview/download" in CHAT_CONTRACT
    assert "recheck authorization" in CHAT_CONTRACT
    assert "citation access" in CHAT_CONTRACT

    result = EvidenceVerifier(allow_active).verify(
        VerificationRequest(
            "tenant-a",
            (Claim("claim-1", "The retention period is 30 days."),),
            (EvidenceRecord(citation(), "The retention period is 30 days."),),
        )
    )
    assert result.claims[0].citation_ids == ("c-1",)
    assert "30 days" not in repr(result)
