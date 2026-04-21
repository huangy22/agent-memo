---
name: memory-status
description: Use when you need a quick view of the current repo-local memory files and request bundles without asking the user to run helper commands.
---

# memory-status

Use this skill to inspect the current memory state for the active repository.

## Workflow

Run the repo-local helper yourself:

```bash
./run.sh .
```

Then summarize:

- whether project memory files exist
- whether short-term trace exists
- whether reflect/distill request bundles exist
- what the next useful memory action is

Do not ask the user to run Python commands.
