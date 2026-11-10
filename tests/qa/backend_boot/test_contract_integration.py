"""Contract and integration-boundary checks for the backend bootstrap."""

import ast
import unittest

from _baseline import (
    CONTRACT_PATH,
    HANDOFF_PATH,
    MAIN_PATH,
    README_PATH,
    ROOT,
    assignment,
    backend_boot_task,
    calls,
    literal,
    pyproject,
    read,
    route_calls,
    route_path,
    tree,
)


class BackendBootstrapContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = read(CONTRACT_PATH)
        cls.handoff = read(HANDOFF_PATH)
        cls.readme = read(README_PATH)
        cls.main_tree = tree(MAIN_PATH)
        cls.project = pyproject()

    def test_public_api_prefix_is_version_one(self) -> None:
        self.assertIn('api_prefix: str = "/api/v1"', read(MAIN_PATH.parent / "core" / "config.py"))
        self.assertIn("/api/v1", self.contract)

    def test_envelope_required_fields_are_documented(self) -> None:
        required = ("message_id", "request_id", "producer", "issued_at", "schema_version", "payload")
        for field in required:
            with self.subTest(field=field):
                self.assertIn(f'"{field}"', self.contract)

    def test_problem_error_shape_is_documented(self) -> None:
        for field in ("code", "safe `message`", "request_id", "retryable"):
            with self.subTest(field=field):
                self.assertIn(field, self.contract)

    def test_versioning_rule_is_additive_within_major_version(self) -> None:
        self.assertIn("Compatibility is additive within major version.", self.contract)
        self.assertIn("A major version change is breaking.", self.contract)

    def test_trace_and_request_correlation_are_distinct(self) -> None:
        self.assertIn("traceparent", self.contract)
        self.assertIn("request_id", self.contract)
        self.assertIn("not a substitute for `traceparent`", self.contract)

    def test_backend_remains_authorization_authority(self) -> None:
        self.assertIn("The LLM NEVER decides authorization", read(ROOT / "AGENTS.md"))
        self.assertIn("The Core creates `AuthenticatedPrincipal`", self.contract)

    def test_bootstrap_exposes_only_one_route(self) -> None:
        routes = route_calls(self.main_tree)
        self.assertEqual(len(routes), 1)
        self.assertEqual(route_path(routes[0]), "/healthz")

    def test_identity_router_is_separate_from_liveness(self) -> None:
        self.assertIn("Feature routes are added by their owning tasks", read(MAIN_PATH))
        self.assertIn("identity_router", read(MAIN_PATH))
        self.assertIn("no feature behavior", backend_boot_task()["acceptance"])

    def test_runtime_dependencies_have_upper_bounds(self) -> None:
        dependencies = self.project["project"]["dependencies"]
        for dependency in ("fastapi>=0.115,<1.0", "pydantic-settings>=2.6,<3.0", "uvicorn>=0.32,<1.0"):
            with self.subTest(dependency=dependency):
                self.assertIn(dependency, dependencies)

    def test_backend_tests_have_declared_http_and_pytest_tools(self) -> None:
        dev_dependencies = self.project["project"]["optional-dependencies"]["dev"]
        self.assertIn("httpx>=0.27,<1.0", dev_dependencies)
        self.assertIn("pytest>=8,<9", dev_dependencies)

if __name__ == "__main__":
    unittest.main()
