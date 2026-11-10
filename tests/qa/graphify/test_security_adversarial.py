import unittest

from _baseline import IGNORE, ROOT, RUNBOOK, SCRIPT, read


class GraphifySecurityTests(unittest.TestCase):
    def test_env_files_are_ignored(self): self.assertIn(".env", read(IGNORE))
    def test_example_env_remains_allowed(self): self.assertIn("!.env.example", read(IGNORE))
    def test_private_data_is_ignored(self): self.assertIn("data/private/", read(IGNORE))
    def test_raw_uploads_are_ignored(self):
        content = read(IGNORE); self.assertIn("data/raw/", content); self.assertIn("data/uploads/", content)
    def test_export_data_is_ignored(self): self.assertIn("data/exports/", read(IGNORE))
    def test_keys_are_ignored(self):
        content = read(IGNORE); self.assertIn("*.pem", content); self.assertIn("*.key", content)
    def test_graph_output_is_not_tracked(self): self.assertIn("/graphify-out/", read(ROOT / ".gitignore"))
    def test_runbook_rejects_private_inputs(self): self.assertIn("Do not place", read(RUNBOOK))
    def test_runbook_does_not_request_api_key_for_code(self): self.assertIn("needs no API key", read(RUNBOOK))
    def test_sync_script_has_failure_exit(self): self.assertIn("GRAPH_SYNC_FAILED", read(SCRIPT))


if __name__ == "__main__": unittest.main()
