"""Small, provider-neutral checks for grounded claims and citations."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Callable, Iterable, Mapping, Sequence


class VerificationOutcome(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONFLICTING = "CONFLICTING"
    PARTIAL = "PARTIAL"
    ACCESS_DENIED = "ACCESS_DENIED"


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """A half-open source range, measured in the source representation's units."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if isinstance(self.start, bool) or not isinstance(self.start, int) or self.start < 0:
            raise ValueError("source span start must be a non-negative integer")
        if isinstance(self.end, bool) or not isinstance(self.end, int) or self.end <= self.start:
            raise ValueError("source span end must be greater than start")


@dataclass(frozen=True, slots=True)
class CitationRecord:
    citation_id: str
    document_id: str
    version_id: str
    tenant_id: str
    source_span: SourceSpan
    page: int | None = None
    chunk_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("citation_id", "document_id", "version_id", "tenant_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_span, SourceSpan):
            raise ValueError("source_span must be a SourceSpan")
        if self.page is not None and (
            isinstance(self.page, bool) or not isinstance(self.page, int) or self.page < 1
        ):
            raise ValueError("page must be a positive integer")


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    citation: CitationRecord
    text: str = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("evidence text must be a non-empty string")


@dataclass(frozen=True, slots=True)
class Claim:
    claim_id: str
    text: str
    citation_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.claim_id, str) or not self.claim_id.strip():
            raise ValueError("claim_id must be a non-empty string")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("claim text must be a non-empty string")
        object.__setattr__(self, "citation_ids", tuple(self.citation_ids))


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """The safe, authoritative attestation returned by a citation PEP."""

    allowed: bool
    tenant_id: str | None = None
    document_id: str | None = None
    version_id: str | None = None
    current_version_id: str | None = None
    status: str | None = None
    revoked: bool = False


@dataclass(frozen=True, slots=True)
class VerificationRequest:
    tenant_id: str
    claims: tuple[Claim, ...]
    evidence: tuple[EvidenceRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_id, str) or not self.tenant_id.strip():
            raise ValueError("tenant_id must be a non-empty string")
        object.__setattr__(self, "claims", tuple(self.claims))
        object.__setattr__(self, "evidence", tuple(self.evidence))


@dataclass(frozen=True, slots=True)
class ClaimVerification:
    claim_id: str
    outcome: VerificationOutcome
    citation_ids: tuple[str, ...] = ()
    reason_code: str | None = None


@dataclass(frozen=True, slots=True)
class VerificationResult:
    outcome: VerificationOutcome
    claims: tuple[ClaimVerification, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "claims", tuple(self.claims))


AuthorizationCallback = Callable[[CitationRecord], AuthorizationDecision]

_TOKEN = re.compile(r"\w+", re.UNICODE)
_LEXICAL_SUPPORT_THRESHOLD = 0.8
_STOP_WORDS = frozenset(
    "a an and are as at be been being by can could do does did for from had has have he her here his how i if in into is it its may me my of on or our she should that the their them then there these they this those to was we were what when where which who why will with would you your".split()
)
_NEGATIONS = frozenset(
    "cannot can't denied disallowed forbidden never no not prohibited without".split()
)


def _terms(text: str) -> set[str]:
    return {token for token in _TOKEN.findall(text.casefold()) if token not in _STOP_WORDS}


def _is_negative(terms: set[str]) -> bool:
    return bool(terms & _NEGATIONS)


def _numeric_terms(terms: set[str]) -> set[str]:
    return {term for term in terms if any(character.isdigit() for character in term)}


def _numeric_conflict(claim_terms: set[str], evidence_terms: set[str]) -> bool:
    claim_values = _numeric_terms(claim_terms)
    evidence_values = _numeric_terms(evidence_terms)
    if not claim_values or not evidence_values or claim_values & evidence_values:
        return False
    claim_anchors = claim_terms - claim_values - _NEGATIONS
    evidence_anchors = evidence_terms - evidence_values - _NEGATIONS
    if not claim_anchors:
        return False
    return (
        len(claim_anchors & evidence_anchors) / len(claim_anchors)
        >= _LEXICAL_SUPPORT_THRESHOLD
    )


def _relation(claim_text: str, evidence_text: str) -> str | None:
    claim_terms = _terms(claim_text)
    evidence_terms = _terms(evidence_text)
    if not claim_terms:
        return None
    overlap = len(claim_terms & evidence_terms) / len(claim_terms)
    if overlap < _LEXICAL_SUPPORT_THRESHOLD and not _numeric_conflict(
        claim_terms, evidence_terms
    ):
        return None
    if _is_negative(claim_terms) != _is_negative(evidence_terms):
        # shortcut: lexical contradiction only, upgrade to domain-aware entailment before production claims.
        return "conflict"
    if _numeric_conflict(claim_terms, evidence_terms):
        return "conflict"
    return "support"


