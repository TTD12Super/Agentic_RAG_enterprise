import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { App } from './App'
import { waitForQueryCompletion } from './api/client'

const principal = {
  user_id: 'user-manager',
  tenant_id: 'tenant-test',
  roles: ['website_manager'],
  groups: [],
  department_ids: ['dept-1'],
  session_id: 'session-test',
  auth_time: '2026-01-01T00:00:00Z',
}

const adminPrincipal = { ...principal, user_id: 'user-admin', roles: ['system_admin'] }

function json(body: unknown, ok = true) {
  return { ok, status: ok ? 200 : 404, json: async () => body } as Response
}

function conversationResponse() {
  return json({
    conversation_id: 'conv-test',
    messages: [
      { message_id: 'message-user', role: 'user', content: 'What is the purchasing policy?', created_at: '2026-01-01T00:00:00Z' },
      { message_id: 'message-answer', role: 'assistant', content: 'Live answer from the backend RAG pipeline.', created_at: '2026-01-01T00:00:01Z' },
    ],
  })
}

beforeEach(() => {
  window.sessionStorage.clear()
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    if (url.endsWith('/auth/sign-in')) return json({ access_token: 'token-test', principal: String((init?.body || '')).includes('admin@example.com') ? adminPrincipal : principal })
    if (url.endsWith('/auth/sign-out')) return json({})
    if (url.endsWith('/conversations') && init?.method === 'POST') return json({ conversation_id: 'conv-test' })
    if (url.includes('/conversations/conv-test/messages')) return json({ job_id: 'job-test' })
    if (url.includes('/query-jobs/job-test')) return json({ job_id: 'job-test', conversation_id: 'conv-test', state: 'COMPLETED', answer: { answer_id: 'answer-test', status: 'ANSWERED', text: 'Live answer from the backend RAG pipeline.', citations: [{ citation_id: 'citation-test', document_id: 'doc-public', locator: { kind: 'PDF', page: 1 } }] } })
    if (url.endsWith('/conversations/conv-test')) return conversationResponse()
    if (url.includes('/citations/citation-test/preview')) return json({ preview: 'Authorized preview from backend.' })
    if (url.includes('/answers/answer-test/feedback')) return json({ feedback_id: 'feedback-test' })
    if (url.endsWith('/dashboard')) return json({ schema_version: '1.0', users: { value: { total: 2, active: 2 }, unit: 'users', status: 'MEASURED', available: true, is_estimate: false, provenance: 'identity_store', measurement_period: {} }, documents: { value: { total: 3 }, unit: 'documents', status: 'MEASURED', available: true, is_estimate: false, provenance: 'ingestion', measurement_period: {} }, usage: { value: { requests: 5 }, unit: 'requests', status: 'MEASURED', available: true, is_estimate: false, provenance: 'chat.repository', measurement_period: {} }, ingestion: { value: { jobs: 1 }, unit: 'jobs', status: 'MEASURED', available: true, is_estimate: false, provenance: 'ingestion', measurement_period: {} }, latency: { value: null, unit: 'milliseconds', status: 'UNAVAILABLE', available: false, is_estimate: false, provenance: 'telemetry', measurement_period: {}, reason: 'LATENCY_TELEMETRY_UNAVAILABLE' }, cost: { value: null, unit: 'USD', status: 'UNAVAILABLE', available: false, is_estimate: false, provenance: 'telemetry', measurement_period: {}, reason: 'PROVIDER_COST_UNAVAILABLE' }, evaluation: { value: null, unit: 'score', status: 'UNAVAILABLE', available: false, is_estimate: false, provenance: 'evaluation', measurement_period: {}, reason: 'EVALUATION_UNAVAILABLE' } })
    if (url.endsWith('/users')) return json({ users: [{ ...principal, email: 'manager@example.com', active: true }] })
    if (url.endsWith('/departments')) return json({ departments: [{ department_id: 'dept-1', tenant_id: 'tenant-test', name: 'Operations', active: true }] })
    if (url.endsWith('/documents?limit=20&offset=0')) return json({ schema_version: '1.0', items: [{ document_id: 'document-test', title: 'Backend document', classification: 'PUBLIC', status: 'ACTIVE', owner_department_id: 'dept-1', current_version_id: 'version-test' }], pagination: { limit: 20, offset: 0, total: 1, has_more: false } })
    if (url.endsWith('/approvals?limit=20&offset=0')) return json({ schema_version: '1.0', items: [{ document_id: 'document-test', version_id: 'version-test', version_number: 1, status: 'PENDING_REVIEW_2', sha256: 'a'.repeat(64), source_uri: 'private://test', job_id: 'ingestion-test', approvals: [{ stage: 1, decision: 'APPROVED', reviewer_id: 'reviewer-test', expires_at: '2026-01-01T00:30:00Z' }] }], pagination: { limit: 20, offset: 0, total: 1, has_more: false } })
    if (url.endsWith('/audit?limit=50&offset=0')) return json({ schema_version: '1.0', items: [{ event_id: 'event-test', event: 'ADMIN_SUCCESS', action: 'admin:document:list', outcome: 'SUCCESS', decision: 'ALLOW', request_id: 'request-test', traceparent: '00-test', trace_id: 'trace-test', principal_id: 'user-manager', tenant_id: 'tenant-test', code: 'DOCUMENTS_LISTED', occurred_at: '2026-01-01T00:00:00Z', safe_metadata: { route: 'admin:document:list' } }], pagination: { limit: 50, offset: 0, total: 1, has_more: false } })
    return json({})
  }))
})

