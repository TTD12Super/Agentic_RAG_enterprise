"""Direct, fail-closed retrieval-to-answer baseline."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
import hashlib
from typing import Protocol

from backend.app.evidence import (
    AuthorizationDecision,
    Claim,
    CitationRecord,
    EvidenceRecord,
    EvidenceVerifier,
    SourceSpan as VerificationSourceSpan,
    VerificationOutcome,
    VerificationRequest,
    VerificationResult,
)
from backend.app.guardrails import (
    Citation as GuardrailCitation,
    inspect_untrusted_content,
    normalize_user_input,
    validate_output,
)
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.models.policy import DataClassification
from backend.app.orchestration.context import RetrievedEvidence, build_secure_context

from .hybrid import HybridEvidence, HybridRetriever


class AnswerStatus(StrEnum):
    ANSWERED = "ANSWERED"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    ACCESS_DENIED = "ACCESS_DENIED"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    """Structured answer returned by an answer-capable model gateway."""

    answer: str
    claims: tuple[Claim, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.answer, str):
            raise TypeError("answer must be a string")
        object.__setattr__(self, "claims", tuple(self.claims))


class AnswerModelGateway(Protocol):
    """The smallest answer-generation surface needed by this pipeline."""

    def generate(
        self,
        messages: tuple[Mapping[str, str], ...],
        *,
        classification: DataClassification,
    ) -> GeneratedAnswer: ...


@dataclass(frozen=True, slots=True)
class AnswerCitation:
    citation_id: str
    document_id: str
    version_id: str
    page: int | None
    source_span: tuple[int, int]
    evidence_snapshot_hash: str
    chunk_id: str


@dataclass(frozen=True, slots=True)
class AnswerResult:
    status: AnswerStatus
    answer: str = ""
    citations: tuple[AnswerCitation, ...] = ()
    reason_codes: tuple[str, ...] = ()
    verification: VerificationResult | None = None


AuthorizationCallback = Callable[[CitationRecord], AuthorizationDecision]


class DirectAnswerPipeline:
    """Run one authorized hybrid retrieval and one grounded answer attempt."""

    def __init__(
        self,
        *,
        retriever: HybridRetriever,
        model_gateway: AnswerModelGateway,
        authorize_citation: AuthorizationCallback,
        top_k: int = 8,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        self._retriever = retriever
        self._model_gateway = model_gateway
        self._authorize_citation = authorize_citation
        self._verifier = EvidenceVerifier(authorize_citation)
        self._top_k = top_k

    def answer(
        self,
        query: str,
        principal: AuthenticatedPrincipal,
        *,
        policy_epoch: int,
    ) -> AnswerResult:
        checked_query = normalize_user_input(query)
        if not checked_query.allowed or checked_query.value is None:
            return self._failure(AnswerStatus.ACCESS_DENIED, checked_query.reason_codes)

        try:
            retrieval = self._retriever.search(
                checked_query.value,
                principal,
                policy_epoch=policy_epoch,
                top_k=self._top_k,
            )
        except Exception:
            return self._failure(AnswerStatus.ERROR, ("retrieval_failed",))
        if retrieval.status == "ERROR":
            return self._failure(AnswerStatus.ERROR, ("retrieval_failed",))
        if not retrieval.evidence:
            return self._failure(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                ("insufficient_evidence",),
                answer="Insufficient evidence to answer this question.",
            )

        evidence_records = self._authorized_evidence(retrieval.evidence, principal.tenant_id)
        if not evidence_records:
            return self._failure(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                ("insufficient_evidence",),
                answer="Insufficient evidence to answer this question.",
            )

        context_evidence = tuple(
            RetrievedEvidence(
                chunk_id=record.citation.chunk_id or record.citation.citation_id,
                document_id=record.citation.document_id,
                version_id=record.citation.version_id,
                text=record.text,
                page_start=record.citation.page,
                page_end=record.citation.page,
                source_span=(record.citation.source_span.start, record.citation.source_span.end),
                retrieval_method="hybrid",
            )
            for record in evidence_records.values()
        )
        try:
            context = build_secure_context(checked_query.value, context_evidence)
            generated = self._model_gateway.generate(
                context.as_messages(), classification=DataClassification.INTERNAL
            )
            if not isinstance(generated, GeneratedAnswer):
                return self._failure(AnswerStatus.ERROR, ("invalid_model_response",))
        except Exception:
            return self._failure(AnswerStatus.ERROR, ("model_failed",))

        try:
            verification = self._verifier.verify(
                VerificationRequest(
                    tenant_id=principal.tenant_id,
                    claims=generated.claims,
                    evidence=tuple(evidence_records.values()),
                )
            )
        except Exception:
            return self._failure(AnswerStatus.ERROR, ("evidence_verification_failed",))

        supported_ids = tuple(
            citation_id
            for result in verification.claims
            if result.outcome is VerificationOutcome.SUPPORTED
            for citation_id in result.citation_ids
        )
        unique_supported_ids = tuple(dict.fromkeys(supported_ids))
        if verification.outcome is VerificationOutcome.ACCESS_DENIED:
            return self._failure(AnswerStatus.ACCESS_DENIED, ("citation_access_denied",))
        if verification.outcome is VerificationOutcome.CONFLICTING:
            return self._failure(AnswerStatus.ERROR, ("conflicting_evidence",))
        if verification.outcome is VerificationOutcome.UNSUPPORTED:
            return self._failure(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                ("insufficient_evidence",),
                answer="Insufficient evidence to answer this question.",
                verification=verification,
            )

        citations = tuple(
            GuardrailCitation(citation_id, evidence_records[citation_id].text)
            for citation_id in unique_supported_ids
            if citation_id in evidence_records
        )
        checked_output = validate_output(generated.answer, citations)
        if not checked_output.allowed or checked_output.value is None:
            return self._failure(AnswerStatus.ERROR, checked_output.reason_codes)

        status = (
            AnswerStatus.ANSWERED
            if verification.outcome is VerificationOutcome.SUPPORTED
            else AnswerStatus.PARTIAL
        )
        return AnswerResult(
            status=status,
            answer=checked_output.value,
            citations=tuple(
                _answer_citation(evidence_records[citation_id])
                for citation_id in unique_supported_ids
                if citation_id in evidence_records
            ),
            verification=verification,
        )

    def _authorized_evidence(
        self,
        evidence: tuple[HybridEvidence, ...],
        tenant_id: str,
    ) -> dict[str, EvidenceRecord]:
        authorized: dict[str, EvidenceRecord] = {}
        for index, item in enumerate(evidence, 1):
            inspected = inspect_untrusted_content(item.text)
            if not inspected.allowed or inspected.value is None:
                continue
            source_span = item.citation.source_span
            if source_span is None:
                continue
            citation_id = f"c-{index}"
            citation = CitationRecord(
                citation_id=citation_id,
                document_id=item.citation.document_id,
                version_id=item.citation.version_id,
                tenant_id=tenant_id,
                page=item.citation.page_start,
                source_span=VerificationSourceSpan(source_span.start, source_span.end),
                chunk_id=item.citation.chunk_id,
            )
            try:
                decision = self._authorize_citation(citation)
            except Exception:
                continue
            if not _authorization_matches(decision, citation):
                continue
            authorized[citation_id] = EvidenceRecord(citation, inspected.value)
        return authorized

    @staticmethod
    def _failure(
        status: AnswerStatus,
        reason_codes: tuple[str, ...],
        *,
        answer: str = "",
        verification: VerificationResult | None = None,
    ) -> AnswerResult:
        return AnswerResult(
            status=status,
            answer=answer,
            reason_codes=tuple(reason_codes),
            verification=verification,
        )


def _authorization_matches(
    decision: AuthorizationDecision,
    citation: CitationRecord,
) -> bool:
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


def _answer_citation(evidence: EvidenceRecord) -> AnswerCitation:
    citation = evidence.citation
    return AnswerCitation(
        citation_id=citation.citation_id,
        document_id=citation.document_id,
        version_id=citation.version_id,
        page=citation.page,
        source_span=(citation.source_span.start, citation.source_span.end),
        evidence_snapshot_hash=hashlib.sha256(evidence.text.encode("utf-8")).hexdigest(),
        chunk_id=citation.chunk_id or citation.citation_id,
    )


__all__ = [
    "AnswerCitation",
    "AnswerModelGateway",
    "AnswerResult",
    "AnswerStatus",
    "DirectAnswerPipeline",
    "GeneratedAnswer",
]
