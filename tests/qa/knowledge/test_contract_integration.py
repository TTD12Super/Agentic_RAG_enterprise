import unittest
from uuid import uuid4

from backend.app.knowledge.models import inherit_acl, to_qdrant_payload

from _baseline import MIGRATION, make_child, make_document, make_parent, make_version, read


class KnowledgeContractIntegrationTests(unittest.TestCase):
    def test_document_contract_requires_tenant_and_document_identity(self):
        document = make_document(current_version_id=uuid4())
        self.assertIsNotNone(document.tenant_id)
        self.assertIsNotNone(document.document_id)

    def test_version_contract_has_private_source_and_checksum(self):
        value = make_version()
        self.assertTrue(value.source_uri.startswith("private://"))
        self.assertEqual(len(value.sha256), 64)

    def test_version_contract_can_represent_active_publication(self):
        try:
            value = make_version(status="ACTIVE")
        except Exception as exc:  # Report the contract mismatch as a test failure.
            self.fail(f"DocumentVersionMetadata cannot represent contract status ACTIVE: {exc}")
        self.assertEqual(value.status, "ACTIVE")

    def test_version_contract_can_represent_revoked_publication(self):
        try:
            value = make_version(status="REVOKED")
        except Exception as exc:
            self.fail(f"DocumentVersionMetadata cannot represent contract status REVOKED: {exc}")
        self.assertEqual(value.status, "REVOKED")

    def test_parent_and_child_keep_tenant_document_and_version_scope(self):
        parent = make_parent()
        child = inherit_acl(parent, make_child(parent))
        self.assertEqual((child.tenant_id, child.document_id, child.version_id), (parent.tenant_id, parent.document_id, parent.version_id))

    def test_acl_reference_is_inherited(self):
        parent = make_parent(acl_policy_ref="policy-contract")
        self.assertEqual(inherit_acl(parent, make_child(parent)).acl_policy_ref, "policy-contract")

    def test_qdrant_projection_contains_tenant_version_and_chunk_keys(self):
        payload = to_qdrant_payload(make_parent())
        self.assertTrue({"tenant_id", "document_id", "version_id", "chunk_id"} <= payload.keys())

    def test_qdrant_projection_does_not_contain_source_text(self):
        payload = to_qdrant_payload(make_parent())
        self.assertNotIn("content_text", payload)

    def test_qdrant_projection_preserves_source_span(self):
        parent = make_parent()
        child = make_child(parent, source_span={"start": 10, "end": 20})
        payload = to_qdrant_payload(inherit_acl(parent, child))
        self.assertEqual(payload["source_span"], {"start": 10, "end": 20})

    def test_db_boundary_keeps_parent_scope_and_active_projection_guards(self):
        migration = read(MIGRATION)
        self.assertIn("FOREIGN KEY (tenant_id, version_id, parent_chunk_id)", migration)
        self.assertIn("index_status <> 'ACTIVE' OR (vector_point_id IS NOT NULL AND index_version IS NOT NULL)", migration)


if __name__ == "__main__":
    unittest.main()
