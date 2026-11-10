# Graphify Runbook

Graphify is a local, derived knowledge graph for code navigation. It helps the main agent and subagents locate symbols and relationships; it does not share conversation memory or replace the repository source of truth.

## Normal workflow

Install Graphify once on the machine (`uv tool install graphifyy`, or another isolated Python install), then run from the repository root:

```bash
scripts/sync_graph.sh
graphify query "How does authentication reach authorization?"
graphify explain "AuthorizationEvaluator"
```

`sync_graph.sh` uses `graphify update .` when an index exists and `graphify extract . --code-only` for the first build. The code-only path is local AST extraction and needs no API key. The published `graphify-out/graph.json`, `graph.html`, `GRAPH_REPORT.md`, and `manifest.json` are versioned so agents and reviewers can inspect the same graph; caches and machine-specific state remain ignored.

## Update after code changes

Run `scripts/sync_graph.sh` after each code change or commit. For automatic Git updates, install Graphify's local hooks once:

```bash
graphify hook install
graphify hook status
```

The hooks are local Git metadata and must be reinstalled after cloning. The project Codex skill and `AGENTS.md` also instruct agents to refresh the graph after code edits.

## Viewing the graph

Open `graphify-out/graph.html` in a browser. The file is a local visualization; no graph data is uploaded by the code-only workflow.

## Scope and limits

- Code relationships are extracted locally from ASTs.
- Markdown and other documents are not semantically indexed by the code-only automation path. A future semantic refresh may use an approved Graphify backend; it must not be introduced silently or require an unapproved API key.
- Do not place source documents, `.env` files, keys, uploads, or private data in the graph input scope.
