from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = TOOL_ROOT / "install.sh"


def _run(
    args: list[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd or TOOL_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def test_install_script_creates_local_cli_and_status_wrapper_works(tmp_path: Path) -> None:
    target_dir = tmp_path / "installed-skills"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    install = _run(["bash", str(INSTALL_SCRIPT), "--target", str(target_dir), "--execute"])
    assert install.returncode == 0, install.stderr

    installed_cli = target_dir / "bin" / "agent-memory-status"
    assert installed_cli.exists(), "expected installer to create a local CLI wrapper"

    status = _run(["bash", str(target_dir / "memory-status" / "run.sh"), str(repo_dir)])
    assert status.returncode == 0, status.stderr
    assert str(repo_dir / ".agent-memory" / "project" / "pitfalls.yaml") in status.stdout


def test_installed_note_wrapper_appends_trace(tmp_path: Path) -> None:
    target_dir = tmp_path / "installed-skills"
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    install = _run(["bash", str(INSTALL_SCRIPT), "--target", str(target_dir), "--execute"])
    assert install.returncode == 0, install.stderr

    body_path = tmp_path / "note.json"
    body_path.write_text(
        json.dumps(
            {
                "symptom": ["wrapper failed"],
                "root_cause": ["stale path"],
                "fix": ["use installed cli"],
                "files": ["skills/memory-note/run.sh"],
                "tags": ["agent-memory"],
            }
        ),
        encoding="utf-8",
    )

    note = _run(
        [
            "bash",
            str(target_dir / "memory-note" / "run.sh"),
            str(repo_dir),
            "error_fixed",
            str(body_path),
            "Wrapper Fix",
        ]
    )
    assert note.returncode == 0, note.stderr

    trace_file = repo_dir / ".agent-memory" / "short-term" / "traces" / "trace.md"
    assert trace_file.exists()
    assert "wrapper failed" in trace_file.read_text(encoding="utf-8")


def test_codex_preset_installs_into_home_skills_dir(tmp_path: Path) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    env = {**os.environ, "HOME": str(fake_home)}

    install = _run(["bash", str(INSTALL_SCRIPT), "--codex", "--execute"], env=env)
    assert install.returncode == 0, install.stderr

    assert (fake_home / ".codex" / "skills" / "memory-status" / "SKILL.md").exists()
    assert (fake_home / ".codex" / "skills" / "memory-policy" / "SKILL.md").exists()
    assert (fake_home / ".codex" / "skills" / "bin" / "agent-memory-status").exists()


def test_claude_preset_installs_into_home_skills_dir(tmp_path: Path) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    env = {**os.environ, "HOME": str(fake_home)}

    install = _run(["bash", str(INSTALL_SCRIPT), "--claude", "--execute"], env=env)
    assert install.returncode == 0, install.stderr

    assert (fake_home / ".claude" / "skills" / "memory-note" / "SKILL.md").exists()
    assert (fake_home / ".claude" / "skills" / "memory-policy" / "SKILL.md").exists()
    assert (fake_home / ".claude" / "skills" / "bin" / "agent-memory-note").exists()
