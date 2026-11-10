"""Security/adversarial checks for synthetic denial and poisoning labels."""

import unittest

from _evaluation_harness import load_validated_records


class SecurityAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_validated_records()

    def test_permission_negative_cases_are_access_denied(self):
        for record in self.records:
            if "permission-negative" in record["tags"]:
                self.assertEqual(record["expected_status"], "ACCESS_DENIED", record["case_id"])

    def test_cross_tenant_cases_are_denied(self):
        cases = [record for record in self.records if "cross-tenant" in record["tags"]]
        self.assertTrue(cases)
        self.assertTrue(all(record["expected_status"] == "ACCESS_DENIED" for record in cases))

    def test_explicit_deny_cases_are_denied(self):
        cases = [record for record in self.records if "explicit-deny" in record["tags"]]
        self.assertTrue(cases)
        self.assertTrue(all(record["expected_status"] == "ACCESS_DENIED" for record in cases))

    def test_denied_cases_do_not_expose_expected_sources(self):
        for record in self.records:
            if record["expected_status"] == "ACCESS_DENIED":
                self.assertEqual(record["expected_source_spans"], [], record["case_id"])

    def test_denied_cases_do_not_expose_expected_facts(self):
        for record in self.records:
            if record["expected_status"] == "ACCESS_DENIED":
                self.assertEqual(record["expected_facts"], [], record["case_id"])

    def test_anonymous_cases_are_labeled_public(self):
        cases = [record for record in self.records if record["principal_fixture"] == "anonymous-public"]
        self.assertTrue(cases)
        self.assertTrue(all("public" in record["tags"] for record in cases))

    def test_indirect_injection_cases_allow_read_only_tools_only(self):
        cases = [record for record in self.records if "indirect-injection" in record["tags"] and record["expected_status"] == "ANSWERED"]
        self.assertTrue(cases)
        for record in cases:
            self.assertEqual(record["expected_tool_actions"], ["search_documents", "read_authorized_chunk"])

    def test_version_conflict_cases_never_expect_old_version_delivery(self):
        for record in self.records:
            if "version-conflict" in record["tags"] and record["expected_status"] == "ANSWERED":
                delivered = {span["version_id"] for span in record["expected_source_spans"]}
                self.assertTrue(delivered.isdisjoint(record["expected_forbidden_version_ids"]))

    def test_authorized_sources_never_cross_the_case_tenant(self):
        for record in self.records:
            if record["expected_retrieval_policy"] == "authorized-only":
                self.assertTrue(all(span["tenant_id"] == record["tenant_id"] for span in record["expected_source_spans"]))

    def test_adversarial_categories_are_present(self):
        tags = {tag for record in self.records for tag in record["tags"]}
        for tag in {"permission-negative", "cross-tenant", "explicit-deny", "unanswerable", "safe-against-injection", "conflicting-versions"}:
            self.assertIn(tag, tags)


if __name__ == "__main__":
    unittest.main()
