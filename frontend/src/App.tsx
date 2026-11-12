import { FormEvent, ReactNode, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  AccessGrant,
  AccessRequestMetadata,
  ApiError,
  ApprovalRecord,
  ConversationMessage,
  createDepartment,
  createConversation,
  createUser,
  ConversationSummary,
  Dashboard,
  DepartmentRecord,
  DocumentRecord,
  DocumentVersion,
  downloadCitation,
  getApprovals,
  getAuditEvents,
  getAccessRequests,
  getCurrentIdentity,
  getConversation,
  getConversations,
  getDashboard,
  getDepartments,
  getDocumentVersions,
  getDocuments,
  getFeedback,
  getIngestionJob,
  getAccessToken,
  getUsers,
  IngestionJob,
  previewCitation,
  Principal,
  publishDocumentVersion,
  QueryAnswer,
  QueryCitation,
  reviewDocumentVersion,
  reviewAccessRequest,
  revokeDocumentVersion,
  signIn,
  signOut,
  streamMessage,
  submitFeedback,
  submitAccessRequest,
  updateDocumentAccess,
  updateUser,
  activateUser,
  uploadMetadataDocument,
  UserRecord,
} from './api/client'
import { appConfig } from './config'
import './styles.css'

type View = 'chat' | 'dashboard' | 'documents' | 'approvals' | 'users' | 'audit'
type RetryMode = 'conversation' | 'query' | 'restore' | null
type AuthMode = 'sign-in' | 'onboarding' | null
type DownloadState = { status: 'idle' | 'loading' | 'error'; message?: string }
const CONVERSATION_STORAGE_KEY = 'enterprise-rag.conversation-id'

function describeRequestError(reason: unknown, fallback: string): string {
  if (reason instanceof ApiError && (reason.status === 401 || reason.status === 403 || reason.code?.includes('SESSION'))) {
    return 'Your session is no longer valid. Retry once, or reconnect and sign in again.'
  }
  return reason instanceof Error ? reason.message : fallback
}

function isConversationGone(reason: unknown): boolean {
  return reason instanceof ApiError && (reason.status === 404 || reason.status === 410 || reason.code === 'CONVERSATION_NOT_FOUND')
}

const navItems: Array<{ id: View; label: string; icon: string; manager?: boolean; admin?: boolean }> = [
  { id: 'chat', label: 'Knowledge chat', icon: '✦' },
  { id: 'dashboard', label: 'Overview', icon: '▦', manager: true },
  { id: 'documents', label: 'Knowledge documents', icon: '▤', manager: true },
  { id: 'approvals', label: 'Review & ingest', icon: '✓', manager: true },
  { id: 'users', label: 'Users & access', icon: '♙', manager: true },
  { id: 'audit', label: 'Audit & monitoring', icon: '◷', manager: true },
]

function hasRole(principal: Principal | null, role: string): boolean { return principal?.roles.includes(role) ?? false }
function canManage(principal: Principal | null): boolean { return hasRole(principal, 'system_admin') || hasRole(principal, 'website_manager') }
function canAdmin(principal: Principal | null): boolean { return hasRole(principal, 'system_admin') }

function Icon({ children }: { children: string }) { return <span className="icon" aria-hidden="true">{children}</span> }

function StatusBadge({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'success' | 'warning' | 'danger' }) {
  return <span className={`status-badge status-${tone}`}><span className="status-dot" aria-hidden="true" />{children}</span>
}

function ErrorNotice({ message, onRetry, onReconnect }: { message: string; onRetry?: () => void; onReconnect?: () => void }) {
  return <div className="notice notice-warning" role="alert"><Icon>!</Icon><div><strong>Backend request unavailable</strong><span>{message}</span>{(onRetry || onReconnect) && <div className="notice-actions">{onRetry && <button className="button button-secondary" type="button" onClick={onRetry}>Retry</button>}{onReconnect && <button className="button button-secondary" type="button" onClick={onReconnect}>Reconnect</button>}</div>}</div></div>
}

function describeSignInError(reason: unknown): string {
  if (reason instanceof ApiError) {
    switch (reason.code) {
      case 'MFA_REQUIRED': return 'Additional verification is required for this account. Enter your MFA code to continue.'
      case 'AUTH_INVALID': return 'Email or password is incorrect.'
      case 'ACCOUNT_INACTIVE':
      case 'AUTH_INACTIVE':
      case 'USER_INACTIVE': return 'This account is inactive. Ask an administrator to activate it.'
      case 'AUTH_REQUIRED':
      case 'SESSION_EXPIRED':
      case 'SESSION_REVOKED': return 'Your session has expired. Sign in again to continue.'
      case 'RATE_LIMITED': return 'Too many sign-in attempts. Try again after the cooldown.'
      case 'AUTH_UNAVAILABLE': return 'Authentication is temporarily unavailable. Retry in a moment.'
    }
    if (reason.status === 503 || reason.code === 'NETWORK_UNAVAILABLE' || reason.code === 'REQUEST_TIMEOUT') return 'Authentication is temporarily unavailable. Retry in a moment.'
  }
  return reason instanceof Error ? reason.message : 'Sign-in failed.'
}

function UnavailableView({ title, endpoint }: { title: string; endpoint: string }) {
  return <section className="empty-state card" aria-labelledby="unavailable-title"><div className="empty-icon"><Icon>⌁</Icon></div><p className="eyebrow">Backend contract boundary</p><h1 id="unavailable-title">{title}</h1><p>This screen does not invent data. The current backend has no endpoint for this capability yet.</p><p className="helper-text">Missing endpoint: {endpoint}</p></section>
}

function OnboardingView({ onModeChange, onCancel, onToast }: { onModeChange: (mode: 'sign-in' | 'onboarding') => void; onCancel: () => void; onToast: (message: string) => void }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [department, setDepartment] = useState('')
  const [reason, setReason] = useState('')
  const [consent, setConsent] = useState(false)
  const [busy, setBusy] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      const result = await submitAccessRequest({ full_name: name, email, department, reason, consent })
      setSubmitted(true)
      onToast(`Access request recorded: ${result.request_id}`)
    } catch (reasonError) {
      setError(describeRequestError(reasonError, 'Access request could not be submitted.'))
    } finally { setBusy(false) }
  }

  return <section className="auth-layout" aria-labelledby="onboarding-title">
    <div className="auth-story"><div className="auth-story-mark"><Icon>✦</Icon></div><p className="eyebrow">Enterprise knowledge workspace</p><h1>Request access with a clear review path.</h1><p>Your request is recorded for administrator review. Submission never grants permissions in the browser.</p><div className="auth-proof"><span>01</span><div><strong>Explicit approval</strong><small>Administrators decide the tenant, department and document access.</small></div></div><div className="auth-proof"><span>02</span><div><strong>Honest status</strong><small>Email confirmation remains unavailable until a provider is configured.</small></div></div></div>
    <div className="auth-card card"><div className="auth-switch"><button type="button" onClick={() => onModeChange('sign-in')}>Sign in</button><button className="active" type="button" onClick={() => onModeChange('onboarding')}>Request access</button></div>
      <p className="eyebrow">Employee onboarding</p><h2 id="onboarding-title">Request access securely</h2><p className="muted">Complete the form and your administrator can review it. No account is created automatically.</p>{error && <ErrorNotice message={error} />}{submitted && <div className="notice notice-success" role="status"><Icon>✓</Icon><div><strong>Request recorded</strong><span>Your administrator can review it. Email confirmation is not configured in this environment.</span></div></div>}
      <div className="notice notice-warning scope-notice" role="note"><Icon>◈</Icon><div><strong>Tenant routing is administrator-controlled</strong><span>Your browser cannot choose an enterprise or grant itself access. This request is routed for review.</span></div></div>
      <form className="auth-form" onSubmit={submit}><label>Full name<input value={name} onChange={(event) => setName(event.target.value)} required autoComplete="name" /></label><label>Work email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" /></label><label>Department or requested area<input value={department} onChange={(event) => setDepartment(event.target.value)} required /></label><label>Why do you need access?<textarea value={reason} onChange={(event) => setReason(event.target.value)} required rows={3} /></label><label className="checkbox-label"><input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} required /> I understand access requires administrator approval.</label><button className="button button-primary auth-submit" type="submit" disabled={busy || submitted || !consent}>{busy ? 'Submitting…' : submitted ? 'Request recorded' : 'Submit request'}</button></form>
      <p className="helper-text auth-footnote">Invitation activation and email confirmation are not configured yet; approval remains an administrator action.</p><button className="text-button auth-cancel" type="button" onClick={onCancel}>Return to chat</button>
    </div>
  </section>
}

