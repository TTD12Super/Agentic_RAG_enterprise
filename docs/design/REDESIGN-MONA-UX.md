# Enterprise Agentic RAG — MONA-style product UX redesign

**Agent:** Agent 1 — Senior Product/UI Designer  
**Status:** FROZEN v1.1 — Iteration 2 handoff baseline for Main Agent and Agent 2  
**Date:** 2026-11-12  
**Implementation status:** Specification only. No frontend or backend source was changed.

## 0. Purpose and design boundary

This document specifies a production-oriented interface for four areas:

1. Enterprise chat workspace.
2. Administration and knowledge operations.
3. Sign in.
4. Employee onboarding / registration request.

It is a handoff for Agent 2. It is not an approval to invent API behavior, permissions, roles, stored data or successful authentication states. The current backend contract and the authorization rules remain the source of truth.

The existing visual references in `docs/design/UI:UX reference/` already establish the Enterprise Knowledge AI direction: Inter typography, light surfaces, thin borders, controlled corporate red, compact enterprise tables and a 260px desktop navigation rail. This redesign keeps that usable foundation and makes the product feel more polished, more focused and more honest about unavailable backend capabilities.

The current frontend is a single React shell in `frontend/src/App.tsx` with a short-lived in-memory bearer token plus a backend HttpOnly session-cookie fallback, a backend-backed conversation history drawer, chat SSE, citation preview, and administration views. Registration/access-request screens are wired to their pending contract; Google OAuth is still unavailable.

### Scope lock

This v1 specification is intentionally complete enough for Agent 2 to implement the existing product boundary and its truthful unavailable states. It is frozen for handoff:

- **Included:** chat workspace, current-conversation recovery, history-unavailable state, SSE/Stop/Retry, citations, admin overview, document lifecycle/review, users/departments/access, audit/monitoring snapshot, email/password/MFA sign-in, and onboarding screens that do not claim unsupported submission.
- **Excluded:** frontend source implementation, backend/API changes, Figma authoring, new runtime agents, Google OAuth implementation, real binary upload before the contract is resolved, fake conversation history, fake email confirmation and fake metrics.
- **Agent 2 rule:** implement only mapped existing endpoints; keep missing capabilities visibly disabled or unavailable; escalate the six decisions in section 15 instead of inventing behavior.
- **Acceptance boundary:** the design is accepted when the rendered UI is usable, responsive, accessible, role-aware and truthful for every endpoint/state in section 12. It is not accepted merely because a static mock looks complete.

## 1. Visual language: MONA-inspired, not copied

The official MONA Media website was used only to derive broad design principles: premium but restrained presentation, large confident headings, strong CTA contrast, spacious composition, proof/metric blocks, clear service grouping and mobile-first behavior. No MONA logo, image, HTML, copy or proprietary asset is reused.

Design principles for this product:

- **Trust before decoration:** every status, permission and data boundary is visible and understandable.
- **Quiet enterprise canvas:** mostly white and very light neutral surfaces; red is reserved for the primary action, active route, important state and destructive confirmation.
- **Editorial hierarchy:** a strong page title, one concise explanation, one clear primary action, then dense but readable operational content.
- **One main decision per surface:** chat asks for a question; document review asks for one approval decision; onboarding asks for one identity action.
- **Human-scale density:** compact tables for admins, generous readable line length for answers, no ornamental panels that do not carry information.
- **Honest incomplete states:** “not available from the backend” is preferable to fabricated history, fake charts or a simulated Google login.
- **Progressive disclosure:** citations, audit metadata and document lifecycle detail are collapsed until requested.

The visual direction is compatible with the existing design reference and may be expressed in Figma before implementation. The Project Owner’s approved Figma specification remains authoritative if it conflicts with this written proposal.

## 2. Design tokens

These tokens are a design target, not a request to add a new styling dependency.

### 2.1 Color

| Token | Value | Use |
|---|---:|---|
| `canvas` | `#F9F9FF` | Application background |
| `surface` | `#FFFFFF` | Main cards, message surfaces, forms |
| `surface-subtle` | `#F1F3FF` | Sidebar sections, table headers, secondary controls |
| `surface-raised` | `#E1E8FD` | Selected rows, chips, metadata blocks |
| `ink` | `#141B2B` | Headings and primary content |
| `ink-muted` | `#5C403F` | Body copy and table values |
| `ink-subtle` | `#6B7280` | Metadata and helper copy |
| `line` | `#E5E7EB` | Dividers and borders |
| `brand-red` | `#C8102E` | Primary CTA and active state |
| `brand-red-dark` | `#9E001F` | Hover/pressed state and high-priority label |
| `brand-red-tint` | `#FEF2F2` | Active/error emphasis without alarm fatigue |
| `success` | `#087443` | Completed/allowed/healthy |
| `warning` | `#A14D00` | Pending, maintenance, retryable |
| `danger` | `#BA1A1A` | Denied, failed, destructive |

Do not use color alone to communicate a state. Every status badge also has text and, where useful, an icon.

### 2.2 Typography

Use Inter, already present in the visual references and current CSS.

| Token | Size / line height | Weight | Use |
|---|---:|---:|---|
| `display` | 36 / 44px | 600 | Admin page title on wide screens |
| `h1` | 30 / 38px | 600 | Primary screen title |
| `h2` | 20 / 28px | 600 | Section title |
| `title` | 16 / 24px | 600 | Card/row title |
| `body-lg` | 16 / 26px | 400 | Long answer reading |
| `body` | 14 / 22px | 400 | General copy |
| `body-sm` | 13 / 18px | 400 | Dense tables and metadata |
| `label` | 11–12 / 14–16px | 500–600 | Controls and status |

Use tabular figures for counts, timestamps, IDs and latency. Use sentence case for labels and buttons; use uppercase only for compact status labels.

