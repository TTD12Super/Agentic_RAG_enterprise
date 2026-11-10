from uuid import UUID

from backend.app.authorization.policy import AccessGrant, Action, DocumentResource
from backend.app.evidence import (
    AuthorizationDecision,
    Claim,
    CitationRecord,
    EvidenceRecord,
    EvidenceVerifier,
    SourceSpan,
    VerificationRequest,
    VerificationOutcome,
)
from backend.app.ingestion import IngestionService
from backend.app.rag.dense import DenseRetriever
from backend.tests.test_dense_retrieval import (
    _active_document,
    _principal,
    _resource,
    _retriever,
)


def evidence_for(result, tenant_id, text=None):
    item = result.evidence[0]
    span = item.citation.source_span
    return EvidenceRecord(
        CitationRecord(
            citation_id="c-1",
            document_id=item.citation.document_id,
            version_id=item.citation.version_id,
            tenant_id=str(tenant_id),
            source_span=SourceSpan(span.start, span.end),
            page=item.citation.page_start,
            chunk_id=item.citation.chunk_id,
        ),
        text or item.text,
    )


def verify_retrieved(retriever, result, principal, tenant_id, *, policy_epoch=7):
    evidence = evidence_for(result, tenant_id)
    citation = evidence.citation

    def authorize(record):
        if retriever.is_authorized(
            record.chunk_id or "", principal, policy_epoch=policy_epoch
        ):
            return AuthorizationDecision(
                allowed=True,
                tenant_id=record.tenant_id,
                document_id=record.document_id,
                version_id=record.version_id,
                current_version_id=record.version_id,
                status="ACTIVE",
            )
        return AuthorizationDecision(allowed=False)

    return EvidenceVerifier(authorize).verify(
        VerificationRequest(str(tenant_id), (Claim("claim-1", evidence.text),), (evidence,))
    )


def test_active_retrieval_to_evidence_verification_succeeds():
    tenant_id = UUID("00000000-0000-0000-0000-000000000101")
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
        text="active warranty evidence",
    )

    result = retriever.search("active warranty", principal, policy_epoch=7)

    assert result.status == "OK"
    assert verify_retrieved(retriever, result, principal, tenant_id).outcome is VerificationOutcome.SUPPORTED


def test_retrieval_citation_keeps_document_version_page_and_span():
    tenant_id = UUID("00000000-0000-0000-0000-000000000102")
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
        text="provenance-bound evidence",
    )

    item = retriever.search("provenance", principal, policy_epoch=7).evidence[0]

    assert item.citation.document_id == str(document_id)
    assert item.citation.version_id == str(version_id)
    assert item.citation.page_start == chunk.page_start
    assert item.citation.source_span == chunk.source_span


def test_revocation_denies_existing_citation_and_removes_retrieval():
    tenant_id = UUID("00000000-0000-0000-0000-000000000103")
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
        text="revocable source evidence",
    )
    before = retriever.search("revocable", principal, policy_epoch=7)
    ingestion.revoke_version(version_id, tenant_id)

    assert retriever.search("revocable", principal, policy_epoch=7).evidence == ()
    assert verify_retrieved(retriever, before, principal, tenant_id).outcome is VerificationOutcome.ACCESS_DENIED
    assert retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7).redacted


def test_superseded_current_version_is_not_operationally_visible():
    tenant_id = UUID("00000000-0000-0000-0000-000000000104")
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
        text="superseded source evidence",
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

    assert retriever.search("superseded", principal, policy_epoch=7).evidence == ()


def test_staging_index_state_cannot_become_evidence():
    tenant_id = UUID("00000000-0000-0000-0000-000000000105")
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
        text="staged source evidence",
    )

    result = retriever.search("staged", principal, policy_epoch=7)

    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert result.evidence == ()


def test_cross_tenant_retrieval_is_empty_and_cannot_be_verified():
    tenant_a = UUID("00000000-0000-0000-0000-000000000106")
    tenant_b = UUID("00000000-0000-0000-0000-000000000107")
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
        text="other tenant evidence",
    )

    result = retriever.search("other tenant", principal, policy_epoch=7)

    assert result.evidence == ()
    assert retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7).redacted


def test_source_download_is_rechecked_after_read_retrieval():
    tenant_id = UUID("00000000-0000-0000-0000-000000000108")
    ingestion = IngestionService()
    document_id, version_id, department_id, chunk = _active_document(
        ingestion, tenant_id=tenant_id
    )
    principal = _principal(tenant_id, department_id)
    deny_download = AccessGrant(Action.SOURCE_DOWNLOAD.value, "DENY", user_id=principal.user_id)
    retriever = _retriever(
        ingestion,
        principal=principal,
        document_id=document_id,
        version_id=version_id,
        department_id=department_id,
        chunk=chunk,
        text="readable but not downloadable evidence",
        acl=(deny_download,),
    )

    result = retriever.search("downloadable", principal, policy_epoch=7)
    source = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)

    assert result.status == "OK"
    assert source.redacted is True
    assert source.content is None
    assert source.citation is None


def test_repeated_operational_verification_is_deterministic():
    tenant_id = UUID("00000000-0000-0000-0000-000000000109")
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
        text="deterministic operational evidence",
    )

    first = retriever.search("deterministic", principal, policy_epoch=7)
    second = retriever.search("deterministic", principal, policy_epoch=7)

    assert first == second
    assert verify_retrieved(retriever, first, principal, tenant_id) == verify_retrieved(
        retriever, second, principal, tenant_id
    )


def test_policy_store_failure_denies_search_and_source_fetch():
    tenant_id = UUID("00000000-0000-0000-0000-000000000110")
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
        text="policy failure evidence",
    )
    retriever._pep.evaluator.policy_store.available = False

    result = retriever.search("policy failure", principal, policy_epoch=7)
    source = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)

    assert result.evidence == ()
    assert source.redacted is True
    assert source.content is None


def test_soft_deleted_document_removes_citation_delivery():
    tenant_id = UUID("00000000-0000-0000-0000-000000000111")
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
        text="soft deleted citation source",
    )
    ingestion.soft_delete_document(document_id, tenant_id)

    result = retriever.search("soft deleted", principal, policy_epoch=7)
    source = retriever.fetch_source(chunk.chunk_id, principal, policy_epoch=7)

    assert result.evidence == ()
    assert source.redacted is True
    assert source.content is None
