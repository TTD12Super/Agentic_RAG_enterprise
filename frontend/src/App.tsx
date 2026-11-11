import { FormEvent, useEffect, useMemo, useState } from 'react'
import {
  ConversationMessage,
  createConversation,
  Dashboard,
  DepartmentRecord,
  DocumentRecord,
  ApprovalRecord,
  AuditRecord,
  getAccessToken,
  getApprovals,
  getConversation,
  getCurrentIdentity,
  getAuditEvents,
  getDashboard,
  getDepartments,
  getDocuments,
  getUsers,
  Principal,
  previewCitation,
  QueryAnswer,
  signIn,
  signOut,
  submitFeedback,
  submitMessage,
  UserRecord,
  waitForQueryCompletion,
} from './api/client'
import { appConfig } from './config'
import './styles.css'

type View = 'chat' | 'dashboard' | 'documents' | 'approvals' | 'users' | 'audit'

const navItems: Array<{ id: View; label: string; icon: string; manager?: boolean; admin?: boolean }> = [
  { id: 'chat', label: 'Knowledge chat', icon: '✦' },
  { id: 'dashboard', label: 'Overview', icon: '▦', manager: true },
  { id: 'documents', label: 'Knowledge documents', icon: '▤' },
  { id: 'approvals', label: 'Review & ingest', icon: '✓', manager: true },
  { id: 'users', label: 'Users & access', icon: '♙', manager: true, admin: true },
  { id: 'audit', label: 'Audit & monitoring', icon: '◷', manager: true },
]

function hasRole(principal: Principal | null, role: string): boolean {
  return principal?.roles.includes(role) ?? false
}

function canManage(principal: Principal | null): boolean {
  return hasRole(principal, 'system_admin') || hasRole(principal, 'website_manager')
}

function canAdmin(principal: Principal | null): boolean {
  return hasRole(principal, 'system_admin')
}

function Icon({ children }: { children: string }) {
  return <span className="icon" aria-hidden="true">{children}</span>
}

function StatusBadge({ children, tone = 'neutral' }: { children: string; tone?: 'neutral' | 'success' | 'warning' | 'danger' }) {
  return <span className={`status-badge status-${tone}`}><span className="status-dot" aria-hidden="true" />{children}</span>
}

function ErrorNotice({ message }: { message: string }) {
  return <div className="notice notice-warning" role="alert"><Icon>!</Icon><div><strong>Backend request unavailable</strong><span>{message}</span></div></div>
}

function UnavailableView({ title, endpoint }: { title: string; endpoint: string }) {
  return <section className="empty-state card" aria-labelledby="unavailable-title">
    <div className="empty-icon"><Icon>⌁</Icon></div>
    <p className="eyebrow">Backend contract boundary</p>
    <h1 id="unavailable-title">{title}</h1>
    <p>This screen does not invent data. The current backend has no list/read endpoint for this resource yet.</p>
    <p className="helper-text">Missing endpoint: {endpoint}</p>
  </section>
}

function AuthView({ onAuthenticated, onCancel, onToast }: { onAuthenticated: (principal: Principal) => void; onCancel: () => void; onToast: (message: string) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const principal = await signIn(email, password, mfaCode || undefined)
      onAuthenticated(principal)
      onToast('Signed in through the backend identity API.')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Sign-in failed.')
    } finally {
      setBusy(false)
    }
  }

  return <section className="auth-card card" aria-labelledby="sign-in-title">
    <p className="eyebrow">Backend identity</p>
    <h1 id="sign-in-title">Sign in to enterprise knowledge</h1>
    <p className="muted">Roles, tenant and department access come from the backend. No client-side role preview is used.</p>
    {error && <ErrorNotice message={error} />}
    <form className="auth-form" onSubmit={submit}>
      <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="username" /></label>
      <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" /></label>
      <label>MFA code <span className="helper-text">(if required)</span><input value={mfaCode} onChange={(event) => setMfaCode(event.target.value)} autoComplete="one-time-code" /></label>
      <div className="heading-actions"><button className="button button-secondary" type="button" onClick={onCancel}>Cancel</button><button className="button button-primary" type="submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button></div>
    </form>
  </section>
}

