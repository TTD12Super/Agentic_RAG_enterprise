"""Policy-enforcing gateway for provider-neutral model adapters."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TypeVar

from ..models.adapters import (
    EmbeddingAdapter,
    EmbeddingRequest,
    EmbeddingResult,
    RerankerAdapter,
    RerankerRequest,
    RerankerResult,
)
from ..models.policy import DataClassification, ModelPolicy, ModelRoute


class ModelProviderError(Exception):
    """A provider failure that is safe to classify for retry/fallback."""

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class ModelEgressDenied(ModelProviderError):
    def __init__(self, provider_id: str, classification: DataClassification | str) -> None:
        safe_classification = (
            classification.value
            if isinstance(classification, DataClassification)
            else "UNKNOWN"
        )
        super().__init__(
            f"model egress denied for provider {provider_id!r} and "
            f"classification {safe_classification!r}",
            retryable=False,
        )


class ModelUnavailable(ModelProviderError):
    def __init__(self, task: str, reasons: tuple[str, ...]) -> None:
        super().__init__(f"no approved {task} model route available: {'; '.join(reasons)}")


Result = TypeVar("Result")
Adapter = TypeVar("Adapter")


class ModelGateway:
    """Execute approved routes with bounded primary retries and one fallback."""

    def __init__(
        self,
        policy: ModelPolicy,
        *,
        embedding_adapters: Mapping[str, EmbeddingAdapter],
        reranker_adapters: Mapping[str, RerankerAdapter],
    ) -> None:
        self.policy = policy
        self._embedding_adapters = embedding_adapters
        self._reranker_adapters = reranker_adapters

    def embed(
        self,
        texts: tuple[str, ...],
        *,
        classification: DataClassification,
    ) -> EmbeddingResult:
        request = EmbeddingRequest(texts=texts)
        return self._execute(
            task="embedding",
            classification=classification,
            primary=self.policy.embedding,
            fallback=self.policy.fallback_embedding,
            adapters=self._embedding_adapters,
            operation=lambda adapter, route: adapter.embed(
                request, route=route, timeout_seconds=self.policy.timeout_seconds
            ),
        )

    def rerank(
        self,
        query: str,
        documents: tuple[tuple[str, str], ...],
        *,
        classification: DataClassification,
    ) -> RerankerResult:
        request = RerankerRequest(query=query, documents=documents)
        return self._execute(
            task="reranker",
            classification=classification,
            primary=self.policy.reranker,
            fallback=self.policy.fallback_reranker,
            adapters=self._reranker_adapters,
            operation=lambda adapter, route: adapter.rerank(
                request, route=route, timeout_seconds=self.policy.timeout_seconds
            ),
        )

    def _execute(
        self,
        *,
        task: str,
        classification: DataClassification,
        primary: ModelRoute,
        fallback: ModelRoute | None,
        adapters: Mapping[str, Adapter],
        operation: Callable[[Adapter, ModelRoute], Result],
    ) -> Result:
        reasons: list[str] = []
        eligible_route = False
        for index, route in enumerate((primary, fallback)):
            if route is None:
                continue
            if not route.provider.allows(classification):
                reasons.append(f"{route.provider.provider_id}: egress denied")
                continue
            eligible_route = True
            adapter = adapters.get(route.provider.provider_id)
            if adapter is None:
                reasons.append(f"{route.provider.provider_id}: adapter unavailable")
                continue

            attempts = self.policy.max_primary_retries + 1 if index == 0 else 1
            for _ in range(attempts):
                try:
                    return operation(adapter, route)
                except TimeoutError:
                    reasons.append(f"{route.provider.provider_id}: timeout")
                except ModelProviderError as error:
                    # Provider messages may contain prompt or response data.
                    reasons.append(f"{route.provider.provider_id}: provider failure")
                    if not error.retryable:
                        break
                except Exception:
                    # Provider SDK errors may contain request or credential data.
                    reasons.append(f"{route.provider.provider_id}: provider failure")
                    break
        if not eligible_route:
            raise ModelEgressDenied(primary.provider.provider_id, classification)
        raise ModelUnavailable(task, tuple(reasons))
