from __future__ import annotations

import subprocess
import time
import unittest
import urllib.error
import urllib.request

from _common import FRONTEND, load_frontend_json, read_frontend, run_frontend


class FrontendE2EOperationalTests(unittest.TestCase):
    def test_node_engine_is_declared_for_reproducible_tooling(self) -> None:
        engines = load_frontend_json("package.json")["engines"]
        self.assertEqual(engines["node"], ">=20.19.0")

    def test_npm_is_available(self) -> None:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout.strip(), r"^\d+\.\d+\.\d+$")

    def test_typecheck_script_passes(self) -> None:
        run_frontend(["npm", "run", "typecheck"])

    def test_lint_script_passes(self) -> None:
        run_frontend(["npm", "run", "lint"])

    def test_component_test_script_passes(self) -> None:
        run_frontend(["npm", "test"])

    def test_production_build_script_passes(self) -> None:
        run_frontend(["npm", "run", "build"])

    def test_build_output_contains_spa_entry_and_title(self) -> None:
        run_frontend(["npm", "run", "build"])
        output = (FRONTEND / "dist/index.html").read_text(encoding="utf-8")
        self.assertIn('<div id="root"></div>', output)
        self.assertIn("Enterprise Agentic RAG", output)
        self.assertIn("/assets/", output)

    def test_build_output_does_not_embed_secret_env_names(self) -> None:
        run_frontend(["npm", "run", "build"])
        output = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "dist").rglob("*") if path.is_file())
        for name in ("VITE_API_KEY", "VITE_SECRET", "VITE_TOKEN", "API_KEY"):
            self.assertNotIn(name, output)

    def test_local_dev_server_serves_the_shell(self) -> None:
        port = "41731"
        process = subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", port],
            cwd=FRONTEND,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        body = ""
        try:
            for _ in range(40):
                if process.poll() is not None:
                    break
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1) as response:
                        body = response.read().decode("utf-8")
                    break
                except (urllib.error.URLError, TimeoutError):
                    time.sleep(0.25)
            self.assertIn("Enterprise Agentic RAG", body)
            self.assertIn('id="root"', body)
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()

    def test_public_env_example_is_suitable_for_local_startup(self) -> None:
        env = read_frontend(".env.example")
        self.assertIn("VITE_APP_NAME=Enterprise Agentic RAG", env)
        self.assertIn("VITE_API_BASE_URL=/api/v1", env)


if __name__ == "__main__":
    unittest.main()
