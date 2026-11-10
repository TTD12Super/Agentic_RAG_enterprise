"""MODEL-001 security/adversarial QA: 12 deterministic synthetic cases."""

import pytest

from backend.app.integrations.model_gateway import ModelEgressDenied, ModelGateway, ModelUnavailable
from backend.app.models.policy import DataClassification, EgressMode

from tests.qa.model._baseline import (
    ScriptedEmbedding,
    mapping,
    policy,
    provider,
    route,
)


def gateway_for(provider_policy, adapter=None, fallback=None):
    return ModelGateway(
        policy(embedding_provider=provider_policy, fallback_embedding=fallback),
        embedding_adapters={provider_policy.provider_id: adapter or ScriptedEmbedding(), **({fallback.provider.provider_id: ScriptedEmbedding()} if fallback else {})},
        reranker_adapters={},
    )


def test_egress_denial_does_not_echo_input():
    with pytest.raises(ModelEgressDenied) as error:
        gateway_for(provider(mode=EgressMode.EXTERNAL, retention=0)).embed(
            ("synthetic-private-text",), classification=DataClassification.INTERNAL
        )
    assert "synthetic-private-text" not in str(error.value)


def test_external_internal_without_dpa_is_denied():
    with pytest.raises(ModelEgressDenied):
        gateway_for(provider(mode=EgressMode.EXTERNAL, retention=0, residency=True)).embed(
            ("internal",), classification=DataClassification.INTERNAL
        )


def test_external_internal_without_residency_is_denied():
    with pytest.raises(ModelEgressDenied):
        gateway_for(provider(mode=EgressMode.EXTERNAL, retention=0, dpa=True)).embed(
            ("internal",), classification=DataClassification.INTERNAL
        )


def test_denied_primary_cannot_use_denied_fallback():
    primary = provider("primary", mode=EgressMode.EXTERNAL, retention=0)
    fallback = route(__import__("backend.app.models.policy", fromlist=["ModelTask"]).ModelTask.EMBEDDING, provider("fallback", mode=EgressMode.EXTERNAL, retention=0))
    with pytest.raises(ModelEgressDenied):
        gateway_for(primary, fallback=fallback).embed(("internal",), classification=DataClassification.INTERNAL)


def test_external_training_provider_is_denied():
    assert not provider(mode=EgressMode.EXTERNAL, retention=0, training=True).allows(DataClassification.PUBLIC)


def test_unknown_classification_fails_closed_with_safe_error():
    with pytest.raises(ModelEgressDenied):
        gateway_for(provider()).embed(("text",), classification="CONFIDENTIAL")  # type: ignore[arg-type]


def test_access_token_is_not_accepted_as_policy_data():
    with pytest.raises(ValueError, match="credentials"):
        from backend.app.models.policy import ModelPolicy

        ModelPolicy.from_mapping(mapping(provider_fields={"access_token": "synthetic"}))


def test_secret_key_is_not_accepted_as_policy_data():
    with pytest.raises(ValueError, match="credentials"):
        from backend.app.models.policy import ModelPolicy

        ModelPolicy.from_mapping(mapping(provider_fields={"secret_key": "synthetic"}))


def test_api_key_is_not_accepted_as_policy_data():
    with pytest.raises(ValueError, match="credentials"):
        from backend.app.models.policy import ModelPolicy

        ModelPolicy.from_mapping(mapping(provider_fields={"api_key": "synthetic"}))


def test_runtime_provider_failure_does_not_leak_raw_payload():
    with pytest.raises(ModelUnavailable) as error:
        gateway_for(provider(), adapter=ScriptedEmbedding(["runtime"])).embed(
            ("text",), classification=DataClassification.PUBLIC
        )
    assert "synthetic-secret-payload" not in str(error.value)
