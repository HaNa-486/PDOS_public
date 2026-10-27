#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "Python 3 was not found. Install Python 3 and retry." >&2
  exit 1
fi

ARGS=("$SCRIPT_DIR/install.py")
if [[ $# -ge 1 ]]; then ARGS+=(--destination "$1"); fi
if [[ $# -ge 2 ]]; then ARGS+=(--codex-home "$2"); fi
"$PYTHON_BIN" "${ARGS[@]}"
