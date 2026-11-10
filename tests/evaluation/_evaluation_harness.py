"""Schema validation and deterministic metrics for the synthetic evaluation dataset."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = Path(__file__).with_name("golden_dataset.jsonl")
REQUIRED_FIELDS = {
    "case_id",
    "query",
    "principal_fixture",
    "tenant_id",
    "expected_source_spans",
    "expected_status",
    "expected_facts",
    "tags",
}
ALLOWED_STATUSES = {"ANSWERED", "PARTIAL", "INSUFFICIENT_EVIDENCE", "ACCESS_DENIED", "ERROR"}
NO_ANSWER_STATUSES = {"INSUFFICIENT_EVIDENCE", "ACCESS_DENIED"}


def load_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw in enumerate(FIXTURE_PATH.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number}: record must be an object")
        records.append(value)
    return records


def _validate_span(span: dict[str, Any]) -> None:
    required = {"kind", "document_id", "version_id", "tenant_id"}
    missing = required - span.keys()
    if missing:
        raise ValueError(f"source span missing fields: {sorted(missing)}")
    if span["kind"] == "PDF":
        if not isinstance(span.get("page"), int) or span["page"] < 1:
            raise ValueError("PDF source span needs a positive page")
        locator = span.get("source_span")
        if not isinstance(locator, dict) or locator.get("start", -1) < 0 or locator.get("end", -1) <= locator.get("start", -1):
            raise ValueError("PDF source span needs an increasing character range")
    elif span["kind"] == "DOCX":
        if not span.get("heading") or not isinstance(span.get("paragraph"), int):
            raise ValueError("DOCX source span needs heading and paragraph")
    elif span["kind"] == "XLSX":
        if not span.get("sheet") or not span.get("cell_range"):
            raise ValueError("XLSX source span needs sheet and cell_range")
    else:
        raise ValueError(f"unsupported source kind: {span['kind']}")


def validate_record(record: dict[str, Any]) -> None:
    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        raise ValueError(f"{record.get('case_id', '<unknown>')}: missing {sorted(missing)}")
    if not record["case_id"] or not record["query"] or not record["principal_fixture"] or not record["tenant_id"]:
        raise ValueError(f"{record['case_id']}: required string is empty")
    if record["expected_status"] not in ALLOWED_STATUSES:
        raise ValueError(f"{record['case_id']}: invalid status")
    if not isinstance(record["expected_source_spans"], list) or not isinstance(record["expected_facts"], list) or not isinstance(record["tags"], list):
        raise ValueError(f"{record['case_id']}: list fields have invalid types")
    for span in record["expected_source_spans"]:
        if not isinstance(span, dict):
            raise ValueError(f"{record['case_id']}: source span must be an object")
        _validate_span(span)
        if span["tenant_id"] != record["tenant_id"]:
            raise ValueError(f"{record['case_id']}: source tenant mismatch")
    if record["expected_status"] in NO_ANSWER_STATUSES and record["expected_source_spans"]:
        raise ValueError(f"{record['case_id']}: no-answer record exposes an expected source")
    if record["expected_status"] == "ANSWERED" and not record["expected_source_spans"]:
        raise ValueError(f"{record['case_id']}: answered record has no expected source")


def validate_dataset(records: list[dict[str, Any]]) -> None:
    if len(records) < 200:
        raise ValueError("dataset must contain at least 200 cases")
    for record in records:
        validate_record(record)
    case_ids = [record["case_id"] for record in records]
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("case_id values must be unique")
    languages = [record.get("language") for record in records]
    complexities = [record.get("complexity") for record in records]
    if languages.count("vi") < 140 or languages.count("en") < 60:
        raise ValueError("dataset must include at least 70% Vietnamese and 30% English cases")
    if complexities.count("simple") < 140 or complexities.count("complex") < 60:
        raise ValueError("dataset must include at least 70% simple and 30% complex cases")
    if sum("permission-negative" in record["tags"] for record in records) < 50:
        raise ValueError("dataset must include at least 50 permission-negative cases")
    if sum("unanswerable" in record["tags"] for record in records) < 30:
        raise ValueError("dataset must include at least 30 unanswerable cases")


def load_validated_records() -> list[dict[str, Any]]:
    records = load_records()
    validate_dataset(records)
    return records


def source_key(span: dict[str, Any]) -> str:
    locator = {
        key: span.get(key)
        for key in ("kind", "document_id", "version_id", "page", "source_span", "heading", "paragraph", "sheet", "cell_range")
        if key in span
    }
    return json.dumps(locator, sort_keys=True, separators=(",", ":"))


def recall_at_k(expected: list[dict[str, Any]], retrieved: list[dict[str, Any]], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    expected_keys = {source_key(span) for span in expected}
    retrieved_keys = {source_key(span) for span in retrieved[:k]}
    if not expected_keys:
        return 1.0 if not retrieved_keys else 0.0
    return len(expected_keys & retrieved_keys) / len(expected_keys)


def ndcg_at_k(expected: list[dict[str, Any]], retrieved: list[dict[str, Any]], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    expected_keys = {source_key(span) for span in expected}
    relevance = [1 if source_key(span) in expected_keys else 0 for span in retrieved[:k]]
    ideal = sorted(relevance, reverse=True)
    ideal_dcg = sum(value / math.log2(index + 2) for index, value in enumerate(ideal))
    if not expected_keys:
        return 1.0 if not relevance else 0.0
    if ideal_dcg == 0:
        return 0.0
    actual_dcg = sum(value / math.log2(index + 2) for index, value in enumerate(relevance))
    return actual_dcg / ideal_dcg


def mean_reciprocal_rank(expected: list[dict[str, Any]], retrieved: list[dict[str, Any]]) -> float:
    expected_keys = {source_key(span) for span in expected}
    if not expected_keys:
        return 1.0 if not retrieved else 0.0
    for rank, span in enumerate(retrieved, 1):
        if source_key(span) in expected_keys:
            return 1.0 / rank
    return 0.0


def citation_accuracy(expected: list[dict[str, Any]], citations: list[dict[str, Any]]) -> float:
    expected_keys = {source_key(span) for span in expected}
    if not citations:
        return 1.0 if not expected_keys else 0.0
    return sum(source_key(citation) in expected_keys for citation in citations) / len(citations)


def answer_correctness(expected_facts: list[str], actual_facts: list[str]) -> float:
    expected = set(expected_facts)
    actual = set(actual_facts)
    if not expected:
        return 1.0 if not actual else 0.0
    return len(expected & actual) / len(expected | actual)


def no_answer_accuracy(expected_status: str, actual_status: str) -> float:
    return float((expected_status in NO_ANSWER_STATUSES) == (actual_status in NO_ANSWER_STATUSES))


def unauthorized_retrieval_rate(outcomes: list[dict[str, Any]]) -> float:
    if not outcomes:
        return 0.0
    return sum(bool(outcome.get("unauthorized_retrieval")) for outcome in outcomes) / len(outcomes)


def evaluate_case(gold: dict[str, Any], actual: dict[str, Any]) -> dict[str, float]:
    return {
        "recall_at_10": recall_at_k(gold["expected_source_spans"], actual.get("retrieved_sources", []), 10),
        "ndcg_at_10": ndcg_at_k(gold["expected_source_spans"], actual.get("retrieved_sources", []), 10),
        "mrr": mean_reciprocal_rank(gold["expected_source_spans"], actual.get("retrieved_sources", [])),
        "citation_accuracy": citation_accuracy(gold["expected_source_spans"], actual.get("citations", [])),
        "answer_correctness": answer_correctness(gold["expected_facts"], actual.get("answer_facts", [])),
        "no_answer_accuracy": no_answer_accuracy(gold["expected_status"], actual.get("status", "ERROR")),
    }
