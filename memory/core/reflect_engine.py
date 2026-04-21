from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import re

import yaml

from .dedupe import find_matching_title_index
from .paths import discover_memory_paths
from .schemas import ensure_memory_layout


def _load_yaml_list(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _save_yaml_list(path: Path, data: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _extract_blocks(trace: str) -> list[str]:
    return [block.strip() for block in trace.split("## ") if block.strip()]


def _extract_last_error_fixed_block(trace: str) -> str | None:
    blocks = _extract_blocks(trace)
    error_blocks = [block for block in blocks if block.startswith("Error Fixed -")]
    if not error_blocks:
        return None
    return error_blocks[-1]


def _parse_trace_block(block: str) -> dict[str, object]:
    lines = block.splitlines()
    parsed: dict[str, object] = {
        "heading": lines[0].strip() if lines else "",
        "tags": [],
    }
    current_section: str | None = None

    for raw_line in lines[1:]:
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("tags: [") and line.endswith("]"):
            tag_text = line[len("tags: [") : -1]
            parsed["tags"] = [tag.strip() for tag in tag_text.split(",") if tag.strip()]
            current_section = None
            continue
        if line.endswith(":") and not line.startswith("- "):
            current_section = line[:-1]
            parsed.setdefault(current_section, [])
            continue
        if line.startswith("- ") and current_section is not None:
            values = parsed.setdefault(current_section, [])
            if isinstance(values, list):
                values.append(line[2:].strip())
    return parsed


def _first_value(parsed: dict[str, object], section: str) -> str | None:
    values = parsed.get(section, [])
    if isinstance(values, list) and values:
        first = str(values[0]).strip()
        return first or None
    return None


def _all_values(parsed: dict[str, object], section: str) -> list[str]:
    values = parsed.get(section, [])
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _normalize_key_fragment(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _extract_last_error_fixed_title(trace: str) -> str | None:
    block = _extract_last_error_fixed_block(trace)
    if block is None:
        return None

    parsed = _parse_trace_block(block)
    root_cause = _first_value(parsed, "root_cause")
    symptom = _first_value(parsed, "symptom")
    if root_cause:
        return f"Error fixed: {root_cause}"
    if symptom:
        return f"Error fixed: {symptom}"
    return "Error fixed from session trace"


def _extract_last_decision_block(trace: str) -> str | None:
    blocks = _extract_blocks(trace)
    decision_blocks = [block for block in blocks if block.startswith("Decision Made -")]
    if not decision_blocks:
        return None
    return decision_blocks[-1]


def _extract_tag_line(block: str) -> list[str]:
    for line in block.splitlines():
        if line.startswith("tags: [") and line.endswith("]"):
            tag_text = line[len("tags: [") : -1]
            return [tag.strip() for tag in tag_text.split(",") if tag.strip()]
    return []


def _extract_section_value(block: str, section: str) -> str | None:
    marker = f"{section}:\n- "
    if marker not in block:
        return None
    value = block.split(marker, 1)[1].split("\n", 1)[0].strip()
    return value or None


def _next_pitfall_id(pitfalls: list[dict[str, object]]) -> str:
    max_suffix = 0
    for entry in pitfalls:
        match = re.fullmatch(r"pitfall-(\d+)", str(entry.get("id", "")).strip())
        if match:
            max_suffix = max(max_suffix, int(match.group(1)))
    return f"pitfall-{max_suffix + 1:03d}"


def _build_pitfall_entry(block: str, pitfalls: list[dict[str, object]]) -> dict[str, object]:
    parsed = _parse_trace_block(block)
    symptom = _first_value(parsed, "symptom")
    root_cause = _first_value(parsed, "root_cause")
    fix = _first_value(parsed, "fix")
    files = _all_values(parsed, "files")
    tags = parsed.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    key_source = root_cause or symptom or "session trace"
    evidence = [value for value in [symptom, root_cause] if value]
    today = date.today()
    return {
        "id": _next_pitfall_id(pitfalls),
        "date": today.isoformat(),
        "expires": (today + timedelta(days=90)).isoformat(),
        "title": f"Error fixed: {key_source}",
        "context": symptom or "See session trace",
        "wrong": symptom or "See session trace",
        "right": fix or "See session trace",
        "impact": root_cause or symptom or "See session trace",
        "evidence": evidence or ["See session trace"],
        "files": files,
        "tags": [str(tag) for tag in tags],
        "source_trace": str(parsed.get("heading", "")),
        "dedupe_key": f"pitfall:{_normalize_key_fragment(key_source)}",
    }


def _find_matching_pitfall_index(
    pitfalls: list[dict[str, object]], entry: dict[str, object]
) -> int | None:
    dedupe_key = str(entry.get("dedupe_key", "")).strip().lower()
    if dedupe_key:
        for index, existing in enumerate(pitfalls):
            existing_key = str(existing.get("dedupe_key", "")).strip().lower()
            if existing_key == dedupe_key:
                return index

    title = str(entry.get("title", "")).strip()
    return find_matching_title_index(pitfalls, title) if title else None


def _next_candidate_id(candidates: list[dict[str, object]]) -> str:
    max_suffix = 0
    for entry in candidates:
        match = re.fullmatch(r"promote-(\d+)", str(entry.get("id", "")).strip())
        if match:
            max_suffix = max(max_suffix, int(match.group(1)))
    return f"promote-{max_suffix + 1:03d}"


def _next_memory_entry_id(entries: list[dict[str, object]], prefix: str) -> str:
    max_suffix = 0
    for entry in entries:
        match = re.fullmatch(rf"{re.escape(prefix)}-(\d+)", str(entry.get("id", "")).strip())
        if match:
            max_suffix = max(max_suffix, int(match.group(1)))
    return f"{prefix}-{max_suffix + 1:03d}"


def _find_matching_entry_index(entries: list[dict[str, object]], entry: dict[str, object]) -> int | None:
    dedupe_key = str(entry.get("dedupe_key", "")).strip().lower()
    if dedupe_key:
        for index, existing in enumerate(entries):
            existing_key = str(existing.get("dedupe_key", "")).strip().lower()
            if existing_key == dedupe_key:
                return index

    title = str(entry.get("title", "")).strip()
    return find_matching_title_index(entries, title) if title else None


def _apply_project_entry(
    path: Path,
    entry: dict[str, object],
    prefix: str,
    finder=_find_matching_entry_index,
) -> None:
    entries = _load_yaml_list(path)
    existing_index = finder(entries, entry)
    if existing_index is not None:
        existing_id = str(entries[existing_index].get("id", "")).strip()
        entry["id"] = existing_id or _next_memory_entry_id(entries, prefix)
        entries[existing_index] = entry
    else:
        entry["id"] = _next_memory_entry_id(entries, prefix)
        entries.append(entry)
    _save_yaml_list(path, entries)


def apply_reflection_result(repo_root: Path, result: dict[str, object]) -> None:
    if not bool(result.get("should_write")):
        return

    classification = str(result.get("classification", "")).strip()
    if classification not in {"pitfall", "pattern", "decision"}:
        return

    paths = discover_memory_paths(repo_root)
    ensure_memory_layout(paths)
    today = date.today()
    entry: dict[str, object] = {
        "date": result.get("date", today.isoformat()),
        "expires": result.get("expires", (today + timedelta(days=90)).isoformat()),
        "title": result.get("title", "Untitled memory"),
        "context": result.get("context", ""),
        "files": list(result.get("files", []) or []),
        "tags": list(result.get("tags", []) or []),
        "source_trace": result.get("source_trace", ""),
        "dedupe_key": result.get("dedupe_key", ""),
    }

    if classification == "pitfall":
        entry.update(
            {
                "wrong": result.get("wrong"),
                "right": result.get("right"),
                "impact": result.get("impact"),
                "evidence": list(result.get("evidence", []) or []),
            }
        )
        _apply_project_entry(
            paths.project_dir / "pitfalls.yaml",
            entry,
            "pitfall",
            _find_matching_pitfall_index,
        )
        return

    if classification == "pattern":
        entry.update(
            {
                "steps": list(result.get("steps", []) or []),
                "when_to_use": list(result.get("when_to_use", []) or []),
                "when_not_to_use": list(result.get("when_not_to_use", []) or []),
                "evidence": list(result.get("evidence", []) or []),
            }
        )
        _apply_project_entry(paths.project_dir / "patterns.yaml", entry, "pattern")
        return

    entry.update(
        {
            "choice": result.get("choice"),
            "rationale": result.get("rationale"),
            "alternatives_considered": list(result.get("alternatives_considered", []) or []),
            "tradeoffs": list(result.get("tradeoffs", []) or []),
            "evidence": list(result.get("evidence", []) or []),
        }
    )
    _apply_project_entry(paths.project_dir / "decisions.yaml", entry, "decision")


def apply_distillation_result(repo_root: Path, result: dict[str, object]) -> None:
    if not bool(result.get("should_create_candidate")):
        return

    paths = discover_memory_paths(repo_root)
    ensure_memory_layout(paths)
    candidate_path = paths.candidates_dir / "promote-to-global.yaml"
    candidates = _load_yaml_list(candidate_path)
    proposal = str(result.get("proposal", "")).strip()
    if not proposal:
        return

    existing_index = None
    for index, candidate in enumerate(candidates):
        if str(candidate.get("proposal", "")).strip().lower() == proposal.lower():
            existing_index = index
            break

    today = date.today()
    entry = {
        "id": "",
        "date": today.isoformat(),
        "source_project": paths.repo_root.name,
        "proposed_target": result.get("proposed_target", "global.patterns"),
        "reason": result.get("reason", ""),
        "supporting_entries": list(result.get("supporting_entries", []) or []),
        "proposal": proposal,
        "status": "pending",
    }
    if result.get("conflicts_with_global"):
        entry["conflicting_global_rule"] = result.get("conflicting_global_rule")

    if existing_index is not None:
        existing_id = str(candidates[existing_index].get("id", "")).strip()
        entry["id"] = existing_id or _next_candidate_id(candidates)
        candidates[existing_index] = entry
    else:
        entry["id"] = _next_candidate_id(candidates)
        candidates.append(entry)
    _save_yaml_list(candidate_path, candidates)


def _append_candidate_from_decision(paths, trace: str) -> None:
    decision_block = _extract_last_decision_block(trace)
    if decision_block is None:
        return

    tags = _extract_tag_line(decision_block)
    if "memory" not in {tag.lower() for tag in tags}:
        return

    decision = _extract_section_value(decision_block, "decision")
    if decision is None:
        return

    candidate_path = paths.candidates_dir / "promote-to-global.yaml"
    candidates = _load_yaml_list(candidate_path)
    if any(
        str(candidate.get("proposal", "")).strip().lower() == decision.strip().lower()
        for candidate in candidates
    ):
        return

    today = date.today()
    candidates.append(
        {
            "id": _next_candidate_id(candidates),
            "date": today.isoformat(),
            "source_project": paths.repo_root.name,
            "proposed_target": "global.patterns",
            "reason": "Session produced a memory-related project decision with possible cross-project relevance",
            "supporting_entries": [],
            "proposal": decision,
            "status": "pending",
        }
    )
    _save_yaml_list(candidate_path, candidates)


def reflect(repo_root: Path) -> None:
    paths = discover_memory_paths(repo_root)
    ensure_memory_layout(paths)

    trace = paths.trace_file.read_text(encoding="utf-8") if paths.trace_file.exists() else ""
    error_block = _extract_last_error_fixed_block(trace)
    if error_block is not None:
        pitfalls_path = paths.project_dir / "pitfalls.yaml"
        pitfalls = _load_yaml_list(pitfalls_path)
        entry = _build_pitfall_entry(error_block, pitfalls)
        existing_index = _find_matching_pitfall_index(pitfalls, entry)
        if existing_index is not None:
            existing_id = str(pitfalls[existing_index].get("id", "")).strip()
            entry["id"] = existing_id or _next_pitfall_id(pitfalls)
            pitfalls[existing_index] = entry
        else:
            entry["id"] = _next_pitfall_id(pitfalls)
            pitfalls.append(entry)
        _save_yaml_list(pitfalls_path, pitfalls)
    _append_candidate_from_decision(paths, trace)
