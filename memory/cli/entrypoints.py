from __future__ import annotations

import argparse
import json
from pathlib import Path

from .distill import apply_distillation_result
from .note import main as note_main
from .reflect import apply_reflection_result
from .status import build_status_report
from .workflow import _print_bundle_summary, main as workflow_main, scaffold_workflow_request


def reflect_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out-dir")
    args = parser.parse_args()

    bundle_dir = scaffold_workflow_request(
        "reflect",
        Path(args.repo),
        Path(args.out_dir) if args.out_dir else None,
    )
    _print_bundle_summary(bundle_dir)


def distill_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out-dir")
    args = parser.parse_args()

    bundle_dir = scaffold_workflow_request(
        "distill",
        Path(args.repo),
        Path(args.out_dir) if args.out_dir else None,
    )
    _print_bundle_summary(bundle_dir)


def reflect_apply_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--result-file", required=True)
    args = parser.parse_args()

    result = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("result-file must contain a JSON object")
    apply_reflection_result(Path(args.repo), result)


def distill_apply_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--result-file", required=True)
    args = parser.parse_args()

    result = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("result-file must contain a JSON object")
    apply_distillation_result(Path(args.repo), result)


def status_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    print(build_status_report(Path(args.repo)))


__all__ = [
    "distill_apply_main",
    "distill_main",
    "note_main",
    "reflect_apply_main",
    "reflect_main",
    "status_main",
    "workflow_main",
]
