# EVID-001 — Main Agent review

## Decision

`ACCEPTED`

The evidence verifier is accepted for the provider-neutral boundary. It
requires an authoritative authorization attestation for the exact tenant,
document, version and ACTIVE current head, rejects revoked/stale citations,
distinguishes supported/unsupported/conflicting/partial outcomes, and does not
return source text in denied results.

## Evidence

- Focused implementation tests: `8 passed`.
- Required QA matrix: initial `38 passed, 2 failed`; after the duplicate-ID
  fail-closed fix, `40 passed`.
- Combined backend/integration/evaluation/security/QA run: `363 passed,
  2 skipped`.
- Duplicate citation IDs now fail as malformed before authorization/evidence
  evaluation; this prevents overwrite-based ambiguity.

## Limits

Claim support is lexical and not semantic entailment. CHAT-001 must reauthorize
every citation preview/download request against the current principal, policy,
tenant, exact version and revocation state.
