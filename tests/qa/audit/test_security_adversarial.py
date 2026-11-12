import unittest

from ._baseline import AUDIT, CONTEXT, IDENTITY_API, MAIN, read


class AuditSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = read(AUDIT)
        cls.context = read(CONTEXT)
        cls.identity = read(IDENTITY_API)
        cls.main = read(MAIN)

    def test_metadata_uses_an_allowlist(self):
        self.assertIn("SAFE_METADATA_KEYS", self.audit)

    def test_unknown_metadata_is_dropped(self):
        self.assertIn("continue", self.audit)

    def test_password_is_not_an_allowed_metadata_key(self):
        self.assertNotIn('"password"', self.audit)

    def test_authorization_is_not_an_allowed_metadata_key(self):
        self.assertNotIn('"authorization"', self.audit)

    def test_content_fields_are_not_allowed_metadata_keys(self):
        for field in ("prompt", "answer", "document_text", "conversation_body", "query"):
            with self.subTest(field=field):
                self.assertNotIn(f'"{field}"', self.audit)

    def test_identifiers_are_bounded(self):
        self.assertIn("<= 256", self.audit)

    def test_codes_are_bounded(self):
        self.assertIn("<= 64", self.audit)

    def test_request_ids_are_bounded(self):
        self.assertIn("{1,128}", self.context)

    def test_identity_api_does_not_log_request_body(self):
        self.assertNotIn("request.body", self.identity)

    def test_problem_handler_does_not_expose_error_details(self):
        self.assertNotIn("error.details", self.main)


if __name__ == "__main__":
    unittest.main()
