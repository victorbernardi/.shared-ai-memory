from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from types import SimpleNamespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "skills" / "sdd-cmdc-opencode" / "scripts" / "cmdc-implementer.py"
SPEC = importlib.util.spec_from_file_location("cmdc_implementer", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

REVIEW_SESSION_PATH = (
    REPO_ROOT / "skills" / "sdd-cmdc-opencode" / "scripts" / "review-session.py"
)
REVIEW_SPEC = importlib.util.spec_from_file_location(
    "review_session", REVIEW_SESSION_PATH
)
assert REVIEW_SPEC is not None and REVIEW_SPEC.loader is not None
REVIEW = importlib.util.module_from_spec(REVIEW_SPEC)
sys.modules[REVIEW_SPEC.name] = REVIEW
REVIEW_SPEC.loader.exec_module(REVIEW)


def test_build_command_uses_fixed_model_and_edit_flags() -> None:
    command = MODULE.build_command(Path("cmdc"))

    assert command == [
        "cmdc",
        "-p",
        "--model",
        "deepseek/deepseek-v4-flash",
        "--max-turns",
        "100",
        "--output-format",
        "json",
        "--no-skills",
        "--trust",
        "--skip-onboarding",
    ]


def test_build_command_includes_yolo_only_for_explicit_consent() -> None:
    command = MODULE.build_command(Path("cmdc"), allow_cmdc_yolo=True)

    assert command == [
        "cmdc",
        "-p",
        "--model",
        "deepseek/deepseek-v4-flash",
        "--max-turns",
        "100",
        "--output-format",
        "json",
        "--yolo",
        "--no-skills",
        "--trust",
        "--skip-onboarding",
    ]
    # The default command never assumes consent.
    assert "--yolo" not in MODULE.build_command(Path("cmdc"))


def test_configure_stdio_requests_utf8(monkeypatch) -> None:
    calls: list[dict[str, str]] = []

    class FakeStream:
        def reconfigure(self, **kwargs: str) -> None:
            calls.append(kwargs)

    monkeypatch.setattr(MODULE.sys, "stdout", FakeStream())
    monkeypatch.setattr(MODULE.sys, "stderr", FakeStream())

    MODULE._configure_stdio()

    assert calls == [
        {"encoding": "utf-8", "errors": "replace"},
        {"encoding": "utf-8", "errors": "replace"},
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


def test_classify_failure_reports_permission_denied() -> None:
    diagnostic = MODULE.classify_failure(4, "", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "PERMISSION_DENIED"


def test_test_evidence_requires_a_positive_pass_result() -> None:
    assert MODULE._has_test_evidence("pytest: 14 passed") is True
    assert MODULE._has_test_evidence("pytest ran; 2 failed") is False
    assert MODULE._has_test_evidence("pytest was not executed") is False
    assert MODULE._has_test_evidence("tests were not passed") is False
    assert MODULE._has_test_evidence("pytest: 14 passed, 2 failed") is False


def test_recovery_requires_a_new_commit_after_recovery_starts() -> None:
    snapshot = {
        "head": "same-head",
        "commits_since_baseline": ["old-commit"],
        "report_exists": True,
        "tests_detectable": True,
    }

    assert MODULE._recovery_is_ready(0, snapshot, "same-head") is False
    assert MODULE._recovery_is_ready(0, {**snapshot, "head": "new-head"}, "same-head") is True


def test_initial_workspace_snapshot_failure_blocks_before_cmdc(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "repo")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_path = _write_prompt(tmp_path, tmp_path / "task-report.md")
    monkeypatch.setattr(
        MODULE,
        "collect_workspace_snapshot",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("git root unavailable")
        ),
    )

    real_run = MODULE.subprocess.run

    def cmdc_must_not_run(*args, **kwargs):
        # Only the child Command Code process is forbidden; the preflight's
        # real Git plumbing must still run.
        if args and Path(str(args[0][0])).name != "git":
            raise AssertionError("cmdc must not run without a Git baseline")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(MODULE.subprocess, "run", cmdc_must_not_run)

    assert MODULE.run_implementer(repo, prompt_path, plan_file=plan) == 1
    captured = capsys.readouterr()
    assert "BLOCKER_CODE: WORKSPACE_INSPECTION_FAILED" in captured.err
    assert "git root unavailable" in captured.err
    assert "MODE: normal" in captured.err


def test_heartbeat_snapshot_failure_is_checkpointed(tmp_path: Path, monkeypatch) -> None:
    checkpoint_path = tmp_path / "heartbeat.jsonl"
    calls = {"count": 0}

    def failing_snapshot(*args, **kwargs):
        calls["count"] += 1
        raise RuntimeError("git status unavailable")

    class StopAfterOneHeartbeat:
        def wait(self, interval: float) -> bool:
            return calls["count"] > 0

    monkeypatch.setattr(MODULE, "collect_workspace_snapshot", failing_snapshot)
    MODULE._heartbeat_loop(
        tmp_path,
        "baseline",
        None,
        checkpoint_path,
        "cmdc --output-format json",
        0.01,
        StopAfterOneHeartbeat(),
    )

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8").splitlines()[0])
    assert checkpoint["event"] == "HEARTBEAT_FAILED"
    assert checkpoint["last_output"] == "git status unavailable"


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
            "MODE:",
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
    # Init on a non-protected branch: the preflight refuses main/master
    # without ledger consent, and these fixtures exercise the run paths,
    # not the protected-branch gate.
    subprocess.run(["git", "init", "-q", "-b", "feature", str(path)], check=True)
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


def test_activity_fingerprint_detects_content_change_with_same_git_status(
    tmp_path: Path,
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-content-fingerprint")
    tracked = repo / "tracked.py"
    tracked.write_text("VALUE = 2\n", encoding="utf-8")
    first = MODULE.collect_workspace_snapshot(repo)
    tracked.write_text("VALUE = 3\n", encoding="utf-8")
    second = MODULE.collect_workspace_snapshot(repo)

    assert first["status"] == second["status"]
    assert MODULE._activity_fingerprint(first) != MODULE._activity_fingerprint(second)


def test_timeout_with_partial_diff_writes_incomplete_checkpoint(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-ação & timeout")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        Path(cwd, "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
        raise MODULE.subprocess.TimeoutExpired(
            command, timeout=0.01, stderr="max turns reached"
        )

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            max_turns=1,
            checkpoint_file=checkpoint_path,
            plan_file=plan,
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
    # Keep the tracked workspace clean: write the plan and prompt outside the
    # repo so the only signal is the timeout itself, not an untracked file.
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt-dir"
    prompt_dir.mkdir(parents=True)
    prompt_path = _write_prompt(prompt_dir, repo / "task-report.md")
    checkpoint_path = repo / "checkpoints.jsonl"

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    def fake_process(command, prompt_text, cwd, **kwargs):
        raise MODULE.subprocess.TimeoutExpired(
            command, timeout=0.01, stderr="max turns reached"
        )

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            max_turns=1,
            checkpoint_file=checkpoint_path,
            plan_file=plan,
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
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, report_path)
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        Path(cwd, "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
        raise MODULE.subprocess.TimeoutExpired(
            command, timeout=0.01, stderr="max turns reached"
        )

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert MODULE.run_implementer(repo, prompt_path, max_turns=1, plan_file=plan) == 8

    captured = capsys.readouterr()
    assert "STATUS: IMPLEMENTATION INCOMPLETE" in captured.err
    assert "WORKSPACE_DIFF: true" in captured.err
    assert "REPORT_EXISTS: false" in captured.err


def test_stall_is_incomplete_without_automatic_recovery(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-stall")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_path = _write_prompt(tmp_path, repo / "task-report.md")
    checkpoint_path = repo / "checkpoints.jsonl"
    calls = {"cmdc": 0}

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        calls["cmdc"] += 1
        Path(cwd, "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
        error = MODULE.subprocess.TimeoutExpired(command, timeout=0.01, stderr="stalled")
        error.watchdog_reason = "STALLED"  # type: ignore[attr-defined]
        raise error

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            heartbeat_interval=0,
            plan_file=plan,
        )
        == 8
    )

    captured = capsys.readouterr()
    assert "BLOCKER_CODE: STALLED" in captured.err
    assert "EVENT_LOG:" in captured.err
    assert calls["cmdc"] == 1
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8").splitlines()[-1])
    assert checkpoint["event"] == "TIMED_OUT"
    assert checkpoint["snapshot"]["event_log"].endswith("checkpoints-events.jsonl")


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
    repo = _create_git_fixture(tmp_path / "fixture-snapshot-fail")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "task-report.md")
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
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: (_ for _ in ()).throw(
            MODULE.subprocess.TimeoutExpired(command, timeout=0.01, stderr="max turns")
        ),
    )

    assert (
        MODULE.run_implementer(
            repo, prompt_path, max_turns=1, plan_file=plan
        )
        == 8
    )
    captured = capsys.readouterr()
    assert "STATUS: BLOCKED" in captured.err
    assert "BLOCKER_CODE: TIMEOUT" in captured.err
    assert "git status unavailable" in captured.err
    assert "MODE: normal" in captured.err


def test_success_writes_starting_and_finished_checkpoints(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-checkpoint-lifecycle")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text("pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"
    real_run = MODULE.subprocess.run
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        (repo / "implemented.py").write_text(
            "IMPLEMENTED = True\n", encoding="utf-8"
        )
        real_run(
            ["git", "-C", str(repo), "add", "--", "implemented.py", "task-report.md"],
            check=True,
        )
        real_run(
            ["git", "-C", str(repo), "commit", "-qm", "implementation commit"],
            check=True,
        )
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            heartbeat_interval=0,
            plan_file=plan,
            allow_dirty=True,
        )
        == 0
    )

    checkpoints = [
        json.loads(line)
        for line in checkpoint_path.read_text(encoding="utf-8").splitlines()
    ]
    assert [item["event"] for item in checkpoints] == ["STARTING", "FINISHED"]
    assert checkpoints[0]["phase"] == "STARTING"
    assert checkpoints[-1]["phase"] == "FINISHED"
    assert checkpoints[-1]["state"] == "CHECKPOINT"
    assert checkpoints[-1]["snapshot"]["report_exists"] is True
    assert checkpoints[-1]["snapshot"]["tests_detectable"] is True
    assert checkpoints[-1]["last_output"] == "pytest 1 passed"


def test_default_wall_timeout_is_separate_from_turn_budget() -> None:
    assert MODULE.DEFAULT_MAX_TURNS == 100
    assert MODULE.DEFAULT_WALL_TIMEOUT_SECONDS == 4 * 60 * 60


def test_stall_expiry_is_separate_from_wall_timeout() -> None:
    assert MODULE._stall_expired(100.0, 100.0 + 900.0, 900.0) is True
    assert MODULE._stall_expired(100.0, 100.0 + 899.9, 900.0) is False


def test_cmdc_process_streams_events_and_records_activity(tmp_path: Path, monkeypatch) -> None:
    class FakeStream:
        def __init__(self, lines: list[str]) -> None:
            self.lines = iter(lines)

        def readline(self) -> str:
            return next(self.lines, "")

        def close(self) -> None:
            return None

    class FakeStdin:
        def __init__(self) -> None:
            self.value = ""

        def write(self, value: str) -> None:
            self.value += value

        def close(self) -> None:
            return None

    class FakeProcess:
        pid = 1234
        returncode = 0

        def __init__(self) -> None:
            self.stdin = FakeStdin()
            self.stdout = FakeStream(["event one\n"])
            self.stderr = FakeStream(["warning\n"])

        def poll(self) -> int:
            return 0

        def wait(self, timeout: float | None = None) -> int:
            return self.returncode

    process = FakeProcess()
    monkeypatch.setattr(MODULE.subprocess, "Popen", lambda *args, **kwargs: process)
    started = time.monotonic()
    activity_state = {
        "lock": MODULE.threading.Lock(),
        "started": started,
        "last_activity": started,
        "last_event": started,
        "last_workspace": started,
        "events_seen": 0,
    }
    event_log = tmp_path / "events.jsonl"

    result = MODULE._run_cmdc_process(
        ["cmdc"],
        "prompt",
        tmp_path,
        wall_timeout_seconds=60,
        stall_timeout_seconds=60,
        activity_state=activity_state,
        event_log=event_log,
    )

    assert result.returncode == 0
    assert result.stdout == "event one\n"
    assert result.stderr == "warning\n"
    assert activity_state["events_seen"] == 2
    assert len(event_log.read_text(encoding="utf-8").splitlines()) == 2


def test_cmdc_process_stops_when_stream_and_workspace_stall(tmp_path: Path, monkeypatch) -> None:
    class EmptyStream:
        def readline(self) -> str:
            return ""

        def close(self) -> None:
            return None

    class FakeStdin:
        def write(self, value: str) -> None:
            return None

        def close(self) -> None:
            return None

    class FakeProcess:
        pid = 5678
        returncode = None

        def __init__(self) -> None:
            self.stdin = FakeStdin()
            self.stdout = EmptyStream()
            self.stderr = EmptyStream()

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            self.returncode = 1
            return self.returncode

    process = FakeProcess()
    terminated: list[int] = []
    monkeypatch.setattr(MODULE.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(MODULE, "_terminate_process_tree", terminated.append)
    monkeypatch.setattr(MODULE, "_process_tree_alive", lambda pid: False)
    started = time.monotonic()
    activity_state = {
        "lock": MODULE.threading.Lock(),
        "started": started,
        "last_activity": started,
        "last_event": started,
        "last_workspace": started,
        "events_seen": 0,
    }

    try:
        MODULE._run_cmdc_process(
            ["cmdc"],
            "prompt",
            tmp_path,
            wall_timeout_seconds=60,
            stall_timeout_seconds=0.01,
            activity_state=activity_state,
        )
    except MODULE.subprocess.TimeoutExpired as error:
        assert getattr(error, "watchdog_reason") == "STALLED"
        assert getattr(error, "watchdog_pid") == 5678
    else:
        raise AssertionError("stall watchdog did not stop the process")

    assert terminated == [5678]


def test_git_success_without_commit_is_transaction_incomplete(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-success-without-commit")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text("pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: SimpleNamespace(
            returncode=0, stdout="pytest 1 passed", stderr=""
        ),
    )

    assert MODULE.run_implementer(repo, prompt_path, plan_file=plan, allow_dirty=True) == 1
    assert "TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_long_run_emits_heartbeat_with_command_and_workspace_snapshot(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-heartbeat")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text("STATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"
    real_run = MODULE.subprocess.run
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        time.sleep(0.05)
        (repo / "heartbeat.py").write_text(
            "HEARTBEAT = True\n", encoding="utf-8"
        )
        real_run(
            ["git", "-C", str(repo), "add", "--", "heartbeat.py", "task-report.md"],
            check=True,
        )
        real_run(
            ["git", "-C", str(repo), "commit", "-qm", "heartbeat commit"],
            check=True,
        )
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            heartbeat_interval=0.005,
            plan_file=plan,
            allow_dirty=True,
        )
        == 0
    )

    checkpoints = [
        json.loads(line)
        for line in checkpoint_path.read_text(encoding="utf-8").splitlines()
    ]
    heartbeat = next(item for item in checkpoints if item["event"] == "HEARTBEAT")
    assert heartbeat["phase"] == "RUNNING"
    assert "cmdc" in heartbeat["last_command"]
    assert "head" in heartbeat["snapshot"]
    assert heartbeat["snapshot"]["elapsed_seconds"] >= 0


