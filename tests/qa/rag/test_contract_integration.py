import inspect
import unittest
from pathlib import Path
from uuid import UUID

from backend.app.authorization.policy import AccessGrant, Action
from backend.app.ingestion import IngestionService
from backend.tests._ingestion_fixtures import make_manifest, quarantine, staged
from backend.tests.test_dense_retrieval import (
    _active_document,
    _principal,
    _retriever,
)
from backend.app.rag.dense import DenseRetriever


ROOT = Path(__file__).resolve().parents[3]
RETRIEVAL_CONTRACT = (ROOT / "docs" / "contracts" / "retrieval.md").read_text(
    encoding="utf-8"
)
DESIGN = (ROOT / "docs" / "rag" / "retrieval-design.md").read_text(encoding="utf-8")
POLICY_CONTRACT = (ROOT / "docs" / "contracts" / "identity-and-policy.md").read_text(
    encoding="utf-8"
)


class DenseRetrievalContractIntegrationTests(unittest.TestCase):
    def test_contract_requires_tenant_active_version_and_acl_filters(self):
        self.assertIn("tenant, current ACTIVE version and ACL", RETRIEVAL_CONTRACT)
        self.assertIn("dense and BM25 branches", RETRIEVAL_CONTRACT)

    def test_contract_requires_revalidation_before_content_return(self):
        self.assertIn("Revalidate each chunk/document", RETRIEVAL_CONTRACT)
        self.assertIn("rechecks authorization", RETRIEVAL_CONTRACT)

    def test_contract_forbids_privileged_source_paths(self):
        self.assertIn("Never send privileged raw document paths", RETRIEVAL_CONTRACT)
        self.assertIn("source spans", DESIGN.lower())

    def test_published_lifecycle_is_visible_to_dense_retrieval(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000021")
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
            text="published contract evidence",
        )

        result = retriever.search("contract evidence", principal, policy_epoch=7)

        self.assertEqual(result.status, "OK")
        self.assertEqual(result.evidence[0].citation.version_id, str(version_id))

    def test_quarantined_lifecycle_is_not_visible(self):
        ingestion = IngestionService()
        manifest = make_manifest(
            tenant_id=UUID("00000000-0000-0000-0000-000000000022")
        )
        quarantine(ingestion, manifest)

        self.assertEqual(
            ingestion.retrievable_chunks(manifest.document_id, manifest.tenant_id), ()
        )

    def test_staged_lifecycle_is_not_visible(self):
        ingestion = IngestionService()
        manifest, _, _, record = staged(
            ingestion,
            make_manifest(tenant_id=UUID("00000000-0000-0000-0000-000000000023")),
        )

        self.assertEqual(record.metadata.status, "PENDING_REVIEW_2")
        self.assertEqual(
            ingestion.retrievable_chunks(manifest.document_id, manifest.tenant_id), ()
        )

    def test_policy_epoch_is_required_for_current_authorized_result(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000024")
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
            text="policy epoch evidence",
        )

        self.assertEqual(
            retriever.search("epoch", principal, policy_epoch=7).status, "OK"
        )
        self.assertEqual(
            retriever.search("epoch", principal, policy_epoch=6).evidence, ()
        )

    def test_citation_binds_chunk_document_version_and_span(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000025")
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
            text="citation-bound evidence",
        )

        citation = retriever.search("citation", principal, policy_epoch=7).evidence[0].citation

        self.assertEqual(citation.document_id, str(document_id))
        self.assertEqual(citation.version_id, str(version_id))
        self.assertEqual(citation.source_span, chunk.source_span)

    def test_source_download_is_rechecked_after_read_allows_search(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000026")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        deny_download = AccessGrant(
            Action.SOURCE_DOWNLOAD.value, "DENY", user_id=principal.user_id
        )
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="readable but not downloadable",
            acl=(deny_download,),
        )

        self.assertEqual(
            retriever.search("downloadable", principal, policy_epoch=7).status, "OK"
        )
        source = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)
        self.assertTrue(source.redacted)
        self.assertIsNone(source.content)
        self.assertIsNone(source.citation)

    def test_retriever_has_no_client_document_allowlist_parameter(self):
        self.assertNotIn(
            "allowed_document_ids", inspect.signature(DenseRetriever.search).parameters
        )
        self.assertIn("never accept an arbitrary `allowed_document_ids`", POLICY_CONTRACT)


if __name__ == "__main__":
    unittest.main()
