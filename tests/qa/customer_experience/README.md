# Customer-experience QA/E2E suite

This suite is intentionally separate from `backend/` and `frontend/`. It is a
customer audit harness: it records the expected user-visible contract and
should fail when a reported UX regression is still present.

## Run

```bash
backend/.venv/bin/python -m pytest tests/qa/customer_experience -q
```

No Gemini key, database, browser, network, or external document is required.
The API checks use the FastAPI ASGI app and the deterministic local RAG
executor. The UI checks read the checked-in React/CSS sources only.

## Reproduction map

| Test area | User reproduction | Expected contract |
| --- | --- | --- |
| Citation preview | Ask the public equipment-policy question, open a citation, press **Preview** | A non-empty authorized source excerpt is returned |
| Reload conversation | Send a message, reload the page | The active conversation ID is restored and history is requested |
| Backend outage/retry | Submit while the backend is unavailable or returns a retryable 5xx | The problem envelope is retryable and the UI offers recovery |
| Long answer | Ask for all approval conditions in the equipment policy | Both department review and Finance approval are present |
| Stream order | Inspect the streamed response event sequence | `message_start`, citations, tokens, then exactly one terminal `done` |
| ACL | Ask for an internal policy anonymously and with the owning department | Anonymous is denied; the owning department can retrieve it |
| Responsive/accessibility | Inspect layout breakpoints and interactive labels | Mobile breakpoints, keyboard focus, labels and status semantics exist |

Failures are evidence for the Main Agent; this directory does not patch the
production implementation.