function AuthView({ mode, onModeChange, onAuthenticated, onCancel, onToast }: { mode: 'sign-in' | 'onboarding'; onModeChange: (mode: 'sign-in' | 'onboarding') => void; onAuthenticated: (principal: Principal) => void; onCancel: () => void; onToast: (message: string) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [name, setName] = useState('')
  const [department, setDepartment] = useState('')
  const [reason, setReason] = useState('')
  const [consent, setConsent] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [mfaRequired, setMfaRequired] = useState(false)

  function switchMode(nextMode: 'sign-in' | 'onboarding') {
    setError('')
    setBusy(false)
    setMfaRequired(false)
    onModeChange(nextMode)
  }

  async function submitSignIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError('')
    try { const principal = await signIn(email, password, mfaCode || undefined); onAuthenticated(principal); onToast('Signed in through the backend identity API.') }
    catch (reasonError) { if (reasonError instanceof ApiError && reasonError.code === 'MFA_REQUIRED') setMfaRequired(true); setError(describeSignInError(reasonError)) }
    finally { setBusy(false) }
  }

  if (mode === 'onboarding') return <OnboardingView onModeChange={onModeChange} onCancel={onCancel} onToast={onToast} />

  return <section className="auth-layout" aria-labelledby={mode === 'sign-in' ? 'sign-in-title' : 'onboarding-title'}>
    <div className="auth-story"><div className="auth-story-mark"><Icon>✦</Icon></div><p className="eyebrow">Enterprise knowledge workspace</p><h1>Answers with a clear source boundary.</h1><p>Ask the company knowledge base, understand where each answer came from and keep every permission decision on the server.</p><div className="auth-proof"><span>01</span><div><strong>Authorized by design</strong><small>RAG answers use only sources available to the current session.</small></div></div><div className="auth-proof"><span>02</span><div><strong>Ready for operations</strong><small>Review, access and audit surfaces stay connected to backend state.</small></div></div></div>
    <div className="auth-card card"><div className="auth-switch"><button className="active" type="button" onClick={() => switchMode('sign-in')}>Sign in</button><button type="button" onClick={() => switchMode('onboarding')}>Request access</button></div>
      {mode === 'sign-in' ? <><p className="eyebrow">Backend identity</p><h2 id="sign-in-title">Sign in to your workspace</h2><p className="muted">Your role, tenant and departments come from the identity API. No client-side role preview is used.</p>{error && <ErrorNotice message={error} />}{mfaRequired && <div className="notice notice-warning" role="status"><Icon>!</Icon><div><strong>Additional verification required</strong><span>The backend requires MFA before issuing a session.</span></div></div>}<form className="auth-form" onSubmit={submitSignIn}><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="username" /></label><label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" /></label>{mfaRequired && <label>MFA code<input value={mfaCode} onChange={(event) => setMfaCode(event.target.value)} autoComplete="one-time-code" required /></label>}<button className="button button-primary auth-submit" type="submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button></form><button className="button button-secondary oauth-button" type="button" disabled>Continue with Google <span>Not connected</span></button><p className="helper-text auth-footnote">Google OAuth is unavailable until a real backend callback and verified principal exist.</p></> : <><p className="eyebrow">Employee onboarding</p><h2 id="onboarding-title">Request access securely</h2><p className="muted">This form is ready for the approved access-request API. It will not create an account in the browser.</p><form className="auth-form"><label>Full name<input value={name} onChange={(event) => setName(event.target.value)} required autoComplete="name" /></label><label>Work email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" /></label><label>Department or requested area<input value={department} onChange={(event) => setDepartment(event.target.value)} required /></label><label>Why do you need access?<textarea value={reason} onChange={(event) => setReason(event.target.value)} required rows={3} /></label><label className="checkbox-label"><input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} required /> I understand access requires administrator approval.</label><div className="notice notice-warning onboarding-unavailable" role="status"><Icon>!</Icon><div><strong>Access requests are not connected yet</strong><span>Contact your administrator; no request is sent from this screen.</span></div></div><button className="button button-primary auth-submit" type="submit" disabled>Submit request <span>Unavailable</span></button></form><p className="helper-text auth-footnote">Invitation activation and email confirmation are also unavailable until the backend supplies signed endpoints.</p></>}
      <button className="text-button auth-cancel" type="button" onClick={onCancel}>Return to chat</button>
    </div>
  </section>
}

function formatLocation(citation: QueryCitation): string {
  const locator = citation.locator
  if (!locator) return 'Verified source reference'
  if (locator.page !== undefined) return `Page ${locator.page}`
  if (locator.heading) return `${locator.heading}${locator.paragraph ? ` · paragraph ${locator.paragraph}` : ''}`
  if (locator.sheet) return `${locator.sheet}${locator.cell_range ? ` · ${locator.cell_range}` : ''}`
  return 'Verified source reference'
}
function citationTitle(citation: QueryCitation): string { return citation.title || citation.document_title || citation.document_name || citation.filename || `Source ${citation.document_id.slice(0, 8)}` }
function citationFilename(citation: QueryCitation): string { return citation.filename || citation.document_name || citation.document_id }
function citationKind(citation: QueryCitation): string { return citation.locator?.kind?.toUpperCase() || citation.filename?.split('.').pop()?.toUpperCase() || 'SRC' }

function renderInlineMarkdown(value: string, keyPrefix: string): ReactNode[] {
  return value.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g).filter(Boolean).map((part, index) => {
    const key = `${keyPrefix}-${index}`
    if (part.startsWith('`') && part.endsWith('`')) return <code key={key}>{part.slice(1, -1)}</code>
    if (part.startsWith('**') && part.endsWith('**')) return <strong key={key}>{part.slice(2, -2)}</strong>
    if (part.startsWith('*') && part.endsWith('*')) return <em key={key}>{part.slice(1, -1)}</em>
    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/)
    if (link) {
      const href = link[2]
      if (/^(https?:\/\/|mailto:)/i.test(href)) return <a key={key} href={href} target="_blank" rel="noreferrer">{link[1]}</a>
      return <span key={key}>{link[1]}</span>
    }
    return <span key={key}>{part}</span>
  })
}

// eslint-disable-next-line react-refresh/only-export-components
export function renderSafeMarkdown(markdown: string): ReactNode[] {
  const lines = markdown.split(/\r?\n/)
  const blocks: ReactNode[] = []
  let index = 0
  while (index < lines.length) {
    const line = lines[index]
    if (!line.trim()) { index += 1; continue }
    if (line.trim().startsWith('```')) {
      const code: string[] = []
      index += 1
      while (index < lines.length && !lines[index].trim().startsWith('```')) { code.push(lines[index]); index += 1 }
      if (index < lines.length) index += 1
      blocks.push(<pre key={`code-${index}`}><code>{code.join('\n')}</code></pre>)
      continue
    }
    const heading = line.match(/^(#{1,3})\s+(.+)$/)
    if (heading) {
      const Heading = `h${heading[1].length}` as 'h1' | 'h2' | 'h3'
      blocks.push(<Heading key={`heading-${index}`}>{renderInlineMarkdown(heading[2], `heading-${index}`)}</Heading>)
      index += 1
      continue
    }
    const unordered = line.match(/^\s*[-*]\s+(.+)$/)
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/)
    if (unordered || ordered) {
      const items: ReactNode[] = []
      const orderedList = Boolean(ordered)
      while (index < lines.length) {
        const match = lines[index].match(orderedList ? /^\s*\d+[.)]\s+(.+)$/ : /^\s*[-*]\s+(.+)$/)
        if (!match) break
        items.push(<li key={`item-${index}`}>{renderInlineMarkdown(match[1], `item-${index}`)}</li>)
        index += 1
      }
      blocks.push(orderedList ? <ol key={`list-${index}`}>{items}</ol> : <ul key={`list-${index}`}>{items}</ul>)
      continue
    }
    const paragraph: string[] = [line]
    index += 1
    while (index < lines.length && lines[index].trim() && !/^#{1,3}\s+/.test(lines[index]) && !/^\s*[-*]\s+/.test(lines[index]) && !/^\s*\d+[.)]\s+/.test(lines[index]) && !lines[index].trim().startsWith('```')) {
      paragraph.push(lines[index]); index += 1
    }
    blocks.push(<p key={`paragraph-${index}`}>{renderInlineMarkdown(paragraph.join(' '), `paragraph-${index}`)}</p>)
  }
  return blocks
}

function AnswerDetailsBody({ answer, citationOpen, preview, downloadStates, onToggleCitations, onPreview, onDownload, onFeedback, onToast }: { answer: QueryAnswer; citationOpen: boolean; preview: string; downloadStates: Record<string, DownloadState>; onToggleCitations: () => void; onPreview: (citationId: string) => void; onDownload: (citation: QueryCitation) => void; onFeedback: (rating: 'POSITIVE' | 'NEGATIVE') => void; onToast: (message: string) => void }) {
  return <><div className="citation-block"><button className="citation-toggle" type="button" aria-expanded={citationOpen} onClick={onToggleCitations}><span><Icon>⌕</Icon> {citationOpen ? 'Hide citations' : `View ${answer.citations.length} citation${answer.citations.length === 1 ? '' : 's'}`}</span><span>{citationOpen ? '⌃' : '⌄'}</span></button>{citationOpen && <div className="citation-list">{answer.citations.length ? answer.citations.map((citation) => { const state = downloadStates[citation.citation_id] || { status: 'idle' as const }; const downloadable = Boolean(answer.answer_id && citation.citation_id); return <div className="citation-row" key={citation.citation_id}><div className={`file-icon file-${citationKind(citation).toLowerCase()}`}>{citationKind(citation)}</div><div className="citation-text"><strong>{citationTitle(citation)}</strong><span>{citationFilename(citation)} · {formatLocation(citation)}</span></div><div className="citation-actions"><button className="text-button" type="button" onClick={() => onPreview(citation.citation_id)}>Preview</button><button className="text-button" type="button" disabled={!downloadable || state.status === 'loading'} title={!downloadable ? 'Download unavailable until the backend returns answer and citation identifiers.' : undefined} onClick={() => onDownload(citation)}>{state.status === 'loading' ? 'Preparing file…' : state.status === 'error' ? 'Retry download' : downloadable ? 'Download original' : 'Download unavailable'}</button>{state.message && <span className="citation-unavailable" role="status">{state.message}</span>}</div></div> }) : <p className="helper-text">The backend returned no citations.</p>}</div>}</div>{preview && <div className="detail-section highlighted"><div className="detail-label">Authorized preview</div><p>{preview}</p></div>}<div className="message-actions"><button className="text-button" type="button" onClick={() => { void navigator.clipboard?.writeText(answer.text); onToast('Answer copied.') }}>Copy</button><button className="icon-button" aria-label="Helpful answer" type="button" onClick={() => onFeedback('POSITIVE')}>♡</button><button className="icon-button" aria-label="Report answer" type="button" onClick={() => onFeedback('NEGATIVE')}>⚑</button>{answer.reason_codes?.length ? <span className="confidence-label">Reason: {answer.reason_codes.join(', ')}</span> : null}</div></>
}

