from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from tests.helpers.process_tree import descendant_fixture_command, fixture_command


def test_process_request_is_immutable(tmp_path: Path) -> None:
    from sdd_cmdc_opencode.process_supervisor import ProcessRequest

    request = ProcessRequest(command=(sys.executable, "-V"), cwd=tmp_path)
    with pytest.raises(FrozenInstanceError):
        request.cwd = tmp_path.parent  # type: ignore[misc]


def test_package_exports_the_public_process_and_cmdc_interfaces() -> None:
    import sdd_cmdc_opencode as package

    assert set(package.__all__) == {
        "ProcessFailure",
        "ProcessOutcome",
        "ProcessRequest",
        "ProcessStatus",
        "StreamEvent",
        "run_process",
        "CmdcEvent",
        "CmdcLocal",
        "CmdcLocalError",
        "CmdcOutcome",
        "CmdcPreflight",
        "CmdcRequest",
        "Blocker",
        "ExecutionPolicy",
        "PlanProvenance",
        "RecoveryEvidence",
        "ReviewPolicy",
        "RunContract",
        "RunLineage",
        "RunRecord",
        "RunRecordError",
        "RunResult",
        "RunStatus",
        "ScopeContract",
        "SuccessPolicy",
        "TaskContract",
        "TestEvidence",
        "WorkspaceContract",
        "workspace_fingerprint",
        "NO_IMPLEMENTATION_PROGRESS",
        "ExecutionLifecycle",
        "LifecycleError",
        "ProgressAssessment",
        "ProgressSignal",
        "append_event_records",
        "classify_progress_event",
        "default_progress_deadline",
        "evaluate_progress",
        "normalize_test_evidence",
        "persist_progress_checkpoint",
    }
    assert "_windows_job" not in package.__all__