### 2.3 Geometry and elevation

- 4px/8px spacing rhythm.
- 8px radius for buttons, inputs and small cards; 12–16px for major panels; 999px for status pills.
- 1px neutral borders as the default separation.
- Level 1: `0 1px 2px rgb(0 0 0 / 5%)`.
- Level 2: use only for a focused composer, open drawer or hovered interactive card.
- Level 3: use only for modal, command surface or citation drawer.
- Focus ring: 3px brand-red at approximately 18–20% opacity.

## 3. Product shell and page map

### 3.1 Shell

Desktop uses a 260px left rail, sticky topbar and a fluid content canvas. The rail contains the product mark/name, New chat, current conversation/history area, role-aware admin link, language control and signed-in profile. The topbar contains breadcrumbs, connection/status information, language switch and profile actions.

The shell must not expose admin navigation to a role that the backend would deny. Hiding a button is only a usability measure; every API call remains backend-authorized.

### 3.2 Proposed routes

These are UI routes, not claims that the current app already has a router.

| Route | Audience | Screen |
|---|---|---|
| `/chat` | Anonymous and authenticated | Chat workspace |
| `/chat/:conversationId` | Owner of conversation | Reopened chat; requires conversation authorization |
| `/sign-in` | All | Email/password + optional MFA |
| `/onboarding` | Unauthenticated employee candidate | Access request / invitation activation |
| `/admin/overview` | System Admin, Website Manager | Snapshot dashboard |
| `/admin/documents` | Managers; read policy still enforced | Document catalog and detail |
| `/admin/review` | Managers | Approval and ingestion work queue |
| `/admin/users` | Managers; privileged mutations policy-checked | Users, departments and access |
| `/admin/audit` | Managers according to audit policy | Audit and operational metadata |

`/onboarding` must branch into “request access” and “activate invited account” only after the corresponding backend endpoints exist. It must never create an active employee account on the client.

### 3.3 Role visibility

Use the canonical roles only: `system_admin`, `website_manager`, `employee`, `chairman`, plus anonymous public access.

- **Anonymous:** public chat only; no internal documents, admin or permanent history claim.
- **Employee:** authorized chat and own permitted history when the backend list/read contract exists.
- **Chairman:** broad published-document read access, but no admin controls and no access to another user’s conversation body.
- **Website Manager:** business administration, document lifecycle and business audit; no code/system controls.
- **System Admin:** Website Manager capabilities plus separately authorized system operations; still no automatic access to another user’s conversation body.

Explicit deny wins over allow. The UI must not label Chairman as “admin” or render an admin portal to Chairman.

## 4. Chat workspace redesign

### 4.1 Desktop wireframe

```text
┌──────────────────┬────────────────────────────────────────────────────────────┐
│ Enterprise AI    │ Enterprise Knowledge AI     [status] [VI|EN] [profile]     │
│ [+ New chat]      ├────────────────────────────────────────────────────────────┤
│ Search history    │ [conversation title / state]                              │
│                   │                                                            │
│ Conversation list │                 Welcome / message thread                   │
│  Today            │                                                            │
│  Yesterday        │                                            [source drawer]│
│                   │                                                            │
│ Admin (if allowed)├────────────────────────────────────────────────────────────┤
│ Profile / sign in │ [multiline question composer]              [Stop / Send]   │
└──────────────────┴────────────────────────────────────────────────────────────┘
```

### 4.2 Empty state

The landing state is purposeful, not a blank card:

- Heading: “Hỏi kho tri thức doanh nghiệp” / “Ask your enterprise knowledge base”.
- One sentence: answers use only sources the current session is authorized to access.
- Three or four neutral prompt suggestions, such as “Tóm tắt quy trình mua sắm” or “Compare the current policies”. These are examples, not claims that a document exists.
- A large composer at the visual center of the page.
- Anonymous scope badge: “Public knowledge only”. Authenticated scope badge: “Authorized enterprise sources”. Do not let the user type an arbitrary document scope.

### 4.3 Conversation sidebar and the current history limitation

The desired production sidebar contains:

- New chat.
- Search history.
- Grouped conversation rows by Today, Yesterday and Older.
- Title, last activity and a compact message count.
- Active row, keyboard focus, hover menu and “Delete/archive” only if the backend supplies those actions.

The current backend exposes `POST /api/v1/conversations` and `GET /api/v1/conversations/{conversation_id}`, but **does not expose a list/search conversation endpoint or a conversation title/update/delete contract**. The current frontend stores only one conversation ID in local storage. Therefore Agent 2 must implement the following honest interim state:

1. Show the current conversation and its messages when an ID is known and authorized.
2. Show “Conversation history will appear here when history sync is enabled” with a non-destructive explanation when no list endpoint is available.
3. Do not render fake historical rows from sample data.
4. Do not promise that clearing local storage deletes the server conversation.
5. Do not put another user’s conversation body in admin tables, audit rows or support views.

The production history experience is blocked until Main Agent approves and backend implements a list contract such as:

```text
GET /api/v1/conversations?limit=20&offset=0&search=<optional>
{
  "items": [{
    "conversation_id": "...",
    "title": "...",             // server-derived or user-set, never client-only truth
    "created_at": "...",
    "updated_at": "...",
    "message_count": 4
  }],
  "pagination": {"limit":20,"offset":0,"total":1,"has_more":false}
}
```

This is a proposed gap-filling contract, not an implemented endpoint.

### 4.4 Message and answer presentation

