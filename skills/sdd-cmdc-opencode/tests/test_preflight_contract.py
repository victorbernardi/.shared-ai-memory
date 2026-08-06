"""Fail-closed preflight boundary contract for the cmdc implementer adapter.

The boundary tests use real temporary Git repositories and committed plan
files. The controller's own checkout is never used as a fixture.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "skills" / "sdd-cmdc-opencode" / "scripts" / "cmdc-implementer.py"
SPEC = importlib.util.spec_from_file_location("cmdc_implementer", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
validate_execution_boundary = MODULE.validate_execution_boundary
capture_initial_git_state = MODULE.capture_initial_git_state


def _init_repo(path: Path, *, branch: str = "feature") -> Path:
    path.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "-b", branch, str(path)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "Fixture User"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "fixture@example.test"],
        check=True,
        capture_output=True,
    )
    return path


def _commit_plan(repo: Path, name: str = "plan.md") -> Path:
    plan = repo / name
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", name],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "baseline"],
        check=True,
        capture_output=True,
    )
    return plan


def _commit_tracked(repo: Path) -> None:
    """Commit a tracked baseline file that later fixtures modify."""
    (repo / "tracked.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "tracked.py"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "tracked baseline"],
        check=True,
        capture_output=True,
    )


def test_preflight_blocks_master_without_recorded_consent(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="master")
    plan = _commit_plan(repo)

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "BRANCH_PROTECTED"


def test_preflight_blocks_main_without_recorded_consent(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="main")
    plan = _commit_plan(repo)

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "BRANCH_PROTECTED"


def test_preflight_allows_protected_branch_with_recorded_ledger_consent(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path / "repo", branch="master")
    plan = _commit_plan(repo)
    ledger = tmp_path / "progress.md"
    ledger.write_text(
        "ALLOW_PROTECTED_BRANCH: master\n",
        encoding="utf-8",
    )

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=True,
        ledger_file=ledger,
    )

    assert "BLOCKER_CODE" not in result
    assert result["branch"] == "master"


def test_preflight_requires_explicit_ledger_consent_for_protected_branch(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path / "repo", branch="master")
    plan = _commit_plan(repo)
    ledger = tmp_path / "progress.md"
    ledger.write_text(
        "# SDD ledger — plan: docs/superpowers/plans/demo.md\n",
        encoding="utf-8",
    )

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=True,
        ledger_file=ledger,
    )

    assert result["BLOCKER_CODE"] == "BRANCH_PROTECTED"
    assert "ALLOW_PROTECTED_BRANCH" in result["MESSAGE"]


def test_preflight_allows_a_trusted_feature_branch(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feat/demo")
    plan = _commit_plan(repo)

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert "BLOCKER_CODE" not in result
    assert result["branch"] == "feat/demo"


def test_preflight_rejects_a_missing_plan_file(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    _commit_plan(repo, name="other.md")
    missing = repo / "plan.md"

    result = validate_execution_boundary(
        repo,
        missing,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "PLAN_NOT_FOUND"
    assert "PLAN" in result["MESSAGE"].upper()


def test_preflight_rejects_a_plan_outside_the_repository(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    _commit_plan(repo)
    outside = tmp_path / "outside-plan.md"
    outside.write_text("# Plan\n", encoding="utf-8")

    result = validate_execution_boundary(
        repo,
        outside,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "PLAN_OUTSIDE_REPOSITORY"


def test_preflight_rejects_an_uncommitted_plan(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "PLAN_NOT_FOUND"
    assert "COMMITTED" in result["MESSAGE"].upper()


def test_preflight_rejects_an_invalid_cwd(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    plan = _commit_plan(repo)
    missing = tmp_path / "missing"

    result = validate_execution_boundary(
        missing,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "CWD_NOT_DIRECTORY"
    assert "MISSING" in result["MESSAGE"].upper()


def test_preflight_rejects_a_cwd_outside_the_repository(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    plan = _commit_plan(repo)
    outside = tmp_path / "outside"
    outside.mkdir()

    result = validate_execution_boundary(
        outside,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "CWD_OUTSIDE_REPOSITORY"


def test_preflight_rejects_an_uncommitted_cwd(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "-b", "feature", str(repo)],
        check=True,
        capture_output=True,
    )
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"],
        check=True,
        capture_output=True,
    )

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "HEAD_UNAVAILABLE"


def test_preflight_snapshot_preserves_each_status_line_verbatim(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    _commit_plan(repo)
    _commit_tracked(repo)
    (repo / "tracked.py").write_text("VALUE = 2\n", encoding="utf-8")
    (repo / "new-file.py").write_text("NEW = 1\n", encoding="utf-8")

    preflight = validate_execution_boundary(
        repo,
        repo / "plan.md",
        allow_protected_branch=False,
        ledger_file=None,
        allow_dirty=True,
    )
    initial = preflight["initial_git_state"]

    expected = subprocess.run(
        ["git", "-C", str(repo), "status", "--short", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert initial["status"] == expected
    assert set(initial["status"]) == {" M tracked.py", "?? new-file.py"}
    assert initial["git_root"] == str(repo.resolve())
    assert initial["head"] == subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_preflight_rejects_dirty_state_without_recorded_consent(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    _commit_plan(repo)
    _commit_tracked(repo)
    (repo / "tracked.py").write_text("VALUE = 2\n", encoding="utf-8")

    result = validate_execution_boundary(
        repo,
        repo / "plan.md",
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "DIRTY_WORKTREE"
    assert set(result["initial_git_state"]["status"]) == {" M tracked.py"}


def test_preflight_accepts_pre_existing_changes_on_a_trusted_worktree(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    _commit_plan(repo)
    _commit_tracked(repo)
    (repo / "tracked.py").write_text("VALUE = 2\n", encoding="utf-8")
    (repo / "notes.txt").write_text("pre-existing untracked\n", encoding="utf-8")

    result = validate_execution_boundary(
        repo,
        repo / "plan.md",
        allow_protected_branch=False,
        ledger_file=None,
        allow_dirty=True,
    )

    assert "BLOCKER_CODE" not in result
    assert result["dirty"] is True
    assert set(result["initial_git_state"]["status"]) == {
        " M tracked.py",
        "?? notes.txt",
    }


def test_preflight_snapshot_never_erases_or_normalizes_status_lines(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    _commit_plan(repo)
    (repo / "space name.py").write_text("S = 1\n", encoding="utf-8")
    (repo / "sub").mkdir()
    (repo / "sub" / "nested.txt").write_text("N = 1\n", encoding="utf-8")

    snapshot = capture_initial_git_state(repo)

    expected = subprocess.run(
        ["git", "-C", str(repo), "status", "--short", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert snapshot["status"] == expected
    assert all(line == raw for line, raw in zip(snapshot["status"], expected))
    assert set(snapshot["status"]) == {
        '?? "space name.py"',
        "?? sub/nested.txt",
    }


def test_capture_initial_git_state_fails_closed_outside_a_repository(
    tmp_path: Path,
) -> None:
    outside = tmp_path / "not-a-repo"
    outside.mkdir()

    with pytest.raises(RuntimeError):
        capture_initial_git_state(outside)


def test_preflight_records_the_explicit_mode(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    plan = _commit_plan(repo)

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
        allow_cmdc_yolo=True,
    )

    assert "BLOCKER_CODE" not in result
    assert result["mode"] == "yolo"
    assert result["yolo_consent"] is True


def test_preflight_blocks_a_deployed_server_path_without_recorded_authorization(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    plan = _commit_plan(repo)

    monkeypatch.setattr(MODULE, "_is_deployed_server_path", lambda path: True)

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["BLOCKER_CODE"] == "DEPLOYED_SERVER_PATH"


def test_preflight_allows_deployed_server_path_with_recorded_authorization(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _init_repo(tmp_path / "repo", branch="feature")
    plan = _commit_plan(repo)
    ledger = tmp_path / "progress.md"
    ledger.write_text(
        "ALLOW_DEPLOYED_EXECUTION: true\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(MODULE, "_is_deployed_server_path", lambda path: True)

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=ledger,
    )

    assert "BLOCKER_CODE" not in result


def test_preflight_returns_a_structured_diagnostic_contract(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo", branch="master")
    plan = _commit_plan(repo)

    result = validate_execution_boundary(
        repo,
        plan,
        allow_protected_branch=False,
        ledger_file=None,
    )

    assert result["STATUS"] == "BLOCKED"
    assert result["BLOCKER_CODE"] == "BRANCH_PROTECTED"
    assert set(
        ("STATUS", "BLOCKER_CODE", "MESSAGE", "ACTION", "MODE", "CWD", "PLAN_FILE")
    ) <= set(result)
    # A blocked result keeps the canonical root, branch, HEAD, and raw status
    # snapshot; the raw lines are never normalized or stripped.
    initial = result["initial_git_state"]
    assert initial["git_root"] == str(repo.resolve())
    assert initial["branch"] == "master"
    assert initial["head"] == subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert initial["status"] == []


def test_run_implementer_fails_closed_when_no_plan_is_supplied(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Without a plan there is no execution boundary, so Command Code must
    never start and the public contract fails closed with PLAN_REQUIRED."""
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text(
        "Write your full report to task-report.md:\n",
        encoding="utf-8",
    )

    def cmdc_must_not_run(*args, **kwargs):
        raise AssertionError("Command Code must not run without a plan")

    monkeypatch.setattr(MODULE, "resolve_cmdc", cmdc_must_not_run)
    monkeypatch.setattr(MODULE, "_run_cmdc_process", cmdc_must_not_run)

    assert MODULE.run_implementer(tmp_path, prompt_path) == 1
    captured = capsys.readouterr()
    assert "BLOCKER_CODE: PLAN_REQUIRED" in captured.err
    assert "MODE: normal" in captured.err


