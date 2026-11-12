import unittest

from ._baseline import compose


class DisposablePostgresBehaviorTests(unittest.TestCase):
    def test_declares_only_postgres_service(self):
        text = compose()
        self.assertIn("services:\n  postgres:", text)
        self.assertNotIn("  redis:", text)

    def test_uses_postgres_17_alpine_image(self):
        self.assertIn("image: postgres:17-alpine", compose())

    def test_declares_synthetic_database_name(self):
        self.assertIn("POSTGRES_DB: enterprise_rag_test", compose())

    def test_declares_synthetic_database_user(self):
        self.assertIn("POSTGRES_USER: enterprise_rag_test", compose())

    def test_declares_disposable_password_marker(self):
        self.assertIn("POSTGRES_PASSWORD: synthetic_only_not_secret", compose())

    def test_publishes_expected_postgres_port(self):
        self.assertIn('"127.0.0.1:55432:5432"', compose())

    def test_uses_postgres_data_tmpfs(self):
        self.assertIn("/var/lib/postgresql/data", compose())
        self.assertIn("tmpfs:", compose())

    def test_sets_shared_memory_size(self):
        self.assertIn("shm_size: 128m", compose())

    def test_disables_restart_policy(self):
        self.assertIn('restart: "no"', compose())

    def test_declares_pg_isready_healthcheck(self):
        text = compose()
        self.assertIn("healthcheck:", text)
        self.assertIn("pg_isready -U enterprise_rag_test -d enterprise_rag_test", text)


if __name__ == "__main__":
    unittest.main()
