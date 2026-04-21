from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..core.paths import discover_memory_paths
from ..core.precedence import load_layers, load_yaml_list
from ..core.prompts import DISTILLATION_OUTPUT_CONTRACT, build_distillation_prompt
from ..core.reflect_engine import apply_distillation_result as apply_distillation_result_core
from ..core.schemas import ensure_memory_layout


def validate_distillation_result(result: dict[str, object]) -> None:
    required_fields = {
        "should_create_candidate",
        "proposed_target",
        "proposal",
        "reason",
        "supporting_entries",
        "conflicts_with_global",
        "conflicting_global_rule",
    }
    missing = sorted(field for field in required_fields if field not in result)
    if missing:
        raise ValueError(f"distillation result missing required field(s): {', '.join(missing)}")


def prepare_distillation_request(repo_root: Path) -> str:
    repo_root = Path(repo_root)
    paths = discover_memory_paths(repo_root)
    ensure_memory_layout(paths)
    layers = load_layers(repo_root)
    project_entries = [
        *layers["project_pitfalls"],
        *layers["project_patterns"],
        *layers["project_decisions"],
    ]
    existing_candidates = load_yaml_list(paths.candidates_dir / "promote-to-global.yaml")
    return build_distillation_prompt(
        project_entries=project_entries,
        repo_instructions=str(layers["repo_instructions"]).strip(),
        user_instructions=str(layers["user_instructions"]).strip(),
        existing_candidates=existing_candidates,
    )


def apply_distillation_result(repo_root: Path, result: dict[str, object]) -> None:
    validate_distillation_result(result)
    apply_distillation_result_core(Path(repo_root), result)


def scaffold_distillation_request(repo_root: Path, out_dir: Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prompt.txt").write_text(
        prepare_distillation_request(Path(repo_root)),
        encoding="utf-8",
    )
    (out_dir / "result.template.json").write_text(
        json.dumps(DISTILLATION_OUTPUT_CONTRACT, indent=2),
        encoding="utf-8",
    )


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

    args = parser.parse_args()
    if args.command == "prepare":
        print(prepare_distillation_request(Path(args.repo)), end="")
        return
    if args.command == "scaffold":
        scaffold_distillation_request(Path(args.repo), Path(args.out_dir))
        return

    result = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("result-file must contain a JSON object")
    apply_distillation_result(Path(args.repo), result)


if __name__ == "__main__":
    main()
