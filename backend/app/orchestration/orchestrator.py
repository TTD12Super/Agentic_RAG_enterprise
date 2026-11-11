"""Bounded LangGraph orchestration behind the backend Tool Gateway."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import uuid
from typing import Any, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.guardrails import inspect_untrusted_content, normalize_user_input
from backend.app.orchestration.context import (
    AssembledContext,
    RetrievedEvidence,
    build_secure_context,
)
from backend.app.tools.gateway import ToolCall, ToolGateway, ToolResult, ToolStatus


MAX_RETRIEVAL_ROUNDS = 2
MAX_SUBQUERIES = 4
MAX_TOOL_CALLS = 8
_GRAPH_RECURSION_LIMIT = 12


class OrchestrationStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    ERROR = "ERROR"


class QueryRoute(StrEnum):
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"


class OrchestrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    query: str = Field(min_length=1, max_length=4_000)
    principal_ref: str = Field(min_length=1, max_length=256)
    authorized_scope_ref: str = Field(min_length=1, max_length=256)
    job_id: str = Field(min_length=1, max_length=128)
    attempt_id: str = Field(min_length=1, max_length=128)
    traceparent: str = Field(min_length=1, max_length=256)
    deadline_at: datetime

    @field_validator("deadline_at")
    @classmethod
    def aware_deadline(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("deadline_at must be timezone-aware")
        return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class AnswerDraft:
    """Result from the answer boundary after it consumes secure context."""

    status: OrchestrationStatus
    answer: str = ""
    citations: tuple[Mapping[str, Any], ...] = ()
    missing_information: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "citations", tuple(self.citations))
        object.__setattr__(self, "missing_information", tuple(self.missing_information))


class AnswerSynthesizer(Protocol):
    def synthesize(
        self,
        query: str,
        context: AssembledContext,
        *,
        principal_ref: str,
        authorized_scope_ref: str,
    ) -> AnswerDraft: ...


@dataclass(frozen=True, slots=True)
class OrchestrationOutcome:
    status: OrchestrationStatus
    answer: str = ""
    citations: tuple[Mapping[str, Any], ...] = ()
    route: QueryRoute = QueryRoute.SIMPLE
    retrieval_rounds: int = 0
    subqueries: int = 0
    tool_calls: int = 0
    reason_codes: tuple[str, ...] = ()
    missing_information: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "citations", tuple(self.citations))
        object.__setattr__(self, "reason_codes", tuple(self.reason_codes))
        object.__setattr__(self, "missing_information", tuple(self.missing_information))


class _GraphState(TypedDict, total=False):
    request: OrchestrationRequest
    checked_query: str
    route: str
    evidence: tuple[RetrievedEvidence, ...]
    retrieval_rounds: int
    subqueries: int
    tool_calls: int
    tool_failures: tuple[ToolStatus, ...]
    draft: AnswerDraft | None
    outcome: OrchestrationOutcome | None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _route(query: str) -> str:
    lowered = query.casefold()
    complex_markers = (
        "compare", "comparison", "versus", " vs ", "difference", "differences",
        "so sánh", "khác nhau", "and ", "và ", "both", "all of",
    )
    return QueryRoute.COMPLEX if query.count("?") > 1 or any(
        marker in lowered for marker in complex_markers
    ) else QueryRoute.SIMPLE


def _subqueries(query: str, route: str, limit: int) -> tuple[str, ...]:
    if limit <= 0:
        return ()
    if route == QueryRoute.SIMPLE:
        return (query,)
    pieces = [piece.strip(" ,;:") for piece in query.replace("?", " ").split(" and ")]
    pieces = [piece for piece in pieces if piece]
    if len(pieces) == 1:
        pieces = [piece.strip(" ,;:") for piece in query.replace("?", " ").split(" và ")]
        pieces = [piece for piece in pieces if piece]
    unique = tuple(dict.fromkeys(pieces))
    return unique[:limit] or (query,)


def _evidence_from_result(result: ToolResult) -> tuple[RetrievedEvidence, ...]:
    if result.status is not ToolStatus.SUCCESS or not isinstance(result.payload, Mapping):
        return ()
    raw_items = result.payload.get("evidence", ())
    if not isinstance(raw_items, Sequence) or isinstance(raw_items, (str, bytes)):
        return ()
    parsed: list[RetrievedEvidence] = []
    seen: set[str] = set()
    for raw in raw_items:
        if not isinstance(raw, Mapping):
            continue
        values = {str(key): value for key, value in raw.items()}
        chunk_id = values.get("chunk_id")
        document_id = values.get("document_id")
        version_id = values.get("version_id")
        text = values.get("text")
        if not all(isinstance(item, str) and item.strip() for item in (chunk_id, document_id, version_id, text)):
            continue
        if chunk_id in seen:
            continue
        inspected = inspect_untrusted_content(text)
        if not inspected.allowed or inspected.value is None:
            continue
        span = values.get("source_span")
        source_span: tuple[int, int] | None = None
        if isinstance(span, Mapping):
            start, end = span.get("start"), span.get("end")
            if isinstance(start, int) and not isinstance(start, bool) and isinstance(end, int) and not isinstance(end, bool):
                source_span = (start, end)
        elif isinstance(span, (list, tuple)) and len(span) == 2 and all(
            isinstance(item, int) and not isinstance(item, bool) for item in span
        ):
            source_span = (span[0], span[1])
        try:
            evidence = RetrievedEvidence(
                chunk_id=chunk_id,
                document_id=document_id,
                version_id=version_id,
                text=inspected.value,
                page_start=values.get("page_start") if isinstance(values.get("page_start"), int) else None,
                page_end=values.get("page_end") if isinstance(values.get("page_end"), int) else None,
                source_span=source_span,
                citation_token=values.get("citation_token") if isinstance(values.get("citation_token"), str) else None,
                retrieval_method=values.get("retrieval_method") if isinstance(values.get("retrieval_method"), str) else None,
            )
        except (TypeError, ValueError):
            continue
        seen.add(chunk_id)
        parsed.append(evidence)
    return tuple(parsed)


class BoundedOrchestrator:
    """Run a user-scoped, single-agent workflow in a compiled LangGraph."""

    def __init__(
        self,
        *,
        tools: ToolGateway,
        answerer: AnswerSynthesizer,
        clock: Any = _utc_now,
        max_rounds: int = MAX_RETRIEVAL_ROUNDS,
        max_subqueries: int = MAX_SUBQUERIES,
        max_tool_calls: int = MAX_TOOL_CALLS,
    ) -> None:
        if (max_rounds, max_subqueries, max_tool_calls) != (
            MAX_RETRIEVAL_ROUNDS, MAX_SUBQUERIES, MAX_TOOL_CALLS,
        ):
            raise ValueError("ORCH-001 limits are fixed by the v1 contract")
        self._tools = tools
        self._answerer = answerer
        self._clock = clock
        self._graph = self._build_graph()

    @property
    def graph(self):
        """Compiled LangGraph object, exposed for runtime/contract inspection."""
        return self._graph

    def run(self, request: OrchestrationRequest | Mapping[str, Any]) -> OrchestrationOutcome:
        try:
            request = request if isinstance(request, OrchestrationRequest) else OrchestrationRequest.model_validate(request)
            checked = normalize_user_input(request.query)
            if not checked.allowed or checked.value is None:
                return OrchestrationOutcome(OrchestrationStatus.ERROR, reason_codes=("INVALID_QUERY",))
        except Exception:
            return OrchestrationOutcome(OrchestrationStatus.ERROR, reason_codes=("INVALID_REQUEST",))

        initial: _GraphState = {
            "request": request,
            "checked_query": checked.value,
            "evidence": (), "retrieval_rounds": 0, "subqueries": 0,
            "tool_calls": 0, "tool_failures": (), "draft": None, "outcome": None,
        }
        try:
            final = self._graph.invoke(initial, config={"recursion_limit": _GRAPH_RECURSION_LIMIT})
        except Exception:
            return OrchestrationOutcome(
                OrchestrationStatus.ERROR,
                route=_route(checked.value),
                reason_codes=("GRAPH_FAILED",),
            )
        outcome = final.get("outcome") if isinstance(final, Mapping) else None
        if isinstance(outcome, OrchestrationOutcome):
            return outcome
        return OrchestrationOutcome(
            OrchestrationStatus.ERROR,
            route=_route(checked.value),
            reason_codes=("GRAPH_FAILED",),
        )

    def _build_graph(self):
        builder = StateGraph(_GraphState)
        builder.add_node("prepare", self._prepare_node)
        builder.add_node("retrieve", self._retrieve_node)
        builder.add_node("synthesize", self._synthesize_node)
        builder.add_node("finish", self._finish_node)
        builder.add_edge(START, "prepare")
        builder.add_edge("prepare", "retrieve")
        builder.add_edge("retrieve", "synthesize")
        builder.add_conditional_edges("synthesize", self._next_node, {"retrieve": "retrieve", "finish": "finish"})
        builder.add_edge("finish", END)
        return builder.compile()

    def _prepare_node(self, state: _GraphState) -> dict[str, object]:
        return {"route": _route(state["checked_query"])}

    def _retrieve_node(self, state: _GraphState) -> dict[str, object]:
        request = state["request"]
        retrieval_round = state.get("retrieval_rounds", 0) + 1
        if self._clock().astimezone(timezone.utc) >= request.deadline_at:
            return {
                "retrieval_rounds": retrieval_round,
                "outcome": self._outcome(state, OrchestrationStatus.INSUFFICIENT_EVIDENCE, "WORKFLOW_TIMEOUT"),
            }
        current_subqueries = state.get("subqueries", 0)
        current_tool_calls = state.get("tool_calls", 0)
        remaining_subqueries = MAX_SUBQUERIES - current_subqueries
        remaining_tools = MAX_TOOL_CALLS - current_tool_calls
        if remaining_subqueries <= 0 or remaining_tools <= 0:
            return {"retrieval_rounds": retrieval_round}
        plan_route = state.get("route", QueryRoute.SIMPLE) if retrieval_round == 1 else QueryRoute.COMPLEX
        planned = _subqueries(
            state["checked_query"], plan_route,
            min(2 if plan_route == QueryRoute.COMPLEX else 1, remaining_subqueries, remaining_tools),
        )
        round_evidence: list[RetrievedEvidence] = []
        failures: list[ToolStatus] = []
        for subquery in planned:
            call = ToolCall(
                tool="search_documents", arguments={"query": subquery, "top_k": 8},
                principal_ref=request.principal_ref, authorized_scope_ref=request.authorized_scope_ref,
                tool_call_id=str(uuid.uuid4()), job_id=request.job_id, attempt_id=request.attempt_id,
                traceparent=request.traceparent, deadline_at=request.deadline_at,
            )
            result = self._tools.execute(call)
            round_evidence.extend(_evidence_from_result(result))
            if result.status is not ToolStatus.SUCCESS:
                failures.append(result.status)
        merged = list(state.get("evidence", ()))
        seen = {item.chunk_id for item in merged}
        for item in round_evidence:
            if item.chunk_id not in seen:
                merged.append(item)
                seen.add(item.chunk_id)
        return {
            "evidence": tuple(merged), "retrieval_rounds": retrieval_round,
            "subqueries": current_subqueries + len(planned),
            "tool_calls": current_tool_calls + len(planned),
            "tool_failures": state.get("tool_failures", ()) + tuple(failures),
        }

    def _synthesize_node(self, state: _GraphState) -> dict[str, object]:
        evidence = state.get("evidence", ())
        failures = state.get("tool_failures", ())
        if not evidence:
            if ToolStatus.DENIED in failures:
                return {"outcome": self._outcome(state, OrchestrationStatus.ERROR, "TOOL_DENIED")}
            return {}
        draft = self._synthesize(state["request"], evidence)
        if draft is None:
            return {"outcome": self._outcome(state, OrchestrationStatus.ERROR, "ANSWER_FAILED")}
        return {"draft": draft}

    def _next_node(self, state: _GraphState) -> str:
        if state.get("outcome") is not None:
            return "finish"
        draft = state.get("draft")
        if draft is not None and draft.status != OrchestrationStatus.INSUFFICIENT_EVIDENCE:
            return "finish"
        if state.get("retrieval_rounds", 0) >= MAX_RETRIEVAL_ROUNDS:
            return "finish"
        if state.get("subqueries", 0) >= MAX_SUBQUERIES or state.get("tool_calls", 0) >= MAX_TOOL_CALLS:
            return "finish"
        return "retrieve"

    def _finish_node(self, state: _GraphState) -> dict[str, object]:
        if state.get("outcome") is not None:
            return {}
        draft = state.get("draft")
        if draft is not None:
            return {"outcome": self._draft_outcome(state, draft)}
        if state.get("tool_failures") and not state.get("evidence"):
            return {"outcome": self._outcome(state, OrchestrationStatus.INSUFFICIENT_EVIDENCE, "TOOL_UNAVAILABLE")}
        return {"outcome": self._outcome(state, OrchestrationStatus.INSUFFICIENT_EVIDENCE, "INSUFFICIENT_EVIDENCE")}

    def _synthesize(self, request: OrchestrationRequest, evidence: tuple[RetrievedEvidence, ...]) -> AnswerDraft | None:
        try:
            context = build_secure_context(request.query, evidence)
            draft = self._answerer.synthesize(
                request.query, context, principal_ref=request.principal_ref,
                authorized_scope_ref=request.authorized_scope_ref,
            )
            if not isinstance(draft, AnswerDraft):
                return None
            if draft.status == OrchestrationStatus.ERROR:
                return draft
            if draft.answer:
                checked = inspect_untrusted_content(draft.answer, max_chars=12_000)
                if not checked.allowed or checked.value is None:
                    return AnswerDraft(OrchestrationStatus.ERROR)
                return AnswerDraft(draft.status, checked.value, tuple(draft.citations), tuple(draft.missing_information))
            return draft
        except Exception:
            return None

    @staticmethod
    def _draft_outcome(state: _GraphState, draft: AnswerDraft) -> OrchestrationOutcome:
        return OrchestrationOutcome(
            status=draft.status, answer=draft.answer, citations=draft.citations,
            route=state.get("route", QueryRoute.SIMPLE),
            retrieval_rounds=state.get("retrieval_rounds", 0),
            subqueries=state.get("subqueries", 0), tool_calls=state.get("tool_calls", 0),
            missing_information=draft.missing_information,
        )

    @staticmethod
    def _outcome(state: _GraphState, status: str, reason: str) -> OrchestrationOutcome:
        return OrchestrationOutcome(
            status=status, route=state.get("route", QueryRoute.SIMPLE),
            retrieval_rounds=state.get("retrieval_rounds", 0),
            subqueries=state.get("subqueries", 0), tool_calls=state.get("tool_calls", 0),
            reason_codes=(reason,),
        )


__all__ = [
    "AnswerDraft", "AnswerSynthesizer", "BoundedOrchestrator",
    "MAX_RETRIEVAL_ROUNDS", "MAX_SUBQUERIES", "MAX_TOOL_CALLS",
    "OrchestrationOutcome", "OrchestrationRequest", "OrchestrationStatus", "QueryRoute",
]
