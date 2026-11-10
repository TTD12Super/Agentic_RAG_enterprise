import unittest
from uuid import UUID

from backend.app.authorization.policy import (
    AccessGrant,
    Action,
    AuthorizationEvaluator,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.integrations.model_gateway import ModelGateway
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelRoute,
    ModelTask,
    ProviderPolicy,
)
from backend.app.rag.dense import DenseRetriever, DeterministicEmbeddingAdapter, InMemoryDenseVectorIndex
from backend.tests.test_dense_retrieval import (
    _active_document,
    _gateway,
    _principal,
    _resource,
    _retriever,
)


def _multi_retriever(ingestion, principal, records):
    gateway = _gateway()
    index = InMemoryDenseVectorIndex(gateway)
    documents = {}
    for document_id, version_id, department_id, chunk, text in records:
        index.upsert(chunk, text, classification=DataClassification.INTERNAL)
        documents[str(document_id)] = _resource(
            document_id, version_id, chunk.tenant_id, department_id
        )
    pep = PolicyEnforcementPoint(
        AuthorizationEvaluator(policy_store=InMemoryPolicyStore(policy_epoch=7))
    )
    return DenseRetriever(
        index=index,
        ingestion=ingestion,
        pep=pep,
        documents=documents,
        model_gateway=gateway,
    )