def test_timeout_checkpoint_detects_test_output(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-timeout-tests")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_path = _write_prompt(tmp_path, repo / "task-report.md")
    checkpoint_path = repo / "checkpoints.jsonl"

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    def fake_process(command, prompt_text, cwd, **kwargs):
        raise MODULE.subprocess.TimeoutExpired(
            command,
            timeout=0.01,
            output="pytest: 14 passed",
            stderr="max turns reached",
        )

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            heartbeat_interval=0,
            plan_file=plan,
        )
        == 8
    )

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8").splitlines()[-1])
    assert checkpoint["event"] == "TIMED_OUT"
    assert checkpoint["snapshot"]["tests_detectable"] is True


def test_timeout_with_partial_diff_runs_bounded_cmdc_recovery(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-timeout-recovery")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    prompt_path = _write_prompt(tmp_path, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"
    calls = {"cmdc": 0}

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        calls["cmdc"] += 1
        if calls["cmdc"] == 1:
            (repo / "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
            raise MODULE.subprocess.TimeoutExpired(
                command, timeout=0.01, stderr="max turns reached"
            )
        report_path.write_text("Tests: pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(repo), "add", "--", "partial.py", "task-report.md"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-qm", "recovery commit"],
            check=True,
        )
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            heartbeat_interval=0,
            recovery_max_turns=2,
            plan_file=plan,
        )
        == 0
    )

    events = [
        json.loads(line)["event"]
        for line in checkpoint_path.read_text(encoding="utf-8").splitlines()
    ]
    assert events == ["STARTING", "TIMED_OUT", "RECOVERY_FINISHED"]
    assert "STATUS: RECOVERED" in capsys.readouterr().out


