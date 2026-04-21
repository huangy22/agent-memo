#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${1:-.}"
ACTION="${2:-prepare}"
RESULT_PATH="$REPO_ROOT/.agent-memory/short-term/requests/reflect-latest/result.json"
PREPARE_CLI="$ROOT_DIR/bin/agent-memory-reflect"
APPLY_CLI="$ROOT_DIR/bin/agent-memory-reflect-apply"

resolve_cli() {
  local local_cli="$1"
  local command_name="$2"
  if [[ -x "$local_cli" ]]; then
    printf '%s\n' "$local_cli"
    return 0
  fi
  if command -v "$command_name" >/dev/null 2>&1; then
    command -v "$command_name"
    return 0
  fi
  echo "$command_name not found. Run the installer to provision the local CLI runtime." >&2
  exit 1
}

case "$ACTION" in
  prepare)
    CLI="$(resolve_cli "$PREPARE_CLI" agent-memory-reflect)"
    "$CLI" --repo "$REPO_ROOT"
    ;;
  apply)
    CLI="$(resolve_cli "$APPLY_CLI" agent-memory-reflect-apply)"
    "$CLI" --repo "$REPO_ROOT" --result-file "$RESULT_PATH"
    echo "Applied reflection result: $RESULT_PATH"
    ;;
  *)
    echo "Usage: ./run.sh [repo-root] [prepare|apply]" >&2
    exit 1
    ;;
esac
