#!/usr/bin/env sh
set -eu
ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$ROOT_DIR"
PYTHON="${PYTHON:-python3}"

printf '%s\n' '== GraphLatch: validate example graph =='
"$PYTHON" scripts/validate_graph.py examples/graph.json
printf '%s\n' '== GraphLatch: run unit tests =='
"$PYTHON" -m unittest discover -s tests -v
printf '%s\n' '== GraphLatch: checks passed =='
