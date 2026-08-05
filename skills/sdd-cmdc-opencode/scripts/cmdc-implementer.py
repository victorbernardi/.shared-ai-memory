#!/usr/bin/env python3
"""Run one bounded Command Code implementer and expose fail-closed diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

MODEL_ID = "deepseek/deepseek-v4-flash"
DEFAULT_MAX_TURNS = 100
DEFAULT_WALL_TIMEOUT_SECONDS = 4 * 60 * 60
MAX_WALL_TIMEOUT_SECONDS = 12 * 60 * 60
DEFAULT_STALL_TIMEOUT_SECONDS = 15 * 60
MAX_STALL_TIMEOUT_SECONDS = 2 * 60 * 60
DEFAULT_RECOVERY_MAX_TURNS = 5
TEST_EVIDENCE_RE = re.compile(
    r"(?:\b\d+\s+passed\b|"
    r"\b(?:all|full|focused)\s+tests?\s+(?:are\s+)?(?:green|ok|successful)\b)",
    flags=re.IGNORECASE,
)
TEST_FAILURE_RE = re.compile(
    r"\b[1-9]\d*\s+(?:failed|errors?)\b",
    flags=re.IGNORECASE,
)
TEST_RESULT_COUNT_RE = re.compile(
    r"\b\d+\s+(?:passed|failed|errors?)\b",
    flags=re.IGNORECASE,
)
KNOWN_FAILURE_DISPOSITION_RE = re.compile(
    r"\b(?:pre-existing|known|out[- ]of[- ]scope)\b",
    flags=re.IGNORECASE,
)
KNOWN_FAILURE_ACCEPT_RE = re.compile(
    r"(?i)\b(?:accept(?:ed|ing)?|acknowledge(?:d|ing)?|documented|approved|verified)\b",
)
KNOWN_FAILURE_REJECT_RE = re.compile(
    r"(?i)\b(?:fix(?:ed)?|resolve(?:d|ing)?|fail(?:ure)?s?\s+(?:in|from)|"
    r"introduced|new\s+failures?|regression|blocker|unresolved|"
    r"unknown|undocumented)\b",
)
KNOWN_FAILURE_ALLOWLIST: dict[str, str] = {
    "pre-existing": "an explicit disposition token is required",
    "known": "an explicit disposition token is required",
    "out-of-scope": "an explicit disposition token is required",
    "out of scope": "an explicit disposition token is required",
}
COMMAND_FLAGS = (
    "--no-skills",
    "--trust",
    "--skip-onboarding",
    "--yolo",
)


def _stall_expired(last_activity: float, now: float, stall_timeout: float) -> bool:
    """Return whether no observable activity occurred within the stall budget."""
    return stall_timeout > 0 and now - last_activity >= stall_timeout


def build_command(cmd_path: Path, max_turns: int = DEFAULT_MAX_TURNS) -> list[str]:
    """Build the Command Code invocation before any platform launcher is added."""
    return [
        str(cmd_path),
        "-p",
        "--model",
        MODEL_ID,
        "--max-turns",
        str(max_turns),
        "--output-format",
        "json",
        *COMMAND_FLAGS,
    ]


def _is_native_windows_cmd(path: Path) -> bool:
    return path.name.lower() == "cmd.exe" and path.parent.name.lower() == "system32"


def resolve_cmdc(cmd_bin: str = "cmdc") -> Path:
    """Resolve Command Code without accepting the native Windows cmd.exe."""
    direct = Path(cmd_bin).expanduser()
    candidates: list[Path] = []
    if direct.is_file():
        candidates.append(direct.resolve())

    found = shutil.which(cmd_bin)
    if found:
        candidates.append(Path(found).resolve())

    if not direct.is_absolute() and len(direct.parts) == 1:
        npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
        candidates.extend(
            (npm_dir / f"{cmd_bin}{suffix}").resolve()
            for suffix in (".ps1", ".cmd", "")
        )

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_file() and not _is_native_windows_cmd(candidate):
            return candidate

    raise FileNotFoundError(
        f"Command Code executable '{cmd_bin}' was not found; "
        "use cmdc or install/authenticate Command Code"
    )


def classify_failure(
    returncode: int,
    stderr: str,
    report_exists: bool,
    cmd_found: bool = True,
) -> dict[str, str]:
    """Classify a failed or contract-invalid implementer run."""
    lowered = stderr.lower()
    if not cmd_found:
        code = "CMD_NOT_FOUND"
        action = "instalar/configurar o Command Code e corrigir o PATH"
        message = "o executável cmdc não foi encontrado"
    elif "not authenticated" in lowered or "authentication" in lowered or "login" in lowered:
        code = "AUTH_REQUIRED"
        action = "autenticar o Command Code e reexecutar a tarefa"
        message = "o Command Code exige autenticação"
    elif "model_not_in_plan" in lowered or "model not available" in lowered:
        code = "MODEL_UNAVAILABLE"
        action = "executar cmdc --list-models e confirmar o modelo fixo"
        message = f"{MODEL_ID} não está disponível no plano atual"
    elif returncode == 4 or "permission denied" in lowered:
        code = "PERMISSION_DENIED"
        action = (
            "verificar --yolo, trust do workspace e regras de permissão; "
            "não aguardar prompt interativo em modo headless"
        )
        message = "o Command Code negou uma operação por permissão"
    elif "rate limit" in lowered or "rate-limited" in lowered or "rate limited" in lowered:
        code = "RATE_LIMITED"
        action = "parar novas invocações e aguardar o limite ser liberado"
        message = "o Command Code aplicou rate limit"
    elif returncode == 8 or "timeout" in lowered or "max turns" in lowered:
        code = "TIMEOUT"
        action = "revisar o limite de turnos e reexecutar controladamente"
        message = "o Command Code atingiu o limite de tempo/turnos"
    elif returncode != 0:
        code = "PROCESS_FAILED"
        action = "inspecionar stderr e corrigir a falha antes de reexecutar"
        message = "o processo Command Code terminou com erro"
    elif not report_exists:
        code = "REPORT_MISSING"
        action = "corrigir o caminho do relatório e reexecutar o implementador"
        message = "o processo terminou com sucesso, mas o relatório não existe"
    else:
        return {}

    return {
        "BLOCKER_CODE": code,
        "MESSAGE": message,
        "COMMAND": "",
        "EXIT_CODE": str(returncode),
        "STDERR": stderr,
        "ACTION": action,
    }


def render_blocked(diagnostic: dict[str, str]) -> str:
    """Render the stable seven-field diagnostic consumed by the orchestrator."""
    fields = [
        ("STATUS", "BLOCKED"),
        ("BLOCKER_CODE", diagnostic.get("BLOCKER_CODE", "PROCESS_FAILED")),
        ("MESSAGE", diagnostic.get("MESSAGE", "")),
        ("COMMAND", diagnostic.get("COMMAND", "")),
        ("EXIT_CODE", diagnostic.get("EXIT_CODE", "N/A")),
        ("STDERR", diagnostic.get("STDERR", "")),
        ("ACTION", diagnostic.get("ACTION", "")),
    ]
    return "\n".join(f"{key}: {value}" for key, value in fields)


def _run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _text_output(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _configure_stdio() -> None:
    """Keep streamed CMDc output lossless on Windows' legacy console codecs."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def _has_test_evidence(output: str) -> bool:
    return not TEST_FAILURE_RE.search(output) and bool(TEST_EVIDENCE_RE.search(output))


