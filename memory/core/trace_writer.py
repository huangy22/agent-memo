from datetime import datetime
from pathlib import Path

from .paths import discover_memory_paths


def append_trace(repo_root: Path, heading: str, body: dict[str, list[str]]) -> None:
    paths = discover_memory_paths(repo_root)
    paths.trace_file.parent.mkdir(parents=True, exist_ok=True)
    if not paths.trace_file.exists():
        paths.trace_file.write_text("# Trace\n", encoding="utf-8")
    lines = [f"## {heading} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    tags = body.get("tags", [])
    if tags:
        lines.append(f"tags: [{', '.join(tags)}]")
    lines.append("")
    for key, values in body.items():
        if key == "tags":
            continue
        lines.append(f"{key}:")
        for value in values:
            lines.append(f"- {value}")
        lines.append("")
    with paths.trace_file.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip() + "\n\n")
