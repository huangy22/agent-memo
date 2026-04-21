from pathlib import Path

from .paths import MemoryPaths


def _write_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def ensure_memory_layout(paths: MemoryPaths) -> None:
    _write_if_missing(paths.project_dir / "pitfalls.yaml", "[]\n")
    _write_if_missing(paths.project_dir / "patterns.yaml", "[]\n")
    _write_if_missing(paths.project_dir / "decisions.yaml", "[]\n")
    _write_if_missing(paths.candidates_dir / "promote-to-global.yaml", "[]\n")
    _write_if_missing(paths.trace_file, "# Trace\n")
    _write_if_missing(paths.active_session_file, "# Active Session\n")
