import unittest

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


def principal(*, user_id="u-1", role="employee", departments=None):
    return AuthenticatedPrincipal(
        user_id=user_id,
        tenant_id="tenant-a",
        roles=[role],
        department_ids=departments or [],
        session_id="session-1",
        auth_time="2026-11-10T00:00:00Z",
    )


def document(*, classification="INTERNAL", department="sales", **overrides):
    values = {
        "document_id": "doc-1",
        "tenant_id": "tenant-a",
        "classification": classification,
        "current_version_id": "v-1",
        "version_id": "v-1",
        "owner_department_id": department,
    }
    values.update(overrides)
    return DocumentResource(**values)


def evaluator(store=None):
    return AuthorizationEvaluator(store or InMemoryPolicyStore(policy_epoch=42))


class AuthorizationBehaviorTests(unittest.TestCase):
    def test_anonymous_can_read_public_document(self):
        decision = evaluator().evaluate(
            AnonymousPrincipal("tenant-a"), "document:read", document(classification="PUBLIC")
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason_code, "PUBLIC_ALLOW")

    def test_anonymous_cannot_read_internal_document(self):
        decision = evaluator().evaluate(
            AnonymousPrincipal("tenant-a"), "document:read", document()
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "ANONYMOUS_PUBLIC_ONLY")

    def test_employee_can_read_assigned_internal_document(self):
        decision = evaluator().evaluate(
            principal(departments=["sales"]), "document:read", document()
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason_code, "RBAC_ALLOW")

    def test_employee_cannot_read_unassigned_internal_document(self):
        decision = evaluator().evaluate(
            principal(departments=["finance"]), "document:read", document()
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "DEPARTMENT_DENY")

    def test_website_manager_can_publish_document(self):
        decision = evaluator().evaluate(
            principal(role="website_manager"), "document:publish", document()
        )
        self.assertTrue(decision.allowed)

    def test_chairman_cannot_publish_document(self):
        decision = evaluator().evaluate(
            principal(role="chairman"), "document:publish", document()
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "CHAIRMAN_READ_ONLY")

    def test_explicit_deny_overrides_chairman_read_role(self):
        resource = document(
            acl=(AccessGrant("document:read", "DENY", role="chairman"),)
        )
        decision = evaluator().evaluate(
            principal(role="chairman"), "document:read", resource
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "EXPLICIT_DENY")

    def test_document_read_requires_current_active_version(self):
        resource = document(current_version_id="v-2", version_id="v-1")
        decision = evaluator().evaluate(principal(), "document:read", resource)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "VERSION_NOT_CURRENT")

    def test_conversation_owner_can_read_own_body(self):
        resource = ConversationResource("conv-1", "tenant-a", "u-1")
        decision = evaluator().evaluate(principal(), "conversation:read", resource)
        self.assertTrue(decision.allowed)

    def test_pep_raises_safe_denial_for_other_conversation(self):
        resource = ConversationResource("conv-2", "tenant-a", "u-2")
        with self.assertRaises(AuthorizationDenied) as raised:
            PolicyEnforcementPoint(evaluator()).enforce(
                principal(), "conversation:read", resource
            )
        self.assertEqual(raised.exception.code, "NOT_FOUND_OR_FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
