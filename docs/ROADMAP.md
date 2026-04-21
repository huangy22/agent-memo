# Roadmap

## Near Term

1. Add upgrade support
- Introduce a safe upgrade path such as `--force` or an explicit `upgrade` mode.

2. Tighten runtime dependency packaging
- Reduce reliance on host Python site-packages so installed skills are more self-contained.

3. Validate real agent invocation
- Verify `#memory-status`, `#memory-note`, `#memory-reflect`, and `#memory-distill` inside real Codex / Claude Code sessions, not only shell-driven wrapper tests.

## Next

4. Expand docs
- Add a short quickstart.
- Add a first-time repository walkthrough.

5. Improve configuration surface
- Clarify and extend `.agent-memory.toml` overrides for storage and instruction loading.

6. Strengthen regression coverage
- Add more standalone end-to-end coverage.
- Add dedupe/update behavior tests for repeated reflect/distill runs.

## Later

7. Define candidate promotion workflow
- Specify how `promote-to-global.yaml` entries are reviewed, accepted, rejected, and archived.
