from __future__ import annotations

import json


REFLECTION_OUTPUT_CONTRACT = {
    "classification": "pitfall | pattern | decision | ignore",
    "should_write": True,
    "should_update_existing": False,
    "update_existing_title": None,
    "title": "string",
    "context": "string",
    "wrong": "string or null",
    "right": "string or null",
    "impact": "string or null",
    "choice": "string or null",
    "rationale": "string or null",
    "steps": ["string"],
    "when_to_use": ["string"],
    "when_not_to_use": ["string"],
    "alternatives_considered": ["string"],
    "tradeoffs": ["string"],
    "evidence": ["string"],
    "files": ["string"],
    "tags": ["string"],
    "source_trace": "string",
    "dedupe_key": "string",
    "should_propose_global_promotion": False,
}

DISTILLATION_OUTPUT_CONTRACT = {
    "should_create_candidate": True,
    "proposed_target": "global.patterns | global.pitfalls | global.decisions",
    "proposal": "string",
    "reason": "string",
    "supporting_entries": ["string"],
    "conflicts_with_global": False,
    "conflicting_global_rule": None,
}


def _json_block(data: object) -> str:
    return json.dumps(data, ensure_ascii=True, indent=2)


def build_reflection_prompt(
    *,
    trace_blocks: list[str],
    existing_memory: dict[str, list[dict[str, object]]],
    repo_instructions: str,
) -> str:
    return "\n\n".join(
        [
            "You are reflecting on short-term agent trace to produce durable project memory.",
            "Your job is not to summarize the session.\nYour job is to extract only reusable, project-relevant knowledge.",
            "\n".join(
                [
                    "Rules:",
                    "- Keep only actionable, specific, non-duplicate knowledge.",
                    "- Ignore one-off chat residue and purely session-local state.",
                    "- Prefer concrete operational lessons over generic advice.",
                    "- Preserve repository-specific terminology when it matters.",
                    "- If an existing project memory entry already expresses the same idea, update it instead of creating a duplicate.",
                    "- Only suggest global promotion when the lesson is phrased broadly enough to matter outside this repository.",
                ]
            ),
            "Return structured output matching this reflection schema:\n"
            + _json_block(REFLECTION_OUTPUT_CONTRACT),
            "Repository instructions:\n" + repo_instructions,
            "Existing project memory:\n" + _json_block(existing_memory),
            "Recent trace blocks:\n" + "\n\n".join(trace_blocks),
        ]
    )


def build_distillation_prompt(
    *,
    project_entries: list[dict[str, object]],
    repo_instructions: str,
    user_instructions: str,
    existing_candidates: list[dict[str, object]],
) -> str:
    return "\n\n".join(
        [
            "You are distilling project memory into possible cross-project guidance.",
            "Your job is not to preserve repository details.\nYour job is to decide whether a broader lesson is justified.",
            "\n".join(
                [
                    "Rules:",
                    "- Promote only when the lesson has value beyond this repository.",
                    "- Keep the proposal shorter and more abstract than project memory.",
                    "- Link every proposal back to concrete supporting project entries.",
                    "- If the lesson only matters inside this repository, return ignore.",
                    "- Do not directly rewrite global instructions; propose a candidate instead.",
                ]
            ),
            "Return structured output matching this distillation schema:\n"
            + _json_block(DISTILLATION_OUTPUT_CONTRACT),
            "Repository instructions:\n" + repo_instructions,
            "User/global instructions:\n" + user_instructions,
            "Existing promotion candidates:\n" + _json_block(existing_candidates),
            "Project memory under consideration:\n" + _json_block(project_entries),
        ]
    )
