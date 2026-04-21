---
name: memory-distill
description: Use when project memory now supports a broader lesson and you want the current agent to write a promotion candidate without asking the user to run helper commands.
---

# memory-distill

Use this skill when project memory now supports a broader cross-project lesson.

## Workflow

1. Run the repo-local helper yourself:

```bash
./run.sh . prepare
```

2. Read the generated prompt and template from:

   - `.agent-memory/short-term/requests/distill-latest/prompt.txt`
   - `.agent-memory/short-term/requests/distill-latest/result.template.json`

3. Write structured JSON to:

   - `.agent-memory/short-term/requests/distill-latest/result.json`

4. Apply it yourself:

```bash
./run.sh . apply
```

5. Summarize the resulting candidate change.

## Notes

- This is agent-driven, not a separate model call.
- Distillation should produce a reviewable candidate, not rewrite global instructions directly.
- The result must match the distillation schema described in the generated prompt.
- Do not ask the user to run Python commands.
