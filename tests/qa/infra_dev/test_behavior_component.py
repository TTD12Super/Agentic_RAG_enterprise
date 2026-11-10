import unittest

from _baseline import COMPOSE, SCRIPT, read


class InfrastructureBehaviorTests(unittest.TestCase):
    def test_development_compose_exists(self):
        self.assertTrue(COMPOSE.is_file())

    def test_migration_script_exists(self):
        self.assertTrue(SCRIPT.is_file())

    def test_only_postgres_service_is_declared(self):
        text = read(COMPOSE)
        self.assertIn("services:\n  postgres:", text)
        self.assertNotIn("  redis:", text)

    def test_uses_postgres_17_alpine(self):
        self.assertIn("image: postgres:17-alpine", read(COMPOSE))

    def test_uses_development_database(self):
        self.assertIn("POSTGRES_DB: enterprise_rag_dev", read(COMPOSE))

    def test_binds_development_port(self):
        self.assertIn('"127.0.0.1:55433:5432"', read(COMPOSE))

    def test_uses_tmpfs_storage(self):
        self.assertIn("tmpfs:", read(COMPOSE))
        self.assertIn("/var/lib/postgresql/data", read(COMPOSE))

    def test_has_healthcheck(self):
        self.assertIn("pg_isready -U enterprise_rag_dev -d enterprise_rag_dev", read(COMPOSE))

    def test_migration_script_accepts_upgrade(self):
        self.assertIn("upgrade)", read(SCRIPT))

    def test_migration_script_accepts_rollback(self):
        self.assertIn("rollback)", read(SCRIPT))


if __name__ == "__main__":
    unittest.main()
