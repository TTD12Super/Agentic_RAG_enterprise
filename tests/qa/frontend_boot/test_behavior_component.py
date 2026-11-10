from __future__ import annotations

import re
import unittest

from _common import read_frontend


class FrontendBehaviorComponentTests(unittest.TestCase):
    def test_app_module_exists_and_exports_component(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn("export function App()", source)

    def test_app_name_drives_heading(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn("<h1 id=\"app-title\">{appConfig.name}</h1>", source)

    def test_hero_has_accessible_label(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn('aria-labelledby="app-title"', source)

    def test_readiness_is_exposed_as_status(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn('<div className="status" role="status">', source)
        self.assertIn("Frontend baseline ready", source)

    def test_workspace_has_authorized_chat_heading(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn('<h2 id="workspace-title">Authorized knowledge chat</h2>', source)

    def test_workspace_references_contract_api_boundary(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn("approved <code>/api/v1</code> contracts", source)

    def test_boundary_chips_are_all_present(self) -> None:
        source = read_frontend("src/App.tsx")
        for label in (
            "Backend authorization is authoritative",
            "Durable-job polling",
            "No token streaming in MVP",
        ):
            self.assertIn(label, source)

    def test_canonical_role_tuple_is_exact(self) -> None:
        source = read_frontend("src/App.tsx")
        match = re.search(r"const supportedRoles = \[(.*?)\] as const", source, re.S)
        self.assertIsNotNone(match)
        self.assertEqual(
            re.findall(r"'([^']+)'", match.group(1)),
            ["system_admin", "website_manager", "employee", "chairman"],
        )

    def test_role_chips_use_stable_role_keys(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn("supportedRoles.map((role) =>", source)
        self.assertIn('key={role}', source)
        self.assertIn('className="role-chip"', source)

    def test_root_mount_uses_strict_mode(self) -> None:
        source = read_frontend("src/main.tsx")
        self.assertIn("<StrictMode>", source)
        self.assertIn("<App />", source)
        self.assertIn("document.getElementById('root')", source)


if __name__ == "__main__":
    unittest.main()
