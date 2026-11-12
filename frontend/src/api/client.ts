import { appConfig } from '../config'

// Keep the short-lived demo token in memory; production should use an HttpOnly session cookie.
let accessToken: string | null = null

export type Principal = {
  user_id: string
  tenant_id: string
  roles: string[]
  groups: string[]
  department_ids: string[]
  session_id: string
  auth_time: string
}

export type QueryCitation = {
  citation_id: string
  tenant_id?: string
  document_id: string
  title?: string
  document_title?: string
  filename?: string
  document_name?: string
  version_id?: string
  locator?: {
    kind?: string
    page?: number
    source_span?: { start: number; end: number }
    heading?: string
    paragraph?: number
    sheet?: string
    cell_range?: string
  }
}

export type QueryAnswer = {
  answer_id?: string
  status: string
  text: string
  citations: QueryCitation[]
  reason_codes?: string[]
}

export type StreamMessageStart = {
  message_id?: string
  conversation_id?: string
  created_at?: string
}

export type StreamHandlers = {
  onStart?: (event: StreamMessageStart) => void
  onToken?: (delta: string) => void
  onCitation?: (citation: QueryCitation) => void
  onDone?: (answer: QueryAnswer) => void
}

export type QueryJob = {
  job_id: string
  conversation_id: string
  state: string
  maintenance?: string | null
  answer?: QueryAnswer
  error?: { code?: string; retryable?: boolean }
}

export type Pagination = {
  limit: number
  offset: number
  total: number
  has_more: boolean
}

export type DocumentRecord = {
  document_id: string
  title: string
  classification: string
  status: string
  owner_department_id?: string | null
  current_version_id?: string | null
}

export type DocumentVersion = {
  document_id: string
  version_id: string
  version_number: number
  status: string
  sha256: string
  source_uri: string
  job_id: string
  approvals: Array<{
    stage: number
    decision: string
    reviewer_id: string
    expires_at: string
  }>
}

export type IngestionJob = {
  job_id: string
  document_id: string
  version_id: string
  state: string
  current_stage: string
  attempt: number
  error_code?: string | null
}

export type FeedbackRecord = {
  feedback_id: string
  answer_id: string
  rating: 'POSITIVE' | 'NEGATIVE'
  created_at: string
}

export type AccessGrant = {
  action: 'document:read' | 'source:download'
  effect: 'ALLOW' | 'DENY'
  user_id?: string
  role?: string
  group?: string
  department_id?: string
}

export type ApprovalRecord = {
  document_id: string
  version_id: string
  version_number: number
  status: string
  sha256: string
  source_uri: string
  job_id: string
  approvals: Array<{
    stage: number
    decision: string
    reviewer_id: string
    expires_at: string
  }>
}

export type AuditRecord = {
  event_id: string
  event: string
  action: string
  outcome: string
  decision?: string | null
  request_id: string
  traceparent: string
  trace_id: string
  principal_id?: string | null
  tenant_id?: string | null
  code?: string | null
  occurred_at: string
  safe_metadata: Record<string, unknown>
}

export type PagedResponse<T> = {
  schema_version?: string
  items: T[]
  pagination: Pagination
}

export type ConversationMessage = {
  message_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  answer_id?: string | null
  status?: string | null
  citations?: QueryCitation[]
  reason_codes?: string[]
}

export type Conversation = {
  conversation_id: string
  messages: ConversationMessage[]
}

export type ConversationSummary = {
  conversation_id: string
  title?: string | null
  created_at: string
  updated_at: string
  message_count: number
}

export type AccessRequestResponse = {
  request_id: string
  status: string
  email_confirmation?: string
}

export type AccessRequestMetadata = {
  request_id: string
  status: string
  full_name: string
  email: string
  department: string
  reason: string
  created_at: string
  reviewed_at?: string | null
  reviewed_by?: string | null
  access_granted: boolean
}


