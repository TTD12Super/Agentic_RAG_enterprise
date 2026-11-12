"""QA for the checked-in synthetic sample corpus and typed citations."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid5

import pytest

from backend.app.authorization.policy import (
    Action,
    AuthorizationEvaluator,
    DocumentResource,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.guardrails import inspect_untrusted_content
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.ingestion import IngestionService, ScanReport, ScanVerdict, StagedIndex, UploadManifest
from backend.app.integrations.model_gateway import ModelGateway
from backend.app.knowledge.models import ChunkMetadata, DOCXLocator, PDFLocator, SourceSpan, XLSXLocator
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelRoute,
    ModelTask,
    ProviderPolicy,
)
from backend.app.rag import (
    AnswerStatus,
    DirectAnswerPipeline,
    DeterministicEmbeddingAdapter,
    DeterministicRerankerAdapter,
    GeneratedAnswer,
    HybridRetriever,
    InMemoryBM25Index,
    InMemoryDenseVectorIndex,
)


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "samples" / "rag" / "manifest.json"
POLICY_EPOCH = 7


def _manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _gateway() -> ModelGateway:
    provider = ProviderPolicy(
        provider_id="deterministic-local",
        egress_mode=EgressMode.LOCAL,
        allowed_classifications=frozenset(DataClassification),
        approved=True,
    )
    return ModelGateway(
        ModelPolicy(
            "sample-corpus-local",
            ModelRoute(ModelTask.EMBEDDING, provider, "deterministic", "1"),
            ModelRoute(ModelTask.RERANKER, provider, "deterministic", "1"),
        ),
        embedding_adapters={"deterministic-local": DeterministicEmbeddingAdapter()},
        reranker_adapters={"deterministic-local": DeterministicRerankerAdapter()},
    )


def _locator(payload: dict[str, object]):
    kind = payload["kind"]
    if kind == "PDF":
        span = payload["source_span"]
        return PDFLocator(
            page=payload["page"],
            source_span=SourceSpan(start=span["start"], end=span["end"]),
        )
    if kind == "DOCX":
        return DOCXLocator(heading=payload["heading"], paragraph=payload["paragraph"])
    if kind == "XLSX":
        return XLSXLocator(sheet=payload["sheet"], cell_range=payload["cell_range"])
    raise AssertionError(f"unsupported sample locator: {kind}")


@dataclass(frozen=True)
class _Corpus:
    principal: AuthenticatedPrincipal
    retriever: HybridRetriever
    pep: PolicyEnforcementPoint
    resources: dict[str, DocumentResource]
    contents: dict[str, str]


def _build_corpus() -> _Corpus:
    manifest = _manifest()
    tenant_id = UUID(manifest["tenant_id"])
    department_ids = [
        UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
        UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc"),
    ]
    principal = AuthenticatedPrincipal(
        user_id="sample-user",
        tenant_id=str(tenant_id),
        roles=["employee"],
        department_ids=[str(value) for value in department_ids],
        session_id="sample-session",
        auth_time="2026-11-10T00:00:00Z",
    )
    gateway = _gateway()
    ingestion = IngestionService()
    dense_index = InMemoryDenseVectorIndex(gateway)
    bm25_index = InMemoryBM25Index()
    resources: dict[str, DocumentResource] = {}
    contents: dict[str, str] = {}

    for raw_document in manifest["documents"]:
        document = dict(raw_document)
        content_path = ROOT / "samples" / "rag" / document["content_path"]
        content = content_path.read_text(encoding="utf-8")
        document_id = UUID(document["document_id"])
        version_id = UUID(document["version_id"])
        chunk_id = UUID(document["chunk_id"])
        classification = DataClassification(document["classification"])
        locator = _locator(document["locator"])
        owner_department_id = (
            UUID(document["owner_department_id"])
            if document["owner_department_id"]
            else None
        )
        manifest_record = UploadManifest(
            tenant_id=tenant_id,
            document_id=document_id,
            version_id=version_id,
            version_number=document["version_number"],
            title=document["title"],
            filename=document["filename"],
            source_uri=f"private://samples/rag/{document['filename']}",
            sha256=document["sha256"],
            size_bytes=document["size_bytes"],
            mime_type=document["mime_type"],
            classification=classification,
            owner_department_id=owner_department_id,
        )
        ingestion.quarantine_upload(manifest_record, idempotency_key=f"sample-upload:{version_id}")
        ingestion.scan(version_id, tenant_id, ScanReport(ScanVerdict.CLEAN))
        reviewer_id = uuid5(tenant_id, f"sample-reviewer:{version_id}")
        ingestion.approve_review1(
            version_id,
            tenant_id,
            reviewer_id,
            idempotency_key=f"sample-review-1:{version_id}",
        )
        chunk = ChunkMetadata(
            chunk_id=chunk_id,
            document_id=document_id,
            version_id=version_id,
            tenant_id=tenant_id,
            chunk_index=0,
            page_start=locator.page if isinstance(locator, PDFLocator) else None,
            page_end=locator.page if isinstance(locator, PDFLocator) else None,
            source_span=locator.source_span if isinstance(locator, PDFLocator) else None,
            source_locator=locator,
            acl_policy_ref=document["acl_policy_ref"],
            text_hash=document["sha256"],
        )
        record = ingestion.process(version_id, tenant_id, (chunk,))
        ingestion.stage_index(
            version_id,
            tenant_id,
            StagedIndex.from_chunks(
                publication_id=f"sample-publication:{version_id}",
                tenant_id=tenant_id,
                version_id=version_id,
                content_sha256=document["sha256"],
                chunks=record.chunks,
            ),
        )
        ingestion.acknowledge_index(version_id, tenant_id)
        ingestion.approve_review2(
            version_id,
            tenant_id,
            reviewer_id,
            idempotency_key=f"sample-review-2:{version_id}",
        )
        active_chunk = ingestion.publish(version_id, tenant_id).chunks[0]
        dense_index.upsert(active_chunk, content, classification=classification)
        bm25_index.upsert(active_chunk, content)
        resources[str(document_id)] = DocumentResource(
            document_id=str(document_id),
            tenant_id=str(tenant_id),
            classification=classification.value,
            current_version_id=str(version_id),
            version_id=str(version_id),
            version_status="ACTIVE",
            owner_department_id=(str(owner_department_id) if owner_department_id else None),
            policy_epoch=POLICY_EPOCH,
        )
        contents[str(document_id)] = content

    pep = PolicyEnforcementPoint(
        AuthorizationEvaluator(policy_store=InMemoryPolicyStore(policy_epoch=POLICY_EPOCH))
    )
    dense = __import__("backend.app.rag", fromlist=["DenseRetriever"]).DenseRetriever(
        index=dense_index,
        ingestion=ingestion,
        pep=pep,
        documents=resources,
        model_gateway=gateway,
    )
    return _Corpus(
        principal=principal,
        retriever=HybridRetriever(dense=dense, bm25=bm25_index, model_gateway=gateway),
        pep=pep,
        resources=resources,
        contents=contents,
    )


class _GroundedSampleAnswer:
    def __init__(self, text: str) -> None:
        self.text = text

    def generate(self, messages, *, classification):
        del messages, classification
        return GeneratedAnswer(self.text, (Claim("claim-1", self.text, ("c-1",)),))


def _authorize(corpus: _Corpus, citation) -> AuthorizationDecision:
    resource = corpus.resources.get(citation.document_id)
    if resource is None:
        return AuthorizationDecision(allowed=False)
    decision = corpus.pep.check(
        corpus.principal,
        Action.DOCUMENT_READ.value,
        resource,
        tenant_id=corpus.principal.tenant_id,
        policy_epoch=POLICY_EPOCH,
    )
    allowed = (
        decision.allowed
        and resource.tenant_id == citation.tenant_id
        and resource.version_id == citation.version_id
    )
    return AuthorizationDecision(
        allowed=allowed,
        tenant_id=resource.tenant_id if allowed else None,
        document_id=resource.document_id if allowed else None,
        version_id=resource.version_id if allowed else None,
        current_version_id=resource.current_version_id if allowed else None,
        status=resource.status if allowed else None,
    )


def test_sample_manifest_is_synthetic_hash_bound_and_private() -> None:
    manifest = _manifest()
    assert manifest["provenance"]["kind"] == "synthetic"
    assert manifest["provenance"]["external_sources"] == []
    assert len(manifest["documents"]) == 3
    for document in manifest["documents"]:
        content_path = ROOT / "samples" / "rag" / document["content_path"]
        content = content_path.read_bytes()
        assert len(content) == document["size_bytes"]
        assert hashlib.sha256(content).hexdigest() == document["sha256"]
        assert document["filename"].endswith((".pdf", ".docx", ".xlsx"))


@pytest.mark.parametrize(
    ("query", "document_id", "locator_kind"),
    [
        (
            "What approval is needed for equipment purchases above 5,000 USD?",
            "11111111-1111-4111-8111-111111111111",
            "PDF",
        ),
        (
            "How long are security audit logs retained?",
            "22222222-2222-4222-8222-222222222221",
            "DOCX",
        ),
        (
            "When must employees submit travel receipts?",
            "33333333-3333-4333-8333-333333333331",
            "XLSX",
        ),
    ],
)
def test_sample_query_returns_evidence_and_typed_citation(
    query: str, document_id: str, locator_kind: str
) -> None:
    corpus = _build_corpus()
    retrieval = corpus.retriever.search(query, corpus.principal, policy_epoch=POLICY_EPOCH, top_k=1)

    assert retrieval.status == "OK"
    assert retrieval.evidence[0].citation.document_id == document_id
    assert retrieval.evidence[0].citation.locator.kind == locator_kind

    answer = DirectAnswerPipeline(
        retriever=corpus.retriever,
        model_gateway=_GroundedSampleAnswer(corpus.contents[document_id]),
        authorize_citation=lambda citation: _authorize(corpus, citation),
        top_k=1,
    ).answer(query, corpus.principal, policy_epoch=POLICY_EPOCH)

    assert answer.status == AnswerStatus.ANSWERED
    assert answer.citations[0].document_id == document_id
    assert answer.citations[0].version_id == corpus.resources[document_id].version_id
    assert answer.citations[0].policy_epoch == POLICY_EPOCH
    assert answer.citations[0].locator.kind == locator_kind
    inspected = inspect_untrusted_content(corpus.contents[document_id])
    assert inspected.allowed and inspected.value is not None
    assert answer.citations[0].evidence_snapshot_hash == hashlib.sha256(
        inspected.value.encode("utf-8")
    ).hexdigest()


def test_no_answer_is_safe_when_sample_corpus_is_outside_tenant_scope() -> None:
    corpus = _build_corpus()
    foreign_principal = corpus.principal.model_copy(
        update={"tenant_id": "dddddddd-dddd-4ddd-8ddd-dddddddddddd", "department_ids": []}
    )
    answer = DirectAnswerPipeline(
        retriever=corpus.retriever,
        model_gateway=_GroundedSampleAnswer("must not be called"),
        authorize_citation=lambda citation: _authorize(corpus, citation),
    ).answer(
        _manifest()["queries"]["no_answer"],
        foreign_principal,
        policy_epoch=POLICY_EPOCH,
    )

    assert answer.status == AnswerStatus.INSUFFICIENT_EVIDENCE
    assert answer.answer == "Insufficient evidence to answer this question."
    assert answer.citations == ()