function formatLocation(citation: QueryAnswer['citations'][number]): string {
  const locator = citation.locator
  if (!locator) return 'Verified source reference'
  if (locator.page !== undefined) return `Page ${locator.page}`
  if (locator.heading) return `${locator.heading}${locator.paragraph ? ` · paragraph ${locator.paragraph}` : ''}`
  if (locator.sheet) return `${locator.sheet}${locator.cell_range ? ` · ${locator.cell_range}` : ''}`
  return 'Verified source reference'
}

function AnswerDetails({ answer, citationOpen, preview, onToggleCitations, onPreview, onFeedback, onToast }: { answer: QueryAnswer; citationOpen: boolean; preview: string; onToggleCitations: () => void; onPreview: (citationId: string) => void; onFeedback: (rating: 'POSITIVE' | 'NEGATIVE') => void; onToast: (message: string) => void }) {
  return <>
    <div className="citation-block"><button className="citation-toggle" type="button" aria-expanded={citationOpen} onClick={onToggleCitations}><span><Icon>⌕</Icon> {citationOpen ? 'Hide citations' : `View ${answer.citations.length} citation${answer.citations.length === 1 ? '' : 's'}`}</span><span>{citationOpen ? '⌃' : '⌄'}</span></button>{citationOpen && <div className="citation-list">{answer.citations.length ? answer.citations.map((citation) => <div className="citation-row" key={citation.citation_id}><div className="file-icon">{citation.locator?.kind || 'SRC'}</div><div className="citation-text"><strong>{citation.document_id}</strong><span>{citation.citation_id} · {formatLocation(citation)}</span></div><button className="text-button" type="button" onClick={() => onPreview(citation.citation_id)}>Preview</button></div>) : <p className="helper-text">The backend returned no citations.</p>}</div>}</div>
    {preview && <div className="detail-section highlighted"><div className="detail-label">Authorized preview</div><p>{preview}</p></div>}
    <div className="message-actions"><button className="text-button" type="button" onClick={() => { void navigator.clipboard?.writeText(answer.text); onToast('Answer copied.') }}>Copy</button><button className="icon-button" aria-label="Helpful answer" type="button" onClick={() => onFeedback('POSITIVE')}>♡</button><button className="icon-button" aria-label="Report answer" type="button" onClick={() => onFeedback('NEGATIVE')}>⚑</button>{answer.reason_codes?.length ? <span className="confidence-label">Reason: {answer.reason_codes.join(', ')}</span> : null}</div>
  </>
}

