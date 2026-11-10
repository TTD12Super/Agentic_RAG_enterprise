"""MODEL-001 model policy, adapter and gateway tests.

The providers below are deterministic test doubles. No network, credentials or
external model package is needed to validate the boundary.
"""

import pytest

from backend.app.integrations.model_gateway import (
    ModelEgressDenied,
    ModelGateway,
    ModelProviderError,
    ModelUnavailable,
)
from backend.app.models.adapters import (
    EmbeddingRequest,
    EmbeddingResult,
    RankedDocument,
    RerankerRequest,
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


def route(task: ModelTask, model_provider: ProviderPolicy | None = None) -> ModelRoute:
    return ModelRoute(
        task=task,
        provider=model_provider or provider(),
        model_id=f"test-{task.value}",
        revision="2026-01-01",
    )


def policy(
    *,
    embedding_provider: ProviderPolicy | None = None,
    reranker_provider: ProviderPolicy | None = None,
    fallback_embedding: ModelRoute | None = None,
    fallback_reranker: ModelRoute | None = None,
    retries: int = 2,
) -> ModelPolicy:
    return ModelPolicy(
        policy_version="model-policy.v1",
        embedding=route(ModelTask.EMBEDDING, embedding_provider),
        reranker=route(ModelTask.RERANKER, reranker_provider),
        fallback_embedding=fallback_embedding,
        fallback_reranker=fallback_reranker,
        max_primary_retries=retries,
    )


class FakeEmbedding:
    def __init__(self, failures: list[str] | None = None) -> None:
        self.failures = list(failures or [])
        self.calls = 0
        self.timeouts: list[float] = []

    def embed(self, request, *, route, timeout_seconds):
        self.calls += 1
        self.timeouts.append(timeout_seconds)
        if self.failures:
            failure = self.failures.pop(0)
            if failure == "timeout":
                raise TimeoutError("synthetic timeout")
            raise ModelProviderError(f"synthetic {failure}", retryable=failure == "retry")
        return EmbeddingResult(vectors=((0.1, 0.2),), route=route)


class FakeReranker:
    def __init__(self, failures: list[str] | None = None) -> None:
        self.failures = list(failures or [])
        self.calls = 0
        self.timeouts: list[float] = []

    def rerank(self, request, *, route, timeout_seconds):
        self.calls += 1
        self.timeouts.append(timeout_seconds)
        if self.failures:
            failure = self.failures.pop(0)
            raise ModelProviderError(f"synthetic {failure}", retryable=failure == "retry")
        return RerankerResult(
            ranked_documents=(RankedDocument(document_id=request.documents[0][0], score=1.0),),
            route=route,
        )


# Policy unit tests (10)
def test_model_task_values_are_stable():
    assert ModelTask.EMBEDDING.value == "embedding"
    assert ModelTask.RERANKER.value == "reranker"


def test_provider_id_is_required():
    with pytest.raises(ValueError):
        provider("")


def test_provider_classification_allowlist_is_required():
    with pytest.raises(ValueError):
        provider(allowed=frozenset())


def test_provider_retention_cannot_be_negative():
    with pytest.raises(ValueError):
        provider(retention=-1)


def test_approved_local_provider_can_process_internal_data():
    assert provider().allows(DataClassification.INTERNAL)


def test_external_provider_requires_approval():
    assert not provider(mode=EgressMode.EXTERNAL, retention=0, approved=False).allows(
        DataClassification.PUBLIC
    )


def test_external_internal_data_requires_processing_agreement():
    external = provider(mode=EgressMode.EXTERNAL, retention=0, residency=True)
    assert not external.allows(DataClassification.INTERNAL)


def test_external_internal_data_requires_residency_approval():
    external = provider(mode=EgressMode.EXTERNAL, retention=0, dpa=True)
    assert not external.allows(DataClassification.INTERNAL)


def test_external_training_is_never_allowed():
    external = provider(mode=EgressMode.EXTERNAL, retention=0, training=True)
    assert not external.allows(DataClassification.PUBLIC)


def test_mapping_loads_versioned_policy_without_credentials():
    loaded = ModelPolicy.from_mapping(
        {
            "policy_version": "model-policy.v1",
            "embedding": {
                "model_id": "bge-m3",
                "revision": "rev-a",
                "provider": {
                    "provider_id": "local",
                    "egress_mode": "local",
                    "allowed_classifications": ["PUBLIC", "INTERNAL"],
                    "approved": True,
                },
            },
            "reranker": {
                "model_id": "bge-reranker",
                "revision": "rev-a",
                "provider": {
                    "provider_id": "local",
                    "egress_mode": "local",
                    "allowed_classifications": ["PUBLIC"],
                    "approved": True,
                },
            },
        }
    )
    assert loaded.policy_version == "model-policy.v1"
    assert loaded.embedding.revision == "rev-a"


# Adapter contract tests (10)
def test_embedding_request_requires_texts():
    with pytest.raises(ValueError):
        EmbeddingRequest(texts=())


def test_embedding_request_rejects_blank_text():
    with pytest.raises(ValueError):
        EmbeddingRequest(texts=(" ",))


def test_embedding_result_requires_vectors():
    with pytest.raises(ValueError):
        EmbeddingResult(vectors=(), route=route(ModelTask.EMBEDDING))


def test_embedding_result_requires_consistent_dimensions():
    with pytest.raises(ValueError):
        EmbeddingResult(
            vectors=((0.1,), (0.1, 0.2)), route=route(ModelTask.EMBEDDING)
        )


def test_reranker_request_requires_query():
    with pytest.raises(ValueError):
        RerankerRequest(query=" ", documents=(("doc-1", "text"),))


def test_reranker_request_requires_documents():
    with pytest.raises(ValueError):
        RerankerRequest(query="query", documents=())


def test_reranker_request_rejects_blank_document_fields():
    with pytest.raises(ValueError):
        RerankerRequest(query="query", documents=(("", "text"),))


def test_reranker_result_requires_ranked_documents():
    with pytest.raises(ValueError):
        RerankerResult(ranked_documents=(), route=route(ModelTask.RERANKER))


def test_ranked_document_preserves_identifier_and_score():
    ranked = RankedDocument(document_id="doc-1", score=0.75)
    assert ranked.document_id == "doc-1"
    assert ranked.score == 0.75


def test_route_task_mismatch_is_rejected_by_policy():
    with pytest.raises(ValueError):
        ModelPolicy(
            policy_version="v1",
            embedding=route(ModelTask.RERANKER),
            reranker=route(ModelTask.RERANKER),
        )


# Gateway operational tests (10)
def test_gateway_embedding_happy_path():
    adapter = FakeEmbedding()
    gateway = ModelGateway(
        policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={}
    )
    result = gateway.embed(("hello",), classification=DataClassification.PUBLIC)
    assert result.vectors == ((0.1, 0.2),)
    assert adapter.calls == 1


def test_gateway_reranker_happy_path():
    adapter = FakeReranker()
    gateway = ModelGateway(
        policy(), embedding_adapters={}, reranker_adapters={"local-test": adapter}
    )
    result = gateway.rerank(
        "hello", (("doc-1", "world"),), classification=DataClassification.PUBLIC
    )
    assert result.ranked_documents[0].document_id == "doc-1"
    assert adapter.calls == 1


def test_gateway_retries_two_transient_timeouts_then_succeeds():
    adapter = FakeEmbedding(["timeout", "timeout"])
    gateway = ModelGateway(
        policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={}
    )
    gateway.embed(("hello",), classification=DataClassification.PUBLIC)
    assert adapter.calls == 3


def test_gateway_caps_primary_retries():
    adapter = FakeEmbedding(["timeout", "timeout", "timeout"])
    gateway = ModelGateway(
        policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={}
    )
    with pytest.raises(ModelUnavailable):
        gateway.embed(("hello",), classification=DataClassification.PUBLIC)
    assert adapter.calls == 3


def test_gateway_uses_fallback_after_primary_retries():
    primary = FakeEmbedding(["retry", "retry", "retry"])
    fallback = FakeEmbedding()
    fallback_route = route(ModelTask.EMBEDDING, provider("fallback"))
    gateway = ModelGateway(
        policy(fallback_embedding=fallback_route),
        embedding_adapters={"local-test": primary, "fallback": fallback},
        reranker_adapters={},
    )
    result = gateway.embed(("hello",), classification=DataClassification.PUBLIC)
    assert result.route.provider.provider_id == "fallback"
    assert primary.calls == 3
    assert fallback.calls == 1


def test_gateway_falls_back_after_nonretryable_primary_error():
    primary = FakeEmbedding(["fatal"])
    fallback = FakeEmbedding()
    gateway = ModelGateway(
        policy(fallback_embedding=route(ModelTask.EMBEDDING, provider("fallback"))),
        embedding_adapters={"local-test": primary, "fallback": fallback},
        reranker_adapters={},
    )
    gateway.embed(("hello",), classification=DataClassification.PUBLIC)
    assert primary.calls == 1
    assert fallback.calls == 1


def test_gateway_does_not_retry_fallback():
    fallback = FakeEmbedding(["retry"])
    gateway = ModelGateway(
        policy(fallback_embedding=route(ModelTask.EMBEDDING, provider("fallback"))),
        embedding_adapters={"local-test": FakeEmbedding(["fatal"]), "fallback": fallback},
        reranker_adapters={},
    )
    with pytest.raises(ModelUnavailable):
        gateway.embed(("hello",), classification=DataClassification.PUBLIC)
    assert fallback.calls == 1


def test_gateway_passes_bounded_timeout_to_adapter():
    adapter = FakeEmbedding()
    gateway = ModelGateway(
        policy(), embedding_adapters={"local-test": adapter}, reranker_adapters={}
    )
    gateway.embed(("hello",), classification=DataClassification.PUBLIC)
    assert adapter.timeouts == [60.0]


def test_gateway_reports_missing_adapter():
    gateway = ModelGateway(policy(), embedding_adapters={}, reranker_adapters={})
    with pytest.raises(ModelUnavailable, match="adapter unavailable"):
        gateway.embed(("hello",), classification=DataClassification.PUBLIC)


def test_gateway_reports_unavailable_without_fallback():
    gateway = ModelGateway(
        policy(), embedding_adapters={"local-test": FakeEmbedding(["fatal"])}, reranker_adapters={}
    )
    with pytest.raises(ModelUnavailable):
        gateway.embed(("hello",), classification=DataClassification.PUBLIC)


# Egress and security tests (10)
def test_external_public_egress_requires_explicit_retention_policy():
    external = provider(mode=EgressMode.EXTERNAL, retention=0)
    assert external.allows(DataClassification.PUBLIC)


def test_external_internal_egress_without_dpa_is_denied_by_gateway():
    external = provider(mode=EgressMode.EXTERNAL, retention=0, residency=True)
    gateway = ModelGateway(
        policy(embedding_provider=external), embedding_adapters={"local-test": FakeEmbedding()}, reranker_adapters={}
    )
    with pytest.raises(ModelEgressDenied):
        gateway.embed(("internal",), classification=DataClassification.INTERNAL)


def test_external_internal_egress_without_residency_is_denied_by_gateway():
    external = provider(mode=EgressMode.EXTERNAL, retention=0, dpa=True)
    gateway = ModelGateway(
        policy(embedding_provider=external), embedding_adapters={"local-test": FakeEmbedding()}, reranker_adapters={}
    )
    with pytest.raises(ModelEgressDenied):
        gateway.embed(("internal",), classification=DataClassification.INTERNAL)


def test_fallback_cannot_bypass_internal_egress_policy():
    primary = provider("primary", mode=EgressMode.EXTERNAL, retention=0)
    fallback = provider("fallback", mode=EgressMode.EXTERNAL, retention=0)
    gateway = ModelGateway(
        policy(embedding_provider=primary, fallback_embedding=route(ModelTask.EMBEDDING, fallback)),
        embedding_adapters={"primary": FakeEmbedding(), "fallback": FakeEmbedding()},
        reranker_adapters={},
    )
    with pytest.raises(ModelEgressDenied):
        gateway.embed(("internal",), classification=DataClassification.INTERNAL)


def test_approved_local_fallback_can_handle_internal_data():
    primary = provider("primary", mode=EgressMode.EXTERNAL, retention=0)
    fallback = provider("fallback")
    gateway = ModelGateway(
        policy(embedding_provider=primary, fallback_embedding=route(ModelTask.EMBEDDING, fallback)),
        embedding_adapters={"primary": FakeEmbedding(), "fallback": FakeEmbedding()},
        reranker_adapters={},
    )
    result = gateway.embed(("internal",), classification=DataClassification.INTERNAL)
    assert result.route.provider.provider_id == "fallback"


def test_unknown_classification_is_denied():
    assert not provider().allows("CONFIDENTIAL")  # type: ignore[arg-type]


def test_unapproved_local_provider_is_denied():
    assert not provider(approved=False).allows(DataClassification.PUBLIC)


def test_external_provider_that_allows_training_is_denied():
    external = provider(mode=EgressMode.EXTERNAL, retention=0, training=True)
    assert not external.allows(DataClassification.PUBLIC)


def test_policy_rejects_credential_fields():
    with pytest.raises(ValueError, match="credentials"):
        ModelPolicy.from_mapping(
            {
                "policy_version": "v1",
                "embedding": {
                    "model_id": "m",
                    "revision": "r",
                    "provider": {
                        "provider_id": "p",
                        "egress_mode": "local",
                        "allowed_classifications": ["PUBLIC"],
                        "approved": True,
                        "api_key": "must-not-be-here",
                    },
                },
                "reranker": {
                    "model_id": "m",
                    "revision": "r",
                    "provider": {
                        "provider_id": "p",
                        "egress_mode": "local",
                        "allowed_classifications": ["PUBLIC"],
                        "approved": True,
                    },
                },
            }
        )


def test_denial_error_does_not_echo_model_input():
    external = provider(mode=EgressMode.EXTERNAL, retention=0)
    gateway = ModelGateway(
        policy(embedding_provider=external), embedding_adapters={"local-test": FakeEmbedding()}, reranker_adapters={}
    )
    with pytest.raises(ModelEgressDenied) as error:
        gateway.embed(("secret-company-text",), classification=DataClassification.INTERNAL)
    assert "secret-company-text" not in str(error.value)
