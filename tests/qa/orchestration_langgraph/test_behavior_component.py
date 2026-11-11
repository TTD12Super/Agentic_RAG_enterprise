from datetime import datetime, timedelta, timezone
from typing import get_type_hints

import pytest
from langgraph.graph.state import CompiledStateGraph

from backend.app.orchestration import (
    AnswerDraft,
    BoundedOrchestrator,
    OrchestrationRequest,
    OrchestrationStatus,
    QueryRoute,
)
from backend.app.orchestration import orchestrator as orchestrator_module
from backend.app.tools import ToolResult, ToolStatus


class Clock:
    value = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)

    def __call__(self):
        return self.value


class Tools:
    def __init__(self, results=()):
        self.results = list(results)
        self.calls = []

    def execute(self, call):
        self.calls.append(call)
        return self.results.pop(0) if self.results else ToolResult(
            ToolStatus.SUCCESS, call.tool, call.tool_call_id, {"evidence": []}
        )


class Answerer:
    def __init__(self, drafts):
        self.drafts = list(drafts)
        self.calls = []

    def synthesize(self, query, context, *, principal_ref, authorized_scope_ref):
        self.calls.append((query, context, principal_ref, authorized_scope_ref))
        return self.drafts.pop(0)


def request(clock, query="What is the warranty?"):
    return OrchestrationRequest(
        query=query,
        principal_ref="principal-1",
        authorized_scope_ref="scope-1",
        job_id="job-1",
        attempt_id="attempt-1",
        traceparent="00-abc-abc-01",
        deadline_at=clock.value + timedelta(minutes=1),
    )


def evidence(text="Warranty coverage is twelve months.", chunk_id="chunk-1"):
    return {
        "evidence": [{
            "chunk_id": chunk_id,
            "document_id": "doc-1",
            "version_id": "version-1",
            "text": text,
            "page_start": 1,
            "page_end": 1,
            "source_span": {"start": 0, "end": len(text)},
        }]
    }


def run(tools, answerer, clock, query="What is the warranty?"):
    return BoundedOrchestrator(tools=tools, answerer=answerer, clock=clock).run(
        request(clock, query)
    )


def test_compiles_a_state_graph_with_expected_nodes():
    graph = BoundedOrchestrator(
        tools=Tools(), answerer=Answerer([AnswerDraft(OrchestrationStatus.SUPPORTED)]), clock=Clock()
    ).graph

    assert isinstance(graph, CompiledStateGraph)
    assert {"prepare", "retrieve", "synthesize", "finish"} <= set(graph.nodes)


def test_simple_query_routes_once_and_preserves_context():
    clock = Clock()
    tools = Tools([ToolResult(ToolStatus.SUCCESS, "search_documents", "c-1", evidence())])
    answerer = Answerer([AnswerDraft(OrchestrationStatus.SUPPORTED, "Twelve months.")])

    result = run(tools, answerer, clock)

    assert result.status is OrchestrationStatus.SUPPORTED
    assert result.route is QueryRoute.SIMPLE
    assert result.retrieval_rounds == result.subqueries == result.tool_calls == 1
    assert answerer.calls[0][1].citations[0].chunk_id == "chunk-1"


def test_complex_query_splits_into_distinct_subqueries():
    clock = Clock()
    tools = Tools([
        ToolResult(ToolStatus.SUCCESS, "search_documents", "c-1", evidence("A is twelve months.")),
        ToolResult(ToolStatus.SUCCESS, "search_documents", "c-2", evidence("B is six months.", "chunk-2")),
    ])
    answerer = Answerer([AnswerDraft(OrchestrationStatus.SUPPORTED, "A and B.")])

    result = run(tools, answerer, clock, "Compare product A and product B")

    assert result.route is QueryRoute.COMPLEX
    assert result.subqueries == 2
    assert [call.arguments["query"] for call in tools.calls] == ["Compare product A", "product B"]


