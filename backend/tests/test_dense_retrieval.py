from uuid import UUID, uuid4

from backend.app.authorization.policy import (
    AccessGrant,
    Action,
    AuthorizationEvaluator,
    DocumentResource,
    Effect,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.ingestion.lifecycle import (
    IngestionService,
    ScanReport,
    ScanVerdict,
    StagedIndex,
    UploadManifest,
)
from backend.app.knowledge.models import ChunkMetadata, SourceSpan
from backend.app.integrations.model_gateway import ModelGateway
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelRoute,
    ModelTask,
    ProviderPolicy,
)
from backend.app.rag.dense import (
    DenseRetriever,
    DeterministicEmbeddingAdapter,
    InMemoryDenseVectorIndex,
)


def _gateway() -> ModelGateway:
    provider = ProviderPolicy(
        provider_id="deterministic-local",
        egress_mode=EgressMode.LOCAL,
        allowed_classifications=frozenset(DataClassification),
        approved=True,
    )
    embedding = ModelRoute(ModelTask.EMBEDDING, provider, "deterministic", "1")
    reranker = ModelRoute(ModelTask.RERANKER, provider, "deterministic", "1")
    policy = ModelPolicy("test-policy", embedding, reranker)
    return ModelGateway(
        policy,
        embedding_adapters={"deterministic-local": DeterministicEmbeddingAdapter()},
        reranker_adapters={},
    )


def _active_document(
    ingestion: IngestionService,
    *,
    tenant_id: UUID,
    classification: DataClassification = DataClassification.INTERNAL,
) -> tuple[UUID, UUID, UUID, ChunkMetadata]:
    document_id, version_id, department_id = uuid4(), uuid4(), uuid4()
    manifest = UploadManifest(
        tenant_id=tenant_id,
        document_id=document_id,
        version_id=version_id,
        version_number=1,
        title="Synthetic policy",
        filename="policy.pdf",
        source_uri="private://documents/policy-v1",
        sha256="a" * 64,
        size_bytes=10,
        mime_type="application/pdf",
        classification=classification,
        owner_department_id=department_id if classification is DataClassification.INTERNAL else None,
    )
    ingestion.quarantine_upload(manifest, idempotency_key=str(version_id))
    ingestion.scan(version_id, tenant_id, ScanReport(ScanVerdict.CLEAN))
    reviewer_id = uuid4()
    ingestion.approve_review1(version_id, tenant_id, reviewer_id, idempotency_key="review-1")
    chunk = ChunkMetadata(
        chunk_id=uuid4(),
        tenant_id=tenant_id,
        document_id=document_id,
        version_id=version_id,
        chunk_index=0,
        page_start=2,
        page_end=2,
        source_span=SourceSpan(start=4, end=28),
        acl_policy_ref="policy-1",
        text_hash="b" * 64,
    )
    ingestion.process(version_id, tenant_id, (chunk,))
    staged = StagedIndex.from_chunks(
        publication_id=f"pub-{version_id}",
        tenant_id=tenant_id,
        version_id=version_id,
        content_sha256="a" * 64,
        chunks=(chunk,),
    )
    ingestion.stage_index(version_id, tenant_id, staged)
    ingestion.acknowledge_index(version_id, tenant_id)
    ingestion.approve_review2(version_id, tenant_id, reviewer_id, idempotency_key="review-2")
    active = ingestion.publish(version_id, tenant_id)
    return document_id, version_id, department_id, active.chunks[0]


def _principal(tenant_id: UUID, department_id: UUID) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=str(uuid4()),
        tenant_id=str(tenant_id),
        roles=["employee"],
        department_ids=[str(department_id)],
        session_id="session-1",
        auth_time="2026-11-10T00:00:00Z",
    )


def _retriever(
    ingestion: IngestionService,
    *,
    principal: AuthenticatedPrincipal,
    document_id: UUID,
    version_id: UUID,
    department_id: UUID,
    chunk: ChunkMetadata,
    text: str,
    acl: tuple[AccessGrant, ...] = (),
    policy_epoch: int = 7,
) -> DenseRetriever:
    gateway = _gateway()
    index = InMemoryDenseVectorIndex(gateway)
    index.upsert(chunk, text, classification=DataClassification.INTERNAL)
    resource = DocumentResource(
        document_id=str(document_id),
        tenant_id=principal.tenant_id,
        classification="INTERNAL",
        current_version_id=str(version_id),
        version_id=str(version_id),
        owner_department_id=str(department_id),
        acl=acl,
        policy_epoch=policy_epoch,
    )
    store = InMemoryPolicyStore(policy_epoch=policy_epoch)
    pep = PolicyEnforcementPoint(AuthorizationEvaluator(policy_store=store))
    return DenseRetriever(
        index=index,
        ingestion=ingestion,
        pep=pep,
        documents={str(document_id): resource},
        model_gateway=gateway,
    )


def _resource(
    document_id: UUID,
    version_id: UUID,
    tenant_id: UUID,
    department_id: UUID,
    *,
    acl: tuple[AccessGrant, ...] = (),
    version_status: str = "ACTIVE",
) -> DocumentResource:
    return DocumentResource(
        document_id=str(document_id),
        tenant_id=str(tenant_id),
        classification="INTERNAL",
        current_version_id=str(version_id),
        version_id=str(version_id),
        version_status=version_status,
        owner_department_id=str(department_id),
        acl=acl,
        policy_epoch=7,
    )