class DenseRetrievalBehaviorTests(unittest.TestCase):
    def test_authorized_dense_retrieval_returns_current_evidence(self):
        tenant_id = UUID("00000000-0000-0000-0000-000000000001")
        ingestion = __import__("backend.app.ingestion", fromlist=["IngestionService"]).IngestionService()
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
            text="authorized warranty coverage",
        )

        result = retriever.search("warranty", principal, policy_epoch=7)

        self.assertEqual(result.status, "OK")
        self.assertEqual(result.evidence[0].text, "authorized warranty coverage")
        self.assertEqual(result.evidence[0].citation.chunk_id, str(chunk.chunk_id))

    def test_tenant_isolation_filters_other_tenant_candidates(self):
        from backend.app.ingestion import IngestionService

        tenant_a = UUID("00000000-0000-0000-0000-000000000002")
        tenant_b = UUID("00000000-0000-0000-0000-000000000003")
        ingestion = IngestionService()
        first = _active_document(ingestion, tenant_id=tenant_a)
        second = _active_document(ingestion, tenant_id=tenant_b)
        principal = _principal(tenant_a, first[2])
        retriever = _multi_retriever(
            ingestion,
            principal,
            (
                (*first, "tenant-a policy"),
                (*second, "tenant-b secret"),
            ),
        )

        result = retriever.search("tenant-b secret", principal, policy_epoch=7)

        self.assertTrue(
            all(item.citation.document_id != str(second[0]) for item in result.evidence)
        )

    def test_explicit_read_deny_removes_candidate(self):
        from backend.app.ingestion import IngestionService

        tenant_id = UUID("00000000-0000-0000-0000-000000000004")
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
            text="explicitly denied source",
            acl=(deny,),
        )

        result = retriever.search("denied source", principal, policy_epoch=7)

        self.assertEqual(result.status, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result.evidence, ())

    def test_assigned_department_allows_internal_employee(self):
        from backend.app.ingestion import IngestionService

        tenant_id = UUID("00000000-0000-0000-0000-000000000005")
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
            text="assigned internal source",
        )

        self.assertEqual(
            retriever.search("assigned", principal, policy_epoch=7).status, "OK"
        )

    def test_unassigned_department_denies_internal_employee(self):
        from backend.app.ingestion import IngestionService

        tenant_id = UUID("00000000-0000-0000-0000-000000000006")
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
            text="unassigned internal source",
        )

        self.assertEqual(
            retriever.search("unassigned", principal, policy_epoch=7).evidence, ()
        )

    def test_superseded_version_is_not_retrievable(self):
        from backend.app.ingestion import IngestionService

        tenant_id = UUID("00000000-0000-0000-0000-000000000007")
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
            text="superseded source",
        )
        retriever = DenseRetriever(
            index=retriever._index,
            ingestion=ingestion,
            pep=retriever._pep,
            documents={
                str(document_id): _resource(
                    document_id,
                    version_id,
                    tenant_id,
                    department_id,
                    version_status="SUPERSEDED",
                )
            },
            model_gateway=retriever._model_gateway,
        )

        self.assertEqual(
            retriever.search("superseded", principal, policy_epoch=7).evidence, ()
        )

    def test_staging_index_is_not_retrievable(self):
        from backend.app.ingestion import IngestionService

        tenant_id = UUID("00000000-0000-0000-0000-000000000008")
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
            chunk=chunk.model_copy(update={"index_state": "STAGING"}),
            text="staging source",
        )

        self.assertEqual(
            retriever.search("staging", principal, policy_epoch=7).evidence, ()
        )

    def test_source_fetch_requires_read_permission(self):
        from backend.app.ingestion import IngestionService

        tenant_id = UUID("00000000-0000-0000-0000-000000000009")
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
            text="read denied source",
            acl=(deny,),
        )

        source = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)

        self.assertTrue(source.redacted)
        self.assertIsNone(source.content)
        self.assertIsNone(source.citation)

    def test_ranking_is_deterministic_and_top_k_is_applied(self):
        from backend.app.ingestion import IngestionService

        tenant_id = UUID("00000000-0000-0000-0000-000000000010")
        ingestion = IngestionService()
        first = _active_document(ingestion, tenant_id=tenant_id)
        second = _active_document(ingestion, tenant_id=tenant_id)
        principal = _principal(tenant_id, first[2]).model_copy(
            update={"department_ids": [str(first[2]), str(second[2])]}
        )
        retriever = _multi_retriever(
            ingestion,
            principal,
            (
                (*first, "alpha warranty"),
                (*second, "alpha alpha warranty"),
            ),
        )

        first_run = retriever.search("alpha", principal, policy_epoch=7, top_k=1)
        second_run = retriever.search("alpha", principal, policy_epoch=7, top_k=1)

        self.assertEqual(len(first_run.evidence), 1)
        self.assertEqual(first_run.evidence, second_run.evidence)

    def test_internal_query_egress_denial_fails_closed(self):
        from backend.app.ingestion import IngestionService

        tenant_id = UUID("00000000-0000-0000-0000-000000000011")
        ingestion = IngestionService()
        document_id, version_id, department_id, chunk = _active_document(
            ingestion, tenant_id=tenant_id
        )
        principal = _principal(tenant_id, department_id)
        local = _retriever(
            ingestion,
            principal=principal,
            document_id=document_id,
            version_id=version_id,
            department_id=department_id,
            chunk=chunk,
            text="internal egress boundary",
        )
        provider = ProviderPolicy(
            provider_id="external-blocked",
            egress_mode=EgressMode.EXTERNAL,
            allowed_classifications=frozenset({DataClassification.INTERNAL}),
            approved=True,
            request_retention_seconds=0,
        )
        route = ModelRoute(ModelTask.EMBEDDING, provider, "embedding", "1")
        reranker = ModelRoute(ModelTask.RERANKER, provider, "reranker", "1")
        blocked = ModelGateway(
            ModelPolicy("blocked-policy", route, reranker),
            embedding_adapters={"external-blocked": DeterministicEmbeddingAdapter()},
            reranker_adapters={},
        )
        retriever = DenseRetriever(
            index=local._index,
            ingestion=ingestion,
            pep=local._pep,
            documents=local._documents,
            model_gateway=blocked,
        )

        result = retriever.search("egress boundary", principal, policy_epoch=7)

        self.assertEqual(result.status, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result.evidence, ())


if __name__ == "__main__":
    unittest.main()
