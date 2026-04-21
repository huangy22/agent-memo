# Execution Checklist

This file records the execution plan for extracting the agent-memory prototype
into a reusable skills library and tracks completion against concrete evidence.

## Plan

1. Fix all `skills/*/run.sh` module-path drift so installed skills no longer depend on stale source-repo imports.
2. Choose a single install/runtime model for end users.
3. Write user-facing installation and usage documentation.
4. Validate the workflow from a fresh repository with an installed skills library.
5. Add smoke tests so wrapper/runtime regressions are caught automatically.

## Product Shape Decision

The original plan's "installable CLI" step was narrowed into a more specific
product shape:

- User-facing product: a skills library for Codex / Claude Code
- User-facing invocation: `#memory-note`, `#memory-reflect`, `#memory-distill`, `#memory-status`
- Internal implementation: `run.sh` wrappers plus bundled `agent-memory-*` runtime

## Status

### 1. Fix wrapper/runtime path drift

Status: `completed`

Evidence:

- Installed skill wrappers now resolve a bundled runtime instead of calling a
  source-repo `python -m ...` path.
- Updated files:
  - `skills/memory-note/run.sh`
  - `skills/memory-reflect/run.sh`
  - `skills/memory-distill/run.sh`
  - `skills/memory-status/run.sh`

### 2. Choose a single install/runtime model

Status: `completed`

Decision:

- Default install targets are user skill-library directories:
  - `--codex` -> `~/.codex/skills`
  - `--claude` -> `~/.claude/skills`
- `--target` remains available only for custom skill-library directories.
- Bundled runtime is provisioned under the installed skills directory.

Evidence:

- `install.sh` supports `--codex`, `--claude`, and `--target`.
- Installed wrappers resolve the bundled runtime from the installed skills tree.

### 3. Write user-facing installation and usage docs

Status: `completed`

Evidence:

- `README.md` now documents the package as a skills library, not a manual shell tool.
- User entrypoint is documented as `#memory-*`.

### 4. Validate from a fresh repository with installed skills

Status: `completed`

Evidence:

- Fresh fake `~/.codex/skills` install completed successfully.
- Fresh test repo completed:
  - `memory-status`
  - `memory-note`
  - `memory-reflect prepare`
  - `memory-reflect apply`
  - `memory-distill prepare`
  - `memory-distill apply`
- Project memory was written under the fresh repo's `.agent-memory/`.
- Promotion candidate was written to `.agent-memory/candidates/promote-to-global.yaml`.

### 5. Add smoke tests

Status: `completed`

Evidence:

- `tests/test_install.py` covers install + wrapper usage.
- `tests/test_distill.py` covers:
  - malformed distill payload rejection
  - template-shaped distill candidate creation
- Current passing coverage includes:
  - custom target install
  - `--codex` preset install
  - `--claude` preset install
  - installed `memory-status`
  - installed `memory-note`
  - distill validation
  - distill candidate persistence

## Remaining Work

1. Decide whether to add an explicit upgrade mode such as `--force` before broader distribution.

## Exit Criteria Before Extraction

- Installed skills work from a fresh repo without depending on this source tree.
- `note -> reflect -> distill -> status` completes end-to-end.
- Malformed distill result payloads fail with a clear error.
- Install docs match the actual Codex / Claude Code workflow.

Current assessment:

- The original extraction work has been completed.
- Fresh standalone-repo verification has also been completed:
  - `pytest tests` passed
  - `install.sh --codex --execute` worked from the standalone repo root
  - `note -> reflect -> distill` completed against a fresh target repository
- The next phase is release hardening, not more extraction work.