def test_run_implementer_accepts_success_with_transaction_evidence(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "repo")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "report.md"
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, report_path)
    observed: dict[str, object] = {}
    real_run = MODULE.subprocess.run

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        (repo / "implemented.py").write_text("IMPLEMENTED = True\n", encoding="utf-8")
        report_path.write_text("pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
        real_run(["git", "-C", str(repo), "add", "--", "implemented.py", "report.md"], check=True)
        real_run(["git", "-C", str(repo), "commit", "-qm", "implementation commit"], check=True)
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert MODULE.run_implementer(repo, prompt_path, plan_file=plan) == 0
    assert observed["command"] == MODULE.build_command(Path("cmdc"))
    assert capsys.readouterr().out == "pytest 1 passed\n"


def test_run_implementer_preserves_failed_process_diagnostics(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "repo")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "missing-report.md")
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    def fake_process(command, prompt_text, cwd, **kwargs):
        return SimpleNamespace(
            returncode=4, stdout="partial output", stderr="MODEL_NOT_IN_PLAN"
        )

    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        fake_process,
    )

    assert MODULE.run_implementer(repo, prompt_path, plan_file=plan) == 4
    captured = capsys.readouterr()
    assert "partial output" in captured.out
    assert "BLOCKER_CODE: MODEL_UNAVAILABLE" in captured.err
    assert "STDERR: MODEL_NOT_IN_PLAN" in captured.err


