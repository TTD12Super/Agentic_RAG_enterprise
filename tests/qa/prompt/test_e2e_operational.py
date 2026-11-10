import unittest

from backend.app.orchestration.context import (
    ContextLimitError,
    RetrievedEvidence,
    build_secure_context,
    estimate_tokens,
)


class PromptOperationalTests(unittest.TestCase):
    def test_empty_evidence_produces_a_complete_bounded_context(self):
        context = build_secure_context("Where is the policy?")
        self.assertEqual(len(context.messages), 3)
        self.assertEqual(context.citations, ())
        self.assertIn("<<<UNTRUSTED_RETRIEVED_CONTENT>>>", context.messages[2].content)
        self.assertIn("<<<END_UNTRUSTED_RETRIEVED_CONTENT>>>", context.messages[2].content)

    def test_multiple_evidence_items_keep_order_and_citation_binding(self):
        evidence = (
            RetrievedEvidence("chunk-a", "doc-a", "v1", "first"),
            RetrievedEvidence("chunk-b", "doc-b", "v3", "second"),
        )
        context = build_secure_context("Compare sources", evidence)
        content = context.messages[2].content
        self.assertLess(content.index("<chunk_id>chunk-a"), content.index("<chunk_id>chunk-b"))
        self.assertEqual(context.citations, evidence)

    def test_planner_prompt_can_run_through_the_same_operational_path(self):
        context = build_secure_context("Find the rule", prompt_name="planner")
        self.assertEqual(context.prompt_name, "planner")
        self.assertIn("bounded plan", context.messages[0].content)

    def test_prompt_selection_is_recorded_for_answer_execution(self):
        context = build_secure_context("Answer this", prompt_name="answer", prompt_version="v1")
        self.assertEqual((context.prompt_name, context.prompt_version), ("answer", "v1"))
        self.assertEqual(context.schema_version, "1")

    def test_repeated_operational_assembly_has_identical_wire_output(self):
        evidence = RetrievedEvidence("chunk-1", "doc-1", "v1", "repeatable")
        outputs = [build_secure_context("repeat", [evidence]).as_messages() for _ in range(3)]
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])

    def test_reported_counts_match_rendered_messages(self):
        context = build_secure_context("Count this", [RetrievedEvidence("c", "d", "v", "evidence")])
        self.assertEqual(context.character_count, sum(len(message.content) for message in context.messages))
        self.assertEqual(context.token_count, sum(estimate_tokens(message.content) for message in context.messages))

    def test_operational_query_limit_fails_closed(self):
        with self.assertRaises(ContextLimitError):
            build_secure_context("x" * 11, max_query_chars=10)

    def test_operational_evidence_limit_fails_closed(self):
        evidence = RetrievedEvidence("chunk", "doc", "v1", "x" * 11)
        with self.assertRaises(ContextLimitError):
            build_secure_context("question", [evidence], max_evidence_chars=10)

    def test_invalid_provenance_is_rejected_before_assembly(self):
        with self.assertRaises(ValueError):
            RetrievedEvidence("chunk", "doc", "v1", "body", page_start=3, page_end=2)

    def test_unknown_version_stops_operational_assembly(self):
        with self.assertRaisesRegex(KeyError, "unknown prompt: answer@v2"):
            build_secure_context("question", prompt_version="v2")


if __name__ == "__main__":
    unittest.main()