- User messages align right or use a quiet red-tint surface; assistant messages remain readable on the canvas rather than inside a heavy colored bubble.
- Use a maximum answer measure of roughly 760–840px.
- Render plain text/Markdown safely, with accessible headings, lists and code blocks if the backend answer format supports them. Never render raw HTML from retrieved text.
- Keep citations collapsed by default, with a visible “Sources (N)” control.
- Each citation row shows title, filename, file type and location when returned. Never lead with a raw UUID.
- “Preview” opens an authorized source drawer or inline panel. “Download original” is a separate action and performs a fresh authorization check.
- Feedback actions are Positive, Negative and optional comment. Do not imply that a feedback click changes the answer.

### 4.5 Streaming, stop, retry and maintenance

The backend SSE stream uses provider-neutral events: `message_start`, `citation`, `token`, `done` and `error`. The UI states are:

| Runtime state | Visual treatment | Available action |
|---|---|---|
| Ready | “Ready” badge | Send |
| Streaming | Red pulse, live text, disabled composer | Stop |
| Stopped / `CANCELLED` | Neutral warning with partial text clearly marked | Retry last question, New chat |
| Retryable error | Amber alert with request ID if safe | Retry, Reconnect |
| Non-retryable error | Red alert with safe message | Edit question, New chat |
| `MAINTENANCE_ACTIVE` | Amber maintenance banner | Wait / refresh status; do not repeatedly submit |
| Insufficient evidence | Calm neutral answer stating evidence is insufficient | Ask a narrower question |
| Citation revoked/unavailable | Source row marked unavailable | No preview/download; answer remains safe |

Stop must abort the browser stream and request backend cancellation through the existing durable-job seam where applicable. A front-end-only disappearance of the stream is not enough.

### 4.6 Chat mobile wireframe

```text
┌──────────────────────────────┐
│ ☰  Enterprise AI   profile   │
├──────────────────────────────┤
│ [New chat] [history drawer]  │
│                              │
│        message thread        │
│                              │
│  [sources drawer / bottom]   │
├──────────────────────────────┤
│ [Ask a question…       ] [↑] │
└──────────────────────────────┘
```

On mobile, history is an off-canvas drawer, the composer respects the safe-area inset, source preview is a bottom sheet, and long filenames wrap or truncate with a title tooltip. No horizontal scrolling is permitted for the main chat experience.

## 5. Admin redesign

The admin shell follows the same visual system but uses a more information-dense layout. It must never expose conversation bodies. All counts and status labels are marked as measured, estimated or unavailable according to the returned metric metadata.

### 5.1 Overview / dashboard

**Layout:** page title + date/snapshot label, primary action row, metric cards, ingestion health panel, recent audit/activity panel.

**Metric cards:** Users, documents, queries, ingestion jobs, latency, model cost, evaluation and cache hit rate. Cards with `available: false` show “Unavailable” plus the backend `reason` and provenance; do not display zero unless the backend actually returned zero.

**Current backend truth:** `GET /api/v1/dashboard` returns users, documents, usage, ingestion and unavailable/available telemetry metadata. It is a snapshot, not a time-series API. Do not draw a fake chart. Use a compact “No time-series data returned” panel until a chart contract exists.

**States:** loading skeleton, partial metrics, authorization denied, retryable backend unavailable, empty tenant, healthy snapshot and stale snapshot label.

### 5.2 Documents / knowledge inventory

**Catalog:** title, classification, lifecycle status, owner department, current version and last activity if returned. Provide search/filter controls only when the endpoint supports them; client-side filter is allowed only over the loaded page.

**Detail drawer:** document metadata, version list, current lifecycle state, access-grant summary and permitted actions. Never expose source content in a list row.

**Lifecycle stepper:**

```text
Upload → Quarantined → Review 1 → Processing → Review 2 → Active
                                      ↘ Failed / Rejected / Revoked
```

Actions are visibly role-gated and require confirmation for reject, revoke, soft delete and permanent delete. Permanent delete requires a second confirmation that displays retention/legal-hold consequences from the backend response, not invented copy.

**Important backend limitation:** the current `POST /api/v1/documents` implementation accepts a JSON `UploadRequest` containing metadata, `source_uri`, hash, size and MIME type. It does not currently accept a multipart file body or expose an object-storage upload URL. Agent 2 must not build a file picker that suggests the binary file was uploaded when only metadata was sent. Until the upload contract is completed, use a disabled upload state explaining “file upload connection is not available” or an explicitly labelled metadata/demo flow.

### 5.3 Review and ingestion

Use a queue view with tabs/filters for pending, processing, failed and completed. Each row shows document/version, stage, job ID, current state, attempt and safe error code. A detail panel presents review decisions and ingestion progress without exposing unapproved source content.

The current backend supports `GET /api/v1/approvals`, `GET /api/v1/ingestion-jobs/{job_id}`, review at `POST /api/v1/documents/{document_id}/versions/{version_id}/approve`, publish, revoke and deletion routes. The frontend must show the two review gates as separate decisions and must never show “Active” before backend publication confirms it.

### 5.4 Users and access

Use a searchable table only when server-side pagination/search is available; otherwise show the returned tenant page. Rows contain email, canonical roles, departments and active/inactive state. The detail drawer contains role and department editing controls only for authorized managers.

Access management sections:

- Departments: list/create/update using the existing department routes.
- Provision account: `POST /api/v1/users` or `/accounts`; show “Pending activation” because the current endpoint creates `active: false`.
- Activate account: existing `POST /api/v1/users/{user_id}/activate` / `/accounts/{user_id}/activate`.
- Document ACL: existing document access route with explicit `ALLOW`/`DENY` grants.
- Access request review: `GET /api/v1/access-requests` lists tenant-scoped safe metadata for managers; `POST /api/v1/access-requests/{request_id}/review` records an idempotent approve/reject decision. Authenticated requests use the principal tenant; anonymous requests are routed by server-only `BACKEND_ACCESS_REQUEST_TENANT_ID`, never by a browser tenant selector. Approval remains `APPROVED_PENDING_PROVISIONING` and never grants access or sends email automatically.