def _known_failure_blocks(output: str) -> list[str]:
    """Split the validation output into failure blocks.

    A failure record starts at a line naming at least one failure count (for
    example ``7 failed``) and ends at the next such line. The full records
    are returned (a prelude of lines before the first failure count is
    dropped).
    """
    blocks: list[str] = []
    current: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if TEST_FAILURE_RE.search(stripped):
            if current:
                blocks.append("\n".join(current))
            current = [stripped]
        elif current:
            current.append(stripped)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _test_result_signature(block: str) -> tuple[str, ...]:
    return tuple(
        match.group(0).lower()
        for match in TEST_RESULT_COUNT_RE.finditer(block)
    )


def _scoped_known_failure_evidence(block: str) -> bool:
    """Validate one scoped known-failure record.

    A single failure record is accepted only when it (1) carries its own
    failure counts, (2) names an allowlisted disposition tied to the failure
    count itself, (3) declares the failures accepted/acknowledged/documented
    in the same record, and (4) contains no rejection language. Failures
    without an explicit disposition, unrelated records, and mixed records all
    stay rejected: the acceptance must be scoped and explicit.
    """
    if not TEST_FAILURE_RE.search(block):
        return False
    if _contains_rejection_wording(block):
        return False
    if not KNOWN_FAILURE_ACCEPT_RE.search(block):
        return False
    disposition = None
    disposition_match = KNOWN_FAILURE_DISPOSITION_RE.search(block)
    if disposition_match:
        disposition = disposition_match.group(0).lower().replace("_", " ")
    if disposition not in KNOWN_FAILURE_ALLOWLIST:
        return False
    if not KNOWN_FAILURE_ACCEPT_RE.search(block):
        return False
    # The disposition must be anchored to the failure count itself, so a
    # disposition token that appears in an unrelated part of the output
    # cannot validate a different failure record.
    anchor = None
    for match in TEST_FAILURE_RE.finditer(block):
        window = block[match.end() : match.end() + 80]
        if disposition in window:
            anchor = match
            break
    return anchor is not None


def _contains_rejection_wording(block: str) -> bool:
    """Return whether a known-failure record contains rejection wording.

    The negation check is strict: ``not accepted`` and ``not acknowledged``
    must not be claimed as acceptance by the ``accepted``/``acknowledged``
    token. ``unrelated`` is rejected only when it qualifies the failure count
    itself (``unrelated failures``); a standalone unrelated token inside a
    scoped accepted record is not rejection evidence.
    """
    if re.search(r"(?i)\bnot\s+(?:accepted|acknowledged)\b", block):
        return True
    if re.search(r"(?i)\bunrelated\s+failures?\b", block):
        return True
    return bool(KNOWN_FAILURE_REJECT_RE.search(block))


def _has_known_failure_test_evidence(output: str) -> bool:
    """Accept only explicitly scoped, validation-only failure records."""
    if not (TEST_EVIDENCE_RE.search(output) and TEST_FAILURE_RE.search(output)):
        return False
    blocks = _known_failure_blocks(output)
    scoped = [
        (index, _test_result_signature(block))
        for index, block in enumerate(blocks)
        if _scoped_known_failure_evidence(block)
    ]
    if not scoped:
        return False
    first_scoped_index = scoped[0][0]
    accepted_signatures = {signature for _, signature in scoped}
    unscoped = []
    for index, block in enumerate(blocks):
        if _scoped_known_failure_evidence(block):
            continue
        if (
            KNOWN_FAILURE_DISPOSITION_RE.search(block)
            or KNOWN_FAILURE_ACCEPT_RE.search(block)
            or _contains_rejection_wording(block)
        ):
            return False
        unscoped.append((index, _test_result_signature(block)))
    if len(unscoped) > 1:
        return False
    if unscoped:
        index, signature = unscoped[0]
        if (
            index != first_scoped_index - 1
            or not signature
            or signature not in accepted_signatures
        ):
            return False
    return True


def _has_tracked_changes(status_lines: list[str]) -> bool:
    """Return True when any status line indicates a tracked or staged change."""
    for line in status_lines:
        code = line[:2] if len(line) >= 2 else ""
        if code.strip(" ") and "?? " not in line:
            return True
    return False


def _recovery_is_ready(
    returncode: int,
    snapshot: dict[str, object],
    recovery_start_head: str,
) -> bool:
    """Require recovery to create a commit after the recovery phase starts."""
    return (
        returncode == 0
        and str(snapshot.get("head", "")) != recovery_start_head
        and bool(snapshot.get("commits_since_baseline"))
        and bool(snapshot.get("report_exists"))
        and bool(snapshot.get("tests_detectable"))
    )