def test_run_implementer_blocked_preflight_keeps_initial_git_state_and_mode(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A blocked boundary through the public path reports the canonical root,
    branch, HEAD, and raw status lines verbatim plus the explicit mode, and
    never starts Command Code."""
    repo = _init_repo(tmp_path / "repo", branch="master")
    plan = _commit_plan(repo)
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text(
        "Write your full report to task-report.md:\n",
        encoding="utf-8",
    )

    def cmdc_must_not_run(*args, **kwargs):
        raise AssertionError("Command Code must not run on a blocked boundary")

    monkeypatch.setattr(MODULE, "resolve_cmdc", cmdc_must_not_run)
    monkeypatch.setattr(MODULE, "_run_cmdc_process", cmdc_must_not_run)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            plan_file=plan,
            allow_protected_branch=False,
            ledger_file=None,
        )
        == 1
    )

    captured = capsys.readouterr()
    assert "BLOCKER_CODE: BRANCH_PROTECTED" in captured.err
    assert "MODE: normal" in captured.err
    assert "INITIAL_GIT_STATE:" in captured.err
    state = json.loads(captured.err.split("INITIAL_GIT_STATE: ", 1)[1].strip())
    assert state["git_root"] == str(repo.resolve())
    assert state["branch"] == "master"
    assert state["head"] == subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    # Raw status lines keep leading status-column whitespace verbatim.
    assert state["status"] == []
