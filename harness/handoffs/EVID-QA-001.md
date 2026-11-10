# Handoff — EVID-QA-001 / QA Agent

- Task ID: EVID-QA-001
- Agent owner: QA
- Status: PASS — MAIN FIX VERIFIED
- Contract version(s) used: Secure Retrieval v1.0; Answer & citation v1.0; Shared Contract Baseline v1.0; Chat/conversation/query-job v1.0 boundary
- Upstream dependencies checked: EVID-001 scope and acceptance; RAG-002 and PROMPT-001 are listed dependencies; CHAT-001 citation preview/download recheck boundary recorded
- Changed files: `tests/qa/evidence/test_behavior_component.py`, `tests/qa/evidence/test_contract_integration.py`, `tests/qa/evidence/test_e2e_operational.py`, `tests/qa/evidence/test_security_adversarial.py`, `harness/handoffs/EVID-QA-001.md`
- New/updated tests: 40 independent tests, exactly 10 per QA family
- Commands actually executed + exit status:
  - `/tmp/graphify-venv/bin/graphify query --graph graphify-out/graph.json --query "backend evidence citation retrieval source span ACTIVE version revoked authorization" --limit 20` — exit 0; 76 nodes found, output truncated to 59 nodes.
  - `/opt/homebrew/bin/python3 -m compileall -q tests/qa/evidence` — exit 0.
  - `/tmp/evid-qa.DYATC4/bin/python -m pytest --collect-only -q tests/qa/evidence` — PASS; 40 tests collected.
  - `/tmp/evid-qa.DYATC4/bin/python -m pytest -q tests/qa/evidence` — initial FAIL; 38 passed, 2 failed. Both failures were duplicate citation-ID cases.
  - `/tmp/evid-qa.DYATC4/bin/python -m pytest -q backend/tests/test_evidence.py backend/tests/test_dense_retrieval.py backend/tests/test_hybrid_retrieval.py tests/qa/evidence` — FAIL; 52 passed, 2 failed. Same duplicate citation-ID defect.
  - `/tmp/evid-qa.DYATC4/bin/python -m pytest -q tests/evaluation tests/security` — PASS; 61 passed.
  - `/tmp/evid-qa.DYATC4/bin/python -m pytest -q backend/tests tests/integration tests/evaluation tests/security tests/qa/evidence` — BLOCKED/FAIL collection; exit 2 with 6 collection errors because the temporary environment lacks declared `fastapi` and `httpx` packages.
  - `git diff --no-index --check /dev/null <each new file>` — PASS; no whitespace errors.
- Security implications (ACL, tenant, PII, injections, tools): Synthetic-only fixtures cover tenant mismatch, stale/current ACTIVE version checks, revocation, callback failure, duplicate evidence, no source leakage, untrusted evidence text, and source-download recheck. No network or API keys.
- Integration steps: Run the exact commands and results recorded below; then review any production defects without changing production code in this QA task.
- Known limitations / blockers with IDs: CHAT-001 preview/download endpoints are not implemented in this task; QA asserts the documented reauthorization boundary and validates the existing retrieval source-fetch recheck. Evidence relation matching remains lexical by the production shortcut.
- Suggested next READY task: CHAT-001 citation preview/download integration recheck tests, followed by EVAL-001 execution.
- Human approval required: Tech Lead review of the 40-case evidence package and any FAILs.

## Execution record

Overall QA result after Main fix: PASS; 40/40 QA tests pass. Production code, task registry, contracts, frontend, infrastructure, commits, and pushes were unchanged by this QA task.

### Production defect

Initial QA found that `backend/app/evidence/verifier.py` checked
`citation_id in evidence_by_id` while the map was still empty, allowing
duplicate IDs to overwrite earlier evidence. Main changed the verifier to
populate and validate the map in one pass; duplicates now return the required
`ACCESS_DENIED`/`MALFORMED_EVIDENCE` result. Revalidation: 40/40 passed.
