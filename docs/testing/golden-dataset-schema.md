# Golden dataset schema (synthetic)

One JSONL record per question:
```json
{"case_id":"case-001","query":"Sản phẩm A bảo hành bao lâu?","principal_fixture":"employee-sales","tenant_id":"tenant-a","expected_source_spans":[{"document_id":"doc-public","version_id":"v1","page":2}],"expected_status":"ANSWERED","expected_facts":["12 months"],"tags":["warranty","public"]}
```

Include: permission-negative examples, document version conflicts, no-answer, indirect injection, multi-hop and long tables. Do not put real PII or proprietary files in checked-in fixtures.

## Owner-provided dataset composition

The initial synthetic dataset should contain at least 200 cases:

- 70% Vietnamese and 30% English.
- 70% simple and 30% complex.
- At least 50 permission-negative cases and at least 30 unanswerable cases; overlap is allowed.
- Include conflicting versions, explicit-deny cases, cross-tenant cases, scanned PDF OCR, Excel cell-range citations, indirect prompt injection, multi-hop questions and long tables.

Proposed quality targets are Recall@10 ≥90%, citation accuracy ≥95%, citation grounding precision ≥95%, answer correctness ≥90%, no-answer accuracy ≥90% and zero unauthorized retrieval. These are targets until Project Owner approval after benchmark evidence.
