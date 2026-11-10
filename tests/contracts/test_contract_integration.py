"""Static/schema checks for cross-boundary compatibility in v1."""

import unittest

from _baseline import BASELINE, json_blocks, require_all, section


class ContractIntegrationTests(unittest.TestCase):
    def test_contract_api_root_is_versioned_rest_json(self):
        require_all(self, section(1), "REST/HTTP JSON under `/api/v1`", "Public APIs use REST/HTTP JSON")

    def test_contract_worker_payload_identifies_schema_and_attempt(self):
        envelope = json_blocks(section(1))[0]
        for field in ("schema_version", "message_id", "request_id", "attempt_id", "payload"):
            self.assertIn(field, envelope)
        self.assertIn("JSON Schema/Pydantic payloads", section(1))

    def test_contract_traceparent_and_request_id_have_distinct_roles(self):
        require_all(self, section(1), "`traceparent` is propagated unchanged as the parent context", "`request_id` is the application correlation identifier", "not a substitute for `traceparent`")

    def test_contract_mutation_idempotency_scope_is_defined(self):
        idem = section(3)
        require_all(self, idem, "Mutating POST commands require", "canonical request fingerprint", "final safe response for 24 hours", "IDEMPOTENCY_KEY_REUSED")
        self.assertIn("tenant_id + resource/job_id + operation + idempotency_key", idem)

    def test_contract_read_and_delete_have_resource_semantics(self):
        self.assertIn("GET and DELETE rely on their resource semantics", section(3))

    def test_contract_authorized_scope_schema_is_server_bound(self):
        policy = section(2)
        scope = json_blocks(policy)[0]
        for field in ("scope_ref", "audience", "principal_id", "tenant_id", "policy_epoch", "issued_at", "expires_at", "revoked_at"):
            self.assertIn(field, scope)
        require_all(self, policy, "server-issued opaque reference", "never accepted from the browser or LLM")

    def test_contract_citation_reference_contains_reauthorization_claims(self):
        retrieval = section(4)
        require_all(self, retrieval, "tenant_id", "immutable `document_version_id`", "evidence snapshot hash", "`policy_epoch`", "audience and expiry", "separate `source:download` check")

    def test_contract_cache_key_carries_all_authorization_epochs(self):
        cache = section(5)
        for field in ("tenant", "principal entitlement fingerprint", "`policy_epoch`", "`corpus_epoch`", "`index_generation`", "query hash", "model configuration", "prompt version"):
            self.assertIn(field, cache)

    def test_contract_publication_requires_index_ack_before_pointer_flip(self):
        lifecycle = section(7)
        first = lifecycle.index("(1) PostgreSQL records")
        second = lifecycle.index("(2) index projections are built")
        self.assertLess(first, second)
        require_all(self, lifecycle, "atomically flips the current pointer", "former ACTIVE version", "publication/fencing token")

    def test_contract_versioned_mutation_endpoints_are_explicit(self):
        api = section(9)
        require_all(self, api, "POST /api/v1/access-requests", "/documents/{document_id}/versions/{version_id}/approve", "/publish", "/answers/{answer_id}/feedback")
        self.assertIn("document-level aliases cannot select a newer version implicitly", api)


if __name__ == "__main__":
    unittest.main()
