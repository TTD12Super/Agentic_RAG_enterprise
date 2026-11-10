import unittest

from _baseline import BASELINE_CONTRACT, EVENTS_CONTRACT, HANDOFF, read


class AuditContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = read(EVENTS_CONTRACT)
        cls.baseline = read(BASELINE_CONTRACT)
        cls.handoff = read(HANDOFF)

    def test_event_contract_is_versioned(self):
        self.assertIn("v1.0", self.events)

    def test_event_contract_requires_traceparent(self):
        self.assertIn("traceparent", self.events)

    def test_event_contract_requires_correlation_id(self):
        self.assertIn("correlation ID", self.events)

    def test_event_contract_excludes_raw_prompts(self):
        self.assertIn("Raw prompts", self.events)

    def test_event_contract_excludes_conversation_bodies(self):
        self.assertIn("conversation bodies", self.events)

    def test_baseline_excludes_secrets_from_events(self):
        self.assertIn("secrets", self.baseline)

    def test_baseline_excludes_source_text(self):
        self.assertIn("source text", self.baseline)

    def test_handoff_records_audit_task(self):
        self.assertIn("AUDIT-001", self.handoff)

    def test_handoff_records_provider_neutral_boundary(self):
        self.assertIn("provider-neutral", self.handoff)

    def test_handoff_records_no_cloud_use(self):
        self.assertIn("cloud/provider files", self.handoff)


if __name__ == "__main__":
    unittest.main()
