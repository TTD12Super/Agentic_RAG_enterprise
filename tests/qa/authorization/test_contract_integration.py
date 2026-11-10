import unittest
from pathlib import Path

from backend.app.authorization import (
    ACTIONS,
    Action,
    AuthorizationEvaluator,
    ConversationResource,
    DocumentResource,
    InMemoryPolicyStore,
    PEP,
    PDP,
    PolicyEnforcementPoint,
)
from backend.app.identity.models import AuthenticatedPrincipal


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = (ROOT / "docs" / "contracts" / "identity-and-policy.md").read_text(
    encoding="utf-8"
)
MATRIX = (ROOT / "docs" / "security" / "authorization-matrix.md").read_text(
    encoding="utf-8"
)


def principal(role="employee"):
    return AuthenticatedPrincipal(
        user_id="u-1",
        tenant_id="tenant-a",
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


def evaluator(epoch=42):
    return AuthorizationEvaluator(InMemoryPolicyStore(policy_epoch=epoch))


class AuthorizationContractIntegrationTests(unittest.TestCase):
    def test_contract_lists_every_canonical_action(self):
        for action in sorted(ACTIONS):
            with self.subTest(action=action):
                self.assertIn(action, CONTRACT)

    def test_contract_lists_every_canonical_role(self):
        for role in ("system_admin", "website_manager", "employee", "chairman"):
            with self.subTest(role=role):
                self.assertIn(role, CONTRACT)

    def test_matrix_documents_default_deny_and_explicit_deny_precedence(self):
        self.assertIn("default deny", CONTRACT)
        self.assertIn("Explicit deny overrides role allow", CONTRACT)
        self.assertIn("Anonymous", MATRIX)

    def test_authorization_package_exports_pdp_and_pep_aliases(self):
        self.assertIs(PDP, AuthorizationEvaluator)
        self.assertIs(PEP, PolicyEnforcementPoint)

    def test_policy_decision_exposes_contract_envelope_fields(self):
        decision = evaluator().evaluate(principal(), Action.DOCUMENT_READ, document())
        self.assertEqual(
            set(vars(decision)),
            {
                "decision",
                "principal_id",
                "resource_type",
                "resource_id",
                "action",
                "policy_epoch",
                "reason_code",
                "evaluated_at",
            },
        )

    def test_allowed_decision_reports_current_policy_epoch(self):
        decision = evaluator().evaluate(principal(), "document:read", document())
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.policy_epoch, 42)

    def test_requested_stale_policy_epoch_is_denied(self):
        decision = evaluator().evaluate(
            principal(), "document:read", document(), policy_epoch=41
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "POLICY_STALE")

    def test_source_download_obeys_current_document_version(self):
        stale = document(current_version_id="v-2", version_id="v-1")
        decision = evaluator().evaluate(principal(), "source:download", stale)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "VERSION_NOT_CURRENT")

    def test_tool_execution_is_allowed_only_to_employee_role(self):
        employee = evaluator().evaluate(principal("employee"), "tool:execute")
        chairman = evaluator().evaluate(principal("chairman"), "tool:execute")
        self.assertTrue(employee.allowed)
        self.assertFalse(chairman.allowed)

    def test_contract_requires_server_issued_opaque_retrieval_scope(self):
        self.assertIn("server-issued, opaque `AuthorizedScope`", CONTRACT)
        self.assertIn("never accept an arbitrary `allowed_document_ids`", CONTRACT)


if __name__ == "__main__":
    unittest.main()