def test_run_implementer_routes_timeout_seconds_through_wall_watchdog(
    tmp_path: Path, monkeypatch
) -> None:
    """The alias feeds the same finite watchdog as --wall-timeout-seconds."""
    repo = _create_git_fixture(tmp_path / "repo")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "task-report.md")
    observed: dict[str, object] = {}
    calls = {"cmdc": 0}
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        calls["cmdc"] += 1
        observed[f"call{calls['cmdc']}"] = kwargs
        error = MODULE.subprocess.TimeoutExpired(command, timeout=0.01, stderr="max turns reached")
        error.watchdog_reason = "WALL_TIMEOUT"  # type: ignore[attr-defined]
        error.watchdog_cleanup_verified = True  # type: ignore[attr-defined]
        raise error

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=repo / "checkpoints.jsonl",
            heartbeat_interval=0,
            wall_timeout_seconds=1234,
            plan_file=plan,
        )
        == 8
    )
    assert calls["cmdc"] == 1
    kwargs = observed["call1"]
    assert kwargs["wall_timeout_seconds"] == 1234


def test_run_implementer_reports_missing_command(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "repo")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "missing-report.md")

    def missing_command(cmd_bin="cmdc"):
        raise FileNotFoundError("cmdc binary not found")

    monkeypatch.setattr(MODULE, "resolve_cmdc", missing_command)

    assert MODULE.run_implementer(repo, prompt_path, plan_file=plan) == 127
    assert "BLOCKER_CODE: CMD_NOT_FOUND" in capsys.readouterr().err


def test_run_implementer_reports_incomplete_transaction_after_zero_exit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "repo")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "missing-report.md")
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    def fake_process(command, prompt_text, cwd, **kwargs):
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        fake_process,
    )

    assert MODULE.run_implementer(repo, prompt_path, plan_file=plan) == 1
    assert "BLOCKER_CODE: TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_strict_no_commit_still_transaction_incomplete(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-strict-no-commit")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text("pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: SimpleNamespace(
            returncode=0, stdout="pytest 1 passed", stderr=""
        ),
    )

    assert (
        MODULE.run_implementer(
            repo, prompt_path, plan_file=plan, allow_no_change=False, allow_dirty=True
        )
        == 1
    )
    assert "TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_validation_only_succeeds_with_untracked_artifact_and_no_commit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-validation-only")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text("pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        (repo / "scratch-note.txt").write_text("untracked\n", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            allow_no_change=True,
            plan_file=plan,
            allow_dirty=True,
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "TRANSACTION_INCOMPLETE" not in captured.err
    assert checkpoint_path.is_file()
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8").splitlines()[-1])
    assert checkpoint["state"] == "CHECKPOINT"
    assert checkpoint["snapshot"]["validation_only"] is True
    assert checkpoint["snapshot"]["commits_since_baseline"] == []
    assert checkpoint["snapshot"]["report_exists"] is True
    assert checkpoint["snapshot"]["tests_detectable"] is True


def test_validation_only_accepts_documented_known_test_failures(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-validation-known-failures")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text(
        "pytest: 77 passed, 7 failed\n"
        "The 7 pre-existing failures are accepted as out-of-scope.\n",
        encoding="utf-8",
    )
    prompt_path = _write_prompt(tmp_path, report_path)
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: SimpleNamespace(
            returncode=0, stdout="pytest 77 passed, 7 failed", stderr=""
        ),
    )

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            allow_no_change=True,
            allow_known_test_failures=True,
            plan_file=plan,
            allow_dirty=True,
        )
        == 0
    )
    assert "TRANSACTION_INCOMPLETE" not in capsys.readouterr().err


def test_known_failure_acceptance_requires_positive_disposition() -> None:
    accepted = (
        "pytest: 77 passed, 7 failed\n"
        "The 7 pre-existing failures are accepted as out-of-scope.\n"
    )
    assert MODULE._has_known_failure_test_evidence(accepted) is True

    # A bare disposition token without a positive declaration is not enough.
    bare = "pytest: 77 passed, 7 failed\n7 pre-existing failures\n"
    assert MODULE._has_known_failure_test_evidence(bare) is False

    # Positive declaration without a disposition token is not enough.
    no_disposition = "pytest: 77 passed, 7 failed\nfailures accepted\n"
    assert MODULE._has_known_failure_test_evidence(no_disposition) is False

    # A passing run is not a known-failure run.
    passing = "pytest: 77 passed\npre-existing failures accepted\n"
    assert MODULE._has_known_failure_test_evidence(passing) is False

    # An unrelated failure with an accepted marker is not a documented known
    # failure: the failure must be tied to the disposition token.
    unrelated = (
        "pytest: 77 passed, 7 failed\n"
        "The 7 unrelated failures are accepted.\n"
    )
    assert MODULE._has_known_failure_test_evidence(unrelated) is False

    same_count_unscoped = (
        "pytest: 77 passed, 7 failed\n"
        "The 7 pre-existing failures are accepted as out-of-scope.\n"
        "pytest: 77 passed, 7 failed\n"
    )
    assert MODULE._has_known_failure_test_evidence(same_count_unscoped) is False


