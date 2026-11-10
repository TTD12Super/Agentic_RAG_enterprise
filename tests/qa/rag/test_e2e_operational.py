import unittest
from uuid import UUID

from backend.app.authorization.policy import DocumentResource
from backend.app.ingestion import IngestionService
from backend.tests._ingestion_fixtures import active, make_manifest, staged
from backend.tests.test_dense_retrieval import (
    _active_document,
    _principal,
    _resource,
    _retriever,
)
from backend.app.rag.dense import DenseRetriever


class DenseRetrievalOperationalTests(unittest.TestCase):
    def test_complete_ingestion_to_retrieval_flow_returns_evidence(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000031")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="operational retrieval evidence",
        )

        result = retriever.search("operational", principal, policy_epoch=7)

        self.assertEqual(result.status, "OK")
        self.assertEqual(len(result.evidence), 1)

    def test_staged_version_is_not_retrievable_before_publication(self):
        ingestion = IngestionService()
        manifest, _, _, version = staged(
            ingestion,
            make_manifest(tenant_id=UUID("00000000-0000-0000-0000-000000000032")),
        )

        self.assertEqual(version.metadata.status, "PENDING_REVIEW_2")
        self.assertEqual(
            ingestion.retrievable_chunks(manifest.document_id, manifest.tenant_id), ()
        )

    def test_revocation_removes_search_and_source_access(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000033")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="revoked operational source",
        )
        ingestion.revoke_version(version_id, tenant_id)

        self.assertEqual(
            retriever.search("revoked", principal, policy_epoch=7).evidence, ()
        )
        self.assertTrue(
            retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7).redacted
        )

    def test_soft_delete_removes_search_and_source_access(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000034")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="deleted operational source",
        )
        ingestion.soft_delete_document(document_id, tenant_id)

        self.assertEqual(
            retriever.search("deleted", principal, policy_epoch=7).evidence, ()
        )
        self.assertTrue(
            retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7).redacted
        )

    def test_policy_store_outage_fails_closed_for_search_and_fetch(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000035")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="policy outage source",
        )
        retriever._pep.evaluator.policy_store.available = False

        self.assertEqual(
            retriever.search("outage", principal, policy_epoch=7).evidence, ()
        )
        source = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)
        self.assertTrue(source.redacted)
        self.assertIsNone(source.content)

    def test_cross_tenant_end_to_end_candidate_is_invisible(self):
        tenant_a = UUID("00000000-0000-0000-0000-000000000036")
        tenant_b = UUID("00000000-0000-0000-0000-000000000037")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_b
        )
        principal = _principal(tenant_a, department_id)
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="other tenant operational secret",
        )

        result = retriever.search("operational secret", principal, policy_epoch=7)

        self.assertEqual(result.evidence, ())
        self.assertTrue(
            retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7).redacted
        )

    def test_chairman_role_can_read_published_internal_document(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000038")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id).model_copy(
            update={"roles": ["chairman"], "department_ids": []}
        )
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="chairman published access",
        )

        self.assertEqual(
            retriever.search("published access", principal, policy_epoch=7).status,
            "OK",
        )

    def test_current_version_binding_blocks_mismatched_resource(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000039")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        baseline = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="current version only",
        )
        stale = DocumentResource(
            document_id=str(document_id),
            tenant_id=str(tenant_id),
            classification="INTERNAL",
            current_version_id=str(version_id),
            version_id=str(version_id),
            version_status="SUPERSEDED",
            owner_department_id=str(department_id),
            policy_epoch=7,
        )
        retriever = DenseRetriever(
            index=baseline._index,
            ingestion=ingestion,
            pep=baseline._pep,
            documents={str(document_id): stale},
            model_gateway=baseline._model_gateway,
        )

        self.assertEqual(
            retriever.search("current", principal, policy_epoch=7).evidence, ()
        )

    def test_repeated_operational_search_has_stable_result(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000040")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="stable operational ranking",
        )

        first = retriever.search("stable", principal, policy_epoch=7)
        second = retriever.search("stable", principal, policy_epoch=7)

        self.assertEqual(first, second)

    def test_operational_result_contains_no_private_source_uri(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000041")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="safe evidence body",
        )

        result = retriever.search("safe evidence", principal, policy_epoch=7)

        self.assertNotIn("private://", repr(result))
        self.assertNotIn("source_uri", repr(result))


if __name__ == "__main__":
    unittest.main()
