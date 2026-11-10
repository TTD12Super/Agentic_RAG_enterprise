"""Static security/adversarial invariants for the v1 authorization boundary."""

import unittest

from _baseline import require_all, section


class SecurityAdversarialTests(unittest.TestCase):
    def test_security_untrusted_clients_cannot_supply_principal_attributes(self):
        require_all(self, section(2), "Browser, LLM and retrieved text cannot supply roles, tenant, departments or scopes", "only from validated authentication")

    def test_security_explicit_deny_overrides_chairman_allow(self):
        policy = section(2)
        require_all(self, policy, "explicit deny; any matching deny overrides every allow", "`chairman` is a broad read allow only", "does not bypass explicit deny")

    def test_security_scope_mismatch_denies_without_existence_leak(self):
        require_all(self, section(2), "Missing, expired, revoked or mismatched scope returns `DENY`", "without revealing resource existence")

    def test_security_worker_jwt_replay_and_cross_tenant_checks_fail_closed(self):
        worker = section(2)
        require_all(self, worker, "one-time `jti` replay state", "job/tenant binding", "Stale, revoked, cross-tenant or replayed commands/results are rejected", "never treated as successful")

    def test_security_scope_is_rechecked_at_each_content_boundary(self):
        require_all(self, section(2), "at admission", "each retrieval branch", "parent expansion", "citation", "source download")

    def test_security_parent_denial_cannot_change_child_authorization(self):
        retrieval = section(4)
        require_all(self, retrieval, "denied parent is omitted", "never used for ranking, context or citation", "independently authorized child may remain as evidence")

    def test_security_stale_cache_is_fail_closed(self):
        cache = section(5)
        require_all(self, cache, "If an epoch is stale, missing or invalidation confirmation is unavailable", "cache miss/fail-closed path", "never proves permission")

    def test_security_privacy_events_exclude_conversation_and_source_content(self):
        events = section(8)
        require_all(self, events, "must not contain conversation bodies", "raw prompts/answers", "source text", "secrets", "tokens", "unrestricted PII")
        self.assertIn("cannot select another user's body", events)

    def test_security_agent_tool_surface_excludes_side_effect_tools(self):
        tools = section(8)
        require_all(self, tools, "Upload, edit, delete, permission-change, SQL, shell, HTTP-fetch and email tools are absent")

    def test_security_output_and_provider_fallback_cannot_bypass_policy(self):
        require_all(self, section(8), "reject unsupported claims", "unauthorized citations", "raw source leakage", "tool-derived instructions")
        require_all(self, section(6), "approved fallback only")


if __name__ == "__main__":
    unittest.main()