function ChatView({ messages, answer, busy, error, preview, onSubmitQuery, onNewChat, onPreview, onFeedback, onToast }: {
  messages: ConversationMessage[]
  answer: QueryAnswer | null
  busy: boolean
  error: string
  preview: string
  onSubmitQuery: (query: string) => void
  onNewChat: () => void
  onPreview: (citationId: string) => void
  onFeedback: (rating: 'POSITIVE' | 'NEGATIVE') => void
  onToast: (message: string) => void
}) {
  const [query, setQuery] = useState('')
  const [citationOpen, setCitationOpen] = useState(false)
  const latestAssistantId = [...messages].reverse().find((message) => message.role === 'assistant')?.message_id

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!query.trim() || busy) return
    onSubmitQuery(query.trim())
    setQuery('')
  }

  return <div className="chat-layout">
    <aside className="conversation-rail card" aria-label="Conversation history">
      <button className="button button-primary new-chat" type="button" onClick={onNewChat}><Icon>＋</Icon>New chat</button>
      <p className="eyebrow rail-label">Current conversation</p>
      <div className="conversation-item active">{messages.length ? `${messages.length} messages` : 'No messages yet'}</div>
      <div className="rail-footer"><StatusBadge>Backend chat API</StatusBadge><p className="helper-text">Conversation bodies are loaded only from the current authorized session.</p></div>
    </aside>
    <section className="chat-column" aria-labelledby="chat-title">
      <header className="page-heading chat-heading"><div><p className="eyebrow">Enterprise knowledge workspace</p><h1 id="chat-title">How can I help today?</h1><p className="muted">Answers and citations are returned by the backend RAG job.</p></div><StatusBadge>Chat API</StatusBadge></header>
      {error && <ErrorNotice message={error} />}
      <div className="chat-thread">
        {!messages.length && !busy && <div className="empty-state card message-empty"><div className="empty-icon"><Icon>✦</Icon></div><h1>Start a conversation</h1><p>Ask a question to create a backend conversation and durable RAG query job.</p></div>}
        {messages.map((message) => message.role === 'user'
          ? <article className="message user-message" key={message.message_id}><div className="avatar avatar-user">U</div><div className="message-body"><div className="message-meta"><strong>You</strong><span>{new Date(message.created_at).toLocaleString()}</span></div><p>{message.content}</p></div></article>
          : <article className="message assistant-message" key={message.message_id}><div className="avatar avatar-ai"><Icon>✦</Icon></div><div className="message-card"><div className="message-meta"><strong>{appConfig.name}</strong><StatusBadge tone={message.message_id === latestAssistantId && answer?.status === 'ANSWERED' ? 'success' : 'neutral'}>{message.message_id === latestAssistantId && answer ? answer.status : 'COMPLETED'}</StatusBadge><span>{new Date(message.created_at).toLocaleString()}</span></div><p>{message.content}</p>{message.message_id === latestAssistantId && answer && <AnswerDetails answer={answer} citationOpen={citationOpen} preview={preview} onToggleCitations={() => setCitationOpen((open) => !open)} onPreview={onPreview} onFeedback={onFeedback} onToast={onToast} />}</div></article>)}
        {busy && <div className="processing-row" role="status"><span className="pulse-dot" />Waiting for the backend RAG job…</div>}
      </div>
      <form className="prompt-box card" onSubmit={submit}><label className="sr-only" htmlFor="chat-query">Ask your enterprise knowledge question</label><textarea id="chat-query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ask a question about authorized enterprise knowledge…" disabled={busy} rows={2} /><div className="prompt-toolbar"><span className="helper-text">{busy ? 'Polling query job status…' : 'The backend enforces identity and source permissions.'}</span><button className="button button-primary send-button" type="submit" disabled={busy || !query.trim()} aria-label="Send question"><Icon>↑</Icon></button></div></form>
    </section>
  </div>
}

function metricValue(metric: Dashboard['users']): string {
  if (!metric?.available || metric.value === null || metric.value === undefined) return 'Unavailable'
  if (typeof metric.value !== 'object') return String(metric.value)
  const value = metric.value as Record<string, unknown>
  const candidate = value.total ?? value.requests ?? value.jobs
  return candidate === undefined ? JSON.stringify(metric.value) : String(candidate)
}

