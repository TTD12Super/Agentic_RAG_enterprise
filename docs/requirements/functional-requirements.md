# Functional Requirements — Enterprise Agentic RAG

**Document ID:** FRD-001  
**Version:** 1.0 — Owner Review Draft  
**Approval status:** PENDING PROJECT OWNER APPROVAL  
**Primary source:** `GOALS.md` (version supplied by Project Owner, 2026-11-09) and the Project Owner's answers to functional-discovery questions 1–51.  
**Scope:** Initial MVP, unless explicitly marked `DEFERRED`.

## 1. Purpose and governance

This document specifies **what the product must do**, its user-visible behavior, and testable acceptance expectations. It does **not** choose implementation architecture, database tables, APIs, message brokers, LLM providers, frameworks, or Figma layout.

- The **Project Owner** approves requirements, architecture, contracts, and design. Development agents may suggest changes but may not decide or silently implement new features.
- `GOALS.md` defines objectives and exclusions. Approved architecture/ADRs and contracts define the *how* after functional requirements are accepted.
- Requirements have stable IDs. Dependent implementation tasks must reference their IDs. Task status is maintained in `harness/tasks/tasks.json`.
- `PENDING` decisions remain unresolved. They must not be filled in by an implementation agent.
- Detailed security, performance, retention, and numeric evaluation thresholds belong in the respective security, non-functional, and evaluation specifications.

## 2. Actors and business permissions

| Actor | Functional scope | Boundaries |
|---|---|---|
| **Anonymous / External User** | Uses public chatbot without an account. | Access only to published `PUBLIC` knowledge. |
| **Internal User / Employee** | Uses authenticated chatbot and history; accesses authorized internal documents. | Access governed by department and document-specific permissions. |
| **Chairman** | Has Internal User capabilities and can read published documents across all departments. | Does **not** obtain administrative or developer powers merely from this role. |
| **Website Manager** | Manages user accounts and documents, including approval, versioning, permissions and business administration. | Can view business-administration audit logs; no developer-only powers. |
| **System Admin** | Has the same business-administration rights as Website Manager, plus developer/system-management capabilities. | Developer-only capabilities must be defined and approved separately. |

**FR-ROLE-001 — Anonymous access.** Unauthenticated visitors may use the public chatbot; the system must not expose internal documents or information derived from them.

**FR-ROLE-002 — Internal access.** Authenticated employees may query `PUBLIC` information and `INTERNAL` information permitted for their identity, department and document-level authorization rules.

**FR-ROLE-003 — Chairman read access.** The Chairman role may retrieve and read all published company documents regardless of department, subject to trusted backend role verification. This role is not a document-editing or administration grant.

**FR-ROLE-004 — Business administration.** Website Manager and System Admin have equivalent business-management privileges for user accounts and document lifecycle operations, including approval and deletion. Both have access to company document content as confirmed by the Project Owner.

**FR-ROLE-005 — Developer distinction.** Only System Admin has additional developer/system privileges; Website Manager has no code or system-management privileges.

**FR-ROLE-006 — Single-company MVP.** The MVP serves one enterprise. The product should remain reusable for a different enterprise's approved document collection without major redesign; a live multi-company control plane is **not** part of this MVP. Requirements for future tenant isolation remain an architectural/security consideration and are not silently implemented as multi-tenant product features.

## 3. Identity and access control

| ID | MVP functional requirement | Acceptance expectation |
|---|---|---|
| **FR-AUTH-001** | Public chatbot is usable without sign-in. | An anonymous visitor can ask about `PUBLIC` knowledge. |
| **FR-AUTH-002** | Company employee accounts are created/provisioned by an authorized administrator; public self-registration is not enabled for internal accounts. | An unapproved visitor cannot self-create an active employee account. |
| **FR-AUTH-003** | Employees activate their admin-provisioned accounts through email and authenticate with email and password. | A not-yet-activated account cannot use employee-only features; valid activation permits sign-in. |
| **FR-AUTH-004** | Website Manager and System Admin may perform approved user-management actions. | Unauthorized users cannot create/activate/manage employee identities. |
| **FR-AUTH-005** | Internal document access considers authenticated identity, department and per-document grants/restrictions. | A user cannot obtain a non-permitted document by changing document IDs, filters, prompts or API inputs. |
| **FR-AUTH-006** | `PUBLIC` versus `INTERNAL` classification is enforced consistently in search, answers, source access and caches. | An anonymous visitor receives no internal content in any of these paths. |
| **FR-AUTH-007** | Authorization is validated by trusted backend services, never delegated to the LLM or frontend. | Prompt/client manipulation cannot grant additional rights. |
| **FR-AUTH-008** | Permission or account revocation affects subsequent protected operations. | A previously allowed but now revoked user/document cannot be accessed using stale retrievals or cached answers. |

