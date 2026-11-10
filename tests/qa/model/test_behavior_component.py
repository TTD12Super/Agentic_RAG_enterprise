"""MODEL-001 behavior/component QA: 12 deterministic synthetic cases."""

import pytest

from backend.app.models.adapters import EmbeddingRequest, EmbeddingResult
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelTask,
)

from tests.qa.model._baseline import policy, provider, route


def test_policy_version_is_required():
    with pytest.raises(ValueError):
        ModelPolicy(policy_version="", embedding=route(ModelTask.EMBEDDING), reranker=route(ModelTask.RERANKER))


def test_provider_id_is_required():
    with pytest.raises(ValueError):
        provider("")


def test_provider_allowlist_is_required():
    with pytest.raises(ValueError):
        provider(allowed=frozenset())


def test_external_unapproved_provider_is_denied():
    assert not provider(mode=EgressMode.EXTERNAL, approved=False, retention=0).allows(DataClassification.PUBLIC)


def test_external_provider_requires_retention_policy():
    assert not provider(mode=EgressMode.EXTERNAL, retention=None).allows(DataClassification.PUBLIC)


def test_external_internal_requires_dpa():
    assert not provider(mode=EgressMode.EXTERNAL, residency=True, retention=0).allows(DataClassification.INTERNAL)


def test_external_internal_requires_residency():
    assert not provider(mode=EgressMode.EXTERNAL, dpa=True, retention=0).allows(DataClassification.INTERNAL)


def test_timeout_cannot_exceed_sixty_seconds():
    with pytest.raises(ValueError):
        policy(timeout=60.1)


def test_primary_retries_cannot_exceed_two():
    with pytest.raises(ValueError):
        policy(retries=3)


def test_embedding_route_task_is_checked():
    with pytest.raises(ValueError):
        ModelPolicy(
            policy_version="v1",
            embedding=route(ModelTask.RERANKER),
            reranker=route(ModelTask.RERANKER),
        )
