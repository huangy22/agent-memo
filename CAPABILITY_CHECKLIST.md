# Agent Memory Capability Checklist

Use this checklist to evaluate whether the memory system is merely runnable or
actually useful during real development work.

## A. Runtime Baseline

- [ ] `ruff check .` passes.
- [ ] `pytest tests -v` passes.
- [ ] `memory note` or the repo-local equivalent appends a structured block to `.agent-memory/short-term/traces/trace.md`.
- [ ] `memory reflect` or the repo-local workflow wrapper creates a predictable request bundle under `.agent-memory/short-term/requests/reflect-latest/`.
- [ ] `memory distill` or the repo-local workflow wrapper creates a predictable request bundle under `.agent-memory/short-term/requests/distill-latest/`.
- [ ] `reflect apply` writes a structured entry into `.agent-memory/project/`.
- [ ] `distill apply` writes a candidate entry into `.agent-memory/candidates/promote-to-global.yaml`.

## B. Layering And Precedence

- [ ] Project memory is loaded before repository instructions.
- [ ] Repository instructions are loaded before user-level instructions.
- [ ] User-level instructions are loaded before global structured memory.
- [ ] A repo-local `.agent-memory.toml` can override storage paths.
- [ ] A repo-local `.agent-memory.toml` can override repository instruction paths.
- [ ] A repo-local `.agent-memory.toml` can override the user instruction file path.

## C. Memory Quality

- [ ] Reflected project memory is more informative than the raw trace block.
- [ ] Reflected entries contain enough detail to be actionable later:
  title, context, wrong/right or rationale, impact/evidence, files, tags.
- [ ] Distilled candidates are more abstract than project memory but still traceable to concrete supporting entries.
- [ ] Re-running reflection on the same lesson updates or deduplicates instead of spamming duplicates.
- [ ] Re-running distillation on the same lesson updates or deduplicates instead of spamming duplicates.

## D. Real-Task Usefulness

- [ ] A real development task produced at least one memory entry you would want to read again next week.
- [ ] The reflected memory captured something not already obvious from the final code diff.
- [ ] The reflected memory would help another agent avoid re-discovering the same lesson.
- [ ] The system did not force unrelated cleanup or documentation churn during the task.
- [ ] The workflow overhead felt acceptable relative to the task size.

## E. Go / No-Go Heuristic

The system is probably only "runnable" if section A passes but section D mostly
fails.

The system is probably "useful" when:

- sections A and B pass
- most of section C passes
- at least 3 items in section D pass on a real task