type AnswerDetailsProps = Parameters<typeof AnswerDetailsBody>[0]

function AnswerDetails(props: AnswerDetailsProps) {
  const [feedback, setFeedback] = useState<'POSITIVE' | 'NEGATIVE' | null>(null)
  function handleFeedback(rating: 'POSITIVE' | 'NEGATIVE') {
    if (feedback) { props.onToast(`Feedback already selected: ${feedback === 'POSITIVE' ? 'helpful' : 'reported'}.`); return }
    setFeedback(rating)
    props.onFeedback(rating)
    props.onToast(rating === 'POSITIVE' ? 'Helpful feedback selected.' : 'Report feedback selected.')
  }
  return <AnswerDetailsBody {...props} onFeedback={handleFeedback} />
}

type ChatViewProps = { messages: ConversationMessage[]; answer: QueryAnswer | null; busy: boolean; cancelled: boolean; error: string; preview: string; downloadStates: Record<string, DownloadState>; conversationId?: string; conversationBusy: boolean; conversations: ConversationSummary[]; conversationListBusy: boolean; conversationListError: string; conversationHasMore: boolean; conversationSearch: string; retryAvailable: boolean; onSubmitQuery: (query: string) => void; onNewChat: () => void; onStopQuery: () => void; onRetry: () => void; onReconnect: () => void; onPreview: (citationId: string) => void; onDownload: (citation: QueryCitation) => void; onFeedback: (rating: 'POSITIVE' | 'NEGATIVE') => void; onToast: (message: string) => void; onSearchConversations: (search: string) => void; onLoadMoreConversations: () => void; onSelectConversation: (conversationId: string) => void }

function ChatBody({ messages, answer, busy, cancelled, error, preview, downloadStates, conversationBusy, retryAvailable, onSubmitQuery, onNewChat, onStopQuery, onRetry, onReconnect, onPreview, onDownload, onFeedback, onToast }: { messages: ConversationMessage[]; answer: QueryAnswer | null; busy: boolean; cancelled: boolean; error: string; preview: string; downloadStates: Record<string, DownloadState>; conversationId?: string; conversationBusy: boolean; retryAvailable: boolean; onSubmitQuery: (query: string) => void; onNewChat: () => void; onStopQuery: () => void; onRetry: () => void; onReconnect: () => void; onPreview: (citationId: string) => void; onDownload: (citation: QueryCitation) => void; onFeedback: (rating: 'POSITIVE' | 'NEGATIVE') => void; onToast: (message: string) => void }) {
  const [query, setQuery] = useState('')
  const [citationOpen, setCitationOpen] = useState(false)
  const latestAssistantId = [...messages].reverse().find((message) => message.role === 'assistant')?.message_id
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!query.trim() || busy) return; onSubmitQuery(query.trim()); setQuery('') }
  return <div className="chat-layout"><section className="chat-column" aria-labelledby="chat-title"><header className="page-heading chat-heading"><div><p className="eyebrow">Enterprise knowledge workspace</p><h1 id="chat-title">How can I help today?</h1><p className="muted">Ask in natural language. The backend streams an answer from sources your session is allowed to access.</p></div><div className="chat-heading-actions"><StatusBadge tone={busy ? 'warning' : cancelled ? 'warning' : 'neutral'}>{busy ? 'STREAMING' : cancelled ? 'CANCELLED' : 'READY'}</StatusBadge><button className="button button-primary" type="button" onClick={onNewChat} disabled={busy || conversationBusy}><Icon>＋</Icon>{conversationBusy ? 'Creating…' : 'New chat'}</button></div></header>{error && <ErrorNotice message={error} onRetry={retryAvailable ? onRetry : undefined} onReconnect={onReconnect} />}{cancelled && !error && <div className="notice notice-warning" role="status"><Icon>■</Icon><div><strong>Generation cancelled</strong><span>No more tokens will be added. You can retry the last question.</span><div className="notice-actions"><button className="button button-secondary" type="button" onClick={onRetry} disabled={!retryAvailable}>Retry</button></div></div></div>}<div className="chat-thread">{!messages.length && !busy && <div className="empty-state card message-empty"><div className="empty-icon"><Icon>✦</Icon></div><p className="eyebrow">Public knowledge only</p><h1>Start a conversation</h1><p>Ask a question to create a backend conversation and durable RAG query job. Try one of these:</p><div className="prompt-suggestions"><button type="button" onClick={() => setQuery('Summarize the purchasing policy')}>Summarize the purchasing policy</button><button type="button" onClick={() => setQuery('What requires finance approval?')}>What requires finance approval?</button></div></div>}{messages.map((message) => message.role === 'user' ? <article className="message user-message" key={message.message_id}><div className="avatar avatar-user">U</div><div className="message-body"><div className="message-meta"><strong>You</strong><span>{new Date(message.created_at).toLocaleString()}</span></div><p>{message.content}</p></div></article> : <article className="message assistant-message" key={message.message_id}><div className="avatar avatar-ai"><Icon>✦</Icon></div><div className="message-card"><div className="message-meta"><strong>{appConfig.name}</strong><StatusBadge tone={message.message_id === latestAssistantId && answer?.status === 'ANSWERED' ? 'success' : message.message_id === latestAssistantId && busy ? 'warning' : 'neutral'}>{message.message_id === latestAssistantId && answer ? answer.status : 'COMPLETED'}</StatusBadge><span>{new Date(message.created_at).toLocaleString()}</span></div><div className={`answer-markdown ${busy && message.message_id === latestAssistantId && !message.content ? 'streaming-placeholder' : ''}`}>{message.content ? renderSafeMarkdown(message.content) : (busy && message.message_id === latestAssistantId ? 'Thinking…' : 'No answer returned.')}</div>{message.message_id === latestAssistantId && answer && <AnswerDetails answer={answer} citationOpen={citationOpen} preview={preview} downloadStates={downloadStates} onToggleCitations={() => setCitationOpen((open) => !open)} onPreview={onPreview} onDownload={onDownload} onFeedback={onFeedback} onToast={onToast} />}</div></article>)}{busy && <div className="processing-row" role="status" aria-live="polite"><span className="pulse-dot" />Generating an answer from authorized sources… <button className="text-button" type="button" onClick={onStopQuery}>Stop generation</button></div>}</div><form className="prompt-box card" onSubmit={submit}><label className="sr-only" htmlFor="chat-query">Ask your enterprise knowledge question</label><textarea id="chat-query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Message Enterprise AI…" disabled={busy} rows={2} /><div className="prompt-toolbar"><span className="helper-text">{busy ? 'Streaming from the backend…' : 'The backend enforces identity and source permissions.'}</span>{busy ? <button className="button button-secondary stop-button" type="button" onClick={onStopQuery} aria-label="Stop generating"><span aria-hidden="true">■</span> Stop</button> : <button className="button button-primary send-button" type="submit" disabled={!query.trim()} aria-label="Send question"><Icon>↑</Icon></button>}</div></form></section></div>
}

function ConversationRail({ conversations, conversationListBusy, conversationListError, conversationHasMore, conversationId, messages, busy, conversationBusy, conversationSearch, onSearchConversations, onLoadMoreConversations, onNewChat, onSelectConversation }: Pick<ChatViewProps, 'conversations' | 'conversationListBusy' | 'conversationListError' | 'conversationHasMore' | 'conversationId' | 'messages' | 'busy' | 'conversationBusy' | 'conversationSearch' | 'onSearchConversations' | 'onLoadMoreConversations' | 'onNewChat' | 'onSelectConversation'>) {
  return <aside className="conversation-rail card" aria-label="Conversation history" aria-busy={conversationListBusy}><button className="button button-primary new-chat" type="button" onClick={onNewChat} disabled={busy || conversationBusy}><Icon>＋</Icon>{conversationBusy ? 'Creating…' : 'New chat'}</button><div className="rail-section"><p className="eyebrow rail-label">Conversations</p><label className="history-search"><span className="sr-only">Search conversation history</span><Icon>⌕</Icon><input aria-label="Search conversation history" value={conversationSearch} onChange={(event) => onSearchConversations(event.target.value)} placeholder="Search history" /></label>{conversationId && <div className="conversation-item active"><strong>Current conversation</strong><span>{messages.length ? `${messages.length} messages` : 'Active now'}</span></div>}{conversationListBusy && !conversations.length ? <p className="helper-text" role="status" aria-live="polite">Loading saved conversations…</p> : conversationListError ? <div className="history-unavailable" role="alert"><strong>History unavailable</strong><p>{conversationListError}</p></div> : conversations.length ? <>{conversations.map((conversation) => <button className={`conversation-item ${conversation.conversation_id === conversationId ? 'active' : ''}`} type="button" key={conversation.conversation_id} onClick={() => onSelectConversation(conversation.conversation_id)} disabled={busy || conversationBusy}><strong>{conversation.title || `Conversation ${conversation.conversation_id.slice(0, 8)}`}</strong><span>{conversation.message_count} messages · {new Date(conversation.updated_at).toLocaleString()}</span></button>)}{conversationHasMore && <button className="text-button history-load-more" type="button" onClick={onLoadMoreConversations} disabled={conversationListBusy}>{conversationListBusy ? 'Loading more…' : 'Load more conversations'}</button>}</> : <p className="helper-text" role="status">{conversationSearch.trim() ? 'No conversations match this search.' : 'No saved conversations yet.'}</p>}</div><div className="rail-footer"><StatusBadge>Backend chat API</StatusBadge><p className="helper-text">Only conversation metadata is listed here. Message bodies load after you select a conversation.</p></div></aside>
}

