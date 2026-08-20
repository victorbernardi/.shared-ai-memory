from __future__ import annotations

import errno
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Literal


_POLL_INTERVAL_SECONDS = 0.02
_STREAM_ORDER_GRACE_SECONDS = 0.02
_TERMINATION_GRACE_SECONDS = 0.5
_WINDOWS_TERMINATION_GRACE_SECONDS = 2.0
_DRAIN_TIMEOUT_SECONDS = 2.0
_THREAD_JOIN_TIMEOUT_SECONDS = 0.5

__all__ = [
    "ProcessFailure",
    "ProcessOutcome",
    "ProcessRequest",
    "ProcessStatus",
    "StreamEvent",
    "run_process",
]


class ProcessStatus(str, Enum):
    EXITED = "EXITED"
    SPAWN_FAILED = "SPAWN_FAILED"
    WALL_TIMEOUT = "WALL_TIMEOUT"
    STALLED = "STALLED"
    INTERRUPTED = "INTERRUPTED"


@dataclass(frozen=True)
class ProcessFailure:
    code: str
    phase: str
    message: str


@dataclass(frozen=True)
class ProcessRequest:
    command: tuple[str, ...]
    cwd: Path
    stdin_text: str = ""
    wall_timeout_seconds: float = 0
    stall_timeout_seconds: float = 0
    env: Mapping[str, str] | None = None


@dataclass(frozen=True)
class StreamEvent:
    stream: Literal["stdout", "stderr"]
    text: str
    elapsed_seconds: float


@dataclass(frozen=True)
class ProcessOutcome:
    pid: int | None
    returncode: int | None
    stdout: str
    stderr: str
    status: ProcessStatus
    containment: str
    cleanup_verified: bool
    drain_verified: bool
    primary_failure: ProcessFailure | None
    secondary_failures: tuple[ProcessFailure, ...]


@dataclass(frozen=True)
class _QueuedOutput:
    stream: Literal["stdout", "stderr"]
    text: str
    timestamp: float


@dataclass(frozen=True)
class _SpawnResult:
    process: subprocess.Popen[str] | None
    job: Any | None
    primary_failure: ProcessFailure | None
    secondary_failures: tuple[ProcessFailure, ...]


def _platform_containment() -> str:
    if os.name == "posix":
        return "posix-process-group"
    if os.name == "nt":
        return "windows-job"
    return "process"


def _popen_options(
    request: ProcessRequest, command: tuple[str, ...] | None = None
) -> dict[str, object]:
    options: dict[str, object] = {
        "args": request.command if command is None else command,
        "cwd": request.cwd,
        "env": dict(request.env) if request.env is not None else None,
        "errors": "replace",
        "encoding": "utf-8",
        "shell": False,
        "stderr": subprocess.PIPE,
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
        "text": True,
        "bufsize": 1,
    }
    if os.name == "posix":
        options["start_new_session"] = True
    return options


def _windows_job_types() -> tuple[Any, Any]:
    from ._windows_job import Job, JobError

    return Job, JobError


def _failure(code: str, phase: str, message: str) -> ProcessFailure:
    return ProcessFailure(code=code, phase=phase, message=message)


def _abort_unassigned_process(
    process: subprocess.Popen[str],
) -> tuple[ProcessFailure, ...]:
    failures: list[ProcessFailure] = []
    try:
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=_TERMINATION_GRACE_SECONDS)
    except (OSError, subprocess.TimeoutExpired) as exc:
        failures.append(
            _failure(
                "PROCESS_TREE_TERMINATION_FAILED",
                "termination",
                str(exc),
            )
        )
        try:
            process.kill()
            process.wait(timeout=_TERMINATION_GRACE_SECONDS)
        except (OSError, subprocess.TimeoutExpired) as kill_exc:
            failures.append(
                _failure(
                    "PROCESS_TREE_TERMINATION_FAILED",
                    "termination",
                    str(kill_exc),
                )
            )
    return tuple(failures)


