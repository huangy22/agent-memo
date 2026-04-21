---
name: memory-policy
description: Use at task start and before completion to decide whether to call memory-status, memory-note, memory-reflect, or memory-distill.
---

# memory-policy

Use this skill as the orchestration layer for the memory skills library.

This skill does not write memory itself. Its job is to decide when the agent
should call the execution skills:

- `memory-status`
- `memory-note`
- `memory-reflect`
- `memory-distill`

## Default Policy

At task start:

1. If the user asks about current memory state, use `memory-status`.
2. Before editing files, check that you are in a development worktree, not on
   `main`, and that the worktree state is understood.

During task execution:

1. When a concrete bug fix or implementation decision has been completed,
   consider `memory-note`.
2. When a reusable implementation or debugging lesson has emerged from the
   current task, consider `memory-reflect`.
3. When project memory now supports a broader cross-project lesson, consider
   `memory-distill`.

Before finishing:

1. Ask whether this task produced a specific fix or decision worth preserving in
   short-term trace.
2. Ask whether it produced a reusable lesson worth promoting to project memory.
3. Ask whether the lesson is broad enough to justify a promotion candidate.

## Trigger Guidance

Use this policy when:

- a task is starting and the agent should decide whether memory state matters
- a task just completed a bug fix or design decision
- a task is about to finish and the agent should check whether to record memory

Do not use this policy as a replacement for the execution skills. It should only
decide when to call them.
