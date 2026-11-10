import json
from pathlib import Path
from uuid import UUID, uuid4

from backend.app.knowledge.models import (
    ChunkMetadata,
    DocumentMetadata,
    DocumentVersionMetadata,
    SourceSpan,
)


ROOT = Path(__file__).resolve().parents[3]
GRAPH = ROOT / "graphify-out/graph.json"
HANDOFF = ROOT / "harness/handoffs/KNOW-001.md"
TASKS = ROOT / "harness/tasks/tasks.json"
MIGRATION = ROOT / "backend/app/db/migrations/versions/0002_documents.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def task(task_id: str) -> dict:
    payload = json.loads(read(TASKS))
    return next(item for item in payload["tasks"] if item["id"] == task_id)


def make_document(
    *,
    classification: str = "PUBLIC",
    status: str = "ACTIVE",
    owner_department_id: UUID | None = None,
    current_version_id: UUID | None = None,
) -> DocumentMetadata:
    return DocumentMetadata(
        tenant_id=uuid4(),
        document_id=uuid4(),
        owner_department_id=owner_department_id,
        classification=classification,
        status=status,
        current_version_id=current_version_id,
        created_by=uuid4(),
    )


def make_version(*, status: str = "PROCESS_VALIDATED") -> DocumentVersionMetadata:
    return DocumentVersionMetadata(
        tenant_id=uuid4(),
        document_id=uuid4(),
        version_id=uuid4(),
        version_number=1,
        source_uri="private://documents/v1",
        sha256="a" * 64,
        status=status,
    )


def make_parent(*, acl_policy_ref: str | None = "policy-1") -> ChunkMetadata:
    return ChunkMetadata(
        chunk_id=uuid4(),
        tenant_id=uuid4(),
        document_id=uuid4(),
        version_id=uuid4(),
        chunk_index=0,
        acl_policy_ref=acl_policy_ref,
        text_hash="a" * 64,
    )


def make_child(parent: ChunkMetadata, **overrides: object) -> ChunkMetadata:
    values: dict[str, object] = {
        "chunk_id": uuid4(),
        "tenant_id": parent.tenant_id,
        "document_id": parent.document_id,
        "version_id": parent.version_id,
        "parent_chunk_id": parent.chunk_id,
        "chunk_index": 1,
        "text_hash": "b" * 64,
    }
    values.update(overrides)
    return ChunkMetadata(**values)