def _report_output(report_path: Path | None) -> str:
    if report_path is None or not report_path.is_file():
        return ""
    return report_path.read_text(encoding="utf-8", errors="replace")


def _workspace_content_fingerprint(
    cwd: Path,
    status_lines: list[str],
    report_path: Path | None,
) -> str:
    digest = hashlib.sha256()
    paths: set[Path] = set()
    for line in status_lines:
        normalized = line.lstrip()
        relative = normalized[2:].strip() if len(normalized) >= 2 else ""
        if " -> " in relative:
            relative = relative.rsplit(" -> ", 1)[-1]
        if relative:
            paths.add((cwd / relative).resolve())
    if report_path is not None:
        paths.add(report_path.expanduser().resolve())
    for path in sorted(paths, key=lambda item: str(item)):
        digest.update(str(path).encode("utf-8", errors="replace"))
        try:
            digest.update(path.read_bytes())
        except OSError:
            digest.update(b"<unreadable-or-missing>")
    return digest.hexdigest()


def collect_workspace_snapshot(
    cwd: Path,
    *,
    baseline_head: str | None = None,
    report_path: Path | None = None,
    checkpoint_file: Path | None = None,
    test_output: str = "",
) -> dict[str, object]:
    """Collect deterministic Git/report evidence without invoking a shell."""
    git_root = _run_git(cwd, "rev-parse", "--show-toplevel")
    if not git_root:
        raise RuntimeError("git root was empty")
    head = _run_git(cwd, "rev-parse", "HEAD")
    status = _run_git(cwd, "status", "--short", "--untracked-files=all")
    status_lines = status.splitlines() if status else []
    if checkpoint_file is not None:
        checkpoint_path = checkpoint_file.expanduser().resolve()
        root_path = Path(git_root).resolve()
        try:
            checkpoint_relative = checkpoint_path.relative_to(root_path).as_posix()
        except ValueError:
            checkpoint_relative = None
        if checkpoint_relative:
            status_lines = [
                line
                for line in status_lines
                if line[3:].strip().replace("\\", "/") != checkpoint_relative
            ]
    commits_since_baseline: list[str] = []
    if baseline_head and baseline_head != head:
        commits = _run_git(cwd, "rev-list", "--reverse", f"{baseline_head}..HEAD")
        commits_since_baseline = commits.splitlines() if commits else []
    report_exists = report_path is not None and report_path.is_file()
    diff_present = bool(status_lines)
    changed = diff_present or bool(commits_since_baseline)
    state = "IMPLEMENTATION INCOMPLETE" if changed else "STARTING"
    return {
        "git_root": git_root,
        "head": head,
        "status": status_lines,
        "diff_present": diff_present,
        "commits_since_baseline": commits_since_baseline,
        "report_exists": report_exists,
        "report_path": str(report_path) if report_path else None,
        "tests_detectable": _has_test_evidence(test_output),
        "state": state,
        "workspace_content_fingerprint": _workspace_content_fingerprint(
            cwd, status_lines, report_path
        ),
    }


def _activity_fingerprint(snapshot: dict[str, object]) -> tuple[object, ...]:
    return (
        snapshot.get("head"),
        tuple(snapshot.get("status", [])),
        snapshot.get("report_exists"),
        snapshot.get("workspace_content_fingerprint"),
    )


def _record_activity(activity_state: dict[str, object], kind: str) -> None:
    now = time.monotonic()
    lock = activity_state["lock"]
    with lock:
        activity_state["last_activity"] = now
        activity_state[f"last_{kind}"] = now
        if kind == "event":
            activity_state["events_seen"] = int(activity_state.get("events_seen", 0)) + 1


def _activity_evidence(activity_state: dict[str, object]) -> dict[str, object]:
    now = time.monotonic()
    lock = activity_state["lock"]
    with lock:
        return {
            "last_activity_seconds": round(now - float(activity_state["last_activity"]), 1),
            "last_event_seconds": round(now - float(activity_state["last_event"]), 1),
            "last_workspace_seconds": round(
                now - float(activity_state["last_workspace"]), 1
            ),
            "events_seen": int(activity_state.get("events_seen", 0)),
        }


def _attach_activity_evidence(
    snapshot: dict[str, object],
    activity_state: dict[str, object],
    event_log: Path | None,
) -> None:
    snapshot.update(_activity_evidence(activity_state))
    if event_log is not None:
        snapshot["event_log"] = str(event_log)


def _drain_stream(
    stream: object,
    stream_name: str,
    chunks: list[str],
    activity_state: dict[str, object],
    event_log: Path | None,
) -> None:
    reader = stream
    try:
        while True:
            line = reader.readline()
            if line == "" or line == b"":
                break
            text = _text_output(line)
            chunks.append(text)
            _record_activity(activity_state, "event")
            if event_log is not None:
                try:
                    with event_log.open("a", encoding="utf-8", newline="\n") as handle:
                        handle.write(
                            json.dumps(
                                {
                                    "stream": stream_name,
                                    "elapsed_seconds": round(
                                        time.monotonic()
                                        - float(activity_state["started"]),
                                        1,
                                    ),
                                    "text": text,
                                },
                                ensure_ascii=False,
                            )
                            + "\n"
                        )
                except OSError:
                    pass
    finally:
        close = getattr(reader, "close", None)
        if close is not None:
            close()


def _terminate_process_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        return
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return


def _windows_process_pids() -> list[int]:
    """List every live PID from tasklist (Windows-only)."""
    result = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    pids: list[int] = []
    for line in result.stdout.splitlines():
        columns = line.split(",")
        if len(columns) >= 2:
            candidate = columns[1].strip().strip('"')
            if candidate.isdigit():
                pids.append(int(candidate))
    return pids


