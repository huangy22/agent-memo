from dataclasses import dataclass
from pathlib import Path

from .config import MemoryConfig


@dataclass(frozen=True)
class MemoryPaths:
    repo_root: Path
    agent_memory_dir: Path
    short_term_dir: Path
    trace_file: Path
    active_session_file: Path
    project_dir: Path
    candidates_dir: Path
    global_dir: Path


def discover_memory_paths(repo_root: Path) -> MemoryPaths:
    config = MemoryConfig.from_repo_root(repo_root)
    agent_memory_dir = config.agent_memory_dir
    short_term_dir = config.short_term_dir

    return MemoryPaths(
        repo_root=config.repo_root,
        agent_memory_dir=agent_memory_dir,
        short_term_dir=short_term_dir,
        trace_file=short_term_dir / "traces" / "trace.md",
        active_session_file=short_term_dir / "active-session.md",
        project_dir=config.project_dir,
        candidates_dir=config.candidates_dir,
        global_dir=config.global_dir,
    )