def test_normal_exit_streams_output_and_proves_drain_and_cleanup(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    seen = []
    outcome = run_process(
        ProcessRequest(command=fixture_command(), cwd=tmp_path),
        on_output=seen.append,
    )

    assert outcome.status is ProcessStatus.EXITED
    assert outcome.returncode == 0
    assert outcome.stdout == "out-one\n"
    assert outcome.stderr == "err-one\n"
    assert [event.stream for event in seen] == ["stdout", "stderr"]
    assert [event.text for event in seen] == ["out-one\n", "err-one\n"]
    assert outcome.drain_verified is True
    assert outcome.cleanup_verified is True
    assert outcome.primary_failure is None
    assert outcome.secondary_failures == ()


def test_cleanup_failures_are_secondary_after_a_normal_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sdd_cmdc_opencode import process_supervisor as supervisor
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessFailure,
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    cleanup_failure = ProcessFailure(
        code="PROCESS_TREE_TERMINATION_FAILED",
        phase="cleanup",
        message="synthetic cleanup failure",
    )
    monkeypatch.setattr(
        supervisor,
        "_contained_state",
        lambda _process, _pid, _containment, _job=None: True,
    )
    monkeypatch.setattr(
        supervisor,
        "_terminate_contained",
        lambda _process, _pid, _containment, _job=None: (
            False,
            (cleanup_failure,),
        ),
    )

    outcome = run_process(ProcessRequest(command=fixture_command(), cwd=tmp_path))

    assert outcome.status is ProcessStatus.EXITED
    assert outcome.primary_failure is None
    assert outcome.secondary_failures == (cleanup_failure,)
    assert outcome.cleanup_verified is False


def test_reader_failures_are_secondary_after_a_normal_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sdd_cmdc_opencode import process_supervisor as supervisor
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    def failing_reader(stream_name, _stream, _output_queue, done, errors) -> None:
        errors.put((stream_name, RuntimeError("synthetic reader failure")))
        done.set()

    monkeypatch.setattr(supervisor, "_reader", failing_reader)

    outcome = run_process(ProcessRequest(command=fixture_command(), cwd=tmp_path))

    assert outcome.status is ProcessStatus.EXITED
    assert outcome.primary_failure is None
    assert [failure.code for failure in outcome.secondary_failures] == [
        "PROCESS_STREAM_READ_FAILED",
        "PROCESS_STREAM_READ_FAILED",
    ]


def test_missing_executable_is_a_spawn_failure_without_cleanup_failure(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    outcome = run_process(
        ProcessRequest(
            command=(str(tmp_path / "does-not-exist"),),
            cwd=tmp_path,
        )
    )

    assert outcome.status is ProcessStatus.SPAWN_FAILED
    assert outcome.primary_failure is not None
    assert outcome.primary_failure.code == "PROCESS_SPAWN_FAILED"
    assert outcome.pid is None
    assert outcome.cleanup_verified is True
    assert outcome.drain_verified is True
    assert outcome.secondary_failures == ()


def test_wall_timeout_preserves_emitted_output_and_cleanup_proof(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    outcome = run_process(
        ProcessRequest(
            command=fixture_command("--wait", "10"),
            cwd=tmp_path,
            wall_timeout_seconds=1.0,
            stall_timeout_seconds=5,
        )
    )

    assert outcome.status is ProcessStatus.WALL_TIMEOUT
    assert outcome.primary_failure is not None
    assert outcome.primary_failure.code == "WALL_TIMEOUT"
    assert "out-one\n" in outcome.stdout
    assert "err-one\n" in outcome.stderr
    assert outcome.drain_verified is True
    assert outcome.cleanup_verified is True


def test_stall_timeout_preserves_emitted_output_and_cleanup_proof(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    outcome = run_process(
        ProcessRequest(
            command=fixture_command("--wait", "10"),
            cwd=tmp_path,
            wall_timeout_seconds=5,
            stall_timeout_seconds=1.0,
        )
    )

    assert outcome.status is ProcessStatus.STALLED
    assert outcome.primary_failure is not None
    assert outcome.primary_failure.code == "STALLED"
    assert "out-one\n" in outcome.stdout
    assert "err-one\n" in outcome.stderr
    assert outcome.drain_verified is True
    assert outcome.cleanup_verified is True


def test_activity_clock_extends_stall_deadline_until_external_activity_stops(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    started = time.monotonic()

    def activity_clock() -> float:
        now = time.monotonic()
        return now if now - started < 0.45 else started

    outcome = run_process(
        ProcessRequest(
            command=fixture_command("--wait", "10"),
            cwd=tmp_path,
            wall_timeout_seconds=5,
            stall_timeout_seconds=0.2,
        ),
        activity_clock=activity_clock,
    )

    assert outcome.status is ProcessStatus.STALLED
    assert outcome.primary_failure is not None
    assert outcome.primary_failure.code == "STALLED"
    assert outcome.drain_verified is True
    assert outcome.cleanup_verified is True


def test_callback_exceptions_are_not_swallowed_and_process_is_cleaned_up(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessCallbackError,
        ProcessRequest,
        run_process,
    )

    def fail_on_output(_event: object) -> None:
        raise RuntimeError("callback failed")

    with pytest.raises(ProcessCallbackError, match="callback failed") as error:
        run_process(
            ProcessRequest(
                command=fixture_command("--wait", "10"),
                cwd=tmp_path,
            ),
            on_output=fail_on_output,
        )

    assert error.value.outcome.cleanup_verified is True
    assert error.value.outcome.drain_verified is True
    assert error.value.outcome.primary_failure is not None
    assert error.value.outcome.primary_failure.code == "PROCESS_OUTPUT_CALLBACK_FAILED"


def test_keyboard_interrupt_callback_preserves_interrupt_and_cleanup_evidence(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessCallbackError,
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    def interrupt_on_output(_event: object) -> None:
        raise KeyboardInterrupt("callback interrupted")

    with pytest.raises(ProcessCallbackError, match="callback interrupted") as error:
        run_process(
            ProcessRequest(
                command=fixture_command("--wait", "10"),
                cwd=tmp_path,
            ),
            on_output=interrupt_on_output,
        )

    assert error.value.outcome.status is ProcessStatus.INTERRUPTED
    assert error.value.outcome.cleanup_verified is True
    assert error.value.outcome.drain_verified is True
    assert error.value.outcome.primary_failure is not None
    assert error.value.outcome.primary_failure.code == "INTERRUPTED"


def test_callback_failure_reports_unverified_cleanup_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sdd_cmdc_opencode import process_supervisor as supervisor
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessCallbackError,
        ProcessFailure,
        ProcessRequest,
        run_process,
    )

    cleanup_failure = ProcessFailure(
        code="PROCESS_TREE_TERMINATION_FAILED",
        phase="cleanup",
        message="synthetic cleanup failure",
    )
    monkeypatch.setattr(
        supervisor,
        "_terminate_contained",
        lambda _process, _pid, _containment, _job=None: (
            False,
            (cleanup_failure,),
        ),
    )

    def fail_on_output(_event: object) -> None:
        raise RuntimeError("callback failed")

    with pytest.raises(ProcessCallbackError) as error:
        run_process(
            ProcessRequest(
                command=fixture_command("--wait", "10"),
                cwd=tmp_path,
            ),
            on_output=fail_on_output,
        )

    assert error.value.outcome.cleanup_verified is False
    assert error.value.outcome.primary_failure is not None
    assert error.value.outcome.primary_failure.code == "PROCESS_OUTPUT_CALLBACK_FAILED"
    assert cleanup_failure in error.value.outcome.secondary_failures


def test_reader_setup_failure_is_supervision_failure_with_unverified_drain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sdd_cmdc_opencode import process_supervisor as supervisor
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        ProcessSupervisionError,
        run_process,
    )

    def fail_thread_start(_thread: object) -> None:
        raise RuntimeError("reader setup failed")

    monkeypatch.setattr(supervisor.threading.Thread, "start", fail_thread_start)

    with pytest.raises(ProcessSupervisionError, match="reader setup failed") as error:
        run_process(
            ProcessRequest(
                command=fixture_command("--wait", "10"),
                cwd=tmp_path,
            )
        )

    assert error.value.outcome.status is ProcessStatus.EXITED
    assert error.value.outcome.cleanup_verified is True
    assert error.value.outcome.drain_verified is False
    assert error.value.outcome.primary_failure is not None
    assert error.value.outcome.primary_failure.code == "PROCESS_SUPERVISION_FAILED"


@pytest.mark.skipif(os.name == "nt", reason="native Windows Job coverage is Task 2")
def test_posix_process_group_terminates_descendants_and_drains_output(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    marker = tmp_path / "pids.json"
    outcome = run_process(
        ProcessRequest(
            command=descendant_fixture_command(marker),
            cwd=tmp_path,
            wall_timeout_seconds=0.5,
            stall_timeout_seconds=5,
        )
    )

    assert outcome.status is ProcessStatus.WALL_TIMEOUT
    assert outcome.containment == "posix-process-group"
    assert outcome.cleanup_verified is True
    assert outcome.drain_verified is True
    assert "grandchild-ready\n" in outcome.stdout

    if marker.exists():
        recorded = json.loads(marker.read_text(encoding="utf-8"))
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            if all(
                not _pid_exists(int(pid)) for pid in recorded.values()
            ):
                break
            time.sleep(0.02)
        assert all(not _pid_exists(int(pid)) for pid in recorded.values())


@pytest.mark.skipif(os.name != "nt", reason="native Windows Job coverage")
def test_windows_job_terminates_child_and_grandchild_and_proves_cleanup(
    tmp_path: Path,
) -> None:
    from sdd_cmdc_opencode.process_supervisor import (
        ProcessRequest,
        ProcessStatus,
        run_process,
    )

    marker = tmp_path / "pids.json"
    outcome = run_process(
        ProcessRequest(
            command=descendant_fixture_command(marker),
            cwd=tmp_path,
            wall_timeout_seconds=1.0,
            stall_timeout_seconds=5,
        )
    )

    assert outcome.status is ProcessStatus.WALL_TIMEOUT
    assert outcome.containment == "windows-job"
    assert outcome.cleanup_verified is True
    assert outcome.drain_verified is True
    assert "grandchild-ready\n" in outcome.stdout

    recorded = json.loads(marker.read_text(encoding="utf-8"))
    assert set(recorded) == {"bootstrap", "child", "grandchild"}
    recorded_pids = [int(pid) for pid in recorded.values()]
    deadline = time.monotonic() + 1.0
    while time.monotonic() < deadline:
        if all(not _windows_pid_exists(pid) for pid in recorded_pids):
            break
        time.sleep(0.02)
    assert all(not _windows_pid_exists(pid) for pid in recorded_pids)


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _windows_pid_exists(pid: int) -> bool:
    import ctypes
    from ctypes import wintypes

    process_query_limited_information = 0x1000
    still_active = 259
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel32.OpenProcess(
        process_query_limited_information, False, pid
    )
    if not handle:
        return False
    try:
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == still_active
    finally:
        kernel32.CloseHandle(handle)
