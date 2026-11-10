import hashlib
import json
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.evidence import AuthorizationDecision, Claim
from backend.app.identity.models import AuthenticatedPrincipal
from backend.app.knowledge.models import DOCXLocator, PDFLocator, SourceSpan, XLSXLocator
from backend.app.models.policy import DataClassification
from backend.app.rag import (
    AnswerCitation,
    Citation,
    DirectAnswerPipeline,
    GeneratedAnswer,
    HybridEvidence,
    HybridRetrievalResult,
)


class _StaticRetriever:
    def __init__(self, citation: Citation, text: str) -> None:
        self._result = HybridRetrievalResult(
            (HybridEvidence(citation, 1.0, text, 1.0, 1.0),), "OK"
        )

    def search(self, query, principal, *, policy_epoch, top_k=8):
        return self._result


class _AnswerModel:
    def __init__(self, text: str) -> None:
        self.text = text

    def generate(self, messages, *, classification):
        assert classification is DataClassification.INTERNAL
        return GeneratedAnswer(self.text, (Claim("claim-1", self.text, ("c-1",)),))


def _principal(tenant_id: str = "tenant-a") -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id="user-1",
        tenant_id=tenant_id,
        roles=["employee"],
        department_ids=["department-1"],
        session_id="session-1",
        auth_time="2026-11-10T00:00:00Z",
    )


def _pipeline(citation: Citation, text: str, authorize=None) -> DirectAnswerPipeline:
    def allow(record):
        return AuthorizationDecision(
            allowed=True,
            tenant_id=record.tenant_id,
            document_id=record.document_id,
            version_id=record.version_id,
            current_version_id=record.version_id,
            status="ACTIVE",
        )

    return DirectAnswerPipeline(
        retriever=_StaticRetriever(citation, text),
        model_gateway=_AnswerModel(text),
        authorize_citation=authorize or allow,
    )


@pytest.mark.parametrize(
    ("locator", "kind"),
    [
        (PDFLocator(page=4, source_span=SourceSpan(start=10, end=30)), "PDF"),
        (DOCXLocator(heading="Security policy", paragraph=7), "DOCX"),
        (XLSXLocator(sheet="Revenue", cell_range="B4:F12"), "XLSX"),
    ],
)
def test_answer_citation_emits_typed_locator_and_bindings(locator, kind):
    text = "The retention period is 30 days."
    citation = Citation("chunk-1", "doc-1", "v-2", "tenant-a", 42, locator)

    result = _pipeline(citation, text).answer("retention period", _principal(), policy_epoch=42)

    assert result.status == "ANSWERED"
    output = result.citations[0]
    assert output.tenant_id == "tenant-a"
    assert output.version_id == "v-2"
    assert output.policy_epoch == 42
    assert output.audience == "answer-client"
    assert output.expires_at > datetime.now(timezone.utc)
    assert output.chunk_id == "chunk-1"
    assert output.locator.kind == kind


def test_answer_rejects_tenant_policy_and_malformed_locator_fail_closed():
    text = "The retention period is 30 days."
    calls = 0

    def authorize(record):
        nonlocal calls
        calls += 1
        return AuthorizationDecision(allowed=True)

    tenant_mismatch = Citation(
        "chunk-1", "doc-1", "v-2", "tenant-b", 42,
        PDFLocator(page=1, source_span=SourceSpan(start=0, end=4)),
    )
    assert _pipeline(tenant_mismatch, text, authorize).answer(
        "retention", _principal(), policy_epoch=42
    ).citations == ()
    assert calls == 0

    stale = Citation(
        "chunk-1", "doc-1", "v-2", "tenant-a", 41,
        PDFLocator(page=1, source_span=SourceSpan(start=0, end=4)),
    )
    assert _pipeline(stale, text).answer("retention", _principal(), policy_epoch=42).citations == ()

    malformed = Citation("chunk-1", "doc-1", "v-2", "tenant-a", 42, {"kind": "PDF"})
    assert _pipeline(malformed, text).answer("retention", _principal(), policy_epoch=42).citations == ()


def test_revoked_citation_is_not_returned():
    text = "The retention period is 30 days."
    citation = Citation(
        "chunk-1", "doc-1", "v-2", "tenant-a", 42,
        PDFLocator(page=1, source_span=SourceSpan(start=0, end=4)),
    )

    def revoked(record):
        return AuthorizationDecision(
            allowed=True,
            tenant_id=record.tenant_id,
            document_id=record.document_id,
            version_id=record.version_id,
            current_version_id=record.version_id,
            status="ACTIVE",
            revoked=True,
        )

    result = _pipeline(citation, text, revoked).answer("retention", _principal(), policy_epoch=42)
    assert result.citations == ()


def test_answer_citation_is_immutable_hash_stable_and_serializable():
    text = "The retention period is 30 days."
    citation = Citation(
        "chunk-1", "doc-1", "v-2", "tenant-a", 42,
        PDFLocator(page=1, source_span=SourceSpan(start=0, end=4)),
    )
    output = _pipeline(citation, text).answer("retention", _principal(), policy_epoch=42).citations[0]

    assert output.evidence_snapshot_hash == hashlib.sha256(text.encode()).hexdigest()
    payload = output.to_dict()
    assert json.loads(output.to_json()) == payload
    assert payload["locator"] == {
        "kind": "PDF",
        "page": 1,
        "source_span": {"start": 0, "end": 4},
    }
    with pytest.raises(FrozenInstanceError):
        output.tenant_id = "tenant-b"
    with pytest.raises(Exception):
        output.locator.page = 2


def test_answer_citation_rejects_naive_expiry():
    with pytest.raises(ValueError):
        Citation(
            "chunk-1", "doc-1", "v-2", "tenant-a", 42,
            PDFLocator(page=1, source_span=SourceSpan(start=0, end=4)),
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5),
        )


def test_malformed_locator_model_is_rejected():
    with pytest.raises(ValueError):
        XLSXLocator(sheet="Revenue", cell_range="not-a-range")
