"""Versioned, provider-neutral model routing policy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping


class ModelTask(StrEnum):
    EMBEDDING = "embedding"
    RERANKER = "reranker"


class DataClassification(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"


class EgressMode(StrEnum):
    LOCAL = "local"
    EXTERNAL = "external"


@dataclass(frozen=True)
class ProviderPolicy:
    """The data-handling approval required before a provider call."""

    provider_id: str
    egress_mode: EgressMode
    allowed_classifications: frozenset[DataClassification]
    approved: bool = False
    data_processing_agreement: bool = False
    residency_approved: bool = False
    training_allowed: bool = False
    request_retention_seconds: int | None = None

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise ValueError("provider_id must not be empty")
        if not self.allowed_classifications:
            raise ValueError("allowed_classifications must not be empty")
        if self.request_retention_seconds is not None and self.request_retention_seconds < 0:
            raise ValueError("request_retention_seconds must be non-negative")

    def allows(self, classification: DataClassification) -> bool:
        """Return whether this exact classification may leave the service."""

        if not isinstance(classification, DataClassification):
            return False
        if classification not in self.allowed_classifications or not self.approved:
            return False
        if self.egress_mode is EgressMode.LOCAL:
            return True
        if self.training_allowed or self.request_retention_seconds is None:
            return False
        if classification is DataClassification.INTERNAL:
            return self.data_processing_agreement and self.residency_approved
        return True


@dataclass(frozen=True)
class ModelRoute:
    task: ModelTask
    provider: ProviderPolicy
    model_id: str
    revision: str

    def __post_init__(self) -> None:
        if not self.model_id.strip() or not self.revision.strip():
            raise ValueError("model_id and revision must not be empty")


@dataclass(frozen=True)
class ModelPolicy:
    """Immutable policy snapshot used by one gateway invocation."""

    policy_version: str
    embedding: ModelRoute
    reranker: ModelRoute
    fallback_embedding: ModelRoute | None = None
    fallback_reranker: ModelRoute | None = None
    timeout_seconds: float = 60.0
    max_primary_retries: int = 2

    def __post_init__(self) -> None:
        if not self.policy_version.strip():
            raise ValueError("policy_version must not be empty")
        if self.embedding.task is not ModelTask.EMBEDDING:
            raise ValueError("embedding route must use the embedding task")
        if self.reranker.task is not ModelTask.RERANKER:
            raise ValueError("reranker route must use the reranker task")
        if self.fallback_embedding and self.fallback_embedding.task is not ModelTask.EMBEDDING:
            raise ValueError("fallback_embedding must use the embedding task")
        if self.fallback_reranker and self.fallback_reranker.task is not ModelTask.RERANKER:
            raise ValueError("fallback_reranker must use the reranker task")
        if not 0 < self.timeout_seconds <= 60:
            raise ValueError("timeout_seconds must be greater than 0 and at most 60")
        if not 0 <= self.max_primary_retries <= 2:
            raise ValueError("max_primary_retries must be between 0 and 2")

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ModelPolicy":
        """Load a versioned policy without reading secrets or environment state."""

        def route(value: Mapping[str, Any], task: ModelTask) -> ModelRoute:
            provider_raw = value["provider"]
            credential_terms = ("key", "token", "secret", "password", "credential")
            if any(
                any(term in str(key).lower() for term in credential_terms)
                for key in provider_raw
            ):
                raise ValueError("provider policy must not contain credentials")
            provider = ProviderPolicy(
                provider_id=provider_raw["provider_id"],
                egress_mode=EgressMode(provider_raw["egress_mode"]),
                allowed_classifications=frozenset(
                    DataClassification(item)
                    for item in provider_raw["allowed_classifications"]
                ),
                approved=provider_raw.get("approved", False),
                data_processing_agreement=provider_raw.get(
                    "data_processing_agreement", False
                ),
                residency_approved=provider_raw.get("residency_approved", False),
                training_allowed=provider_raw.get("training_allowed", False),
                request_retention_seconds=provider_raw.get("request_retention_seconds"),
            )
            return ModelRoute(
                task=task,
                provider=provider,
                model_id=value["model_id"],
                revision=value["revision"],
            )

        return cls(
            policy_version=raw["policy_version"],
            embedding=route(raw["embedding"], ModelTask.EMBEDDING),
            reranker=route(raw["reranker"], ModelTask.RERANKER),
            fallback_embedding=(
                route(raw["fallback_embedding"], ModelTask.EMBEDDING)
                if raw.get("fallback_embedding")
                else None
            ),
            fallback_reranker=(
                route(raw["fallback_reranker"], ModelTask.RERANKER)
                if raw.get("fallback_reranker")
                else None
            ),
            timeout_seconds=raw.get("timeout_seconds", 60.0),
            max_primary_retries=raw.get("max_primary_retries", 2),
        )