class EvidenceVerifier:
    """Verify claims using only evidence authorized by the supplied PEP callback."""

    def __init__(self, authorize: AuthorizationCallback) -> None:
        self._authorize = authorize

    def verify(self, request: VerificationRequest) -> VerificationResult:
        evidence_by_id: dict[str, EvidenceRecord] = {}
        for evidence in request.evidence:
            if (
                not isinstance(evidence, EvidenceRecord)
                or evidence.citation.citation_id in evidence_by_id
            ):
                return self._malformed_result(request.claims)
            evidence_by_id[evidence.citation.citation_id] = evidence

        allowed: dict[str, bool] = {
            citation_id: self._is_authorized(request.tenant_id, evidence.citation)
            for citation_id, evidence in evidence_by_id.items()
        }
        results = tuple(
            self._verify_claim(claim, evidence_by_id, allowed) for claim in request.claims
        )
        return VerificationResult(self._overall_outcome(results), results)

    def _is_authorized(self, tenant_id: str, citation: CitationRecord) -> bool:
        if citation.tenant_id != tenant_id:
            return False
        try:
            decision = self._authorize(citation)
        except Exception:
            return False
        return (
            isinstance(decision, AuthorizationDecision)
            and decision.allowed
            and decision.tenant_id == citation.tenant_id
            and decision.document_id == citation.document_id
            and decision.version_id == citation.version_id
            and decision.current_version_id == citation.version_id
            and decision.status == "ACTIVE"
            and not decision.revoked
        )

    @staticmethod
    def _verify_claim(
        claim: Claim,
        evidence_by_id: Mapping[str, EvidenceRecord],
        allowed: Mapping[str, bool],
    ) -> ClaimVerification:
        if claim.citation_ids:
            candidate_ids = [
                citation_id for citation_id in claim.citation_ids if citation_id in evidence_by_id
            ]
        else:
            candidate_ids = list(evidence_by_id)

        considered = [citation_id for citation_id in candidate_ids if allowed.get(citation_id, False)]
        denied = bool(candidate_ids) and not considered
        supported: list[str] = []
        conflicting: list[str] = []
        for citation_id in considered:
            relation = _relation(claim.text, evidence_by_id[citation_id].text)
            if relation == "support":
                supported.append(citation_id)
            elif relation == "conflict":
                conflicting.append(citation_id)

        if supported and conflicting:
            return ClaimVerification(
                claim.claim_id,
                VerificationOutcome.CONFLICTING,
                tuple(supported + conflicting),
                "CONFLICTING_EVIDENCE",
            )
        if conflicting:
            return ClaimVerification(
                claim.claim_id,
                VerificationOutcome.CONFLICTING,
                tuple(conflicting),
                "CONFLICTING_EVIDENCE",
            )
        if supported:
            return ClaimVerification(
                claim.claim_id, VerificationOutcome.SUPPORTED, tuple(supported), "LEXICAL_SUPPORT"
            )
        if denied:
            return ClaimVerification(
                claim.claim_id, VerificationOutcome.ACCESS_DENIED, reason_code="ACCESS_DENIED"
            )
        return ClaimVerification(
            claim.claim_id, VerificationOutcome.UNSUPPORTED, reason_code="INSUFFICIENT_EVIDENCE"
        )

    @staticmethod
    def _overall_outcome(results: Sequence[ClaimVerification]) -> VerificationOutcome:
        outcomes = [result.outcome for result in results]
        if not outcomes:
            return VerificationOutcome.UNSUPPORTED
        if VerificationOutcome.CONFLICTING in outcomes:
            return VerificationOutcome.CONFLICTING
        if all(outcome is VerificationOutcome.ACCESS_DENIED for outcome in outcomes):
            return VerificationOutcome.ACCESS_DENIED
        if all(outcome is VerificationOutcome.SUPPORTED for outcome in outcomes):
            return VerificationOutcome.SUPPORTED
        if any(outcome is VerificationOutcome.SUPPORTED for outcome in outcomes):
            return VerificationOutcome.PARTIAL
        return VerificationOutcome.UNSUPPORTED

    @staticmethod
    def _malformed_result(claims: Sequence[Claim]) -> VerificationResult:
        results = tuple(
            ClaimVerification(
                claim.claim_id,
                VerificationOutcome.ACCESS_DENIED,
                reason_code="MALFORMED_EVIDENCE",
            )
            for claim in claims
        )
        return VerificationResult(VerificationOutcome.ACCESS_DENIED, results)
