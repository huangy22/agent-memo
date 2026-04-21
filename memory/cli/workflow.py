from __future__ import annotations

import argparse
from pathlib import Path

from .distill import scaffold_distillation_request
from .reflect import scaffold_reflection_request


def _default_bundle_dir(repo_root: Path, kind: str) -> Path:
    return Path(repo_root) / ".agent-memory" / "short-term" / "requests" / f"{kind}-latest"


def _print_bundle_summary(bundle_dir: Path) -> None:
    print(f"Scaffold created: {bundle_dir}")
    print(f"Prompt: {bundle_dir / 'prompt.txt'}")
    print(f"Template: {bundle_dir / 'result.template.json'}")
    print(f"Result target: {bundle_dir / 'result.json'}")


def scaffold_workflow_request(kind: str, repo_root: Path, out_dir: Path | None = None) -> Path:
    repo_root = Path(repo_root)
    bundle_dir = Path(out_dir) if out_dir else _default_bundle_dir(repo_root, kind)
    if kind == "reflect":
        scaffold_reflection_request(repo_root, bundle_dir)
    elif kind == "distill":
        scaffold_distillation_request(repo_root, bundle_dir)
    else:
        raise ValueError(f"Unsupported workflow kind: {kind}")
    return bundle_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    reflect_parser = subparsers.add_parser("reflect")
    reflect_parser.add_argument("--repo", required=True)
    reflect_parser.add_argument("--out-dir")

    distill_parser = subparsers.add_parser("distill")
    distill_parser.add_argument("--repo", required=True)
    distill_parser.add_argument("--out-dir")

    args = parser.parse_args()
    repo_root = Path(args.repo)

    if args.command == "reflect":
        bundle_dir = scaffold_workflow_request("reflect", repo_root, Path(args.out_dir) if args.out_dir else None)
        _print_bundle_summary(bundle_dir)
        return

    bundle_dir = scaffold_workflow_request("distill", repo_root, Path(args.out_dir) if args.out_dir else None)
    _print_bundle_summary(bundle_dir)


if __name__ == "__main__":
    main()
