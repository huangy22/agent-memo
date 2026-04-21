---
name: memory-reflect
description: Use when a development task produced a reusable lesson and you want the current agent to write durable project memory without asking the user to run helper commands.
---

# memory-reflect

Use this skill when the current task produced a reusable lesson and the agent should turn recent trace into durable project memory.

## Workflow

1. Run the repo-local helper yourself:

```bash
./run.sh . prepare
```

2. Read the generated prompt and template from:

   - `.agent-memory/short-term/requests/reflect-latest/prompt.txt`
   - `.agent-memory/short-term/requests/reflect-latest/result.template.json`

3. Write structured JSON to:

   - `.agent-memory/short-term/requests/reflect-latest/result.json`

4. Apply it yourself:

```bash
./run.sh . apply
```

5. Summarize the resulting project memory change.

## Notes

- This is agent-driven, not a separate model call.
- The agent should write only actionable, repository-relevant memory.
- The result must match the reflection schema described in the generated prompt.
- Do not ask the user to run Python commands.
