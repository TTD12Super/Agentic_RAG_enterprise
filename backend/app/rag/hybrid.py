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
from ..knowledge.models import ChunkMetadata
from ..models.adapters import RankedDocument, RerankerRequest, RerankerResult
from ..models.policy import DataClassification, ModelRoute
from .dense import Citation, DenseRetriever, SourceFetchResult


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
        )

    def fetch_source(
        self,
        chunk_id: UUID | str,
        principal: AuthenticatedPrincipal,
        *,
        policy_epoch: int,
    ) -> SourceFetchResult:
        return self._dense.fetch_source(chunk_id, principal, policy_epoch=policy_epoch)

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
            if self._dense.is_authorized(
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
                scored.append((_citation(record.chunk), record.text, score))
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


def _citation(chunk: ChunkMetadata) -> Citation:
    return Citation(
        chunk_id=str(chunk.chunk_id),
        document_id=str(chunk.document_id),
        version_id=str(chunk.version_id),
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        source_span=chunk.source_span,
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
