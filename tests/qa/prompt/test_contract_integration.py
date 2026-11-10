import json
import unittest
from inspect import signature
from pathlib import Path

from backend.app.orchestration.context import RetrievedEvidence, SecureContextBuilder, build_secure_context
from backend.app.prompts.registry import DEFAULT_PROMPT_REGISTRY


ROOT = Path(__file__).resolve().parents[3]


class PromptContractIntegrationTests(unittest.TestCase):
    def test_task_registry_defines_prompt_acceptance_and_handoff(self):
        task = next(item for item in json.loads((ROOT / "harness/tasks/tasks.json").read_text())["tasks"] if item["id"] == "PROMPT-001")
        self.assertIn("Context assembly preserves provenance", task["acceptance"])
        self.assertEqual(task["handoff"], "harness/handoffs/PROMPT-001.md")

    def test_prompt_metadata_points_to_existing_governed_sources(self):
        for prompt in DEFAULT_PROMPT_REGISTRY.definitions:
            source = ROOT / prompt.metadata["source"]
            self.assertTrue(source.is_file(), source)
            self.assertIn(prompt.version, source.read_text(encoding="utf-8"))

    def test_registry_exposes_the_contract_prompt_set(self):
        self.assertEqual(DEFAULT_PROMPT_REGISTRY.versions("system"), ("v1",))
        self.assertEqual(DEFAULT_PROMPT_REGISTRY.versions("planner"), ("v1",))
        self.assertEqual(DEFAULT_PROMPT_REGISTRY.versions("answer"), ("v1",))

    def test_prompt_input_schema_is_strict_and_versioned(self):
        for prompt in DEFAULT_PROMPT_REGISTRY.definitions:
            self.assertEqual(prompt.schema["type"], "object")
            self.assertEqual(prompt.schema["required"], ("user_query", "evidence"))
            self.assertEqual(prompt.schema["properties"]["user_query"]["type"], "string")
            self.assertEqual(prompt.schema["properties"]["evidence"]["type"], "array")

    def test_unknown_prompt_version_is_rejected(self):
        with self.assertRaisesRegex(KeyError, "unknown prompt: answer@v9"):
            DEFAULT_PROMPT_REGISTRY.get("answer", "v9")

    def test_context_records_prompt_and_schema_versions(self):
        context = build_secure_context("Question", prompt_name="planner", prompt_version="v1")
        self.assertEqual((context.prompt_name, context.prompt_version, context.schema_version), ("planner", "v1", "1"))

    def test_context_wire_messages_are_role_content_objects(self):
        context = build_secure_context("Question")
        self.assertEqual(set(context.as_messages()[0]), {"role", "content"})
        self.assertTrue(all(set(message) == {"role", "content"} for message in context.as_messages()))

    def test_provenance_metadata_excludes_evidence_text(self):
        evidence = RetrievedEvidence("chunk-1", "doc-1", "v1", "private body", source_span=(0, 4))
        provenance = evidence.provenance()
        self.assertNotIn("text", provenance)
        self.assertNotIn(evidence.text, provenance.values())
        self.assertEqual(provenance["source_span"], (0, 4))

    def test_contracts_require_untrusted_context_and_source_spans(self):
        prompt_doc = (ROOT / "docs/architecture/blocks/07-prompt-management.md").read_text(encoding="utf-8")
        retrieval_doc = (ROOT / "docs/contracts/retrieval.md").read_text(encoding="utf-8")
        self.assertIn("untrusted data", prompt_doc)
        self.assertIn("source_span", retrieval_doc)
        self.assertIn("Revalidate each chunk/document", retrieval_doc)

    def test_builder_does_not_accept_history_or_authorization_inputs(self):
        parameters = set(signature(SecureContextBuilder.build).parameters)
        self.assertNotIn("conversation_history", parameters)
        self.assertNotIn("authorized_scope_ref", parameters)
        self.assertNotIn("principal", parameters)


if __name__ == "__main__":
    unittest.main()