function ChatView(props: ChatViewProps) {
  const [historyOpen, setHistoryOpen] = useState(false)
  const historyButtonRef = useRef<HTMLButtonElement>(null)
  const historyDrawerRef = useRef<HTMLDivElement>(null)
  function closeHistory() { setHistoryOpen(false); window.requestAnimationFrame(() => historyButtonRef.current?.focus()) }
  useEffect(() => {
    if (!historyOpen) return
    const drawer = historyDrawerRef.current
    const first = drawer?.querySelector<HTMLElement>('.history-close, input, button:not([disabled])')
    first?.focus()
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') { event.preventDefault(); closeHistory(); return }
      if (event.key !== 'Tab' || !drawer) return
      const focusable = Array.from(drawer.querySelectorAll<HTMLElement>('button:not([disabled]), input, select, textarea, [href]'))
      if (!focusable.length) return
      const firstFocusable = focusable[0]
      const lastFocusable = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === firstFocusable) { event.preventDefault(); lastFocusable.focus() }
      else if (!event.shiftKey && document.activeElement === lastFocusable) { event.preventDefault(); firstFocusable.focus() }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [historyOpen])
  function newChat() { closeHistory(); props.onNewChat() }
  function selectConversation(conversationId: string) { closeHistory(); props.onSelectConversation(conversationId) }
  const childProps: ChatViewProps = { ...props, onNewChat: newChat, onSelectConversation: selectConversation }
  return <div className="chat-history-shell"><div className="chat-mobile-toolbar"><button ref={historyButtonRef} className="button button-secondary history-button" type="button" aria-expanded={historyOpen} aria-controls="conversation-history-drawer" onClick={() => setHistoryOpen((open) => !open)}><Icon>☰</Icon> History</button></div>{historyOpen && <button className="history-scrim" aria-label="Close history" type="button" onClick={closeHistory} />}<div ref={historyDrawerRef} id="conversation-history-drawer" className={`history-drawer ${historyOpen ? 'history-drawer-open' : ''}`} role={historyOpen ? 'dialog' : undefined} aria-modal={historyOpen ? true : undefined} aria-labelledby={historyOpen ? 'conversation-history-title' : undefined}><button className="history-close" type="button" onClick={closeHistory}>Close history</button><h2 id="conversation-history-title" className="sr-only">Conversation history</h2><ConversationRail {...childProps} /></div><div className="chat-body"><ChatBody {...childProps} /></div></div>
}

function metricValue(metric: Dashboard['users']): string { if (!metric?.available || metric.value === null || metric.value === undefined) return 'Unavailable'; if (typeof metric.value !== 'object') return String(metric.value); const value = metric.value as Record<string, unknown>; const candidate = value.total ?? value.requests ?? value.jobs; return candidate === undefined ? JSON.stringify(metric.value) : String(candidate) }

function DashboardView() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(true)
  async function load() { setLoading(true); setError(''); try { setDashboard(await getDashboard()) } catch (reason) { setError(reason instanceof Error ? reason.message : 'Dashboard request failed.') } finally { setLoading(false) } }
  useEffect(() => { void load() }, [])
  const metrics = [['users', 'Users', 'users'], ['documents', 'Documents', 'documents'], ['usage', 'Queries', 'requests'], ['ingestion', 'Ingestion jobs', 'jobs'], ['latency', 'Latency', 'milliseconds'], ['cost', 'Model cost', 'USD'], ['evaluation', 'Evaluation', 'score'], ['cache_hit_rate', 'Cache hit rate', 'ratio']] as const
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">System intelligence</p><h1>Admin overview</h1><p className="muted">A measured snapshot from the administrative API. No fake charts or zeros are added.</p></div><button className="button button-secondary" type="button" onClick={() => void load()}>↻ Refresh</button></header>{error && <ErrorNotice message={error} onRetry={() => void load()} />}{loading ? <div className="empty-state card"><h1>Loading dashboard…</h1></div> : <><div className="metrics-grid">{metrics.map(([key, label, unit]) => { const metric = dashboard?.[key as keyof Dashboard] as Dashboard['users']; return <div className="metric-card card" key={key}><div className="metric-top"><span>{label}</span><span className="metric-icon">▦</span></div><strong>{metricValue(metric)}</strong><small>{metric?.available ? `${metric.unit || unit} · ${metric.provenance}` : metric?.reason || 'No backend measurement'}</small></div> })}</div><div className="dashboard-grid"><section className="card empty-state compact-empty"><h2>No time-series data</h2><p>The current contract exposes snapshots only. A monitoring chart will appear when a telemetry endpoint exists.</p></section><section className="card info-card"><div className="info-card-title"><span>Operational source</span><Icon>◈</Icon></div><strong>{dashboard?.schema_version || 'v1'}</strong><p className="muted">Last refreshed from the backend; values are not estimated by the frontend.</p></section></div></>}</div>
}

function DataViewEmpty({ message }: { message: string }) { return <div className="empty-state card"><div className="empty-icon"><Icon>⌁</Icon></div><h1>No records returned</h1><p>{message}</p></div> }