export type DashboardMetric<T = unknown> = {
  value: T | null
  unit: string
  status: string
  available: boolean
  is_estimate: boolean
  provenance: string
  measurement_period: { label?: string; start?: string; end?: string }
  reason?: string
}

export type Dashboard = {
  schema_version?: string
  users?: DashboardMetric<{ total?: number; active?: number; by_role?: Record<string, number> }>
  documents?: DashboardMetric<{ total?: number; current_versions?: number; by_status?: Record<string, number> }>
  usage?: DashboardMetric<{ requests?: number; by_state?: Record<string, number> }>
  ingestion?: DashboardMetric<{ jobs?: number; failed?: number; by_state?: Record<string, number> }>
  latency?: DashboardMetric<number>
  cost?: DashboardMetric<number>
  evaluation?: DashboardMetric<number>
  cache_hit_rate?: DashboardMetric<number>
}

export type UserRecord = {
  user_id: string
  tenant_id: string
  email: string
  roles: string[]
  department_ids: string[]
  active: boolean
}

export type DepartmentRecord = {
  department_id: string
  tenant_id: string
  name: string
  active: boolean
}

export function getAccessToken(): string | null {
  return accessToken
}

function setAccessToken(token: string): void {
  accessToken = token
}

export function clearAccessToken(): void {
  accessToken = null
}

export class ApiError extends Error {
  readonly code?: string
  readonly retryable: boolean
  readonly status: number

  constructor(message: string, options: { code?: string; retryable?: boolean; status?: number } = {}) {
    super(message)
    this.name = 'ApiError'
    this.code = options.code
    this.retryable = options.retryable ?? false
    this.status = options.status ?? 0
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body && !(init.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 15_000)
  let response: Response
  try {
    response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
      ...init,
      credentials: 'include',
      headers,
      signal: controller.signal,
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('The backend request timed out.', { code: 'REQUEST_TIMEOUT', retryable: true })
    }
    throw new ApiError('Could not reach the backend. Check that it is running.', { code: 'NETWORK_UNAVAILABLE', retryable: true })
  } finally {
    window.clearTimeout(timeout)
  }
  const body = await response.json().catch(() => ({})) as Record<string, unknown>
  if (!response.ok) {
    const detail = body.detail
    const detailObject = typeof detail === 'object' && detail !== null ? detail as { code?: string; message?: string; retryable?: boolean } : undefined
    const detailMessage = typeof detail === 'object' && detail !== null
      ? (detail as { message?: string }).message
      : detail
    const message = body.message || detailMessage || body.code || `Request failed (${response.status})`
    throw new ApiError(String(message), {
      code: typeof body.code === 'string' ? body.code : detailObject?.code,
      retryable: body.retryable === true || detailObject?.retryable === true || response.status === 401 || response.status === 408 || response.status === 429 || response.status >= 500,
      status: response.status,
    })
  }
  return body as T
}

function readStreamPayload(value: unknown): Record<string, unknown> | string {
  if (typeof value !== 'string') return value as Record<string, unknown>
  try {
    return JSON.parse(value) as Record<string, unknown>
  } catch {
    return value
  }
}

function objectValue(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? value as Record<string, unknown> : {}
}

function answerFromStream(value: unknown, text: string, citations: QueryCitation[]): QueryAnswer {
  const payload = objectValue(value)
  const candidate = objectValue(payload.answer ?? payload.final_answer ?? value)
  const candidateCitations = Array.isArray(candidate.citations) ? candidate.citations as QueryCitation[] : citations
  return {
    answer_id: typeof candidate.answer_id === 'string' ? candidate.answer_id : undefined,
    status: typeof candidate.status === 'string' ? candidate.status : 'ANSWERED',
    text: typeof candidate.text === 'string' ? candidate.text : text,
    citations: candidateCitations,
    reason_codes: Array.isArray(candidate.reason_codes) ? candidate.reason_codes as string[] : undefined,
  }
}

