"""Contract/integration checks for golden source and outcome shape."""

import unittest

from tests.evaluation._evaluation_harness import load_validated_records


class ContractIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_validated_records()

    def test_every_answered_case_has_authorized_source_evidence(self):
        for record in self.records:
            if record["expected_status"] == "ANSWERED":
                self.assertTrue(record["expected_source_spans"], record["case_id"])

    def test_every_no_answer_case_has_no_expected_source(self):
        for record in self.records:
            if record["expected_status"] in {"INSUFFICIENT_EVIDENCE", "ACCESS_DENIED"}:
                self.assertEqual(record["expected_source_spans"], [], record["case_id"])

    def test_source_spans_bind_document_and_version(self):
        for record in self.records:
            for span in record["expected_source_spans"]:
                self.assertTrue(span["document_id"])
                self.assertTrue(span["version_id"])

    def test_source_spans_bind_to_the_case_tenant(self):
        for record in self.records:
            for span in record["expected_source_spans"]:
                self.assertEqual(span["tenant_id"], record["tenant_id"])

    def test_answered_cases_have_expected_facts_and_answer_text(self):
        for record in self.records:
            if record["expected_status"] == "ANSWERED":
                self.assertTrue(record["expected_facts"], record["case_id"])
                self.assertTrue(record["expected_answer"], record["case_id"])

    def test_unanswerable_cases_have_no_expected_facts(self):
        for record in self.records:
            if "unanswerable" in record["tags"]:
                self.assertEqual(record["expected_facts"], [], record["case_id"])

    def test_version_conflict_cases_pin_the_active_and_forbidden_versions(self):
        cases = [record for record in self.records if "version-conflict" in record["tags"] and record["expected_status"] == "ANSWERED"]
        self.assertTrue(cases)
        for record in cases:
            self.assertEqual(record["expected_source_spans"][0]["version_id"], "v2")
            self.assertEqual(record["expected_forbidden_version_ids"], ["v1"])

    def test_multi_hop_cases_have_multiple_expected_spans(self):
        cases = [record for record in self.records if "multi-hop" in record["tags"] and record["expected_status"] == "ANSWERED"]
        self.assertTrue(cases)
        self.assertTrue(all(len(record["expected_source_spans"]) >= 2 for record in cases))

    def test_xlsx_cases_pin_sheet_and_cell_range(self):
        cases = [record for record in self.records if "xlsx-table" in record["tags"] or "long-table" in record["tags"]]
        self.assertTrue(cases)
        for record in cases:
            if record["expected_status"] == "ANSWERED":
                for span in record["expected_source_spans"]:
                    self.assertEqual(span["kind"], "XLSX")
                    self.assertTrue(span["sheet"])
                    self.assertTrue(span["cell_range"])

    def test_pdf_and_docx_cases_pin_file_specific_provenance(self):
        pdfs = [span for record in self.records for span in record["expected_source_spans"] if span["kind"] == "PDF"]
        docxs = [span for record in self.records for span in record["expected_source_spans"] if span["kind"] == "DOCX"]
        self.assertTrue(all(span["page"] >= 1 and span["source_span"]["end"] > span["source_span"]["start"] for span in pdfs))
        self.assertTrue(all(span["heading"] and span["paragraph"] >= 1 for span in docxs))

if __name__ == "__main__":
    unittest.main()