def _spawn_windows_process(request: ProcessRequest) -> _SpawnResult:
    Job, JobError = _windows_job_types()
    try:
        job = Job.create()
    except JobError as exc:
        return _SpawnResult(
            process=None,
            job=None,
            primary_failure=_failure(
                "PROCESS_JOB_ASSIGNMENT_FAILED", "spawn", str(exc)
            ),
            secondary_failures=(),
        )

    bootstrap = Path(__file__).with_name("_job_bootstrap.py")
    command = (sys.executable, "-u", str(bootstrap), "--", *request.command)
    try:
        process = subprocess.Popen[str](
            **_popen_options(request, command=command)
        )
    except (OSError, TypeError, ValueError, IndexError) as exc:
        secondary: list[ProcessFailure] = []
        try:
            job.active_processes()
            job.close()
        except JobError as close_exc:
            secondary.append(
                _failure(
                    "PROCESS_CLEANUP_UNVERIFIABLE", "cleanup", str(close_exc)
                )
            )
        return _SpawnResult(
            process=None,
            job=None,
            primary_failure=_failure("PROCESS_SPAWN_FAILED", "spawn", str(exc)),
            secondary_failures=tuple(secondary),
        )

    try:
        job.assign_process(process)
    except JobError as exc:
        secondary = list(_abort_unassigned_process(process))
        try:
            job.active_processes()
            job.close()
        except JobError as close_exc:
            secondary.append(
                _failure(
                    "PROCESS_CLEANUP_UNVERIFIABLE", "cleanup", str(close_exc)
                )
            )
        return _SpawnResult(
            process=None,
            job=None,
            primary_failure=_failure(
                "PROCESS_JOB_ASSIGNMENT_FAILED", "spawn", str(exc)
            ),
            secondary_failures=tuple(secondary),
        )

    try:
        assert process.stdin is not None
        assert process.stdout is not None
        stdin_buffer = getattr(process.stdin, "buffer", None)
        if stdin_buffer is not None:
            stdin_buffer.write(b"SDD_CMDC_GO\n")
            stdin_buffer.flush()
        else:
            process.stdin.write("SDD_CMDC_GO\n")
            process.stdin.flush()
        sentinel_line = process.stdout.readline()
        if not sentinel_line:
            return _SpawnResult(
                process=process,
                job=job,
                primary_failure=_failure(
                    "PROCESS_BOOTSTRAP_PROTOCOL_ERROR",
                    "spawn",
                    "bootstrap exited without a target sentinel",
                ),
                secondary_failures=(),
            )
        try:
            sentinel = json.loads(sentinel_line)
        except json.JSONDecodeError as exc:
            return _SpawnResult(
                process=process,
                job=job,
                primary_failure=_failure(
                    "PROCESS_BOOTSTRAP_PROTOCOL_ERROR", "spawn", str(exc)
                ),
                secondary_failures=(),
            )
        if sentinel.get("type") == "target_spawn_failed":
            return _SpawnResult(
                process=process,
                job=job,
                primary_failure=_failure(
                    "PROCESS_SPAWN_FAILED",
                    "spawn",
                    str(sentinel.get("error", "target spawn failed")),
                ),
                secondary_failures=(),
            )
        if sentinel.get("type") != "target_spawned":
            return _SpawnResult(
                process=process,
                job=job,
                primary_failure=_failure(
                    "PROCESS_BOOTSTRAP_PROTOCOL_ERROR",
                    "spawn",
                    "unexpected bootstrap sentinel",
                ),
                secondary_failures=(),
            )
    except (OSError, ValueError, TypeError) as exc:
        return _SpawnResult(
            process=process,
            job=job,
            primary_failure=_failure(
                "PROCESS_BOOTSTRAP_PROTOCOL_ERROR", "spawn", str(exc)
            ),
            secondary_failures=(),
        )
    return _SpawnResult(
        process=process,
        job=job,
        primary_failure=None,
        secondary_failures=(),
    )


def _reader(
    stream_name: Literal["stdout", "stderr"],
    stream: object,
    output_queue: queue.Queue[_QueuedOutput],
    done: threading.Event,
    errors: queue.Queue[tuple[Literal["stdout", "stderr"], BaseException]],
) -> None:
    try:
        readline = getattr(stream, "readline")
        while True:
            text = readline()
            if text == "":
                break
            output_queue.put(
                _QueuedOutput(stream_name, text, time.monotonic())
            )
    except BaseException as exc:
        errors.put((stream_name, exc))
    finally:
        done.set()


