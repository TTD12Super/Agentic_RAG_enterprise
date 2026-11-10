# Runtime prompt templates

These Markdown files document prompts the **application** may use. They are not Codex development-agent instructions. Keep system/developer messages separate from retrieved user/document/tool data in the LLM API.

Version prompts and regression-test changes. Authorization remains external to the prompt.

## Owner-provided prompt governance

- Git files are the prompt source of truth; the database stores active-version metadata and audit references only.
- Planner, router and tool outputs must validate dedicated JSON Schemas before runtime use.
- Every answer records prompt version, model version, retrieval configuration version and policy version.
- Promotion requires the Technical Owner and an authorized reviewer, followed by Golden Dataset, citation, security and prompt-injection regression tests.
- The runtime tool registry is limited to `search_documents`, `read_authorized_chunk` and `get_document_metadata`.
