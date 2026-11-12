# UI implementation boundary

The files under `docs/design/UI:UX reference/` are visual references supplied by the Project Owner. They do not define API state names or authorization identifiers.

For implementation, the Frontend Agent must follow the approved contract v1.0:

- canonical roles: `system_admin`, `website_manager`, `employee`, `chairman`;
- maintenance is the system mode `MAINTENANCE_ACTIVE`, not a job state;
- job state `PAUSED` is displayed only for a durable paused job;
- Chat uses server-side SSE token streaming over `fetch`; durable-job polling remains the recovery path and the durable query-job endpoint remains the audit source of truth;
- citation preview and original-file download are separate actions and must reauthorize;
- access requests use `POST /api/v1/access-requests` and never grant access by themselves.

If a visual reference conflicts with the contract, preserve the visual style while using the contract state/permission semantics. Do not silently invent missing product behavior; report a material conflict to the Main Agent.
