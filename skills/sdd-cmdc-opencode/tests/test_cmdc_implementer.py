from __future__ import annotations

import importlib.util
import json
import subprocess
from types import SimpleNamespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "skills" / "sdd-cmdc-opencode" / "scripts" / "cmdc-implementer.py"
SPEC = importlib.util.spec_from_file_location("cmdc_implementer", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_command_uses_fixed_model_and_edit_flags() -> None:
    command = MODULE.build_command(Path("cmdc"))

    assert command == [
        "cmdc",
        "-p",
        "--model",
        "deepseek/deepseek-v4-flash",
        "--max-turns",
        "20",
        "--no-skills",
        "--trust",
        "--skip-onboarding",
        "--yolo",
    ]


def test_build_command_accepts_a_task_specific_turn_limit() -> None:
    command = MODULE.build_command(Path("cmdc"), max_turns=7)

    assert command[command.index("--max-turns") + 1] == "7"
    assert command[command.index("--model") + 1] == "deepseek/deepseek-v4-flash"


def test_classify_failure_reports_missing_command() -> None:
    diagnostic = MODULE.classify_failure(127, "", report_exists=False, cmd_found=False)

    assert diagnostic["BLOCKER_CODE"] == "CMD_NOT_FOUND"


def test_classify_failure_reports_authentication_requirement() -> None:
    diagnostic = MODULE.classify_failure(3, "not authenticated", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "AUTH_REQUIRED"


def test_classify_failure_reports_unavailable_model() -> None:
    diagnostic = MODULE.classify_failure(4, "MODEL_NOT_IN_PLAN", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "MODEL_UNAVAILABLE"


def test_classify_failure_reports_rate_limit() -> None:
    diagnostic = MODULE.classify_failure(5, "rate limited", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "RATE_LIMITED"


def test_classify_failure_reports_timeout() -> None:
    diagnostic = MODULE.classify_failure(8, "max turns reached", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "TIMEOUT"


def test_classify_failure_reports_generic_process_failure() -> None:
    diagnostic = MODULE.classify_failure(1, "unexpected failure", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "PROCESS_FAILED"


def test_classify_failure_reports_missing_report_after_success() -> None:
    diagnostic = MODULE.classify_failure(0, "", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "REPORT_MISSING"


def test_render_blocked_emits_the_structured_contract() -> None:
    diagnostic = {
        "BLOCKER_CODE": "MODEL_UNAVAILABLE",
        "MESSAGE": "deepseek/deepseek-v4-flash não está disponível no plano atual",
        "COMMAND": "cmdc -p --model deepseek/deepseek-v4-flash",
        "EXIT_CODE": "4",
        "STDERR": "MODEL_NOT_IN_PLAN",
        "ACTION": "executar cmdc --list-models e interromper a tarefa",
    }

    assert MODULE.render_blocked(diagnostic) == "\n".join(
        [
            "STATUS: BLOCKED",
            "BLOCKER_CODE: MODEL_UNAVAILABLE",
            "MESSAGE: deepseek/deepseek-v4-flash não está disponível no plano atual",
            "COMMAND: cmdc -p --model deepseek/deepseek-v4-flash",
            "EXIT_CODE: 4",
            "STDERR: MODEL_NOT_IN_PLAN",
            "ACTION: executar cmdc --list-models e interromper a tarefa",
        ]
    )


def _write_prompt(tmp_path: Path, report_path: Path) -> Path:
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text(
        f"Write your full report to {report_path}:\n",
        encoding="utf-8",
    )
    return prompt_path


def _create_git_fixture(path: Path) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "Fixture User"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "fixture@example.test"],
        check=True,
    )
    (path / "tracked.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "--", "tracked.py"], check=True)
    subprocess.run(
        ["git", "-C", str(path), "commit", "-qm", "fixture baseline"],
        check=True,
    )
    return path


def test_collect_workspace_snapshot_detects_partial_unicode_fixture_diff(
    tmp_path: Path,
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-ação & recovery")

    baseline = MODULE.collect_workspace_snapshot(repo)
    (repo / "partial.py").write_text("VALUE = 2\n", encoding="utf-8")

    snapshot = MODULE.collect_workspace_snapshot(
        repo,
        baseline_head=baseline["head"],
        report_path=repo / "task-report.md",
    )

    assert snapshot["head"] == baseline["head"]
    assert snapshot["diff_present"] is True
    assert snapshot["commits_since_baseline"] == []
    assert snapshot["report_exists"] is False
    assert snapshot["state"] == "IMPLEMENTATION INCOMPLETE"


def test_timeout_with_partial_diff_writes_incomplete_checkpoint(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-ação & timeout")
    report_path = repo / "task-report.md"
    prompt_path = _write_prompt(repo, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"
    real_run = MODULE.subprocess.run

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_run(command, **kwargs):
        if command[0] == "cmdc":
            Path(kwargs["cwd"], "partial.py").write_text(
                "PARTIAL = True\n", encoding="utf-8"
            )
            raise MODULE.subprocess.TimeoutExpired(
                command, timeout=0.01, stderr="max turns reached"
            )
        return real_run(command, **kwargs)

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            max_turns=1,
            checkpoint_file=checkpoint_path,
        )
        != 0
    )

    captured = capsys.readouterr()
    assert "STATUS: IMPLEMENTATION INCOMPLETE" in captured.err
    assert "WORKSPACE_DIFF: true" in captured.err
    assert checkpoint_path.is_file()
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8").splitlines()[-1])
    assert checkpoint["state"] == "IMPLEMENTATION INCOMPLETE"
    assert checkpoint["snapshot"]["diff_present"] is True


def test_timeout_without_diff_writes_distinct_timeout_checkpoint(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-timeout-no-diff")
    # Keep the tracked workspace clean: write the prompt outside the repo so
    # the only signal is the timeout itself, not an untracked prompt file.
    prompt_dir = tmp_path / "prompt-dir"
    prompt_dir.mkdir(parents=True)
    prompt_path = _write_prompt(prompt_dir, repo / "task-report.md")
    checkpoint_path = repo / "checkpoints.jsonl"

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    real_run = MODULE.subprocess.run

    def fake_run(command, **kwargs):
        if command[0] == "cmdc":
            raise MODULE.subprocess.TimeoutExpired(
                command, timeout=0.01, stderr="max turns reached"
            )
        return real_run(command, **kwargs)

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            max_turns=1,
            checkpoint_file=checkpoint_path,
        )
        == 8
    )

    captured = capsys.readouterr()
    assert "STATUS: IMPLEMENTATION INCOMPLETE" in captured.err
    assert "WORKSPACE_DIFF: false" in captured.err
    assert checkpoint_path.is_file()
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8").splitlines()[-1])
    assert checkpoint["event"] == "TIMED_OUT"
    assert checkpoint["state"] == "IMPLEMENTATION INCOMPLETE"
    assert checkpoint["snapshot"]["diff_present"] is False
    assert checkpoint["snapshot"]["report_exists"] is False


def test_timeout_with_diff_but_missing_report_is_incomplete(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-diff-no-report")
    report_path = repo / "task-report.md"
    prompt_path = _write_prompt(repo, report_path)
    real_run = MODULE.subprocess.run

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_run(command, **kwargs):
        if command[0] == "cmdc":
            Path(kwargs["cwd"], "partial.py").write_text(
                "PARTIAL = True\n", encoding="utf-8"
            )
            raise MODULE.subprocess.TimeoutExpired(
                command, timeout=0.01, stderr="max turns reached"
            )
        return real_run(command, **kwargs)

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    assert MODULE.run_implementer(repo, prompt_path, max_turns=1) == 8

    captured = capsys.readouterr()
    assert "STATUS: IMPLEMENTATION INCOMPLETE" in captured.err
    assert "WORKSPACE_DIFF: true" in captured.err
    assert "REPORT_EXISTS: false" in captured.err


def test_snapshot_with_commit_but_no_report_is_incomplete(
    tmp_path: Path,
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-commit-no-report")

    baseline = MODULE.collect_workspace_snapshot(repo)
    (repo / "added.py").write_text("VALUE = 3\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "--", "added.py"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "commit without report"],
        check=True,
    )

    snapshot = MODULE.collect_workspace_snapshot(
        repo,
        baseline_head=baseline["head"],
        report_path=repo / "task-report.md",
    )

    assert snapshot["head"] != baseline["head"]
    assert snapshot["commits_since_baseline"] != []
    assert snapshot["report_exists"] is False
    assert snapshot["state"] == "IMPLEMENTATION INCOMPLETE"


def test_snapshot_with_report_but_no_commit_is_incomplete(
    tmp_path: Path,
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-report-no-commit")
    report_path = repo / "task-report.md"
    report_path.write_text("STATUS: DONE\n", encoding="utf-8")

    baseline = MODULE.collect_workspace_snapshot(repo, report_path=report_path)
    snapshot = MODULE.collect_workspace_snapshot(
        repo,
        baseline_head=baseline["head"],
        report_path=report_path,
    )

    assert snapshot["head"] == baseline["head"]
    assert snapshot["commits_since_baseline"] == []
    assert snapshot["report_exists"] is True
    # A report alone never proves implementation completed; the workspace
    # snapshot must stay fail-closed.
    assert snapshot["state"] == "IMPLEMENTATION INCOMPLETE"


def test_report_path_accepts_colon_marker_variant(tmp_path: Path) -> None:
    report_path = tmp_path / "task-report.md"
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text(
        "Write the full report to: task-report.md\n",
        encoding="utf-8",
    )

    prompt_text = prompt_path.read_text(encoding="utf-8")

    assert MODULE._extract_report_path(prompt_text, tmp_path) == report_path


def test_timeout_preserves_diagnostic_when_snapshot_collection_fails(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    prompt_path = _write_prompt(tmp_path, tmp_path / "task-report.md")
    snapshots = iter(
        [
            {"head": "baseline"},
            RuntimeError("git status unavailable"),
        ]
    )

    def collect_snapshot(*args, **kwargs):
        result = next(snapshots)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(MODULE, "collect_workspace_snapshot", collect_snapshot)
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE.subprocess,
        "run",
        lambda command, **kwargs: (_ for _ in ()).throw(
            MODULE.subprocess.TimeoutExpired(command, timeout=0.01, stderr="max turns")
        ),
    )

    assert MODULE.run_implementer(tmp_path, prompt_path, max_turns=1) == 8
    captured = capsys.readouterr()
    assert "STATUS: BLOCKED" in captured.err
    assert "BLOCKER_CODE: TIMEOUT" in captured.err
    assert "git status unavailable" in captured.err


def test_run_implementer_accepts_success_with_report(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    report_path = tmp_path / "report.md"
    report_path.write_text("STATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    observed: dict[str, object] = {}

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="worker output", stderr="")

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    assert MODULE.run_implementer(tmp_path, prompt_path) == 0
    assert observed["command"] == MODULE.build_command(Path("cmdc"))
    assert capsys.readouterr().out == "worker output\n"


def test_run_implementer_preserves_failed_process_diagnostics(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    prompt_path = _write_prompt(tmp_path, tmp_path / "missing-report.md")
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE.subprocess,
        "run",
        lambda command, **kwargs: SimpleNamespace(
            returncode=4, stdout="partial output", stderr="MODEL_NOT_IN_PLAN"
        ),
    )

    assert MODULE.run_implementer(tmp_path, prompt_path) == 4
    captured = capsys.readouterr()
    assert "partial output" in captured.out
    assert "BLOCKER_CODE: MODEL_UNAVAILABLE" in captured.err
    assert "STDERR: MODEL_NOT_IN_PLAN" in captured.err


def test_run_implementer_reports_missing_command(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    prompt_path = _write_prompt(tmp_path, tmp_path / "missing-report.md")

    def missing_command(cmd_bin="cmdc"):
        raise FileNotFoundError("cmdc binary not found")

    monkeypatch.setattr(MODULE, "resolve_cmdc", missing_command)

    assert MODULE.run_implementer(tmp_path, prompt_path) == 127
    assert "BLOCKER_CODE: CMD_NOT_FOUND" in capsys.readouterr().err


def test_run_implementer_reports_missing_report_after_zero_exit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    prompt_path = _write_prompt(tmp_path, tmp_path / "missing-report.md")
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE.subprocess,
        "run",
        lambda command, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )

    assert MODULE.run_implementer(tmp_path, prompt_path) == 1
    assert "BLOCKER_CODE: REPORT_MISSING" in capsys.readouterr().err
