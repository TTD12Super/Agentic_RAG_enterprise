# GUARD-001 — Main Agent review

## Decision

`ACCEPTED`

The guardrail boundary is accepted as defense-in-depth. It normalizes and
bounds input, detects direct/indirect injection, redacts high-confidence
secrets/PII, keeps tools non-authoritative, and requires citation-backed output
or safe abstention.

## Evidence

- Guardrail implementation tests: `8 passed`.
- Required QA matrix: `40 passed` (`10` per family).
- Full backend/integration/evaluation/security suite: `315 passed, 2 skipped`.
- Main closed the educational-context bypass edge: educational framing no
  longer suppresses a matched injection pattern.

## Limits

Lexical grounding and heuristic redaction are not semantic verification or a
complete DLP engine. Backend authorization, provider egress policy and tool
execution checks remain authoritative and must be rechecked downstream.
