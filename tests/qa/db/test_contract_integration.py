import unittest

from _baseline import CONTRACT, DATABASE_DOC, HANDOFF, migration_text, read


class DatabaseBaselineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = migration_text()
        cls.design = read(DATABASE_DOC)
        cls.contract = read(CONTRACT)
        cls.handoff = read(HANDOFF)

    def test_identity_tables_are_migrated(self):
        for table in ("tenants", "users", "tenant_memberships", "roles"):
            with self.subTest(table=table):
                self.assertIn(f"CREATE TABLE {table}", self.schema)

    def test_canonical_roles_are_seeded(self):
        for role in ("system_admin", "website_manager", "employee", "chairman"):
            with self.subTest(role=role):
                self.assertIn(role, self.schema)

    def test_document_head_is_authoritative(self):
        self.assertIn("CREATE TABLE document_heads", self.schema)
        self.assertIn("DOCUMENT_HEADS", self.design)

    def test_document_versions_have_tenant_and_version_uniqueness(self):
        self.assertIn("UNIQUE (tenant_id, document_id, version_number)", self.schema)

    def test_ingestion_and_query_jobs_are_durable(self):
        for table in ("ingestion_jobs", "query_jobs", "agent_execution_steps"):
            with self.subTest(table=table):
                self.assertIn(f"CREATE TABLE {table}", self.schema)

    def test_citations_bind_evidence_snapshot(self):
        self.assertIn("evidence_snapshot_hash", self.schema)
        self.assertIn("evidence snapshot hash", self.contract)

    def test_authorized_scopes_bind_policy_epoch(self):
        self.assertIn("CREATE TABLE authorized_scopes", self.schema)
        self.assertIn("policy_epoch", self.schema)

    def test_outbox_and_watermarks_are_present(self):
        for table in ("outbox_events", "outbox_consumer_watermarks"):
            with self.subTest(table=table):
                self.assertIn(f"CREATE TABLE {table}", self.schema)

    def test_database_design_maps_authoritative_tables(self):
        for name in ("IDEMPOTENCY_KEYS", "AUTHORIZED_SCOPES", "OUTBOX_EVENTS", "REVOCATION_TOMBSTONES"):
            with self.subTest(name=name):
                self.assertIn(name, self.design)

    def test_handoff_records_main_review_boundary(self):
        self.assertIn("READY_FOR_MAIN_REVIEW", self.handoff)
        self.assertIn("DB-QA-001", self.handoff)


if __name__ == "__main__":
    unittest.main()