def _windows_pid_in_group(pid: int, leader: int) -> bool:
    """Return whether a Windows process belongs to the tree rooted at leader.

    On Windows the process group is not exposed to Python, so the tree is
    approximated by walking parent links: every process whose ancestor chain
    reaches the leader is a member. A process that cannot be resolved is
    treated as a member so the check stays fail-closed.
    """
    if pid == leader:
        return True
    seen: set[int] = set()
    current = pid
    while current not in seen:
        seen.add(current)
        parent = _windows_parent_pid(current)
        if parent is None:
            # The process's parent could not be resolved (wmic failed or the
            # process vanished); treat it as a member so cleanup verification
            # fails closed instead of declaring a false clean tree.
            return True
        if parent == 0:
            # A known root that is not the leader: the chain is fully
            # resolved and never reaches the leader, so this process is a
            # known non-member of the tree.
            return False
        if parent == leader:
            return True
        current = parent
    return False


def _windows_parent_pid(pid: int) -> int | None:
    """Return the PPID of a Windows process via wmic, or None when unknown."""
    result = subprocess.run(
        ["wmic", "process", "where", f"ProcessId={pid}", "get", "ParentProcessId"],
        capture_output=True,
        text=True,
        check=False,
    )
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            return int(line)
    return None


def _capture_process_group(pid: int) -> int | None:
    """Capture the POSIX process-group identity before the leader exits.

    killpg(pid) keeps the group id equal to the leader pid, so the group is
    captured before termination; after the leader exits os.getpgid(leader)
    raises ProcessLookupError and the group identity is gone.
    """
    if os.name == "nt":
        return None
    try:
        return os.getpgid(pid)
    except (ProcessLookupError, PermissionError, OSError):
        return None


def _process_tree_alive(pid: int, group: int | None = None) -> bool:
    """Return True when any process of the group is still alive.

    killpg()/taskkill /T keep the group id equal to the leader pid, so the
    whole tree is verified from the group captured before termination
    instead of only the leader. A surviving descendant makes the cleanup
    unverified; an uncaptured group identity counts as alive (fail closed).
    """
    if os.name == "nt":
        # On Windows, taskkill /T (used by _terminate_process_tree) kills the
        # whole tree rooted at pid. Verify absence by scanning the full
        # process list for any surviving member of that tree rather than
        # trusting the leader alone.
        return any(
            _windows_pid_in_group(candidate_pid, pid)
            for candidate_pid in _windows_process_pids()
        )
    if group is None:
        # The group identity was never captured (or could not be resolved).
        # The tree cannot be verified absent, so it must count as alive:
        # fail closed.
        return True
    try:
        processes = os.listdir("/proc")
    except (PermissionError, OSError):
        return True
    for process in processes:
        if not process.isdigit():
            continue
        try:
            if os.getpgid(int(process)) == group:
                return True
        except ProcessLookupError:
            continue
        except (PermissionError, OSError):
            return True
    return False


def _fresh_activity_state(
    baseline_fingerprint: tuple[object, ...] | None = None,
) -> dict[str, object]:
    """Build an activity state with an independent wall-clock baseline.

    The wall deadline is derived from ``started``, so reusing the primary
    state for recovery would let a recovery that starts near the primary
    timeout exceed its budget immediately. Recovery gets a fresh baseline.
    """
    now = time.monotonic()
    return {
        "lock": threading.Lock(),
        "started": now,
        "last_activity": now,
        "last_event": now,
        "last_workspace": now,
        "events_seen": 0,
        "workspace_fingerprint": baseline_fingerprint,
    }