Never provide a “grant access” shortcut that merely edits the browser. The backend must evaluate role, department, document ACL, tenant and explicit deny precedence.

### 5.5 Audit and monitoring

Show metadata-only audit rows: time, event, action, outcome, decision, request/trace ID, principal ID where permitted, safe code and safe metadata. Do not display another user’s conversation body, prompts, model output, raw tokens or secrets.

The current backend supports `GET /api/v1/audit` and feedback review routes. The application also has a root `/healthz` liveness endpoint, but no current `/api/v1` live monitoring stream. Use refresh + “last updated” until a telemetry contract is supplied. Do not label a snapshot “real-time”.

## 6. Login design

### 6.1 Layout

Use a split but restrained layout on wide screens:

```text
┌──────────────────────────────┬──────────────────────────────┐
│ Enterprise AI                │ Sign in to your workspace    │
│ short trust/value statement  │ work email                   │
│ red/neutral abstract panel   │ password + show/hide          │
│ no fabricated company logos  │ MFA code when requested      │
│                              │ [Sign in]                     │
│                              │ [Google — not connected]     │
└──────────────────────────────┴──────────────────────────────┘
```

On mobile, stack brand mark above the form and keep the form to one column.

### 6.2 Implementable login flow

Current backend endpoint:

```text
POST /api/v1/auth/sign-in
{ "email": "...", "password": "...", "mfa_code": "..." }
→ { "access_token": "...", "token_type": "Bearer", "principal": {...} }
```

The form must provide email, password, optional MFA only when requested/needed, submit loading, invalid credentials, MFA-required, account inactive, backend unavailable and rate-limit states. Do not display roles from client input; render roles only from `principal` returned by the server.

Current `GET /api/v1/auth/me` and `POST /api/v1/auth/sign-out` are available. The backend sets an HttpOnly session cookie and the frontend sends credentialed requests, so a reload can restore identity when the configured backend identity store is available; the in-memory bearer remains a short-lived compatibility path. If the session is invalid, show a clear “session expired — sign in again” state.

### 6.3 Google sign-in

There is no Google OAuth endpoint, callback, provider configuration or server-issued Google session in the current backend. The requirements also record Google/Microsoft/SSO as not approved for MVP. Therefore:

- The Google button may exist as a disabled, clearly labelled “Google sign-in — not connected” design state for stakeholder review.
- It must not open a fake popup, return a fake principal, or show a success toast.
- Agent 2 must leave it disabled unless Main Agent and Project Owner approve an OAuth contract and backend implementation.

## 7. Registration / onboarding design

### 7.1 Product decision reflected in the UX

Public self-registration of an active employee account is not allowed by the current requirements. The production UX therefore uses two honest paths:

1. **Request access:** an employee candidate submits a work email, name, department/requested area, reason and consent. This records a request only; it never grants access.
2. **Activate invitation:** an administrator-provisioned user follows an email link, confirms identity, sets a password and completes required MFA enrollment where applicable.

### 7.2 Three-step request-access wireframe

```text
1. Your work identity       2. Confirm request          3. Status
[Name] [Work email]         Review submitted details     Request received
[Department]                [Back] [Submit request]     Reference only if API returns it
[Reason]                    Consent checkbox             “Awaiting administrator review”
```

The success state must be used only after the backend responds successfully. If the endpoint is absent, show a disabled submit state and a concise explanation directing the user to the administrator. Never generate a request ID in the browser.

### 7.3 Current backend gaps

- `POST /api/v1/access-requests`, manager listing and approve/reject review routes now exist; access requests are durable when PostgreSQL is configured, but they do not yet provision an identity or send email.
- Account creation exists for managers, but it returns an inactive account and there is no current email invitation or activation-token endpoint.
- There is no password-reset endpoint.
- There is no email verification/confirmation endpoint.
- There is no Google OAuth flow.

Until durable persistence, provisioning and email activation are implemented and reviewed, Agent 2 must keep the pending/provisioning states explicit and must not claim a completed registration flow.

## 8. Component state specification

Every data-driven component must support these states.

| Component | Required states |
|---|---|
| Page | loading, ready, empty, permission denied, not found, retryable outage |
| Conversation list | unavailable contract, empty, populated, searching, no results, stale selection |
| Composer | ready, submitting, streaming, stopped, disabled by maintenance, validation error |
| Assistant answer | streaming, answered, insufficient evidence, failed, cancelled, citation unavailable |
| Citation row | collapsed, expanded, preview loading, preview ready, preview denied/revoked, download unavailable |
| Metric card | measured, estimated, unavailable with reason, stale |
| Document row | quarantined, processing, pending review, active, rejected, failed, revoked |
| Approval action | idle, confirmation, submitting, succeeded, conflict/409, denied, retryable failure |
| Auth form | idle, field error, submitting, invalid credentials, MFA required, inactive, unavailable |
| Onboarding | draft, validation error, unavailable endpoint, submitted, awaiting review |
| Toast/banner | success, neutral info, warning, error; dismissible and announced |

Use skeletons for first load, not a spinner that shifts the page. Preserve user-entered text across retryable failures. A 403/404 message must not reveal whether a protected document exists.

## 9. Exact interaction flows

### 9.1 First visit → public chat

1. Load the shell and show the public knowledge scope.
2. Do not require sign-in for a public query.
3. Create an anonymous session through `POST /conversations` when the user sends the first query.
4. Stream authorized events.
5. Persist only the current session/conversation handle as allowed; do not promise permanent anonymous history.
6. Invite sign-in only when the user attempts an employee-only action, not before a public answer.

### 9.2 Sign in → own chat

