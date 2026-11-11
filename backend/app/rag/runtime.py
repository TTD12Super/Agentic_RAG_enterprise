"""Small local runtime that connects the chat API to the RAG pipeline.

This is a development adapter: it exercises the real ingestion lifecycle,
permission-aware hybrid retrieval and answer/citation verification with one
synthetic PUBLIC document. Provider-backed model and durable index adapters can
replace this seam without changing the chat API.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, UUID, uuid5

from backend.app.authorization import (
    Action,
    AnonymousPrincipal,
    AuthorizationEvaluator,
    DocumentResource,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.ingestion.lifecycle import (
    IngestionService,
    ScanReport,
    ScanVerdict,
    StagedIndex,
    UploadManifest,
)
from backend.app.integrations.model_gateway import ModelGateway
from backend.app.knowledge.models import ChunkMetadata, PDFLocator, SourceSpan
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelRoute,
    ModelTask,
    ProviderPolicy,
)
from backend.app.rag.answer import DirectAnswerPipeline, GeneratedAnswer
from backend.app.rag.dense import (
    DenseRetriever,
    DeterministicEmbeddingAdapter,
    InMemoryDenseVectorIndex,
)
from backend.app.rag.hybrid import (
    DeterministicRerankerAdapter,
    HybridRetriever,
    InMemoryBM25Index,
)


PUBLIC_TENANT_ID = "public"
PUBLIC_TENANT_UUID = uuid5(NAMESPACE_URL, "enterprise-agentic-rag:public")
PUBLIC_DOCUMENT_ID = uuid5(NAMESPACE_URL, "enterprise-agentic-rag:public-equipment-policy")
PUBLIC_VERSION_ID = uuid5(NAMESPACE_URL, "enterprise-agentic-rag:public-equipment-policy:v1")
PUBLIC_CHUNK_ID = uuid5(NAMESPACE_URL, "enterprise-agentic-rag:public-equipment-policy:chunk-1")
PUBLIC_POLICY_TEXT = (
    "Chính sách công khai quy định đề xuất mua sắm thiết bị phải được phòng ban "
    "xem xét trước khi mua."
)

Principal = AuthenticatedPrincipal | AnonymousPrincipal


class _LocalAnswerModel:
    def generate(
        self,
        messages: tuple[Mapping[str, str], ...],
        *,
        classification: DataClassification,
    ) -> GeneratedAnswer:
        del classification
        query = " ".join(message["content"] for message in messages if message.get("role") == "user")
        terms = query.casefold()
        if not any(term in terms for term in ("thiết bị", "mua sắm", "equipment", "purchasing")):
            return GeneratedAnswer("", ())
        return GeneratedAnswer(
            PUBLIC_POLICY_TEXT,
            (Claim("claim-1", PUBLIC_POLICY_TEXT, ("c-1",)),),
        )


class LocalRagExecutor:
    """QueryExecutor backed by the real local retrieval and answer pipeline."""

    def __init__(self) -> None:
        self._contexts: dict[str, tuple[Principal, int]] = {}
        self._policy_store = InMemoryPolicyStore(policy_epoch=1)
        self._pep = PolicyEnforcementPoint(AuthorizationEvaluator(self._policy_store))
        self._ingestion = IngestionService()
        self._model_gateway = self._make_model_gateway()
        self._documents = self._publish_fixture()
        dense_index = InMemoryDenseVectorIndex(self._model_gateway)
        bm25_index = InMemoryBM25Index()
        chunk = self._ingestion.retrievable_chunks(PUBLIC_DOCUMENT_ID, PUBLIC_TENANT_UUID)[0]
        dense_index.upsert(chunk, PUBLIC_POLICY_TEXT, classification=DataClassification.PUBLIC)
        bm25_index.upsert(chunk, PUBLIC_POLICY_TEXT)
        dense = DenseRetriever(
            index=dense_index,
            ingestion=self._ingestion,
            pep=self._pep,
            documents=self._documents,
            model_gateway=self._model_gateway,
        )
        self._retriever = HybridRetriever(dense=dense, bm25=bm25_index, model_gateway=self._model_gateway)

    @staticmethod
    def _make_model_gateway() -> ModelGateway:
        provider = ProviderPolicy(
            provider_id="deterministic-local",
            egress_mode=EgressMode.LOCAL,
            allowed_classifications=frozenset(DataClassification),
            approved=True,
        )
        embedding = ModelRoute(ModelTask.EMBEDDING, provider, "deterministic", "1")
        reranker = ModelRoute(ModelTask.RERANKER, provider, "deterministic", "1")
        return ModelGateway(
            ModelPolicy("local-runtime", embedding, reranker),
            embedding_adapters={"deterministic-local": DeterministicEmbeddingAdapter()},
            reranker_adapters={"deterministic-local": DeterministicRerankerAdapter()},
        )

    def _publish_fixture(self) -> dict[str, DocumentResource]:
        text_hash = hashlib.sha256(PUBLIC_POLICY_TEXT.encode()).hexdigest()
        manifest = UploadManifest(
            tenant_id=PUBLIC_TENANT_UUID,
            document_id=PUBLIC_DOCUMENT_ID,
            version_id=PUBLIC_VERSION_ID,
            version_number=1,
            title="Public equipment policy",
            filename="public-equipment-policy.pdf",
            source_uri="private://runtime/public-equipment-policy.pdf",
            sha256=text_hash,
            size_bytes=len(PUBLIC_POLICY_TEXT.encode()),
            mime_type="application/pdf",
            classification=DataClassification.PUBLIC,
        )
        self._ingestion.quarantine_upload(manifest, idempotency_key="local-runtime-upload-v1")
        self._ingestion.scan(PUBLIC_VERSION_ID, PUBLIC_TENANT_UUID, ScanReport(ScanVerdict.CLEAN))
        reviewer = uuid5(NAMESPACE_URL, "enterprise-agentic-rag:local-reviewer")
        self._ingestion.approve_review1(PUBLIC_VERSION_ID, PUBLIC_TENANT_UUID, reviewer, idempotency_key="local-runtime-review-1")
        chunk = ChunkMetadata(
            chunk_id=PUBLIC_CHUNK_ID,
            document_id=PUBLIC_DOCUMENT_ID,
            version_id=PUBLIC_VERSION_ID,
            tenant_id=PUBLIC_TENANT_UUID,
            chunk_index=0,
            page_start=1,
            page_end=1,
            source_span=SourceSpan(start=0, end=len(PUBLIC_POLICY_TEXT)),
            source_locator=PDFLocator(page=1, source_span=SourceSpan(start=0, end=len(PUBLIC_POLICY_TEXT))),
            acl_policy_ref="public-policy",
            text_hash=text_hash,
        )
        self._ingestion.process(PUBLIC_VERSION_ID, PUBLIC_TENANT_UUID, (chunk,))
        self._ingestion.stage_index(
            PUBLIC_VERSION_ID,
            PUBLIC_TENANT_UUID,
            StagedIndex.from_chunks(
                publication_id="local-runtime-public-publication",
                tenant_id=PUBLIC_TENANT_UUID,
                version_id=PUBLIC_VERSION_ID,
                content_sha256=text_hash,
                chunks=(chunk,),
            ),
        )
        self._ingestion.acknowledge_index(PUBLIC_VERSION_ID, PUBLIC_TENANT_UUID)
        self._ingestion.approve_review2(PUBLIC_VERSION_ID, PUBLIC_TENANT_UUID, reviewer, idempotency_key="local-runtime-review-2")
        self._ingestion.publish(PUBLIC_VERSION_ID, PUBLIC_TENANT_UUID)
        return {
            str(PUBLIC_DOCUMENT_ID): DocumentResource(
                document_id=str(PUBLIC_DOCUMENT_ID),
                tenant_id=PUBLIC_TENANT_ID,
                classification=DataClassification.PUBLIC.value,
                current_version_id=str(PUBLIC_VERSION_ID),
                version_id=str(PUBLIC_VERSION_ID),
                version_status="ACTIVE",
                policy_epoch=1,
            )
        }

    def bind_context(self, principal_ref: str, principal: Principal, policy_epoch: int) -> None:
        self._contexts[principal_ref] = (principal, policy_epoch)

    def run(self, request: object) -> object:
        context = self._contexts.get(getattr(request, "principal_ref", ""))
        if context is None:
            from backend.app.orchestration import OrchestrationOutcome, OrchestrationStatus

            return OrchestrationOutcome(OrchestrationStatus.ERROR, reason_codes=("RAG_CONTEXT_UNAVAILABLE",))
        principal, policy_epoch = context

        def authorize(citation: object) -> AuthorizationDecision:
            resource = self._documents.get(str(getattr(citation, "document_id", "")))
            if resource is None:
                return AuthorizationDecision(allowed=False)
            decision = self._pep.check(
                principal,
                Action.DOCUMENT_READ.value,
                resource,
                tenant_id=principal.tenant_id,
                policy_epoch=policy_epoch,
            )
            return AuthorizationDecision(
                allowed=decision.allowed,
                tenant_id=principal.tenant_id if decision.allowed else None,
                document_id=resource.document_id if decision.allowed else None,
                version_id=resource.version_id if decision.allowed else None,
                current_version_id=resource.current_version_id if decision.allowed else None,
                status=resource.status if decision.allowed else None,
            )

        return DirectAnswerPipeline(
            retriever=self._retriever,
            model_gateway=_LocalAnswerModel(),
            authorize_citation=authorize,
        ).answer(
            getattr(request, "query", ""),
            principal,  # type: ignore[arg-type]
            policy_epoch=policy_epoch,
        )


__all__ = ["LocalRagExecutor"]
