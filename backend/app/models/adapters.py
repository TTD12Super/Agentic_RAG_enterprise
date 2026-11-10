"""Small adapter protocols shared by embeddings and reranking callers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from .policy import ModelRoute


@dataclass(frozen=True)
class EmbeddingRequest:
    texts: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.texts or any(not text.strip() for text in self.texts):
            raise ValueError("texts must contain non-empty strings")


@dataclass(frozen=True)
class EmbeddingResult:
    vectors: tuple[tuple[float, ...], ...]
    route: ModelRoute

    def __post_init__(self) -> None:
        if not self.vectors or any(not vector for vector in self.vectors):
            raise ValueError("vectors must contain non-empty vectors")
        dimensions = len(self.vectors[0])
        if any(len(vector) != dimensions for vector in self.vectors):
            raise ValueError("all vectors must have the same dimension")


class EmbeddingAdapter(Protocol):
    def embed(
        self,
        request: EmbeddingRequest,
        *,
        route: ModelRoute,
        timeout_seconds: float,
    ) -> EmbeddingResult: ...


@dataclass(frozen=True)
class RerankerRequest:
    query: str
    documents: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.query.strip() or not self.documents:
            raise ValueError("query and documents are required")
        if any(not document_id.strip() or not text.strip() for document_id, text in self.documents):
            raise ValueError("documents must contain non-empty ids and text")


@dataclass(frozen=True)
class RankedDocument:
    document_id: str
    score: float


@dataclass(frozen=True)
class RerankerResult:
    ranked_documents: tuple[RankedDocument, ...]
    route: ModelRoute

    def __post_init__(self) -> None:
        if not self.ranked_documents:
            raise ValueError("ranked_documents must not be empty")


class RerankerAdapter(Protocol):
    def rerank(
        self,
        request: RerankerRequest,
        *,
        route: ModelRoute,
        timeout_seconds: float,
    ) -> RerankerResult: ...
