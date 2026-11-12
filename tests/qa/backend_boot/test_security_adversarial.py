"""Security/adversarial checks for the dependency-free backend shell."""

import ast
import re
import unittest

from ._baseline import CONFIG_PATH, CONTRACT_PATH, MAIN_PATH, ROOT, read, tree


class BackendBootstrapSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config_text = read(CONFIG_PATH)
        cls.main_tree = tree(MAIN_PATH)
        cls.contract = read(CONTRACT_PATH)

    def test_configuration_has_no_secret_literal_defaults(self) -> None:
        forbidden = re.compile(r"(?i)(sk-[a-z0-9]{16,}|-----begin [^-]+ key-----|password\s*[:=]\s*['\"][^'\"]+)")
        self.assertIsNone(forbidden.search(self.config_text))

    def test_configuration_uses_backend_environment_namespace(self) -> None:
        self.assertIn('env_prefix="BACKEND_"', self.config_text)

    def test_unknown_environment_values_are_not_promoted_to_settings(self) -> None:
        self.assertIn('extra="ignore"', self.config_text)

    def test_healthz_has_no_user_supplied_parameters(self) -> None:
        healthz = next(
            node
            for node in ast.walk(self.main_tree)
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "healthz"
        )
        self.assertEqual(len(healthz.args.args), 0)
        self.assertEqual(len(healthz.args.kwonlyargs), 0)

    def test_healthz_does_not_call_external_services(self) -> None:
        healthz = next(
            node
            for node in ast.walk(self.main_tree)
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "healthz"
        )
        self.assertEqual(
            [node for statement in healthz.body for node in ast.walk(statement) if isinstance(node, ast.Call)],
            [],
        )

    def test_shell_imports_do_not_include_data_or_provider_clients(self) -> None:
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(self.main_tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".")[0]
            for node in ast.walk(self.main_tree)
            if isinstance(node, ast.ImportFrom)
            and node.module
        )
        self.assertTrue(imported.issubset({"fastapi", "api", "core", "identity", "observability"}))

    def test_contract_requires_explicit_deny_to_win(self) -> None:
        self.assertIn("explicit deny", self.contract)
        self.assertIn("overrides every allow", self.contract)

    def test_contract_restricts_anonymous_access_to_public(self) -> None:
        self.assertIn("Anonymous access is PUBLIC-only.", self.contract)

    def test_contract_protects_other_users_conversation_bodies(self) -> None:
        self.assertIn("system_admin` cannot read another user's conversation body", self.contract)
        self.assertIn("audit, support, incident, export, cache or trace views", self.contract)

    def test_checked_in_configuration_example_contains_no_secret_values(self) -> None:
        example = read(ROOT / ".env.example")
        assignments = [line for line in example.splitlines() if line and not line.startswith("#") and "=" in line]
        self.assertTrue(assignments)
        for line in assignments:
            with self.subTest(line=line.split("=", 1)[0]):
                self.assertEqual(line.split("=", 1)[1], "")


if __name__ == "__main__":
    unittest.main()
