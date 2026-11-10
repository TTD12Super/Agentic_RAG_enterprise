import unittest

from backend.app.authorization import (
    AccessGrant,
    AuthorizationEvaluator,
    DocumentResource,
    InMemoryPolicyStore,
)
from backend.app.identity.models import AuthenticatedPrincipal


def principal(*, tenant_id="tenant-a", role="employee", user_id="u-1"):
    return AuthenticatedPrincipal(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=[role],
        department_ids=["sales"],
        session_id="session-1",
        auth_time="2026-11-10T00:00:00Z",
    )


def document(**overrides):
    values = {
        "document_id": "doc-1",
        "tenant_id": "tenant-a",
        "classification": "PUBLIC",
        "current_version_id": "v-1",
        "version_id": "v-1",
    }
    values.update(overrides)
    return DocumentResource(**values)


def evaluator(store=None):
    return AuthorizationEvaluator(store or InMemoryPolicyStore(policy_epoch=42))


class AuthorizationSecurityAdversarialTests(unittest.TestCase):
    def test_cross_tenant_document_is_denied(self):
        decision = evaluator().evaluate(
            principal(), "document:read", document(tenant_id="tenant-b")
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "TENANT_MISMATCH")

    def test_conflicting_tenant_argument_is_denied(self):
        decision = evaluator().evaluate(
            principal(), "document:read", document(), tenant_id="tenant-b"
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "TENANT_MISMATCH")

    def test_forged_noncanonical_role_is_denied(self):
        forged = AuthenticatedPrincipal.model_construct(
            user_id="u-1",
            tenant_id="tenant-a",
            roles=["admin"],
            groups=[],
            department_ids=[],
            session_id="session-1",
            auth_time="2026-11-10T00:00:00Z",
        )
        decision = evaluator().evaluate(forged, "document:read", document())
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "INVALID_PRINCIPAL")

    def test_unknown_classification_is_denied(self):
        decision = evaluator().evaluate(
            principal(), "document:read", document(classification="RESTRICTED")
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "UNKNOWN_CLASSIFICATION")

    def test_unavailable_policy_store_fails_closed(self):
        store = InMemoryPolicyStore(policy_epoch=42, available=False)
        decision = evaluator(store).evaluate(
            principal(), "document:read", document()
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "POLICY_UNAVAILABLE")

    def test_revoked_principal_is_denied_even_for_public_document(self):
        store = InMemoryPolicyStore(
            policy_epoch=42, revoked_principals={("tenant-a", "u-1")}
        )
        decision = evaluator(store).evaluate(
            principal(), "document:read", document()
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "PRINCIPAL_REVOKED")

    def test_tenant_grant_deny_overrides_role_allow(self):
        store = InMemoryPolicyStore(
            policy_epoch=42,
            grants={
                "tenant-a": (AccessGrant("document:read", "DENY", role="employee"),)
            },
        )
        decision = evaluator(store).evaluate(
            principal(), "document:read", document()
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "EXPLICIT_DENY")

    def test_document_acl_deny_overrides_matching_user_allow(self):
        resource = document(
            acl=(
                AccessGrant("document:read", "ALLOW", user_id="u-1"),
                AccessGrant("document:read", "DENY", user_id="u-1"),
            )
        )
        decision = evaluator().evaluate(principal(), "document:read", resource)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "EXPLICIT_DENY")

    def test_revoked_document_version_is_denied(self):
        decision = evaluator().evaluate(
            principal(), "document:read", document(version_status="REVOKED")
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "VERSION_NOT_CURRENT")

    def test_boolean_policy_epoch_is_not_accepted(self):
        decision = evaluator().evaluate(
            principal(), "document:read", document(), policy_epoch=True
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "POLICY_STALE")


if __name__ == "__main__":
    unittest.main()
