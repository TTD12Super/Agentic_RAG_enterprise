# Codex agent configuration

`AGENTS.md` = repository instructions automatically discovered by Codex; `.codex/agents/*.toml` = custom **development subagent** definitions. `.codex/config.toml` contains project subagent defaults. These are not LangGraph runtime agent definitions.

The eight specialist role files are valid TOML with `name`, `description`, `developer_instructions`. Model names are intentionally omitted so the parent session chooses an available model.

Task ownership uses `tech_lead` as a special role mapped to the Main Agent. It is not a ninth specialist profile. All other task owners must map to one of the eight files in `.codex/agents/`.

The harness allows up to 10 active agent threads, but activation is task-specific. Each agent thread has an isolated context window; shared work is coordinated through repository files, task packets and handoffs rather than shared conversation memory.

Custom agent instructions do **not** provide filesystem ACL or independent sandboxes. The parent Codex permission mode applies. Use separate worktrees for parallel edits, review PRs and enforce CI tests.

Documentation checked: https://learn.chatgpt.com/docs/agent-configuration/subagents and https://learn.chatgpt.com/docs/agent-configuration/agents-md (2026-11-08). If config differs in your installed Codex version, inspect that version's documentation before making changes.
