from pathlib import Path

from ..core.precedence import load_layers
from ..core.paths import discover_memory_paths
from ..core.schemas import ensure_memory_layout


def build_session_summary(repo_root: Path) -> str:
    repo_root = Path(repo_root)
    ensure_memory_layout(discover_memory_paths(repo_root))
    layers = load_layers(repo_root)

    lines = ["# Active Session", "", "## Project Memory"]
    for entry in layers["project_pitfalls"]:
        title = entry.get("title", "Untitled pitfall")
        lines.append(f"- {title}")
    for entry in layers["project_patterns"]:
        title = entry.get("title", "Untitled pattern")
        lines.append(f"- {title}")
    for entry in layers["project_decisions"]:
        title = entry.get("title", "Untitled decision")
        lines.append(f"- {title}")

    lines.extend(["", "## Repository Instructions"])
    repo_instructions = str(layers["repo_instructions"]).strip()
    if repo_instructions:
        lines.append(repo_instructions)

    lines.extend(["", "## User Instructions"])
    user_instructions = str(layers["user_instructions"]).strip()
    if user_instructions:
        lines.append(user_instructions)

    lines.extend(["", "## Global Memory"])
    for entry in layers["global_pitfalls"]:
        title = entry.get("title", "Untitled global pitfall")
        lines.append(f"- {title}")
    for entry in layers["global_patterns"]:
        title = entry.get("title", "Untitled global pattern")
        lines.append(f"- {title}")
    for entry in layers["global_decisions"]:
        title = entry.get("title", "Untitled global decision")
        lines.append(f"- {title}")

    return "\n".join(lines).rstrip() + "\n"
