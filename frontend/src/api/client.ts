import { appConfig } from '../config'

const TOKEN_KEY = 'enterprise-rag-access-token'

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
}

export type Conversation = {
  conversation_id: string
  messages: ConversationMessage[]
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
  try {
    return window.sessionStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

function setAccessToken(token: string): void {
  window.sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearAccessToken(): void {
  window.sessionStorage.removeItem(TOKEN_KEY)
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

  const response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    ...init,
    credentials: 'include',
    headers,
  })
  const body = await response.json().catch(() => ({})) as Record<string, unknown>
  if (!response.ok) {
    const detail = body.detail
    const detailMessage = typeof detail === 'object' && detail !== null
      ? (detail as { message?: string }).message
      : detail
    const message = body.message || detailMessage || body.code || `Request failed (${response.status})`
    throw new ApiError(String(message), {
      code: typeof body.code === 'string' ? body.code : undefined,
      retryable: body.retryable === true,
      status: response.status,
    })
  }
  return body as T
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

export function createConversation() {
  return request<{ conversation_id: string }>('/conversations', { method: 'POST', body: '{}' })
}

export function getConversation(conversationId: string) {
  return request<Conversation>(`/conversations/${conversationId}`)
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
