# Ingestion scoped instructions

Follow document lifecycle contract. Untrusted uploads stay in quarantine until scanning and approval. Parse with resource limits; generate source-span metadata; child chunks inherit ACL. Index into STAGING and publish active version atomically. Revoke, update and deletion must address derived index/caches. Never process a suspicious file with unrestricted execution.