1. Submit email/password to `POST /auth/sign-in`.
2. If MFA is required, keep the form context and request the code; do not discard the password field until safe.
3. On success, render the server principal and authorized navigation.
4. Reopen only a conversation ID that the backend authorizes.
5. If the history list endpoint is still missing, show current-conversation-only limitation.
6. On 401/session expiry, preserve the unsent question locally in component state, request sign-in and resume only after explicit user action.

### 9.3 Ask → stream → source preview

1. Validate non-empty query client-side, then let backend enforce length and policy.
2. Disable duplicate submit, show Streaming and Stop.
3. Render citations only from `citation` events or the final answer payload.
4. On `done`, render the final status and enable feedback.
5. Preview calls `GET /answers/{answer_id}/citations/{citation_id}/preview` with a fresh authorization check.
6. Download calls the separate download endpoint; never reuse preview content as a file.

### 9.4 Admin document review

1. Load only the authorized queue.
2. Open detail and show lifecycle metadata, not unapproved source text.
3. Confirm stage 1 or stage 2 decision with an idempotency key.
4. Refresh the returned version/job status.
5. Show Publish only when backend state permits it.
6. On policy outage, disable mutation actions and show retryable state; do not optimistically update the row.

### 9.5 Onboarding request

1. Validate name, company email, requested department and reason.
2. Display consent and privacy copy.
3. If `/access-requests` is unavailable, explain that an administrator must provision the account and do not submit.
4. When implemented, send the request and show only the response fields returned by backend.
5. Never convert the request into a principal or active session.

## 10. Responsive behavior

| Breakpoint | Behavior |
|---|---|
| `>= 1280px` | Persistent 260px rail; centered 840px chat column; optional 360–380px citation drawer; full admin tables |
| `1024–1279px` | Slide-over navigation or 64px icon rail; two-column admin sections collapse when necessary |
| `768–1023px` | Single main content column; table becomes horizontal-scroll region; citation drawer becomes panel |
| `< 768px` | Off-canvas history/admin navigation; full-width chat; bottom-sheet sources; composer fixed above safe area |
| `< 480px` | One-column metric cards, wrapped actions, no clipped status badges, 44px touch targets |

Acceptance checks:

- No page-level horizontal overflow at 320px, 375px, 768px, 1024px and 1440px.
- Long Vietnamese and English labels wrap without breaking cards.
- Tables can scroll inside their own region without moving the whole page.
- Sticky composer never covers the last message or keyboard focus.
- Dialogs and drawers remain usable at 200% browser zoom.

## 11. Accessibility acceptance criteria

- One meaningful `h1` per screen and correct heading order.
- Landmarks: `header`, `nav`, `main`, `aside`, and `footer` where used.
- Every input has a visible or programmatic label; validation is associated with the field.
- Keyboard-only navigation reaches New chat, history rows, composer, Stop, Retry, citation Preview and admin actions in logical order.
- Visible focus ring is never removed without an accessible replacement.
- Minimum interactive target is 44×44 CSS pixels on touch surfaces.
- Normal text meets WCAG AA contrast; status is communicated with text/icon in addition to color.
- Streaming updates use `aria-live="polite"` without announcing every token; announce start, completion, stop and error only.
- Stop is available by keyboard and does not trap focus.
- Modals/drawers have a labelled heading, Escape behavior and focus return.
- Respect `prefers-reduced-motion`; no required information depends on animation.
- Citation preview content has a readable title, source location and close control.
- Error text is actionable and safe; do not reveal protected document existence or raw backend exceptions.
- `lang` is switched for Vietnamese/English UI modes when localization is implemented.

## 12. API mapping and implementation truth table

Base URL is `/api/v1`. “Existing” means the current backend route was found in `backend/app/api`; “FE gap” means backend exists but the current frontend does not use it; “backend gap” means the design must not pretend it works yet.