def test_validation_only_rejects_unrelated_known_token_failures(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-validation-unrelated-failures")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text(
        "pytest: 77 passed, 7 failed\n"
        "The 7 unrelated failures are not accepted as out-of-scope.\n",
        encoding="utf-8",
    )
    prompt_path = _write_prompt(tmp_path, report_path)
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: SimpleNamespace(
            returncode=0, stdout="pytest 77 passed, 7 failed", stderr=""
        ),
    )

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            allow_no_change=True,
            allow_known_test_failures=True,
            plan_file=plan,
            allow_dirty=True,
        )
        == 1
    )
    assert "TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_recovery_uses_fresh_activity_deadline(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-recovery-fresh-deadline")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    prompt_path = _write_prompt(tmp_path, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"
    observed: dict[str, object] = {}
    process_calls: list[int] = []

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        process_calls.append(1)
        call = len(process_calls)
        observed[f"call{call}_activity_started"] = float(
            kwargs["activity_state"]["started"]
        )
        if call == 1:
            (repo / "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
            raise MODULE.subprocess.TimeoutExpired(
                command, timeout=0.01, stderr="max turns reached"
            )
        report_path.write_text("Tests: pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(repo), "add", "--", "partial.py", "task-report.md"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-qm", "recovery commit"],
            check=True,
        )
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            heartbeat_interval=0,
            recovery_max_turns=2,
            plan_file=plan,
        )
        == 0
    )

    events = [
        json.loads(line)["event"]
        for line in checkpoint_path.read_text(encoding="utf-8").splitlines()
    ]
    assert events == ["STARTING", "TIMED_OUT", "RECOVERY_FINISHED"]
    assert "STATUS: RECOVERED" in capsys.readouterr().out
    # The recovery process received an activity state with a fresh started
    # baseline, not the primary run's wall-clock origin.
    assert observed["call1_activity_started"] != observed["call2_activity_started"]


def test_recovery_receives_its_own_activity_state_and_fingerprint(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-recovery-fresh-state")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    prompt_path = _write_prompt(tmp_path, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"
    observed: dict[str, object] = {}
    process_calls: list[int] = []

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        process_calls.append(1)
        call = len(process_calls)
        observed[f"call{call}_activity"] = kwargs["activity_state"]
        observed[f"call{call}_activity_events"] = int(
            kwargs["activity_state"].get("events_seen", 0)
        )
        if call == 1:
            (repo / "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
            raise MODULE.subprocess.TimeoutExpired(
                command, timeout=0.01, stderr="max turns reached"
            )
        report_path.write_text("Tests: pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(repo), "add", "--", "partial.py", "task-report.md"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-qm", "recovery commit"],
            check=True,
        )
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    # The recovery phase collects a fresh snapshot with the partial file and
    # the recovery commit, so the recovered checkpoint records the commit.
    snapshots = iter(
        [
            {
                "git_root": str(repo),
                "head": "timeout-head",
                "status": [f" M {repo / 'partial.py'}"],
                "diff_present": True,
                "commits_since_baseline": [],
                "report_exists": False,
                "report_path": str(report_path),
                "tests_detectable": True,
                "state": "IMPLEMENTATION INCOMPLETE",
            },
            {
                "git_root": str(repo),
                "head": "timeout-head",
                "status": [f" M {repo / 'partial.py'}"],
                "diff_present": True,
                "commits_since_baseline": [],
                "report_exists": False,
                "report_path": str(report_path),
                "tests_detectable": True,
                "state": "IMPLEMENTATION INCOMPLETE",
            },
            {
                "git_root": str(repo),
                "head": "recovery-head-2",
                "status": [],
                "diff_present": False,
                "commits_since_baseline": ["recovery-commit"],
                "report_exists": True,
                "report_path": str(report_path),
                "tests_detectable": True,
                "state": "IMPLEMENTATION INCOMPLETE",
            },
        ]
    )

    def collect_snapshot(*args, **kwargs):
        return next(snapshots)

    monkeypatch.setattr(MODULE, "collect_workspace_snapshot", collect_snapshot)

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            heartbeat_interval=0,
            recovery_max_turns=2,
            plan_file=plan,
        )
        == 0
    )

    primary_state = observed["call1_activity"]
    recovery_state = observed["call2_activity"]
    assert recovery_state is not primary_state
    # The recovery state is a fresh, empty activity baseline: no events carried
    # over from the primary run.
    assert observed["call1_activity_events"] == 0
    assert observed["call2_activity_events"] == 0
    assert float(recovery_state["started"]) >= float(primary_state["started"])


def test_unverified_watchdog_cleanup_blocks_before_recovery(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-unverified-cleanup")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    prompt_path = _write_prompt(tmp_path, report_path)
    checkpoint_path = repo / "checkpoints.jsonl"
    calls = {"cmdc": 0}
    real_run = MODULE.subprocess.run

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        calls["cmdc"] += 1
        if calls["cmdc"] == 1:
            (repo / "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
            error = MODULE.subprocess.TimeoutExpired(
                command, timeout=0.01, stderr="max turns reached"
            )
            error.watchdog_reason = "WALL_TIMEOUT"  # type: ignore[attr-defined]
            error.watchdog_pid = 9999  # type: ignore[attr-defined]
            error.watchdog_cleanup_verified = False  # type: ignore[attr-defined]
            raise error
        raise AssertionError("recovery must not run while the tree is unverified")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)
    monkeypatch.setattr(
        MODULE,
        "collect_workspace_snapshot",
        lambda *args, **kwargs: {
            "head": "h1",
            "git_root": str(repo),
            "status": [],
            "diff_present": True,
            "commits_since_baseline": [],
            "report_exists": False,
            "tests_detectable": True,
            "state": "IMPLEMENTATION INCOMPLETE",
        },
    )

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            checkpoint_file=checkpoint_path,
            heartbeat_interval=0,
            recovery_max_turns=2,
            plan_file=plan,
        )
        == 8
    )

    captured = capsys.readouterr()
    assert "STATUS: BLOCKED" in captured.err
    assert "BLOCKER_CODE: WATCHDOG_CLEANUP_UNVERIFIED" in captured.err
    assert calls["cmdc"] == 1
    if checkpoint_path.exists():
        events = [
            json.loads(line)["event"]
            for line in checkpoint_path.read_text(encoding="utf-8").splitlines()
        ]
        assert events == ["STARTING"], (
            "no TIMED_OUT/recovery checkpoint may exist after an unverified kill"
        )


