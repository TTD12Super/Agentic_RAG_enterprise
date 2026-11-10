"""E2E/operational metric self-checks with synthetic outcomes."""

import unittest

from tests.evaluation._evaluation_harness import (
    answer_correctness,
    citation_accuracy,
    evaluate_case,
    load_validated_records,
    mean_reciprocal_rank,
    ndcg_at_k,
    no_answer_accuracy,
    recall_at_k,
    unauthorized_retrieval_rate,
)


class E2EOperationalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_validated_records()
        cls.answered = next(record for record in cls.records if record["expected_status"] == "ANSWERED")
        cls.multi_hop = next(record for record in cls.records if "multi-hop" in record["tags"] and record["expected_status"] == "ANSWERED")

    def test_recall_at_ten_is_one_for_perfect_retrieval(self):
        sources = self.answered["expected_source_spans"]
        self.assertEqual(recall_at_k(sources, sources, 10), 1.0)

    def test_recall_at_ten_penalizes_missing_multi_hop_evidence(self):
        sources = self.multi_hop["expected_source_spans"]
        self.assertEqual(recall_at_k(sources, sources[:1], 10), 0.5)

    def test_ndcg_at_ten_rewards_perfect_rank(self):
        sources = self.multi_hop["expected_source_spans"]
        self.assertEqual(ndcg_at_k(sources, sources, 10), 1.0)

    def test_ndcg_at_ten_penalizes_relevant_source_after_noise(self):
        sources = self.multi_hop["expected_source_spans"]
        noise = {"kind": "PDF", "document_id": "noise", "version_id": "v1", "tenant_id": "tenant-a", "page": 1, "source_span": {"start": 1, "end": 2}}
        self.assertLess(ndcg_at_k(sources, [noise, sources[0]], 10), 1.0)

    def test_mrr_returns_first_relevant_rank(self):
        sources = self.answered["expected_source_spans"]
        noise = {"kind": "PDF", "document_id": "noise-mrr", "version_id": "v1", "tenant_id": "tenant-a", "page": 1, "source_span": {"start": 1, "end": 2}}
        self.assertEqual(mean_reciprocal_rank(sources, [noise, sources[0]]), 0.5)

    def test_citation_accuracy_rejects_an_unexpected_citation(self):
        sources = self.answered["expected_source_spans"]
        self.assertEqual(citation_accuracy(sources, sources), 1.0)
        self.assertEqual(citation_accuracy(sources, [{"kind": "PDF", "document_id": "wrong", "version_id": "v1", "tenant_id": "tenant-a", "page": 1, "source_span": {"start": 1, "end": 2}}]), 0.0)

    def test_answer_correctness_handles_exact_and_partial_facts(self):
        self.assertEqual(answer_correctness(["a", "b"], ["a", "b"]), 1.0)
        self.assertEqual(answer_correctness(["a", "b"], ["a"]), 0.5)

    def test_no_answer_accuracy_compares_outcome_class(self):
        self.assertEqual(no_answer_accuracy("INSUFFICIENT_EVIDENCE", "ACCESS_DENIED"), 1.0)
        self.assertEqual(no_answer_accuracy("ANSWERED", "INSUFFICIENT_EVIDENCE"), 0.0)

    def test_unauthorized_retrieval_rate_is_an_incident_rate(self):
        self.assertEqual(unauthorized_retrieval_rate([{"unauthorized_retrieval": False}, {"unauthorized_retrieval": False}]), 0.0)
        self.assertEqual(unauthorized_retrieval_rate([{"unauthorized_retrieval": True}, {"unauthorized_retrieval": False}]), 0.5)

    def test_case_evaluation_is_deterministic_and_composes_metrics(self):
        gold = self.answered
        actual = {
            "status": gold["expected_status"],
            "retrieved_sources": gold["expected_source_spans"],
            "citations": gold["expected_source_spans"],
            "answer_facts": gold["expected_facts"],
        }
        first = evaluate_case(gold, actual)
        second = evaluate_case(gold, actual)
        self.assertEqual(first, second)
        self.assertEqual(set(first), {"recall_at_10", "ndcg_at_10", "mrr", "citation_accuracy", "answer_correctness", "no_answer_accuracy"})


if __name__ == "__main__":
    unittest.main()
