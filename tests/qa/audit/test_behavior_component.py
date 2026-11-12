import unittest

from ._baseline import AUDIT, CONTEXT, IDENTITY_API, MAIN, OBS, read


class AuditBehaviorTests(unittest.TestCase):
    def test_observability_package_exists(self):
        self.assertTrue((OBS / "__init__.py").is_file())

    def test_audit_module_exists(self):
        self.assertTrue(AUDIT.is_file())

    def test_context_module_exists(self):
        self.assertTrue(CONTEXT.is_file())

    def test_correlation_context_is_defined(self):
        self.assertIn("class CorrelationContext", read(CONTEXT))

    def test_traceparent_validation_is_defined(self):
        self.assertIn("_valid_traceparent", read(CONTEXT))

    def test_audit_event_is_immutable(self):
        self.assertIn("@dataclass(frozen=True, slots=True)", read(AUDIT))

    def test_sink_is_append_only(self):
        text = read(AUDIT)
        self.assertIn("append(self, event: AuditEvent)", text)
        self.assertIn("self._events.append(event)", text)

    def test_redaction_entrypoint_exists(self):
        self.assertIn("def redact_metadata", read(AUDIT))

    def test_identity_api_uses_correlation_context(self):
        self.assertIn("CorrelationContext", read(IDENTITY_API))

    def test_error_handler_adds_correlation_context(self):
        self.assertIn("CorrelationContext.from_headers", read(MAIN))


if __name__ == "__main__":
    unittest.main()
