from pathlib import Path

import yaml

from .config import MemoryConfig
from .paths import discover_memory_paths


def load_yaml_list(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def load_instruction_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_repo_instruction_text(config: MemoryConfig) -> str:
    for path in config.repo_instruction_files:
        text = load_instruction_text(path)
        if text:
            return text
    return ""


def load_layers(repo_root: Path) -> dict[str, object]:
    config = MemoryConfig.from_repo_root(repo_root)
    paths = discover_memory_paths(repo_root)
    return {
        "project_pitfalls": load_yaml_list(paths.project_dir / "pitfalls.yaml"),
        "project_patterns": load_yaml_list(paths.project_dir / "patterns.yaml"),
        "project_decisions": load_yaml_list(paths.project_dir / "decisions.yaml"),
        "repo_instructions": load_repo_instruction_text(config),
        "user_instructions": load_instruction_text(config.user_instruction_file),
        "global_pitfalls": load_yaml_list(paths.global_dir / "pitfalls.yaml"),
        "global_patterns": load_yaml_list(paths.global_dir / "patterns.yaml"),
        "global_decisions": load_yaml_list(paths.global_dir / "decisions.yaml"),
    }
