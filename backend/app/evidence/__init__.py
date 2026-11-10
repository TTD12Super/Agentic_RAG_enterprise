"""Provider-neutral evidence and citation verification."""

from .verifier import (
    AuthorizationDecision,
    Claim,
    ClaimVerification,
    CitationRecord,
    EvidenceRecord,
    EvidenceVerifier,
    SourceSpan,
    VerificationOutcome,
    VerificationRequest,
    VerificationResult,
)

__all__ = [
    "AuthorizationDecision",
    "Claim",
    "ClaimVerification",
    "CitationRecord",
    "EvidenceRecord",
    "EvidenceVerifier",
    "SourceSpan",
    "VerificationOutcome",
    "VerificationRequest",
    "VerificationResult",
]