**MVP authentication decision:** Email/password with admin-provisioned accounts and email activation. Google/Microsoft login and enterprise SSO are **not approved for MVP**.

**Design decision pending:** Detailed conflict precedence among department rules, per-document ACLs and privileged Chairman/Admin read roles. No implementation agent may invent a precedence rule.

## 4. Document and knowledge management

### 4.1 Content classification and supported formats

| ID | MVP functional requirement | Acceptance expectation |
|---|---|---|
| **FR-DOC-001** | Accept **PDF, Word and Excel** documents through authorized upload workflows. | Each supported format is accepted when valid; unsupported/invalid uploads are handled safely. |
| **FR-DOC-002** | Every document has one of two primary classifications: `PUBLIC` or `INTERNAL`. | Published `INTERNAL` content is not available to public/anonymous chat. |
| **FR-DOC-003** | `INTERNAL` documents carry department information and support document-specific permissions. | Search and source-opening enforce the applicable permissions. |
| **FR-DOC-004** | Only Website Manager and System Admin can upload and perform authorized document-management actions. | Other users cannot upload, approve, alter or delete managed company documents. |

### 4.2 Two-stage administrative review

**Required business workflow:**

`Upload → Admin review #1 → Approved processing → Admin review #2 → Publish/activate → Available to chatbot`

- **First review:** An authorized administrator checks the submitted document **before** its content is processed for retrieval.
- **Processing:** Only documents passing the first review may proceed through approved extraction/indexing operations. Implementation details remain architectural decisions.
- **Second review:** After processing, an authorized administrator checks the result **again** and explicitly approves publication.
- **Publication gate:** Unapproved, rejected, failed, deleted, expired/superseded or otherwise non-active content must not be served to users, including through caches.

| ID | MVP functional requirement | Acceptance expectation |
|---|---|---|
| **FR-DOC-005** | The system must track review/processing/publication progress for uploaded documents. | An authorized administrator can distinguish pending, rejected, failed and publishable items. |
| **FR-DOC-006** | Both review stages require an authorized administrative decision. | A document cannot bypass either mandatory review. |
| **FR-DOC-007** | Documents become usable by chatbot only after the second approval and successful activation. | A merely uploaded or processed document cannot appear in a response. |
| **FR-DOC-008** | Document versions are retained and distinguishable. | Administrators can inspect a document's version history. |
| **FR-DOC-009** | Retrieval uses only the latest approved `ACTIVE` version. | A superseded version is not returned in ordinary chatbot answers. |
| **FR-DOC-010** | Authorized administrators can edit document metadata and access permissions. | Subsequent authorized retrieval observes the updated permissions and metadata. |
| **FR-DOC-011** | Authorized administrators can perform **Soft Delete** and **Permanent Delete** as distinct human-managed operations. | Soft-deleted documents cease retrieval and are recoverable under approved policy; permanently deleted content cannot be restored through normal product recovery. |
| **FR-DOC-012** | Administrators can view upload owner, approval information and relevant document action history. | The interface exposes the available accountable record of those operations. |
| **FR-DOC-013** | Users can access an original document only when currently authorized. | An answer/source reference does not bypass the current document access policy. |

**Pending policy details:** Exact metadata fields, department-sharing rules, review rejection/retry procedure, version transition timing, retention/deletion safeguards, and requirements for Word/Excel source locations. The owner-provided baseline permits the same administrator to perform both reviews, subject to final approval.

## 5. Advanced RAG and evidence-grounded answers

| ID | MVP functional requirement | Acceptance expectation |
|---|---|---|
| **FR-RAG-001** | Support questions and answers in **Vietnamese and English**. | Chat accepts either language and can generate an appropriate response in the supported languages. |
| **FR-RAG-002** | Answer company-related questions from **authorized enterprise documents only**; do not search the public Internet for answer evidence. | Enterprise-specific factual claims do not rely on unapproved external web sources. |
| **FR-RAG-003** | Use Advanced Hybrid RAG for relevant evidence retrieval. | Retrieval can use approved semantic and lexical matching while respecting authorization. |
| **FR-RAG-004** | Support document-grounded Q&A, summarization, comparison and synthesis across permitted sources. | The answer covers requested tasks only as far as available evidence supports them. |
| **FR-RAG-005** | Retrieve across all documents the user is authorized to access by default. | Users are not required to manually select a document or department for each query. |
| **FR-RAG-006** | Pass relevant retrieved evidence to an approved LLM API for answer generation. | The answer reflects the retrieved authorized context; it does not invent company-specific facts unsupported by that context. |
| **FR-RAG-007** | When no sufficient evidence is available, explicitly say that relevant information was not found. | The system does not fabricate a company answer. |
| **FR-RAG-008** | If only part of a question can be answered, return only supported parts and identify unsupported parts. | Unsupported subanswers are omitted or qualified. |
| **FR-RAG-009** | Apply an owner-approved policy when sources conflict; where the conflict cannot be resolved, disclose it. | Contradictory evidence is not silently merged into a false statement. |
| **FR-RAG-010** | Maintain verifiable links between an answer and its supporting source documents/versions. | A source record can be validated against the correct authorized document/version. |
| **FR-RAG-011** | **Citation presentation is collapsed/hidden by default** but users can reveal supporting sources and open the original permitted document. | The default answer stays visually simple; source expansion respects current access rights. |
| **FR-RAG-012** | Where possible, sources provide excerpt and source location (such as PDF page, Word section, or Excel sheet/range). | Users can identify the supporting passage or location in the original file. |

