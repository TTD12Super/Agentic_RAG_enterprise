"""Small local runtime that connects the chat API to the RAG pipeline.

The adapter loads the checked-in synthetic corpus through the same ingestion,
authorization, hybrid retrieval and citation verification seams used by the
production boundary. The older public fixture remains for compatibility with
the baseline chat tests.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
from collections.abc import Iterator, Mapping
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from backend.app.authorization import (
    Action,
    AnonymousPrincipal,
    AuthorizationEvaluator,
    DocumentResource,
    InMemoryPolicyStore,
    PolicyEnforcementPoint,
)
from backend.app.core.config import get_settings
from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.guardrails import validate_output
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.ingestion.lifecycle import (
    IngestionService,
    ScanReport,
    ScanVerdict,
    StagedIndex,
    UploadManifest,
)
from backend.app.integrations.gemini import GeminiProviderError, GeminiStreamProvider
from backend.app.integrations.model_gateway import ModelGateway
from backend.app.knowledge.models import (
    ChunkMetadata,
    DOCXLocator,
    PDFLocator,
    SourceSpan,
    XLSXLocator,
)
from backend.app.models.policy import (
    DataClassification,
    EgressMode,
    ModelPolicy,
    ModelRoute,
    ModelTask,
    ProviderPolicy,
)
from backend.app.rag.answer import AnswerCitation, AnswerStatus, DirectAnswerPipeline, GeneratedAnswer
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
LOCAL_DEMO_CHUNK_DELAY_SECONDS = 0.22
LOCAL_DEMO_CHUNK_SIZE = 56


class _LocalAnswerModel:
    _CONTENT_PATTERN = re.compile(r"<CONTENT>\n(.*?)\n</CONTENT>", re.DOTALL)

    def generate(
        self,
        messages: tuple[Mapping[str, str], ...],
        *,
        classification: DataClassification,
    ) -> GeneratedAnswer:
        del classification
        query_message = next(
            (
                message.get("content", "")
                for message in messages
                if "<<<USER_QUERY>>>" in message.get("content", "")
            ),
            "",
        )
        query = query_message.split("<<<USER_QUERY>>>", 1)[-1].split(
            "<<<END_USER_QUERY>>>", 1
        )[0]
        terms = query.casefold()
        evidence = [
            html.unescape(match)
            for message in messages
            for match in self._CONTENT_PATTERN.findall(message.get("content", ""))
        ]
        if not evidence:
            return GeneratedAnswer("", ())
        selected = _relevant_evidence(query, evidence)
        if any(
            term in terms for term in ("thiết bị", "mua sắm", "equipment", "purchasing")
        ):
            legacy = tuple(item for item in evidence if PUBLIC_POLICY_TEXT in item)
            detailed = any(term in terms for term in ("above", "5000", "5,000", "approval"))
            selected = tuple(dict.fromkeys((*legacy, *selected))) if detailed else legacy or selected
        if not selected:
            return GeneratedAnswer("", ())
        answer = "\n\n".join(dict.fromkeys(selected))
        return GeneratedAnswer(
            answer,
            tuple(
                Claim(f"claim-{index}", item, (f"c-{evidence.index(item) + 1}",))
                for index, item in enumerate(selected, 1)
            ),
        )


class LocalRagExecutor:
    """QueryExecutor backed by the real local retrieval and answer pipeline."""

    def __init__(self, *, gemini_provider: GeminiStreamProvider | None = None) -> None:
        self._contexts: dict[str, tuple[Principal, int]] = {}
        self._index_records: list[tuple[ChunkMetadata, str, DataClassification]] = []
        self._source_metadata: dict[str, dict[str, object]] = {}
        self._policy_store = InMemoryPolicyStore(policy_epoch=1)
        self._pep = PolicyEnforcementPoint(AuthorizationEvaluator(self._policy_store))
        self._ingestion = IngestionService()
        self._model_gateway = self._make_model_gateway()
        settings = get_settings()
        self._gemini_provider = gemini_provider or (
            GeminiStreamProvider(settings.gemini_api_key, settings.gemini_model)
            if settings.gemini_api_key
            else None
        )
        self._answer_model = _LocalAnswerModel()
        self._documents = {**self._publish_fixture(), **self._publish_sample_corpus()}
        dense_index = InMemoryDenseVectorIndex(self._model_gateway)
        bm25_index = InMemoryBM25Index()
        for chunk, text, classification in self._index_records:
            dense_index.upsert(chunk, text, classification=classification)
            bm25_index.upsert(chunk, text)
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
        active_chunk = self._ingestion.retrievable_chunks(PUBLIC_DOCUMENT_ID, PUBLIC_TENANT_UUID)[0]
        self._index_records.append((active_chunk, PUBLIC_POLICY_TEXT, DataClassification.PUBLIC))
        self._source_metadata[str(PUBLIC_DOCUMENT_ID)] = {
            "title": "Public equipment policy",
            "filename": "public-equipment-policy.pdf",
            "mime_type": "application/pdf",
            "preview": PUBLIC_POLICY_TEXT,
            "download": PUBLIC_POLICY_TEXT.encode("utf-8"),
            "location": {"kind": "PDF", "page": 1, "source_span": {"start": 0, "end": len(PUBLIC_POLICY_TEXT)}},
            "owner_department_id": None,
            "version_id": str(PUBLIC_VERSION_ID),
        }
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

    def _publish_sample_corpus(self) -> dict[str, DocumentResource]:
        """Load the checked-in synthetic corpus into the local runtime."""

        corpus_root = Path(__file__).resolve().parents[3] / "samples" / "rag"
        manifest = json.loads((corpus_root / "manifest.json").read_text(encoding="utf-8"))
        runtime_documents: dict[str, DocumentResource] = {}
        reviewer = uuid5(NAMESPACE_URL, "enterprise-agentic-rag:sample-reviewer")

        for raw_document in manifest["documents"]:
            document = dict(raw_document)
            content = (corpus_root / document["content_path"]).read_text(encoding="utf-8")
            content_bytes = content.encode("utf-8")
            if (
                len(content_bytes) != document["size_bytes"]
                or hashlib.sha256(content_bytes).hexdigest() != document["sha256"]
            ):
                raise ValueError(f"sample corpus integrity check failed: {document['filename']}")

            document_id = UUID(document["document_id"])
            version_id = UUID(document["version_id"])
            chunk_id = UUID(document["chunk_id"])
            classification = DataClassification(document["classification"])
            owner_department_id = (
                UUID(document["owner_department_id"])
                if document["owner_department_id"]
                else None
            )
            locator_payload = document["locator"]
            if locator_payload["kind"] == "PDF":
                locator = PDFLocator(
                    page=locator_payload["page"],
                    source_span=SourceSpan(start=0, end=len(content)),
                )
            elif locator_payload["kind"] == "DOCX":
                locator = DOCXLocator(
                    heading=locator_payload["heading"], paragraph=locator_payload["paragraph"]
                )
            elif locator_payload["kind"] == "XLSX":
                locator = XLSXLocator(
                    sheet=locator_payload["sheet"], cell_range=locator_payload["cell_range"]
                )
            else:
                raise ValueError(f"unsupported sample locator: {locator_payload['kind']}")

            upload = UploadManifest(
                tenant_id=PUBLIC_TENANT_UUID,
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
            self._ingestion.quarantine_upload(upload, idempotency_key=f"local-sample-upload:{version_id}")
            self._ingestion.scan(version_id, PUBLIC_TENANT_UUID, ScanReport(ScanVerdict.CLEAN))
            self._ingestion.approve_review1(
                version_id,
                PUBLIC_TENANT_UUID,
                reviewer,
                idempotency_key=f"local-sample-review-1:{version_id}",
            )
            chunk = ChunkMetadata(
                chunk_id=chunk_id,
                document_id=document_id,
                version_id=version_id,
                tenant_id=PUBLIC_TENANT_UUID,
                chunk_index=0,
                page_start=locator.page if isinstance(locator, PDFLocator) else None,
                page_end=locator.page if isinstance(locator, PDFLocator) else None,
                source_span=locator.source_span if isinstance(locator, PDFLocator) else None,
                source_locator=locator,
                acl_policy_ref=document["acl_policy_ref"],
                text_hash=document["sha256"],
            )
            record = self._ingestion.process(version_id, PUBLIC_TENANT_UUID, (chunk,))
            self._ingestion.stage_index(
                version_id,
                PUBLIC_TENANT_UUID,
                StagedIndex.from_chunks(
                    publication_id=f"local-sample-publication:{version_id}",
                    tenant_id=PUBLIC_TENANT_UUID,
                    version_id=version_id,
                    content_sha256=document["sha256"],
                    chunks=record.chunks,
                ),
            )
            self._ingestion.acknowledge_index(version_id, PUBLIC_TENANT_UUID)
            self._ingestion.approve_review2(
                version_id,
                PUBLIC_TENANT_UUID,
                reviewer,
                idempotency_key=f"local-sample-review-2:{version_id}",
            )
            active_chunk = self._ingestion.publish(version_id, PUBLIC_TENANT_UUID).chunks[0]
            self._index_records.append((active_chunk, content, classification))
            self._source_metadata[str(document_id)] = {
                "title": document["title"],
                "filename": document["filename"],
                "mime_type": document["mime_type"],
                "preview": content[:2_000],
                "download": content_bytes,
                "location": dict(locator_payload),
                "owner_department_id": (
                    str(owner_department_id) if owner_department_id else None
                ),
                "version_id": str(version_id),
            }
            runtime_documents[str(document_id)] = DocumentResource(
                document_id=str(document_id),
                tenant_id=PUBLIC_TENANT_ID,
                classification=classification.value,
                current_version_id=str(version_id),
                version_id=str(version_id),
                version_status="ACTIVE",
                owner_department_id=(str(owner_department_id) if owner_department_id else None),
                policy_epoch=1,
            )
        return runtime_documents

    def citation_state(self, artifact: object) -> object | None:
        """Return local source metadata only after citation identity matches."""

        document_id = str(getattr(artifact, "document_id", ""))
        version_id = str(getattr(artifact, "version_id", ""))
        metadata = self._source_metadata.get(document_id)
        if metadata is None or metadata.get("version_id") != version_id:
            return None
        return replace(
            artifact,
            preview=str(metadata["preview"]),
            download=bytes(metadata["download"]),
            title=str(metadata["title"]),
            filename=str(metadata["filename"]),
            mime_type=str(metadata["mime_type"]),
            location=dict(metadata["location"]),
            owner_department_id=(
                str(metadata["owner_department_id"])
                if metadata["owner_department_id"]
                else None
            ),
            classification=str(
                self._documents[document_id].classification
                if document_id in self._documents
                else getattr(artifact, "classification", "INTERNAL")
            ),
            current_version_id=version_id,
            version_status="ACTIVE",
        )

    def _display_citation(self, citation: AnswerCitation) -> AnswerCitation:
        metadata = self._source_metadata.get(citation.document_id)
        if metadata is None or metadata.get("version_id") != citation.version_id:
            return citation
        return replace(
            citation,
            title=str(metadata["title"]),
            filename=str(metadata["filename"]),
            mime_type=str(metadata["mime_type"]),
            location=dict(metadata["location"]),
        )

    def bind_context(self, principal_ref: str, principal: Principal, policy_epoch: int) -> None:
        self._contexts[principal_ref] = (principal, policy_epoch)

    def _authorize_citation(
        self,
        principal: Principal,
        policy_epoch: int,
        citation: object,
    ) -> AuthorizationDecision:
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

    def _pipeline(self, principal: Principal, policy_epoch: int) -> DirectAnswerPipeline:
        return DirectAnswerPipeline(
            retriever=self._retriever,
            model_gateway=self._answer_model,
            authorize_citation=lambda citation: self._authorize_citation(
                principal, policy_epoch, citation
            ),
        )

    @staticmethod
    def _chunks(
        text: str, *, chunk_size: int = 80, delay_seconds: float = 0.0
    ) -> Iterator[str]:
        for start in range(0, len(text), chunk_size):
            if start and delay_seconds:
                # shortcut: bounded delay is local-demo-only; production uses provider/network streaming.
                time.sleep(delay_seconds)
            yield text[start : start + chunk_size]

    def run(self, request: object) -> object:
        context = self._contexts.get(getattr(request, "principal_ref", ""))
        if context is None:
            from backend.app.orchestration import OrchestrationOutcome, OrchestrationStatus

            return OrchestrationOutcome(OrchestrationStatus.ERROR, reason_codes=("RAG_CONTEXT_UNAVAILABLE",))
        principal, policy_epoch = context

        result = self._pipeline(principal, policy_epoch).answer(
            getattr(request, "query", ""),
            principal,  # type: ignore[arg-type]
            policy_epoch=policy_epoch,
        )
        return replace(
            result,
            citations=tuple(self._display_citation(citation) for citation in result.citations),
        )

    def stream(self, request: object) -> Iterator[dict[str, object]]:
        """Yield provider-neutral events after authorized retrieval."""

        context = self._contexts.get(getattr(request, "principal_ref", ""))
        if context is None:
            yield {"event": "error", "data": {"code": "RAG_CONTEXT_UNAVAILABLE"}}
            return
        principal, policy_epoch = context
        query = getattr(request, "query", "")
        prepared = self._pipeline(principal, policy_epoch).prepare_context(
            query,
            principal,  # type: ignore[arg-type]
            policy_epoch=policy_epoch,
        )
        if prepared.status is not AnswerStatus.ANSWERED or prepared.context is None:
            yield {
                "event": "complete",
                "data": {
                    "status": prepared.status.value,
                    "answer": "Insufficient evidence to answer this question."
                    if prepared.status is AnswerStatus.INSUFFICIENT_EVIDENCE
                    else "",
                    "citations": [],
                    "reason_codes": list(prepared.reason_codes),
                },
            }
            return

        display_citations = tuple(self._display_citation(citation) for citation in prepared.citations)
        for citation in display_citations:
            yield {"event": "citation", "data": citation.to_dict()}

        pieces: list[str] = []
        if self._gemini_provider is None:
            generated = self._answer_model.generate(
                prepared.context.as_messages(), classification=DataClassification.INTERNAL
            )
            for piece in self._chunks(
                generated.answer,
                chunk_size=LOCAL_DEMO_CHUNK_SIZE,
                delay_seconds=LOCAL_DEMO_CHUNK_DELAY_SECONDS,
            ):
                pieces.append(piece)
                yield {"event": "token", "data": {"text": piece}}
        else:
            try:
                pieces.extend(self._gemini_provider.stream(prepared.context.as_messages()))
            except GeminiProviderError:
                yield {"event": "error", "data": {"code": "PROVIDER_ERROR"}}
                return

        answer = "".join(pieces)
        if self._gemini_provider is not None and not _answer_covers_evidence(
            query, tuple(item.excerpt for item in prepared.guardrail_citations), answer
        ):
            yield {
                "event": "complete",
                "data": {
                    "status": AnswerStatus.INSUFFICIENT_EVIDENCE.value,
                    "answer": "Insufficient evidence to answer this question.",
                    "citations": [],
                    "reason_codes": ["incomplete_evidence_coverage"],
                },
            }
            return
        checked = validate_output(answer, prepared.guardrail_citations)
        if not checked.allowed or checked.value is None:
            yield {
                "event": "complete",
                "data": {
                    "status": AnswerStatus.INSUFFICIENT_EVIDENCE.value,
                    "answer": "Insufficient evidence to answer this question.",
                    "citations": [],
                    "reason_codes": list(checked.reason_codes),
                },
            }
            return
        if self._gemini_provider is not None:
            for piece in self._chunks(checked.value):
                yield {"event": "token", "data": {"text": piece}}
        yield {
            "event": "complete",
            "data": {
                "status": AnswerStatus.ANSWERED.value,
                "answer": checked.value,
                "citations": [citation.to_dict() for citation in display_citations],
                "reason_codes": [],
            },
        }


__all__ = ["LocalRagExecutor"]


_TOKEN = re.compile(r"[\w]+", re.UNICODE)
_CLAIM_STOP_WORDS = frozenset(
    "a an and are as at be been before by can could do does for from had has have how i if in is it of on or our the their them these this to was what when which with would you your all must request requests after employees submit".split()
)
_CLAIM_ALIASES = {
    "finance": ("finance", "financial", "tài chính"),
    "department": ("department", "phòng ban", "bộ phận"),
    "reviewed": ("review", "reviewed", "reviewing", "xem xét"),
    "approval": ("approval", "approve", "phê duyệt"),
    "equipment": ("equipment", "thiết bị"),
    "retained": ("retained", "retention", "lưu giữ"),
    "security": ("security", "bảo mật"),
    "receipts": ("receipt", "receipts", "biên lai", "chứng từ"),
}


def _claim_terms(value: str) -> set[str]:
    return {
        token.casefold()
        for token in _TOKEN.findall(value)
        if token.casefold() not in _CLAIM_STOP_WORDS
    }


def _relevant_evidence(query: str, evidence: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    query_terms = _claim_terms(query)
    if not query_terms:
        return ()
    return tuple(item for item in evidence if query_terms & _claim_terms(item))


def _answer_has_term(answer: str, term: str) -> bool:
    normalized = answer.casefold()
    return any(alias in normalized for alias in _CLAIM_ALIASES.get(term, (term,)))


def _answer_covers_evidence(query: str, evidence: tuple[str, ...], answer: str) -> bool:
    """Require every retrieved, query-related sentence's material anchors."""

    relevant = _relevant_evidence(query, evidence)
    if not relevant or not answer.strip():
        return False
    answer_terms = _claim_terms(answer)
    for item in relevant:
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", item):
            terms = _claim_terms(sentence)
            if not terms:
                continue
            numeric = {term for term in terms if any(char.isdigit() for char in term)}
            if numeric and not all(term.replace(",", "") in answer.replace(",", "") for term in numeric):
                return False
            for term in terms - numeric:
                if term in _CLAIM_ALIASES and _answer_has_term(answer, term):
                    continue
                if term in _CLAIM_ALIASES:
                    return False
                if len(term) >= 5 and term not in answer_terms:
                    return False
    return True
