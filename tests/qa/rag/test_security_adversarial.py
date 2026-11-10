import unittest
from uuid import UUID

from backend.app.authorization.policy import AccessGrant, Action
from backend.app.ingestion import IngestionService
from backend.app.integrations.model_gateway import ModelEgressDenied, ModelGateway
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelRoute,
    ModelTask,
    ProviderPolicy,
)
from backend.app.rag.dense import DeterministicEmbeddingAdapter
from backend.tests.test_dense_retrieval import (
    _active_document,
    _principal,
    _retriever,
)


class DenseRetrievalSecurityAdversarialTests(unittest.TestCase):
    def test_malformed_chunk_id_is_redacted(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000051")
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
            text="malformed id source",
        )

        source = retriever.fetch_source("not-a-uuid", principal, policy_epoch=7)

        self.assertTrue(source.redacted)
        self.assertIsNone(source.content)
        self.assertIsNone(source.citation)

    def test_foreign_tenant_chunk_id_cannot_be_fetched(self):
        tenant_a = UUID("00000000-0000-0000-0000-000000000052")
        tenant_b = UUID("00000000-0000-0000-0000-000000000053")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_a
        )
        principal = _principal(tenant_b, department_id)
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="foreign tenant secret",
        )

        source = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)

        self.assertTrue(source.redacted)
        self.assertNotIn("foreign tenant secret", repr(source))

    def test_empty_query_is_rejected(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000054")
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
            text="query boundary source",
        )

        with self.assertRaises(ValueError):
            retriever.search("", principal, policy_epoch=7)

    def test_whitespace_query_is_rejected(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000055")
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
            text="query boundary source",
        )

        with self.assertRaises(ValueError):
            retriever.search(" \t\n", principal, policy_epoch=7)

    def test_nonpositive_top_k_is_rejected(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000056")
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
            text="top k boundary source",
        )

        for top_k in (0, -1):
            with self.subTest(top_k=top_k), self.assertRaises(ValueError):
                retriever.search("top", principal, policy_epoch=7, top_k=top_k)

    def test_malformed_top_k_cannot_return_evidence(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000057")
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
            text="malformed top k secret",
        )

        with self.assertRaises((TypeError, ValueError)):
            retriever.search("secret", principal, policy_epoch=7, top_k="all")

    def test_explicit_read_deny_leaks_neither_text_nor_citation(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000058")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        deny = AccessGrant(
            Action.DOCUMENT_READ.value, "DENY", user_id=principal.user_id
        )
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="classified adversarial payload",
            acl=(deny,),
        )

        result = retriever.search("classified", principal, policy_epoch=7)

        self.assertEqual(result.evidence, ())
        self.assertNotIn("classified adversarial payload", repr(result))
        self.assertNotIn(str(chunk.chunk_id), repr(result))

    def test_unassigned_department_leaks_neither_text_nor_citation(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000059")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, UUID("00000000-0000-0000-0000-000000000099"))
        retriever = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="department restricted payload",
        )

        result = retriever.search("restricted", principal, policy_epoch=7)

        self.assertEqual(result.evidence, ())
        self.assertNotIn("department restricted payload", repr(result))
        self.assertNotIn(str(chunk.chunk_id), repr(result))

    def test_stale_policy_epoch_leaks_no_candidate_metadata(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000060")
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
            text="stale policy payload",
        )

        result = retriever.search("stale", principal, policy_epoch=6)

        self.assertEqual(result.evidence, ())
        self.assertNotIn(str(chunk.chunk_id), repr(result))

    def test_external_internal_model_egress_is_denied_without_secret_echo(self):
        provider = ProviderPolicy(
            provider_id="external-adversarial",
            egress_mode=EgressMode.EXTERNAL,
            allowed_classifications=frozenset({DataClassification.INTERNAL}),
            approved=True,
            request_retention_seconds=0,
        )
        embedding = ModelRoute(ModelTask.EMBEDDING, provider, "embedding", "1")
        reranker = ModelRoute(ModelTask.RERANKER, provider, "reranker", "1")
        gateway = ModelGateway(
            ModelPolicy("egress-security", embedding, reranker),
            embedding_adapters={
                "external-adversarial": DeterministicEmbeddingAdapter()
            },
            reranker_adapters={},
        )

        with self.assertRaises(ModelEgressDenied) as raised:
            gateway.embed(("do-not-egress-this-secret",), classification=DataClassification.INTERNAL)

        self.assertNotIn("do-not-egress-this-secret", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
