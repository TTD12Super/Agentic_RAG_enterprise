import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { App } from './App'

describe('application shell', () => {
  it('renders the contract-bound workspace entry point', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: 'Enterprise Agentic RAG' })).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('Frontend baseline ready')
    expect(screen.getByText('Backend authorization is authoritative')).toBeInTheDocument()
  })

  it('exposes the canonical role identifiers without granting permissions', () => {
    render(<App />)

    for (const role of ['system_admin', 'website_manager', 'employee', 'chairman']) {
      expect(screen.getByText(role)).toBeInTheDocument()
    }
  })
})
