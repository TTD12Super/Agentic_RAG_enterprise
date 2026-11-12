import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { App, renderSafeMarkdown } from './App'
import { clearAccessToken, createConversation, streamMessage, waitForQueryCompletion } from './api/client'

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

function streamResponse(body: string) {
  const encoder = new TextEncoder()
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(body))
      controller.close()
    },
  })
  return { ok: true, status: 200, body: stream } as unknown as Response
}

function conversationResponse() {
  return json({
    conversation_id: 'conv-test',
    messages: [
      { message_id: 'message-user', role: 'user', content: 'What is the purchasing policy?', created_at: '2026-01-01T00:00:00Z' },
      { message_id: 'message-answer', role: 'assistant', content: 'Live answer from the backend RAG pipeline.', created_at: '2026-01-01T00:00:01Z', answer_id: 'answer-test', status: 'ANSWERED', citations: [{ citation_id: 'citation-test', document_id: 'doc-public', title: 'Equipment Purchasing Policy', filename: 'equipment-purchasing-policy.pdf', locator: { kind: 'PDF', page: 1 } }] },
    ],
  })
}

beforeEach(() => {
  clearAccessToken()
  window.history.replaceState({}, '', '/chat')
  window.sessionStorage.clear()
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    if (url.endsWith('/auth/sign-in')) return json({ access_token: 'token-test', principal: String((init?.body || '')).includes('admin@example.com') ? adminPrincipal : principal })
    if (url.endsWith('/auth/sign-out')) return json({})
    if (url.endsWith('/conversations?limit=20&offset=0')) return json({ schema_version: '1.0', items: [{ conversation_id: 'conv-test', title: 'Purchasing policy', created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:01:00Z', message_count: 2 }], pagination: { limit: 20, offset: 0, total: 1, has_more: false } })
    if (url.endsWith('/conversations') && init?.method === 'POST') return json({ conversation_id: 'conv-test' })
    if (url.includes('/conversations/conv-test/messages/stream')) return streamResponse([
      'event: message_start\ndata: {"message_id":"message-answer"}\n\n',
      'event: token\ndata: {"delta":"Live answer "}\n\n',
      'event: token\ndata: {"delta":"from the backend RAG pipeline."}\n\n',
      'event: citation\ndata: {"citation_id":"citation-test","document_id":"doc-public","title":"Equipment Purchasing Policy","filename":"equipment-purchasing-policy.pdf","locator":{"kind":"PDF","page":1}}\n\n',
      'event: done\ndata: {"answer":{"answer_id":"answer-test","status":"ANSWERED","text":"Live answer from the backend RAG pipeline.","citations":[{"citation_id":"citation-test","document_id":"doc-public","title":"Equipment Purchasing Policy","filename":"equipment-purchasing-policy.pdf","locator":{"kind":"PDF","page":1}}]}}\n\n',
    ].join(''))
    if (url.includes('/query-jobs/job-test')) return json({ job_id: 'job-test', conversation_id: 'conv-test', state: 'COMPLETED', answer: { answer_id: 'answer-test', status: 'ANSWERED', text: 'Live answer from the backend RAG pipeline.', citations: [{ citation_id: 'citation-test', document_id: 'doc-public', locator: { kind: 'PDF', page: 1 } }] } })
    if (url.endsWith('/conversations/conv-test')) return conversationResponse()
    if (url.includes('/citations/citation-test/preview')) return json({ preview: 'Authorized preview from backend.' })
    if (url.includes('/answers/answer-test/citations/citation-test/download')) return json({ code: 'CITATION_REVOKED' }, false)
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

afterEach(() => {
  clearAccessToken()
  window.history.replaceState({}, '', '/chat')
  window.localStorage.clear()
  window.sessionStorage.clear()
  vi.unstubAllGlobals()
})

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

  it('creates a conversation from either New chat control', async () => {
    render(<App />)
    fireEvent.click(screen.getAllByRole('button', { name: 'New chat' })[0])
    await waitFor(() => expect(screen.getByText('Active now')).toBeInTheDocument())
    fireEvent.click(screen.getAllByRole('button', { name: 'New chat' })[1])
    await waitFor(() => expect(vi.mocked(fetch).mock.calls.filter(([input, init]) => String(input).endsWith('/conversations') && init?.method === 'POST')).toHaveLength(2))

    const createCall = vi.mocked(fetch).mock.calls.find(([input, init]) => (
      String(input).endsWith('/conversations') && init?.method === 'POST'
    ))
    expect(createCall).toBeDefined()
  })

  it('lists saved conversations and restores the selected conversation', async () => {
    render(<App />)
    await waitFor(() => expect(screen.getByRole('button', { name: /Purchasing policy/ })).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /Purchasing policy/ }))
    await waitFor(() => expect(screen.getByText('What is the purchasing policy?')).toBeInTheDocument())
    expect(vi.mocked(fetch).mock.calls.some(([input]) => String(input).endsWith('/conversations/conv-test'))).toBe(true)
  })

  it('submits a live query and renders conversation, citation and preview data', async () => {
    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'What is the purchasing policy?' } })
    fireEvent.submit(textbox.closest('form')!)
    await waitFor(() => expect(screen.getByText('Live answer from the backend RAG pipeline.')).toBeInTheDocument())
    const calls = vi.mocked(fetch).mock.calls
    expect(calls.some(([input, init]) => String(input).includes('/conversations/conv-test/messages/stream') && init?.method === 'POST')).toBe(true)
    fireEvent.click(screen.getByRole('button', { name: /View 1 citation/ }))
    expect(screen.getByText('Equipment Purchasing Policy')).toBeInTheDocument()
    expect(screen.getByText(/equipment-purchasing-policy\.pdf/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Preview' }))
    await waitFor(() => expect(screen.getByText('Authorized preview from backend.')).toBeInTheDocument())
  })

  it('calls the real citation download endpoint and exposes a revoked source safely', async () => {
    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'Download this source' } })
    fireEvent.submit(textbox.closest('form')!)
    await waitFor(() => expect(screen.getByText('Live answer from the backend RAG pipeline.')).toBeInTheDocument())

    fireEvent.click(screen.getByRole('button', { name: /View 1 citation/ }))
    fireEvent.click(screen.getByRole('button', { name: 'Download original' }))

    await waitFor(() => expect(screen.getByText('This source is no longer available for your session.')).toBeInTheDocument())
    expect(screen.getByRole('button', { name: 'Retry download' })).toBeInTheDocument()
    expect(vi.mocked(fetch).mock.calls.some(([input]) => String(input).includes('/answers/answer-test/citations/citation-test/download'))).toBe(true)
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
    expect(screen.getByRole('button', { name: 'Users & access' })).toBeInTheDocument()
    expect(screen.queryByText('manager@example.com')).not.toBeInTheDocument()
    expect(screen.getAllByText('website_manager').length).toBeGreaterThan(0)
  })

  it('opens and closes the real conversation history drawer', async () => {
    render(<App />)
    await waitFor(() => expect(screen.getByText('Purchasing policy')).toBeInTheDocument())
    fireEvent.click(screen.getByText('History', { exact: true }))
    const historyScrim = document.querySelector<HTMLButtonElement>('button.history-scrim')
    expect(historyScrim).not.toBeNull()
    expect(screen.getByText('Only conversation metadata is listed here. Message bodies load after you select a conversation.')).toBeInTheDocument()
    fireEvent.click(historyScrim!)
    expect(document.querySelector('button.history-scrim')).toBeNull()
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

  it('turns a hung backend request into a visible retryable timeout', async () => {
    vi.useFakeTimers()
    vi.stubGlobal('fetch', vi.fn((_input: RequestInfo | URL, init?: RequestInit) => new Promise<Response>((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')))
    })))
    try {
      const pending = createConversation()
      const assertion = expect(pending).rejects.toMatchObject({ code: 'REQUEST_TIMEOUT', retryable: true })
      await vi.advanceTimersByTimeAsync(15_000)
      await assertion
    } finally {
      vi.useRealTimers()
    }
  })

  it('accumulates token events and resolves the done answer', async () => {
    const tokens: string[] = []
    vi.stubGlobal('fetch', vi.fn(async () => streamResponse([
      'event: message_start\ndata: {"message_id":"message-stream"}\n\n',
      'event: token\ndata: {"delta":"Hello"}\n\n',
      'event: token\ndata: {"delta":" world"}\n\n',
      'event: done\ndata: {"status":"ANSWERED","text":"Hello world","citations":[]}\n\n',
    ].join(''))))

    const answer = await streamMessage('conv-test', 'Say hello', { onToken: (token) => tokens.push(token) })

    expect(tokens).toEqual(['Hello', ' world'])
    expect(answer).toMatchObject({ status: 'ANSWERED', text: 'Hello world', citations: [] })
  })

  it('surfaces a streamed error event as an ApiError', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => streamResponse('event: error\ndata: {"code":"RAG_FAILED","message":"Retrieval failed"}\n\n')))

    await expect(streamMessage('conv-test', 'Fail safely')).rejects.toMatchObject({ code: 'RAG_FAILED', message: 'Retrieval failed' })
  })

  it('restores the saved conversation messages from the backend after reload', async () => {
    window.localStorage.setItem('enterprise-rag.conversation-id', 'conv-test')
    render(<App />)

    await waitFor(() => expect(screen.getByText('What is the purchasing policy?')).toBeInTheDocument())
    expect(screen.getByText('Live answer from the backend RAG pipeline.')).toBeInTheDocument()
    expect(vi.mocked(fetch).mock.calls.some(([input, init]) => String(input).endsWith('/conversations/conv-test') && !init?.method)).toBe(true)
  })

  it('restores citations and answer actions with saved conversation messages', async () => {
    window.localStorage.setItem('enterprise-rag.conversation-id', 'conv-test')
    render(<App />)

    await waitFor(() => expect(screen.getByRole('button', { name: /View 1 citation/ })).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /View 1 citation/ }))
    expect(screen.getByRole('button', { name: 'Preview' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Download original' })).toBeInTheDocument()
  })

  it('turns a missing saved conversation into a clean empty state', async () => {
    window.localStorage.setItem('enterprise-rag.conversation-id', 'conv-gone')
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).endsWith('/conversations/conv-gone')) return json({ code: 'CONVERSATION_NOT_FOUND' }, false)
      return json({})
    }))

    render(<App />)
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Start a conversation' })).toBeInTheDocument())
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(window.localStorage.getItem('enterprise-rag.conversation-id')).toBeNull()
    expect(screen.getAllByRole('button', { name: 'New chat' })).toHaveLength(3)
  })

  it('offers retry and reconnect when streaming cannot reach the backend', async () => {
    let streamAttempts = 0
    let conversationCreates = 0
    const streamUrls: string[] = []
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.endsWith('/conversations') && init?.method === 'POST') {
        conversationCreates += 1
        return json({ conversation_id: `conv-${conversationCreates}` })
      }
      if (url.includes('/messages/stream')) {
        streamAttempts += 1
        streamUrls.push(url)
        if (streamAttempts === 1) throw new TypeError('network down')
        return streamResponse('event: done\ndata: {"status":"ANSWERED","text":"Recovered answer","citations":[]}\n\n')
      }
      return json({})
    }))

    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'Retry this question' } })
    fireEvent.submit(textbox.closest('form')!)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument())
    expect(screen.getByRole('button', { name: 'Reconnect' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Retry' }))
    await waitFor(() => expect(screen.getByText('Recovered answer')).toBeInTheDocument())
    expect(screen.getAllByText('Retry this question')).toHaveLength(1)
    expect(streamAttempts).toBe(2)
    expect(conversationCreates).toBe(2)
    expect(streamUrls[1]).toContain('/conversations/conv-2/messages/stream')
  })

  it('creates a fresh conversation and replays the query when the old one is gone', async () => {
    let conversationsCreated = 0
    const streamUrls: string[] = []
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.endsWith('/conversations') && init?.method === 'POST') {
        conversationsCreated += 1
        return json({ conversation_id: `conv-${conversationsCreated}` })
      }
      if (url.includes('/messages/stream')) {
        streamUrls.push(url)
        if (streamUrls.length === 1) return json({ code: 'CONVERSATION_NOT_FOUND', message: 'Conversation no longer exists.' }, false)
        return streamResponse('event: done\ndata: {"status":"ANSWERED","text":"Recovered after restart","citations":[]}\n\n')
      }
      return json({})
    }))

    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'Replay after restart' } })
    fireEvent.submit(textbox.closest('form')!)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument())

    fireEvent.click(screen.getByRole('button', { name: 'Retry' }))
    await waitFor(() => expect(screen.getByText('Recovered after restart')).toBeInTheDocument())
    expect(conversationsCreated).toBe(2)
    expect(streamUrls[1]).toContain('/conversations/conv-2/messages/stream')
    expect(screen.getAllByText('Replay after restart')).toHaveLength(1)
    expect(window.localStorage.getItem('enterprise-rag.conversation-id')).toBe('conv-2')
  })

  it('clears a stale saved conversation without showing a backend error', async () => {
    window.localStorage.setItem('enterprise-rag.conversation-id', 'conv-stale')
    let created = 0
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.endsWith('/conversations/conv-stale')) return json({ code: 'CONVERSATION_NOT_FOUND' }, false)
      if (url.endsWith('/conversations') && init?.method === 'POST') {
        created += 1
        return json({ conversation_id: `conv-fresh-${created}` })
      }
      return json({})
    }))

    render(<App />)
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Start a conversation' })).toBeInTheDocument())
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(created).toBe(0)
    expect(window.localStorage.getItem('enterprise-rag.conversation-id')).toBeNull()
  })

  it('shows an explicit cancelled state when Stop interrupts a stream', async () => {
    let controller: ReadableStreamDefaultController<Uint8Array> | undefined
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.endsWith('/conversations') && init?.method === 'POST') return json({ conversation_id: 'conv-test' })
      if (url.includes('/messages/stream')) {
        const encoder = new TextEncoder()
        const body = new ReadableStream<Uint8Array>({ start(next) { controller = next; next.enqueue(encoder.encode('event: message_start\ndata: {"message_id":"message-stream"}\n\n')) } })
        init?.signal?.addEventListener('abort', () => controller?.close(), { once: true })
        return { ok: true, status: 200, body } as unknown as Response
      }
      return json({})
    }))

    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'Stop this question' } })
    fireEvent.submit(textbox.closest('form')!)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Stop generating' })).toBeInTheDocument())
    expect(screen.getByText(/Generating an answer from authorized sources/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Stop generating' }))
    await waitFor(() => expect(screen.getByText('Generation cancelled')).toBeInTheDocument())
    expect(screen.getAllByText('CANCELLED').length).toBeGreaterThan(0)
  })

  it('keeps management navigation hidden for an anonymous session', () => {
    render(<App />)
    expect(screen.queryByRole('button', { name: 'Overview' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Users & access' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Knowledge chat' })).toBeInTheDocument()
  })

  it('shows an explicit sign-in guard for a direct anonymous admin URL', () => {
    window.history.replaceState({}, '', '/admin')
    render(<App />)

    expect(screen.getByRole('heading', { name: 'Sign in to enter Admin' })).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: 'Sign in' }).length).toBeGreaterThan(0)
    expect(vi.mocked(fetch).mock.calls.some(([input]) => String(input).endsWith('/dashboard'))).toBe(false)
  })

  it('clears sign-in errors when switching to request access', async () => {
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).endsWith('/auth/sign-in')) return json({ message: 'Invalid authentication credentials.' }, false)
      return json({})
    }))
    render(<App />)

    fireEvent.click(screen.getAllByRole('button', { name: 'Sign in' })[0])
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'wrong@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrong' } })
    fireEvent.submit(screen.getByLabelText('Email').closest('form')!)
    await waitFor(() => expect(screen.getByText('Invalid authentication credentials.')).toBeInTheDocument())

    fireEvent.click(screen.getAllByRole('button', { name: 'Request access' })[0])
    expect(screen.getByRole('heading', { name: 'Request access securely' })).toBeInTheDocument()
    expect(screen.queryByText('Invalid authentication credentials.')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Continue with Google/ })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Submit request/ })).toBeDisabled()
  })

  it('marks the unavailable language switch instead of exposing a no-op toggle', () => {
    render(<App />)

    expect(screen.getByRole('button', { name: 'Language switch unavailable' })).toBeDisabled()
    expect(screen.queryByRole('button', { name: 'VI' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'EN' })).not.toBeInTheDocument()
  })

  it('renders the supported markdown subset without executing raw HTML or unsafe links', () => {
    render(<div>{renderSafeMarkdown('# Policy\n\n- **Finance** approval\n\n<script>alert(1)</script>\n\n[Unsafe](javascript:alert(1))')}</div>)

    expect(screen.getByRole('heading', { name: 'Policy' })).toBeInTheDocument()
    expect(screen.getByRole('listitem')).toHaveTextContent('Finance approval')
    expect(screen.queryByRole('link')).not.toBeInTheDocument()
    expect(screen.queryByRole('script')).not.toBeInTheDocument()
    expect(screen.getByText('<script>alert(1)</script>')).toBeInTheDocument()
  })
})
