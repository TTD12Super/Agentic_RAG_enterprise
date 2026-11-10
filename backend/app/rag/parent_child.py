"""Bounded, provider-neutral parent expansion for authorized child evidence."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any


@dataclass(frozen=True, slots=True)
class ChildEvidence:
    """Already-authorized child evidence and its immutable citation provenance."""

    chunk_id: str
    tenant_id: str
    document_id: str
    version_id: str
    text: str
    citation: object
    parent_chunk_id: str | None = None


@dataclass(frozen=True, slots=True)
class ParentRecord:
    """Parent metadata and text from the authoritative parent store."""

    chunk_id: str
    tenant_id: str
    document_id: str
    version_id: str
    text: str
    source_locator: object | None = None
    status: str = "ACTIVE"
    document_status: str = "ACTIVE"
    version_status: str = "ACTIVE"
    index_state: str = "ACTIVE"


@dataclass(frozen=True, slots=True)
class ParentEvidence:
    """Parent text bound back to every child citation that requested it."""

    parent_chunk_id: str
    tenant_id: str
    document_id: str
    version_id: str
    text: str
    source_locator: object | None
    child_chunk_ids: tuple[str, ...]
    child_citations: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class ParentExpansionResult:
    """Authorized children plus bounded, authorized parent context."""

    children: tuple[ChildEvidence, ...]
    parents: tuple[ParentEvidence, ...]

    @property
    def context(self) -> tuple[ChildEvidence | ParentEvidence, ...]:
        return self.children + self.parents


ParentAuthorizer = Callable[[ParentRecord], bool]
ParentInput = ParentRecord | Mapping[str, object]
ChildInput = ChildEvidence | Mapping[str, object]


def expand_parent_context(
    child_evidence: Sequence[ChildInput],
    parent_records: Iterable[ParentInput] | Mapping[str, ParentInput],
    authorize_parent: ParentAuthorizer,
    *,
    max_parents: int = 8,
    max_characters: int = 8_000,
) -> ParentExpansionResult:
    """Expand only current, in-scope parents without changing child authorization.

    Malformed children/parents and authorization callback failures are omitted
    from expansion. Children that are valid input remain in the result.
    """

    _validate_limit(max_parents, "max_parents")
    _validate_limit(max_characters, "max_characters")
    if not callable(authorize_parent):
        raise TypeError("authorize_parent must be callable")

    children = _valid_unique_children(child_evidence)
    parents = _index_parents(parent_records)
    selected: dict[str, ParentEvidence] = {}
    characters = 0

    for child in children:
        parent_id = child.parent_chunk_id
        if not parent_id:
            continue

        existing = selected.get(parent_id)
        if existing is not None:
            selected[parent_id] = replace(
                existing,
                child_chunk_ids=existing.child_chunk_ids + (child.chunk_id,),
                child_citations=existing.child_citations + (child.citation,),
            )
            continue

        parent = parents.get(parent_id)
        if parent is None or not _same_scope(child, parent) or not _active(parent):
            continue
        if len(selected) >= max_parents or len(parent.text) > max_characters - characters:
            continue
        try:
            allowed = authorize_parent(parent)
        except Exception:
            continue
        if allowed is not True:
            continue

        selected[parent_id] = ParentEvidence(
            parent_chunk_id=parent.chunk_id,
            tenant_id=parent.tenant_id,
            document_id=parent.document_id,
            version_id=parent.version_id,
            text=parent.text,
            source_locator=parent.source_locator,
            child_chunk_ids=(child.chunk_id,),
            child_citations=(child.citation,),
        )
        characters += len(parent.text)

    return ParentExpansionResult(children, tuple(selected.values()))


def _validate_limit(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")


def _valid_unique_children(values: Sequence[ChildInput]) -> tuple[ChildEvidence, ...]:
    result: list[ChildEvidence] = []
    seen: set[str] = set()
    try:
        iterator = iter(values)
    except TypeError:
        return ()
    for value in iterator:
        child = _coerce_child(value)
        if child is None or child.chunk_id in seen:
            continue
        seen.add(child.chunk_id)
        result.append(child)
    return tuple(result)


def _index_parents(
    values: Iterable[ParentInput] | Mapping[str, ParentInput],
) -> dict[str, ParentRecord | None]:
    indexed: dict[str, ParentRecord | None] = {}
    try:
        entries = values.items() if isinstance(values, Mapping) else ((None, value) for value in values)
        for key, value in entries:
            parent = _coerce_parent(value)
            if parent is None or (key is not None and key != parent.chunk_id):
                continue
            if parent.chunk_id in indexed and indexed[parent.chunk_id] != parent:
                indexed[parent.chunk_id] = None
            else:
                indexed.setdefault(parent.chunk_id, parent)
    except (TypeError, ValueError, AttributeError):
        return indexed
    return indexed


def _coerce_child(value: ChildInput) -> ChildEvidence | None:
    if isinstance(value, ChildEvidence):
        candidate = value
    elif isinstance(value, Mapping):
        candidate = _construct(
            ChildEvidence,
            value,
            required=("chunk_id", "tenant_id", "document_id", "version_id", "text", "citation"),
            optional=("parent_chunk_id",),
        )
        if candidate is None:
            return None
    else:
        return None
    if not _identity(candidate) or not isinstance(candidate.text, str) or not candidate.text.strip():
        return None
    if candidate.parent_chunk_id is not None and not _string(candidate.parent_chunk_id):
        return None
    if candidate.citation is None:
        return None
    return candidate


def _coerce_parent(value: ParentInput) -> ParentRecord | None:
    if isinstance(value, ParentRecord):
        candidate = value
    elif isinstance(value, Mapping):
        candidate = _construct(
            ParentRecord,
            value,
            required=("chunk_id", "tenant_id", "document_id", "version_id", "text", "status"),
            optional=("source_locator", "document_status", "version_status", "index_state"),
        )
        if candidate is None:
            return None
    else:
        return None
    if not _identity(candidate) or not _string(candidate.text) or not candidate.text.strip():
        return None
    if not all(_string(getattr(candidate, field)) for field in ("status", "document_status", "version_status", "index_state")):
        return None
    return candidate


def _construct(model: type[Any], value: Mapping[str, object], *, required: tuple[str, ...], optional: tuple[str, ...]) -> Any | None:
    if any(field not in value for field in required):
        return None
    fields = {field: value[field] for field in required + optional if field in value}
    try:
        return model(**fields)
    except (TypeError, ValueError):
        return None


def _identity(value: Any) -> bool:
    return all(_string(getattr(value, field, None)) for field in ("chunk_id", "tenant_id", "document_id", "version_id"))


def _string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _same_scope(child: ChildEvidence, parent: ParentRecord) -> bool:
    return (
        child.tenant_id == parent.tenant_id
        and child.document_id == parent.document_id
        and child.version_id == parent.version_id
    )


def _active(parent: ParentRecord) -> bool:
    return all(
        getattr(parent, field) == "ACTIVE"
        for field in ("status", "document_status", "version_status", "index_state")
    )


__all__ = [
    "ChildEvidence",
    "ParentAuthorizer",
    "ParentEvidence",
    "ParentExpansionResult",
    "ParentRecord",
    "expand_parent_context",
]