function streamError(value: unknown, status = 0): ApiError {
  const payload = objectValue(value)
  const detail = objectValue(payload.detail)
  const detailMessage = typeof payload.detail === 'string' ? payload.detail : detail.message
  return new ApiError(String(payload.message || detailMessage || payload.code || 'The streaming query failed.'), {
    code: typeof payload.code === 'string' ? payload.code : undefined,
    retryable: payload.retryable === true || status === 401 || status === 408 || status === 429 || status >= 500,
    status,
  })
}

export async function streamMessage(
  conversationId: string,
  query: string,
  handlers: StreamHandlers = {},
  signal?: AbortSignal,
): Promise<QueryAnswer> {
  const headers = new Headers({
    Accept: 'text/event-stream',
    'Content-Type': 'application/json',
    'Idempotency-Key': `web-${Date.now()}-${Math.random().toString(36).slice(2)}`,
  })
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response: Response
  try {
    response = await fetch(`${appConfig.apiBaseUrl}/conversations/${conversationId}/messages/stream`, {
      method: 'POST',
      credentials: 'include',
      headers,
      body: JSON.stringify({ query }),
      signal,
    })
  } catch (error) {
    if (signal?.aborted) throw error
    throw new ApiError('Could not reach the backend. Check that it is running.', { code: 'NETWORK_UNAVAILABLE', retryable: true })
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw streamError(body, response.status)
  }
  if (!response.body) throw new ApiError('The backend did not return a streaming body.', { code: 'STREAM_BODY_MISSING' })

  const reader = response.body.getReader()
  const cancelReader = () => { void reader.cancel() }
  signal?.addEventListener('abort', cancelReader, { once: true })
  const decoder = new TextDecoder()
  let buffer = ''
  let eventName = ''
  let dataLines: string[] = []
  let answer: QueryAnswer | undefined
  let text = ''
  const citations: QueryCitation[] = []

  const dispatch = () => {
    if (!eventName && !dataLines.length) return
    const raw = dataLines.join('\n')
    const payload = readStreamPayload(raw)
    switch (eventName) {
      case 'message_start':
        handlers.onStart?.(objectValue(payload) as StreamMessageStart)
        break
      case 'token': {
        const tokenPayload = objectValue(payload)
        const delta = typeof payload === 'string' ? payload : tokenPayload.delta ?? tokenPayload.token ?? tokenPayload.text
        if (typeof delta === 'string') {
          text += delta
          handlers.onToken?.(delta)
        }
        break
      }
      case 'citation': {
        const citation = objectValue(payload).citation ?? payload
        if (objectValue(citation).citation_id) {
          citations.push(citation as QueryCitation)
          handlers.onCitation?.(citation as QueryCitation)
        }
        break
      }
      case 'done':
        answer = answerFromStream(payload, text, citations)
        handlers.onDone?.(answer)
        break
      case 'error':
        throw streamError(payload)
      default:
        break
    }
    eventName = ''
    dataLines = []
  }

  try {
    while (true) {
      const chunk = await reader.read()
      buffer += decoder.decode(chunk.value || new Uint8Array(), { stream: !chunk.done })
      const lines = buffer.split(/\r?\n/)
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line) { dispatch(); continue }
        if (line.startsWith('event:')) eventName = line.slice(6).trim()
        else if (line.startsWith('data:')) dataLines.push(line.slice(5).trimStart())
      }
      if (chunk.done) break
    }
    if (buffer) {
      if (buffer.startsWith('event:')) eventName = buffer.slice(6).trim()
      else if (buffer.startsWith('data:')) dataLines.push(buffer.slice(5).trimStart())
    }
    dispatch()
    if (!answer) throw new ApiError('The backend stream ended without a done event.', { code: 'STREAM_DONE_MISSING' })
    return answer
  } finally {
    signal?.removeEventListener('abort', cancelReader)
  }
}

export async function signIn(email: string, password: string, mfaCode?: string): Promise<Principal> {
  const payload = await request<{ access_token: string; principal: Principal }>('/auth/sign-in', {
    method: 'POST',
    body: JSON.stringify({ email, password, ...(mfaCode ? { mfa_code: mfaCode } : {}) }),
  })
  setAccessToken(payload.access_token)
  return payload.principal
}

