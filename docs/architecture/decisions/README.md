# Architecture Decision Records (ADR)

Status convention: Proposed → Accepted / Rejected → Superseded.
ADR records context, decision, alternatives, consequences, owner approval and affected contracts. A new agent must not silently override an Accepted ADR.

Create new decisions using `ADR-TEMPLATE.md`, then update affected contracts and tests after approval.

## Current architecture review state

- ARCH-OVERVIEW-001 is the current draft architecture map.
- ADR-0001 through ADR-0005 are revised proposals aligned with that overview; none is Accepted.
- The proposed Rust Core + Python worker boundary does not authorize a repository migration.
- New decisions are required for the Rust/Python trust boundary, queue/scheduler priority, durable maintenance pause/resume and selected data/cloud topology.
- Until an ADR is accepted, implementation agents must preserve the current repository layout and report the dependent task as blocked.

The owner-provided Q1–Q34 proposal parameters are centralized in [`../../requirements/owner-decision-baseline.md`](../../requirements/owner-decision-baseline.md). They align the drafts but do not by themselves accept an ADR or authorize deployment.

The current unresolved decision points and their affected tasks are tracked in [`DECISION-REGISTER.md`](DECISION-REGISTER.md). The register records blockers without selecting an option on behalf of the Project Owner.
