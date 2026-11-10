"""Behavior/component invariants represented by the v1 baseline."""

import re
import unittest

from _baseline import BASELINE, json_blocks, require_all, section


class BehaviorComponentTests(unittest.TestCase):
    def test_behavior_baseline_is_approved_mvp_profile(self):
        require_all(self, BASELINE, "Status:** `APPROVED`", "Scope:", "public API")

    def test_behavior_common_envelope_has_required_identity_fields(self):
        envelope = json_blocks(section(1))[0]
        for field in ("contract_name", "schema_version", "message_id", "request_id", "producer", "issued_at", "expires_at", "payload"):
            self.assertIn(field, envelope)

    def test_behavior_timestamps_use_utc_rfc3339_z(self):
        envelope_text = section(1)
        self.assertRegex(envelope_text, r'"issued_at":\s*"[^" ]+Z"')
        self.assertRegex(envelope_text, r'"expires_at":\s*"[^" ]+Z"')
        self.assertIn("UTC RFC 3339 with `Z`", envelope_text)

    def test_behavior_schema_evolution_is_additive_within_major_version(self):
        require_all(self, section(1), "A major version change is breaking", "fields may be added as optional", "reject unknown required semantics")

    def test_behavior_problem_details_shape_is_safe(self):
        require_all(self, section(1), "application/problem+json", "`code`", "safe `message`", "`request_id`", "redacted `details`", "`retryable`")
        self.assertIn("No stack traces, secrets, source text or private paths", section(1))

    def test_behavior_authorization_order_is_explicit(self):
        policy = section(2)
        ordered = [
            "Validate principal, session and tenant binding.",
            "Validate resource classification and current lifecycle state.",
            "Apply RBAC and department membership.",
            "Apply document-level ACL.",
            "Apply explicit deny; any matching deny overrides every allow.",
            "Require the current ACTIVE document version and current policy epoch.",
        ]
        positions = [policy.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_behavior_anonymous_and_role_boundaries_are_present(self):
        require_all(self, section(2), "Anonymous access is PUBLIC-only", "`chairman` is a broad read allow only", "`website_manager` has website-management powers but no code/system powers")

    def test_behavior_citation_locator_is_discriminated_by_file_type(self):
        retrieval = section(4)
        require_all(self, retrieval, '"kind":"PDF"', '"kind":"DOCX"', '"kind":"XLSX"', "source locator")
        self.assertEqual(len(re.findall(r'"kind":"(?:PDF|DOCX|XLSX)"', retrieval)), 3)

    def test_behavior_job_states_and_maintenance_are_separate(self):
        jobs = section(6)
        require_all(self, jobs, "`job_state` is one of", "`QUEUED`", "`RUNNING`", "`PAUSED`", "`RETRY_SCHEDULED`", "`COMPLETED`", "`FAILED`", "`CANCELLED`", "Maintenance is a system mode, not a job state")
        self.assertNotIn("`MAINTENANCE_ACTIVE` is a job state", jobs)

    def test_behavior_mvp_tool_allowlist_and_budgets_are_bounded(self):
        tools = section(8)
        require_all(self, tools, "exactly `search_documents`, `read_authorized_chunk` and `get_document_metadata`", "at most two retrieval rounds total", "four subqueries total", "eight tool calls total")


if __name__ == "__main__":
    unittest.main()