function DashboardView() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    setError('')
    try { setDashboard(await getDashboard()) } catch (reason) { setError(reason instanceof Error ? reason.message : 'Dashboard request failed.') } finally { setLoading(false) }
  }
  useEffect(() => { void load() }, [])

  const metrics = [['users', 'Users', 'users'], ['documents', 'Documents', 'documents'], ['usage', 'Queries', 'requests'], ['ingestion', 'Ingestion jobs', 'jobs'], ['latency', 'Latency', 'milliseconds'], ['cost', 'Model cost', 'USD'], ['evaluation', 'Evaluation', 'score'], ['cache_hit_rate', 'Cache hit rate', 'ratio']] as const
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">System intelligence</p><h1>Admin overview</h1><p className="muted">Snapshot metrics supplied by the administrative API.</p></div><button className="button button-secondary" type="button" onClick={() => void load()}>↻ Refresh</button></header>{error && <ErrorNotice message={error} />}{loading ? <div className="empty-state card"><h1>Loading dashboard…</h1></div> : <><div className="metrics-grid">{metrics.map(([key, label, unit]) => { const metric = dashboard?.[key as keyof Dashboard] as Dashboard['users']; return <div className="metric-card card" key={key}><div className="metric-top"><span>{label}</span><span className="metric-icon">▦</span></div><strong>{metricValue(metric)}</strong><small>{metric?.available ? `${metric.unit || unit} · ${metric.provenance}` : metric?.reason || 'No backend measurement'}</small></div> })}</div><div className="dashboard-grid"><section className="card empty-state"><h1>No time-series data</h1><p>The current dashboard contract exposes request snapshots only; chart data is unavailable.</p></section><section className="card info-card"><div className="info-card-title"><span>Operational source</span><Icon>◈</Icon></div><strong>{dashboard?.schema_version || 'v1'}</strong><p className="muted">Metrics are not estimated by the frontend.</p></section></div></>}</div>
}

function UsersView() {
  const [users, setUsers] = useState<UserRecord[]>([])
  const [departments, setDepartments] = useState<DepartmentRecord[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  useEffect(() => { Promise.all([getUsers(), getDepartments()]).then(([userResult, departmentResult]) => { setUsers(userResult.users); setDepartments(departmentResult.departments) }).catch((reason) => setError(reason instanceof Error ? reason.message : 'Identity request failed.')).finally(() => setLoading(false)) }, [])
  const departmentNames = useMemo(() => new Map(departments.map((department) => [department.department_id, department.name])), [departments])
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">Identity & access</p><h1>Users & departments</h1><p className="muted">Records below come directly from the backend identity store.</p></div></header>{error && <ErrorNotice message={error} />}{loading ? <div className="empty-state card"><h1>Loading identities…</h1></div> : <section className="card activity-card"><div className="section-heading"><div><h2>Enterprise identities</h2><p className="muted">No client-side accounts or role labels are fabricated.</p></div><StatusBadge tone="success">{`${users.length} returned`}</StatusBadge></div>{users.length ? <div className="table-wrap"><table><thead><tr><th>User</th><th>Roles</th><th>Departments</th><th>Status</th></tr></thead><tbody>{users.map((user) => <tr key={user.user_id}><td><strong>{user.email}</strong><span className="table-subtitle">{user.user_id}</span></td><td>{user.roles.map((role) => <span className="soft-chip" key={role}>{role}</span>)}</td><td>{user.department_ids.map((id) => departmentNames.get(id) || id).join(', ') || 'None returned'}</td><td><StatusBadge tone={user.active ? 'success' : 'danger'}>{user.active ? 'ACTIVE' : 'INACTIVE'}</StatusBadge></td></tr>)}</tbody></table></div> : <p className="muted">No users returned for this tenant.</p>}</section>}</div>
}

function DataViewEmpty({ message }: { message: string }) {
  return <div className="empty-state card"><div className="empty-icon"><Icon>⌁</Icon></div><h1>No records returned</h1><p>{message}</p></div>
}

function DocumentsView() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [total, setTotal] = useState(0)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    setError('')
    try {
      const result = await getDocuments()
      setDocuments(result.items)
      setTotal(result.pagination.total)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Document request failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [])

  return <div className="content-stack">
    <header className="page-heading"><div><p className="eyebrow">Authorized knowledge inventory</p><h1>Knowledge documents</h1><p className="muted">Documents are filtered by the backend access policy for the signed-in principal.</p></div><button className="button button-secondary" type="button" onClick={() => void load()}>↻ Refresh</button></header>
    {error && <ErrorNotice message={error} />}
    {loading ? <div className="empty-state card"><h1>Loading documents…</h1></div> : documents.length ? <section className="card activity-card"><div className="section-heading"><div><h2>Returned documents</h2><p className="muted">Showing {documents.length} of {total} records from GET /api/v1/documents.</p></div><StatusBadge tone="success">{`${documents.length} returned`}</StatusBadge></div><div className="table-wrap"><table><thead><tr><th>Document</th><th>Classification</th><th>Status</th><th>Department</th><th>Current version</th></tr></thead><tbody>{documents.map((document) => <tr key={document.document_id}><td><strong>{document.title}</strong><span className="table-subtitle">{document.document_id}</span></td><td><span className="soft-chip">{document.classification}</span></td><td><StatusBadge tone={document.status === 'ACTIVE' ? 'success' : 'neutral'}>{document.status}</StatusBadge></td><td>{document.owner_department_id || 'Not returned'}</td><td>{document.current_version_id || 'Not published'}</td></tr>)}</tbody></table></div></section> : <DataViewEmpty message="The backend returned no documents for this principal." />}
  </div>
}