def _linux_group_has_live_members(pgid: int) -> bool | None:
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        return None

    try:
        entries = tuple(proc_root.iterdir())
    except OSError:
        return None

    for entry in entries:
        if not entry.name.isdecimal():
            continue
        try:
            stat_text = (entry / "stat").read_text(encoding="ascii")
        except (OSError, UnicodeError):
            continue
        closing_paren = stat_text.rfind(")")
        if closing_paren < 0:
            continue
        fields = stat_text[closing_paren + 2 :].split()
        if len(fields) < 3:
            continue
        state = fields[0]
        try:
            process_group = int(fields[2])
        except ValueError:
            continue
        if process_group != pgid:
            continue
        if state != "Z":
            return True

    return False


def _posix_group_has_live_members(pgid: int) -> bool | None:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return None
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        return None

    if sys.platform.startswith("linux"):
        live_members = _linux_group_has_live_members(pgid)
        if live_members is not None:
            return live_members
    return True


def _contained_state(
    process: subprocess.Popen[str],
    pid: int,
    containment: str,
    job: Any | None = None,
) -> bool | None:
    if containment == "posix-process-group":
        return _posix_group_has_live_members(pid)
    if containment == "windows-job":
        if job is None:
            return None
        try:
            return job.active_processes() != 0
        except Exception:
            return None
    return process.poll() is None


def _wait_for_contained_empty(
    process: subprocess.Popen[str],
    pid: int,
    containment: str,
    timeout: float,
    job: Any | None = None,
) -> bool | None:
    deadline = time.monotonic() + timeout
    while True:
        process.poll()
        state = _contained_state(process, pid, containment, job)
        if state is False or state is None:
            return state
        if time.monotonic() >= deadline:
            return state
        time.sleep(_POLL_INTERVAL_SECONDS)


def _send_termination_signal(
    process: subprocess.Popen[str],
    pid: int,
    containment: str,
    sig: int,
    job: Any | None = None,
) -> None:
    if containment == "posix-process-group":
        os.killpg(pid, sig)
    elif containment == "windows-job":
        if job is None:
            raise RuntimeError("Windows Job Object is unavailable")
        job.terminate(1)
    elif process.poll() is None:
        if sig == signal.SIGTERM:
            process.terminate()
        else:
            process.kill()


def _terminate_contained(
    process: subprocess.Popen[str],
    pid: int,
    containment: str,
    job: Any | None = None,
) -> tuple[bool, tuple[ProcessFailure, ...]]:
    failures: list[ProcessFailure] = []
    grace = (
        _WINDOWS_TERMINATION_GRACE_SECONDS
        if containment == "windows-job"
        else _TERMINATION_GRACE_SECONDS
    )

    try:
        _send_termination_signal(process, pid, containment, signal.SIGTERM, job)
    except ProcessLookupError:
        pass
    except Exception as exc:
        failures.append(
            ProcessFailure(
                code="PROCESS_TREE_TERMINATION_FAILED",
                phase="termination",
                message=str(exc),
            )
        )

    state = _wait_for_contained_empty(
        process, pid, containment, grace, job
    )
    if state is True:
        try:
            if containment == "windows-job":
                _send_termination_signal(
                    process, pid, containment, signal.SIGTERM, job
                )
            else:
                _send_termination_signal(
                    process, pid, containment, signal.SIGKILL, job
                )
        except ProcessLookupError:
            pass
        except Exception as exc:
            failures.append(
                ProcessFailure(
                    code="PROCESS_TREE_TERMINATION_FAILED",
                    phase="termination",
                    message=str(exc),
                )
            )
        state = _wait_for_contained_empty(
            process, pid, containment, grace, job
        )

    try:
        process.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        failures.append(
            ProcessFailure(
                code="PROCESS_TREE_TERMINATION_FAILED",
                phase="termination",
                message="process leader did not exit after termination",
            )
        )
    except OSError as exc:
        failures.append(
            ProcessFailure(
                code="PROCESS_TREE_TERMINATION_FAILED",
                phase="termination",
                message=str(exc),
            )
        )

    if state is None:
        failures.append(
            ProcessFailure(
                code="PROCESS_CLEANUP_UNVERIFIABLE",
                phase="cleanup",
                message="contained process state could not be verified",
            )
        )
        return False, tuple(failures)
    if state is True:
        failures.append(
            ProcessFailure(
                code="PROCESS_TREE_TERMINATION_FAILED",
                phase="cleanup",
                message="contained process group remained non-empty",
            )
        )
        return False, tuple(failures)
    return not failures, tuple(failures)


