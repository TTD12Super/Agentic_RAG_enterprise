# Handoff: GRAPHIFY-001

## Outcome

Graphify is integrated as a local derived code knowledge graph. The project Codex skill, `AGENTS.md`, `.graphifyignore`, sync script, runbook, and QA checks are present.

## Scope

- Code graph: automatic local AST extraction with `scripts/sync_graph.sh`.
- Agent guidance: `.codex/skills/graphify/SKILL.md` and the generated `AGENTS.md` section.
- Automatic refresh: Graphify Git hooks can be installed locally with `graphify hook install`.
- Visualization: `graphify-out/graph.html` is generated locally and ignored by Git.

## Evidence

Run from the repository root:

```bash
scripts/sync_graph.sh
python3 -m unittest discover -s tests/qa/graphify -p 'test_*.py'
```

## Limits

The default path is code-only. Semantic Markdown extraction remains a separately approved decision because it may use an external model/backend. Graphify remains derived; requirements, tasks, contracts, and source code remain authoritative.
