import unittest

from ._baseline import ALERTMANAGER, COMPOSE, OTEL, RUNBOOK, read


class MonitoringSecurityTests(unittest.TestCase):
    def test_collector_deletes_user_id(self):
        self.assertIn("user.id", read(OTEL))

    def test_collector_deletes_document_id(self):
        self.assertIn("document.id", read(OTEL))

    def test_collector_deletes_query(self):
        self.assertIn("key: query", read(OTEL))

    def test_collector_deletes_prompt(self):
        self.assertIn("key: prompt", read(OTEL))

    def test_collector_deletes_answer(self):
        self.assertIn("key: answer", read(OTEL))

    def test_collector_deletes_conversation_body(self):
        self.assertIn("conversation.body", read(OTEL))

    def test_compose_binds_services_to_loopback(self):
        text = read(COMPOSE)
        self.assertEqual(text.count('"127.0.0.1:'), 6)

    def test_compose_uses_non_privileged_containers(self):
        self.assertEqual(read(COMPOSE).count("no-new-privileges:true"), 4)

    def test_alertmanager_has_no_external_webhook(self):
        self.assertNotIn("webhook_configs", read(ALERTMANAGER))

    def test_runbook_forbids_production_claims(self):
        self.assertIn("Production retention", read(RUNBOOK))


if __name__ == "__main__":
    unittest.main()