afterEach(() => vi.unstubAllGlobals())

async function signInAsManager(email = 'manager@example.com') {
  fireEvent.click(screen.getAllByRole('button', { name: 'Sign in' })[0])
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: email } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password' } })
  fireEvent.submit(screen.getByLabelText('Email').closest('form')!)
  const role = email.startsWith('admin') ? 'system_admin' : 'website_manager'
  await waitFor(() => expect(screen.getAllByText(role).length).toBeGreaterThan(0))
}

describe('frontend/backend integration', () => {
  it('starts empty and does not render business fixtures', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: 'Start a conversation' })).toBeInTheDocument()
    expect(screen.getAllByText('Public session').length).toBeGreaterThan(0)
    expect(screen.queryByText('1,820')).not.toBeInTheDocument()
    expect(screen.queryByText('Q4 expense policy review')).not.toBeInTheDocument()
  })

  it('submits a live query and renders conversation, citation and preview data', async () => {
    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'What is the purchasing policy?' } })
    fireEvent.submit(textbox.closest('form')!)
    await waitFor(() => expect(screen.getByText('Live answer from the backend RAG pipeline.')).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /View 1 citation/ }))
    expect(screen.getByText('doc-public')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Preview' }))
    await waitFor(() => expect(screen.getByText('Authorized preview from backend.')).toBeInTheDocument())
  })

  it('sends feedback through the backend answer endpoint', async () => {
    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'What is the purchasing policy?' } })
    fireEvent.submit(textbox.closest('form')!)
    await waitFor(() => expect(screen.getByText('Live answer from the backend RAG pipeline.')).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: 'Helpful answer' }))
    await waitFor(() => expect(screen.getByText('Feedback recorded by the backend.')).toBeInTheDocument())
  })

  it('uses backend identity instead of a client role selector', async () => {
    render(<App />)
    await signInAsManager()
    expect(screen.queryByRole('combobox', { name: 'Preview role' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Overview' })).toBeInTheDocument()
    expect(screen.queryByText('manager@example.com')).not.toBeInTheDocument()
    expect(screen.getAllByText('website_manager').length).toBeGreaterThan(0)
  })

  it('renders dashboard metrics returned by the backend and unavailable telemetry honestly', async () => {
    render(<App />)
    await signInAsManager()
    fireEvent.click(screen.getByRole('button', { name: 'Overview' }))
    await waitFor(() => expect(screen.getByText('Admin overview')).toBeInTheDocument())
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('No backend measurement')).toBeInTheDocument()
    expect(screen.getByText('No time-series data')).toBeInTheDocument()
  })

  it('renders actual users and departments from backend endpoints', async () => {
    render(<App />)
    await signInAsManager('admin@example.com')
    fireEvent.click(screen.getByRole('button', { name: 'Users & access' }))
    await waitFor(() => expect(screen.getByText('manager@example.com')).toBeInTheDocument())
    expect(screen.getByText('Operations')).toBeInTheDocument()
  })

  it('renders documents, approvals and audit records from backend endpoints', async () => {
    render(<App />)
    await signInAsManager()
    fireEvent.click(screen.getByRole('button', { name: 'Knowledge documents' }))
    await waitFor(() => expect(screen.getByText('Backend document')).toBeInTheDocument())
    expect(screen.getByText('PUBLIC')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Review & ingest' }))
    await waitFor(() => expect(screen.getByText('PENDING_REVIEW_2')).toBeInTheDocument())
    expect(screen.getByText(/Stage 1: APPROVED/)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Audit & monitoring' }))
    await waitFor(() => expect(screen.getByText('ADMIN_SUCCESS')).toBeInTheDocument())
    expect(screen.getByText('DOCUMENTS_LISTED')).toBeInTheDocument()
  })

  it('polls transient query states and retryable failures until completion', async () => {
    const responses = [
      json({ job_id: 'job-test', conversation_id: 'conv-test', state: 'QUEUED' }),
      json({ job_id: 'job-test', conversation_id: 'conv-test', state: 'RUNNING' }),
      json({ code: 'TEMPORARY', message: 'Retry later', retryable: true }, false),
      json({ job_id: 'job-test', conversation_id: 'conv-test', state: 'PAUSED' }),
      json({ job_id: 'job-test', conversation_id: 'conv-test', state: 'FAILED', error: { code: 'UPSTREAM_RETRYABLE', retryable: true } }),
      json({ job_id: 'job-test', conversation_id: 'conv-test', state: 'RETRY_SCHEDULED' }),
      json({ job_id: 'job-test', conversation_id: 'conv-test', state: 'COMPLETED', answer: { status: 'ANSWERED', text: 'done', citations: [] } }),
    ]
    const fetchMock = vi.fn(async () => responses.shift()!)
    vi.stubGlobal('fetch', fetchMock)

    const result = await waitForQueryCompletion('job-test', { deadlineMs: 1_000, initialDelayMs: 1, maxDelayMs: 2 })

    expect(result.state).toBe('COMPLETED')
    expect(fetchMock).toHaveBeenCalledTimes(7)
  })

  it('keeps management navigation hidden for an anonymous session', () => {
    render(<App />)
    expect(screen.queryByRole('button', { name: 'Overview' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Users & access' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Knowledge chat' })).toBeInTheDocument()
  })
})
