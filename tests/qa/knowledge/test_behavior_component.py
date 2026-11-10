import unittest
from uuid import uuid4

from pydantic import ValidationError

from backend.app.knowledge.models import (
    ChunkMetadata,
    DocumentVersionMetadata,
    SourceSpan,
)

from _baseline import make_document, make_version


class KnowledgeBehaviorTests(unittest.TestCase):
    def test_public_document_without_department_is_valid(self):
        self.assertEqual(
            make_document(classification="PUBLIC", current_version_id=uuid4()).classification,
            "PUBLIC",
        )

    def test_internal_document_requires_department(self):
        with self.assertRaises(ValueError):
            make_document(classification="INTERNAL")

    def test_active_document_requires_current_version(self):
        with self.assertRaises(ValueError):
            make_document(status="ACTIVE")

    def test_soft_deleted_document_can_have_no_current_version(self):
        self.assertIsNone(make_document(status="SOFT_DELETED").current_version_id)

    def test_document_model_is_immutable(self):
        value = make_document(current_version_id=uuid4())
        with self.assertRaises(ValidationError):
            value.status = "SOFT_DELETED"

    def test_version_identity_contains_tenant_document_version_and_number(self):
        value = make_version()
        self.assertEqual(value.identity, (value.tenant_id, value.document_id, value.version_id, 1))

    def test_version_number_must_be_positive(self):
        with self.assertRaises(ValidationError):
            DocumentVersionMetadata(
                tenant_id=uuid4(), document_id=uuid4(), version_id=uuid4(), version_number=0,
                source_uri="private://documents/v0", sha256="a" * 64, status="UPLOADED",
            )

    def test_source_uri_must_be_private(self):
        with self.assertRaises(ValueError):
            DocumentVersionMetadata(
                tenant_id=uuid4(), document_id=uuid4(), version_id=uuid4(), version_number=1,
                source_uri="https://public.example/doc", sha256="a" * 64, status="UPLOADED",
            )

    def test_sha256_is_normalized_to_lowercase(self):
        value = DocumentVersionMetadata(
            tenant_id=uuid4(), document_id=uuid4(), version_id=uuid4(), version_number=1,
            source_uri="private://documents/v1", sha256="B" * 64, status="UPLOADED",
        )
        self.assertEqual(value.sha256, "b" * 64)

    def test_source_span_is_half_open_and_forward(self):
        self.assertEqual(SourceSpan(start=3, end=9).end, 9)
        with self.assertRaises(ValidationError):
            SourceSpan(start=9, end=3)


if __name__ == "__main__":
    unittest.main()
