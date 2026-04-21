#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${1:-.}"
LOCAL_CLI="$ROOT_DIR/bin/agent-memory-status"

if [[ -x "$LOCAL_CLI" ]]; then
  CLI="$LOCAL_CLI"
elif command -v agent-memory-status >/dev/null 2>&1; then
  CLI="$(command -v agent-memory-status)"
else
  echo "agent-memory-status not found. Run the installer to provision the local CLI runtime." >&2
  exit 1
fi

"$CLI" --repo "$REPO_ROOT"
