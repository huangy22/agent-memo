import argparse
from pathlib import Path

from ..core.paths import discover_memory_paths
from ..core.schemas import ensure_memory_layout


def build_status_report(repo_root: Path) -> str:
    paths = discover_memory_paths(Path(repo_root))
    ensure_memory_layout(paths)
    return "\n".join(
        [
            str(paths.project_dir / "pitfalls.yaml"),
            str(paths.project_dir / "patterns.yaml"),
            str(paths.project_dir / "decisions.yaml"),
            str(paths.trace_file),
            str(paths.active_session_file),
            str(paths.candidates_dir / "promote-to-global.yaml"),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    print(build_status_report(Path(args.repo)))


if __name__ == "__main__":
    main()