function UsersView({ onToast }: { onToast: (message: string) => void }) {
  const [users, setUsers] = useState<UserRecord[]>([])
  const [departments, setDepartments] = useState<DepartmentRecord[]>([])
  const [accessRequests, setAccessRequests] = useState<AccessRequestMetadata[]>([])
  const [accessStatus, setAccessStatus] = useState<'PENDING_ADMIN_REVIEW' | 'ALL'>('PENDING_ADMIN_REVIEW')
  const [reviewingRequestId, setReviewingRequestId] = useState<string | null>(null)
  const [reviewRetry, setReviewRetry] = useState<{ request: AccessRequestMetadata; decision: 'APPROVE' | 'REJECT' } | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [showUserForm, setShowUserForm] = useState(false)
  const [showDepartmentForm, setShowDepartmentForm] = useState(false)
  const [email, setEmail] = useState('')
  const [temporaryPassword, setTemporaryPassword] = useState('')
  const [departmentName, setDepartmentName] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [userResult, departmentResult, accessRequestResult] = await Promise.all([
        getUsers(),
        getDepartments(),
        getAccessRequests(accessStatus),
      ])
      setUsers(userResult.users)
      setDepartments(departmentResult.departments)
      setAccessRequests(Array.isArray(accessRequestResult.items) ? accessRequestResult.items : [])
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Identity request failed.')
    } finally {
      setLoading(false)
    }
  }, [accessStatus])

  useEffect(() => { void load() }, [load])
  const departmentNames = useMemo(() => new Map(departments.map((department) => [department.department_id, department.name])), [departments])

  async function provisionUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    try {
      await createUser({ email, password: temporaryPassword, roles: ['employee'], department_ids: [] })
      setEmail('')
      setTemporaryPassword('')
      setShowUserForm(false)
      onToast('Inactive account provisioned by the backend.')
      await load()
    } catch (reason) {
      setError(describeRequestError(reason, 'Account could not be provisioned.'))
    }
  }

  async function provisionDepartment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    try {
      await createDepartment(departmentName)
      setDepartmentName('')
      setShowDepartmentForm(false)
      onToast('Department created by the backend.')
      await load()
    } catch (reason) {
      setError(describeRequestError(reason, 'Department could not be created.'))
    }
  }

  async function toggleUser(user: UserRecord) {
    try {
      if (!user.active) await activateUser(user.user_id)
      else await updateUser(user.user_id, { active: false })
      onToast(user.active ? 'Account deactivated.' : 'Account activated.')
      await load()
    } catch (reason) {
      setError(describeRequestError(reason, 'Account update failed.'))
    }
  }

  async function reviewRequest(accessRequest: AccessRequestMetadata, decision: 'APPROVE' | 'REJECT') {
    const action = decision === 'APPROVE' ? 'approve' : 'reject'
    if (!window.confirm(`Are you sure you want to ${action} this access request?`)) return
    setReviewingRequestId(accessRequest.request_id)
    try {
      await reviewAccessRequest(accessRequest.request_id, decision)
      setReviewRetry(null)
      onToast(decision === 'APPROVE' ? 'Request approved; provisioning is still required.' : 'Request rejected.')
      await load()
    } catch (reason) {
      const conflict = reason instanceof ApiError && reason.status === 409
      setReviewRetry(conflict || (reason instanceof ApiError && reason.retryable) ? { request: accessRequest, decision } : null)
      setError(conflict ? 'This access request changed before your decision was saved. Refresh and retry the review.' : describeRequestError(reason, 'Access request review failed.'))
    } finally {
      setReviewingRequestId(null)
    }
  }

  return <div className="content-stack">
    <header className="page-heading"><div><p className="eyebrow">Identity & access</p><h1>Users & departments</h1><p className="muted">Manage only the identity and department operations exposed by the backend. Chairman is a reader, not an administrator.</p></div><div className="heading-actions"><button className="button button-secondary" type="button" onClick={() => setShowDepartmentForm((value) => !value)}>＋ Department</button><button className="button button-primary" type="button" onClick={() => setShowUserForm((value) => !value)}>＋ Provision account</button></div></header>
    {error && <ErrorNotice message={error} onRetry={reviewRetry ? () => void reviewRequest(reviewRetry.request, reviewRetry.decision) : () => void load()} />}
    {showUserForm && <form className="inline-form card" onSubmit={provisionUser}><div><strong>Provision inactive account</strong><p className="helper-text">The backend returns active=false until a real invitation/activation flow exists.</p></div><label>Work email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label>Temporary password<input value={temporaryPassword} onChange={(event) => setTemporaryPassword(event.target.value)} required /></label><button className="button button-primary" type="submit">Create account</button></form>}
    {showDepartmentForm && <form className="inline-form card" onSubmit={provisionDepartment}><label>Department name<input value={departmentName} onChange={(event) => setDepartmentName(event.target.value)} required /></label><button className="button button-primary" type="submit">Create department</button></form>}
    {loading ? <div className="empty-state card"><h1>Loading identities…</h1></div> : <>
      <section className="card activity-card"><div className="section-heading"><div><h2>Access requests</h2><p className="muted">Managers see applicant details needed for review. Approval never grants access or sends email automatically.</p></div><div className="heading-actions"><label className="compact-select">View <select aria-label="Access request filter" value={accessStatus} onChange={(event) => setAccessStatus(event.target.value as 'PENDING_ADMIN_REVIEW' | 'ALL')}><option value="PENDING_ADMIN_REVIEW">Pending</option><option value="ALL">All statuses</option></select></label><StatusBadge tone="warning">{`${accessRequests.length} returned`}</StatusBadge></div></div>{accessRequests.length ? <div className="table-wrap"><table><thead><tr><th>Applicant</th><th>Department / reason</th><th>Created</th><th>Action</th></tr></thead><tbody>{accessRequests.map((accessRequest) => <tr key={accessRequest.request_id}><td><strong>{accessRequest.full_name}</strong><span className="table-subtitle">{accessRequest.email}</span><span className="table-subtitle">{accessRequest.request_id}</span></td><td><strong>{accessRequest.department}</strong><span className="table-subtitle">{accessRequest.reason}</span></td><td>{new Date(accessRequest.created_at).toLocaleString()}</td><td>{accessRequest.status === 'PENDING_ADMIN_REVIEW' ? <><button className="text-button" type="button" disabled={reviewingRequestId === accessRequest.request_id} onClick={() => void reviewRequest(accessRequest, 'APPROVE')}>{reviewingRequestId === accessRequest.request_id ? 'Saving…' : 'Approve request'}</button><button className="text-button danger-text" type="button" disabled={reviewingRequestId === accessRequest.request_id} onClick={() => void reviewRequest(accessRequest, 'REJECT')}>Reject request</button></> : <StatusBadge tone="neutral">{accessRequest.status}</StatusBadge>}</td></tr>)}</tbody></table></div> : <p className="muted">No access requests for this tenant and filter.</p>}</section>
      <section className="card activity-card"><div className="section-heading"><div><h2>Enterprise identities</h2><p className="muted">No client-side accounts or role labels are fabricated.</p></div><StatusBadge tone="success">{`${users.length} returned`}</StatusBadge></div>{users.length ? <div className="table-wrap"><table><thead><tr><th>User</th><th>Roles</th><th>Departments</th><th>Status</th><th>Action</th></tr></thead><tbody>{users.map((user) => <tr key={user.user_id}><td><strong>{user.email}</strong><span className="table-subtitle">{user.user_id}</span></td><td>{user.roles.map((role) => <span className="soft-chip" key={role}>{role}</span>)}</td><td>{user.department_ids.map((id) => departmentNames.get(id) || id).join(', ') || 'None returned'}</td><td><StatusBadge tone={user.active ? 'success' : 'danger'}>{user.active ? 'ACTIVE' : 'INACTIVE'}</StatusBadge></td><td><button className="text-button" type="button" onClick={() => void toggleUser(user)}>{user.active ? 'Deactivate' : 'Activate'}</button></td></tr>)}</tbody></table></div> : <p className="muted">No users returned for this tenant.</p>}</section>
    </>}
  </div>
}

function DocumentDetail({ document, onToast, onChanged }: { document: DocumentRecord; onToast: (message: string) => void; onChanged: () => void }) {
  const [versions, setVersions] = useState<DocumentVersion[]>([]); const [job, setJob] = useState<IngestionJob | null>(null); const [error, setError] = useState(''); const [accessRole, setAccessRole] = useState('employee'); const [accessEffect, setAccessEffect] = useState<'ALLOW' | 'DENY'>('ALLOW')
  useEffect(() => { void getDocumentVersions(document.document_id).then((result) => setVersions(Array.isArray(result) ? result : [])).catch((reason) => setError(describeRequestError(reason, 'Version history unavailable.'))) }, [document.document_id])
  async function run(action: () => Promise<unknown>, message: string) { try { await action(); onToast(message); onChanged() } catch (reason) { setError(describeRequestError(reason, 'The backend rejected this action.')) } }
  const latest = versions[versions.length - 1]
  return <aside className="detail-panel card" aria-label="Document details"><div className="detail-heading"><div><p className="eyebrow">Authorized detail</p><h2>{document.title}</h2><p className="helper-text">{document.document_id}</p></div><StatusBadge tone={document.status === 'ACTIVE' ? 'success' : 'warning'}>{document.status}</StatusBadge></div>{error && <ErrorNotice message={error} />}{latest ? <><div className="detail-section highlighted"><div className="detail-label"><span>Version {latest.version_number}</span><span>{latest.status}</span></div><div className="property-grid"><span>Source URI<strong>{latest.source_uri}</strong></span><span>Ingestion job<strong>{latest.job_id}</strong></span><span>Checksum<strong>{latest.sha256.slice(0, 12)}…</strong></span><span>Approvals<strong>{latest.approvals.length || 'None returned'}</strong></span></div><div className="detail-actions">{(latest.status === 'QUARANTINED' || latest.status === 'PENDING_REVIEW_2') && <button className="button button-secondary" type="button" onClick={() => void run(() => reviewDocumentVersion(document.document_id, latest.version_id, latest.status === 'QUARANTINED' ? 1 : 2), 'Review decision recorded.')}>Approve stage {latest.status === 'QUARANTINED' ? 1 : 2}</button>}{latest.status === 'PROCESS_VALIDATED' && <button className="button button-primary" type="button" onClick={() => void run(() => publishDocumentVersion(document.document_id, latest.version_id), 'Version published.')}>Publish version</button>}{latest.status === 'ACTIVE' && <button className="button button-secondary danger-text" type="button" onClick={() => void run(() => revokeDocumentVersion(document.document_id, latest.version_id), 'Version revoked.')}>Revoke version</button>}</div></div><div className="detail-section"><div className="detail-label"><span>Document ACL</span><span>Explicit deny overrides allow</span></div><div className="inline-access"><select aria-label="Access role" value={accessRole} onChange={(event) => setAccessRole(event.target.value)}><option value="employee">employee</option><option value="chairman">chairman</option><option value="website_manager">website_manager</option></select><select aria-label="Access effect" value={accessEffect} onChange={(event) => setAccessEffect(event.target.value as 'ALLOW' | 'DENY')}><option value="ALLOW">ALLOW</option><option value="DENY">DENY</option></select><button className="button button-secondary" type="button" onClick={() => { const grant: AccessGrant = { action: 'document:read', effect: accessEffect, role: accessRole }; void run(() => updateDocumentAccess(document.document_id, [grant]), 'Document access policy updated.') }}>Save ACL</button></div></div><div className="detail-section"><div className="detail-label"><span>Version history</span><span>{versions.length} returned</span></div>{versions.map((version) => <div className="review-row" key={version.version_id}><div className="review-main"><strong>v{version.version_number} · {version.status}</strong><span>{version.version_id} · {version.approvals.length} approval records</span></div><button className="text-button" type="button" onClick={() => void getIngestionJob(version.job_id).then(setJob).catch((reason) => setError(describeRequestError(reason, 'Ingestion status unavailable.')))}>Job status</button></div>)}{job && <p className="helper-text">Job {job.job_id}: {job.state} · {job.current_stage} · attempt {job.attempt}</p>}</div></> : <div className="detail-section highlighted"><p>No version metadata returned for this document.</p></div>}</aside>
}

