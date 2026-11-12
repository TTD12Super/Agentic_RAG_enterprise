import unittest

from ._baseline import BASELINE, CONTRACT, HANDOFF, read


class IdentityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = read(CONTRACT)
        cls.baseline = read(BASELINE)
        cls.handoff = read(HANDOFF)

    def test_authenticated_principal_is_contract_named(self):
        self.assertIn("AuthenticatedPrincipal", self.contract)

    def test_all_canonical_roles_are_documented(self):
        for role in ("system_admin", "website_manager", "employee", "chairman"):
            with self.subTest(role=role):
                self.assertIn(role, self.contract)

    def test_client_cannot_choose_principal_claims(self):
        self.assertIn("client cannot choose tenant, role or group", self.contract)

    def test_pdp_pep_boundary_is_documented(self):
        self.assertIn("PDP", self.contract)
        self.assertIn("PEP", self.contract)

    def test_policy_failure_is_closed(self):
        self.assertIn("Fail closed", self.contract)

    def test_anonymous_access_is_public_only(self):
        self.assertIn("anonymous access is limited to", self.contract)
        self.assertIn("PUBLIC", self.contract)

    def test_explicit_deny_wins(self):
        self.assertIn("Explicit deny overrides role allow", self.contract)

    def test_problem_envelope_has_safe_fields(self):
        for field in ("code", "message", "request_id", "retryable"):
            with self.subTest(field=field):
                self.assertIn(field, self.baseline)

    def test_handoff_records_identity_boundary(self):
        self.assertIn("No default user", self.handoff)

    def test_handoff_is_integration_ready(self):
        self.assertIn("READY_FOR_INTEGRATION", self.handoff)


if __name__ == "__main__":
    unittest.main()