function ApprovalsView() {
  const [approvals, setApprovals] = useState<ApprovalRecord[]>([])
  const [total, setTotal] = useState(0)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    setError('')
    try {
      const result = await getApprovals()
      setApprovals(result.items)
      setTotal(result.pagination.total)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Approval request failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [])

  return <div className="content-stack">
    <header className="page-heading"><div><p className="eyebrow">Ingestion governance</p><h1>Review & ingest</h1><p className="muted">Version approval records supplied by the backend management API.</p></div><button className="button button-secondary" type="button" onClick={() => void load()}>↻ Refresh</button></header>
    {error && <ErrorNotice message={error} />}
    {loading ? <div className="empty-state card"><h1>Loading approval queue…</h1></div> : approvals.length ? <section className="card activity-card"><div className="section-heading"><div><h2>Approval queue</h2><p className="muted">Showing {approvals.length} of {total} records from GET /api/v1/approvals.</p></div><StatusBadge tone="warning">{`${approvals.length} returned`}</StatusBadge></div><div className="table-wrap"><table><thead><tr><th>Document / version</th><th>Status</th><th>Ingestion job</th><th>Approvals</th></tr></thead><tbody>{approvals.map((record) => <tr key={record.version_id}><td><strong>{record.document_id}</strong><span className="table-subtitle">{record.version_id} · v{record.version_number}</span></td><td><StatusBadge tone={record.status === 'APPROVED' ? 'success' : 'warning'}>{record.status}</StatusBadge></td><td><span className="table-subtitle">{record.job_id}</span></td><td>{record.approvals.length ? record.approvals.map((approval) => <div className="table-subtitle" key={`${record.version_id}-${approval.stage}`}>Stage {approval.stage}: {approval.decision} · {approval.reviewer_id}</div>) : 'No approval decision returned'}</td></tr>)}</tbody></table></div></section> : <DataViewEmpty message="The backend returned no versions awaiting or carrying approval decisions." />}
  </div>
}

function AuditView() {
  const [events, setEvents] = useState<AuditRecord[]>([])
  const [total, setTotal] = useState(0)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    setError('')
    try {
      const result = await getAuditEvents()
      setEvents(result.items)
      setTotal(result.pagination.total)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Audit request failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [])

  return <div className="content-stack">
    <header className="page-heading"><div><p className="eyebrow">Traceable administration</p><h1>Audit & monitoring</h1><p className="muted">Security and administrative events returned by the backend audit API.</p></div><button className="button button-secondary" type="button" onClick={() => void load()}>↻ Refresh</button></header>
    {error && <ErrorNotice message={error} />}
    {loading ? <div className="empty-state card"><h1>Loading audit events…</h1></div> : events.length ? <section className="card activity-card"><div className="section-heading"><div><h2>Audit events</h2><p className="muted">Showing {events.length} of {total} records from GET /api/v1/audit.</p></div><StatusBadge tone="neutral">{`${events.length} returned`}</StatusBadge></div><div className="table-wrap"><table><thead><tr><th>Time</th><th>Event / action</th><th>Outcome</th><th>Principal</th><th>Code / metadata</th></tr></thead><tbody>{events.map((event) => <tr key={event.event_id}><td><span className="table-subtitle">{new Date(event.occurred_at).toLocaleString()}</span><span className="table-subtitle">{event.event_id}</span></td><td><strong>{event.event}</strong><span className="table-subtitle">{event.action}</span></td><td><StatusBadge tone={event.outcome === 'SUCCESS' || event.decision === 'ALLOW' ? 'success' : event.decision === 'DENY' ? 'danger' : 'neutral'}>{`${event.outcome}${event.decision ? ` · ${event.decision}` : ''}`}</StatusBadge></td><td>{event.principal_id || 'System / unavailable'}</td><td><span className="table-subtitle">{event.code || 'No code returned'}</span><span className="table-subtitle">{JSON.stringify(event.safe_metadata)}</span></td></tr>)}</tbody></table></div></section> : <DataViewEmpty message="The backend returned no audit events for this principal." />}
  </div>
}