function DocumentsView({ onToast }: { onToast: (message: string) => void }) {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]); const [total, setTotal] = useState(0); const [selected, setSelected] = useState<DocumentRecord | null>(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(true); const [showUpload, setShowUpload] = useState(false); const [uploadBusy, setUploadBusy] = useState(false); const [uploadTitle, setUploadTitle] = useState(''); const [uploadFilename, setUploadFilename] = useState(''); const [uploadSource, setUploadSource] = useState('private://documents/metadata')
  async function load() { setLoading(true); setError(''); try { const result = await getDocuments(); setDocuments(result.items); setTotal(result.pagination.total); setSelected((current) => current ? result.items.find((item) => item.document_id === current.document_id) || null : null) } catch (reason) { setError(reason instanceof Error ? reason.message : 'Document request failed.') } finally { setLoading(false) } }
  useEffect(() => { void load() }, [])
  async function upload(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setError(''); setUploadBusy(true); try { const extension = uploadFilename.split('.').pop()?.toLowerCase() || ''; if (!['pdf', 'docx', 'xlsx'].includes(extension)) { setError('Use a PDF, DOCX or XLSX filename for the metadata contract. No binary file is uploaded here.'); return } const mime = extension === 'docx' ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : extension === 'xlsx' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' : 'application/pdf'; await uploadMetadataDocument({ title: uploadTitle, filename: uploadFilename, source_uri: uploadSource, sha256: '0'.repeat(64), size_bytes: 0, mime_type: mime, classification: 'PUBLIC' }); setShowUpload(false); setUploadTitle(''); setUploadFilename(''); onToast('Document metadata registered. No binary file was uploaded.'); await load() } catch (reason) { setError(describeRequestError(reason, 'Metadata registration failed.')) } finally { setUploadBusy(false) } }
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">Authorized knowledge inventory</p><h1>Knowledge documents</h1><p className="muted">Metadata and lifecycle state come from the backend. Source content is never shown in the catalog.</p></div><div className="heading-actions"><button className="button button-secondary" type="button" onClick={() => void load()}>↻ Refresh</button><button className="button button-primary" type="button" onClick={() => setShowUpload((value) => !value)}>＋ Register metadata</button></div></header>{error && <ErrorNotice message={error} onRetry={() => void load()} />}{showUpload && <form className="inline-form card" onSubmit={upload}><div><strong>Register document metadata</strong><p className="helper-text">The current backend accepts JSON metadata only. This flow does not upload a binary file or calculate a real checksum.</p></div><label>Title<input value={uploadTitle} onChange={(event) => setUploadTitle(event.target.value)} required /></label><label>Filename<input value={uploadFilename} onChange={(event) => setUploadFilename(event.target.value)} placeholder="policy.pdf" required /></label><label>Source URI<input value={uploadSource} onChange={(event) => setUploadSource(event.target.value)} required /></label><button className="button button-primary" type="submit" disabled={uploadBusy}>{uploadBusy ? 'Registering…' : 'Register metadata'}</button></form>}{loading ? <div className="empty-state card"><h1>Loading documents…</h1></div> : documents.length ? <div className="document-workspace"><section className="card document-list"><div className="section-heading"><div><h2>Returned documents</h2><p className="muted">Showing {documents.length} of {total} records from GET /api/v1/documents.</p></div><StatusBadge tone="success">{`${documents.length} returned`}</StatusBadge></div><div className="table-wrap document-table"><table><thead><tr><th>Document</th><th>Classification</th><th>Status</th><th>Department</th><th>Current version</th></tr></thead><tbody>{documents.map((document) => <tr className={selected?.document_id === document.document_id ? 'selected-row' : ''} key={document.document_id} onClick={() => setSelected(document)}><td><button className="table-link" type="button" onClick={() => setSelected(document)}><strong>{document.title}</strong><span className="table-subtitle">{document.document_id}</span></button></td><td><span className="soft-chip">{document.classification}</span></td><td><StatusBadge tone={document.status === 'ACTIVE' ? 'success' : 'neutral'}>{document.status}</StatusBadge></td><td>{document.owner_department_id || 'Not returned'}</td><td>{document.current_version_id || 'Not published'}</td></tr>)}</tbody></table></div></section>{selected ? <DocumentDetail document={selected} onToast={onToast} onChanged={() => void load()} /> : <div className="detail-panel card empty-detail"><h2>Select a document</h2><p className="muted">Open authorized metadata and version history without exposing source text.</p></div>}</div> : <DataViewEmpty message="The backend returned no documents for this principal." />}</div>
}

function ApprovalsView({ onToast }: { onToast: (message: string) => void }) {
  const [approvals, setApprovals] = useState<ApprovalRecord[]>([]); const [total, setTotal] = useState(0); const [error, setError] = useState(''); const [loading, setLoading] = useState(true)
  async function load() { setLoading(true); setError(''); try { const result = await getApprovals(); setApprovals(result.items); setTotal(result.pagination.total) } catch (reason) { setError(reason instanceof Error ? reason.message : 'Approval request failed.') } finally { setLoading(false) } }
  useEffect(() => { void load() }, [])
  async function approve(record: ApprovalRecord) { const stage = record.status === 'QUARANTINED' ? 1 : 2; try { await reviewDocumentVersion(record.document_id, record.version_id, stage); onToast(`Stage ${stage} approval recorded.`); await load() } catch (reason) { setError(describeRequestError(reason, 'Review decision failed.')) } }
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">Ingestion governance</p><h1>Review & ingest</h1><p className="muted">Two review gates remain separate. Publish is never implied by an approval click.</p></div><button className="button button-secondary" type="button" onClick={() => void load()}>↻ Refresh</button></header>{error && <ErrorNotice message={error} onRetry={() => void load()} />}{loading ? <div className="empty-state card"><h1>Loading approval queue…</h1></div> : approvals.length ? <section className="card activity-card"><div className="section-heading"><div><h2>Approval queue</h2><p className="muted">Showing {approvals.length} of {total} records from GET /api/v1/approvals.</p></div><StatusBadge tone="warning">{`${approvals.length} returned`}</StatusBadge></div><div className="table-wrap"><table><thead><tr><th>Document / version</th><th>Status</th><th>Ingestion job</th><th>Approvals</th><th>Decision</th></tr></thead><tbody>{approvals.map((record) => <tr key={record.version_id}><td><strong>{record.document_id}</strong><span className="table-subtitle">{record.version_id} · v{record.version_number}</span></td><td><StatusBadge tone={record.status === 'ACTIVE' ? 'success' : 'warning'}>{record.status}</StatusBadge></td><td><span className="table-subtitle">{record.job_id}</span></td><td>{record.approvals.length ? record.approvals.map((approval) => <div className="table-subtitle" key={`${record.version_id}-${approval.stage}`}>Stage {approval.stage}: {approval.decision} · {approval.reviewer_id}</div>) : 'No approval decision returned'}</td><td>{record.status === 'QUARANTINED' || record.status === 'PENDING_REVIEW_2' ? <button className="text-button" type="button" onClick={() => void approve(record)}>Approve stage {record.status === 'QUARANTINED' ? 1 : 2}</button> : <span className="helper-text">No action</span>}</td></tr>)}</tbody></table></div></section> : <DataViewEmpty message="The backend returned no versions awaiting or carrying approval decisions." />}</div>
}

function AuditView() {
  const [events, setEvents] = useState<Array<{ event_id: string; event: string; action: string; outcome: string; decision?: string | null; principal_id?: string | null; code?: string | null; occurred_at: string; safe_metadata: Record<string, unknown> }>>([]); const [feedbackCount, setFeedbackCount] = useState<number | null>(null); const [total, setTotal] = useState(0); const [error, setError] = useState(''); const [loading, setLoading] = useState(true)
  async function load() { setLoading(true); setError(''); try { const [audit, feedback] = await Promise.all([getAuditEvents(), getFeedback()]); setEvents(audit.items); setTotal(audit.pagination.total); setFeedbackCount(feedback.pagination.total) } catch (reason) { setError(reason instanceof Error ? reason.message : 'Audit request failed.') } finally { setLoading(false) } }
  useEffect(() => { void load() }, [])
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">Traceable administration</p><h1>Audit & monitoring</h1><p className="muted">Metadata-only events and feedback counts. Conversation bodies, prompts and model output never enter this view.</p></div><button className="button button-secondary" type="button" onClick={() => void load()}>↻ Refresh</button></header>{error && <ErrorNotice message={error} onRetry={() => void load()} />}{loading ? <div className="empty-state card"><h1>Loading audit events…</h1></div> : <><div className="summary-grid"><div className="metric-card card"><span>Audit events</span><strong>{total}</strong><small>GET /api/v1/audit snapshot</small></div><div className="metric-card card"><span>Feedback records</span><strong>{feedbackCount ?? 'Unavailable'}</strong><small>Minimized review projection</small></div><div className="metric-card card"><span>Monitoring stream</span><strong>Unavailable</strong><small>No time-series endpoint returned</small></div></div>{events.length ? <section className="card activity-card"><div className="section-heading"><div><h2>Audit events</h2><p className="muted">Showing {events.length} of {total} records from GET /api/v1/audit.</p></div><StatusBadge tone="neutral">{`${events.length} returned`}</StatusBadge></div><div className="table-wrap"><table><thead><tr><th>Time</th><th>Event / action</th><th>Outcome</th><th>Principal</th><th>Code / metadata</th></tr></thead><tbody>{events.map((event) => <tr key={event.event_id}><td><span className="table-subtitle">{new Date(event.occurred_at).toLocaleString()}</span><span className="table-subtitle">{event.event_id}</span></td><td><strong>{event.event}</strong><span className="table-subtitle">{event.action}</span></td><td><StatusBadge tone={event.outcome === 'SUCCESS' || event.decision === 'ALLOW' ? 'success' : event.decision === 'DENY' ? 'danger' : 'neutral'}>{`${event.outcome}${event.decision ? ` · ${event.decision}` : ''}`}</StatusBadge></td><td>{event.principal_id || 'System / unavailable'}</td><td><span className="table-subtitle">{event.code || 'No code returned'}</span><span className="table-subtitle">{JSON.stringify(event.safe_metadata)}</span></td></tr>)}</tbody></table></div></section> : <DataViewEmpty message="The backend returned no audit events for this principal." />}</>}</div>
}

function viewFromPath(pathname: string): View {
  if (pathname === '/admin' || pathname === '/admin/' || pathname.startsWith('/admin/overview')) return 'dashboard'
  if (pathname.startsWith('/admin/documents')) return 'documents'
  if (pathname.startsWith('/admin/review')) return 'approvals'
  if (pathname.startsWith('/admin/users')) return 'users'
  if (pathname.startsWith('/admin/audit')) return 'audit'
  return 'chat'
}

function pathForView(view: View): string {
  return view === 'chat' ? '/chat' : `/admin/${view === 'dashboard' ? 'overview' : view}`
}

function AdminGuardView({ principal, onSignIn }: { principal: Principal | null; onSignIn: () => void }) {
  if (!principal) return <section className="empty-state card" aria-labelledby="admin-sign-in-title"><div className="empty-icon"><Icon>⌁</Icon></div><p className="eyebrow">Protected workspace</p><h1 id="admin-sign-in-title">Sign in to enter Admin</h1><p>Admin data is never requested for an anonymous session. Sign in with a backend-issued identity to continue.</p><button className="button button-primary" type="button" onClick={onSignIn}>Sign in</button></section>
  return <section className="empty-state card" aria-labelledby="admin-denied-title"><div className="empty-icon"><Icon>!</Icon></div><p className="eyebrow">Access boundary</p><h1 id="admin-denied-title">Admin access is unavailable</h1><p>Your current backend role cannot enter this workspace. Chairman and employee sessions are not treated as administrators.</p><p className="helper-text">No admin endpoint was requested.</p></section>
}

export function App() {
  const initialPath = window.location.pathname
  const [routePath, setRoutePath] = useState(initialPath)
  const [authReturnPath, setAuthReturnPath] = useState('/chat')
  const [principal, setPrincipal] = useState<Principal | null>(null); const [identityChecked, setIdentityChecked] = useState(false); const [view, setView] = useState<View>(() => viewFromPath(initialPath)); const [authMode, setAuthMode] = useState<AuthMode>(() => initialPath === '/sign-in' ? 'sign-in' : initialPath === '/onboarding' ? 'onboarding' : null); const [mobileNavOpen, setMobileNavOpen] = useState(false); const [toast, setToast] = useState(''); const [conversationId, setConversationId] = useState<string>(); const [conversationBusy, setConversationBusy] = useState(false); const [messages, setMessages] = useState<ConversationMessage[]>([]); const [answer, setAnswer] = useState<QueryAnswer | null>(null); const [downloadStates, setDownloadStates] = useState<Record<string, DownloadState>>({}); const [queryBusy, setQueryBusy] = useState(false); const [queryCancelled, setQueryCancelled] = useState(false); const [queryError, setQueryError] = useState(''); const [retryMode, setRetryMode] = useState<RetryMode>(null); const [retryQuery, setRetryQuery] = useState(''); const [preview, setPreview] = useState(''); const streamAbortRef = useRef<AbortController | null>(null)

  const [conversations, setConversations] = useState<ConversationSummary[]>([]); const [conversationListBusy, setConversationListBusy] = useState(false); const [conversationListError, setConversationListError] = useState(''); const [conversationHasMore, setConversationHasMore] = useState(false); const [conversationSearch, setConversationSearch] = useState(''); const conversationOffsetRef = useRef(0)
  const loadConversationList = useCallback(async (search: string, append = false) => { const offset = append ? conversationOffsetRef.current : 0; setConversationListBusy(true); try { const result = await getConversations(20, offset, search); const items = Array.isArray(result.items) ? result.items : []; conversationOffsetRef.current = offset + items.length; setConversations((current) => append ? [...current, ...items.filter((item) => !current.some((existing) => existing.conversation_id === item.conversation_id))] : items); setConversationHasMore(Boolean(result.pagination?.has_more)); setConversationListError('') } catch (reason) { if (!append && reason instanceof ApiError && [404, 410].includes(reason.status)) { setConversations([]); setConversationHasMore(false); setConversationListError('') } else setConversationListError(describeRequestError(reason, 'Saved conversations are unavailable.')) } finally { setConversationListBusy(false) } }, [])
  useEffect(() => { if (!getAccessToken()) { setIdentityChecked(true); return } getCurrentIdentity().then(setPrincipal).catch(() => setPrincipal(null)).finally(() => setIdentityChecked(true)) }, [])
  useEffect(() => { if (identityChecked) void loadConversationList(conversationSearch) }, [identityChecked, conversationSearch, loadConversationList])
  useEffect(() => { if (identityChecked && !queryBusy && conversationId) void loadConversationList(conversationSearch) }, [identityChecked, queryBusy, conversationId, conversationSearch, loadConversationList])
  useEffect(() => { if (queryBusy) return; const latest = [...messages].reverse().find((message) => message.role === 'assistant' && message.answer_id); if (latest?.answer_id) setAnswer({ answer_id: latest.answer_id, status: latest.status || 'ANSWERED', text: latest.content, citations: latest.citations || [], reason_codes: latest.reason_codes }) }, [messages, queryBusy])
  useEffect(() => { const onPopState = () => { const nextPath = window.location.pathname; setRoutePath(nextPath); setView(viewFromPath(nextPath)); setAuthMode(nextPath === '/sign-in' ? 'sign-in' : nextPath === '/onboarding' ? 'onboarding' : null) }; window.addEventListener('popstate', onPopState); return () => window.removeEventListener('popstate', onPopState) }, [])
  useEffect(() => { const saved = window.localStorage.getItem(CONVERSATION_STORAGE_KEY); if (saved) void restoreConversation(saved) }, [])
  useEffect(() => { if (conversationId) window.localStorage.setItem(CONVERSATION_STORAGE_KEY, conversationId); else window.localStorage.removeItem(CONVERSATION_STORAGE_KEY) }, [conversationId])
  async function restoreConversation(savedConversationId: string) { setConversationId(savedConversationId); setConversationBusy(true); setQueryError(''); setRetryMode(null); try { const conversation = await getConversation(savedConversationId); setMessages(conversation.messages); setAnswer(null); setPreview(''); setDownloadStates({}) } catch (reason) { const missing = reason instanceof ApiError && [404, 410].includes(reason.status); if (missing) { window.localStorage.removeItem(CONVERSATION_STORAGE_KEY); setConversationId(undefined); setMessages([]); setAnswer(null); setPreview(''); setDownloadStates({}); setQueryError(''); setRetryMode(null) } else { const staleSession = reason instanceof ApiError && [401, 403].includes(reason.status); setRetryMode(staleSession ? 'conversation' : 'restore'); setQueryError(describeRequestError(reason, 'The saved conversation is unavailable. Retry or reconnect your session.')) } } finally { setConversationBusy(false) } }
  function notify(message: string) { setToast(message); window.setTimeout(() => setToast(''), 3200) }
  function openAuth(mode: 'sign-in' | 'onboarding') { const returnPath = routePath.startsWith('/admin') ? routePath : authReturnPath; setAuthReturnPath(returnPath); const nextPath = mode === 'sign-in' ? '/sign-in' : '/onboarding'; window.history.pushState({}, '', nextPath); setRoutePath(nextPath); setAuthMode(mode); setQueryError('') }
  function closeAuth() { navigate('chat') }
  function navigate(nextView: View) { const item = navItems.find((nav) => nav.id === nextView); if (item?.admin && !canAdmin(principal)) { notify('This area is restricted by the backend policy.'); return } if (item?.manager && !canManage(principal)) { notify('This area is restricted by the backend policy.'); return } const nextPath = pathForView(nextView); window.history.pushState({}, '', nextPath); setRoutePath(nextPath); setAuthMode(null); setView(nextView); setMobileNavOpen(false); setQueryError('') }
  async function newChat(force = false) { if (!force && (queryBusy || conversationBusy)) return; setConversationBusy(true); setQueryError(''); setRetryMode(null); setRetryQuery(''); setQueryCancelled(false); try { const conversation = await createConversation(); setConversationId(conversation.conversation_id); setMessages([]); setAnswer(null); setPreview(''); setDownloadStates({}); notify('New backend conversation created.') } catch (reason) { const message = describeRequestError(reason, 'Conversation could not be created.'); setQueryError(message); setRetryMode('conversation'); notify(message) } finally { setConversationBusy(false) } }
  function startNewChat() { navigate('chat'); void newChat() }
  function updateAssistantMessage(messageId: string, content: string) { setMessages((current) => current.map((message) => message.message_id === messageId ? { ...message, content } : message)) }
  function stopLiveQuery() { streamAbortRef.current?.abort() }
  async function submitLiveQuery(query: string, retry = false) {
    setQueryBusy(true); setQueryError(''); setRetryMode(null); setQueryCancelled(false); setRetryQuery(query); setAnswer(null); setPreview(''); const controller = new AbortController(); streamAbortRef.current = controller
    try { const activeConversation = (retry || !conversationId) ? (await createConversation()).conversation_id : conversationId; setConversationId(activeConversation); setAnswer({ status: 'STREAMING', text: '', citations: [] }); const existingAssistant = retry ? [...messages].reverse().find((message) => message.role === 'assistant') : undefined; let assistantMessageId = existingAssistant?.message_id || `stream-${Date.now()}-${Math.random().toString(36).slice(2)}`; let streamedText = ''; let streamedCitations: QueryCitation[] = []
      if (existingAssistant) setMessages((current) => current.map((message) => message.message_id === assistantMessageId ? { ...message, content: '' } : message)); else setMessages((current) => [...current, { message_id: `user-${Date.now()}-${Math.random().toString(36).slice(2)}`, role: 'user', content: query, created_at: new Date().toISOString() }, { message_id: assistantMessageId, role: 'assistant', content: '', created_at: new Date().toISOString() }])
      const completed = await streamMessage(activeConversation, query, { onStart: (event) => { if (!event.message_id) return; const previousId = assistantMessageId; assistantMessageId = event.message_id; setMessages((current) => current.map((message) => message.message_id === previousId ? { ...message, message_id: assistantMessageId } : message)) }, onToken: (delta) => { streamedText += delta; updateAssistantMessage(assistantMessageId, streamedText); setAnswer((current) => current ? { ...current, text: streamedText } : current) }, onCitation: (citation) => { streamedCitations = [...streamedCitations, citation]; setAnswer((current) => current ? { ...current, citations: streamedCitations } : current) }, onDone: (finalAnswer) => { setAnswer(finalAnswer); updateAssistantMessage(assistantMessageId, finalAnswer.text) } }, controller.signal); setAnswer(completed); updateAssistantMessage(assistantMessageId, completed.text); notify('Answer received from the backend RAG stream.')
    } catch (reason) { if (controller.signal.aborted) { setAnswer((current) => current ? { ...current, status: 'CANCELLED' } : current); setQueryCancelled(true); setRetryMode('query'); notify('Answer generation stopped.'); return } if (isConversationGone(reason)) { window.localStorage.removeItem(CONVERSATION_STORAGE_KEY); setConversationId(undefined) } const message = describeRequestError(reason, 'The RAG query could not be completed.'); setAnswer((current) => current ? { ...current, status: 'ERROR' } : current); setQueryError(message); setRetryMode('query'); notify(message) }
    finally { if (streamAbortRef.current === controller) streamAbortRef.current = null; setQueryBusy(false) }
  }
  function retryLastAction() { if (retryMode === 'conversation') { void newChat(); return } if (retryMode === 'query' && retryQuery) void submitLiveQuery(retryQuery, true); if (retryMode === 'restore') { const saved = window.localStorage.getItem(CONVERSATION_STORAGE_KEY); if (saved) void restoreConversation(saved) } }
  function reconnect() { streamAbortRef.current?.abort(); window.localStorage.removeItem(CONVERSATION_STORAGE_KEY); setConversationId(undefined); setMessages([]); setAnswer(null); setPreview(''); setDownloadStates({}); setQueryError(''); setRetryMode(null); setRetryQuery(''); setQueryCancelled(false); void newChat(true) }
  async function handlePreview(citationId: string) { if (!answer?.answer_id) { notify('The backend did not return an answer identifier for preview.'); return } try { const result = await previewCitation(answer.answer_id, citationId); setPreview(result.preview || 'The backend returned no preview content.') } catch (reason) { notify(reason instanceof Error ? reason.message : 'Citation preview unavailable.') } }
  async function handleDownload(citation: QueryCitation) {
    const citationId = citation.citation_id
    if (!answer?.answer_id || !citationId) { setDownloadStates((current) => ({ ...current, [citationId]: { status: 'error', message: 'Download unavailable until the backend returns source identifiers.' } })); return }
    setDownloadStates((current) => ({ ...current, [citationId]: { status: 'loading' } }))
    try { const result = await downloadCitation(answer.answer_id, citationId); const url = URL.createObjectURL(result.blob); const anchor = document.createElement('a'); anchor.href = url; anchor.download = result.filename || citationFilename(citation); document.body.appendChild(anchor); anchor.click(); anchor.remove(); window.setTimeout(() => URL.revokeObjectURL(url), 0); setDownloadStates((current) => ({ ...current, [citationId]: { status: 'idle' } })); notify('Authorized source download started.') }
    catch (reason) { const message = reason instanceof ApiError && reason.code === 'CITATION_UNAVAILABLE' ? 'This source is no longer available for your session.' : reason instanceof ApiError && reason.retryable ? 'The source download failed. Retry this download.' : 'This source is no longer available for your session.'; setDownloadStates((current) => ({ ...current, [citationId]: { status: 'error', message } })) }
  }
  async function handleFeedback(rating: 'POSITIVE' | 'NEGATIVE') { if (!answer?.answer_id) { notify('Feedback is unavailable until the backend returns an answer identifier.'); return } try { await submitFeedback(answer.answer_id, rating); notify('Feedback recorded by the backend.') } catch (reason) { notify(reason instanceof Error ? reason.message : 'Feedback could not be recorded.') } }
  async function handleSignOut() { try { await signOut() } finally { setPrincipal(null); setView('chat'); setConversationId(undefined); setMessages([]); setAnswer(null); setRetryMode(null); setRetryQuery(''); setQueryCancelled(false); notify('Signed out.') } }
  function completeAuthentication(next: Principal) { setPrincipal(next); setAuthMode(null); const requestedAdminPath = authReturnPath.startsWith('/admin') && canManage(next); const targetPath = requestedAdminPath ? (authReturnPath === '/admin' || authReturnPath === '/admin/' ? '/admin/overview' : authReturnPath) : '/chat'; window.history.replaceState({}, '', targetPath); setRoutePath(targetPath); setView(viewFromPath(targetPath)) }
  if (!identityChecked) return <div className="app-shell"><main className="main-content"><div className="empty-state card"><h1>Loading identity…</h1></div></main></div>
  const manager = canManage(principal); const roleLabel = principal?.roles.join(', ') || 'Public session'; const currentNav = navItems.find((item) => item.id === view)
  const adminView = view === 'dashboard' ? <DashboardView /> : view === 'users' ? <UsersView onToast={notify} /> : view === 'documents' ? <DocumentsView onToast={notify} /> : view === 'approvals' ? <ApprovalsView onToast={notify} /> : view === 'audit' ? <AuditView /> : <UnavailableView title="This workspace is unavailable" endpoint="backend authorization" />
  const renderedView = authMode ? <AuthView key={authMode} mode={authMode} onModeChange={openAuth} onAuthenticated={completeAuthentication} onCancel={closeAuth} onToast={notify} /> : view === 'chat' ? <ChatView messages={messages} answer={answer} busy={queryBusy} cancelled={queryCancelled} error={queryError} preview={preview} downloadStates={downloadStates} conversationId={conversationId} conversationBusy={conversationBusy} conversations={conversations} conversationListBusy={conversationListBusy} conversationListError={conversationListError} conversationHasMore={conversationHasMore} conversationSearch={conversationSearch} onSearchConversations={setConversationSearch} onLoadMoreConversations={() => void loadConversationList(conversationSearch, true)} retryAvailable={Boolean(retryMode === 'conversation' || (retryMode === 'query' && retryQuery))} onSubmitQuery={(query) => { void submitLiveQuery(query) }} onNewChat={startNewChat} onStopQuery={stopLiveQuery} onRetry={retryLastAction} onReconnect={reconnect} onPreview={handlePreview} onDownload={(citation) => { void handleDownload(citation) }} onFeedback={handleFeedback} onToast={notify} onSelectConversation={(id) => { void restoreConversation(id) }} /> : manager ? adminView : <AdminGuardView principal={principal} onSignIn={() => openAuth('sign-in')} />
  return <div className="app-shell"><aside className={`sidebar ${mobileNavOpen ? 'sidebar-open' : ''}`}><div><div className="brand"><div className="brand-mark"><Icon>✦</Icon></div><div><strong>Enterprise AI</strong><span>Knowledge workspace</span></div></div><button className="button button-primary new-chat sidebar-new-chat" type="button" onClick={startNewChat} disabled={queryBusy || conversationBusy}><Icon>＋</Icon>{conversationBusy ? 'Creating…' : 'New chat'}</button><div className="nav-section"><p className="eyebrow">Workspace</p><nav aria-label="Main navigation">{navItems.filter((item) => !item.manager || manager).map((item) => <button className={`nav-item ${view === item.id && !authMode ? 'nav-item-active' : ''}`} key={item.id} type="button" onClick={() => navigate(item.id)}><Icon>{item.icon}</Icon><span>{item.label}</span></button>)}</nav></div></div><div className="sidebar-bottom"><div className="role-summary"><div className="avatar avatar-user">{principal ? 'ID' : 'PU'}</div><div><strong>{roleLabel}</strong><span>{principal ? principal.tenant_id : 'Public session'}</span></div></div>{principal ? <button className="text-button" type="button" onClick={() => void handleSignOut()}>Sign out</button> : <button className="text-button" type="button" onClick={() => openAuth('sign-in')}>Sign in</button>}</div></aside>{mobileNavOpen && <button className="mobile-scrim" aria-label="Close navigation" type="button" onClick={() => setMobileNavOpen(false)} />}<div className="main-shell"><header className="topbar"><div className="topbar-left"><button className="mobile-menu" aria-label="Open navigation" type="button" onClick={() => setMobileNavOpen(true)}>☰</button><div className="breadcrumbs"><strong>{view === 'chat' ? 'Enterprise Knowledge AI' : 'Enterprise Admin Portal'}</strong><span>›</span><span>{authMode ? (authMode === 'sign-in' ? 'Sign in' : 'Request access') : currentNav?.label}</span></div><StatusBadge>API boundary</StatusBadge><div className="scope-notice topbar-scope" role="note"><Icon>◈</Icon><span>{principal ? `Tenant: ${principal.tenant_id} · Authorized sources` : 'Scope: Public knowledge only'}</span></div></div><div className="topbar-actions"><div className="language-switch language-unavailable"><button type="button" disabled aria-label="Language switch unavailable">VI / EN <span>Unavailable</span></button></div>{principal ? <div className="topbar-profile"><div><strong>{roleLabel}</strong><span>{principal.tenant_id}</span></div><div className="avatar avatar-primary">ID</div></div> : <><button className="button button-secondary" type="button" onClick={() => openAuth('onboarding')}>Request access</button><button className="button button-primary" type="button" onClick={() => openAuth('sign-in')}>Sign in</button></>}</div></header><main className="main-content">{renderedView}</main></div>{toast && <div className="toast" role="status">{toast}</div>}</div>
}
