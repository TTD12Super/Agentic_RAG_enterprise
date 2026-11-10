import { appConfig } from './config'
import './styles.css'

const supportedRoles = ['system_admin', 'website_manager', 'employee', 'chairman'] as const

export function App() {
  return (
    <main className="app-shell">
      <section className="hero" aria-labelledby="app-title">
        <p className="eyebrow">Enterprise knowledge workspace</p>
        <h1 id="app-title">{appConfig.name}</h1>
        <p className="lede">
          A contract-first application shell for authorized enterprise knowledge chat.
        </p>
        <div className="status" role="status">
          <span className="status-dot" aria-hidden="true" />
          Frontend baseline ready
        </div>
      </section>

      <section className="workspace" aria-labelledby="workspace-title">
        <div>
          <p className="eyebrow">MVP starting point</p>
          <h2 id="workspace-title">Authorized knowledge chat</h2>
          <p>
            Chat, citations, document actions and role-aware screens will be connected to the
            approved <code>/api/v1</code> contracts in later tasks.
          </p>
        </div>
        <div className="boundary" aria-label="Implementation boundaries">
          <span>Backend authorization is authoritative</span>
          <span>Durable-job polling</span>
          <span>No token streaming in MVP</span>
        </div>
      </section>

      <section className="roles" aria-labelledby="roles-title">
        <p className="eyebrow">Canonical roles</p>
        <h2 id="roles-title">Role-aware views are contract-bound</h2>
        <div className="role-list">
          {supportedRoles.map((role) => (
            <span className="role-chip" key={role}>
              {role}
            </span>
          ))}
        </div>
      </section>
    </main>
  )
}