| UI section / action | Current endpoint | Payload returned / accepted | Status and honest UX |
|---|---|---|---|
| Public chat create | `POST /conversations` | Returns `conversation_id`, `tenant_id`, `session_id`, `expires_at` | Existing; FE wired |
| Reopen one chat | `GET /conversations/{id}` | `conversation_id`, `messages[]` with ID, role, content, created_at | Existing; authorization required |
| Chat durable submit | `POST /conversations/{id}/messages` | Accepts `{query}`; returns `job_id` and job state | Existing; FE helper exists, polling recovery |
| Chat streaming | `POST /conversations/{id}/messages/stream` | Accepts `{query}`; SSE `message_start`, `citation`, `token`, `done`, `error` | Existing; FE wired |
| Query recovery | `GET /query-jobs/{job_id}` | State, answer when complete, error/maintenance metadata | Existing; use on stream interruption |
| Citation preview | `GET /answers/{answer_id}/citations/{citation_id}/preview` | Citation, preview, title, filename, location | Existing; separate reauthorization |
| Original source | `GET /answers/{answer_id}/citations/{citation_id}/download` | Binary response after authorization | Existing backend; current FE design should add separate action |
| Answer feedback | `POST /answers/{answer_id}/feedback` | Accepts rating/comment; returns feedback ID | Existing; current FE supports rating |
| Conversation list/search | `GET /conversations?limit&offset&search` | Paged items with title and timestamps | Existing; FE history drawer reads metadata |
| Conversation rename/archive/delete | None | No approved payload | Backend gap; hide actions |
| Sign in | `POST /auth/sign-in` | Accepts email/password/optional MFA; returns bearer + principal | Existing; FE wired |
| Current identity | `GET /auth/me` | Returns server principal | Existing; HttpOnly cookie restore plus memory bearer fallback |
| Sign out | `POST /auth/sign-out` | 204 | Existing; FE wired |
| Google sign-in | None | No OAuth initiation/callback/session | Backend gap and not approved MVP; disabled state |
| Registration/access request | `POST /access-requests` | Records a pending request with idempotency; it never grants access | Backend wired; manager review is wired; durable provisioning and email confirmation remain unavailable |
| Access request review | `GET /access-requests`, `POST /access-requests/{request_id}/review` | Tenant-scoped applicant metadata and idempotent approve/reject state | Backend + Users UI wired; Postgres persistence requires migrations/configuration; provisioning/email remain unavailable |
| Email confirmation / activation | None at runtime | No invite token, verify or password-set payload | Backend gap; no fake success |
| Admin overview | `GET /dashboard` | Metric objects with value, availability, provenance, period, reason | Existing; snapshot only |
| Document catalog | `GET /documents?limit&offset` | Paged document metadata | Existing backend; current FE reads it |
| Document detail | `GET /documents/{id}` | Document metadata | Existing backend; FE gap |
| Document versions | `GET /documents/{id}/versions` | Version/approval/job metadata list | Existing backend; FE gap |
| Upload / quarantine | `POST /documents` | Current code accepts JSON metadata `UploadRequest`; returns job payload | Existing metadata route, but no binary multipart upload; major gap |
| Ingestion status | `GET /ingestion-jobs/{job_id}` | Job state, stage, attempt, error code | Existing backend; FE gap |
| Approval queue | `GET /approvals` or `/documents/approval-queue` | Paged pending version records | Existing backend; FE reads queue |
| Review decision | `POST /documents/{id}/versions/{version}/approve` | Accepts stage + APPROVE/REJECT + idempotency header | Existing backend; FE mutation gap |
| Publish/revoke/delete | POST/DELETE document lifecycle routes | Version/job or 204, idempotency where required | Existing backend; FE mutation gap |
| Document ACL | `POST`/`PUT /documents/{id}/access` | Grants with action/effect and optional user/role/group/department | Existing backend; FE mutation gap |
| Users | `GET /users` or `/accounts` | `{users:[...]}` | Existing backend; FE reads users |
| Create user | `POST /users` or `/accounts` | User request; returns inactive identity | Existing backend; no email invitation |
| Update/activate user | `PATCH /users/{id}`, `POST /users/{id}/activate` | Updated user / user identity | Existing backend; FE mutation gap |
| Departments | `GET /departments`, POST/PATCH routes | Department records | Existing backend; FE reads list |
| Audit | `GET /audit?limit&offset` | Metadata-only paged audit events | Existing; no conversation bodies |
| Feedback review | `GET /feedback` or `/feedback/review` | Paged feedback records and rating filter | Existing backend; FE gap |
| Liveness | `GET /healthz` | `{status:"ok"}` | Existing root route; not a full dependency/monitoring health check |

### 12.1 Contract conflict to escalate

`docs/contracts/ingestion.md` describes a multipart upload boundary, while the current `backend/app/api/admin.py` route validates a JSON `UploadRequest` and stores only metadata/source URI. Main Agent must choose and version the actual upload contract before Agent 2 ships a production file-upload UI.

## 13. Backend gaps for Main Agent

Priority order for a real production chat product:

1. **Configured durable authenticated session:** the HttpOnly cookie path is implemented; the in-memory fallback remains only for local/demo mode when PostgreSQL is not configured.
2. **Employee onboarding completion:** request recording, Postgres persistence and manager review now exist when the database is configured; identity provisioning, email invitation, activation token, password set/reset and verification remain to be implemented.
3. **Conversation URL restore:** history search and load-more now exist; grouping and deep-link semantics remain a UX enhancement.
4. **Google OAuth decision and implementation:** only if the Project Owner changes the current MVP decision.
5. **Binary document upload/object-storage contract:** align docs and implementation before exposing a real file picker.
6. **Admin mutation schemas in frontend contract:** exact form validation, response envelopes, conflict errors and optimistic-lock behavior.
7. **Monitoring/telemetry contract:** distinguish liveness, dependency readiness, time-series metrics and alerts.
8. **Localization contract:** supported UI language strings and answer-language behavior.

These are not silently implemented by the designer. Agent 2 may build read-only existing screens and unavailable states while the gaps are pending.

## 14. Handoff checklist for Agent 2

### Before implementation

- [ ] Read this document, `docs/design/IMPLEMENTATION-BOUNDARY.md`, `docs/contracts/v1-baseline.md`, `docs/contracts/identity-and-policy.md`, `docs/contracts/admin-management.md` and the relevant ingestion/answer contracts.
- [ ] Confirm whether the Project Owner has an approved Figma version. If it conflicts with this document, stop and report the conflict to Main Agent.
- [ ] Do not invent Google OAuth, email activation or binary upload success; access requests must remain truthful through pending/review/provisioning states.
- [ ] Keep role names and deny semantics canonical.
- [ ] Map every button to an existing endpoint or render it disabled with an explanation.

### Chat

- [ ] Implement current conversation restore and clear 404/403 behavior.
- [ ] Preserve SSE status transitions and durable polling recovery.
- [ ] Add explicit Stop/Retry/Reconnect states.
- [ ] Keep citations collapsed by default; add separate preview/download affordances.
- [ ] Do not expose raw IDs as the primary source label when title/filename is returned.
- [ ] Use honest history-unavailable state until list/search exists.

### Admin

- [ ] Keep unavailable dashboard metrics unavailable rather than zero.
- [ ] Build document lifecycle stepper from backend states, not visual-only states.
- [ ] Add mutation confirmation and idempotency handling only where routes support it.
- [ ] Never place conversation bodies into audit or admin views.
- [ ] Treat upload as blocked until JSON-vs-multipart contract is resolved.

### Auth/onboarding

- [ ] Implement email/password/MFA sign-in and safe error states.
- [ ] Show Google as disabled/pending, never as a simulated success.
- [ ] Show request-access/activation forms as unavailable until their endpoints exist.
- [ ] Keep entered form data on retryable failures and never create a client-side principal.

