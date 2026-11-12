"""E2E/operational readiness checks without external services or real data."""

from pathlib import Path
import subprocess
import unittest

from ._baseline import (
    BACKEND,
    CONFIG_PATH,
    HANDOFF_PATH,
    MAIN_PATH,
    README_PATH,
    ROOT,
    backend_boot_task,
    compile_sources_without_writes,
    read,
    route_calls,
    route_path,
    tree,
)


class BackendBootstrapOperationalTests(unittest.TestCase):
    def test_all_backend_python_sources_compile_in_child_process(self) -> None:
        sources = sorted(BACKEND.rglob("*.py"))
        result = compile_sources_without_writes(sources)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"compiled {len(sources)} files", result.stdout)

    def test_compile_probe_runs_from_repository_root(self) -> None:
        result = compile_sources_without_writes([MAIN_PATH, CONFIG_PATH])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_health_endpoint_is_liveness_only(self) -> None:
        self.assertIn("process liveness", read(MAIN_PATH))
        self.assertIn("without querying external dependencies", read(MAIN_PATH))

    def test_health_endpoint_is_not_a_readiness_claim(self) -> None:
        self.assertIn("readiness and dependency health belong to the infrastructure/operations task", read(HANDOFF_PATH))

    def test_local_setup_uses_a_virtual_environment(self) -> None:
        readme = read(README_PATH)
        self.assertIn("python3 -m venv backend/.venv", readme)
        self.assertIn("backend/.venv/bin/python -m pip install -e 'backend[dev]'", readme)

    def test_local_validation_commands_are_documented(self) -> None:
        readme = read(README_PATH)
        self.assertIn("backend/.venv/bin/python -m compileall backend", readme)
        self.assertIn("backend/.venv/bin/python -m pytest backend/tests", readme)

    def test_shell_has_no_external_service_configuration_requirement(self) -> None:
        readme = read(README_PATH)
        for service in ("PostgreSQL", "Qdrant", "Redis", "object storage", "LLM"):
            with self.subTest(service=service):
                self.assertIn(service, readme)
        self.assertIn("without contacting", readme)

    def test_route_inventory_is_stable_for_the_bootstrap(self) -> None:
        routes = route_calls(tree(MAIN_PATH))
        self.assertEqual([route_path(route) for route in routes], ["/healthz"])

    def test_task_validation_command_matches_requested_qa_command(self) -> None:
        validation = backend_boot_task()["validation"]
        self.assertIn("python -m compileall backend", validation)
        self.assertIn("python -m pytest backend/tests", validation)

    def test_bootstrap_handoff_records_runtime_deferral_and_no_delivery(self) -> None:
        handoff = read(HANDOFF_PATH)
        self.assertIn("all feature routes remain unimplemented", handoff)
        self.assertIn("No commit or push was made by this agent", handoff)
        self.assertTrue(Path(ROOT / "backend").is_dir())


if __name__ == "__main__":
    unittest.main()
