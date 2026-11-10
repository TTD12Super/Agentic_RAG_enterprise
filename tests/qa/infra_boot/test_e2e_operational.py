import unittest

from _baseline import BOOT_HANDOFF, compose, compose_config_result, database, handoff


class DisposablePostgresOperationalTests(unittest.TestCase):
    def test_compose_validation_command_is_reproducible(self):
        result = compose_config_result()
        self.assertEqual(result.args[-1], "--quiet")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_restart_is_not_implicitly_retried(self):
        self.assertIn('restart: "no"', compose())

    def test_healthcheck_has_interval_timeout_and_retry_controls(self):
        text = compose()
        for marker in ("interval: 2s", "timeout: 3s", "retries: 15"):
            self.assertIn(marker, text)

    def test_healthcheck_retry_budget_is_bounded(self):
        self.assertIn("retries: 15", compose())
        self.assertNotIn("retries: 0", compose())

    def test_image_is_explicitly_pinned_to_major_version(self):
        self.assertIn("postgres:17-alpine", compose())
        self.assertNotIn("postgres:latest", compose())

    def test_disposable_storage_supports_safe_project_cleanup(self):
        text = compose()
        self.assertIn("tmpfs:", text)
        self.assertNotIn("volumes:", text)

    def test_boot_handoff_records_exact_startup_commands(self):
        text = handoff()
        self.assertIn("docker compose -f infra/docker/postgres-test.compose.yml", text)
        self.assertIn("up -d --wait", text)
        self.assertIn("pg_isready", text)

    def test_boot_handoff_records_scoped_cleanup_only(self):
        text = handoff()
        self.assertIn("down --remove-orphans", text)
        self.assertIn("Do not run broad", text)
        self.assertIn("docker system prune", text)
        self.assertNotIn("docker system prune -a", text)

    def test_bootstrap_migration_boundary_and_production_provisioning_remain_separate(self):
        text = handoff() + database()
        self.assertIn("| Migration execution | NOT RUN; owned by DB-001", text)
        self.assertIn("| Database migration execution | PASS", text)
        self.assertIn("production resources", text)
        self.assertIn("Production readiness | NOT CLAIMED", text)

    def test_handoff_path_and_disposable_boundary_exist(self):
        self.assertTrue(BOOT_HANDOFF.is_file())
        text = handoff()
        self.assertIn("disposable", text.lower())
        self.assertIn("must never be used for staging or production", text)


if __name__ == "__main__":
    unittest.main()
