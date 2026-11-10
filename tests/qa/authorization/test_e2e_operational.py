import unittest
from datetime import datetime, timezone
from pathlib import Path

from backend.app.authorization import (
    AuthorizationDenied,
    AuthorizationEvaluator,
    DocumentResource,
    InMemoryPolicyStore,
    PEP,
    PDP,
    PolicyEnforcementPoint,
)
from backend.app.identity.models import AuthenticatedPrincipal


ROOT = Path(__file__).resolve().parents[3]
POLICY = ROOT / "backend" / "app" / "authorization" / "policy.py"


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


def evaluator(store=None, clock=None):
    return AuthorizationEvaluator(
        store or InMemoryPolicyStore(policy_epoch=42), clock=clock
    )


class AuthorizationOperationalTests(unittest.TestCase):
    def test_policy_source_compiles_in_memory(self):
        compile(POLICY.read_text(encoding="utf-8"), str(POLICY), "exec")

    def test_pdp_and_pep_aliases_are_operational_classes(self):
        self.assertIs(PDP, AuthorizationEvaluator)
        self.assertIs(PEP, PolicyEnforcementPoint)

    def test_pep_check_returns_denial_without_raising(self):
        decision = PolicyEnforcementPoint(evaluator()).check(
            principal("chairman"), "document:update", document()
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "CHAIRMAN_READ_ONLY")

    def test_pep_enforce_returns_allowed_decision(self):
        decision = PolicyEnforcementPoint(evaluator()).enforce(
            principal(), "document:read", document()
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.resource_id, "doc-1")

    def test_pep_enforce_preserves_safe_denial_code(self):
        with self.assertRaises(AuthorizationDenied) as raised:
            PolicyEnforcementPoint(evaluator()).enforce(
                principal("employee"),
                "document:read",
                document(classification="INTERNAL", owner_department_id="finance"),
            )
        self.assertEqual(raised.exception.code, "NOT_FOUND_OR_FORBIDDEN")

    def test_fixed_clock_makes_decision_timestamp_deterministic(self):
        fixed = lambda: datetime(2026, 11, 10, 1, 2, 3, tzinfo=timezone.utc)
        decision = evaluator(clock=fixed).evaluate(
            principal(), "document:read", document()
        )
        self.assertEqual(decision.evaluated_at, "2026-11-10T01:02:03Z")

    def test_store_outage_transition_changes_allow_to_deny(self):
        store = InMemoryPolicyStore(policy_epoch=42)
        pdp = evaluator(store)
        self.assertTrue(pdp.evaluate(principal(), "document:read", document()).allowed)
        store.available = False
        decision = pdp.evaluate(principal(), "document:read", document())
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "POLICY_UNAVAILABLE")

    def test_system_admin_can_create_without_document_resource(self):
        decision = evaluator().evaluate(principal("system_admin"), "document:create")
        self.assertTrue(decision.allowed)

    def test_source_download_changes_from_allow_to_deny_on_version_change(self):
        store = InMemoryPolicyStore(policy_epoch=42)
        pdp = evaluator(store)
        current = document()
        self.assertTrue(pdp.evaluate(principal(), "source:download", current).allowed)
        stale = document(current_version_id="v-2", version_id="v-1")
        decision = pdp.evaluate(principal(), "source:download", stale)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, "VERSION_NOT_CURRENT")

    def test_policy_source_has_no_external_service_dependency(self):
        source = POLICY.read_text(encoding="utf-8").lower()
        for forbidden in ("boto3", "requests", "openai", "httpx"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
