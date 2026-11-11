import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { App } from './App'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith('/conversations')) return { ok: true, json: async () => ({ conversation_id: 'conv-test' }) }
    if (url.includes('/messages')) return { ok: true, json: async () => ({ job_id: 'job-test' }) }
    return {
      ok: true,
      json: async () => ({
        job_id: 'job-test',
        state: 'COMPLETED',
        answer: {
          status: 'ANSWERED',
          text: 'Live answer from the local RAG pipeline.',
          citations: [{ citation_id: 'c-1', document_id: 'doc-public', locator: { kind: 'PDF', page: 1 } }],
        },
      }),
    }
  }))
})

afterEach(() => vi.unstubAllGlobals())

function chooseRole(role: string) {
  fireEvent.change(screen.getByRole('combobox', { name: 'Preview role' }), {
    target: { value: role },
  })
}

describe('UI-001 role-aware enterprise workspace', () => {
  it('opens employees in the authorized chat workspace', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: 'How can I help today?' })).toBeInTheDocument()
    expect(screen.getAllByText('Employee')).not.toHaveLength(0)
    expect(screen.getByRole('button', { name: 'Knowledge chat' })).toBeInTheDocument()
  })

  it('keeps management navigation hidden from employees', () => {
    render(<App />)
    expect(screen.queryByRole('button', { name: 'Overview' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Review & ingest' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Users & access' })).not.toBeInTheDocument()
  })

  it('shows Website Manager website controls without system administration', () => {
    render(<App />)
    chooseRole('website_manager')
    expect(screen.getByRole('button', { name: 'Overview' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Review & ingest/ })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Users & access' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Audit & monitoring' })).not.toBeInTheDocument()
  })

  it('keeps Chairman in read-only knowledge navigation', () => {
    render(<App />)
    chooseRole('chairman')
    expect(screen.getByRole('button', { name: 'Knowledge documents' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Overview' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Review & ingest' })).not.toBeInTheDocument()
  })

  it('shows the complete administrative navigation only to System Admin', () => {
    render(<App />)
    chooseRole('system_admin')
    expect(screen.getByRole('button', { name: 'Overview' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Users & access' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Audit & monitoring' })).toBeInTheDocument()
  })

  it('limits anonymous citation details to PUBLIC sources', () => {
    render(<App />)
    chooseRole('anonymous')
    fireEvent.click(screen.getByRole('button', { name: /View 1 supporting source/ }))
    expect(screen.getByText('Bảng định mức trang thiết bị làm việc')).toBeInTheDocument()
    expect(screen.queryByText('Quy chế chi tiêu nội bộ và công tác phí 2025')).not.toBeInTheDocument()
  })

  it('keeps internal citation details available to an authenticated employee', () => {
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: /View 3 supporting sources/ }))
    expect(screen.getByText('Quy chế chi tiêu nội bộ và công tác phí 2025')).toBeInTheDocument()
    expect(screen.getByText('Hướng dẫn thực thi thanh toán')).toBeInTheDocument()
  })

  it('exposes maintenance control only to System Admin and pauses chat input', () => {
    render(<App />)
    chooseRole('system_admin')
    fireEvent.click(screen.getByRole('button', { name: 'Operational' }))
    expect(screen.getByRole('alert')).toHaveTextContent('MAINTENANCE_ACTIVE')
    expect(screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })).toBeDisabled()
  })

  it('submits a question as a durable-job notification', () => {
    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'What is the warranty?' } })
    fireEvent.submit(textbox.closest('form')!)
    expect(screen.getAllByRole('status').some((status) => status.textContent?.includes('durable job'))).toBe(true)
  })

  it('renders the answer returned by the backend RAG query job', async () => {
    render(<App />)
    const textbox = screen.getByRole('textbox', { name: 'Ask your enterprise knowledge question' })
    fireEvent.change(textbox, { target: { value: 'What is the purchasing policy?' } })
    fireEvent.submit(textbox.closest('form')!)
    await waitFor(() => expect(screen.getByText('Live answer from the local RAG pipeline.')).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /View 1 supporting source/ }))
    expect(screen.getByText('Document doc-public')).toBeInTheDocument()
  })

  it('switches the visible chat copy between English and Vietnamese', () => {
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'VI' }))
    expect(screen.getByRole('heading', { name: 'Tôi có thể giúp gì hôm nay?' })).toBeInTheDocument()
    expect(screen.getByText('Cuộc trò chuyện mới')).toBeInTheDocument()
  })
})
