import { FormEvent, useMemo, useState } from 'react'
import { createConversation, QueryAnswer, submitMessage, waitForQueryCompletion } from './api/client'
import { appConfig } from './config'
import './styles.css'

type Role = 'anonymous' | 'system_admin' | 'website_manager' | 'employee' | 'chairman'
type View = 'chat' | 'dashboard' | 'documents' | 'approvals' | 'users' | 'audit'

const roles: Array<{ id: Role; label: string; shortLabel: string }> = [
  { id: 'anonymous', label: 'Anonymous visitor', shortLabel: 'Public' },
  { id: 'employee', label: 'Employee', shortLabel: 'Employee' },
  { id: 'chairman', label: 'Chairman', shortLabel: 'Chairman' },
  { id: 'website_manager', label: 'Website Manager', shortLabel: 'Manager' },
  { id: 'system_admin', label: 'System Admin', shortLabel: 'Admin' },
]

const documents = [
  { type: 'PDF', title: 'Quy chế chi tiêu nội bộ và công tác phí 2025', id: 'DOC-2025-FIN-0842', department: 'Tài chính', state: 'ACTIVE', visibility: 'INTERNAL' },
  { type: 'DOCX', title: 'Hướng dẫn thực thi bảo mật thông tin ISO27001', id: 'DOC-2024-SEC-0391', department: 'IT & Security', state: 'ACTIVE', visibility: 'INTERNAL' },
  { type: 'XLSX', title: 'Bảng định mức trang thiết bị làm việc', id: 'DOC-2024-OPS-0129', department: 'Vận hành', state: 'ACTIVE', visibility: 'PUBLIC' },
  { type: 'PDF', title: 'Quy trình tiếp nhận và xử lý khiếu nại dịch vụ', id: 'DOC-2025-CS-0511', department: 'Chăm sóc khách hàng', state: 'QUARANTINED', visibility: 'INTERNAL' },
  { type: 'PDF', title: 'Chính sách nghỉ phép và chế độ bảo hiểm y tế', id: 'DOC-2025-HR-0774', department: 'Nhân sự', state: 'ACTIVE', visibility: 'INTERNAL' },
]

const citations = [
  { type: 'PDF', title: 'Quy chế chi tiêu nội bộ và công tác phí 2025', location: 'Trang 4 · §2.1', confidence: '99.1%', id: 'DOC-2025-FIN-0842', visibility: 'INTERNAL' },
  { type: 'XLSX', title: 'Bảng định mức trang thiết bị làm việc', location: 'Sheet: Định mức · C12:E24', confidence: '96.4%', id: 'DOC-2024-OPS-0129', visibility: 'PUBLIC' },
  { type: 'DOCX', title: 'Hướng dẫn thực thi thanh toán', location: 'Mục 2.3 · Quy trình', confidence: '93.8%', id: 'DOC-2024-FIN-0175', visibility: 'INTERNAL' },
]

const navItems: Array<{ id: View; label: string; icon: string; adminOnly?: boolean; managementOnly?: boolean }> = [
  { id: 'chat', label: 'Knowledge chat', icon: '✦' },
  { id: 'dashboard', label: 'Overview', icon: '▦', managementOnly: true },
  { id: 'documents', label: 'Knowledge documents', icon: '▤' },
  { id: 'approvals', label: 'Review & ingest', icon: '✓', managementOnly: true },
  { id: 'users', label: 'Users & access', icon: '♙', adminOnly: true },
  { id: 'audit', label: 'Audit & monitoring', icon: '◷', adminOnly: true },
]

function roleCanManage(role: Role) {
  return role === 'system_admin' || role === 'website_manager'
}

function roleCanAdmin(role: Role) {
  return role === 'system_admin'
}

function roleCanReadKnowledge(role: Role) {
  return role !== 'anonymous'
}

function visibleDocumentsForRole(role: Role) {
  if (roleCanManage(role)) return documents
  if (role === 'chairman') return documents.filter((document) => document.state === 'ACTIVE')
  if (role === 'employee') {
    return documents.filter((document) => document.state === 'ACTIVE' && (
      document.visibility === 'PUBLIC' || document.department === 'Tài chính'
    ))
  }
  return []
}

