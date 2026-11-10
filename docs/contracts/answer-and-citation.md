# Answer & citation contract (v1.0)

The normative citation-location, version-binding and source reauthorization rules are defined in [`v1-baseline.md`](v1-baseline.md).

## Answer
```json
{"answer":"...","status":"ANSWERED","citations":[{"citation_id":"c-1","document_id":"doc-42","version_id":"v-2","page":4,"source_span":{"start":101,"end":412},"evidence_snapshot_hash":"hex","chunk_id":"chunk-77"}],"missing_information":[],"traceparent":"00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01","policy_epoch":42}
```
Allowed status: ANSWERED, PARTIAL, INSUFFICIENT_EVIDENCE, ACCESS_DENIED, ERROR.

## Verification
- Historical citation metadata remains linked to its original version; if that version is no longer ACTIVE, do not return its excerpt or file. Return a safe unavailable indication after the current access check; never silently substitute a newer version.
- Each factual company claim maps to one or more authorized, ACTIVE source spans.
- Check page/span/source version exists and current principal may view it.
- Disagreement in sources becomes a disclosed conflict or human review, not fabricated harmonization.
- Citation link endpoint rechecks `document:read`/`source:download` on each fetch.
- `PARTIAL` and `INSUFFICIENT_EVIDENCE` are first-class valid outcomes.

## Owner-provided answer policy

- Answer in the user's language unless explicitly requested otherwise.
- For conflicting sources, prefer approved/effective authoritative material and the newest ACTIVE version; if conflict remains, disclose both sources.
- Partial evidence produces a qualified partial answer; no sufficient evidence produces `INSUFFICIENT_EVIDENCE`.
- Citation details are collapsed by default but a visible source indicator remains available. Preview and download recheck current authorization.
