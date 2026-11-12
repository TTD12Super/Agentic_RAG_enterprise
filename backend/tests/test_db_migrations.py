"""Minimal DB-001 verification; the separate DB-QA-001 owns the 4x10 suite."""

import os
import unittest


@unittest.skipUnless(
    os.getenv("DB001_DATABASE_URL"),
    "set DB001_DATABASE_URL to run against the disposable PostgreSQL service",
)
class DatabaseMigrationSmokeTests(unittest.TestCase):
    def test_head_and_authoritative_tables_are_present(self) -> None:
        try:
            import psycopg
        except ImportError:
            self.skipTest("install the backend[db] extra for DB tests")

        conninfo = os.environ["DB001_DATABASE_URL"].replace(
            "postgresql+psycopg://", "postgresql://", 1
        )
        expected = {
            "tenants",
            "users",
            "tenant_memberships",
            "documents",
            "document_versions",
            "document_heads",
            "query_jobs",
            "ingestion_jobs",
            "answer_citations",
            "audit_events",
            "outbox_events",
            "idempotency_keys",
            "access_requests",
        }
        with psycopg.connect(conninfo) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version_num FROM alembic_version")
                self.assertEqual(cursor.fetchone()[0], "0007_identity_credentials")
                cursor.execute(
                    "SELECT tablename FROM pg_catalog.pg_tables "
                    "WHERE schemaname = 'public'"
                )
                self.assertTrue(expected <= {row[0] for row in cursor.fetchall()})


if __name__ == "__main__":
    unittest.main()
