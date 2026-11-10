# Structure-aware ingestion design

1. Upload to quarantine with malware and signature checks.
2. Detect format, parse via Docling (OCR only when needed), extract headings, tables, page/layout provenance.
3. Build tree: document → section(parent) → child chunk; use token-aware hybrid chunking, preserving context and table headers.
4. Attach document_id, version_id, tenant_id, classification, ACL policy ref, page/span and text hash to every child.
5. Produce dense embeddings and sparse keyword/BM25 index separately; stage atomically.
6. Validate missing pages, invalid chunks, no-ACL chunks, indexing mismatches and sample retrieval.
7. Publish ACTIVE version with controlled invalidate of caches; old version becomes SUPERSEDED.

## Suggested experiments (not fixed best parameters)
Child size 300–600 tokens; overlap 0–80; parent section bounded by allowed evidence window. Measure retrieval quality and cost before tuning.

No uploaded material may be assumed benign because it was provided by an admin.

## Owner-provided ingestion limits

- Accept `.pdf`, `.docx` and `.xlsx` only; reject `.doc` and `.xls`.
- Enforce a 200,000,000-byte upload limit, streamed to private object storage with byte-count, MIME/magic-byte, checksum and malware checks.
- PDF supports text and Vietnamese/English OCR up to 2,000 pages. DOCX is limited to two million extracted words. XLSX is limited to 50 sheets, 200,000 populated rows per workbook and 200 columns per sheet.
- Do not execute macros, scripts or formulas. Record OCR quality and fail closed when extracted content is not trustworthy.
- Target child chunks at 500–800 tokens with 10–15% overlap, capped near 120 tokens; parent sections target 2,000 tokens.
- Preserve PDF page/section, DOCX heading/paragraph/table and XLSX sheet/cell-range provenance without inventing locations.