def test_dense_retrieval_returns_authorized_current_chunk_only():
    tenant_id = uuid4()
    ingestion = IngestionService()
    document_id, version_id, department_id, chunk = _active_document(
        ingestion,
        tenant_id=tenant_id,
    )
    principal = _principal(tenant_id, department_id)
    retriever = _retriever(
        ingestion,
        principal=principal,
        document_id=document_id,
        version_id=version_id,
        department_id=department_id,
        chunk=chunk,
        text="Warranty coverage applies to product A.",
    )

    result = retriever.search("product A warranty", principal, policy_epoch=7, top_k=3)

    assert result.status == "OK"
    assert len(result.evidence) == 1
    assert result.evidence[0].text == "Warranty coverage applies to product A."
    assert result.evidence[0].citation.version_id == str(version_id)
    source = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)
    assert source.redacted is False
    assert source.content == "Warranty coverage applies to product A."
    assert source.citation == result.evidence[0].citation


def test_explicit_deny_candidates_are_not_exposed():
    tenant_id = uuid4()
    ingestion = IngestionService()
    document_id, version_id, department_id, chunk = _active_document(
        ingestion,
        tenant_id=tenant_id,
    )
    principal = _principal(tenant_id, department_id)
    denied = AccessGrant(
        action=Action.DOCUMENT_READ.value,
        effect=Effect.DENY.value,
        user_id=principal.user_id,
    )
    retriever = _retriever(
        ingestion,
        principal=principal,
        document_id=document_id,
        version_id=version_id,
        department_id=department_id,
        chunk=chunk,
        text="restricted source content",
        acl=(denied,),
    )

    result = retriever.search("restricted source", principal, policy_epoch=7)

    assert result.evidence == ()
    assert result.status == "INSUFFICIENT_EVIDENCE"


def test_cross_tenant_candidates_are_not_exposed():
    tenant_a, tenant_b = uuid4(), uuid4()
    ingestion = IngestionService()
    document_a, version_a, department_a, chunk_a = _active_document(
        ingestion,
        tenant_id=tenant_a,
    )
    document_b, version_b, department_b, chunk_b = _active_document(
        ingestion,
        tenant_id=tenant_b,
    )
    principal = _principal(tenant_a, department_a)
    gateway = _gateway()
    index = InMemoryDenseVectorIndex(gateway)
    index.upsert(chunk_a, "alpha internal source", classification=DataClassification.INTERNAL)
    index.upsert(chunk_b, "beta internal source", classification=DataClassification.INTERNAL)
    pep = PolicyEnforcementPoint(AuthorizationEvaluator(policy_store=InMemoryPolicyStore(policy_epoch=7)))
    retriever = DenseRetriever(
        index=index,
        ingestion=ingestion,
        pep=pep,
        documents={
            str(document_a): _resource(document_a, version_a, tenant_a, department_a),
            str(document_b): _resource(document_b, version_b, tenant_b, department_b),
        },
        model_gateway=gateway,
    )

    result = retriever.search("beta", principal, policy_epoch=7)

    assert all(item.citation.document_id != str(document_b) for item in result.evidence)


def test_stale_policy_and_non_active_version_fail_closed():
    tenant_id = uuid4()
    ingestion = IngestionService()
    document_id, version_id, department_id, chunk = _active_document(
        ingestion,
        tenant_id=tenant_id,
    )
    principal = _principal(tenant_id, department_id)
    retriever = _retriever(
        ingestion,
        principal=principal,
        document_id=document_id,
        version_id=version_id,
        department_id=department_id,
        chunk=chunk,
        text="current approved source",
    )

    assert retriever.search("approved source", principal, policy_epoch=6).evidence == ()

    resource = DocumentResource(
        document_id=str(document_id),
        tenant_id=principal.tenant_id,
        classification="INTERNAL",
        current_version_id=str(version_id),
        version_id=str(version_id),
        version_status="SUPERSEDED",
        owner_department_id=str(department_id),
        policy_epoch=7,
    )
    stale_version_retriever = DenseRetriever(
        index=retriever._index,
        ingestion=ingestion,
        pep=retriever._pep,
        documents={str(document_id): resource},
        model_gateway=retriever._model_gateway,
    )
    assert stale_version_retriever.search("approved source", principal, policy_epoch=7).evidence == ()

    staging_index = InMemoryDenseVectorIndex(retriever._model_gateway)
    staging_index.upsert(
        chunk.model_copy(update={"index_state": "STAGING"}),
        "current approved source",
        classification=DataClassification.INTERNAL,
    )
    staging_retriever = DenseRetriever(
        index=staging_index,
        ingestion=ingestion,
        pep=retriever._pep,
        documents={str(document_id): _resource(document_id, version_id, tenant_id, department_id)},
        model_gateway=retriever._model_gateway,
    )
    assert staging_retriever.search("approved source", principal, policy_epoch=7).evidence == ()


def test_forbidden_source_fetch_is_redacted_without_content_or_citation():
    tenant_id = uuid4()
    ingestion = IngestionService()
    document_id, version_id, department_id, chunk = _active_document(
        ingestion,
        tenant_id=tenant_id,
    )
    principal = _principal(tenant_id, department_id)
    denied = AccessGrant(
        action=Action.SOURCE_DOWNLOAD.value,
        effect=Effect.DENY.value,
        user_id=principal.user_id,
    )
    retriever = _retriever(
        ingestion,
        principal=principal,
        document_id=document_id,
        version_id=version_id,
        department_id=department_id,
        chunk=chunk,
        text="do not return this source",
        acl=(denied,),
    )

    result = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)

    assert retriever.search("do not return this source", principal, policy_epoch=7).status == "OK"
    assert result.redacted is True
    assert result.content is None
    assert result.citation is None
