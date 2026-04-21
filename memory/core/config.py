from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class MemoryConfig:
    repo_root: Path
    user_home: Path
    project_name: str | None
    short_term_dir: Path
    project_dir: Path
    candidates_dir: Path
    global_dir: Path
    repo_instruction_files: list[Path]
    user_instruction_file: Path

    @classmethod
    def from_repo_root(cls, repo_root: Path) -> "MemoryConfig":
        repo_root = Path(repo_root).resolve()
        user_home = Path.home()

        config_path = repo_root / ".agent-memory.toml"
        raw_config: dict[str, object] = {}
        if config_path.exists():
            raw_config = tomllib.loads(config_path.read_text(encoding="utf-8"))

        storage = raw_config.get("storage", {})
        if not isinstance(storage, dict):
            storage = {}
        instructions = raw_config.get("instructions", {})
        if not isinstance(instructions, dict):
            instructions = {}
        project = raw_config.get("project", {})
        if not isinstance(project, dict):
            project = {}

        short_term_dir = _resolve_repo_path(
            repo_root, storage.get("short_term_dir", ".agent-memory/short-term")
        )
        project_dir = _resolve_repo_path(repo_root, storage.get("project_dir", ".agent-memory/project"))
        candidates_dir = _resolve_repo_path(
            repo_root, storage.get("candidates_dir", ".agent-memory/candidates")
        )
        global_dir = _resolve_user_path(user_home, storage.get("global_dir", "~/.codex/memories/global"))

        repo_files = instructions.get("repo_files", ["CLAUDE.md", "AGENTS.md"])
        if not isinstance(repo_files, list):
            repo_files = ["CLAUDE.md", "AGENTS.md"]
        repo_instruction_files = [
            _resolve_repo_path(repo_root, value)
            for value in repo_files
            if isinstance(value, str) and value.strip()
        ]
        user_instruction_file = _resolve_user_path(
            user_home, instructions.get("user_file", "~/.claude/CLAUDE.md")
        )

        config = cls(
            repo_root=repo_root,
            user_home=user_home,
            project_name=_coerce_optional_string(project.get("name")),
            short_term_dir=short_term_dir,
            project_dir=project_dir,
            candidates_dir=candidates_dir,
            global_dir=global_dir,
            repo_instruction_files=repo_instruction_files,
            user_instruction_file=user_instruction_file,
        )
        return config

    @property
    def agent_memory_dir(self) -> Path:
        return self.short_term_dir.parent


def _resolve_repo_path(repo_root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("repo-local config path must be a non-empty string")
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _resolve_user_path(user_home: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("user config path must be a non-empty string")
    return Path(value.replace("~", str(user_home), 1)).expanduser()


def _coerce_optional_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None
