import subprocess
import sys
import unittest

from _baseline import API, HANDOFF, MAIN, ROOT, task, read


class IdentityOperationalTests(unittest.TestCase):
    def test_identity_sources_compile(self):
        paths = sorted((ROOT / "backend" / "app" / "identity").glob("*.py"))
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", *(str(path) for path in paths)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_api_source_compiles(self):
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(API / "identity.py"), str(MAIN)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_task_is_integration_ready(self):
        self.assertEqual(task("IDENT-001")["status"], "DONE")

    def test_qa_task_depends_on_identity(self):
        self.assertEqual(task("IDENT-QA-001")["depends_on"], ["IDENT-001"])

    def test_task_uses_identity_validation(self):
        self.assertTrue(any("identity" in value for value in task("IDENT-001")["validation"]))

    def test_handoff_lists_sign_in_endpoint(self):
        self.assertIn("POST /api/v1/auth/sign-in", read(HANDOFF))

    def test_handoff_lists_expiry_and_revocation(self):
        handoff = read(HANDOFF)
        self.assertIn("session expiry", handoff)
        self.assertIn("revocation", handoff)

    def test_api_uses_problem_media_type(self):
        self.assertIn("application/problem+json", read(MAIN))

    def test_api_has_no_provider_client(self):
        self.assertNotIn("boto3", read(API / "identity.py"))
        self.assertNotIn("openai", read(API / "identity.py"))

    def test_identity_uses_no_environment_secret(self):
        self.assertNotIn("API_KEY", read(API / "identity.py"))


if __name__ == "__main__":
    unittest.main()
