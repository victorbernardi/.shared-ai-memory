#!/usr/bin/env python3
"""Run one clean, ephemeral, read-only host review session.

The launcher owns only process lifecycle and deterministic evidence. OCR,
finding classification, and review reasoning remain controller responsibilities.
All incomplete or ambiguous outcomes are fail-closed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 1800
MAX_TIMEOUT_SECONDS = 3600
TIMEOUT_EXIT_CODE = 124
CHECK_FAILURE_EXIT_CODE = 2
EXEC_FAILURE_EXIT_CODE = 3
ORPHAN_EXIT_CODE = 4
REPORT_INVALID_EXIT_CODE = 5
HOST_PROCESS_EXIT_CODE = 6
_REAL_POPEN = subprocess.Popen
_WINDOW_PROCESS_TREE: set[int] | None = None

REQUIRED_REPORT_FIELDS = (
    "Files reviewed",
    "Excluded files",
    "Commands",
    "Exit codes",
    "Critical/High",
    "Medium",
    "Review status",
    "BASE",
    "HEAD",
)


def _field_value(report: str, heading: str) -> str:
    """Extract the value of a colon-terminated report heading.

    Returns the value text (joined across continuation lines) or an empty
    string when the heading is absent or has no non-empty value.
    """
    match = re.search(rf"(?im)^\s*{re.escape(heading)}\s*:\s*(.*)$", report)
    if not match:
        return ""
    return match.group(1).strip()


def _collect_report_fields(report: str) -> dict[str, str]:
    """Collect the required report fields with their values.

    A field's value is everything from the heading line up to the next line
    that starts with a required field heading. Continuation lines are joined
    with spaces so multi-line values (for example a list of files) are
    preserved as one block.
    """
    markers = tuple(REQUIRED_REPORT_FIELDS)
    lines = report.splitlines()
    collected: dict[str, str] = {}
    current: str | None = None
    for line in lines:
        stripped = line.strip()
        matched = None
        for marker in markers:
            if re.search(
                rf"^\s*{re.escape(marker)}\s*:", stripped, flags=re.IGNORECASE
            ):
                matched = marker
                break
        if matched is not None:
            current = matched
            value = stripped.split(":", 1)[1].strip()
            collected[current] = value
            continue
        if current is not None and stripped:
            collected[current] = " ".join(
                part for part in (collected[current], stripped) if part
            )
    return collected


def _extract_evidence_lines(
    report: str, heading: str, expected: str
) -> tuple[bool, str]:
    """Return whether a report field carries the exact expected evidence.

    The field may use the heading on its own line followed by an indented
    value, or the same line as ``heading: value``. The expected token must
    appear in the exact field value (not anywhere in the report), so evidence
    from an unrelated field or a stray mention cannot satisfy the check.
    """
    lines = report.splitlines()
    values: list[str] = []
    collecting = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not collecting:
            if re.search(
                rf"^\s*{re.escape(heading)}\s*:", stripped, flags=re.IGNORECASE
            ):
                collecting = True
                remainder = stripped.split(":", 1)[1].strip()
                if remainder:
                    values.append(remainder)
            continue
        if re.search(
            rf"^\s*{re.escape(heading)}\s*:", stripped, flags=re.IGNORECASE
        ):
            break
        if stripped:
            values.append(stripped)
        else:
            # A blank line ends the indented value block only when the value
            # is indented; an inline value after the heading never spans
            # blank lines.
            if values and lines[index - 1].startswith((" ", "\t")):
                break
    joined = " ".join(values)
    return bool(expected in joined), joined

def _review_status_of(report: str) -> str:
    match = re.search(
        r"(?im)^\s*Review status\s*:\s*(REVIEW CLEAN|REVIEW INCOMPLETE|BLOCKED)\s*$",
        report,
    )
    return match.group(1) if match else ""


def _classify_success(
    report_file: Path,
    base: str | None = None,
    head: str | None = None,
) -> dict[str, object]:
    if not report_file.is_file():
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_MISSING",
            "message": "host session exited 0 but the report file was not written",
        }
    try:
        report = report_file.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"status": "BLOCKED", "blocker_code": "REPORT_UNREADABLE", "message": str(exc)}

    fields = _collect_report_fields(report)
    missing = [field for field in REQUIRED_REPORT_FIELDS if field not in fields]
    if missing:
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_FIELDS_MISSING",
            "message": "report is missing required fields: " + ", ".join(missing),
        }
    empty = [
        field for field in REQUIRED_REPORT_FIELDS if not fields[field].strip()
    ]
    if empty:
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_FIELDS_EMPTY",
            "message": "report fields are empty: " + ", ".join(empty),
        }
    # The report must declare the exact reviewed range. When the caller
    # resolved BASE/HEAD refs, each corresponding report field must equal the
    # resolved value after trimming; a missing, empty, malformed, or
    # mismatched range cannot support a clean verdict (fail closed).
    mismatched: list[str] = []
    if base is not None and fields["BASE"].strip() != base.strip():
        mismatched.append("BASE")
    if head is not None and fields["HEAD"].strip() != head.strip():
        mismatched.append("HEAD")
    if mismatched:
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_RANGE_MISMATCH",
            "message": "report range does not match the reviewed range: "
            + ", ".join(mismatched),
        }
    if _review_status_of(report) != "REVIEW CLEAN":
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_STATUS_INVALID",
            "message": "report does not declare REVIEW CLEAN",
        }
    # Findings blocks are only meaningful when they name real files or
    # explicitly declare none; an empty or placeholder findings section
    # cannot support a clean verdict.
    if not _meaningful_findings(fields["Critical/High"]):
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_FINDINGS_EMPTY",
            "message": "Critical/High findings do not name any reviewed file",
        }
    if not _meaningful_findings(fields["Medium"]):
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_FINDINGS_EMPTY",
            "message": "Medium findings do not name any reviewed file",
        }
    # The report must record at least one command and its exit code. Without
    # command evidence the host session has not demonstrated the review ran.
    commands, _ = _extract_evidence_lines(report, "Commands", "")
    _, exit_codes = _extract_evidence_lines(report, "Exit codes", "")
    if not commands:
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_EVIDENCE_MISSING",
            "message": "report does not record any review command",
        }
    if not exit_codes:
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_EVIDENCE_MISSING",
            "message": "report does not record any exit code",
        }
    if not any(token.isdigit() for token in exit_codes.split()):
        return {
            "status": "BLOCKED",
            "blocker_code": "REPORT_EVIDENCE_MISSING",
            "message": "report exit codes do not contain any exit code value",
        }
    return {"status": "REVIEW CLEAN"}


def _meaningful_findings(value: str) -> bool:
    """Require structured recommendations or an explicit no-findings value."""
    if not value or not value.strip():
        return False
    stripped = value.strip()
    lowered = stripped.lower()
    if lowered in {"none", "0", "no findings"}:
        return True
    has_path = bool(re.search(r"(?im)(?:^|\s)path\s*:\s*[^\s,]+", stripped))
    has_lines = bool(
        re.search(r"(?im)(?:^|\s)start_line\s*:\s*\d+", stripped)
        and re.search(r"(?im)(?:^|\s)end_line\s*:\s*\d+", stripped)
    )
    has_detail = bool(
        re.search(
            r"(?im)(?:^|\s)(?:finding|issue|recommendation|recommendations)\s*:\s*\S+",
            stripped,
        )
    )
    return has_path and (has_lines or has_detail)


class ReviewError(Exception):
    """A validation failure that must become a BLOCKED result."""

    def __init__(self, blocker_code: str, message: str, exit_code: int = CHECK_FAILURE_EXIT_CODE):
        super().__init__(message)
        self.blocker_code = blocker_code
        self.message = message
        self.exit_code = exit_code


@dataclass
class ProcessResult:
    pid: int
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    orphaned: bool = False
    cleanup_failed: bool = False
    drain_verified: bool = False


def build_command(codex_path: Path, repo: Path, report_file: Path) -> list[str]:
    """Build the exact clean-host command; the prompt is supplied via stdin."""
    return [
        str(codex_path),
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--cd",
        str(repo),
        "--json",
        "--output-last-message",
        str(report_file),
        "-",
    ]


def _is_native_windows_cmd(path: Path) -> bool:
    return path.name.lower() == "cmd.exe" and path.parent.name.lower() == "system32"


def resolve_codex(codex_bin: str = "codex") -> Path:
    """Resolve Codex while rejecting the native Windows command interpreter."""
    direct = Path(codex_bin).expanduser()
    candidates: list[Path] = []
    if direct.is_file():
        candidates.append(direct.resolve())
    found = shutil.which(codex_bin)
    if found:
        candidates.append(Path(found).resolve())

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_file() and not _is_native_windows_cmd(candidate):
            return candidate
    raise FileNotFoundError(
        f"Codex executable '{codex_bin}' was not found; "
        "use codex or point PATH at the Codex CLI"
    )


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def validate_ref(repo: Path, ref: str, kind: str) -> str:
    if not ref or not ref.strip():
        raise ReviewError("INVALID_REF", f"{kind} ref is empty")
    result = _run_git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    if result.returncode != 0:
        raise ReviewError("INVALID_REF", f"{kind} ref '{ref}' does not resolve to a commit")
    return result.stdout.strip()


def validate_inputs(
    plan_file: Path,
    prompt_file: Path,
    repo: Path,
    base: str,
    head: str,
) -> tuple[str, str]:
    for label, path in (
        ("PLAN_FILE", plan_file),
        ("PROMPT_FILE", prompt_file),
    ):
        if not path.is_file():
            raise ReviewError("MISSING_FILE", f"{label} does not exist: {path}")
    if not repo.is_dir():
        raise ReviewError("MISSING_FILE", f"REPOSITORY does not exist: {repo}")
    return validate_ref(repo, base, "BASE"), validate_ref(repo, head, "HEAD")


def _platform_command(command: list[str]) -> list[str]:
    """Launch Windows script shims without changing the Codex backend."""
    path = Path(command[0])
    if os.name == "nt" and path.suffix.lower() in {".cmd", ".bat"}:
        launcher = os.environ.get("COMSPEC", "cmd.exe")
        return [launcher, "/d", "/s", "/c", subprocess.list2cmdline(command)]
    if os.name == "nt" and path.suffix.lower() == ".ps1":
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if not powershell:
            raise FileNotFoundError("PowerShell launcher was not found")
        return [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", *command]
    return command


def _review_environment() -> dict[str, str]:
    """Remove API/LLM endpoint credentials from the clean host environment."""
    environment = os.environ.copy()
    blocked_exact = {
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_API_BASE",
        "ANTHROPIC_API_KEY",
        "CODEX_API_KEY",
    }
    blocked_prefixes = ("OCR_LLM_", "AZURE_OPENAI_")
    for key in list(environment):
        if key in blocked_exact or key.startswith(blocked_prefixes):
            environment.pop(key, None)
    return environment


def _text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return "" if value is None else str(value)


def _creation_kwargs() -> dict[str, object]:
    if os.name == "nt":
        return {
            "creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        }
    return {"start_new_session": True}


def _run_process(
    command: list[str],
    prompt: str,
    *,
    repo: Path | None = None,
    timeout_seconds: int,
) -> ProcessResult:
    """Run a child with a retained PID and verified timeout cleanup."""
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(repo) if repo else None,
        env=_review_environment(),
        text=True,
        encoding="utf-8",
        errors="replace",
        **_creation_kwargs(),
    )
    pid = process.pid
    try:
        stdout, stderr = process.communicate(input=prompt, timeout=timeout_seconds)
        return ProcessResult(pid, process.returncode, stdout, stderr)
    except subprocess.TimeoutExpired as exc:
        stdout = _text(exc.output)
        stderr = _text(exc.stderr)
        cleanup_failed = False
        orphaned = False
        drain_verified = False
        group = _capture_process_group(pid)
        global _WINDOW_PROCESS_TREE
        _WINDOW_PROCESS_TREE = (
            _capture_windows_process_tree(pid)
            if os.name == "nt" and subprocess.Popen is _REAL_POPEN
            else None
        )
        try:
            _terminate_tree(pid)
            time.sleep(0.1)
            orphaned = (
                _process_tree_alive(pid)
                if os.name == "nt"
                else _process_tree_alive(pid, group)
            )
            if not orphaned:
                try:
                    drained_stdout, drained_stderr = process.communicate(timeout=1)
                    drain_verified = True
                except subprocess.TimeoutExpired as drain_timeout:
                    # The final drain may itself time out; every byte read so
                    # far is still partial evidence and must be preserved.
                    drain_verified = False
                    stdout += _text(drain_timeout.output)
                    stderr += _text(drain_timeout.stderr)
                except OSError:
                    cleanup_failed = True
                else:
                    stdout += _text(drained_stdout)
                    stderr += _text(drained_stderr)
        except OSError:
            cleanup_failed = True
        _WINDOW_PROCESS_TREE = None
        return ProcessResult(
            pid,
            TIMEOUT_EXIT_CODE,
            stdout,
            stderr,
            timed_out=True,
            orphaned=orphaned,
            cleanup_failed=cleanup_failed,
            drain_verified=drain_verified,
        )


def _terminate_tree(pid: int) -> None:
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


def _windows_process_parents() -> dict[int, int] | None:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if not powershell:
        return None
    try:
        result = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "Get-CimInstance Win32_Process | "
                "Select-Object ProcessId,ParentProcessId | ConvertTo-Json -Compress",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list) or not rows:
        return None
    parents: dict[int, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            return None
        pid = row.get("ProcessId")
        parent = row.get("ParentProcessId")
        if not isinstance(pid, int) or not isinstance(parent, int):
            return None
        parents[pid] = parent
    return parents


def _windows_parent_pid(pid: int) -> int | None:
    parents = _windows_process_parents()
    return None if parents is None else parents.get(pid)


def _windows_pid_in_group(pid: int, leader: int) -> bool:
    if pid == leader:
        return True
    seen: set[int] = set()
    current = pid
    while current not in seen:
        seen.add(current)
        parent = _windows_parent_pid(current)
        if parent is None:
            return True
        if parent == 0:
            return False
        if parent == leader:
            return True
        current = parent
    return True


def _capture_windows_process_tree(pid: int) -> set[int] | None:
    parents = _windows_process_parents()
    if parents is None or pid not in parents:
        return None
    tree = {pid}
    for candidate in parents:
        current = candidate
        seen: set[int] = set()
        while current not in seen:
            seen.add(current)
            if current == pid:
                tree.add(candidate)
                break
            parent = parents.get(current)
            if parent is None or parent == 0:
                break
            current = parent
    return tree


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
    """Verify the whole process tree is absent, not just the leader.

    A descendant can survive after the leader exits, which would make the
    leader-only check report a false clean cleanup. The tree is always
    traversed from the process group captured before termination because
    killpg(pid) and taskkill /T keep the group id equal to the leader pid,
    and the group identity is unrecoverable once the leader has exited.
    """
    if os.name == "nt":
        if _WINDOW_PROCESS_TREE is None:
            return True
        try:
            result = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            # tasklist could not be launched; the tree cannot be verified
            # absent, so it must count as alive: fail closed.
            return True
        if result.returncode != 0 or not result.stdout.strip():
            # A failed inventory cannot prove the tree is absent.
            return True
        live_pids: set[int] = set()
        for line in result.stdout.splitlines():
            columns = line.split(",")
            if len(columns) >= 2 and columns[1].strip().strip('"').isdigit():
                live_pids.add(int(columns[1].strip().strip('"')))
        if not live_pids:
            # Unusable output; the tree cannot be verified absent.
            return True
        return bool(_WINDOW_PROCESS_TREE & live_pids)
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


def _process_alive(pid: int) -> bool:
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
        return f'","{pid}",' in result.stdout or result.stdout.strip().startswith(f'"{pid}"')
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def _write_evidence(
    evidence_dir: Path,
    command: list[str],
    summary: dict[str, object],
    *,
    plan_file: Path,
    repo: Path,
    base: str,
    head: str,
) -> bool:
    try:
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "command.txt").write_text(
            " ".join(str(part) for part in command) + "\n", encoding="utf-8"
        )
        (evidence_dir / "stdout.jsonl").write_text(_text(summary.get("stdout")), encoding="utf-8")
        (evidence_dir / "stderr.txt").write_text(_text(summary.get("stderr")), encoding="utf-8")
        (evidence_dir / "pid.txt").write_text(_text(summary.get("pid")) + "\n", encoding="utf-8")
        (evidence_dir / "range.json").write_text(
            json.dumps(
                {"plan": str(plan_file), "repo": str(repo), "base": base, "head": head},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (evidence_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return True
    except OSError as exc:
        summary["evidence_error"] = str(exc)
        return False


def run_session(
    plan_file: Path,
    base: str,
    head: str,
    prompt_file: Path,
    report_file: Path,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    repo: Path | None = None,
    evidence_dir: Path | None = None,
    codex_bin: str = "codex",
) -> int:
    plan_file = plan_file.expanduser().resolve()
    prompt_file = prompt_file.expanduser().resolve()
    report_file = report_file.expanduser().resolve()
    repo = repo.expanduser().resolve() if repo else Path.cwd().resolve()
    evidence_dir = evidence_dir.expanduser().resolve() if evidence_dir else plan_file.parent / "evidence"
    timeout_seconds = DEFAULT_TIMEOUT_SECONDS if timeout_seconds <= 0 else min(timeout_seconds, MAX_TIMEOUT_SECONDS)
    summary: dict[str, object] = {
        "status": "BLOCKED",
        "timeout_seconds": timeout_seconds,
        "codex_executable": "",
        "stdout": "",
        "stderr": "",
        "report_exists": False,
    }
    status: dict[str, object] = {"status": "BLOCKED", "blocker_code": "NOT_STARTED"}
    command: list[str] = []
    resolved_base = base
    resolved_head = head
    exit_code = CHECK_FAILURE_EXIT_CODE
    started = time.monotonic()
    try:
        codex_path = resolve_codex(codex_bin)
        summary["codex_executable"] = str(codex_path)
        resolved_base, resolved_head = validate_inputs(
            plan_file, prompt_file, repo, base, head
        )
        command = _platform_command(build_command(codex_path, repo, report_file))
        summary.update({"base": resolved_base, "head": resolved_head, "command": command})
        result = _run_process(
            command,
            prompt_file.read_text(encoding="utf-8"),
            repo=repo,
            timeout_seconds=timeout_seconds,
        )
        summary.update(
            {
                "pid": result.pid,
                "returncode": result.returncode,
                "duration_seconds": round(time.monotonic() - started, 3),
                "timed_out": result.timed_out,
                "orphaned": result.orphaned,
                "cleanup_failed": result.cleanup_failed,
                "drain_verified": result.drain_verified,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report_exists": report_file.is_file(),
            }
        )
        if result.timed_out:
            if result.orphaned or result.cleanup_failed:
                status = {
                    "status": "BLOCKED",
                    "blocker_code": "ORPHANED_PROCESS" if result.orphaned else "CLEANUP_FAILED",
                    "message": "child process tree was not verified absent",
                }
                exit_code = ORPHAN_EXIT_CODE
            else:
                status = {"status": "REVIEW INCOMPLETE", "reason": "CLEAN_HOST_TIMEOUT"}
                exit_code = TIMEOUT_EXIT_CODE
        elif result.returncode != 0:
            status = {
                "status": "REVIEW INCOMPLETE",
                "reason": "CLEAN_HOST_EXIT",
                "exit_code": result.returncode,
            }
            exit_code = HOST_PROCESS_EXIT_CODE
        else:
            status = _classify_success(report_file, base=resolved_base, head=resolved_head)
            exit_code = 0 if status["status"] == "REVIEW CLEAN" else REPORT_INVALID_EXIT_CODE
    except FileNotFoundError as exc:
        status = {"status": "BLOCKED", "blocker_code": "CODEX_NOT_FOUND", "message": str(exc)}
        exit_code = EXEC_FAILURE_EXIT_CODE
    except ReviewError as exc:
        status = {"status": "BLOCKED", "blocker_code": exc.blocker_code, "message": exc.message}
        exit_code = exc.exit_code
    except OSError as exc:
        status = {"status": "BLOCKED", "blocker_code": "EXEC_FAILED", "message": str(exc)}
        exit_code = EXEC_FAILURE_EXIT_CODE
    except Exception as exc:  # fail closed for unexpected lifecycle failures
        status = {"status": "BLOCKED", "blocker_code": "UNEXPECTED_ERROR", "message": str(exc)}
        exit_code = EXEC_FAILURE_EXIT_CODE
    finally:
        summary.update(status)
        summary["duration_seconds"] = round(time.monotonic() - started, 3)
        if not _write_evidence(
            evidence_dir,
            command,
            summary,
            plan_file=plan_file,
            repo=repo,
            base=resolved_base,
            head=resolved_head,
        ):
            status = {
                "status": "BLOCKED",
                "blocker_code": "EVIDENCE_WRITE_FAILED",
                "message": summary.get("evidence_error", "unable to write lifecycle evidence"),
            }
            exit_code = EXEC_FAILURE_EXIT_CODE
            summary.update(status)
            _write_evidence(
                evidence_dir,
                command,
                summary,
                plan_file=plan_file,
                repo=repo,
                base=resolved_base,
                head=resolved_head,
            )
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one fail-closed clean host review session.")
    parser.add_argument("plan_file", type=Path)
    parser.add_argument("base")
    parser.add_argument("head")
    parser.add_argument("prompt_file", type=Path)
    parser.add_argument("report_file", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--repo", default=None, type=Path)
    parser.add_argument("--evidence-dir", default=None, type=Path)
    parser.add_argument("--codex-bin", default="codex")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(
        run_session(
            args.plan_file,
            args.base,
            args.head,
            args.prompt_file,
            args.report_file,
            timeout_seconds=args.timeout_seconds,
            repo=args.repo,
            evidence_dir=args.evidence_dir,
            codex_bin=args.codex_bin,
        )
    )
