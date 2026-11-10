import unittest
from uuid import uuid4

from pydantic import ValidationError

from backend.app.knowledge.models import ChunkMetadata, inherit_acl, to_qdrant_payload

from _baseline import make_child, make_parent


class KnowledgeSecurityAdversarialTests(unittest.TestCase):
    def test_cross_tenant_parent_is_denied(self):
        parent = make_parent()
        with self.assertRaises(ValueError):
            inherit_acl(parent, make_child(parent, tenant_id=uuid4()))

    def test_cross_document_parent_is_denied(self):
        parent = make_parent()
        with self.assertRaises(ValueError):
            inherit_acl(parent, make_child(parent, document_id=uuid4()))

    def test_cross_version_parent_is_denied(self):
        parent = make_parent()
        with self.assertRaises(ValueError):
            inherit_acl(parent, make_child(parent, version_id=uuid4()))

    def test_unrelated_parent_reference_is_denied(self):
        parent = make_parent()
        with self.assertRaises(ValueError):
            inherit_acl(parent, make_child(parent, parent_chunk_id=uuid4()))

    def test_child_acl_broadening_is_denied(self):
        parent = make_parent(acl_policy_ref="narrow")
        with self.assertRaises(ValueError):
            inherit_acl(parent, make_child(parent, acl_policy_ref="broader"))

    def test_missing_child_acl_is_not_a_bypass(self):
        parent = make_parent(acl_policy_ref="policy-1")
        self.assertEqual(inherit_acl(parent, make_child(parent)).acl_policy_ref, "policy-1")

    def test_active_chunk_without_acl_is_denied(self):
        with self.assertRaises(ValidationError):
            ChunkMetadata(
                chunk_id=uuid4(), tenant_id=uuid4(), document_id=uuid4(), version_id=uuid4(),
                chunk_index=0, text_hash="a" * 64, index_state="ACTIVE",
            )

    def test_qdrant_projection_without_acl_is_denied(self):
        parent = make_parent(acl_policy_ref=None)
        with self.assertRaises(ValueError):
            to_qdrant_payload(parent)

    def test_qdrant_projection_preserves_tenant_boundary(self):
        parent = make_parent()
        self.assertEqual(to_qdrant_payload(parent)["tenant_id"], str(parent.tenant_id))

    def test_qdrant_projection_excludes_authorization_decisions(self):
        payload = to_qdrant_payload(make_parent())
        self.assertNotIn("policy_decision", payload)
        self.assertNotIn("authorized_scope", payload)


if __name__ == "__main__":
    unittest.main()