export function App() {
  const [principal, setPrincipal] = useState<Principal | null>(null)
  const [identityChecked, setIdentityChecked] = useState(false)
  const [view, setView] = useState<View>('chat')
  const [authOpen, setAuthOpen] = useState(false)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [toast, setToast] = useState('')
  const [conversationId, setConversationId] = useState<string>()
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [answer, setAnswer] = useState<QueryAnswer | null>(null)
  const [queryBusy, setQueryBusy] = useState(false)
  const [queryError, setQueryError] = useState('')
  const [preview, setPreview] = useState('')

  useEffect(() => {
    if (!getAccessToken()) { setIdentityChecked(true); return }
    getCurrentIdentity().then(setPrincipal).catch(() => { setPrincipal(null) }).finally(() => setIdentityChecked(true))
  }, [])

  function notify(message: string) {
    setToast(message)
    window.setTimeout(() => setToast(''), 3200)
  }

  function navigate(nextView: View) {
    const item = navItems.find((nav) => nav.id === nextView)
    if (item?.admin && !canAdmin(principal)) { notify('This area is restricted by the backend policy.'); return }
    if (item?.manager && !canManage(principal)) { notify('This area is restricted by the backend policy.'); return }
    setAuthOpen(false)
    setView(nextView)
    setMobileNavOpen(false)
  }

  async function refreshConversation(id: string) {
    const conversation = await getConversation(id)
    setMessages(conversation.messages)
  }

  async function newChat() {
    try {
      const conversation = await createConversation()
      setConversationId(conversation.conversation_id)
      setMessages([])
      setAnswer(null)
      setPreview('')
      setQueryError('')
      notify('New backend conversation created.')
    } catch (reason) { notify(reason instanceof Error ? reason.message : 'Conversation could not be created.') }
  }

  async function submitLiveQuery(query: string) {
    setQueryBusy(true)
    setQueryError('')
    try {
      const activeConversation = conversationId ?? (await createConversation()).conversation_id
      setConversationId(activeConversation)
      const job = await submitMessage(activeConversation, query)
      const completed = await waitForQueryCompletion(job.job_id)
      setAnswer(completed.answer ?? null)
      await refreshConversation(activeConversation)
      notify('Answer received from the backend RAG job.')
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : 'The RAG query could not be completed.'
      setQueryError(message)
      notify(message)
    } finally { setQueryBusy(false) }
  }

  async function handlePreview(citationId: string) {
    if (!answer?.answer_id) { notify('The backend did not return an answer identifier for preview.'); return }
    try { const result = await previewCitation(answer.answer_id, citationId); setPreview(result.preview || 'The backend returned no preview content.') } catch (reason) { notify(reason instanceof Error ? reason.message : 'Citation preview unavailable.') }
  }

  async function handleFeedback(rating: 'POSITIVE' | 'NEGATIVE') {
    if (!answer?.answer_id) { notify('Feedback is unavailable until the backend returns an answer identifier.'); return }
    try { await submitFeedback(answer.answer_id, rating); notify('Feedback recorded by the backend.') } catch (reason) { notify(reason instanceof Error ? reason.message : 'Feedback could not be recorded.') }
  }

  async function handleSignOut() {
    await signOut()
    setPrincipal(null)
    setView('chat')
    setConversationId(undefined)
    setMessages([])
    setAnswer(null)
    notify('Signed out.')
  }

  if (!identityChecked) return <div className="app-shell"><main className="main-content"><div className="empty-state card"><h1>Loading identity…</h1></div></main></div>
  const manager = canManage(principal)
  const admin = canAdmin(principal)
  const roleLabel = principal?.roles.join(', ') || 'Public session'
  const currentNav = navItems.find((item) => item.id === view)
  const renderedView = authOpen
    ? <AuthView onAuthenticated={(next) => { setPrincipal(next); setAuthOpen(false) }} onCancel={() => setAuthOpen(false)} onToast={notify} />
    : view === 'chat' ? <ChatView messages={messages} answer={answer} busy={queryBusy} error={queryError} preview={preview} onSubmitQuery={submitLiveQuery} onNewChat={newChat} onPreview={handlePreview} onFeedback={handleFeedback} onToast={notify} />
      : view === 'dashboard' && manager ? <DashboardView />
        : view === 'users' && admin ? <UsersView />
          : view === 'documents' && principal ? <DocumentsView />
            : view === 'approvals' && manager ? <ApprovalsView />
              : view === 'audit' && manager ? <AuditView />
                : <UnavailableView title="This workspace is unavailable" endpoint="backend authorization" />

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNavOpen ? 'sidebar-open' : ''}`}><div><div className="brand"><div className="brand-mark"><Icon>✦</Icon></div><div><strong>Enterprise AI</strong><span>Knowledge workspace</span></div></div><button className="button button-primary new-chat sidebar-new-chat" type="button" onClick={() => navigate('chat')}><Icon>＋</Icon>New chat</button><div className="nav-section"><p className="eyebrow">Workspace</p><nav aria-label="Main navigation">{navItems.filter((item) => item.id !== 'documents' || Boolean(principal)).filter((item) => !item.manager || manager).filter((item) => !item.admin || admin).map((item) => <button className={`nav-item ${view === item.id && !authOpen ? 'nav-item-active' : ''}`} key={item.id} type="button" onClick={() => navigate(item.id)}><Icon>{item.icon}</Icon><span>{item.label}</span></button>)}</nav></div></div><div className="sidebar-bottom"><div className="role-summary"><div className="avatar avatar-user">{principal ? 'ID' : 'PU'}</div><div><strong>{roleLabel}</strong><span>{principal ? principal.tenant_id : 'Public session'}</span></div></div>{principal ? <button className="text-button" type="button" onClick={() => void handleSignOut()}>Sign out</button> : <button className="text-button" type="button" onClick={() => setAuthOpen(true)}>Sign in</button>}</div></aside>
    {mobileNavOpen && <button className="mobile-scrim" aria-label="Close navigation" type="button" onClick={() => setMobileNavOpen(false)} />}
    <div className="main-shell"><header className="topbar"><div className="topbar-left"><button className="mobile-menu" aria-label="Open navigation" type="button" onClick={() => setMobileNavOpen(true)}>☰</button><div className="breadcrumbs"><strong>{view === 'chat' ? 'Enterprise Knowledge AI' : 'Enterprise Admin Portal'}</strong><span>›</span><span>{authOpen ? 'Sign in' : currentNav?.label}</span></div><StatusBadge>API boundary</StatusBadge></div><div className="topbar-actions">{principal ? <div className="topbar-profile"><div><strong>{roleLabel}</strong><span>{principal.tenant_id}</span></div><div className="avatar avatar-primary">ID</div></div> : <button className="button button-secondary" type="button" onClick={() => setAuthOpen(true)}>Sign in</button>}</div></header><main className="main-content">{renderedView}</main></div>
    {toast && <div className="toast" role="status">{toast}</div>}
  </div>
}
