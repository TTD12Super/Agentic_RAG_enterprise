import os
from pathlib import Path

import pytest

from backend.app.knowledge.models import ChunkMetadata, inherit_acl


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "backend/app/db/migrations/versions/0002_documents.py"


def migration_text():
    return MIGRATION.read_text(encoding="utf-8")


def test_existing_db_contract_has_documents_table():
    assert "CREATE TABLE documents" in migration_text()


def test_existing_db_contract_has_document_versions_table():
    assert "CREATE TABLE document_versions" in migration_text()


def test_existing_db_contract_has_chunks_table():
    assert "CREATE TABLE chunks" in migration_text()


def test_existing_db_contract_has_immutable_version_uniqueness():
    assert "UNIQUE (tenant_id, document_id, version_number)" in migration_text()


def test_existing_db_contract_has_tenant_version_chunk_uniqueness():
    assert "UNIQUE (tenant_id, version_id, chunk_index)" in migration_text()


def test_existing_db_contract_has_composite_parent_fk():
    assert "FOREIGN KEY (tenant_id, version_id, parent_chunk_id)" in migration_text()


def test_existing_db_contract_has_private_source_constraint():
    assert "source_uri LIKE 'private://%'" in migration_text()


def test_existing_db_contract_has_active_index_guard():
    assert "index_status <> 'ACTIVE' OR (vector_point_id IS NOT NULL AND index_version IS NOT NULL)" in migration_text()


def test_in_memory_parent_child_matches_db_scope():
    parent = ChunkMetadata(
        chunk_id=__import__("uuid").uuid4(), tenant_id=__import__("uuid").uuid4(),
        document_id=__import__("uuid").uuid4(), version_id=__import__("uuid").uuid4(),
        chunk_index=0, acl_policy_ref="policy-1", text_hash="a" * 64
    )
    child = ChunkMetadata(
        chunk_id=__import__("uuid").uuid4(), tenant_id=parent.tenant_id,
        document_id=parent.document_id, version_id=parent.version_id,
        parent_chunk_id=parent.chunk_id, chunk_index=1, text_hash="b" * 64
    )
    assert inherit_acl(parent, child).parent_chunk_id == parent.chunk_id


@pytest.mark.skipif(not os.getenv("DB001_DATABASE_URL"), reason="requires disposable DB001_DATABASE_URL")
def test_optional_database_probe_is_explicitly_opt_in():
    psycopg = pytest.importorskip("psycopg")
    conninfo = os.environ["DB001_DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(conninfo) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name IN ('documents', 'document_versions', 'chunks')"
            )
            assert {row[0] for row in cursor.fetchall()} == {"documents", "document_versions", "chunks"}
