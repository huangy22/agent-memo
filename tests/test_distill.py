from __future__ import annotations

from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memory.cli.distill import apply_distillation_result, scaffold_distillation_request


def test_apply_distillation_result_rejects_malformed_payload(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    malformed = {
        "should_write": True,
        "title": "wrong schema",
    }

    with pytest.raises(ValueError, match="distillation result missing required field"):
        apply_distillation_result(repo_dir, malformed)


def test_apply_distillation_result_writes_candidate_from_template_shape(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    out_dir = repo_dir / ".agent-memory" / "short-term" / "requests" / "distill-latest"
    repo_dir.mkdir()
    (repo_dir / "CLAUDE.md").write_text("Use worktrees.\n", encoding="utf-8")

    scaffold_distillation_request(repo_dir, out_dir)

    apply_distillation_result(
        repo_dir,
        {
            "should_create_candidate": True,
            "proposed_target": "global.patterns",
            "proposal": "Package reusable skills against an installed runtime, not a source checkout.",
            "reason": "Installed skills should remain portable outside the development repository.",
            "supporting_entries": ["pitfall:installed-skills-must-use-bundled-runtime"],
            "conflicts_with_global": False,
            "conflicting_global_rule": None,
        },
    )

    candidates = yaml.safe_load(
        (repo_dir / ".agent-memory" / "candidates" / "promote-to-global.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert isinstance(candidates, list)
    assert len(candidates) == 1
    assert candidates[0]["proposal"].startswith("Package reusable skills against an installed runtime")
