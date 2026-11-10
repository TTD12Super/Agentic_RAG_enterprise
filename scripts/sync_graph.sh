#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

GRAPHIFY_PYTHON=""
GRAPHIFY_BIN="${GRAPHIFY_BIN:-}"
if [ -z "$GRAPHIFY_BIN" ] && command -v graphify >/dev/null 2>&1; then
    GRAPHIFY_BIN=$(command -v graphify)
fi
if [ -z "$GRAPHIFY_BIN" ] && [ -f graphify-out/.graphify_python ]; then
    GRAPHIFY_PYTHON=$(cat graphify-out/.graphify_python)
    "$GRAPHIFY_PYTHON" -m graphify --help >/dev/null 2>&1 || GRAPHIFY_PYTHON=""
fi
if [ -z "$GRAPHIFY_BIN" ] && [ -z "$GRAPHIFY_PYTHON" ]; then
    echo "GRAPH_SYNC_FAILED: install graphifyy or set GRAPHIFY_BIN" >&2
    exit 2
fi

run_graphify() {
    if [ -n "$GRAPHIFY_PYTHON" ]; then
        "$GRAPHIFY_PYTHON" -m graphify "$@"
    else
        "$GRAPHIFY_BIN" "$@"
    fi
}

if [ -s graphify-out/graph.json ]; then
    run_graphify update .
else
    run_graphify extract . --code-only
fi
run_graphify cluster-only . --no-label
run_graphify export html --graph graphify-out/graph.json

for artifact in graphify-out/graph.json graphify-out/graph.html graphify-out/GRAPH_REPORT.md; do
    [ -s "$artifact" ] || {
        echo "GRAPH_SYNC_FAILED: missing $artifact" >&2
        exit 1
    }
done

echo "GRAPH_SYNC_PASS: graphify-out/graph.json graphify-out/graph.html graphify-out/GRAPH_REPORT.md"
