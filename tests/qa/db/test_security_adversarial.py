import re
import unittest

from _baseline import CONTRACT, DATABASE_DOC, migration_text, read


class DatabaseBaselineSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = migration_text()
        cls.design = read(DATABASE_DOC)
        cls.contract = read(CONTRACT)

    def test_document_sources_are_private_uris(self):
        self.assertIn("source_uri LIKE 'private://%'", self.schema)

    def test_child_relations_use_tenant_composite_foreign_keys(self):
        self.assertGreaterEqual(self.schema.count("FOREIGN KEY (tenant_id,"), 10)

    def test_anonymous_sessions_are_tenant_unique(self):
        self.assertIn("UNIQUE (tenant_id, session_hash)", self.schema)

    def test_feedback_requires_one_actor_kind(self):
        self.assertIn("membership_id IS NOT NULL", self.schema)
        self.assertIn("anonymous_session_hash IS NOT NULL", self.schema)

    def test_worker_replay_nonce_is_unique(self):
        self.assertIn("CREATE TABLE worker_replay_nonces", self.schema)
        self.assertIn("worker_jti_hash text NOT NULL UNIQUE", self.schema)

    def test_authorized_scope_has_expiry_and_revocation(self):
        self.assertIn("expires_at", self.schema)
        self.assertIn("revoked_at", self.schema)

    def test_document_classification_is_bounded(self):
        self.assertIn("classification IN ('PUBLIC', 'INTERNAL')", self.schema)

    def test_migrations_do_not_contain_private_key_material(self):
        self.assertIsNone(re.search(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----", self.schema))

    def test_contract_keeps_llm_out_of_authorization(self):
        self.assertIn("LLM arguments cannot grant access", self.contract)
        self.assertIn("explicit deny", self.contract.lower())

    def test_design_requires_application_policy_enforcement(self):
        self.assertIn("PDP/PEP", self.design)
        self.assertIn("application enforcement is mandatory", self.design)


if __name__ == "__main__":
    unittest.main()