export function getCurrentIdentity(): Promise<Principal> {
  return request<Principal>('/auth/me')
}

export async function signOut(): Promise<void> {
  try {
    await request<void>('/auth/sign-out', { method: 'POST' })
  } finally {
    clearAccessToken()
  }
}

export function submitAccessRequest(payload: {
  full_name: string
  email: string
  department: string
  reason: string
  consent: boolean
}) {
  return request<AccessRequestResponse>('/access-requests', {
    method: 'POST',
    headers: { 'Idempotency-Key': `access-request-${Date.now()}-${Math.random().toString(36).slice(2)}` },
    body: JSON.stringify(payload),
  })
}

export function createConversation() {
  return request<{ conversation_id: string }>('/conversations', { method: 'POST', body: '{}' })
}

export function getConversation(conversationId: string) {
  return request<Conversation>(`/conversations/${conversationId}`)
}

export function getConversations(limit = 20, offset = 0, search = '') {
  const query = new URLSearchParams({ limit: String(limit), offset: String(offset) })
  if (search.trim()) query.set('search', search.trim())
  return request<PagedResponse<ConversationSummary>>(`/conversations?${query.toString()}`)
}

export function submitMessage(conversationId: string, query: string) {
  return request<{ job_id: string }>(`/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Idempotency-Key': `web-${Date.now()}-${Math.random().toString(36).slice(2)}` },
    body: JSON.stringify({ query }),
  })
}

export async function waitForQueryCompletion(
  jobId: string,
  options: { deadlineMs?: number; initialDelayMs?: number; maxDelayMs?: number } = {},
): Promise<QueryJob> {
  const deadline = Date.now() + (options.deadlineMs ?? 30_000)
  const maxDelay = options.maxDelayMs ?? 1_500
  let delay = options.initialDelayMs ?? 100
  const pendingStates = new Set(['QUEUED', 'RUNNING', 'PAUSED', 'RETRY_SCHEDULED'])

  while (Date.now() < deadline) {
    let job: QueryJob
    try {
      job = await request<QueryJob>(`/query-jobs/${jobId}`)
    } catch (error) {
      if (!(error instanceof ApiError) || !error.retryable) throw error
      if (Date.now() >= deadline) break
      await new Promise((resolve) => window.setTimeout(resolve, Math.min(delay, deadline - Date.now())))
      delay = Math.min(maxDelay, Math.ceil(delay * 1.7))
      continue
    }
    if (job.state === 'COMPLETED') return job
    if (job.state === 'FAILED' || job.state === 'CANCELLED') {
      if (job.state === 'FAILED' && job.error?.retryable) {
        const remaining = deadline - Date.now()
        if (remaining <= 0) break
        await new Promise((resolve) => window.setTimeout(resolve, Math.min(delay, remaining)))
        delay = Math.min(maxDelay, Math.ceil(delay * 1.7))
        continue
      }
      throw new ApiError(job.error?.code || `Query ${job.state.toLowerCase()}`, {
        code: job.error?.code,
        retryable: job.error?.retryable === true,
      })
    }
    if (!pendingStates.has(job.state)) throw new ApiError(`Unknown query state: ${job.state}`, { code: 'QUERY_STATE_INVALID' })
    const remaining = deadline - Date.now()
    if (remaining <= 0) break
    await new Promise((resolve) => window.setTimeout(resolve, Math.min(delay, remaining)))
    delay = Math.min(maxDelay, Math.ceil(delay * 1.7))
  }
  throw new ApiError('Query timed out while waiting for completion', { code: 'QUERY_TIMEOUT', retryable: true })
}

export function previewCitation(answerId: string, citationId: string) {
  return request<{ preview?: string; citation?: QueryCitation }>(
    `/answers/${encodeURIComponent(answerId)}/citations/${encodeURIComponent(citationId)}/preview`,
  )
}

export async function downloadCitation(answerId: string, citationId: string): Promise<{ blob: Blob; filename?: string }> {
  const headers = new Headers()
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  let response: Response
  try {
    response = await fetch(`${appConfig.apiBaseUrl}/answers/${encodeURIComponent(answerId)}/citations/${encodeURIComponent(citationId)}/download`, {
      credentials: 'include',
      headers,
    })
  } catch {
    throw new ApiError('Could not reach the backend. Check that it is running.', { code: 'NETWORK_UNAVAILABLE', retryable: true })
  }
  if (!response.ok) {
    if ([401, 403, 404, 410].includes(response.status)) {
      throw new ApiError('This source is no longer available for your session.', { code: 'CITATION_UNAVAILABLE', status: response.status })
    }
    throw new ApiError('The source download failed. Retry this download.', {
      code: 'CITATION_DOWNLOAD_FAILED',
      retryable: response.status === 408 || response.status === 429 || response.status >= 500,
      status: response.status,
    })
  }
  const disposition = response.headers.get('content-disposition') || ''
  const encodedName = disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1]
  const plainName = disposition.match(/filename="?([^";]+)"?/i)?.[1]
  const filename = decodeURIComponent(encodedName || plainName || '').replace(/[\\/]/g, '').trim() || undefined
  return { blob: await response.blob(), filename }
}

export function submitFeedback(answerId: string, rating: 'POSITIVE' | 'NEGATIVE', comment?: string) {
  return request<{ feedback_id: string }>(`/answers/${encodeURIComponent(answerId)}/feedback`, {
    method: 'POST',
    headers: { 'Idempotency-Key': `feedback-${answerId}-${rating}` },
    body: JSON.stringify({ rating, ...(comment ? { comment } : {}) }),
  })
}

export function getDashboard() {
  return request<Dashboard>('/dashboard')
}

export function getDocuments(limit = 20, offset = 0) {
  return request<PagedResponse<DocumentRecord>>(`/documents?limit=${limit}&offset=${offset}`)
}

export function getDocument(documentId: string) {
  return request<DocumentRecord>(`/documents/${encodeURIComponent(documentId)}`)
}

export function getDocumentVersions(documentId: string) {
  return request<DocumentVersion[]>(`/documents/${encodeURIComponent(documentId)}/versions`)
}

export function getIngestionJob(jobId: string) {
  return request<IngestionJob>(`/ingestion-jobs/${encodeURIComponent(jobId)}`)
}

function mutationHeaders(idempotencyKey: string): HeadersInit {
  return { 'Idempotency-Key': idempotencyKey }
}

export function reviewDocumentVersion(documentId: string, versionId: string, stage: 1 | 2, decision: 'APPROVE' | 'REJECT' = 'APPROVE') {
  return request<DocumentVersion>(`/documents/${encodeURIComponent(documentId)}/versions/${encodeURIComponent(versionId)}/approve`, {
    method: 'POST',
    headers: mutationHeaders(`review-${documentId}-${versionId}-${stage}-${decision}-${Date.now()}`),
    body: JSON.stringify({ stage, decision }),
  })
}

export function publishDocumentVersion(documentId: string, versionId: string) {
  return request<DocumentVersion>(`/documents/${encodeURIComponent(documentId)}/versions/${encodeURIComponent(versionId)}/publish`, {
    method: 'POST',
    headers: mutationHeaders(`publish-${documentId}-${versionId}-${Date.now()}`),
    body: '{}',
  })
}

export function revokeDocumentVersion(documentId: string, versionId: string) {
  return request<DocumentVersion>(`/documents/${encodeURIComponent(documentId)}/versions/${encodeURIComponent(versionId)}/revoke`, {
    method: 'POST',
    headers: mutationHeaders(`revoke-${documentId}-${versionId}-${Date.now()}`),
    body: '{}',
  })
}

export function deleteDocument(documentId: string) {
  return request<void>(`/documents/${encodeURIComponent(documentId)}`, { method: 'DELETE' })
}

export function permanentlyDeleteDocument(documentId: string, retentionExpired: boolean, legalHold: boolean) {
  return request<void>(`/documents/${encodeURIComponent(documentId)}/permanent-delete`, {
    method: 'POST',
    headers: mutationHeaders(`permanent-delete-${documentId}-${Date.now()}`),
    body: JSON.stringify({ retention_expired: retentionExpired, legal_hold: legalHold }),
  })
}

export function updateDocumentAccess(documentId: string, grants: AccessGrant[]) {
  return request<{ document_id: string; grants: AccessGrant[] }>(`/documents/${encodeURIComponent(documentId)}/access`, {
    method: 'PUT',
    headers: mutationHeaders(`access-${documentId}-${Date.now()}`),
    body: JSON.stringify({ grants }),
  })
}

export function uploadMetadataDocument(payload: {
  title: string
  filename: string
  source_uri: string
  sha256: string
  size_bytes: number
  mime_type: string
  classification: 'PUBLIC' | 'INTERNAL'
  owner_department_id?: string
}) {
  return request<IngestionJob>('/documents', {
    method: 'POST',
    headers: mutationHeaders(`upload-${Date.now()}-${Math.random().toString(36).slice(2)}`),
    body: JSON.stringify(payload),
  })
}

export function getApprovals(limit = 20, offset = 0) {
  return request<PagedResponse<ApprovalRecord>>(`/approvals?limit=${limit}&offset=${offset}`)
}

export function getAuditEvents(limit = 50, offset = 0) {
  return request<PagedResponse<AuditRecord>>(`/audit?limit=${limit}&offset=${offset}`)
}

export function getUsers() {
  return request<{ users: UserRecord[] }>('/users')
}

export function getDepartments() {
  return request<{ departments: DepartmentRecord[] }>('/departments')
}

export function getAccessRequests(status = 'PENDING_ADMIN_REVIEW', limit = 20, offset = 0) {
  const query = new URLSearchParams({ status, limit: String(limit), offset: String(offset) })
  return request<PagedResponse<AccessRequestMetadata> & { filter: { status: string } }>(`/access-requests?${query.toString()}`)
}

export function reviewAccessRequest(requestId: string, decision: 'APPROVE' | 'REJECT') {
  return request<AccessRequestMetadata>(`/access-requests/${encodeURIComponent(requestId)}/review`, {
    method: 'POST',
    headers: mutationHeaders(`access-request-review-${requestId}-${Date.now()}`),
    body: JSON.stringify({ decision }),
  })
}

export function createUser(payload: { email: string; password: string; roles: string[]; department_ids: string[]; mfa_code?: string }) {
  return request<UserRecord>('/users', {
    method: 'POST',
    headers: mutationHeaders(`user-create-${Date.now()}-${Math.random().toString(36).slice(2)}`),
    body: JSON.stringify(payload),
  })
}

export function updateUser(userId: string, payload: { active?: boolean; roles?: string[]; department_ids?: string[] }) {
  return request<{ user: UserRecord }>(`/users/${encodeURIComponent(userId)}`, { method: 'PATCH', body: JSON.stringify(payload) })
}

export function activateUser(userId: string) {
  return request<UserRecord>(`/users/${encodeURIComponent(userId)}/activate`, {
    method: 'POST',
    headers: mutationHeaders(`activate-${userId}-${Date.now()}`),
    body: '{}',
  })
}

export function createDepartment(name: string, active = true) {
  return request<{ department: DepartmentRecord }>('/departments', { method: 'POST', body: JSON.stringify({ name, active }) })
}

export function updateDepartment(departmentId: string, name: string, active: boolean) {
  return request<{ department: DepartmentRecord }>(`/departments/${encodeURIComponent(departmentId)}`, { method: 'PATCH', body: JSON.stringify({ name, active }) })
}

export function getFeedback(limit = 50, offset = 0) {
  return request<PagedResponse<FeedbackRecord>>(`/feedback/review?limit=${limit}&offset=${offset}`)
}
