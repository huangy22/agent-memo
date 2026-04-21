#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${1:-.}"
NOTE_TYPE="${2:-}"
BODY_FILE="${3:-}"
TITLE="${4:-Memory Note}"
LOCAL_CLI="$ROOT_DIR/bin/agent-memory-note"

if [[ -z "$NOTE_TYPE" || -z "$BODY_FILE" ]]; then
  echo "Usage: ./run.sh <repo-root> <error_fixed|decision_made> <body-json-file> [title]" >&2
  exit 1
fi

if [[ -x "$LOCAL_CLI" ]]; then
  CLI="$LOCAL_CLI"
elif command -v agent-memory-note >/dev/null 2>&1; then
  CLI="$(command -v agent-memory-note)"
else
  echo "agent-memory-note not found. Run the installer to provision the local CLI runtime." >&2
  exit 1
fi

"$CLI" \
  --repo "$REPO_ROOT" \
  --type "$NOTE_TYPE" \
  --title "$TITLE" \
  --body-file "$BODY_FILE"

echo "Appended note from: $BODY_FILE"
