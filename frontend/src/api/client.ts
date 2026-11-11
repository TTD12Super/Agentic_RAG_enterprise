import { appConfig } from '../config'

export type QueryAnswer = {
  status: string
  text: string
  citations: Array<{
    citation_id: string
    document_id: string
    locator?: { kind?: string; page?: number; source_span?: { start: number; end: number } }
  }>
}

export type QueryJob = {
  job_id: string
  state: string
  answer?: QueryAnswer
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    ...init,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...init.headers },
  })
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(body.detail?.message || body.detail || `Request failed (${response.status})`)
  return body as T
}

export function createConversation() {
  return request<{ conversation_id: string }>('/conversations', { method: 'POST', body: '{}' })
}

export function submitMessage(conversationId: string, query: string) {
  return request<{ job_id: string }>(`/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Idempotency-Key': `web-${Date.now()}-${Math.random().toString(36).slice(2)}` },
    body: JSON.stringify({ query }),
  })
}

export async function waitForQueryCompletion(jobId: string): Promise<QueryJob> {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    const job = await request<QueryJob>(`/query-jobs/${jobId}`)
    if (job.state === 'COMPLETED') return job
    if (job.state === 'FAILED' || job.state === 'CANCELLED') throw new Error(`Query ${job.state.toLowerCase()}`)
    await new Promise((resolve) => window.setTimeout(resolve, 100))
  }
  throw new Error('Query timed out while waiting for completion')
}
