from __future__ import annotations

import json
import re
import unittest

from _common import load_frontend_json, read, read_frontend


class FrontendContractIntegrationTests(unittest.TestCase):
    def test_package_identity_is_private_and_esm(self) -> None:
        package = load_frontend_json("package.json")
        self.assertEqual(package["name"], "enterprise-agentic-rag-frontend")
        self.assertTrue(package["private"])
        self.assertEqual(package["type"], "module")

    def test_required_quality_scripts_are_declared(self) -> None:
        scripts = load_frontend_json("package.json")["scripts"]
        for name in ("dev", "build", "lint", "test", "typecheck"):
            self.assertIn(name, scripts)

    def test_build_script_contains_typecheck_gate(self) -> None:
        scripts = load_frontend_json("package.json")["scripts"]
        self.assertEqual(scripts["build"], "npm run typecheck && vite build")

    def test_lockfile_matches_package_identity(self) -> None:
        package = load_frontend_json("package.json")
        lock = load_frontend_json("package-lock.json")
        root = lock["packages"][""]
        self.assertEqual(lock["lockfileVersion"], 3)
        self.assertEqual(root["name"], package["name"])
        self.assertEqual(root["version"], package["version"])

    def test_public_environment_contract_has_only_two_names(self) -> None:
        lines = [line for line in read_frontend(".env.example").splitlines() if line and not line.startswith("#")]
        names = [line.split("=", 1)[0] for line in lines]
        self.assertEqual(names, ["VITE_APP_NAME", "VITE_API_BASE_URL"])

    def test_api_base_defaults_to_v1(self) -> None:
        source = read_frontend("src/config.ts")
        self.assertIn("import.meta.env.VITE_API_BASE_URL || '/api/v1'", source)

    def test_contract_uses_versioned_rest_base(self) -> None:
        contract = read("docs/contracts/v1-baseline.md")
        self.assertIn("Public APIs use REST/HTTP JSON under `/api/v1`", contract)

    def test_role_identifiers_match_contract_and_boundary(self) -> None:
        app = read_frontend("src/App.tsx")
        contract = read("docs/contracts/v1-baseline.md")
        boundary = read("docs/design/IMPLEMENTATION-BOUNDARY.md")
        for role in ("system_admin", "website_manager", "employee", "chairman"):
            self.assertIn(role, app)
            self.assertIn(role, contract)
            self.assertIn(role, boundary)

    def test_polling_and_maintenance_semantics_are_preserved(self) -> None:
        boundary = read("docs/design/IMPLEMENTATION-BOUNDARY.md")
        contract = read("docs/contracts/v1-baseline.md")
        self.assertIn("durable-job polling", boundary)
        self.assertIn("MAINTENANCE_ACTIVE", boundary)
        self.assertIn("not a job state", boundary)
        self.assertIn("PAUSED", contract)

    def test_citation_and_access_request_boundaries_are_explicit(self) -> None:
        boundary = read("docs/design/IMPLEMENTATION-BOUNDARY.md")
        contract = read("docs/contracts/v1-baseline.md")
        self.assertIn("citation preview and original-file download are separate actions", boundary)
        self.assertIn("POST /api/v1/access-requests", contract)
        self.assertIn("never grants access", contract)


if __name__ == "__main__":
    unittest.main()
