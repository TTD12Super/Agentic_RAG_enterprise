from __future__ import annotations

import unittest

from ._common import read_frontend


class FrontendBehaviorComponentTests(unittest.TestCase):
    def test_app_module_exists_and_exports_component(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn("export function App()", source)

    def test_app_name_drives_heading(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn("<strong>{appConfig.name}</strong>", source)

    def test_hero_has_accessible_label(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn('aria-labelledby="chat-title"', source)
        self.assertIn('<h1 id="chat-title">How can I help today?</h1>', source)

    def test_readiness_is_exposed_as_status(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn('className="processing-row" role="status"', source)
        self.assertIn("Generating an answer from authorized sources", source)

    def test_workspace_has_authorized_chat_heading(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn('<p className="eyebrow">Enterprise knowledge workspace</p>', source)
        self.assertIn('<h1 id="chat-title">How can I help today?</h1>', source)

    def test_workspace_references_contract_api_boundary(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn("The backend enforces identity and source permissions", source)

    def test_boundary_chips_are_all_present(self) -> None:
        source = read_frontend("src/App.tsx")
        for label in (
            "backend enforces identity and source permissions",
            "durable RAG query job",
        ):
            self.assertIn(label, source)

    def test_roles_are_received_from_backend_identity(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertIn("principal?.roles.includes(role)", source)
        self.assertIn("principal?.roles.join(', ')", source)

    def test_role_preview_is_not_client_controlled(self) -> None:
        source = read_frontend("src/App.tsx")
        self.assertNotIn('aria-label="Preview role"', source)
        self.assertIn("No client-side role preview is used.", source)

    def test_root_mount_uses_strict_mode(self) -> None:
        source = read_frontend("src/main.tsx")
        self.assertIn("<StrictMode>", source)
        self.assertIn("<App />", source)
        self.assertIn("document.getElementById('root')", source)


if __name__ == "__main__":
    unittest.main()