**Citation clarification:** Evidence provenance is required; always-visible inline citations are **not** required for MVP. This implements the Project Owner's decision (question 49.A) and retains the evidence-based success criterion in `GOALS.md`.

**Pending policy details:** Specific language selection rules, acceptable conflicts/source-authority rules, source-location representation for different formats, and exact insufficient-evidence thresholds.

## 6. Basic agentic orchestration and cost-aware processing

| ID | MVP functional requirement | Acceptance expectation |
|---|---|---|
| **FR-AGENT-001** | Support a **basic Agentic RAG** workflow, without multi-agent runtime architecture. | Straightforward questions can be answered via a simple retrieval-and-answer path; complex questions may invoke a controlled multi-step path. |
| **FR-AGENT-002** | Use multiple retrieval/reasoning steps only when the question is complex or first-pass evidence is insufficient. | Routine questions need not incur the full agent workflow. |
| **FR-AGENT-003** | Reduce LLM API usage for simple/repetitive questions through an approved caching strategy and lower-cost model routing where appropriate. | A valid reusable response or simpler model path can serve qualifying questions without a full expensive workflow. |
| **FR-AGENT-004** | Cache reuse is permission-aware and reflects current document versions and access revocation. | No user can obtain inaccessible/stale content by triggering a cache hit. |
| **FR-AGENT-005** | Agent tools in MVP are **read-only** with respect to enterprise/business data. | The agent cannot autonomously upload, modify, delete or send data using side-effecting tools. |
| **FR-AGENT-006** | Tool access and workflow execution are checked against approved backend policies and operational bounds. | Unauthorized tools are denied, and runaway workflows cannot proceed without limit. |
| **FR-AGENT-007** | Partial success is allowed: answer what evidence supports and state what cannot be answered. | Failure in one part does not cause unsupported answers for the remainder. |
| **FR-AGENT-008** | Expose high-level progress states to users, without exposing private model reasoning. | The UI can show steps such as retrieving and composing an answer. |

**Pending architecture decisions:** Cache model/invalidation strategy, routing/classification policy, LLM model/provider selection, step budgets and read-only tool registry. These are not decisions for development agents.

## 7. Chat and administration interfaces

| ID | MVP functional requirement | Acceptance expectation |
|---|---|---|
| **FR-UI-001** | The primary experience for both anonymous visitors and employees is a **chat interface**. | Visitors land directly in chat; employees can use chat with authorized company context after sign-in. |
| **FR-UI-002** | Administrators have additional management functionality beyond the chat interface. | Website Manager/System Admin can access their authorized management functions. |
| **FR-UI-003** | Anonymous chat supports conversation context and **temporary history for the current session**. | Follow-up questions can use current-session context; no permanent anonymous account/history is implied. |
| **FR-UI-004** | Signed-in employees can view conversation history and reopen earlier permitted conversations. | The user can continue their own saved conversations subject to access policies. |
| **FR-UI-005** | Provide management functions for accounts and documents, including upload, two approvals, version history and allowed deletion operations. | Authorized administrators can complete the approved document lifecycle through UI functions. |
| **FR-UI-006** | Users can see their own department information when assigned. | A signed-in employee can identify their department; administrative visibility follows business rights. |
| **FR-UI-007** | Support a **Vietnamese/English** interface with user-selectable language. | Supported interface text can be switched between the two languages. |
| **FR-UI-008** | Provide appropriate permission-denied, not-found, processing and failure states. | Users receive understandable feedback without exposing restricted data. |
| **FR-UI-009** | Support source expansion/opening as specified in FR-RAG-010 through FR-RAG-012. | An authorized user can reveal sources without persistent citation clutter. |
| **FR-UI-010** | Frontend implementation must follow **Project Owner-authored and approved Figma designs**. | Development agents do not independently approve new screens, workflows or layouts. |

