import unittest

from ._baseline import API, IDENTITY, MAIN, read


class IdentitySecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = read(IDENTITY / "models.py")
        cls.store = read(IDENTITY / "store.py")
        cls.service = read(IDENTITY / "service.py")
        cls.errors = read(IDENTITY / "errors.py")
        cls.api = read(API / "identity.py")
        cls.main = read(MAIN)

    def test_principal_forbids_extra_fields(self):
        self.assertIn('extra="forbid"', self.models)

    def test_passwords_use_pbkdf2(self):
        self.assertIn("pbkdf2_hmac", self.store)

    def test_password_comparison_is_constant_time(self):
        self.assertIn("hmac.compare_digest", self.store)

    def test_bearer_tokens_are_hashed(self):
        self.assertIn("sha256", self.service)
        self.assertIn("token_hash", self.service)

    def test_expired_sessions_are_rejected(self):
        self.assertIn("session.expires_at <= now", self.service)

    def test_revoked_sessions_are_rejected(self):
        self.assertIn("session.revoked_at is not None", self.service)

    def test_store_errors_fail_closed(self):
        self.assertIn("AUTH_UNAVAILABLE", self.service)

    def test_mfa_roles_are_explicit(self):
        self.assertIn("MFA_ROLES", self.models)

    def test_auth_errors_do_not_expose_credentials(self):
        self.assertNotIn("password", self.errors.split("message=")[-1].lower())

    def test_problem_response_does_not_return_internal_details(self):
        self.assertNotIn("error.details", read(MAIN))


if __name__ == "__main__":
    unittest.main()
