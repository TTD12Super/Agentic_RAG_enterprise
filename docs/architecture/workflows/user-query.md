# Flow B: Authorized user → answer with citations

This workflow uses the React client, the Python/FastAPI Core MVP, a PostgreSQL-backed priority queue and Python RAG workers. It is a proposal until the job, policy and model contracts are approved.

1. React sends a question; the Core authenticates the employee/Chairman or creates a temporary anonymous session.
2. The Core validates request shape, abuse limits, current maintenance state and server-side identity.
3. If maintenance is active, new work is not processed; the UI receives an explicit MAINTENANCE state. Existing approved jobs remain resumable.
4. Otherwise, the Core creates an auditable question job, binds a trusted policy reference and places it in the approved priority queue.
5. The UI may show QUEUED, an estimated/current queue position and PROCESSING; positions can change under Chairman priority and are not completion guarantees.
6. A Python worker revalidates identity, policy version, ACTIVE source versions and permission-aware exact-question/retrieval caches before doing work.
7. A simple question uses the direct Advanced Hybrid RAG path. An eligible complex question or insufficient first retrieval may invoke bounded single-agent LangGraph with read-only tools.
8. Dense and lexical retrieval apply identical tenant, ACTIVE-version and ACL filters before RRF, reranking and deduplication.
9. Parent expansion, source fetch and citation creation perform a second authorization check. Retrieved text and tool output remain untrusted data.
10. The Python model gateway sends only authorized relevant excerpts to approved external LLM APIs, with bounded retry and approved fallback.
11. Evidence verification maps factual claims to authorized source spans. Conflicts are disclosed; insufficient evidence produces abstention or a permitted partial answer.
12. The Core rechecks policy before delivering the full answer and before any source is opened. MVP does not stream tokens.
13. The system writes only permitted conversation history, usage telemetry, citations and privacy-safe audit events.
14. An irrecoverable ordinary failure returns a clear retryable error. Maintenance interruption is a separate path that resumes or safely replays an idempotent read-only step.

## Roles

- Anonymous user: published PUBLIC evidence only; temporary session history.
- Internal employee: published INTERNAL evidence allowed by department and document policy.
- Chairman: broad published-document read access without upload, approval, deletion or developer rights.
- Website Manager/System Admin: administrative operations according to the approved policy; MFA required.

## Acceptance examples

- A client-supplied role, document ID or allowed scope cannot broaden retrieval.
- A cross-tenant, denied, inactive or revoked document produces no chunk, snippet, facet or citation leak.
- Dense and lexical branches return the same authorization boundary.
- A citation opened after revocation is denied.
- No private model reasoning is exposed in progress or error states.

## Owner-provided execution parameters

- MVP uses a PostgreSQL-backed durable queue with priority `Chairman > Website Manager/System Admin > authenticated employee > anonymous`.
- Initial limits are 20 concurrent RAG tasks, 2 ingestion tasks and 200 waiting query jobs, subject to load testing.
- During maintenance, new queries receive `503 MAINTENANCE_ACTIVE`; existing jobs pause at durable PostgreSQL checkpoints.
- An external LLM call may run for up to 60 seconds before safe checkpoint/cancellation handling. Resume always rechecks tenant, ACL, policy and document version.
- Simple/complex budgets are 16k/2k and 32k/4k input/output tokens, with at most two retrieval rounds, four subqueries and eight tool calls.