def test_conditional_loop_recovers_after_first_insufficient_draft():
    clock = Clock()
    tools = Tools([
        ToolResult(ToolStatus.SUCCESS, "search_documents", "c-1", evidence()),
        ToolResult(ToolStatus.SUCCESS, "search_documents", "c-2", evidence("More warranty detail.", "chunk-2")),
    ])
    answerer = Answerer([
        AnswerDraft(OrchestrationStatus.INSUFFICIENT_EVIDENCE, missing_information=("term",)),
        AnswerDraft(OrchestrationStatus.SUPPORTED, "The warranty is twelve months."),
    ])

    result = run(tools, answerer, clock)

    assert result.status is OrchestrationStatus.SUPPORTED
    assert result.retrieval_rounds == 2
    assert len(answerer.calls) == 2


def test_empty_retrieval_stops_at_two_rounds():
    clock = Clock()
    tools = Tools()
    answerer = Answerer([AnswerDraft(OrchestrationStatus.INSUFFICIENT_EVIDENCE)])

    result = run(tools, answerer, clock)

    assert result.status is OrchestrationStatus.INSUFFICIENT_EVIDENCE
    assert result.retrieval_rounds == 2
    assert result.subqueries == result.tool_calls == 2
    assert answerer.calls == []


def test_complex_loop_caps_subqueries_and_tool_calls_at_four():
    clock = Clock()
    tools = Tools()
    answerer = Answerer([AnswerDraft(OrchestrationStatus.INSUFFICIENT_EVIDENCE)])

    result = run(tools, answerer, clock, "Compare A and B and C and D")

    assert result.status is OrchestrationStatus.INSUFFICIENT_EVIDENCE
    assert result.retrieval_rounds == 2
    assert result.subqueries == result.tool_calls == 4
    assert len(tools.calls) == 4


def test_graph_state_declares_typed_workflow_fields():
    annotations = get_type_hints(orchestrator_module._GraphState)

    assert annotations["request"] is OrchestrationRequest
    assert "evidence" in annotations
    assert "retrieval_rounds" in annotations
    assert "tool_failures" in annotations
    assert "outcome" in annotations


def test_malformed_evidence_is_removed_before_answer_context():
    clock = Clock()
    malformed = {"evidence": [{"chunk_id": "c", "document_id": "d", "version_id": "v", "text": ""}]}
    tools = Tools([ToolResult(ToolStatus.SUCCESS, "search_documents", "c-1", malformed)])
    answerer = Answerer([AnswerDraft(OrchestrationStatus.INSUFFICIENT_EVIDENCE)])

    result = run(tools, answerer, clock)

    assert result.status is OrchestrationStatus.INSUFFICIENT_EVIDENCE
    assert answerer.calls == []


def test_duplicate_chunks_are_deduplicated_deterministically():
    clock = Clock()
    item = evidence()
    item["evidence"].append(dict(item["evidence"][0]))
    tools = Tools([ToolResult(ToolStatus.SUCCESS, "search_documents", "c-1", item)])
    answerer = Answerer([AnswerDraft(OrchestrationStatus.SUPPORTED, "answer")])

    result = run(tools, answerer, clock)

    assert result.status is OrchestrationStatus.SUPPORTED
    assert [item.chunk_id for item in answerer.calls[0][1].citations] == ["chunk-1"]


def test_partial_answer_is_a_first_class_successful_outcome():
    clock = Clock()
    tools = Tools([ToolResult(ToolStatus.SUCCESS, "search_documents", "c-1", evidence())])
    answerer = Answerer([AnswerDraft(
        OrchestrationStatus.PARTIAL, "Known portion.", missing_information=("delivery date",)
    )])

    result = run(tools, answerer, clock)

    assert result.status is OrchestrationStatus.PARTIAL
    assert result.answer == "Known portion."
    assert result.missing_information == ("delivery date",)
