"""MODEL-001 E2E/operational QA: 12 deterministic synthetic cases."""

import json

import pytest

from backend.app.integrations.model_gateway import ModelEgressDenied, ModelGateway, ModelUnavailable
from backend.app.models.policy import DataClassification, EgressMode

from tests.qa.model._baseline import (
    GRAPH,
    HANDOFF,
    ScriptedEmbedding,
    ScriptedReranker,
    graph_labels,
    policy,
    provider,
    route,
    run_graph_query,
    task,
)


def test_embedding_happy_path_completes_once():
    adapter = ScriptedEmbedding()
    gateway = ModelGateway(policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={})
    result = gateway.embed(("synthetic text",), classification=DataClassification.PUBLIC)
    assert result.vectors and adapter.calls == 1


def test_reranker_happy_path_completes_once():
    adapter = ScriptedReranker()
    gateway = ModelGateway(policy(), embedding_adapters={}, reranker_adapters={"local-test": adapter})
    result = gateway.rerank("query", (("doc-1", "text"),), classification=DataClassification.PUBLIC)
    assert result.ranked_documents and adapter.calls == 1


def test_primary_retries_twice_then_succeeds():
    adapter = ScriptedEmbedding(["timeout", "retry"])
    ModelGateway(policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={}).embed(
        ("text",), classification=DataClassification.PUBLIC
    )
    assert adapter.calls == 3


def test_primary_attempts_are_bounded():
    adapter = ScriptedEmbedding(["timeout", "timeout", "timeout", "timeout"])
    with pytest.raises(ModelUnavailable):
        ModelGateway(policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={}).embed(
            ("text",), classification=DataClassification.PUBLIC
        )
    assert adapter.calls == 3


def test_approved_fallback_runs_after_primary_failure():
    primary = ScriptedEmbedding(["retry", "retry", "retry"])
    fallback = ScriptedEmbedding()
    fallback_route = route(task=__import__("backend.app.models.policy", fromlist=["ModelTask"]).ModelTask.EMBEDDING, model_provider=provider("fallback"))
    result = ModelGateway(
        policy(fallback_embedding=fallback_route),
        embedding_adapters={"local-test": primary, "fallback": fallback},
        reranker_adapters={},
    ).embed(("text",), classification=DataClassification.PUBLIC)
    assert result.route.provider.provider_id == "fallback"
    assert primary.calls == 3 and fallback.calls == 1


def test_fallback_is_attempted_once():
    fallback = ScriptedEmbedding(["retry", "retry"])
    fallback_route = route(__import__("backend.app.models.policy", fromlist=["ModelTask"]).ModelTask.EMBEDDING, provider("fallback"))
    with pytest.raises(ModelUnavailable):
        ModelGateway(
            policy(fallback_embedding=fallback_route),
            embedding_adapters={"local-test": ScriptedEmbedding(["fatal"]), "fallback": fallback},
            reranker_adapters={},
        ).embed(("text",), classification=DataClassification.PUBLIC)
    assert fallback.calls == 1


def test_task_registry_keeps_model_acceptance_and_validation():
    item = task("MODEL-001")
    assert item["phase"] == 2
    assert "provider timeout, bounded retry, fallback and egress-policy cases" in " ".join(item["validation"])


def test_handoff_records_no_provider_selection():
    text = HANDOFF.read_text(encoding="utf-8")
    assert "No commit or push was performed" in text
    assert "No provider was guessed" in text


def test_graph_contains_model_symbols():
    labels = graph_labels()
    assert {"ModelPolicy", "ModelGateway", "EmbeddingAdapter", "RerankerAdapter"} <= labels


def test_graphify_query_finds_model_gateway():
    result = run_graph_query("ModelGateway ModelPolicy EmbeddingAdapter RerankerAdapter")
    assert result.returncode == 0
    assert "ModelGateway" in result.stdout