### Quality gate

- [ ] Test desktop at 1440px and 1280px, tablet at 768px/1024px, mobile at 320px/375px/480px.
- [ ] Test keyboard-only flow and screen-reader labels for chat, citations, dialogs and admin actions.
- [ ] Test empty/loading/403/404/409/422/429/500/503 states.
- [ ] Test session expiry, stream interruption, Stop, retry and maintenance.
- [ ] Run `npm run typecheck`, `npm run lint`, frontend tests and production build.
- [ ] Run backend contract and integration tests without weakening authorization tests.
- [ ] Ask Agent 3 to judge the rendered UI, not the source code, after each integrated iteration.

## 15. Decision requests to Main Agent

The following decisions are material and are intentionally not made by Agent 1:

1. Approve the proposed conversation-list/search contract and retention/title semantics.
2. Approve a secure browser session/refresh strategy.
3. Approve whether employee onboarding is request-only, invitation-only or both, then replace the current in-memory review flow with durable provisioning/email activation.
4. Decide whether Google OAuth is added after the current MVP exclusion.
5. Resolve the JSON-vs-multipart document upload conflict.
6. Approve the Figma source of truth for the final visual handoff.

Until these are resolved, the correct product behavior is a polished UI with truthful “not connected yet” states, not simulated production behavior.

## 16. Iteration 2 — customer findings

**Customer score:** 66/100  
**Scope:** visual experience, usability and production-facing behavior; no code review.  
**Design response:** Agent 1 only. This section adds UX decisions and acceptance criteria for Agent 2. It does not add or assume backend endpoints.

### 16.1 Finding: citation download fails

**Customer observation:** The Download citation action is visible but fails.

**UX solution:**

- Separate `Preview` and `Download original` in the source drawer; never reuse preview text as a file download.
- Render Download only when the answer has a valid `answer_id`, the citation has a valid `citation_id`, and the current contract exposes the download action.
- While downloading, disable only that citation’s Download button and show “Preparing file…”. Keep the rest of the answer usable.
- On 401/403/404/410, show “This source is no longer available for your session.” Do not show raw backend detail or imply the document exists.
- On retryable 5xx/timeout, show Retry for that download only. Never show a success toast before the binary response is received.
- If the endpoint is not wired, show a disabled `Download unavailable` affordance with a short explanation rather than a dead button.

**Existing API truth:** `GET /api/v1/answers/{answer_id}/citations/{citation_id}/download` exists in the backend and returns binary content, but the current frontend client does not expose a dedicated download helper.

**Acceptance criteria:**

- An authorized 2xx response downloads a file with the server-provided content type/name when available.
- Preview success never counts as Download success.
- A failed download leaves the answer and citation list intact and exposes a scoped Retry.
- A denied, revoked or expired citation never exposes source bytes or a misleading success state.
- Keyboard and screen-reader users can distinguish Preview from Download.

### 16.2 Finding: fresh page shows a stale backend error

**Customer observation:** After an earlier backend failure, a fresh page still displays the old error.

**UX solution:**

- Scope errors to the page/resource/request that produced them; do not use one global error string for the whole shell.
- On a full page load or route entry, initialize the view in Loading/Ready state and clear transient request errors before making the new request.
- Do not persist backend error banners in local storage or reuse them as initial state.
- If a conversation ID is restored, show “Restoring conversation…” first; show an error only when that restoration request fails now.
- If the current session is stale, show the session-specific reconnect/sign-in action, not a generic old backend error.

**Acceptance criteria:**

- After a prior 500, a fresh page has no old error before the new request completes.
- A new failure is shown only in the component that owns the failed request.
- Navigating from a failed admin screen to chat does not carry the admin error into chat.
- Reloading does not resurrect transient error text from browser storage.
- Retry replaces the scoped error with Loading and then the new result.

### 16.3 Finding: `/admin` has no route or guard

**Customer observation:** The admin experience is not reachable as a guarded production route.

**UX solution:**

- Treat `/admin` as a route group with `/admin/overview` as its default child; preserve the existing conceptual page map.
- Direct navigation to `/admin` resolves to `/admin/overview` only after identity and role checks complete.
- Anonymous users receive a sign-in surface; `employee` and `chairman` receive a safe unauthorized/unavailable state and no admin data request.
- `website_manager` and `system_admin` may enter the business admin shell; Chairman must not be treated as an administrator.
- The guard is a UX optimization only. Every admin endpoint still performs backend authorization, and a 403/404 remains a valid runtime outcome.
- If the current implementation has no router yet, Agent 2 may add the smallest existing-project routing mechanism; this does not create new backend behavior.

**Acceptance criteria:**

- Visiting `/admin` directly reaches the correct guarded state after identity resolution.
- Anonymous, employee and chairman sessions cannot see admin data or trigger admin fetches.
- Manager sessions can navigate between overview, documents, review, users and audit without losing the shell.
- Refreshing an allowed admin child route preserves the route or returns to a safe authorized default.
- A backend denial is rendered as a safe permission state, never as a blank page or client-side role override.

### 16.4 Finding: history shows only the current conversation

**Customer observation:** The sidebar does not show saved conversations; it only shows the current conversation.

**UX solution:**

- Keep the current conversation card prominent, but label it explicitly as `Current conversation`, not `History`.
- Until a list/search endpoint exists, show an honest empty panel: “Conversation history is not connected yet.” Include New chat and the current conversation only.
- Do not create fake historical rows from local storage, sample data or previous page state.
- Do not show search, rename, archive or delete actions while their server contracts are absent.
- When Main Agent approves a list endpoint, replace the unavailable panel with server-paginated rows grouped by server timestamps; search must query the server or only loaded records with clear scope.

**Existing API truth:** The backend has create and get-one conversation endpoints but no list/search endpoint, title contract or conversation delete/archive contract.