def test_watchdog_tree_verification_is_fail_closed_with_live_descendant(
    tmp_path: Path, monkeypatch
) -> None:
    class EmptyStream:
        def readline(self) -> str:
            return ""

        def close(self) -> None:
            return None

    class FakeStdin:
        def write(self, value: str) -> None:
            return None

        def close(self) -> None:
            return None

    class FakeProcess:
        pid = 4242
        returncode = None

        def __init__(self) -> None:
            self.stdin = FakeStdin()
            self.stdout = EmptyStream()
            self.stderr = EmptyStream()

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            self.returncode = 1
            return self.returncode

    process = FakeProcess()
    monkeypatch.setattr(MODULE.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(MODULE, "_terminate_process_tree", lambda pid: None)
    monkeypatch.setattr(MODULE, "_process_tree_alive", lambda pid: True)
    started = time.monotonic()
    activity_state = {
        "lock": MODULE.threading.Lock(),
        "started": started,
        "last_activity": started,
        "last_event": started,
        "last_workspace": started,
        "events_seen": 0,
    }

    try:
        MODULE._run_cmdc_process(
            ["cmdc"],
            "prompt",
            tmp_path,
            wall_timeout_seconds=0.01,
            stall_timeout_seconds=60,
            activity_state=activity_state,
        )
    except MODULE.subprocess.TimeoutExpired as error:
        assert getattr(error, "watchdog_reason") == "WALL_TIMEOUT"
        assert getattr(error, "watchdog_cleanup_verified") is False
    else:
        raise AssertionError("watchdog did not stop the process")


def test_clean_watchdog_tree_verification_is_verified(
    tmp_path: Path, monkeypatch
) -> None:
    class EmptyStream:
        def readline(self) -> str:
            return ""

        def close(self) -> None:
            return None

    class FakeStdin:
        def write(self, value: str) -> None:
            return None

        def close(self) -> None:
            return None

    class FakeProcess:
        pid = 4243
        returncode = None

        def __init__(self) -> None:
            self.stdin = FakeStdin()
            self.stdout = EmptyStream()
            self.stderr = EmptyStream()

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            self.returncode = 1
            return self.returncode

    process = FakeProcess()
    monkeypatch.setattr(MODULE.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(MODULE, "_terminate_process_tree", lambda pid: None)
    monkeypatch.setattr(MODULE, "_process_tree_alive", lambda pid: False)
    started = time.monotonic()
    activity_state = {
        "lock": MODULE.threading.Lock(),
        "started": started,
        "last_activity": started,
        "last_event": started,
        "last_workspace": started,
        "events_seen": 0,
    }

    try:
        MODULE._run_cmdc_process(
            ["cmdc"],
            "prompt",
            tmp_path,
            wall_timeout_seconds=0.01,
            stall_timeout_seconds=60,
            activity_state=activity_state,
        )
    except MODULE.subprocess.TimeoutExpired as error:
        assert getattr(error, "watchdog_reason") == "WALL_TIMEOUT"
        assert getattr(error, "watchdog_cleanup_verified") is True
    else:
        raise AssertionError("watchdog did not stop the process")


def test_validation_only_blocked_when_report_absent(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-validation-no-report")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_path = _write_prompt(tmp_path, repo / "task-report.md")
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: SimpleNamespace(
            returncode=0, stdout="pytest 1 passed", stderr=""
        ),
    )

    assert (
        MODULE.run_implementer(
            repo, prompt_path, allow_no_change=True, plan_file=plan, allow_dirty=True
        )
        == 1
    )
    assert "TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_validation_only_blocked_when_test_evidence_absent(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-validation-no-tests")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text("STATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: SimpleNamespace(
            returncode=0, stdout="no test output", stderr=""
        ),
    )

    assert (
        MODULE.run_implementer(
            repo, prompt_path, allow_no_change=True, plan_file=plan, allow_dirty=True
        )
        == 1
    )
    assert "TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_validation_only_blocked_when_tracked_change_exists(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-validation-tracked")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text("pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        (repo / "tracked.py").write_text("VALUE = 99\n", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo, prompt_path, allow_no_change=True, plan_file=plan, allow_dirty=True
        )
        == 1
    )
    assert "TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_validation_only_blocked_when_commit_exists(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-validation-commit")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    report_path = repo / "task-report.md"
    report_path.write_text("pytest 1 passed\nSTATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    real_run = MODULE.subprocess.run
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        (repo / "extra.py").write_text("X = 1\n", encoding="utf-8")
        real_run(["git", "-C", str(repo), "add", "--", "extra.py", "task-report.md"], check=True)
        real_run(["git", "-C", str(repo), "commit", "-qm", "should not happen"], check=True)
        return SimpleNamespace(returncode=0, stdout="pytest 1 passed", stderr="")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert (
        MODULE.run_implementer(
            repo, prompt_path, allow_no_change=True, plan_file=plan, allow_dirty=True
        )
        == 1
    )
    assert "TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_cli_help_exposes_allow_no_change_flag() -> None:
    import subprocess
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "--allow-no-change" in result.stdout
    assert "--allow-known-test-failures" in result.stdout


def test_cli_help_exposes_timeout_seconds_alias() -> None:
    import subprocess
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--wall-timeout-seconds" in result.stdout
    assert "--timeout-seconds" in result.stdout
    assert "--wall-timeout-seconds" in result.stdout.split(
        "--timeout-seconds"
    )[0], "the alias must be listed next to the canonical wall-timeout option"


def test_cli_accepts_timeout_seconds_alias_and_rejects_non_positive_values() -> None:
    import subprocess
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--timeout-seconds" in result.stdout
    # An explicit alias value parses; the same value also parses through the
    # canonical spelling, proving both flags share one parsing destination.
    for flag in ("--timeout-seconds", "--wall-timeout-seconds"):
        parsed = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--prompt-file", "prompt.md", flag, "3600", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert parsed.returncode == 0, f"{flag} did not parse"
    # Non-positive values are rejected by the shared argparse constraint.
    for value in ("0", "-1", "-900"):
        rejected = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--prompt-file", "prompt.md", "--timeout-seconds", value],
            capture_output=True,
            text=True,
            check=False,
        )
        assert rejected.returncode == 2, f"--timeout-seconds {value} was accepted"
        assert "must be a positive integer" in rejected.stderr


