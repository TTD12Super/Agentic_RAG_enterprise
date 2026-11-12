# Local RAG sample corpus

This directory contains a small, synthetic enterprise-policy corpus for local
retrieval and citation tests. The documents are deliberately written for this
repository; they are not copied from a company, customer, public website, or
production corpus.

`manifest.json` is the source of truth for the deterministic test metadata:

- stable tenant, document, version, and chunk identifiers;
- MIME/format and typed citation locator (`PDF`, `DOCX`, or `XLSX`);
- classification and owning department;
- SHA-256 binding between each metadata record and its checked-in text file;
- example answerable queries and an explicit no-answer case.

The `.md` files are content stand-ins. Their manifest MIME types model the
formats supported by the product without requiring binary fixtures or parser
dependencies. All source URIs used by tests remain private object-storage
references; no raw local path is exposed as citation metadata.

The QA harness and `LocalRagExecutor` publish each record through the existing
local ingestion lifecycle and index it in the deterministic dense/BM25 doubles.
The runtime maps this synthetic corpus to the local `public` demo tenant while
preserving PUBLIC/INTERNAL classification and department ACL checks. Tests
cover retrieval, authorization, typed citation metadata, and safe no-answer
behavior. The deterministic fallback does not require an API key; when the
backend Gemini secret is configured, the same authorized context is streamed
through Gemini server-side.