**Design boundary:** A simple, ChatGPT-like chat/dashboard experience is the design direction, **not** permission for an AI developer to invent a UI. Detailed components, screen structure and interactions are governed by approved Figma specifications.

## 8. Audit, dashboard, feedback and evaluation

| ID | MVP functional requirement | Acceptance expectation |
|---|---|---|
| **FR-AUD-001** | Audit sign-in, sign-out and security-relevant events. | Designated events can be traced by authorized operators. |
| **FR-AUD-002** | Audit document upload, approval, update and deletion operations. | Administrators can identify the actor, relevant document and outcome. |
| **FR-AUD-003** | **System Admin** can view all permitted system audit logs; **Website Manager** can view business-administration logs. | A Website Manager cannot access developer-only diagnostics solely through the business role. |
| **FR-DASH-001** | Admin dashboard shows user counts, document counts and chatbot usage. | Authorized administrators can view the corresponding measures. |
| **FR-DASH-002** | Dashboard shows ingestion progress, failed processing and operational error information. | Problems are visible with appropriate status information. |
| **FR-DASH-003** | Dashboard tracks LLM API token consumption, estimated cost, cache hit rate and response latency. | Available usage/cost measurements are visible; **tracking does not imply per-account token quotas**. |
| **FR-DASH-004** | Dashboard exposes available RAG quality/retrieval/agentic-workflow evaluation measures. | Authorized administrators can inspect measured results. |
| **FR-FEED-001** | Chat users can give positive/negative feedback, provide text feedback and report incorrect/inappropriate responses. | Feedback is accepted and available to authorized review functions. |
| **FR-EVAL-001** | Support evaluation using an approved **Golden Dataset** covering retrieval and answer quality. | Evaluations produce reviewable results against the approved dataset and measures. |
| **FR-ALERT-001** | Show incident information on the administration dashboard and send **system-generated email alerts** for approved severe incidents, including ingestion failures, LLM unavailability and severe security events. | Authorized recipients receive applicable operational notices. |

**Boundary:** Automated operational alerts are system functionality, **not** permission for the chatbot/agent to send autonomous emails. Continuous evaluation, scheduled evaluation and CI/CD evaluation are **not** required by the owner's selection of Golden Dataset evaluation alone.

## 9. Explicitly deferred features and exclusions

### 9.1 Deferred product features

- **Per-account token budgets/limits**, granting tokens, periodic resets, what happens when a user exhausts an allocation, and anonymous-user usage quotas (**questions 40 additional request and 46–48**): **DEFERRED**, because the Project Owner prioritized the chatbot first.
- **Google/Microsoft login and enterprise SSO:** Not approved for MVP; could be separately proposed later.
- **Multi-enterprise administration/hosting:** Not an MVP product requirement; platform reusability across document collections remains a goal.

**Distinction:** Token **telemetry and cost reporting** remain in scope through FR-DASH-003. Basic platform security and abuse protection remain subject to the security/NFR design even though *product token quotas* are deferred.

### 9.2 Excluded by `GOALS.md`

- Multi-agent **runtime** architecture (development Codex subagents are separate from runtime chatbot agents).
- Production Knowledge Graph / GraphRAG.
- Live CRM or ERP integrations.
- Autonomous email sending **by AI agents**.
- Autonomous enterprise document modification/deletion **by AI agents**.

The MVP makes no promise of zero hallucinations or perfect security.

## 10. Pending decisions for owner review

| ID | Decision still required | Why it matters |
|---|---|---|
| **P-FR-09** | Actual system-alert recipients, on-call addresses and final visibility of audit/dashboard/feedback data. | Prevents privilege and notification assumptions. |
| **P-FR-10** | Formal approval of Golden Dataset metrics and thresholds after benchmark. | Converts proposed targets into objective quality gates. |
| **P-FR-11** | Whether future `CONFIDENTIAL`/`RESTRICTED` egress tiers remain outside the MVP classification UI. | Keeps product classification aligned with provider-egress policy. |

The owner-provided answers for account lifecycle, System Admin scope, authorization precedence, file formats, review behavior, retention, answer language and evidence behavior are recorded in [`owner-decision-baseline.md`](owner-decision-baseline.md). The rows above remain **PENDING** until explicitly approved.

## 11. Traceability and approval

`GOALS.md → Functional Requirements → Architecture / Approved ADRs → Contracts → Tasks → Tests → Owner Acceptance`

- Requirements must be reflected in approved designs/contracts before implementation.
- Requirements changes must be reviewed for scope, security, data, UI, evaluation and operational impact.
- Only `harness/tasks/tasks.json` is the authoritative task-state record.

**Project Owner approval:** PENDING  
**Approved baseline:** None yet  
**Next review step:** Review the pending decisions above, then approve or revise this version.
