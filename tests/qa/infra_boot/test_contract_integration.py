import unittest

from _baseline import compose, compose_config_result, database, handoff, tasks


class DisposablePostgresContractTests(unittest.TestCase):
    def test_service_attaches_to_postgres_test_network(self):
        text = compose()
        self.assertIn("networks:\n      - postgres_test", text)

    def test_declares_postgres_test_network(self):
        self.assertIn("networks:\n  postgres_test:", compose())

    def test_healthcheck_uses_configured_user(self):
        self.assertIn("pg_isready -U enterprise_rag_test", compose())

    def test_healthcheck_uses_configured_database(self):
        self.assertIn("-d enterprise_rag_test", compose())

    def test_healthcheck_interval_is_two_seconds(self):
        self.assertIn("interval: 2s", compose())

    def test_healthcheck_timeout_is_three_seconds(self):
        self.assertIn("timeout: 3s", compose())

    def test_healthcheck_has_fifteen_retries(self):
        self.assertIn("retries: 15", compose())

    def test_container_port_is_postgresql_default(self):
        self.assertIn(":55432:5432", compose())

    def test_compose_config_is_valid(self):
        result = compose_config_result()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_database_contract_keeps_postgres_authoritative_and_records_migrations(self):
        text = database()
        self.assertIn("PostgreSQL is authoritative", text)
        self.assertIn("Alembic migrations implement the authoritative schema", text)
        self.assertIn("Five ordered Alembic revisions", text)
        self.assertIn("| Migration execution | NOT RUN", handoff())
        self.assertIn("| Database migration execution | PASS", text)
        self.assertIn('"INFRA-BOOT-QA-001"', tasks())


if __name__ == "__main__":
    unittest.main()
