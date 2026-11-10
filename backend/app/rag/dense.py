"""Permission-aware dense retrieval with a deterministic local index double."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import re
from typing import Mapping
from uuid import UUID

from ..authorization.policy import Action, DocumentResource, PolicyEnforcementPoint
from ..identity.models import AuthenticatedPrincipal
from ..ingestion.lifecycle import IngestionService
from ..knowledge.models import ChunkMetadata, SourceSpan
from ..integrations.model_gateway import ModelGateway
from ..models.adapters import EmbeddingRequest, EmbeddingResult
from ..models.policy import DataClassification, ModelRoute


_TOKEN = re.compile(r"[\w]+", re.UNICODE)
_DIMENSIONS = 32


class DeterministicEmbeddingAdapter:
    """Small local embedding test double; it has no provider or network dependency."""

    def embed(
        self,
        request: EmbeddingRequest,
        *,
        route: ModelRoute,
        timeout_seconds: float,
    ) -> EmbeddingResult:
        del timeout_seconds
        return EmbeddingResult(
            vectors=tuple(_vectorize(text) for text in request.texts),
            route=route,
        )


@dataclass(frozen=True, slots=True)
class Citation:
    chunk_id: str
    document_id: str
    version_id: str
    page_start: int | None
    page_end: int | None
    source_span: SourceSpan | None


@dataclass(frozen=True, slots=True)
class DenseEvidence:
    citation: Citation
    score: float
    text: str


@dataclass(frozen=True, slots=True)
class DenseRetrievalResult:
    evidence: tuple[DenseEvidence, ...]
    status: str


@dataclass(frozen=True, slots=True)
class SourceFetchResult:
    content: str | None
    citation: Citation | None
    redacted: bool


@dataclass(frozen=True, slots=True)
class _VectorRecord:
    chunk: ChunkMetadata
    text: str
    vector: tuple[float, ...]


class InMemoryDenseVectorIndex:
    """Deterministic vector adapter used by the baseline and its tests."""

    def __init__(self, model_gateway: ModelGateway) -> None:
        self._model_gateway = model_gateway
        self._records: dict[UUID, _VectorRecord] = {}

    def upsert(
        self,
        chunk: ChunkMetadata,
        text: str,
        *,
        classification: DataClassification,
    ) -> None:
        if not text.strip():
            raise ValueError("indexed text must not be empty")
        result = self._model_gateway.embed((text,), classification=classification)
        self._records[chunk.chunk_id] = _VectorRecord(chunk, text, result.vectors[0])

    def _records_for_retrieval(self) -> tuple[_VectorRecord, ...]:
        return tuple(self._records.values())

    def _record(self, chunk_id: UUID) -> _VectorRecord | None:
        return self._records.get(chunk_id)


class DenseRetriever:
    """Dense-only retrieval with policy and lifecycle checks at every boundary."""

    def __init__(
        self,
        *,
        index: InMemoryDenseVectorIndex,
        ingestion: IngestionService,
        pep: PolicyEnforcementPoint,
        documents: Mapping[str, DocumentResource],
        model_gateway: ModelGateway,
    ) -> None:
        self._index = index
        self._ingestion = ingestion
        self._pep = pep
        self._documents = documents
        self._model_gateway = model_gateway

    def search(
        self,
        query: str,
        principal: AuthenticatedPrincipal,
        *,
        policy_epoch: int,
        top_k: int = 8,
    ) -> DenseRetrievalResult:
        if not query.strip():
            raise ValueError("query must not be empty")
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        try:
            query_vector = self._model_gateway.embed(
                (query,),
                # Query text can contain enterprise data; use the stricter route.
                classification=DataClassification.INTERNAL,
            ).vectors[0]
        except Exception:
            return DenseRetrievalResult((), "INSUFFICIENT_EVIDENCE")

        ranked: list[DenseEvidence] = []
        for record in self._index._records_for_retrieval():
            if not self._authorized(record, principal, policy_epoch, Action.DOCUMENT_READ.value):
                continue
            ranked.append(
                DenseEvidence(
                    citation=_citation(record.chunk),
                    score=_cosine(query_vector, record.vector),
                    text=record.text,
                )
            )

        ranked.sort(key=lambda item: (-item.score, item.citation.chunk_id))
        evidence = tuple(ranked[:top_k])
        return DenseRetrievalResult(evidence, "OK" if evidence else "INSUFFICIENT_EVIDENCE")

    def fetch_source(
        self,
        chunk_id: UUID | str,
        principal: AuthenticatedPrincipal,
        *,
        policy_epoch: int,
    ) -> SourceFetchResult:
        try:
            parsed_chunk_id = chunk_id if isinstance(chunk_id, UUID) else UUID(str(chunk_id))
        except (TypeError, ValueError):
            return SourceFetchResult(None, None, True)

        record = self._index._record(parsed_chunk_id)
        if record is None or not self._authorized(
            record, principal, policy_epoch, Action.DOCUMENT_READ.value
        ):
            return SourceFetchResult(None, None, True)
        if not self._authorized(record, principal, policy_epoch, Action.SOURCE_DOWNLOAD.value):
            return SourceFetchResult(None, None, True)
        return SourceFetchResult(record.text, _citation(record.chunk), False)

    def _authorized(
        self,
        record: _VectorRecord,
        principal: AuthenticatedPrincipal,
        policy_epoch: int,
        action: str,
    ) -> bool:
        chunk = record.chunk
        if chunk.tenant_id != _uuid(principal.tenant_id) or chunk.index_state != "ACTIVE":
            return False

        resource = self._documents.get(str(chunk.document_id))
        if resource is None or resource.tenant_id != principal.tenant_id:
            return False
        if (
            resource.document_id != str(chunk.document_id)
            or resource.status != "ACTIVE"
            or resource.current_version_id != str(chunk.version_id)
            or resource.version_id != str(chunk.version_id)
            or resource.version_status != "ACTIVE"
        ):
            return False

        try:
            active_chunks = self._ingestion.retrievable_chunks(
                chunk.document_id,
                chunk.tenant_id,
            )
        except Exception:
            return False
        if not any(active.chunk_id == chunk.chunk_id for active in active_chunks):
            return False

        try:
            return self._pep.check(
                principal,
                action,
                resource,
                tenant_id=principal.tenant_id,
                policy_epoch=policy_epoch,
            ).allowed
        except Exception:
            return False


def _uuid(value: str) -> UUID | None:
    try:
        return UUID(value)
    except (TypeError, ValueError):
        return None


def _citation(chunk: ChunkMetadata) -> Citation:
    return Citation(
        chunk_id=str(chunk.chunk_id),
        document_id=str(chunk.document_id),
        version_id=str(chunk.version_id),
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        source_span=chunk.source_span,
    )


def _vectorize(text: str) -> tuple[float, ...]:
    vector = [0.0] * _DIMENSIONS
    for token in _TOKEN.findall(text.casefold()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        vector[int.from_bytes(digest[:2], "big") % _DIMENSIONS] += 1.0
    magnitude = math.sqrt(sum(value * value for value in vector))
    return tuple(value / magnitude for value in vector) if magnitude else tuple(vector)


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        return -1.0
    return sum(a * b for a, b in zip(left, right, strict=True))


__all__ = [
    "Citation",
    "DenseEvidence",
    "DenseRetriever",
    "DenseRetrievalResult",
    "DeterministicEmbeddingAdapter",
    "InMemoryDenseVectorIndex",
    "SourceFetchResult",
]
