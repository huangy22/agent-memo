---
name: memory-note
description: Use when a task just produced a concrete bug fix or design decision and you want to append a structured trace note without asking the user to run helper commands.
---

# memory-note

Use this skill to record a short-term memory note as part of the current task flow.

## Workflow

1. Infer the note type from context:
   - `error_fixed` for a resolved bug or root cause
   - `decision_made` for a concrete implementation choice with rationale
2. Write a temporary JSON body file under `.agent-memory/short-term/requests/note-latest/`.
3. Run the repo-local helper yourself:

```bash
./run.sh . <error_fixed|decision_made> <body-json-file> "Title"
```

4. Do not ask the user to run Python commands.
5. Summarize what was captured and which trace file was updated.

## Required Body Fields

- For `error_fixed`: `symptom`, `root_cause`, `fix`, `files`, `tags`
- For `decision_made`: `decision`, `why`, `alternatives_considered`, `tradeoffs`, `files`, `tags`
