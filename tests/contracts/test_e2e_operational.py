"""Static operational workflow invariants; runtime flows are deliberately not mocked."""

import unittest

from ._baseline import require_all, section


class E2EOperationalTests(unittest.TestCase):
    def test_e2e_anonymous_flow_has_public_only_boundary(self):
        require_all(self, section(2), "Anonymous access is PUBLIC-only", "Require the current ACTIVE document version")

    def test_e2e_employee_flow_requires_department_acl_and_active_version(self):
        policy = section(2)
        require_all(self, policy, "Apply RBAC and department membership", "Apply document-level ACL", "current ACTIVE document version")

    def test_e2e_upload_publication_retains_previous_active_version_until_verified(self):
        lifecycle = section(7)
        require_all(self, lifecycle, "retaining the former ACTIVE version", "Until both steps verify, retrieval continues to use the former ACTIVE version")

    def test_e2e_failed_publication_emits_repair_without_replacing_active(self):
        lifecycle = section(7)
        require_all(self, lifecycle, "Any mismatch, timeout or stale writer", "leaves the former ACTIVE version served", "emits a tombstone/repair event")

    def test_e2e_invalid_ingestion_is_terminal_without_retry(self):
        require_all(self, section(7), "invalid format/malware/limit is terminal without retry", "review decisions are never auto-retried")

    def test_e2e_transient_ingestion_retry_is_bounded_and_checksum_bound(self):
        lifecycle = section(7)
        require_all(self, lifecycle, "transient storage/", "may retry up to three attempts", "unchanged checksum", "Every ingestion attempt is bound to", "content_sha256")

    def test_e2e_lease_expiry_allows_at_most_one_retryable_attempt(self):
        jobs = section(6)
        require_all(self, jobs, "Lease expiry creates at most one retryable attempt", "compare-and-swap state transition", "monotonic fencing token")

    def test_e2e_maintenance_pause_resume_rechecks_fresh_security_context(self):
        jobs = section(6)
        require_all(self, jobs, "503 MAINTENANCE_ACTIVE", "existing jobs checkpoint at safe boundaries", "fresh principal, tenant, ACL, policy epoch and document-version checks")

    def test_e2e_restore_replays_tombstones_before_any_read(self):
        lifecycle = section(7)
        require_all(self, lifecycle, "Revocation uses a deduplicated tombstone", "replay applies tombstones in sequence before any read")

    def test_e2e_deadline_timeout_and_model_fallback_remain_safe(self):
        require_all(self, section(8), "workflow_deadline_at", "A node cannot extend the workflow deadline", "safe partial/insufficient-evidence result or `TIMEOUT`")
        require_all(self, section(6), "provider retries use bounded exponential backoff and approved fallback only")


if __name__ == "__main__":
    unittest.main()
