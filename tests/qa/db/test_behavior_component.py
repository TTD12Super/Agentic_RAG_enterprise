import unittest

from _baseline import ALEMBIC_INI, DB_APP, ENV_PY, MIGRATIONS, migration_files, migration_text, read


class DatabaseBaselineBehaviorTests(unittest.TestCase):
    def test_database_package_exists(self):
        self.assertTrue((DB_APP / "__init__.py").is_file())

    def test_alembic_configuration_exists(self):
        self.assertTrue(ALEMBIC_INI.is_file())

    def test_migration_script_location_is_backend_owned(self):
        self.assertIn("script_location = backend/app/db/migrations", read(ALEMBIC_INI))

    def test_environment_module_exists(self):
        self.assertTrue(ENV_PY.is_file())

    def test_exactly_five_ordered_revisions_exist(self):
        self.assertEqual([path.stem for path in migration_files()], [
            "0001_identity_tenants", "0002_documents", "0003_jobs_conversations",
            "0004_delivery_policy", "0005_indexes",
        ])

    def test_each_revision_has_upgrade(self):
        for path in migration_files():
            with self.subTest(path=path.name):
                self.assertIn("def upgrade()", read(path))

    def test_each_revision_has_downgrade(self):
        for path in migration_files():
            with self.subTest(path=path.name):
                self.assertIn("def downgrade()", read(path))

    def test_first_revision_is_root(self):
        self.assertIn("down_revision = None", read(migration_files()[0]))

    def test_last_revision_is_index_revision(self):
        self.assertIn('revision = "0005_indexes"', read(migration_files()[-1]))

    def test_migrations_use_alembic_operations(self):
        self.assertIn("from alembic import op", migration_text())


if __name__ == "__main__":
    unittest.main()
