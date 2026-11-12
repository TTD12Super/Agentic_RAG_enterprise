"""Direct, fail-closed retrieval-to-answer baseline."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import hashlib
import json
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
from backend.app.knowledge.models import DOCXLocator, PDFLocator, SourceLocator, XLSXLocator
from backend.app.models.policy import DataClassification
from backend.app.orchestration.context import AssembledContext, RetrievedEvidence, build_secure_context

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
    tenant_id: str
    document_id: str
    version_id: str
    policy_epoch: int
    audience: str
    expires_at: datetime
    locator: SourceLocator
    evidence_snapshot_hash: str
    chunk_id: str
    # Optional display metadata is additive; the authorization-bound identity
    # and typed locator remain the source of truth.
    title: str | None = None
    filename: str | None = None
    mime_type: str | None = None
    location: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        for name in ("citation_id", "tenant_id", "document_id", "version_id", "chunk_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.policy_epoch, bool) or not isinstance(self.policy_epoch, int) or self.policy_epoch < 0:
            raise ValueError("policy_epoch must be a non-negative integer")
        if not isinstance(self.audience, str) or not self.audience.strip():
            raise ValueError("audience must be a non-empty string")
        if not isinstance(self.expires_at, datetime) or self.expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        if not _valid_locator(self.locator):
            raise ValueError("citation locator is malformed")
        if len(self.evidence_snapshot_hash) != 64 or any(
            char not in "0123456789abcdef" for char in self.evidence_snapshot_hash
        ):
            raise ValueError("evidence_snapshot_hash must be a lowercase SHA-256 digest")
        for name in ("title", "filename", "mime_type"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string when present")
        if self.location is not None and not isinstance(self.location, Mapping):
            raise ValueError("location must be a mapping when present")

    @property
    def page(self) -> int | None:
        return self.locator.page if isinstance(self.locator, PDFLocator) else None

    @property
    def source_span(self) -> tuple[int, int] | None:
        if not isinstance(self.locator, PDFLocator):
            return None
        return (self.locator.source_span.start, self.locator.source_span.end)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "citation_id": self.citation_id,
            "tenant_id": self.tenant_id,
            "document_id": self.document_id,
            "version_id": self.version_id,
            "policy_epoch": self.policy_epoch,
            "audience": self.audience,
            "expires_at": _utc_z(self.expires_at),
            "locator": self.locator.model_dump(mode="json"),
            "page": self.page,
            "source_span": (
                {"start": self.source_span[0], "end": self.source_span[1]}
                if self.source_span is not None
                else None
            ),
            "evidence_snapshot_hash": self.evidence_snapshot_hash,
            "chunk_id": self.chunk_id,
        }
        for name in ("title", "filename", "mime_type"):
            value = getattr(self, name)
            if value is not None:
                payload[name] = value
        if self.location is not None:
            payload["location"] = dict(self.location)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class AnswerResult:
    status: AnswerStatus
    answer: str = ""
    citations: tuple[AnswerCitation, ...] = ()
    reason_codes: tuple[str, ...] = ()
    verification: VerificationResult | None = None


@dataclass(frozen=True, slots=True)
class PreparedAnswer:
    """Authorized retrieval context shared by batch and streaming answers."""

    status: AnswerStatus
    reason_codes: tuple[str, ...] = ()
    context: AssembledContext | None = None
    evidence_records: Mapping[str, EvidenceRecord] = field(default_factory=dict)
    citation_metadata: Mapping[str, object] = field(default_factory=dict)
    citations: tuple[AnswerCitation, ...] = ()
    guardrail_citations: tuple[GuardrailCitation, ...] = ()


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
        self._citation_expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    def answer(
        self,
        query: str,
        principal: AuthenticatedPrincipal,
        *,
        policy_epoch: int,
    ) -> AnswerResult:
        prepared = self.prepare_context(query, principal, policy_epoch=policy_epoch)
        if prepared.status is not AnswerStatus.ANSWERED or prepared.context is None:
            answer = (
                "Insufficient evidence to answer this question."
                if prepared.status is AnswerStatus.INSUFFICIENT_EVIDENCE
                else ""
            )
            return self._failure(prepared.status, prepared.reason_codes, answer=answer)

        evidence_records = prepared.evidence_records
        citation_metadata = prepared.citation_metadata
        checked_query = normalize_user_input(query)
        try:
            generated = self._model_gateway.generate(
                prepared.context.as_messages(), classification=DataClassification.INTERNAL
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
                _answer_citation(
                    evidence_records[citation_id],
                    citation_metadata[citation_id],
                    default_expires_at=self._citation_expires_at,
                )
                for citation_id in unique_supported_ids
                if citation_id in evidence_records
            ),
            verification=verification,
        )

    def prepare_context(
        self,
        query: str,
        principal: AuthenticatedPrincipal,
        *,
        policy_epoch: int,
    ) -> PreparedAnswer:
        """Run authorized retrieval and build the provider-safe context once."""

        checked_query = normalize_user_input(query)
        if not checked_query.allowed or checked_query.value is None:
            return PreparedAnswer(AnswerStatus.ACCESS_DENIED, checked_query.reason_codes)
        try:
            retrieval = self._retriever.search(
                checked_query.value,
                principal,
                policy_epoch=policy_epoch,
                top_k=self._top_k,
            )
        except Exception:
            return PreparedAnswer(AnswerStatus.ERROR, ("retrieval_failed",))
        if retrieval.status == "ERROR":
            return PreparedAnswer(AnswerStatus.ERROR, ("retrieval_failed",))
        if not retrieval.evidence:
            return PreparedAnswer(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                ("insufficient_evidence",),
            )

        evidence_records, citation_metadata = self._authorized_evidence(
            retrieval.evidence + retrieval.expanded_context,
            principal.tenant_id,
            policy_epoch,
        )
        if not evidence_records:
            return PreparedAnswer(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                ("insufficient_evidence",),
            )

        context_evidence = tuple(
            RetrievedEvidence(
                chunk_id=record.citation.chunk_id or record.citation.citation_id,
                document_id=record.citation.document_id,
                version_id=record.citation.version_id,
                text=record.text,
                page_start=record.citation.page,
                page_end=record.citation.page,
                source_span=(
                    (record.citation.source_span.start, record.citation.source_span.end)
                    if record.citation.source_span is not None
                    else None
                ),
                retrieval_method="hybrid",
            )
            for record in evidence_records.values()
        )
        try:
            context = build_secure_context(checked_query.value, context_evidence)
            citations = tuple(
                _answer_citation(
                    evidence_records[citation_id],
                    citation_metadata[citation_id],
                    default_expires_at=self._citation_expires_at,
                )
                for citation_id in evidence_records
            )
        except Exception:
            return PreparedAnswer(AnswerStatus.ERROR, ("model_failed",))
        guardrail_citations = tuple(
            GuardrailCitation(citation_id, evidence_records[citation_id].text)
            for citation_id in evidence_records
        )
        return PreparedAnswer(
            AnswerStatus.ANSWERED,
            context=context,
            evidence_records=evidence_records,
            citation_metadata=citation_metadata,
            citations=citations,
            guardrail_citations=guardrail_citations,
        )

    def _authorized_evidence(
        self,
        evidence: tuple[HybridEvidence, ...],
        tenant_id: str,
        policy_epoch: int,
    ) -> tuple[dict[str, EvidenceRecord], dict[str, object]]:
        authorized: dict[str, EvidenceRecord] = {}
        metadata: dict[str, object] = {}
        for index, item in enumerate(evidence, 1):
            try:
                source = item.citation
                if (
                    source.tenant_id != tenant_id
                    or source.policy_epoch != policy_epoch
                    or not _valid_locator(source.locator)
                    or _expired(source.expires_at)
                ):
                    continue
                inspected = inspect_untrusted_content(item.text)
                if not inspected.allowed or inspected.value is None:
                    continue
                # EvidenceVerifier still requires a span; the typed locator remains the output authority.
                source_span = source.source_span or VerificationSourceSpan(
                    0, max(1, len(inspected.value))
                )
                citation_id = f"c-{index}"
                citation = CitationRecord(
                    citation_id=citation_id,
                    document_id=source.document_id,
                    version_id=source.version_id,
                    tenant_id=source.tenant_id,
                    page=source.page_start,
                    source_span=VerificationSourceSpan(source_span.start, source_span.end),
                    chunk_id=source.chunk_id,
                )
                decision = self._authorize_citation(citation)
            except Exception:
                continue
            if not _authorization_matches(decision, citation):
                continue
            authorized[citation_id] = EvidenceRecord(citation, inspected.value)
            metadata[citation_id] = item.citation
        return authorized, metadata

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


def _answer_citation(
    evidence: EvidenceRecord,
    metadata: object,
    *,
    default_expires_at: datetime,
) -> AnswerCitation:
    citation = evidence.citation
    if not hasattr(metadata, "locator") or not _valid_locator(metadata.locator):
        raise ValueError("citation locator is malformed")
    return AnswerCitation(
        citation_id=citation.citation_id,
        tenant_id=citation.tenant_id,
        document_id=citation.document_id,
        version_id=citation.version_id,
        policy_epoch=metadata.policy_epoch,
        audience=getattr(metadata, "audience", "answer-client"),
        expires_at=(
            metadata.expires_at
            if getattr(metadata, "expires_at", None) is not None
            else default_expires_at
        ),
        locator=metadata.locator,
        evidence_snapshot_hash=hashlib.sha256(evidence.text.encode("utf-8")).hexdigest(),
        chunk_id=citation.chunk_id or citation.citation_id,
    )


def _valid_locator(locator: object) -> bool:
    return isinstance(locator, (PDFLocator, DOCXLocator, XLSXLocator))


def _expired(value: object) -> bool:
    return isinstance(value, datetime) and value.tzinfo is not None and value <= datetime.now(timezone.utc)


def _utc_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


__all__ = [
    "AnswerCitation",
    "AnswerModelGateway",
    "AnswerResult",
    "PreparedAnswer",
    "AnswerStatus",
    "DirectAnswerPipeline",
    "GeneratedAnswer",
]
