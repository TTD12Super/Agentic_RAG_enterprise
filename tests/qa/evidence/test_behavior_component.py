from dataclasses import FrozenInstanceError

import pytest

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


def citation(
    citation_id: str = "c-1",
    *,
    tenant_id: str = "tenant-a",
    document_id: str = "doc-1",
    version_id: str = "v-2",
) -> CitationRecord:
    return CitationRecord(
        citation_id=citation_id,
        document_id=document_id,
        version_id=version_id,
        tenant_id=tenant_id,
        source_span=SourceSpan(10, 30),
        page=2,
        chunk_id="chunk-1",
    )


def allow_active(record: CitationRecord) -> AuthorizationDecision:
    return AuthorizationDecision(
        allowed=True,
        tenant_id=record.tenant_id,
        document_id=record.document_id,
        version_id=record.version_id,
        current_version_id=record.version_id,
        status="ACTIVE",
    )


def verify(claims, evidence, authorize=allow_active, tenant_id="tenant-a"):
    return EvidenceVerifier(authorize).verify(
        VerificationRequest(tenant_id, tuple(claims), tuple(evidence))
    )


def test_source_span_and_citation_metadata_are_immutable():
    record = citation()

    with pytest.raises(FrozenInstanceError):
        record.source_span.start = 11
    with pytest.raises(FrozenInstanceError):
        record.version_id = "v-3"

    assert record.source_span == SourceSpan(10, 30)
    assert record.chunk_id == "chunk-1"


def test_source_span_rejects_non_positive_half_open_ranges():
    with pytest.raises(ValueError):
        SourceSpan(4, 4)
    with pytest.raises(ValueError):
        SourceSpan(-1, 4)
    with pytest.raises(ValueError):
        SourceSpan(True, 4)


def test_supported_claim_preserves_citation_provenance():
    record = citation()
    result = verify(
        [Claim("claim-1", "The retention period is 30 days.")],
        [EvidenceRecord(record, "The retention period is 30 days.")],
    )

    assert result.outcome is VerificationOutcome.SUPPORTED
    assert result.claims[0].citation_ids == ("c-1",)
    assert record.tenant_id == "tenant-a"
    assert record.document_id == "doc-1"
    assert record.version_id == "v-2"
    assert record.source_span == SourceSpan(10, 30)


def test_unrelated_evidence_produces_unsupported_claim():
    result = verify(
        [Claim("claim-1", "The retention period is 30 days.")],
        [EvidenceRecord(citation(), "The office is open on weekdays.")],
    )

    assert result.outcome is VerificationOutcome.UNSUPPORTED
    assert result.claims[0].outcome is VerificationOutcome.UNSUPPORTED
    assert result.claims[0].citation_ids == ()
    assert result.claims[0].reason_code == "INSUFFICIENT_EVIDENCE"


def test_supported_and_unsupported_claims_produce_partial_outcome():
    evidence = EvidenceRecord(citation(), "The retention period is 30 days.")
    result = verify(
        [
            Claim("supported", "The retention period is 30 days."),
            Claim("missing", "The escalation window is 4 hours."),
        ],
        [evidence],
    )

    assert result.outcome is VerificationOutcome.PARTIAL
    assert result.claims[0].outcome is VerificationOutcome.SUPPORTED
    assert result.claims[1].outcome is VerificationOutcome.UNSUPPORTED


def test_numeric_mismatch_is_conflicting_not_supported():
    result = verify(
        [Claim("claim-1", "The retention period is 30 days.")],
        [EvidenceRecord(citation(), "The retention period is 90 days.")],
    )

    assert result.outcome is VerificationOutcome.CONFLICTING
    assert result.claims[0].outcome is VerificationOutcome.CONFLICTING
    assert result.claims[0].reason_code == "CONFLICTING_EVIDENCE"


def test_negation_mismatch_is_conflicting_not_supported():
    result = verify(
        [Claim("claim-1", "The report is approved.")],
        [EvidenceRecord(citation(), "The report is not approved.")],
    )

    assert result.outcome is VerificationOutcome.CONFLICTING
    assert result.claims[0].outcome is VerificationOutcome.CONFLICTING


def test_current_active_version_is_required_by_authorization_attestation():
    def stale_current(record: CitationRecord) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=True,
            tenant_id=record.tenant_id,
            document_id=record.document_id,
            version_id=record.version_id,
            current_version_id="v-3",
            status="ACTIVE",
        )

    result = verify(
        [Claim("claim-1", "The retention period is 30 days.")],
        [EvidenceRecord(citation(), "The retention period is 30 days.")],
        stale_current,
    )

    assert result.outcome is VerificationOutcome.ACCESS_DENIED
    assert result.claims[0].citation_ids == ()


def test_authorization_callback_error_fails_closed():
    def broken(_: CitationRecord) -> AuthorizationDecision:
        raise RuntimeError("policy store unavailable")

    result = verify(
        [Claim("claim-1", "The retention period is 30 days.")],
        [EvidenceRecord(citation(), "The retention period is 30 days.")],
        broken,
    )

    assert result.outcome is VerificationOutcome.ACCESS_DENIED
    assert result.claims[0].reason_code == "ACCESS_DENIED"


def test_repeated_verification_is_deterministic():
    claims = [Claim("claim-1", "The retention period is 30 days.")]
    evidence = [EvidenceRecord(citation(), "The retention period is 30 days.")]

    first = verify(claims, evidence)
    second = verify(claims, evidence)

    assert first == second
