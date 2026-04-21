#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
TARGET_DIR=""
TARGET_KIND="custom"
MODE="copy"
EXECUTE=0
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUNTIME_DIR_NAME=".agent-memory-runtime"
SOURCE_DIR_NAME="src"

cli_commands=(
  agent-memory-note
  agent-memory-reflect
  agent-memory-reflect-apply
  agent-memory-distill
  agent-memory-distill-apply
  agent-memory-status
  agent-memory-workflow
)

usage() {
  cat <<'EOF'
Usage:
  bash install.sh --codex [--mode copy|symlink] [--execute]
  bash install.sh --claude [--mode copy|symlink] [--execute]
  bash install.sh --target <dir> [--mode copy|symlink] [--execute]

Behavior:
  - default mode is a dry run; nothing is written unless --execute is provided
  - installs repo-local skill directories into a Codex/Claude skill library target
  - provisions a local CLI runtime under the target directory
  - use --codex for ~/.codex/skills, --claude for ~/.claude/skills
  - use --target only when you want a custom skills directory
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --codex)
      TARGET_DIR="$HOME/.codex/skills"
      TARGET_KIND="codex"
      shift
      ;;
    --claude)
      TARGET_DIR="$HOME/.claude/skills"
      TARGET_KIND="claude"
      shift
      ;;
    --target)
      TARGET_DIR="${2:-}"
      TARGET_KIND="custom"
      shift 2
      ;;
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --execute)
      EXECUTE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$TARGET_DIR" ]]; then
  echo "one of --codex, --claude, or --target is required" >&2
  usage >&2
  exit 1
fi

if [[ "$MODE" != "copy" && "$MODE" != "symlink" ]]; then
  echo "--mode must be copy or symlink" >&2
  exit 1
fi

echo "Agent memory prototype installer"
echo "Source skills: $SKILLS_DIR"
echo "Target dir: $TARGET_DIR"
echo "Target kind: $TARGET_KIND"
echo "Mode: $MODE"
if [[ "$EXECUTE" -eq 1 ]]; then
  echo "Execution: apply"
  echo "Python: $PYTHON_BIN"
else
  echo "Execution: dry-run"
fi

runtime_dir="$TARGET_DIR/$RUNTIME_DIR_NAME"
bin_dir="$TARGET_DIR/bin"

create_cli_wrapper() {
  local command_name="$1"
  local entrypoint_name="$2"
  cat > "$bin_dir/$command_name" <<EOF
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="\$SCRIPT_DIR/../$RUNTIME_DIR_NAME/$SOURCE_DIR_NAME\${PYTHONPATH:+:\$PYTHONPATH}"
exec "\$SCRIPT_DIR/../$RUNTIME_DIR_NAME/bin/python" -c "from memory.cli.entrypoints import $entrypoint_name as main; main()" "\$@"
EOF
  chmod +x "$bin_dir/$command_name"
}

if [[ "$EXECUTE" -eq 1 ]]; then
  mkdir -p "$TARGET_DIR"
  if [[ -e "$runtime_dir" ]]; then
    echo "Refusing to overwrite existing runtime path: $runtime_dir" >&2
    exit 1
  fi
  if [[ -e "$bin_dir" ]]; then
    echo "Refusing to overwrite existing bin path: $bin_dir" >&2
    exit 1
  fi
fi

for skill in memory-note memory-reflect memory-distill memory-status; do
  src="$SKILLS_DIR/$skill"
  dest="$TARGET_DIR/$skill"
  echo "Install: $src -> $dest"

  if [[ "$EXECUTE" -eq 1 ]]; then
    if [[ -e "$dest" ]]; then
      echo "Refusing to overwrite existing path: $dest" >&2
      exit 1
    fi

    if [[ "$MODE" == "copy" ]]; then
      cp -R "$src" "$dest"
    else
      ln -s "$src" "$dest"
    fi
    if [[ -f "$dest/run.sh" ]]; then
      chmod +x "$dest/run.sh"
    fi
  fi
done

echo "Runtime: $SCRIPT_DIR -> $runtime_dir"
for command_name in "${cli_commands[@]}"; do
  echo "CLI: $bin_dir/$command_name"
done

if [[ "$EXECUTE" -eq 1 ]]; then
  "$PYTHON_BIN" -m venv --system-site-packages "$runtime_dir"
  mkdir -p "$runtime_dir/$SOURCE_DIR_NAME"
  cp -R "$SCRIPT_DIR/memory" "$runtime_dir/$SOURCE_DIR_NAME/memory"
  mkdir -p "$bin_dir"
  create_cli_wrapper "agent-memory-note" "note_main"
  create_cli_wrapper "agent-memory-reflect" "reflect_main"
  create_cli_wrapper "agent-memory-reflect-apply" "reflect_apply_main"
  create_cli_wrapper "agent-memory-distill" "distill_main"
  create_cli_wrapper "agent-memory-distill-apply" "distill_apply_main"
  create_cli_wrapper "agent-memory-status" "status_main"
  create_cli_wrapper "agent-memory-workflow" "workflow_main"
fi

cat <<EOF

Verification:
  1. Inspect installed skills under: $TARGET_DIR
  2. Confirm these skills exist in your agent's skills library:
     - memory-note
     - memory-reflect
     - memory-distill
     - memory-status
  3. Inspect installed CLI wrappers under: $bin_dir
  4. Read:
     - $TARGET_DIR/memory-note/SKILL.md
     - $TARGET_DIR/memory-reflect/SKILL.md
     - $TARGET_DIR/memory-distill/SKILL.md
     - $TARGET_DIR/memory-status/SKILL.md
  5. In Codex / Claude Code, invoke:
     - #memory-status
     - #memory-note
     - #memory-reflect
     - #memory-distill
  6. Internal runtime fallback from a shell:
     - $TARGET_DIR/memory-note/run.sh /path/to/repo error_fixed /path/to/body.json "Error Fixed"
     - $TARGET_DIR/memory-reflect/run.sh /path/to/repo
     - $TARGET_DIR/memory-distill/run.sh /path/to/repo
     - $TARGET_DIR/memory-status/run.sh /path/to/repo
  7. Optional: add $bin_dir to PATH if you want to invoke agent-memory-* directly
EOF
