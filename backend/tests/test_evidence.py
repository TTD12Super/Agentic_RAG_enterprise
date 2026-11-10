from dataclasses import FrozenInstanceError

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
    version_id: str = "v-2",
) -> CitationRecord:
    return CitationRecord(
        citation_id=citation_id,
        document_id="doc-1",
        version_id=version_id,
        tenant_id=tenant_id,
        source_span=SourceSpan(10, 30),
        page=2,
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


def verify(claims, evidence, authorize=allow_active):
    return EvidenceVerifier(authorize).verify(
        VerificationRequest("tenant-a", tuple(claims), tuple(evidence))
    )


def test_supported_claim_returns_immutable_citation_metadata_only():
    evidence = EvidenceRecord(citation(), "The retention period is 30 days.")

    result = verify([Claim("claim-1", "The retention period is 30 days.")], [evidence])

    assert result.outcome is VerificationOutcome.SUPPORTED
    assert result.claims[0].citation_ids == ("c-1",)
    assert "30 days" not in repr(result.claims[0])
    assert evidence.citation.source_span == SourceSpan(10, 30)


def test_citation_and_source_span_are_immutable():
    record = citation()

    try:
        record.source_span.start = 11
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("source span must be immutable")

    try:
        record.version_id = "v-3"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("citation must be immutable")


def test_unsupported_claim_does_not_use_lexically_unrelated_evidence():
    evidence = EvidenceRecord(citation(), "The office is open on weekdays.")

    result = verify([Claim("claim-1", "The retention period is 30 days.")], [evidence])

    assert result.outcome is VerificationOutcome.UNSUPPORTED
    assert result.claims[0].outcome is VerificationOutcome.UNSUPPORTED
    assert result.claims[0].citation_ids == ()


def test_conflicting_numeric_source_spans_are_disclosed():
    first = EvidenceRecord(citation("c-1"), "The retention period is 30 days.")
    second = EvidenceRecord(citation("c-2"), "The retention period is 90 days.")

    result = verify([Claim("claim-1", "The retention period is 30 days.")], [first, second])

    assert result.outcome is VerificationOutcome.CONFLICTING
    assert result.claims[0].citation_ids == ("c-1", "c-2")


def test_stale_version_is_denied_even_when_text_matches():
    stale = EvidenceRecord(citation(version_id="v-1"), "The retention period is 30 days.")

    def current_v2(record: CitationRecord) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=True,
            tenant_id=record.tenant_id,
            document_id=record.document_id,
            version_id=record.version_id,
            current_version_id="v-2",
            status="ACTIVE",
        )

    result = verify(
        [Claim("claim-1", "The retention period is 30 days.")], [stale], current_v2
    )

    assert result.outcome is VerificationOutcome.ACCESS_DENIED
    assert result.claims[0].citation_ids == ()


def test_authorizer_must_attest_active_current_and_not_revoked():
    def revoked(record: CitationRecord) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=True,
            tenant_id=record.tenant_id,
            document_id=record.document_id,
            version_id=record.version_id,
            current_version_id=record.version_id,
            status="ACTIVE",
            revoked=True,
        )

    result = verify(
        [Claim("claim-1", "The retention period is 30 days.")],
        [EvidenceRecord(citation(), "The retention period is 30 days.")],
        revoked,
    )

    assert result.outcome is VerificationOutcome.ACCESS_DENIED


def test_tenant_mismatch_fails_closed_without_calling_pep():
    called = False

    def unexpected(record: CitationRecord) -> AuthorizationDecision:
        nonlocal called
        called = True
        return allow_active(record)

    result = verify(
        [Claim("claim-1", "The retention period is 30 days.")],
        [EvidenceRecord(citation(tenant_id="tenant-b"), "The retention period is 30 days.")],
        unexpected,
    )

    assert result.outcome is VerificationOutcome.ACCESS_DENIED
    assert called is False


def test_denial_result_does_not_leak_source_text():
    secret = "Confidential merger target Acme Delta"
    result = verify(
        [Claim("claim-1", "The merger target is Acme Delta.")],
        [EvidenceRecord(citation(), secret)],
        lambda record: AuthorizationDecision(allowed=False),
    )

    assert result.outcome is VerificationOutcome.ACCESS_DENIED
    assert secret not in repr(result)
    assert result.claims[0].citation_ids == ()
