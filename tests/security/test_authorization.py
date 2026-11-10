from datetime import datetime, timezone

import pytest

from backend.app.authorization import (
    AccessGrant,
    AnonymousPrincipal,
    AuthorizationDenied,
    AuthorizationEvaluator,
    ConversationResource,
    DocumentResource,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.identity.models import AuthenticatedPrincipal


def principal(
    *,
    user_id: str = "u-1",
    tenant_id: str = "tenant-a",
    role: str = "employee",
    departments: list[str] | None = None,
) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=[role],
        department_ids=departments or [],
        session_id="session-1",
        auth_time="2026-11-10T00:00:00Z",
    )


def document(
    *,
    tenant_id: str = "tenant-a",
    classification: str = "INTERNAL",
    department: str | None = "sales",
    version_status: str = "ACTIVE",
    acl: tuple[AccessGrant, ...] = (),
    policy_epoch: int | None = None,
) -> DocumentResource:
    return DocumentResource(
        document_id="doc-1",
        tenant_id=tenant_id,
        classification=classification,
        current_version_id="v-1",
        version_id="v-1",
        version_status=version_status,
        owner_department_id=department,
        acl=acl,
        policy_epoch=policy_epoch,
    )


def evaluator(store: InMemoryPolicyStore | None = None) -> AuthorizationEvaluator:
    return AuthorizationEvaluator(store or InMemoryPolicyStore(policy_epoch=42))


def test_employee_reads_public_and_assigned_internal_documents():
    pdp = evaluator()

    assert pdp.evaluate(principal(), "document:read", document(classification="PUBLIC")).allowed
    assert pdp.evaluate(
        principal(departments=["sales"]), "document:read", document()
    ).allowed


def test_employee_without_department_is_denied_internal_document():
    decision = evaluator().evaluate(
        principal(departments=["finance"]), "document:read", document()
    )

    assert not decision.allowed
    assert decision.reason_code == "DEPARTMENT_DENY"


def test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman():
    assigned = document(
        department="finance",
        acl=(AccessGrant("document:read", "ALLOW", user_id="u-1"),),
    )
    assert evaluator().evaluate(principal(), "document:read", assigned).reason_code == "ACL_ALLOW"

    denied = document(
        acl=(AccessGrant("document:read", "DENY", role="chairman"),),
    )
    decision = evaluator().evaluate(
        principal(role="chairman"), "document:read", denied
    )
    assert not decision.allowed
    assert decision.reason_code == "EXPLICIT_DENY"


def test_chairman_is_read_only():
    decision = evaluator().evaluate(
        principal(role="chairman"), "document:update", document()
    )

    assert not decision.allowed
    assert decision.reason_code == "CHAIRMAN_READ_ONLY"


def test_anonymous_is_public_only():
    pdp = evaluator()

    assert pdp.evaluate(AnonymousPrincipal("tenant-a"), "document:read", document(classification="PUBLIC")).allowed
    decision = pdp.evaluate(AnonymousPrincipal("tenant-a"), "document:read", document())
    assert not decision.allowed
    assert decision.reason_code == "ANONYMOUS_PUBLIC_ONLY"


def test_tenant_mismatch_is_denied_without_resource_existence_detail():
    decision = evaluator().evaluate(
        principal(), "document:read", document(tenant_id="tenant-b")
    )

    assert not decision.allowed
    assert decision.reason_code == "TENANT_MISMATCH"


def test_stale_policy_and_non_active_version_are_denied():
    pdp = evaluator()

    stale = pdp.evaluate(principal(), "document:read", document(policy_epoch=41))
    revoked = pdp.evaluate(
        principal(), "document:read", document(version_status="REVOKED")
    )

    assert stale.reason_code == "POLICY_STALE"
    assert revoked.reason_code == "VERSION_NOT_CURRENT"


def test_revoked_principal_is_denied():
    store = InMemoryPolicyStore(
        policy_epoch=42,
        revoked_principals={("tenant-a", "u-1")},
    )

    decision = evaluator(store).evaluate(
        principal(), "document:read", document(classification="PUBLIC")
    )

    assert not decision.allowed
    assert decision.reason_code == "PRINCIPAL_REVOKED"


def test_policy_store_outage_fails_closed_and_pep_raises_safe_denial():
    store = InMemoryPolicyStore(policy_epoch=42, available=False)
    pdp = evaluator(store)
    decision = pdp.evaluate(
        principal(), "document:read", document(classification="PUBLIC")
    )
    assert not decision.allowed
    assert decision.reason_code == "POLICY_UNAVAILABLE"

    with pytest.raises(AuthorizationDenied) as error:
        PolicyEnforcementPoint(pdp).enforce(
            principal(), "document:read", document(classification="PUBLIC")
        )
    assert error.value.code == "NOT_FOUND_OR_FORBIDDEN"


def test_unknown_classification_and_noncanonical_principal_are_denied():
    unknown = evaluator().evaluate(
        principal(), "document:read", document(classification="CONFIDENTIAL")
    )
    malformed = AuthenticatedPrincipal.model_construct(
        user_id="u-1",
        tenant_id="tenant-a",
        roles=["admin"],
        groups=[],
        department_ids=[],
        session_id="session-1",
        auth_time="2026-11-10T00:00:00Z",
    )
    invalid = evaluator().evaluate(malformed, "document:read", document(classification="PUBLIC"))

    assert unknown.reason_code == "UNKNOWN_CLASSIFICATION"
    assert invalid.reason_code == "INVALID_PRINCIPAL"


def test_conversation_body_is_owner_only():
    pdp = evaluator()
    own = ConversationResource("conv-1", "tenant-a", "u-1")
    other = ConversationResource("conv-2", "tenant-a", "u-2")

    assert pdp.evaluate(principal(), "conversation:read", own).allowed
    decision = pdp.evaluate(principal(), "conversation:read", other)
    assert not decision.allowed
    assert decision.reason_code == "OWNER_ONLY"


def test_conversation_requires_conversation_resource():
    decision = evaluator().evaluate(principal(), "conversation:read")

    assert not decision.allowed
    assert decision.reason_code == "RESOURCE_REQUIRED"