function Icon({ children }: { children: string }) {
  return <span className="icon" aria-hidden="true">{children}</span>
}

function StatusBadge({ children, tone = 'neutral' }: { children: string; tone?: 'neutral' | 'success' | 'warning' | 'danger' }) {
  return <span className={`status-badge status-${tone}`}><span className="status-dot" aria-hidden="true" />{children}</span>
}

function PermissionDenied({ onChat }: { onChat: () => void }) {
  return <section className="empty-state card" aria-labelledby="denied-title">
    <div className="empty-icon"><Icon>⊘</Icon></div>
    <p className="eyebrow">Access boundary</p>
    <h1 id="denied-title">You do not have permission to view this workspace</h1>
    <p>The backend policy service remains authoritative. This UI hides unavailable actions and does not grant access by itself.</p>
    <button className="button button-primary" type="button" onClick={onChat}>Return to knowledge chat</button>
  </section>
}

function ChatView({ role, language, maintenance, busy, answer, onMaintenance, onSubmitQuery, onToast }: { role: Role; language: 'VI' | 'EN'; maintenance: boolean; busy: boolean; answer: QueryAnswer | null; onMaintenance: () => void; onSubmitQuery: (query: string) => void; onToast: (message: string) => void }) {
  const [citationOpen, setCitationOpen] = useState(false)
  const [query, setQuery] = useState('')
  const copy = language === 'VI'
    ? {
      newChat: 'Cuộc trò chuyện mới', history: 'Lịch sử trò chuyện', title: 'Tôi có thể giúp gì hôm nay?',
      description: 'Câu trả lời chỉ sử dụng các nguồn tri thức doanh nghiệp mà bạn được phép truy cập.',
      sources: (count: number) => `Xem ${count} nguồn hỗ trợ`, hideSources: 'Ẩn nguồn hỗ trợ',
      placeholder: 'Đặt câu hỏi về tri thức doanh nghiệp được cấp quyền...',
    }
    : {
      newChat: 'New chat', history: 'Conversation history', title: 'How can I help today?',
      description: 'Answers use authorized enterprise sources only. Citation details stay collapsed until you inspect them.',
      sources: (count: number) => `View ${count} supporting source${count === 1 ? '' : 's'}`, hideSources: 'Hide supporting sources',
      placeholder: 'Ask a question about your authorized enterprise knowledge...',
    }
  const liveCitations = answer?.citations.map((citation) => ({
    type: citation.locator?.kind || 'SOURCE',
    title: `Document ${citation.document_id}`,
    location: citation.locator?.page ? `Page ${citation.locator.page}` : 'Verified source span',
    confidence: 'VERIFIED',
    id: citation.document_id,
    visibility: 'PUBLIC',
  })) ?? []
  const visibleCitations = (liveCitations.length ? liveCitations : citations).filter((citation) => role !== 'anonymous' || citation.visibility === 'PUBLIC')

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!query.trim()) return
    onToast('Query accepted as a durable job. The answer area will update after polling.')
    onSubmitQuery(query.trim())
    setQuery('')
  }

  return <div className="chat-layout">
    <aside className="conversation-rail card" aria-label="Conversation history">
      <button className="button button-primary new-chat" type="button" onClick={() => onToast('A new conversation has been created.')}><Icon>＋</Icon>{copy.newChat}</button>
      <p className="eyebrow rail-label">{copy.history}</p>
      <button className="conversation-item active" type="button">Q4 expense policy review</button>
      {role !== 'anonymous' && <>
        <button className="conversation-item" type="button">Healthcare policy 2025</button>
        <button className="conversation-item" type="button">Onboarding process summary</button>
      </>}
      <div className="rail-footer">
        <StatusBadge tone="success">RAG cluster operational</StatusBadge>
        <p className="helper-text">Temporary history is kept only for the current anonymous session.</p>
      </div>
    </aside>

    <section className="chat-column" aria-labelledby="chat-title">
      <header className="page-heading chat-heading">
        <div>
          <p className="eyebrow">Enterprise knowledge workspace</p>
          <h1 id="chat-title">{copy.title}</h1>
          <p className="muted">{copy.description}</p>
        </div>
        <div className="heading-actions">
          <StatusBadge tone="success">RAG-Enterprise-v4.1</StatusBadge>
          {roleCanAdmin(role) && <button className={`toggle ${maintenance ? 'toggle-on' : ''}`} type="button" aria-pressed={maintenance} onClick={onMaintenance}><span />{maintenance ? 'MAINTENANCE_ACTIVE' : 'Operational'}</button>}
        </div>
      </header>

      {maintenance && <div className="notice notice-warning" role="alert"><Icon>!</Icon><div><strong>MAINTENANCE_ACTIVE</strong><span>New jobs are paused. Existing durable jobs resume only after authorization and version checks.</span></div><StatusBadge tone="warning">PAUSED is a job state</StatusBadge></div>}

      <div className="chat-thread">
        <article className="message user-message">
          <div className="avatar avatar-user">MA</div>
          <div className="message-body"><div className="message-meta"><strong>Nguyễn Minh Anh</strong><span>14:32</span></div><p>Quy định về thời hạn và quy trình xét duyệt đề xuất mua sắm thiết bị làm việc năm 2025 như thế nào?</p></div>
        </article>

        <div className="processing-row" role="status"><span className="pulse-dot" />Completed · confidence 98.2%<span className="trace-id">trace: rag-2025-08921</span></div>

        <article className="message assistant-message">
          <div className="avatar avatar-ai"><Icon>✦</Icon></div>
          <div className="message-card">
            <div className="message-meta"><strong>{appConfig.name}</strong><StatusBadge tone={answer?.status === 'ANSWERED' ? 'success' : 'warning'}>{answer?.status || 'ANSWERED'}</StatusBadge><span>14:32</span></div>
            {answer ? <p>{answer.text || 'No supported answer was found in the authorized knowledge.'}</p> : role === 'anonymous' ? <p>Public knowledge is available below. Sign in to search company-internal sources.</p> : <>
              <p>The current policy requires the request to follow a three-step approval flow:</p>
              <ol className="answer-list">
                <li><strong>Prepare the request:</strong> include the business reason, specification and estimated budget.</li>
                <li><strong>Department review:</strong> the department owner verifies the need and budget before approval.</li>
                <li><strong>Purchasing review:</strong> Finance and Procurement validate the request against the current policy.</li>
              </ol>
            </>}

            <div className="citation-block">
              <button className="citation-toggle" type="button" aria-expanded={citationOpen} onClick={() => setCitationOpen((open) => !open)}><span><Icon>⌕</Icon> {citationOpen ? copy.hideSources : copy.sources(visibleCitations.length)}</span><span>{citationOpen ? '⌃' : '⌄'}</span></button>
              {citationOpen && <div className="citation-list">
                {visibleCitations.map((citation) => <div className="citation-row" key={citation.id}>
                  <div className={`file-icon file-${citation.type.toLowerCase()}`}>{citation.type}</div>
                  <div className="citation-text"><strong>{citation.title}</strong><span>{citation.id} · {citation.location}</span></div>
                  <StatusBadge tone="success">{citation.confidence}</StatusBadge>
                  <button className="text-button" type="button" onClick={() => onToast(role === 'anonymous' ? `Public preview reauthorized for ${citation.id}.` : `Preview reauthorized for ${citation.id}.`)}>Preview</button>
                </div>)}
              </div>}
            </div>
            <div className="message-actions"><button className="text-button" type="button" onClick={() => onToast('Answer copied to clipboard.')}>Copy</button><button className="icon-button" aria-label="Helpful answer" type="button" onClick={() => onToast('Positive feedback recorded.')}>♡</button><button className="icon-button" aria-label="Report answer" type="button" onClick={() => onToast('Feedback review request recorded.')}>⚑</button><span className="confidence-label">Calibrated confidence <strong>98.2%</strong></span></div>
          </div>
        </article>
      </div>

      <form className="prompt-box card" onSubmit={submit}>
        <label className="sr-only" htmlFor="chat-query">Ask your enterprise knowledge question</label>
        <textarea id="chat-query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={maintenance ? 'New questions are paused during maintenance.' : copy.placeholder} disabled={maintenance || busy} rows={2} />
        <div className="prompt-toolbar"><span className="helper-text"><Icon>⌁</Icon>{busy ? 'Waiting for the RAG answer...' : 'Sources are checked against current permissions before delivery.'}</span><button className="button button-primary send-button" type="submit" disabled={maintenance || busy || !query.trim()} aria-label="Send question"><Icon>↑</Icon></button></div>
      </form>
    </section>
  </div>
}

