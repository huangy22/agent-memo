from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..core.paths import discover_memory_paths
from ..core.precedence import load_layers
from ..core.prompts import REFLECTION_OUTPUT_CONTRACT, build_reflection_prompt
from ..core.reflect_engine import apply_reflection_result as apply_reflection_result_core, reflect
from ..core.schemas import ensure_memory_layout


def prepare_reflection_request(repo_root: Path) -> str:
    repo_root = Path(repo_root)
    paths = discover_memory_paths(repo_root)
    ensure_memory_layout(paths)
    trace_text = paths.trace_file.read_text(encoding="utf-8") if paths.trace_file.exists() else ""
    trace_blocks = [block.strip() for block in trace_text.split("## ") if block.strip()]
    layers = load_layers(repo_root)
    existing_memory = {
        "pitfalls": layers["project_pitfalls"],
        "patterns": layers["project_patterns"],
        "decisions": layers["project_decisions"],
    }
    return build_reflection_prompt(
        trace_blocks=trace_blocks[-3:],
        existing_memory=existing_memory,
        repo_instructions=str(layers["repo_instructions"]).strip(),
    )


def apply_reflection_result(repo_root: Path, result: dict[str, object]) -> None:
    apply_reflection_result_core(Path(repo_root), result)


def scaffold_reflection_request(repo_root: Path, out_dir: Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prompt.txt").write_text(
        prepare_reflection_request(Path(repo_root)),
        encoding="utf-8",
    )
    (out_dir / "result.template.json").write_text(
        json.dumps(REFLECTION_OUTPUT_CONTRACT, indent=2),
        encoding="utf-8",
    )


def reflect_session(repo_root: Path) -> None:
    reflect(Path(repo_root))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--repo", required=True)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--repo", required=True)
    apply_parser.add_argument("--result-file", required=True)

    scaffold_parser = subparsers.add_parser("scaffold")
    scaffold_parser.add_argument("--repo", required=True)
    scaffold_parser.add_argument("--out-dir", required=True)

    legacy_parser = subparsers.add_parser("legacy-reflect")
    legacy_parser.add_argument("--repo", required=True)

    args = parser.parse_args()
    if args.command == "prepare":
        print(prepare_reflection_request(Path(args.repo)), end="")
        return
    if args.command == "apply":
        result = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
        if not isinstance(result, dict):
            raise ValueError("result-file must contain a JSON object")
        apply_reflection_result(Path(args.repo), result)
        return
    if args.command == "scaffold":
        scaffold_reflection_request(Path(args.repo), Path(args.out_dir))
        return
    reflect_session(Path(args.repo))


if __name__ == "__main__":
    main()
