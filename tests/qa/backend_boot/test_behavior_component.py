"""Behavior/component checks for the minimal backend shell."""

import ast
import unittest

from ._baseline import (
    BACKEND,
    CONFIG_PATH,
    MAIN_PATH,
    assignment,
    calls,
    function,
    literal,
    tree,
)


class BackendBootstrapBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_tree = tree(MAIN_PATH)
        cls.config_tree = tree(CONFIG_PATH)

    def test_backend_package_boundaries_exist(self) -> None:
        self.assertTrue((BACKEND / "__init__.py").is_file())
        self.assertTrue((BACKEND / "app" / "__init__.py").is_file())
        self.assertTrue((BACKEND / "app" / "core" / "__init__.py").is_file())

    def test_fastapi_application_is_created(self) -> None:
        app_assignment = assignment(self.main_tree, "app")
        self.assertIsInstance(app_assignment, ast.Assign)
        self.assertTrue(calls(self.main_tree, "FastAPI"))

    def test_application_title_comes_from_settings(self) -> None:
        fastapi_call = calls(self.main_tree, "FastAPI")[0]
        title = next(keyword for keyword in fastapi_call.keywords if keyword.arg == "title")
        self.assertIsInstance(title.value, ast.Attribute)
        self.assertEqual(title.value.attr, "app_name")

    def test_application_version_is_stable(self) -> None:
        fastapi_call = calls(self.main_tree, "FastAPI")[0]
        version = next(keyword for keyword in fastapi_call.keywords if keyword.arg == "version")
        self.assertEqual(literal(version.value), "0.1.0")

    def test_healthz_is_async(self) -> None:
        healthz = function(self.main_tree, "healthz")
        self.assertIsInstance(healthz, ast.AsyncFunctionDef)

    def test_healthz_has_the_expected_route(self) -> None:
        route = function(self.main_tree, "healthz")
        self.assertEqual(route.name, "healthz")
        route_call = next(call for call in calls(self.main_tree, "get") if call.args)
        self.assertEqual(literal(route_call.args[0]), "/healthz")

    def test_healthz_is_hidden_from_openapi(self) -> None:
        route_call = next(call for call in calls(self.main_tree, "get") if call.args)
        include = next(keyword for keyword in route_call.keywords if keyword.arg == "include_in_schema")
        self.assertIs(literal(include.value), False)

    def test_healthz_returns_exact_liveness_payload(self) -> None:
        healthz = function(self.main_tree, "healthz")
        returns = [node for node in healthz.body if isinstance(node, ast.Return)]
        self.assertEqual(len(returns), 1)
        self.assertEqual(literal(returns[0].value), {"status": "ok"})

    def test_settings_defaults_are_safe_and_local(self) -> None:
        settings_class = next(node for node in self.config_tree.body if isinstance(node, ast.ClassDef) and node.name == "Settings")
        defaults = {
            node.target.id: literal(node.value)
            for node in settings_class.body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
        }
        self.assertEqual(defaults["app_name"], "Enterprise Agentic RAG Backend")
        self.assertEqual(defaults["environment"], "development")
        self.assertEqual(defaults["log_level"], "INFO")
        self.assertEqual(defaults["api_prefix"], "/api/v1")

    def test_settings_are_cached_process_locally(self) -> None:
        cache_decorators = [
            decorator
            for node in self.config_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "get_settings"
            for decorator in node.decorator_list
        ]
        self.assertTrue(
            any(
                isinstance(decorator, ast.Name) and decorator.id == "lru_cache"
                for decorator in cache_decorators
            )
        )


if __name__ == "__main__":
    unittest.main()
