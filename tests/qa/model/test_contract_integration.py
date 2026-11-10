"""MODEL-001 contract/integration QA: 12 deterministic synthetic cases."""

import pytest

from backend.app.integrations.model_gateway import ModelGateway
from backend.app.models.adapters import EmbeddingRequest, RerankerRequest
from backend.app.models.policy import DataClassification, ModelPolicy, ModelTask

from tests.qa.model._baseline import (
    ScriptedEmbedding,
    ScriptedReranker,
    mapping,
    policy,
    provider,
    route,
)


def test_versioned_mapping_loads_without_credentials():
    loaded = ModelPolicy.from_mapping(mapping())
    assert loaded.policy_version == "model-policy.synthetic.v1"


def test_exact_api_key_field_is_rejected():
    with pytest.raises(ValueError, match="credentials"):
        ModelPolicy.from_mapping(mapping(provider_fields={"api_key": "synthetic"}))


def test_access_token_field_is_rejected():
    with pytest.raises(ValueError, match="credentials"):
        ModelPolicy.from_mapping(mapping(provider_fields={"access_token": "synthetic"}))


def test_secret_key_field_is_rejected():
    with pytest.raises(ValueError, match="credentials"):
        ModelPolicy.from_mapping(mapping(provider_fields={"secret_key": "synthetic"}))


def test_embedding_gateway_contract_passes_request_route_and_timeout():
    adapter = ScriptedEmbedding()
    gateway = ModelGateway(policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={})
    gateway.embed(("synthetic text",), classification=DataClassification.PUBLIC)
    assert isinstance(adapter.requests[0], EmbeddingRequest)
    assert adapter.routes[0].task is ModelTask.EMBEDDING
    assert adapter.timeouts == [60.0]


def test_reranker_gateway_contract_passes_request_route_and_timeout():
    adapter = ScriptedReranker()
    gateway = ModelGateway(policy(), embedding_adapters={}, reranker_adapters={"local-test": adapter})
    gateway.rerank("synthetic query", (("doc-1", "synthetic text"),), classification=DataClassification.PUBLIC)
    assert isinstance(adapter.requests[0], RerankerRequest)
    assert adapter.routes[0].task is ModelTask.RERANKER
    assert adapter.timeouts == [60.0]


def test_embedding_result_keeps_selected_route():
    adapter = ScriptedEmbedding()
    result = ModelGateway(policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={}).embed(
        ("text",), classification=DataClassification.PUBLIC
    )
    assert result.route == adapter.routes[0]


def test_reranker_result_keeps_selected_route():
    adapter = ScriptedReranker()
    result = ModelGateway(policy(), embedding_adapters={}, reranker_adapters={"local-test": adapter}).rerank(
        "query", (("doc-1", "text"),), classification=DataClassification.PUBLIC
    )
    assert result.route == adapter.routes[0]


def test_fallback_route_task_mismatch_is_rejected():
    with pytest.raises(ValueError):
        ModelPolicy(
            policy_version="v1",
            embedding=route(ModelTask.EMBEDDING),
            reranker=route(ModelTask.RERANKER),
            fallback_embedding=route(ModelTask.RERANKER),
        )


def test_mapping_rejects_empty_model_revision():
    raw = mapping()
    raw["embedding"]["revision"] = ""
    with pytest.raises(ValueError):
        ModelPolicy.from_mapping(raw)
