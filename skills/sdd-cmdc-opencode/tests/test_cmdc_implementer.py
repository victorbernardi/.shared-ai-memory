from __future__ import annotations

import importlib.util
import json
import subprocess
import time
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
        "100",
        "--output-format",
        "json",
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
    prompt_path = _write_prompt(tmp_path, tmp_path / "task-report.md")
    monkeypatch.setattr(
        MODULE,
        "collect_workspace_snapshot",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("git root unavailable")
        ),
    )

    def cmdc_must_not_run(*args, **kwargs):
        raise AssertionError("cmdc must not run without a Git baseline")

    monkeypatch.setattr(MODULE.subprocess, "run", cmdc_must_not_run)

    assert MODULE.run_implementer(tmp_path, prompt_path) == 1
    captured = capsys.readouterr()
    assert "BLOCKER_CODE: WORKSPACE_INSPECTION_FAILED" in captured.err
    assert "git root unavailable" in captured.err


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
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_process(command, prompt_text, cwd, **kwargs):
        Path(cwd, "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
        raise MODULE.subprocess.TimeoutExpired(
            command, timeout=0.01, stderr="max turns reached"
        )

    monkeypatch.setattr(MODULE, "_run_cmdc_process", fake_process)

    assert MODULE.run_implementer(repo, prompt_path, max_turns=1) == 8

    captured = capsys.readouterr()
    assert "STATUS: IMPLEMENTATION INCOMPLETE" in captured.err
    assert "WORKSPACE_DIFF: true" in captured.err
    assert "REPORT_EXISTS: false" in captured.err


def test_stall_is_incomplete_without_automatic_recovery(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-stall")
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
        MODULE,
        "_run_cmdc_process",
        lambda command, prompt_text, cwd, **kwargs: (_ for _ in ()).throw(
            MODULE.subprocess.TimeoutExpired(command, timeout=0.01, stderr="max turns")
        ),
    )

    assert MODULE.run_implementer(tmp_path, prompt_path, max_turns=1) == 8
    captured = capsys.readouterr()
    assert "STATUS: BLOCKED" in captured.err
    assert "BLOCKER_CODE: TIMEOUT" in captured.err
    assert "git status unavailable" in captured.err


def test_success_writes_starting_and_finished_checkpoints(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-checkpoint-lifecycle")
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

    assert MODULE.run_implementer(repo, prompt_path) == 1
    assert "TRANSACTION_INCOMPLETE" in capsys.readouterr().err


def test_long_run_emits_heartbeat_with_command_and_workspace_snapshot(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _create_git_fixture(tmp_path / "fixture-heartbeat")
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

    assert MODULE.run_implementer(repo, prompt_path) == 0
    assert observed["command"] == MODULE.build_command(Path("cmdc"))
    assert capsys.readouterr().out == "pytest 1 passed\n"


def test_run_implementer_preserves_failed_process_diagnostics(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "repo")
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

    assert MODULE.run_implementer(repo, prompt_path) == 4
    captured = capsys.readouterr()
    assert "partial output" in captured.out
    assert "BLOCKER_CODE: MODEL_UNAVAILABLE" in captured.err
    assert "STDERR: MODEL_NOT_IN_PLAN" in captured.err


def test_run_implementer_reports_missing_command(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "repo")
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    prompt_path = _write_prompt(prompt_dir, repo / "missing-report.md")

    def missing_command(cmd_bin="cmdc"):
        raise FileNotFoundError("cmdc binary not found")

    monkeypatch.setattr(MODULE, "resolve_cmdc", missing_command)

    assert MODULE.run_implementer(repo, prompt_path) == 127
    assert "BLOCKER_CODE: CMD_NOT_FOUND" in capsys.readouterr().err


def test_run_implementer_reports_incomplete_transaction_after_zero_exit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _create_git_fixture(tmp_path / "repo")
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

    assert MODULE.run_implementer(repo, prompt_path) == 1
    assert "BLOCKER_CODE: TRANSACTION_INCOMPLETE" in capsys.readouterr().err