def test_cli_alias_populates_shared_wall_timeout_destination(monkeypatch) -> None:
    """Both spellings populate the argparse destination main() forwards into
    the process-runner watchdog, with the exact value from the command line.

    Unlike the --help checks, this drives the real parser and main() entry
    point, so it fails when the alias registration is absent instead of only
    proving option recognition.
    """
    received: list[int] = []

    def fake_run_implementer(*args, **kwargs):
        received.append(int(kwargs["wall_timeout_seconds"]))
        return 0

    monkeypatch.setattr(MODULE, "run_implementer", fake_run_implementer)
    for flag in ("--timeout-seconds", "--wall-timeout-seconds"):
        monkeypatch.setattr(
            MODULE.sys,
            "argv",
            [
                "cmdc-implementer.py",
                "--prompt-file",
                "prompt.md",
                "--plan-file",
                "plan.md",
                flag,
                "1234",
            ],
        )
        assert MODULE.main() == 0

    # Both spellings reach the single watchdog destination used by the
    # process runner, carrying the exact command-line value.
    assert received == [1234, 1234]


def test_windows_tree_verification_is_fail_closed(monkeypatch) -> None:
    """The Windows process-group helper walks parent links and stays
    fail-closed when a process cannot be resolved."""
    # A chain ending at a known root (parent 0). A PID with no entry is
    # unknown (returns None from _windows_parent_pid).
    parent_map = {500: 400, 400: 300, 300: 200, 200: 0}
    monkeypatch.setattr(
        MODULE, "_windows_parent_pid", lambda pid: parent_map.get(pid)
    )

    # A descendant whose ancestor chain reaches the leader is a member.
    assert MODULE._windows_pid_in_group(500, 300) is True
    # The leader itself is always a member.
    assert MODULE._windows_pid_in_group(300, 300) is True
    # A process on a fully-resolved chain that never reaches the leader is a
    # known non-member.
    assert MODULE._windows_pid_in_group(500, 600) is False
    # A process whose parent cannot be resolved is treated as a member so
    # cleanup verification fails closed.
    assert MODULE._windows_pid_in_group(900, 300) is True


def test_review_windows_tree_verification_is_fail_closed(monkeypatch) -> None:
    """The review launcher's Windows helper has the same fail-closed semantics."""
    parent_map = {500: 400, 400: 300, 300: 200, 200: 0}
    monkeypatch.setattr(
        REVIEW, "_windows_parent_pid", lambda pid: parent_map.get(pid)
    )

    assert REVIEW._windows_pid_in_group(500, 300) is True
    assert REVIEW._windows_pid_in_group(300, 300) is True
    assert REVIEW._windows_pid_in_group(500, 600) is False
    assert REVIEW._windows_pid_in_group(900, 300) is True


def test_review_timeout_cleanup_verifies_full_process_tree(
    tmp_path: Path, monkeypatch
) -> None:
    """A leader that exits while a descendant survives is ORPHANED, not clean."""

    class FakeStream:
        def readline(self) -> str:
            return ""

        def close(self) -> None:
            return None

    class FakeStdin:
        def write(self, value: str) -> None:
            return None

        def close(self) -> None:
            return None

    class FakeProcess:
        pid = 7777
        returncode = None

        def __init__(self) -> None:
            self.stdin = FakeStdin()
            self.stdout = FakeStream()
            self.stderr = FakeStream()

        def communicate(self, input=None, timeout=None):
            if timeout is not None:
                raise REVIEW.subprocess.TimeoutExpired("cmd", timeout)
            return ("", "")

    process = FakeProcess()
    # The leader is gone but the tree check still finds a descendant.
    monkeypatch.setattr(REVIEW, "_terminate_tree", lambda pid: None)
    monkeypatch.setattr(REVIEW, "_process_tree_alive", lambda pid: True)
    monkeypatch.setattr(REVIEW.subprocess, "Popen", lambda *a, **k: process)

    result = REVIEW._run_process(
        ["codex"],
        "prompt",
        timeout_seconds=0.01,
    )

    assert result.timed_out is True
    assert result.orphaned is True
    assert result.cleanup_failed is False
    assert result.drain_verified is False


def test_review_timeout_cleanup_verified_with_clean_tree(
    tmp_path: Path, monkeypatch
) -> None:
    """A fully absent tree yields a verified clean cleanup."""

    class FakeStream:
        def readline(self) -> str:
            return ""

        def close(self) -> None:
            return None

    class FakeStdin:
        def write(self, value: str) -> None:
            return None

        def close(self) -> None:
            return None

    class FakeProcess:
        pid = 7778
        returncode = None

        def __init__(self) -> None:
            self.stdin = FakeStdin()
            self.stdout = FakeStream()
            self.stderr = FakeStream()
            self.calls = 0

        def communicate(self, input=None, timeout=None):
            self.calls += 1
            if self.calls == 1:
                raise REVIEW.subprocess.TimeoutExpired("cmd", timeout)
            return ("drained-out", "drained-err")

    process = FakeProcess()
    monkeypatch.setattr(REVIEW, "_terminate_tree", lambda pid: None)
    monkeypatch.setattr(REVIEW, "_process_tree_alive", lambda pid: False)
    monkeypatch.setattr(REVIEW.subprocess, "Popen", lambda *a, **k: process)

    result = REVIEW._run_process(
        ["codex"],
        "prompt",
        timeout_seconds=0.01,
    )

    assert result.timed_out is True
    assert result.orphaned is False
    assert result.cleanup_failed is False
    assert result.drain_verified is True
    assert "drained-out" in result.stdout
    assert "drained-err" in result.stderr