def _run_cmdc_process(
    process_command: list[str],
    prompt_text: str,
    cwd: Path,
    *,
    wall_timeout_seconds: int,
    stall_timeout_seconds: int,
    activity_state: dict[str, object],
    event_log: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run CMDc while streaming events and enforcing both watchdogs."""
    process = subprocess.Popen(
        process_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=(
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if os.name == "nt"
        else 0,
        start_new_session=os.name != "nt",
    )
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []
    readers = [
        threading.Thread(
            target=_drain_stream,
            args=(process.stdout, "stdout", stdout_chunks, activity_state, event_log),
            daemon=True,
        ),
        threading.Thread(
            target=_drain_stream,
            args=(process.stderr, "stderr", stderr_chunks, activity_state, event_log),
            daemon=True,
        ),
    ]
    for reader in readers:
        reader.start()
    try:
        if process.stdin is not None:
            try:
                process.stdin.write(prompt_text)
                process.stdin.close()
            except (BrokenPipeError, OSError):
                pass
        started = float(activity_state["started"])
        while process.poll() is None:
            now = time.monotonic()
            last_activity = float(activity_state["last_activity"])
            if now - started >= wall_timeout_seconds:
                reason = "WALL_TIMEOUT"
            elif _stall_expired(last_activity, now, stall_timeout_seconds):
                reason = "STALLED"
            else:
                reason = ""
            if reason:
                process_group = _capture_process_group(process.pid)
                _terminate_process_tree(process.pid)
                cleanup_verified = False
                try:
                    process.wait(timeout=5)
                    cleanup_verified = not _process_tree_alive(process.pid)
                    if process_group is not None:
                        cleanup_verified = not _process_tree_alive(process.pid, process_group)
                except subprocess.TimeoutExpired:
                    cleanup_verified = not _process_tree_alive(process.pid)
                    if process_group is not None:
                        cleanup_verified = not _process_tree_alive(process.pid, process_group)
                for reader in readers:
                    reader.join(timeout=2)
                error = subprocess.TimeoutExpired(
                    process_command,
                    timeout=wall_timeout_seconds
                    if reason == "WALL_TIMEOUT"
                    else stall_timeout_seconds,
                    output="".join(stdout_chunks),
                    stderr="".join(stderr_chunks),
                )
                error.watchdog_reason = reason  # type: ignore[attr-defined]
                error.watchdog_pid = process.pid  # type: ignore[attr-defined]
                error.watchdog_cleanup_verified = cleanup_verified  # type: ignore[attr-defined]
                raise error
            time.sleep(0.2)
    finally:
        for reader in readers:
            reader.join(timeout=2)
    return subprocess.CompletedProcess(
        process_command,
        process.returncode,
        "".join(stdout_chunks),
        "".join(stderr_chunks),
    )


def _write_checkpoint(
    path: Path,
    event: str,
    snapshot: dict[str, object],
    state: str | None = None,
    *,
    phase: str | None = None,
    last_command: str = "",
    last_output: str = "",
) -> None:
    """Append one JSONL checkpoint record; the snapshot never claims COMPLETE."""
    path.parent.mkdir(parents=True, exist_ok=True)
    state = state or str(snapshot["state"])
    if state == "COMPLETE":
        raise ValueError("a workspace snapshot cannot claim COMPLETE")
    payload = {
        "event": event,
        "last_command": last_command,
        "last_output": last_output,
        "phase": phase or event,
        "snapshot": snapshot,
        "state": state,
    }
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _heartbeat_loop(
    cwd: Path,
    baseline_head: str,
    report_path: Path | None,
    checkpoint_file: Path | None,
    command: str,
    interval: float,
    stop_event: threading.Event,
    started_monotonic: float | None = None,
    activity_state: dict[str, object] | None = None,
) -> None:
    started_monotonic = started_monotonic or time.monotonic()
    while not stop_event.wait(interval):
        try:
            snapshot = collect_workspace_snapshot(
                cwd,
                baseline_head=baseline_head,
                report_path=report_path,
                checkpoint_file=checkpoint_file,
            )
        except RuntimeError as exc:
            if checkpoint_file is not None:
                _write_checkpoint(
                    checkpoint_file,
                    "HEARTBEAT_FAILED",
                    {"state": "RUNNING", "error": str(exc)},
                    state="RUNNING",
                    phase="RUNNING",
                    last_command=command,
                    last_output=str(exc),
                )
            continue
        if activity_state is not None:
            fingerprint = _activity_fingerprint(snapshot)
            lock = activity_state["lock"]
            with lock:
                if fingerprint != activity_state["workspace_fingerprint"]:
                    activity_state["workspace_fingerprint"] = fingerprint
                    activity_state["last_activity"] = time.monotonic()
                    activity_state["last_workspace"] = activity_state["last_activity"]
            _attach_activity_evidence(snapshot, activity_state, None)
        snapshot["elapsed_seconds"] = round(time.monotonic() - started_monotonic, 1)
        if checkpoint_file is not None:
            _write_checkpoint(
                checkpoint_file,
                "HEARTBEAT",
                snapshot,
                state="RUNNING",
                phase="RUNNING",
                last_command=command,
            )


def _render_incomplete(
    diagnostic: dict[str, str], snapshot: dict[str, object], checkpoint_file: Path | None
) -> str:
    lines = render_blocked(diagnostic).splitlines()
    lines[0] = "STATUS: IMPLEMENTATION INCOMPLETE"
    lines.extend(
        [
            f"WORKSPACE_ROOT: {snapshot['git_root']}",
            f"WORKSPACE_HEAD: {snapshot['head']}",
            f"WORKSPACE_DIFF: {'true' if snapshot['diff_present'] else 'false'}",
            f"WORKSPACE_STATUS: {' | '.join(snapshot['status'])}",
            f"WORKSPACE_COMMITS: {len(snapshot['commits_since_baseline'])}",
            f"REPORT_EXISTS: {'true' if snapshot['report_exists'] else 'false'}",
            f"WORKSPACE_TESTS: {'true' if snapshot['tests_detectable'] else 'false'}",
            f"CHECKPOINT_FILE: {checkpoint_file or ''}",
        ]
    )
    if snapshot.get("event_log"):
        lines.append(f"EVENT_LOG: {snapshot['event_log']}")
    return "\n".join(lines)


def _extract_report_path(prompt_text: str, cwd: Path) -> Path | None:
    for line in prompt_text.splitlines():
        match = re.search(
            r"Write (?:your|the) full report to\s*:?[ \t]*(.+?)[ \t]*:?[ \t]*$",
            line,
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        candidate = match.group(1).strip().rstrip(":").strip()
        if not candidate or candidate.startswith("["):
            return None
        path = Path(candidate).expanduser()
        return path if path.is_absolute() else cwd / path
    return None


def _platform_command(command: list[str]) -> list[str]:
    """Launch Windows script shims through PowerShell/cmd while keeping cmdc."""
    path = Path(command[0])
    if os.name == "nt" and path.suffix.lower() == ".ps1":
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if not powershell:
            raise FileNotFoundError("PowerShell launcher was not found")
        return [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", *command]
    if os.name == "nt" and path.suffix.lower() in {".cmd", ".bat"}:
        launcher = os.environ.get("COMSPEC", "cmd.exe")
        return [launcher, "/d", "/c", *command]
    return command


def run_implementer(
    cwd: Path,
    prompt_file: Path,
    max_turns: int = DEFAULT_MAX_TURNS,
    cmd_bin: str = "cmdc",
    checkpoint_file: Path | None = None,
    heartbeat_interval: float = 30.0,
    recovery_max_turns: int = DEFAULT_RECOVERY_MAX_TURNS,
    wall_timeout_seconds: int = DEFAULT_WALL_TIMEOUT_SECONDS,
    stall_timeout_seconds: int = DEFAULT_STALL_TIMEOUT_SECONDS,
    allow_no_change: bool = False,
    allow_known_test_failures: bool = False,
) -> int:
    """Run Command Code and return zero only after process/report success."""
    cwd = cwd.expanduser().resolve()
    prompt_file = prompt_file.expanduser().resolve()
    prompt_text = prompt_file.read_text(encoding="utf-8")
    report_path = _extract_report_path(prompt_text, cwd)
    baseline_snapshot: dict[str, object] | None = None
    try:
        baseline_snapshot = collect_workspace_snapshot(
            cwd,
            report_path=report_path,
            checkpoint_file=checkpoint_file,
        )
    except RuntimeError as exc:
        diagnostic = {
            "BLOCKER_CODE": "WORKSPACE_INSPECTION_FAILED",
            "MESSAGE": "não foi possível estabelecer o baseline Git do workspace",
            "COMMAND": " ".join([cmd_bin, *COMMAND_FLAGS]),
            "EXIT_CODE": "1",
            "STDERR": str(exc),
            "ACTION": "corrigir a disponibilidade do Git antes de iniciar o CMDc",
        }
        print(render_blocked(diagnostic), file=sys.stderr)
        return 1

    command: list[str] = [cmd_bin, *COMMAND_FLAGS]
    completed = None
    heartbeat_stop = threading.Event()
    heartbeat_thread: threading.Thread | None = None
    wall_timeout_seconds = min(
        max(60, wall_timeout_seconds), MAX_WALL_TIMEOUT_SECONDS
    )
    stall_timeout_seconds = min(
        max(0, stall_timeout_seconds), MAX_STALL_TIMEOUT_SECONDS
    )
    started_monotonic = time.monotonic()
    activity_state: dict[str, object] = {
        "lock": threading.Lock(),
        "started": started_monotonic,
        "last_activity": started_monotonic,
        "last_event": started_monotonic,
        "last_workspace": started_monotonic,
        "events_seen": 0,
        "workspace_fingerprint": _activity_fingerprint(baseline_snapshot),
    }
    event_log = (
        checkpoint_file.with_name(checkpoint_file.stem + "-events.jsonl")
        if checkpoint_file is not None
        else None
    )

    try:
        cmd_path = resolve_cmdc(cmd_bin)
        command = build_command(cmd_path, max_turns=max_turns)
        process_command = _platform_command(command)
        command_text = " ".join(str(part) for part in command)
        if checkpoint_file and baseline_snapshot is not None:
            _write_checkpoint(
                checkpoint_file,
                "STARTING",
                baseline_snapshot,
                state="STARTING",
                phase="STARTING",
                last_command=command_text,
            )
        if stall_timeout_seconds > 0:
            monitor_interval = heartbeat_interval if heartbeat_interval > 0 else 30.0
            heartbeat_thread = threading.Thread(
                target=_heartbeat_loop,
                args=(
                    cwd,
                    str(baseline_snapshot["head"]),
                    report_path,
                    checkpoint_file,
                    command_text,
                    monitor_interval,
                    heartbeat_stop,
                    started_monotonic,
                    activity_state,
                ),
                daemon=True,
            )
            heartbeat_thread.start()
        completed = _run_cmdc_process(
            process_command,
            prompt_text,
            cwd,
            wall_timeout_seconds=wall_timeout_seconds,
            stall_timeout_seconds=stall_timeout_seconds,
            activity_state=activity_state,
            event_log=event_log,
        )
        if completed.stdout:
            stdout = _text_output(completed.stdout)
            sys.stdout.write(stdout)
            if not stdout.endswith("\n"):
                sys.stdout.write("\n")
        if completed.stderr:
            stderr = _text_output(completed.stderr)
            sys.stderr.write(stderr)
            if not stderr.endswith("\n"):
                sys.stderr.write("\n")
        report_exists = report_path is not None and report_path.is_file()
        known_failure_evidence = (
            allow_no_change
            and allow_known_test_failures
            and completed.returncode in {0, 1}
            and _has_known_failure_test_evidence(
                "\n".join(
                    part
                    for part in (
                        _text_output(completed.stdout),
                        _text_output(completed.stderr),
                        _report_output(report_path),
                    )
                    if part
                )
            )
        )
        diagnostic = classify_failure(
            completed.returncode,
            stderr if completed.stderr else "",
            report_exists=report_exists,
        )
        if known_failure_evidence:
            diagnostic = {}
            exit_code = 0
        else:
            exit_code = completed.returncode
    except FileNotFoundError as exc:
        command = [cmd_bin, *COMMAND_FLAGS]
        diagnostic = classify_failure(127, str(exc), report_exists=False, cmd_found=False)
        exit_code = 127
    except subprocess.TimeoutExpired as exc:
        command = build_command(Path(cmd_bin), max_turns=max_turns)
        timeout_stdout = _text_output(exc.stdout)
        timeout_stderr = _text_output(exc.stderr) or str(exc)
        timeout_output = "\n".join(
            part for part in (timeout_stdout, timeout_stderr) if part
        )
        watchdog_reason = getattr(exc, "watchdog_reason", "WALL_TIMEOUT")
        watchdog_cleanup_verified = getattr(
            exc, "watchdog_cleanup_verified", True
        )
        # Fail closed before any recovery: a live CMDc tree could still mutate
        # the workspace, so it must never be followed by a recovery attempt.
        if not watchdog_cleanup_verified:
            diagnostic = {
                "BLOCKER_CODE": "WATCHDOG_CLEANUP_UNVERIFIED",
                "MESSAGE": (
                    "o processo CMDc não foi verificado ausente após o watchdog; "
                    "a árvore de processos pode continuar alterando o workspace"
                ),
                "COMMAND": "",
                "EXIT_CODE": "8",
                "STDERR": timeout_stderr,
                "ACTION": (
                    "inspecionar e encerrar manualmente os processos CMDc "
                    "remanescentes antes de qualquer nova invocação"
                ),
            }
            print(render_blocked(diagnostic), file=sys.stderr)
            return 8
        if watchdog_reason == "STALLED":
            diagnostic = {
                "BLOCKER_CODE": "STALLED",
                "MESSAGE": (
                    "o CMDc não produziu eventos nem mudanças observáveis no workspace "
                    f"por {stall_timeout_seconds}s"
                ),
                "COMMAND": "",
                "EXIT_CODE": "8",
                "STDERR": timeout_stderr,
                "ACTION": (
                    "inspecionar o event log e o prompt; não repetir automaticamente "
                    "sem corrigir a falta de progresso"
                ),
            }
            if event_log is not None:
                diagnostic["EVENT_LOG"] = str(event_log)
        else:
            diagnostic = classify_failure(8, timeout_stderr, report_exists=False)
        exit_code = 8

        snapshot = None
        if baseline_snapshot is not None:
            try:
                snapshot = collect_workspace_snapshot(
                    cwd,
                    baseline_head=str(baseline_snapshot["head"]),
                    report_path=report_path,
                    checkpoint_file=checkpoint_file,
                    test_output=f"{timeout_output}\n{_report_output(report_path)}",
                )
            except RuntimeError as snapshot_error:
                diagnostic["STDERR"] = (
                    f"{timeout_stderr}\nworkspace snapshot failed: {snapshot_error}"
                )
        if snapshot is not None:
            _attach_activity_evidence(snapshot, activity_state, event_log)
            # A timeout is never success. A diff (or commits) means partial
            # work exists and must be preserved deterministically; no diff
            # still produces a distinct timeout checkpoint when requested.
            if snapshot["diff_present"]:
                diagnostic["ACTION"] = (
                    "preservar o diff e executar a recuperação determinística antes de revisar"
                )
            if checkpoint_file:
                _write_checkpoint(
                    checkpoint_file,
                    "TIMED_OUT",
                    snapshot,
                    state="IMPLEMENTATION INCOMPLETE",
                    phase="TIMED_OUT",
                    last_command=" ".join(str(part) for part in command),
                    last_output=timeout_output,
                )
            partial_workspace = bool(
                snapshot["diff_present"] or snapshot["commits_since_baseline"]
            )
            if checkpoint_file and partial_workspace and watchdog_reason != "STALLED":
                heartbeat_stop.set()
                if heartbeat_thread is not None:
                    heartbeat_thread.join(timeout=max(1.0, heartbeat_interval))
                recovery_start_head = str(snapshot["head"])
                recovery_command = [cmd_bin, *COMMAND_FLAGS]
                recovery_text = (
                    f"{prompt_text}\n\n"
                    "RECOVERY MODE: the previous implementer timed out. This is a "
                    "fresh, short CMDc process. Inspect the current workspace and "
                    "preserve valid partial work. Run the focused/full validation "
                    "required by the brief, write the requested report, and commit "
                    "only the task scope. Do not claim completion if any artifact "
                    "is missing.\n"
                )
                try:
                    recovery_command = build_command(
                        resolve_cmdc(cmd_bin), max_turns=recovery_max_turns
                    )
                    command = recovery_command
                    recovery_timeout = max(60, recovery_max_turns * 120)
                    recovery_activity = _fresh_activity_state(
                        _activity_fingerprint(snapshot)
                    )
                    recovery_completed = _run_cmdc_process(
                        recovery_command,
                        recovery_text,
                        cwd,
                        wall_timeout_seconds=recovery_timeout,
                        stall_timeout_seconds=min(stall_timeout_seconds, recovery_timeout),
                        activity_state=recovery_activity,
                        event_log=event_log,
                    )
                    recovery_output = "\n".join(
                        part
                        for part in (
                            _text_output(recovery_completed.stdout),
                            _text_output(recovery_completed.stderr),
                        )
                        if part
                    )
                    if recovery_completed.stdout:
                        print(_text_output(recovery_completed.stdout), end="")
                    if recovery_completed.stderr:
                        print(_text_output(recovery_completed.stderr), end="", file=sys.stderr)
                    recovery_snapshot = collect_workspace_snapshot(
                        cwd,
                        baseline_head=str(baseline_snapshot["head"]),
                        report_path=report_path,
                        checkpoint_file=checkpoint_file,
                        test_output=f"{recovery_output}\n{_report_output(report_path)}",
                    )
                    _attach_activity_evidence(
                        recovery_snapshot, recovery_activity, event_log
                    )
                    recovery_ready = _recovery_is_ready(
                        recovery_completed.returncode,
                        recovery_snapshot,
                        recovery_start_head,
                    )
                    _write_checkpoint(
                        checkpoint_file,
                        "RECOVERY_FINISHED",
                        recovery_snapshot,
                        state=(
                            "CHECKPOINT"
                            if recovery_ready
                            else "IMPLEMENTATION INCOMPLETE"
                        ),
                        phase="RECOVERY_FINISHED",
                        last_command=" ".join(str(part) for part in recovery_command),
                        last_output=recovery_output,
                    )
                    if recovery_ready:
                        print("STATUS: RECOVERED")
                        print(
                            "RECOVERY_EVIDENCE: commit=true report=true tests=true"
                        )
                        return 0
                    snapshot = recovery_snapshot
                    diagnostic = classify_failure(
                        recovery_completed.returncode,
                        recovery_output,
                        report_exists=bool(recovery_snapshot["report_exists"]),
                    )
                    if not diagnostic:
                        diagnostic = {
                            "BLOCKER_CODE": "RECOVERY_INCOMPLETE",
                            "MESSAGE": (
                                "a recuperação terminou sem evidência transacional completa"
                            ),
                            "COMMAND": "",
                            "EXIT_CODE": str(recovery_completed.returncode),
                            "STDERR": recovery_output,
                            "ACTION": (
                                "preservar o estado e recuperar commit, relatório e testes "
                                "antes da revisão"
                            ),
                        }
                except (FileNotFoundError, RuntimeError, subprocess.TimeoutExpired) as recovery_error:
                    recovery_output = _text_output(
                        getattr(recovery_error, "stdout", "")
                    ) + "\n" + _text_output(
                        getattr(recovery_error, "stderr", "")
                    )
                    try:
                        snapshot = collect_workspace_snapshot(
                            cwd,
                            baseline_head=str(baseline_snapshot["head"]),
                            report_path=report_path,
                            checkpoint_file=checkpoint_file,
                            test_output=f"{recovery_output}\n{_report_output(report_path)}",
                        )
                    except RuntimeError:
                        pass
                    _write_checkpoint(
                        checkpoint_file,
                        "RECOVERY_FAILED",
                        snapshot,
                        state="IMPLEMENTATION INCOMPLETE",
                        phase="RECOVERY_FAILED",
                        last_command=" ".join(str(part) for part in recovery_command),
                        last_output=recovery_output.strip(),
                    )
                    diagnostic["STDERR"] = (
                        f"{diagnostic.get('STDERR', '')}\n"
                        f"recovery failed: {recovery_error}"
                    ).strip()
                    command = recovery_command
            diagnostic["COMMAND"] = " ".join(str(part) for part in command)
            print(_render_incomplete(diagnostic, snapshot, checkpoint_file), file=sys.stderr)
            return exit_code
    finally:
        if heartbeat_thread is not None:
            heartbeat_stop.set()
            heartbeat_thread.join(timeout=max(1.0, heartbeat_interval))

    if baseline_snapshot is not None and completed is not None:
        final_snapshot = None
        known_failure_evidence = False
        try:
            final_snapshot = collect_workspace_snapshot(
                cwd,
                baseline_head=str(baseline_snapshot["head"]),
                report_path=report_path,
                checkpoint_file=checkpoint_file,
                test_output="\n".join(
                    part
                    for part in (
                        _text_output(completed.stdout),
                        _text_output(completed.stderr),
                        _report_output(report_path),
                    )
                    if part
                ),
            )
        except RuntimeError:
            final_snapshot = None
        if final_snapshot is not None:
            _attach_activity_evidence(final_snapshot, activity_state, event_log)
            has_tracked = _has_tracked_changes(final_snapshot.get("status", []))
            if allow_no_change:
                no_commit = not bool(final_snapshot["commits_since_baseline"])
                no_tracked = not has_tracked
                test_output = "\n".join(
                    part
                    for part in (
                        _text_output(completed.stdout),
                        _text_output(completed.stderr),
                        _report_output(report_path),
                    )
                    if part
                )
                test_evidence = bool(final_snapshot["tests_detectable"])
                known_failure_evidence = (
                    allow_known_test_failures
                    and completed.returncode in {0, 1}
                    and _has_known_failure_test_evidence(test_output)
                )
                transaction_ready = (
                    (completed.returncode == 0 or known_failure_evidence)
                    and no_commit
                    and no_tracked
                    and bool(final_snapshot["report_exists"])
                    and (test_evidence or known_failure_evidence)
                )
            else:
                transaction_ready = (
                    completed.returncode == 0
                    and bool(final_snapshot["commits_since_baseline"])
                    and bool(final_snapshot["report_exists"])
                    and bool(final_snapshot["tests_detectable"])
                )
            checkpoint_state = (
                "CHECKPOINT" if transaction_ready else "IMPLEMENTATION INCOMPLETE"
            )
            if checkpoint_file:
                ckpt_snapshot = dict(final_snapshot)
                if allow_no_change:
                    ckpt_snapshot["validation_only"] = True
                _write_checkpoint(
                    checkpoint_file,
                    "FINISHED",
                    ckpt_snapshot,
                    state=checkpoint_state,
                    phase="FINISHED",
                    last_command=" ".join(str(part) for part in command),
                    last_output="\n".join(
                        part for part in (completed.stdout, completed.stderr) if part
                    ),
                )
            if (completed.returncode == 0 or known_failure_evidence) and not transaction_ready:
                if allow_no_change:
                    missing = [
                        name
                        for name, present in (
                            (
                                "no-new-commit",
                                not bool(final_snapshot["commits_since_baseline"]),
                            ),
                            (
                                "no-tracked-changes",
                                not has_tracked,
                            ),
                            ("report", bool(final_snapshot["report_exists"])),
                            (
                                "tests",
                                bool(final_snapshot["tests_detectable"])
                                or known_failure_evidence,
                            ),
                        )
                        if not present
                    ]
                else:
                    missing = [
                        name
                        for name, present in (
                            ("commit", bool(final_snapshot["commits_since_baseline"])),
                            ("report", bool(final_snapshot["report_exists"])),
                            ("tests", bool(final_snapshot["tests_detectable"])),
                        )
                        if not present
                    ]
                diagnostic = {
                    "BLOCKER_CODE": "TRANSACTION_INCOMPLETE",
                    "MESSAGE": "faltam evidências obrigatórias: " + ", ".join(missing),
                    "COMMAND": "",
                    "EXIT_CODE": "1",
                    "STDERR": "",
                    "ACTION": (
                        "recuperar os artefatos faltantes antes de gerar o pacote de revisão"
                    ),
                }
                exit_code = 1

    if diagnostic:
        diagnostic["COMMAND"] = " ".join(str(part) for part in command)
        print(render_blocked(diagnostic), file=sys.stderr)
        return exit_code or 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=".", type=Path)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--max-turns", default=DEFAULT_MAX_TURNS, type=int)
    parser.add_argument("--cmd-bin", default="cmdc")
    parser.add_argument("--checkpoint-file", type=Path)
    parser.add_argument("--heartbeat-interval", default=30.0, type=float)
    parser.add_argument(
        "--wall-timeout-seconds",
        default=DEFAULT_WALL_TIMEOUT_SECONDS,
        type=int,
        help="finite process watchdog; turn budget remains controlled by --max-turns",
    )
    parser.add_argument(
        "--stall-timeout-seconds",
        default=DEFAULT_STALL_TIMEOUT_SECONDS,
        type=int,
        help="stop after no streamed event or workspace activity; 0 disables it",
    )
    parser.add_argument(
        "--recovery-max-turns", default=DEFAULT_RECOVERY_MAX_TURNS, type=int
    )
    parser.add_argument(
        "--allow-no-change",
        action="store_true",
        default=False,
        help="succeed when CMDc exits zero with report and test evidence but "
        "makes no tracked changes or commits (validation-only runs)",
    )
    parser.add_argument(
        "--allow-known-test-failures",
        action="store_true",
        default=False,
        help="in validation-only mode, accept a report with known or "
        "pre-existing out-of-scope test failures",
    )
    return parser.parse_args()


def main() -> int:
    _configure_stdio()
    args = parse_args()
    return run_implementer(
        cwd=args.cwd,
        prompt_file=args.prompt_file,
        max_turns=args.max_turns,
        cmd_bin=args.cmd_bin,
        checkpoint_file=args.checkpoint_file,
        heartbeat_interval=args.heartbeat_interval,
        recovery_max_turns=args.recovery_max_turns,
        wall_timeout_seconds=args.wall_timeout_seconds,
        stall_timeout_seconds=args.stall_timeout_seconds,
        allow_no_change=args.allow_no_change,
        allow_known_test_failures=args.allow_known_test_failures,
    )


if __name__ == "__main__":
    raise SystemExit(main())