def _failure_from_reader(
    stream: Literal["stdout", "stderr"], error: BaseException
) -> ProcessFailure:
    return ProcessFailure(
        code="PROCESS_STREAM_READ_FAILED",
        phase=stream,
        message=str(error),
    )


def run_process(
    request: ProcessRequest,
    *,
    on_output: Callable[[StreamEvent], None] | None = None,
    activity_clock: Callable[[], float] | None = None,
) -> ProcessOutcome:
    """Run one contained process and return only after drain and cleanup proof."""

    containment = _platform_containment()
    job: Any | None = None
    if os.name == "nt":
        spawn_result = _spawn_windows_process(request)
        process = spawn_result.process
        job = spawn_result.job
        initial_failure = spawn_result.primary_failure
        initial_secondary = list(spawn_result.secondary_failures)
    else:
        try:
            process = subprocess.Popen[str](**_popen_options(request))
        except (OSError, TypeError, ValueError, IndexError) as exc:
            process = None
            initial_failure = _failure("PROCESS_SPAWN_FAILED", "spawn", str(exc))
            initial_secondary = []

    if process is None:
        return ProcessOutcome(
            pid=None,
            returncode=None,
            stdout="",
            stderr="",
            status=ProcessStatus.SPAWN_FAILED,
            containment=containment,
            cleanup_verified=not initial_secondary,
            drain_verified=True,
            primary_failure=initial_failure,
            secondary_failures=tuple(initial_secondary),
        )

    assert process.stdout is not None
    assert process.stderr is not None
    pid = process.pid
    started = time.monotonic()
    output_queue: queue.Queue[_QueuedOutput] = queue.Queue()
    reader_errors: queue.Queue[
        tuple[Literal["stdout", "stderr"], BaseException]
    ] = queue.Queue()
    reader_done = {
        "stdout": threading.Event(),
        "stderr": threading.Event(),
    }
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    reader_threads = (
        threading.Thread(
            target=_reader,
            args=(
                "stdout",
                process.stdout,
                output_queue,
                reader_done["stdout"],
                reader_errors,
            ),
            name=f"process-supervisor-{pid}-stdout",
            daemon=True,
        ),
        threading.Thread(
            target=_reader,
            args=(
                "stderr",
                process.stderr,
                output_queue,
                reader_done["stderr"],
                reader_errors,
            ),
            name=f"process-supervisor-{pid}-stderr",
            daemon=True,
        ),
    )
    for thread in reader_threads:
        thread.start()

    stdin_thread: threading.Thread | None = None
    stdin_errors: queue.Queue[BaseException] = queue.Queue()
    if process.stdin is not None:
        if request.stdin_text:

            def write_stdin() -> None:
                try:
                    process.stdin.write(request.stdin_text)
                    process.stdin.flush()
                except BaseException as exc:
                    stdin_errors.put(exc)
                finally:
                    try:
                        process.stdin.close()
                    except BaseException as exc:
                        stdin_errors.put(exc)

            stdin_thread = threading.Thread(
                target=write_stdin,
                name=f"process-supervisor-{pid}-stdin",
                daemon=True,
            )
            stdin_thread.start()
        else:
            process.stdin.close()

    status = (
        ProcessStatus.SPAWN_FAILED
        if initial_failure is not None
        else ProcessStatus.EXITED
    )
    primary_failure: ProcessFailure | None = initial_failure
    secondary_failures: list[ProcessFailure] = initial_secondary
    cleanup_requested = False
    cleanup_verified = False
    callback_error: BaseException | None = None
    callback_traceback = None
    callback = on_output
    last_activity = started
    activity_error_reported = False
    pending_output: list[_QueuedOutput] = []
    stdout_dispatched = False

    def record_execution_failure(failure: ProcessFailure) -> None:
        nonlocal primary_failure
        if primary_failure is None:
            primary_failure = failure
        else:
            secondary_failures.append(failure)

    def record_secondary(failure: ProcessFailure) -> None:
        secondary_failures.append(failure)

    def collect_reader_errors() -> None:
        while True:
            try:
                stream, error = reader_errors.get_nowait()
            except queue.Empty:
                break
            record_secondary(_failure_from_reader(stream, error))

    def collect_stdin_errors() -> None:
        while True:
            try:
                error = stdin_errors.get_nowait()
            except queue.Empty:
                break
            if request.stdin_text:
                record_secondary(
                    ProcessFailure(
                        code="PROCESS_STDIN_FAILED",
                        phase="stdin",
                        message=str(error),
                    )
                )

    def dispatch_pending(timeout: float = 0) -> None:
        nonlocal last_activity, callback, callback_error, callback_traceback
        nonlocal stdout_dispatched

        def fill_pending(wait: float) -> None:
            try:
                if wait > 0:
                    pending_output.append(output_queue.get(timeout=wait))
            except queue.Empty:
                return
            while True:
                try:
                    pending_output.append(output_queue.get_nowait())
                except queue.Empty:
                    return

        while True:
            fill_pending(timeout)
            timeout = 0
            if not pending_output:
                return

            item_index = 0
            if not stdout_dispatched:
                stdout_index = next(
                    (
                        index
                        for index, candidate in enumerate(pending_output)
                        if candidate.stream == "stdout"
                    ),
                    None,
                )
                if stdout_index is not None:
                    item_index = stdout_index
                elif not reader_done["stdout"].is_set():
                    wait_for_stdout = max(
                        0.0,
                        pending_output[0].timestamp
                        + _STREAM_ORDER_GRACE_SECONDS
                        - time.monotonic(),
                    )
                    if wait_for_stdout > 0:
                        fill_pending(wait_for_stdout)
                        stdout_index = next(
                            (
                                index
                                for index, candidate in enumerate(pending_output)
                                if candidate.stream == "stdout"
                            ),
                            None,
                        )
                        if stdout_index is not None:
                            item_index = stdout_index

            item = pending_output.pop(item_index)
            if item.stream == "stdout":
                stdout_parts.append(item.text)
                stdout_dispatched = True
            else:
                stderr_parts.append(item.text)
            last_activity = max(last_activity, item.timestamp)
            if callback is None:
                continue
            event = StreamEvent(
                stream=item.stream,
                text=item.text,
                elapsed_seconds=max(0.0, item.timestamp - started),
            )
            try:
                callback(event)
            except BaseException as exc:
                callback_error = exc
                callback_traceback = exc.__traceback__
                callback = None

    def refresh_external_activity() -> None:
        nonlocal last_activity, activity_error_reported
        if activity_clock is None:
            return
        try:
            observed = float(activity_clock())
        except Exception as exc:
            if not activity_error_reported:
                record_secondary(
                    ProcessFailure(
                        code="PROCESS_ACTIVITY_CLOCK_FAILED",
                        phase="supervision",
                        message=str(exc),
                    )
                )
                activity_error_reported = True
            return
        if observed > last_activity:
            last_activity = observed

    try:
        while True:
            dispatch_pending()
            collect_reader_errors()
            collect_stdin_errors()
            refresh_external_activity()
            if callback_error is not None:
                cleanup_requested = True
                break

            returncode = process.poll()
            if returncode is not None:
                state = _contained_state(process, pid, containment, job)
                cleanup_requested = state is not False
                break

            now = time.monotonic()
            wall_deadline = (
                started + request.wall_timeout_seconds
                if request.wall_timeout_seconds > 0
                else None
            )
            stall_deadline = (
                last_activity + request.stall_timeout_seconds
                if request.stall_timeout_seconds > 0
                else None
            )
            if wall_deadline is not None and (
                stall_deadline is None or wall_deadline <= stall_deadline
            ) and now >= wall_deadline:
                status = ProcessStatus.WALL_TIMEOUT
                record_execution_failure(
                    ProcessFailure(
                        code="WALL_TIMEOUT",
                        phase="execution",
                        message="process exceeded its wall-clock deadline",
                    )
                )
                cleanup_requested = True
                break
            if stall_deadline is not None and now >= stall_deadline:
                status = ProcessStatus.STALLED
                record_execution_failure(
                    ProcessFailure(
                        code="STALLED",
                        phase="execution",
                        message="process produced no output or activity before the stall deadline",
                    )
                )
                cleanup_requested = True
                break

            wait_for = _POLL_INTERVAL_SECONDS
            deadlines = [
                deadline
                for deadline in (wall_deadline, stall_deadline)
                if deadline is not None
            ]
            if deadlines:
                wait_for = min(wait_for, max(0.0, min(deadlines) - now))
            dispatch_pending(wait_for)
    except KeyboardInterrupt as exc:
        status = ProcessStatus.INTERRUPTED
        record_execution_failure(
            ProcessFailure(
                code="INTERRUPTED",
                phase="execution",
                message=str(exc) or "process supervision was interrupted",
            )
        )
        cleanup_requested = True
    except BaseException as exc:
        callback_error = exc
        callback_traceback = exc.__traceback__
        cleanup_requested = True

    try:
        state = _contained_state(process, pid, containment, job)
        if cleanup_requested or state is not False:
            cleanup_verified, failures = _terminate_contained(
                process, pid, containment, job
            )
            for failure in failures:
                record_secondary(failure)
        else:
            cleanup_verified = True
    except BaseException as exc:
        cleanup_verified = False
        record_secondary(
            ProcessFailure(
                code="PROCESS_CLEANUP_UNVERIFIABLE",
                phase="cleanup",
                message=str(exc),
            )
        )

    if process.stdin is not None:
        try:
            process.stdin.close()
        except BaseException as exc:
            record_secondary(
                ProcessFailure(
                    code="PROCESS_STDIN_DRAIN_FAILED",
                    phase="drain",
                    message=str(exc),
                )
            )
    if stdin_thread is not None:
        stdin_thread.join(timeout=_THREAD_JOIN_TIMEOUT_SECONDS)
        if stdin_thread.is_alive():
            record_secondary(
                ProcessFailure(
                    code="PROCESS_STDIN_DRAIN_FAILED",
                    phase="drain",
                    message="stdin writer did not finish",
                )
            )
    collect_stdin_errors()

    drain_deadline = time.monotonic() + _DRAIN_TIMEOUT_SECONDS
    while not all(event.is_set() for event in reader_done.values()):
        dispatch_pending(_POLL_INTERVAL_SECONDS)
        collect_reader_errors()
        if time.monotonic() >= drain_deadline:
            break
    for thread in reader_threads:
        thread.join(timeout=_THREAD_JOIN_TIMEOUT_SECONDS)
    drain_verified = all(
        event.is_set() and not thread.is_alive()
        for event, thread in zip(reader_done.values(), reader_threads)
    )
    if not drain_verified:
        for stream in (process.stdout, process.stderr):
            try:
                stream.close()
            except BaseException:
                pass
        for thread in reader_threads:
            thread.join(timeout=_THREAD_JOIN_TIMEOUT_SECONDS)
        drain_verified = all(not thread.is_alive() for thread in reader_threads)
    while True:
        before = output_queue.qsize()
        dispatch_pending()
        collect_reader_errors()
        if before == 0 and output_queue.empty():
            break
    if not drain_verified:
        record_secondary(
            ProcessFailure(
                code="PROCESS_DRAIN_FAILED",
                phase="drain",
                message="stdout or stderr reader did not reach EOF",
            )
        )

    if job is not None and cleanup_verified:
        try:
            job.close()
        except Exception as exc:
            cleanup_verified = False
            record_secondary(
                _failure("PROCESS_CLEANUP_UNVERIFIABLE", "cleanup", str(exc))
            )

    try:
        returncode = process.wait(timeout=0)
    except subprocess.TimeoutExpired:
        returncode = process.returncode
    except OSError as exc:
        returncode = process.returncode
        record_secondary(
            ProcessFailure(
                code="PROCESS_WAIT_FAILED",
                phase="cleanup",
                message=str(exc),
            )
        )

    if callback_error is not None:
        raise callback_error.with_traceback(callback_traceback)

    return ProcessOutcome(
        pid=None if status is ProcessStatus.SPAWN_FAILED else pid,
        returncode=returncode,
        stdout="".join(stdout_parts),
        stderr="".join(stderr_parts),
        status=status,
        containment=containment,
        cleanup_verified=cleanup_verified,
        drain_verified=drain_verified,
        primary_failure=primary_failure,
        secondary_failures=tuple(secondary_failures),
    )
