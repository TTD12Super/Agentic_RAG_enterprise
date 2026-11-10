"""Synthetic helpers and repository evidence for MODEL-001 QA."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from backend.app.integrations.model_gateway import (
    ModelProviderError,
)
from backend.app.models.adapters import (
    EmbeddingResult,
    RankedDocument,
    RerankerResult,
)
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelRoute,
    ModelTask,
    ProviderPolicy,
)


ROOT = Path(__file__).resolve().parents[3]
TASKS = ROOT / "harness/tasks/tasks.json"
HANDOFF = ROOT / "harness/handoffs/MODEL-001.md"
GRAPH = ROOT / "graphify-out/graph.json"


def provider(
    provider_id: str = "local-test",
    *,
    mode: EgressMode = EgressMode.LOCAL,
    allowed: frozenset[DataClassification] | None = None,
    approved: bool = True,
    dpa: bool = False,
    residency: bool = False,
    training: bool = False,
    retention: int | None = None,
) -> ProviderPolicy:
    return ProviderPolicy(
        provider_id=provider_id,
        egress_mode=mode,
        allowed_classifications=(
            allowed
            if allowed is not None
            else frozenset({DataClassification.PUBLIC, DataClassification.INTERNAL})
        ),
        approved=approved,
        data_processing_agreement=dpa,
        residency_approved=residency,
        training_allowed=training,
        request_retention_seconds=retention,
    )


def route(
    task: ModelTask,
    model_provider: ProviderPolicy | None = None,
    *,
    model_id: str | None = None,
) -> ModelRoute:
    return ModelRoute(
        task=task,
        provider=model_provider or provider(),
        model_id=model_id or f"synthetic-{task.value}",
        revision="synthetic-revision-1",
    )


def policy(
    *,
    embedding_provider: ProviderPolicy | None = None,
    reranker_provider: ProviderPolicy | None = None,
    fallback_embedding: ModelRoute | None = None,
    fallback_reranker: ModelRoute | None = None,
    retries: int = 2,
    timeout: float = 60.0,
) -> ModelPolicy:
    return ModelPolicy(
        policy_version="model-policy.synthetic.v1",
        embedding=route(ModelTask.EMBEDDING, embedding_provider),
        reranker=route(ModelTask.RERANKER, reranker_provider),
        fallback_embedding=fallback_embedding,
        fallback_reranker=fallback_reranker,
        max_primary_retries=retries,
        timeout_seconds=timeout,
    )


class ScriptedEmbedding:
    """Deterministic adapter double; outcomes are timeout, retry, fatal, runtime or ok."""

    def __init__(self, outcomes: list[str] | None = None) -> None:
        self.outcomes = list(outcomes or [])
        self.calls = 0
        self.requests: list[Any] = []
        self.routes: list[ModelRoute] = []
        self.timeouts: list[float] = []

    def embed(self, request, *, route, timeout_seconds):
        self.calls += 1
        self.requests.append(request)
        self.routes.append(route)
        self.timeouts.append(timeout_seconds)
        outcome = self.outcomes.pop(0) if self.outcomes else "ok"
        if outcome == "timeout":
            raise TimeoutError("synthetic timeout")
        if outcome == "retry":
            raise ModelProviderError("synthetic provider payload", retryable=True)
        if outcome == "fatal":
            raise ModelProviderError("synthetic fatal payload", retryable=False)
        if outcome == "runtime":
            raise RuntimeError("synthetic-secret-payload")
        return EmbeddingResult(vectors=((0.1, 0.2),), route=route)


class ScriptedReranker:
    """Deterministic reranker double with the same failure vocabulary."""

    def __init__(self, outcomes: list[str] | None = None) -> None:
        self.outcomes = list(outcomes or [])
        self.calls = 0
        self.requests: list[Any] = []
        self.routes: list[ModelRoute] = []
        self.timeouts: list[float] = []

    def rerank(self, request, *, route, timeout_seconds):
        self.calls += 1
        self.requests.append(request)
        self.routes.append(route)
        self.timeouts.append(timeout_seconds)
        outcome = self.outcomes.pop(0) if self.outcomes else "ok"
        if outcome == "timeout":
            raise TimeoutError("synthetic timeout")
        if outcome == "retry":
            raise ModelProviderError("synthetic provider payload", retryable=True)
        if outcome == "fatal":
            raise ModelProviderError("synthetic fatal payload", retryable=False)
        if outcome == "runtime":
            raise RuntimeError("synthetic-secret-payload")
        return RerankerResult(
            ranked_documents=(RankedDocument(document_id="doc-1", score=1.0),),
            route=route,
        )


def mapping(*, provider_fields: dict[str, Any] | None = None) -> dict[str, Any]:
    provider_data: dict[str, Any] = {
        "provider_id": "local",
        "egress_mode": "local",
        "allowed_classifications": ["PUBLIC", "INTERNAL"],
        "approved": True,
    }
    provider_data.update(provider_fields or {})
    route_data = {
        "model_id": "synthetic-model",
        "revision": "synthetic-revision-1",
        "provider": provider_data,
    }
    return {
        "policy_version": "model-policy.synthetic.v1",
        "embedding": route_data,
        "reranker": dict(route_data),
    }


def task(task_id: str) -> dict[str, Any]:
    data = json.loads(TASKS.read_text(encoding="utf-8"))
    return next(item for item in data["tasks"] if item["id"] == task_id)


def graph_labels() -> set[str]:
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    return {node["label"] for node in data["nodes"]}


def run_graph_query(query: str) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("graphify") or "/tmp/graphify-venv/bin/graphify"
    return subprocess.run(
        [executable, "query", query, "--graph", str(GRAPH), "--budget", "3000"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
