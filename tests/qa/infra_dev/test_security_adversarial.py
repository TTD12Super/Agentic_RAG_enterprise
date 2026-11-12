import unittest

from ._baseline import COMPOSE, SCRIPT, read


class InfrastructureSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compose = read(COMPOSE)
        cls.script = read(SCRIPT)

    def test_host_binding_is_loopback_only(self):
        self.assertIn("127.0.0.1:55433:5432", self.compose)

    def test_no_host_network_mode(self):
        self.assertNotIn("network_mode: host", self.compose)

    def test_no_privileged_mode(self):
        self.assertNotIn("privileged: true", self.compose)

    def test_no_persistent_volume_is_declared(self):
        self.assertNotIn("volumes:", self.compose)

    def test_no_cloud_provider_is_provisioned(self):
        for provider in ("aws", "azure", "gcp", "oracle"):
            with self.subTest(provider=provider):
                self.assertNotIn(provider, self.compose.lower())

    def test_no_production_url_is_hardcoded(self):
        self.assertNotIn("production", self.script.lower())

    def test_no_broad_destructive_cleanup_exists(self):
        self.assertNotIn("docker system prune", self.script)
        self.assertNotIn("rm -rf", self.script)

    def test_runner_fails_when_alembic_is_missing(self):
        self.assertIn("Alembic executable not found", self.script)

    def test_service_has_no_new_privileges(self):
        self.assertIn("no-new-privileges:true", self.compose)

    def test_service_does_not_expose_api_keys(self):
        self.assertNotIn("API_KEY", self.compose)


if __name__ == "__main__":
    unittest.main()