function DashboardView({ onNavigate }: { onNavigate: (view: View) => void }) {
  return <div className="content-stack">
    <header className="page-heading"><div><p className="eyebrow">System intelligence</p><h1>Admin overview</h1><p className="muted">Monitor RAG capacity, ingestion state and approved operational measures.</p></div><div className="heading-actions"><button className="button button-secondary" type="button">↓ Export report</button><button className="button button-primary" type="button" onClick={() => onNavigate('documents')}><Icon>＋</Icon>Upload document</button></div></header>
    <div className="metrics-grid">
      <Metric label="Active users" value="348" detail="+14% this month" tone="red" icon="♙" />
      <Metric label="Total documents" value="1,820" detail="18 departments" icon="▤" />
      <Metric label="Active knowledge" value="1,745" detail="95.8% indexed" icon="✓" />
      <Metric label="Awaiting review" value="15" detail="Needs action" tone="red" icon="!" />
      <Metric label="Chat questions" value="68,420" detail="+24% week on week" icon="✦" />
      <Metric label="SLA success" value="99.9%" detail="12 open incidents" icon="◷" />
    </div>
    <div className="dashboard-grid">
      <section className="card chart-card"><div className="section-heading"><div><h2>RAG query volume</h2><p className="muted">Direct chat and policy lookups over the last 7 days</p></div><StatusBadge tone="success">Live</StatusBadge></div><div className="bar-chart" aria-label="RAG query volume chart">{[54, 66, 78, 94, 72, 38, 28].map((height, index) => <div className="bar-group" key={index}><div className="bar-stack"><span className="bar-main" style={{ height: `${height}%` }} /><span className="bar-secondary" style={{ height: `${Math.max(12, height * 0.3)}%` }} /></div><span>{['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}</span></div>)}</div><div className="chart-note"><span>Peak window: <strong>14:00–16:30</strong></span><StatusBadge tone="success">Vector DB active</StatusBadge></div></section>
      <div className="dashboard-side"><InfoCard title="LLM cost & token usage" value="$214.50" detail="35.7% of $600 monthly limit" progress={36} /><InfoCard title="Average latency" value="310ms" detail="RAG 68ms · Generation 242ms" /><InfoCard title="Cache hit rate" value="84.8%" detail="Estimated saving $320/month" /></div>
    </div>
    <section className="card activity-card"><div className="section-heading"><div><h2>Recent knowledge activity</h2><p className="muted">Accountable document and ingestion events</p></div><button className="text-button" type="button" onClick={() => onNavigate('audit')}>View audit logs →</button></div><ActivityTable /></section>
  </div>
}

function Metric({ label, value, detail, icon, tone }: { label: string; value: string; detail: string; icon: string; tone?: 'red' }) {
  return <div className="metric-card card"><div className="metric-top"><span>{label}</span><span className={`metric-icon ${tone === 'red' ? 'metric-icon-red' : ''}`}>{icon}</span></div><strong>{value}</strong><small className={tone === 'red' ? 'text-red' : ''}>{detail}</small></div>
}

function InfoCard({ title, value, detail, progress }: { title: string; value: string; detail: string; progress?: number }) {
  return <section className="card info-card"><div className="info-card-title"><span>{title}</span><Icon>◈</Icon></div><strong>{value}</strong>{progress !== undefined && <div className="progress"><span style={{ width: `${progress}%` }} /></div>}<p className="muted">{detail}</p></section>
}

function ActivityTable() {
  return <div className="table-wrap"><table><thead><tr><th>Time</th><th>Document</th><th>Department</th><th>Action</th><th>Status</th></tr></thead><tbody>{documents.slice(0, 4).map((document, index) => <tr key={document.id}><td>{['10:45', '10:12', '09:30', '08:50'][index]} today</td><td><strong>{document.title}</strong><span className="table-subtitle">{document.id}</span></td><td><span className="soft-chip">{document.department}</span></td><td>{index === 1 ? 'Version approval' : index === 2 ? 'ACL update' : 'New ingestion'}</td><td><StatusBadge tone={document.state === 'ACTIVE' ? 'success' : 'warning'}>{document.state === 'ACTIVE' ? 'SUCCESS' : 'PENDING'}</StatusBadge></td></tr>)}</tbody></table></div>
}

function DocumentsView({ role, onToast, onNavigate }: { role: Role; onToast: (message: string) => void; onNavigate: (view: View) => void }) {
  const visibleDocuments = visibleDocumentsForRole(role)
  const [selectedId, setSelectedId] = useState(visibleDocuments[0]?.id ?? documents[0].id)
  const selected = visibleDocuments.find((document) => document.id === selectedId) ?? visibleDocuments[0] ?? documents[0]
  const canManage = roleCanManage(role)
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">Authorized knowledge</p><h1>{canManage ? 'Knowledge documents' : 'Permitted knowledge'}</h1><p className="muted">{canManage ? 'Manage indexed sources, versions and review state.' : 'Only published documents allowed for your identity are shown.'}</p></div><div className="heading-actions">{canManage && <><button className="button button-secondary" type="button">↓ Export CSV</button><button className="button button-primary" type="button" onClick={() => onToast('Upload flow is ready for the approved ingestion API.')}><Icon>＋</Icon>Upload document</button></>}</div></header><div className="summary-grid"><Metric label="Total documents" value="1,820" detail="Across 18 departments" icon="▤" /><Metric label="Active" value="1,745" detail="Published and retrievable" icon="✓" /><Metric label="Quarantined" value="15" detail="Two-stage review required" tone="red" icon="!" /><Metric label="Vector knowledge DB" value="14.6 GB" detail="Derived projection" icon="◈" /></div><div className="document-workspace"><section className="card document-list"><div className="filter-row"><label className="search-field"><Icon>⌕</Icon><input aria-label="Search documents" placeholder="Search document, ID or tag" /></label><select aria-label="Filter by status" defaultValue="all"><option value="all">All status</option><option value="active">Active</option><option value="quarantined">Quarantined</option></select><select aria-label="Filter by type" defaultValue="all"><option value="all">All formats</option><option value="pdf">PDF</option><option value="docx">DOCX</option><option value="xlsx">XLSX</option></select></div><div className="selection-toolbar"><span>{visibleDocuments.length} visible documents</span>{canManage ? <><button className="text-button" type="button" onClick={() => onToast('Re-index request queued with current checksum.')}>Re-index</button><button className="text-button danger-text" type="button" onClick={() => onToast('Deletion requires current permission, retention and legal-hold checks.')}>Delete</button></> : <span className="helper-text">Read-only access</span>}</div><div className="table-wrap document-table"><table><thead><tr><th aria-label="Select" /><th>Document</th><th>Department</th><th>Visibility</th><th>Status</th></tr></thead><tbody>{visibleDocuments.map((document) => <tr className={selected.id === document.id ? 'selected-row' : ''} key={document.id} onClick={() => setSelectedId(document.id)}><td><input type="checkbox" aria-label={`Select ${document.title}`} checked={selected.id === document.id} onChange={() => setSelectedId(document.id)} onClick={(event) => event.stopPropagation()} /></td><td><div className="file-cell"><span className={`file-icon file-${document.type.toLowerCase()}`}>{document.type}</span><div><strong>{document.title}</strong><span className="table-subtitle">{document.id}</span></div></div></td><td>{document.department}</td><td><span className="soft-chip">{document.visibility}</span></td><td><StatusBadge tone={document.state === 'ACTIVE' ? 'success' : 'warning'}>{document.state}</StatusBadge></td></tr>)}</tbody></table></div><div className="table-footer"><span>Showing 1–{visibleDocuments.length} permitted documents</span><span>‹ 1 ›</span></div></section><DocumentDetails document={selected} canManage={canManage} onToast={onToast} onNavigate={onNavigate} /></div></div>
}

function DocumentDetails({ document, canManage, onToast, onNavigate }: { document: typeof documents[number]; canManage: boolean; onToast: (message: string) => void; onNavigate: (view: View) => void }) {
  return <aside className="card detail-panel"><div className="detail-heading"><div className="file-cell"><span className={`file-icon file-${document.type.toLowerCase()}`}>{document.type}</span><div><strong>{document.title}</strong><span className="table-subtitle">{document.id}</span></div></div><button className="icon-button" aria-label="Close details" type="button" onClick={() => onToast('Detail panel remains available for the selected document.')}>×</button></div><div className="detail-tabs"><button className="active" type="button">Overview</button><button type="button">Versions (3)</button><button type="button">Access</button><button type="button">Vector RAG</button></div><div className="detail-section highlighted"><div className="detail-label">Security classification <StatusBadge tone="warning">{document.visibility}</StatusBadge></div><p>Only authorized principals may preview or download the current version. Explicit deny wins over role allow.</p></div><div className="detail-section"><div className="detail-label">Technical properties</div><div className="property-grid"><span>Size<strong>8.4 MB</strong></span><span>Version<strong>v2.1 current</strong></span><span>MIME<strong>application/{document.type.toLowerCase()}</strong></span><span>Chunks<strong>320 active</strong></span></div></div><div className="detail-section"><div className="detail-label">Vector RAG status <StatusBadge tone="success">100% parsed</StatusBadge></div><p className="muted">Qdrant is a derived projection. PostgreSQL and the policy service remain authoritative.</p></div><div className="detail-actions"><button className="button button-secondary" type="button" onClick={() => onToast(`Source preview reauthorized for ${document.id}.`)}>↧ Preview source</button>{canManage && <button className="button button-primary" type="button" onClick={() => onNavigate('approvals')}>Review lifecycle</button>}</div></aside>
}

function ReviewView({ onToast }: { onToast: (message: string) => void }) {
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">Document lifecycle</p><h1>Review & ingest</h1><p className="muted">Quarantine, two review decisions and index publication remain separate states.</p></div><StatusBadge tone="warning">15 awaiting review</StatusBadge></header><section className="card review-card"><div className="section-heading"><div><h2>Approval queue</h2><p className="muted">Every action requires a current authorization and writes an audit event.</p></div><button className="button button-secondary" type="button" onClick={() => onToast('Queue refreshed from the administrative API.')}>↻ Refresh</button></div><div className="review-list">{documents.slice(0, 4).map((document, index) => <div className="review-row" key={document.id}><div className={`file-icon file-${document.type.toLowerCase()}`}>{document.type}</div><div className="review-main"><strong>{document.title}</strong><span>{document.id} · Uploaded by {index % 2 === 0 ? 'Nguyễn Thị Lan' : 'Trần Minh'}</span></div><StatusBadge tone={document.state === 'QUARANTINED' ? 'warning' : 'success'}>{document.state === 'QUARANTINED' ? 'QUARANTINED' : 'READY'}</StatusBadge><button className="button button-secondary" type="button" onClick={() => onToast(`Review opened for ${document.id}.`)}>Open review</button></div>)}</div></section></div>
}

function UsersView({ onToast }: { onToast: (message: string) => void }) {
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">Identity & access</p><h1>Users & departments</h1><p className="muted">Account provisioning is admin-only; access requests never grant access by themselves.</p></div><button className="button button-primary" type="button" onClick={() => onToast('The account provisioning form is ready for the approved API.')}>＋ Add user</button></header><section className="card activity-card"><div className="section-heading"><div><h2>Enterprise identities</h2><p className="muted">Role and department are resolved by the trusted backend.</p></div><StatusBadge tone="success">348 active</StatusBadge></div><div className="table-wrap"><table><thead><tr><th>User</th><th>Role</th><th>Department</th><th>MFA</th><th>Status</th></tr></thead><tbody>{[['Nguyễn Minh Anh', 'employee', 'Finance'], ['Trần Minh', 'chairman', 'Executive'], ['Lê Thu Hà', 'website_manager', 'Operations'], ['Admin Enterprise', 'system_admin', 'Security']].map(([name, role, department]) => <tr key={name}><td><strong>{name}</strong><span className="table-subtitle">{name.toLowerCase().replaceAll(' ', '.')}@corp.internal</span></td><td><span className="soft-chip">{role}</span></td><td>{department}</td><td><StatusBadge tone="success">MFA active</StatusBadge></td><td><StatusBadge tone="success">ACTIVE</StatusBadge></td></tr>)}</tbody></table></div></section></div>
}

function AuditView({ onToast }: { onToast: (message: string) => void }) {
  return <div className="content-stack"><header className="page-heading"><div><p className="eyebrow">Privacy-safe operations</p><h1>Audit & monitoring</h1><p className="muted">Operational evidence is visible without exposing conversation bodies, raw prompts or source text.</p></div><button className="button button-secondary" type="button" onClick={() => onToast('Audit export requested with current filters.')}>↓ Export logs</button></header><section className="card activity-card"><div className="section-heading"><div><h2>Recent security events</h2><p className="muted">Correlation ID, policy decision and redacted metadata only.</p></div><StatusBadge tone="success">Operational</StatusBadge></div><ActivityTable /></section></div>
}

export function App() {
  const [role, setRole] = useState<Role>('employee')
  const [view, setView] = useState<View>('chat')
  const [language, setLanguage] = useState<'VI' | 'EN'>('EN')
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [maintenance, setMaintenance] = useState(false)
  const [toast, setToast] = useState('')
  const [conversationId, setConversationId] = useState<string>()
  const [queryBusy, setQueryBusy] = useState(false)
  const [liveAnswer, setLiveAnswer] = useState<QueryAnswer | null>(null)

  const canManage = roleCanManage(role)
  const canAdmin = roleCanAdmin(role)
  const currentRole = useMemo(() => roles.find((item) => item.id === role)!, [role])

  function notify(message: string) {
    setToast(message)
    window.setTimeout(() => setToast(''), 3200)
  }

  function navigate(nextView: View) {
    const item = navItems.find((nav) => nav.id === nextView)
    if (item?.adminOnly && !canAdmin) {
      notify('This area is limited to System Admin. The backend will enforce the same boundary.')
      return
    }
    if (item?.managementOnly && !canManage) {
      notify('This area is limited to Website Manager and System Admin.')
      return
    }
    if (nextView === 'documents' && !roleCanReadKnowledge(role)) {
      notify('Anonymous visitors can query only published PUBLIC knowledge through chat.')
      return
    }
    setView(nextView)
    setMobileNavOpen(false)
  }

  async function submitLiveQuery(query: string) {
    setQueryBusy(true)
    try {
      const activeConversation = conversationId ?? (await createConversation()).conversation_id
      setConversationId(activeConversation)
      const job = await submitMessage(activeConversation, query)
      const completed = await waitForQueryCompletion(job.job_id)
      setLiveAnswer(completed.answer ?? null)
      notify('Answer received from RAG with verified citations.')
    } catch (error) {
      notify(error instanceof Error ? error.message : 'The RAG query could not be completed.')
    } finally {
      setQueryBusy(false)
    }
  }

  function renderView() {
    if (view === 'chat') return <ChatView role={role} language={language} maintenance={maintenance} busy={queryBusy} answer={liveAnswer} onMaintenance={() => setMaintenance((active) => !active)} onSubmitQuery={submitLiveQuery} onToast={notify} />
    if (view === 'dashboard' && canManage) return <DashboardView onNavigate={navigate} />
    if (view === 'documents' && roleCanReadKnowledge(role)) return <DocumentsView role={role} onToast={notify} onNavigate={navigate} />
    if (view === 'approvals' && canManage) return <ReviewView onToast={notify} />
    if (view === 'users' && canAdmin) return <UsersView onToast={notify} />
    if (view === 'audit' && canAdmin) return <AuditView onToast={notify} />
    return <PermissionDenied onChat={() => navigate('chat')} />
  }

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNavOpen ? 'sidebar-open' : ''}`}>
      <div><div className="brand"><div className="brand-mark"><Icon>✦</Icon></div><div><strong>Enterprise AI</strong><span>Knowledge workspace</span></div></div><button className="button button-primary new-chat sidebar-new-chat" type="button" onClick={() => navigate('chat')}><Icon>＋</Icon>New chat</button><div className="nav-section"><p className="eyebrow">Workspace</p><nav aria-label="Main navigation">{navItems.filter((item) => item.id !== 'documents' || roleCanReadKnowledge(role)).filter((item) => !item.adminOnly || canAdmin).filter((item) => !item.managementOnly || canManage).map((item) => <button className={`nav-item ${view === item.id ? 'nav-item-active' : ''}`} key={item.id} type="button" onClick={() => navigate(item.id)}><Icon>{item.icon}</Icon><span>{item.label}</span>{item.id === 'approvals' && <span className="nav-count">15</span>}</button>)}</nav></div></div><div className="sidebar-bottom"><div className="role-summary"><div className="avatar avatar-user">{currentRole.shortLabel.slice(0, 2).toUpperCase()}</div><div><strong>{currentRole.label}</strong><span>{role === 'anonymous' ? 'Public session' : 'MFA verified session'}</span></div></div><button className="text-button" type="button" onClick={() => notify('Sign-out will be handled by the identity API.')}>Sign out</button></div>
    </aside>
    {mobileNavOpen && <button className="mobile-scrim" aria-label="Close navigation" type="button" onClick={() => setMobileNavOpen(false)} />}
    <div className="main-shell"><header className="topbar"><div className="topbar-left"><button className="mobile-menu" aria-label="Open navigation" type="button" onClick={() => setMobileNavOpen(true)}>☰</button><div className="breadcrumbs"><strong>{view === 'chat' ? 'Enterprise Knowledge AI' : 'Enterprise Admin Portal'}</strong><span>›</span><span>{navItems.find((item) => item.id === view)?.label}</span></div><StatusBadge tone="success">RAG cluster healthy</StatusBadge></div><div className="topbar-actions"><label className="role-preview">Preview role<select aria-label="Preview role" value={role} onChange={(event) => { setRole(event.target.value as Role); setView('chat') }}><option value="anonymous">anonymous</option><option value="employee">employee</option><option value="chairman">chairman</option><option value="website_manager">website_manager</option><option value="system_admin">system_admin</option></select></label><div className="language-switch" aria-label="Language"><button className={language === 'VI' ? 'active' : ''} type="button" onClick={() => setLanguage('VI')}>VI</button><button className={language === 'EN' ? 'active' : ''} type="button" onClick={() => setLanguage('EN')}>EN</button></div><button className="icon-button notification" aria-label="Notifications" type="button" onClick={() => notify('No new operational notifications.')}>♧</button><div className="topbar-profile"><div><strong>{currentRole.label}</strong><span>{canAdmin ? 'Full system scope' : canManage ? 'Business management scope' : 'Read scope from backend policy'}</span></div><div className="avatar avatar-primary">{currentRole.shortLabel.slice(0, 2).toUpperCase()}</div></div></div></header><main className="main-content">{renderView()}</main></div>
    {toast && <div className="toast" role="status">{toast}</div>}
  </div>
}
