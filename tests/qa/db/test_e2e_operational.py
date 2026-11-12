import unittest

from ._baseline import (
    ALEMBIC_INI,
    COMPOSE,
    DATABASE_DOC,
    ENV_PY,
    HANDOFF,
    MIGRATIONS,
    compose_config_result,
    read,
)


class DatabaseBaselineOperationalTests(unittest.TestCase):
    def test_compose_configuration_is_valid(self):
        result = compose_config_result()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_disposable_postgres_compose_exists(self):
        self.assertTrue(COMPOSE.is_file())

    def test_migration_runner_accepts_synthetic_database_env(self):
        text = read(ENV_PY)
        self.assertIn("DB001_DATABASE_URL", text)
        self.assertIn("BACKEND_DATABASE_URL", text)

    def test_empty_database_url_fails_closed(self):
        self.assertIn("raise RuntimeError", read(ENV_PY))

    def test_alembic_url_is_not_hardcoded(self):
        self.assertIn("sqlalchemy.url =", read(ALEMBIC_INI))
        self.assertNotIn("postgresql://", read(ALEMBIC_INI))

    def test_migrations_are_reversible_by_contract(self):
        for path in MIGRATIONS.glob("*.py"):
            with self.subTest(path=path.name):
                self.assertIn("def downgrade()", read(path))

    def test_handoff_records_upgrade_evidence(self):
        self.assertIn("upgrade head", read(HANDOFF))
        self.assertIn("0001 through 0005", read(HANDOFF))

    def test_handoff_records_downgrade_evidence(self):
        self.assertIn("downgrade base", read(HANDOFF))
        self.assertIn("PASS — 0005 through 0001 and base", read(HANDOFF))

    def test_database_design_marks_production_unclaimed(self):
        self.assertIn("Production readiness | NOT CLAIMED", read(DATABASE_DOC))

    def test_database_document_points_to_backend_migrations(self):
        self.assertIn("backend/app/db/migrations/versions", read(DATABASE_DOC))


if __name__ == "__main__":
    unittest.main()
