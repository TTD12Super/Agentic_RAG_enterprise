"""Behavior/component checks for the synthetic evaluation fixture."""

import unittest

from tests.evaluation._evaluation_harness import ALLOWED_STATUSES, load_validated_records


class BehaviorComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_validated_records()

    def test_dataset_has_at_least_200_records(self):
        self.assertGreaterEqual(len(self.records), 200)

    def test_case_ids_are_unique_and_stable(self):
        ids = [record["case_id"] for record in self.records]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[0], "case-001")
        self.assertEqual(ids[-1], "case-200")

    def test_required_schema_fields_exist_on_every_record(self):
        required = {"case_id", "query", "principal_fixture", "tenant_id", "expected_source_spans", "expected_status", "expected_facts", "tags"}
        for record in self.records:
            self.assertTrue(required <= record.keys(), record["case_id"])

    def test_statuses_use_answer_contract_values(self):
        for record in self.records:
            self.assertIn(record["expected_status"], ALLOWED_STATUSES)

    def test_source_spans_have_supported_file_locators(self):
        kinds = {span["kind"] for record in self.records for span in record["expected_source_spans"]}
        self.assertEqual(kinds, {"PDF", "DOCX", "XLSX"})

    def test_language_mix_matches_owner_dataset_composition(self):
        self.assertEqual(sum(record["language"] == "vi" for record in self.records), 140)
        self.assertEqual(sum(record["language"] == "en" for record in self.records), 60)

    def test_complexity_mix_matches_owner_dataset_composition(self):
        self.assertEqual(sum(record["complexity"] == "simple" for record in self.records), 140)
        self.assertEqual(sum(record["complexity"] == "complex" for record in self.records), 60)

    def test_permission_negative_minimum_is_met(self):
        self.assertGreaterEqual(sum("permission-negative" in record["tags"] for record in self.records), 50)

    def test_unanswerable_minimum_is_met(self):
        self.assertGreaterEqual(sum("unanswerable" in record["tags"] for record in self.records), 30)

    def test_required_evaluation_features_are_represented(self):
        required = {"version-conflict", "scanned-pdf-ocr", "xlsx-table", "long-table", "indirect-injection", "multi-hop"}
        tags = {tag for record in self.records for tag in record["tags"]}
        self.assertTrue(required <= tags)


if __name__ == "__main__":
    unittest.main()
