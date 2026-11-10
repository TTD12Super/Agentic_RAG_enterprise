from __future__ import annotations

import re
import unittest
from pathlib import Path

from _common import FRONTEND, read, read_frontend


class FrontendSecurityAdversarialTests(unittest.TestCase):
    def test_source_has_no_credential_assignment_patterns(self) -> None:
        source = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*" ) if path.is_file())
        self.assertIsNone(re.search(r"(?i)(api[_-]?key|client[_-]?secret|password|private[_-]?key)\s*[:=]", source))

    def test_public_env_names_cannot_be_secret_names(self) -> None:
        env = read_frontend(".env.example")
        names = re.findall(r"^([A-Z][A-Z0-9_]*)=", env, re.M)
        self.assertEqual(names, ["VITE_APP_NAME", "VITE_API_BASE_URL"])
        self.assertFalse(any(re.search(r"(?i)(key|secret|password|token)", name) for name in names))

    def test_html_contains_no_bearer_or_secret_material(self) -> None:
        html = read_frontend("index.html")
        self.assertIsNone(re.search(r"(?i)(bearer\s|api[_-]?key|client[_-]?secret|password=)", html))

    def test_backend_authorization_is_declared_authoritative(self) -> None:
        source = read_frontend("src/App.tsx")
        readme = read_frontend("README.md")
        self.assertIn("Backend authorization is authoritative", source)
        self.assertIn("Backend services remain responsible for authentication and authorization enforcement", readme)

    def test_shell_has_no_client_grant_or_permission_logic(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIsNone(re.search(r"(?i)(\bgrant\b|\bauthorize\b|hasPermission|canAccess|isAdmin|\bpermissions\b)", source))

    def test_shell_has_no_restricted_payload_fields(self) -> None:
        source = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*" ) if path.is_file())
        for field in ("conversation_body", "raw_prompt", "source_text", "api_key", "access_token"):
            self.assertNotIn(field, source)

    def test_bootstrap_does_not_call_backend_yet(self) -> None:
        source = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*" ) if path.is_file())
        self.assertIsNone(re.search(r"\b(fetch|axios|XMLHttpRequest)\s*[(.]", source))

    def test_streaming_transports_are_absent_from_shell(self) -> None:
        source = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*" ) if path.is_file())
        self.assertIsNone(re.search(r"(?i)\b(SSE|WebSocket|EventSource)\b", source))

    def test_only_approved_import_meta_environment_names_are_read(self) -> None:
        source = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*" ) if path.is_file())
        self.assertEqual(
            sorted(set(re.findall(r"import\.meta\.env\.([A-Z0-9_]+)", source))),
            ["VITE_API_BASE_URL", "VITE_APP_NAME"],
        )

    def test_sensitive_local_environment_files_are_not_part_of_frontend(self) -> None:
        names = {path.name for path in FRONTEND.iterdir() if path.name.startswith(".env")}
        self.assertEqual(names, {".env.example"})
        ignore = read(".gitignore")
        for pattern in (".env", ".env.*", "*.pem", "*.key"):
            self.assertIn(pattern, ignore)


if __name__ == "__main__":
    unittest.main()
