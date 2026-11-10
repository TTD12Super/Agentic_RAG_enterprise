"""Deterministic, permission-aware hybrid retrieval for local evaluation."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re
from typing import Mapping, Sequence
from uuid import UUID

from ..identity.models import AuthenticatedPrincipal
from ..integrations.model_gateway import ModelGateway
from ..knowledge.models import ChunkMetadata, DOCXLocator, PDFLocator, XLSXLocator
from ..models.adapters import RankedDocument, RerankerRequest, RerankerResult
from ..models.policy import DataClassification, ModelRoute
from .dense import Citation, DenseRetriever, SourceFetchResult
from .parent_child import ChildEvidence, expand_parent_context


_TOKEN = re.compile(r"[\w]+", re.UNICODE)


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(_TOKEN.findall(text.casefold()))


@dataclass(frozen=True, slots=True)
class _BM25Record:
    chunk: ChunkMetadata
    text: str
    tokens: tuple[str, ...]


class InMemoryBM25Index:
    """Small local BM25 index double; records contain no external state."""

    def __init__(self, *, k1: float = 1.5, b: float = 0.75) -> None:
        if k1 < 0 or not 0 <= b <= 1:
            raise ValueError("BM25 parameters must satisfy k1 >= 0 and 0 <= b <= 1")
        self.k1 = k1
        self.b = b
        self._records: dict[UUID, _BM25Record] = {}

    def upsert(self, chunk: ChunkMetadata, text: str) -> None:
        if not text.strip():
            raise ValueError("indexed text must not be empty")
        self._records[chunk.chunk_id] = _BM25Record(chunk, text, _tokens(text))

    def _records_for_retrieval(self) -> tuple[_BM25Record, ...]:
        return tuple(self._records.values())


@dataclass(frozen=True, slots=True)
class HybridRetrievalConfig:
    branch_top_k: int = 20
    rrf_k: int = 60
    rerank_top_k: int = 20

    def __post_init__(self) -> None:
        if self.branch_top_k <= 0 or self.rerank_top_k <= 0 or self.rrf_k < 0:
            raise ValueError("retrieval limits must be positive and rrf_k must be non-negative")


@dataclass(frozen=True, slots=True)
class HybridEvidence:
    citation: Citation
    score: float
    text: str
    rrf_score: float
    rerank_score: float


@dataclass(frozen=True, slots=True)
class HybridRetrievalResult:
    evidence: tuple[HybridEvidence, ...]
    status: str
    expanded_context: tuple[HybridEvidence, ...] = ()


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[str]],
    *,
    rank_constant: int = 60,
) -> dict[str, float]:
    """Return RRF scores; scores are rank signals, never confidence values."""
    if rank_constant < 0:
        raise ValueError("rank_constant must be non-negative")
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        seen: set[str] = set()
        for rank, item_id in enumerate(ranked, 1):
            if item_id in seen:
                continue
            seen.add(item_id)
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (rank_constant + rank)
    return scores


class DeterministicRerankerAdapter:
    """Provider-neutral local reranker used by tests and offline benchmarks."""

    def rerank(
        self,
        request: RerankerRequest,
        *,
        route: ModelRoute,
        timeout_seconds: float,
    ) -> RerankerResult:
        del timeout_seconds
        query_terms = Counter(_tokens(request.query))
        ranked = []
        for document_id, text in request.documents:
            document_terms = Counter(_tokens(text))
            score = float(sum(query_terms[token] * document_terms[token] for token in query_terms))
            ranked.append(RankedDocument(document_id, score))
        ranked.sort(key=lambda item: (-item.score, item.document_id))
        return RerankerResult(tuple(ranked), route=route)


@dataclass(frozen=True, slots=True)
class _FusedCandidate:
    citation: Citation
    text: str
    rrf_score: float


class HybridRetriever:
    """Compose authorized dense candidates with local BM25, RRF and reranking."""

    def __init__(
        self,
        *,
        dense: DenseRetriever,
        bm25: InMemoryBM25Index,
        model_gateway: ModelGateway,
        config: HybridRetrievalConfig | None = None,
    ) -> None:
        self._dense = dense
        self._bm25 = bm25
        self._model_gateway = model_gateway
        self._config = config or HybridRetrievalConfig()

    def search(
        self,
        query: str,
        principal: AuthenticatedPrincipal,
        *,
        policy_epoch: int,
        top_k: int = 8,
    ) -> HybridRetrievalResult:
        if not query.strip():
            raise ValueError("query must not be empty")
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        branch_k = self._config.branch_top_k
        dense_result = self._dense.search(
            query,
            principal,
            policy_epoch=policy_epoch,
            top_k=branch_k,
        )
        if dense_result.status == "ERROR":
            return HybridRetrievalResult((), "ERROR")
        bm25_ranked = self._bm25_search(query, principal, policy_epoch, branch_k)
        candidates = self._fuse(dense_result.evidence, bm25_ranked)
        if not candidates:
            return HybridRetrievalResult((), "INSUFFICIENT_EVIDENCE")

        rerank_candidates = candidates[: self._config.rerank_top_k]
        try:
            reranked = self._model_gateway.rerank(
                query,
                tuple((item.citation.chunk_id, item.text) for item in rerank_candidates),
                classification=DataClassification.INTERNAL,
            )
        except Exception:
            return HybridRetrievalResult((), "ERROR")

        by_id = {item.citation.chunk_id: item for item in rerank_candidates}
        evidence: list[HybridEvidence] = []
        seen: set[str] = set()
        for ranked in reranked.ranked_documents:
            candidate = by_id.get(ranked.document_id)
            if candidate is None or ranked.document_id in seen:
                continue
            seen.add(ranked.document_id)
            evidence.append(
                HybridEvidence(
                    citation=candidate.citation,
                    score=ranked.score,
                    text=candidate.text,
                    rrf_score=candidate.rrf_score,
                    rerank_score=ranked.score,
                )
            )
            if len(evidence) == top_k:
                break
        return HybridRetrievalResult(
            tuple(evidence),
            "OK" if evidence else "ERROR",
            self._expand_parent_context(tuple(evidence), principal, policy_epoch),
        )

    def fetch_source(
        self,
        chunk_id: UUID | str,
        principal: AuthenticatedPrincipal,
        *,
        policy_epoch: int,
    ) -> SourceFetchResult:
        return self._dense.fetch_source(chunk_id, principal, policy_epoch=policy_epoch)

    def _expand_parent_context(
        self,
        evidence: tuple[HybridEvidence, ...],
        principal: AuthenticatedPrincipal,
        policy_epoch: int,
    ) -> tuple[HybridEvidence, ...]:
        children = tuple(
            ChildEvidence(
                chunk_id=item.citation.chunk_id,
                tenant_id=item.citation.tenant_id,
                document_id=item.citation.document_id,
                version_id=item.citation.version_id,
                text=item.text,
                citation=item.citation,
                parent_chunk_id=item.citation.parent_chunk_id,
            )
            for item in evidence
        )
        parent_records = tuple(
            record
            for child in children
            if child.parent_chunk_id
            for record in (self._dense.parent_record(child.parent_chunk_id),)
            if record is not None
        )
        try:
            expansion = expand_parent_context(
                children,
                parent_records,
                lambda parent: self._dense.is_authorized(
                    parent.chunk_id,
                    principal,
                    policy_epoch=policy_epoch,
                ),
            )
        except Exception:
            return ()
        child_ids = {item.citation.chunk_id for item in evidence}
        expanded: list[HybridEvidence] = []
        for parent in expansion.parents:
            if parent.parent_chunk_id in child_ids:
                continue
            if not isinstance(parent.source_locator, (PDFLocator, DOCXLocator, XLSXLocator)):
                continue
            expanded.append(
                HybridEvidence(
                    citation=Citation(
                        chunk_id=parent.parent_chunk_id,
                        document_id=parent.document_id,
                        version_id=parent.version_id,
                        tenant_id=parent.tenant_id,
                        policy_epoch=policy_epoch,
                        locator=parent.source_locator,
                    ),
                    score=0.0,
                    text=parent.text,
                    rrf_score=0.0,
                    rerank_score=0.0,
                )
            )
        return tuple(expanded)

    def _bm25_search(
        self,
        query: str,
        principal: AuthenticatedPrincipal,
        policy_epoch: int,
        top_k: int,
    ) -> tuple[tuple[Citation, str, float], ...]:
        query_terms = Counter(_tokens(query))
        if not query_terms:
            return ()
        records = self._bm25._records_for_retrieval()
        if not records:
            return ()
        authorized_records = tuple(
            record
            for record in records
            if record.chunk.source_locator is not None
            and self._dense.is_authorized(
                record.chunk.chunk_id,
                principal,
                policy_epoch=policy_epoch,
            )
        )
        if not authorized_records:
            return ()
        document_frequency = Counter(
            term for record in authorized_records for term in set(record.tokens)
        )
        average_length = max(
            1.0,
            sum(len(record.tokens) for record in authorized_records) / len(authorized_records),
        )
        scored: list[tuple[Citation, str, float]] = []
        for record in authorized_records:
            score = self._bm25_score(
                query_terms,
                record,
                document_frequency,
                len(authorized_records),
                average_length,
            )
            if score > 0:
                scored.append((_citation(record.chunk, policy_epoch), record.text, score))
        scored.sort(key=lambda item: (-item[2], item[0].chunk_id))
        return tuple(scored[:top_k])

    def _bm25_score(
        self,
        query_terms: Mapping[str, int],
        record: _BM25Record,
        document_frequency: Mapping[str, int],
        document_count: int,
        average_length: float,
    ) -> float:
        term_frequency = Counter(record.tokens)
        score = 0.0
        for term, query_frequency in query_terms.items():
            frequency = term_frequency.get(term, 0)
            if not frequency:
                continue
            idf = math.log1p((document_count - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5))
            denominator = frequency + self._bm25.k1 * (
                1 - self._bm25.b + self._bm25.b * len(record.tokens) / average_length
            )
            score += idf * frequency * (self._bm25.k1 + 1) / denominator * query_frequency
        return score

    def _fuse(
        self,
        dense: Sequence,
        bm25: Sequence[tuple[Citation, str, float]],
    ) -> tuple[_FusedCandidate, ...]:
        dense_ids = [item.citation.chunk_id for item in dense]
        bm25_ids = [item[0].chunk_id for item in bm25]
        scores = reciprocal_rank_fusion(
            (dense_ids, bm25_ids),
            rank_constant=self._config.rrf_k,
        )
        by_id: dict[str, tuple[Citation, str]] = {
            item.citation.chunk_id: (item.citation, item.text) for item in dense
        }
        by_id.update({item[0].chunk_id: (item[0], item[1]) for item in bm25})
        ordered = sorted(scores, key=lambda item: (-scores[item], item))
        return tuple(
            _FusedCandidate(by_id[item_id][0], by_id[item_id][1], scores[item_id])
            for item_id in ordered
        )


def _citation(chunk: ChunkMetadata, policy_epoch: int) -> Citation:
    return Citation(
        chunk_id=str(chunk.chunk_id),
        document_id=str(chunk.document_id),
        version_id=str(chunk.version_id),
        tenant_id=str(chunk.tenant_id),
        policy_epoch=policy_epoch,
        locator=chunk.source_locator,
        parent_chunk_id=(str(chunk.parent_chunk_id) if chunk.parent_chunk_id is not None else None),
    )


__all__ = [
    "DeterministicRerankerAdapter",
    "HybridEvidence",
    "HybridRetrievalConfig",
    "HybridRetrievalResult",
    "HybridRetriever",
    "InMemoryBM25Index",
    "reciprocal_rank_fusion",
]