**Acceptance criteria:**

- The UI never presents fabricated older conversations.
- Current conversation reload still works when its ID and session are authorized.
- Missing history is explained in one compact, non-alarming state with no dead search field.
- A new chat does not claim that the previous conversation was deleted.
- Once a real list endpoint is available, the sidebar can show title, updated time, message count and pagination from server data.

### 16.5 Finding: login error leaks into Request access

**Customer observation:** A failed login displays or routes into Request access content, mixing two different flows.

**UX solution:**

- Keep Login and Request access as separate routes/screens and separate component state machines.
- Login errors stay beside the login form: invalid credentials, MFA required, inactive account, session error or backend unavailable.
- Request access shows truthful recorded/pending state; manager users can review requests, while provisioning/email remain explicit unavailable states.
- A login failure never redirects to onboarding automatically. Provide an explicit, secondary “Request access” link only if the product owner wants it.
- Preserve the email field on retryable login failures; clear only secrets according to the security policy.

**Acceptance criteria:**

- Invalid login remains on the login screen and has no Request access success/error banner.
- Opening Request access starts with its own clean state and does not inherit login error text.
- No login error reveals account existence beyond the approved safe message.
- Keyboard focus moves to the first invalid field or error summary.
- If the access-request endpoint is unavailable, submit is disabled with a truthful explanation; review actions are never optimistic.

### 16.6 Finding: VI/EN switch does not work

**Customer observation:** The language control is visible but changing it does not translate the interface.

**UX solution:**

- Treat language as a real application state, not a decorative toggle.
- Maintain a complete translation catalog for every static shell, auth, chat, admin, error, empty and accessibility label before enabling the switch.
- When the catalog is not wired, hide the switch or render it disabled with `Language switch unavailable`; do not leave a no-op control.
- Changing language updates visible labels, document direction metadata where needed, date/number formatting conventions and `lang` for assistive technology.
- Do not imply that the answer language is controlled by the UI switch unless the backend answer-language contract supports it; label that boundary clearly.

**Acceptance criteria:**

- VI → EN and EN → VI change all visible product-owned strings on the current screen.
- No mixed-language button, error, empty state or aria label remains in the switched shell.
- The active language is visually and programmatically announced.
- The choice survives navigation only if the frontend explicitly supports that persistence; otherwise it resets predictably and visibly.
- If translation coverage is incomplete, the control is unavailable rather than a no-op.

### 16.7 Finding: Markdown answer is rendered literally

**Customer observation:** Markdown markers are shown as literal text instead of readable headings, lists or emphasis.

**UX solution:**

- Render the backend answer as a safe, limited Markdown subset: headings, paragraphs, emphasis, ordered/unordered lists, inline code, fenced code and safe links.
- Treat answer text and retrieved source text as untrusted. Escape raw HTML, reject unsafe URL schemes and never execute embedded scripts or event attributes.
- Keep citation controls outside the Markdown renderer so a model-generated link cannot replace Preview/Download authorization.
- During streaming, render progressively but preserve valid paragraph/list boundaries; on completion, run the same safe renderer over the final answer.
- If the renderer is unavailable, display escaped plain text intentionally and do not show broken Markdown controls.

**Acceptance criteria:**

- `**bold**`, headings, bullets, numbered lists, inline code and fenced code are readable in the final answer.
- Raw HTML/script payloads are displayed safely or removed; they never execute.
- `javascript:`, `data:` and other unsafe links are not clickable.
- Streaming and completed answer rendering use the same safety rules.
- Citation Preview/Download remains a controlled application action, not a Markdown link side effect.

### 16.8 Finding: Google OAuth and email confirmation are missing

**Customer observation:** Production onboarding appears incomplete because Google sign-in and email confirmation cannot complete. Access-request submission now records a pending request but does not complete onboarding.

**UX solution:**

- **Google OAuth:** show a disabled `Continue with Google — not connected` state only if stakeholders need to see the future location. No popup, fake callback, fake principal or success toast.
- **Request access:** submit to `POST /api/v1/access-requests` and show the returned pending state. The manager review queue uses the separate list/review endpoints; no browser action may imply provisioning or email delivery.
- **Email confirmation:** provide an invitation activation screen only as an unavailable/pending flow until the backend supplies a signed invitation/activation contract. Never show “email sent” or “account activated” from the browser alone.
- **Current viable MVP path:** keep email/password sign-in and manager-provisioned inactive users as the only real authentication path. Make the inactive state explicit.

**Acceptance criteria:**

- Google never presents a successful login without a real backend callback and verified principal.
- Request-access submission cannot send data to a nonexistent route.
- Email confirmation never fabricates a token, request ID, email-sent state or active session.
- Inactive provisioned users receive a clear activation-required state from the backend response.
- Each unavailable capability has a visible explanation and a safe next action, without exposing secrets or internal stack traces.

### 16.9 Iteration 2 handoff gate

Agent 2 may implement this iteration only when each change is mapped to an existing endpoint or a deliberately unavailable state. Before Agent 3 re-evaluates, verify:

- [ ] Download is either fully wired to the existing binary endpoint or visibly unavailable; no dead button.
- [ ] Fresh route loads clear stale transient errors.
- [ ] `/admin` and child routes have client-side navigation plus backend-enforced guards.
- [ ] History limitation is explicit and no fake rows are shown.
- [ ] Login and Request access have isolated state and error ownership.
- [ ] VI/EN is functional or disabled; no no-op toggle remains.
- [ ] Markdown is safely rendered or deliberately escaped plain text.
- [ ] Google OAuth and email activation remain clearly pending until their real contracts exist; access requests remain pending until administrator review.
- [ ] Agent 3 tests the rendered experience at desktop, mobile and keyboard-only breakpoints.

