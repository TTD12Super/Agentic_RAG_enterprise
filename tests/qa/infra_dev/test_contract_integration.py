import unittest

from ._baseline import HANDOFF, README, RUNBOOK, SCRIPT, task, read


class InfrastructureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = read(SCRIPT)
        cls.handoff = read(HANDOFF)

    def test_runner_uses_backend_alembic_config(self):
        self.assertIn("backend/app/db/alembic.ini", self.script)

    def test_runner_accepts_alembic_override(self):
        self.assertIn("ALEMBIC_BIN", self.script)

    def test_runner_accepts_database_override(self):
        self.assertIn("DB001_DATABASE_URL", self.script)

    def test_runner_defaults_to_synthetic_development_database(self):
        self.assertIn("enterprise_rag_dev", self.script)
        self.assertIn("synthetic_only_not_secret", self.script)

    def test_infra_does_not_define_schema(self):
        self.assertNotIn("CREATE TABLE", self.script)

    def test_backend_owns_migrations(self):
        self.assertIn("Backend owns PostgreSQL schema and migration definitions", read(README))

    def test_handoff_records_upgrade(self):
        self.assertIn("migrate.sh upgrade", self.handoff)

    def test_handoff_records_rollback(self):
        self.assertIn("migrate.sh rollback", self.handoff)

    def test_runbook_distinguishes_local_and_production(self):
        self.assertIn("local development compose", read(RUNBOOK))

    def test_task_uses_compose_validation(self):
        self.assertIn("docker compose config", " ".join(task("INFRA-001")["validation"]))


if __name__ == "__main__":
    unittest.main()
