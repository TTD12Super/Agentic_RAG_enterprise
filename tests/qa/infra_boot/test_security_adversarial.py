import unittest

from _baseline import compose


class DisposablePostgresSecurityTests(unittest.TestCase):
    def test_host_binding_is_loopback_only(self):
        self.assertIn("127.0.0.1:55432:5432", compose())

    def test_wildcard_host_binding_is_absent(self):
        text = compose()
        self.assertNotIn('"0.0.0.0:', text)
        self.assertNotIn('":::55432:', text)

    def test_persistent_volume_declarations_are_absent(self):
        text = compose()
        self.assertNotIn("volumes:", text)
        self.assertNotIn("source:", text)

    def test_privileged_mode_is_absent(self):
        self.assertNotIn("privileged:", compose())

    def test_host_network_mode_is_absent(self):
        self.assertNotIn("network_mode:", compose())

    def test_no_new_privileges_is_enabled(self):
        self.assertIn("no-new-privileges:true", compose())

    def test_password_is_marked_synthetic_not_secret(self):
        text = compose()
        self.assertIn("synthetic_only_not_secret", text)
        self.assertNotIn("POSTGRES_PASSWORD_FILE", text)

    def test_cloud_account_and_provider_resources_are_absent(self):
        text = compose().lower()
        for marker in ("aws", "gcp", "azure", "arn:", "access_key", "api_key"):
            self.assertNotIn(marker, text)

    def test_secret_and_config_mounts_are_absent(self):
        text = compose()
        self.assertNotIn("secrets:", text)
        self.assertNotIn("configs:", text)
        self.assertNotIn("/run/secrets", text)

    def test_host_data_bind_mounts_are_absent(self):
        text = compose()
        self.assertNotIn("/data/", text)
        self.assertNotIn("/var/lib/postgresql/data:", text)


if __name__ == "__main__":
    unittest.main()