def test_review_timeout_preserves_final_drain_output(
    tmp_path: Path, monkeypatch
) -> None:
    """Output produced after the timeout is drained and preserved."""
    captured: dict[str, str] = {}

    class FakeStream:
        def readline(self) -> str:
            return ""

        def close(self) -> None:
            return None

    class FakeStdin:
        def write(self, value: str) -> None:
            return None

        def close(self) -> None:
            return None

    class FakeProcess:
        pid = 7779
        returncode = None

        def __init__(self) -> None:
            self.stdin = FakeStdin()
            self.stdout = FakeStream()
            self.stderr = FakeStream()

        def communicate(self, input=None, timeout=None):
            if timeout is not None:
                raise REVIEW.subprocess.TimeoutExpired(
                    "cmd", timeout, output="drained-out", stderr="drained-err"
                )
            return ("", "")

    process = FakeProcess()
    monkeypatch.setattr(REVIEW, "_terminate_tree", lambda pid: None)
    monkeypatch.setattr(REVIEW, "_process_tree_alive", lambda pid: False)
    monkeypatch.setattr(REVIEW.subprocess, "Popen", lambda *a, **k: process)

    result = REVIEW._run_process(
        ["codex"],
        "prompt",
        timeout_seconds=0.01,
    )

    # The exc already carried some partial output; the final drain bytes are
    # appended to it instead of being discarded.
    assert "drained-out" in result.stdout
    assert "drained-err" in result.stderr


def test_failed_child_process_keeps_mode_and_full_initial_git_state(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A failed child process after a valid preflight retains the selected
    mode and the complete initial Git snapshot through the real diagnostic
    rendering path, not only the process details."""
    repo = _create_git_fixture(tmp_path / "fixture-failed-process-enrichment")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "missing-report.md")
    # A pre-existing tracked change makes the raw status lines observable in
    # the initial snapshot carried by the diagnostic.
    (repo / "tracked.py").write_text("VALUE = 2\n", encoding="utf-8")
    expected_status = subprocess.run(
        ["git", "-C", str(repo), "status", "--short", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: SimpleNamespace(
            returncode=4, stdout="partial output", stderr="MODEL_NOT_IN_PLAN"
        ),
    )

    assert (
        MODULE.run_implementer(repo, prompt_path, plan_file=plan, allow_dirty=True)
        == 4
    )
    captured = capsys.readouterr()
    assert "BLOCKER_CODE: MODEL_UNAVAILABLE" in captured.err
    assert "MODE: normal" in captured.err
    # The full initial snapshot rides in the rendered diagnostic, including
    # the canonical root, branch, HEAD, and every raw status line.
    state = json.loads(captured.err.split("INITIAL_GIT_STATE: ", 1)[1].strip())
    assert state["git_root"] == str(repo.resolve())
    assert state["branch"] == "feature"
    assert state["head"] == subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert state["status"] == expected_status
    assert " M tracked.py" in state["status"]
    assert "MODE" in captured.err and "INITIAL_GIT_STATE" in captured.err


def test_failed_child_process_yolo_mode_keeps_full_initial_git_state(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The selected yolo mode is preserved through the same real path."""
    repo = _create_git_fixture(tmp_path / "fixture-failed-process-yolo-enrichment")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "missing-report.md")
    expected_status = subprocess.run(
        ["git", "-C", str(repo), "status", "--short", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: SimpleNamespace(
            returncode=1, stdout="", stderr="unexpected failure"
        ),
    )

    assert (
        MODULE.run_implementer(
            repo,
            prompt_path,
            plan_file=plan,
            allow_cmdc_yolo=True,
            allow_dirty=True,
        )
        == 1
    )
    captured = capsys.readouterr()
    assert "BLOCKER_CODE: PROCESS_FAILED" in captured.err
    assert "MODE: yolo" in captured.err
    state = json.loads(captured.err.split("INITIAL_GIT_STATE: ", 1)[1].strip())
    assert state["git_root"] == str(repo.resolve())
    assert state["branch"] == "feature"
    assert state["head"] == subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert state["status"] == expected_status


def test_cmd_not_found_after_preflight_keeps_mode_and_full_initial_git_state(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A missing CMDc binary after a valid preflight keeps the selected mode
    and the complete initial Git snapshot in the rendered diagnostic."""
    repo = _create_git_fixture(tmp_path / "fixture-cmd-not-found-enrichment")
    plan = repo / "plan.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(repo), "add", "--", "plan.md"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "plan"], check=True
    )
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "missing-report.md")
    # A pre-existing tracked change makes the raw status lines observable in
    # the initial snapshot carried by the diagnostic.
    (repo / "tracked.py").write_text("VALUE = 2\n", encoding="utf-8")
    expected_status = subprocess.run(
        ["git", "-C", str(repo), "status", "--short", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def missing_command(command, prompt_text, cwd, **kwargs):
        raise FileNotFoundError("cmdc binary not found")

    monkeypatch.setattr(MODULE, "_run_cmdc_process", missing_command)

    assert (
        MODULE.run_implementer(repo, prompt_path, plan_file=plan, allow_dirty=True)
        == 127
    )
    captured = capsys.readouterr()
    assert "BLOCKER_CODE: CMD_NOT_FOUND" in captured.err
    assert "MODE: normal" in captured.err
    # The full initial snapshot rides in the rendered diagnostic.
    state = json.loads(captured.err.split("INITIAL_GIT_STATE: ", 1)[1].strip())
    assert state["git_root"] == str(repo.resolve())
    assert state["branch"] == "feature"
    assert state["head"] == subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert state["status"] == expected_status
    assert " M tracked.py" in state["status"]
