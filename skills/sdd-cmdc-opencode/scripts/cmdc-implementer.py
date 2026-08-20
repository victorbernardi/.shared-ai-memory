#!/usr/bin/env python3
"""Run one bounded Command Code implementer and expose fail-closed diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from sdd_cmdc_opencode.cmdc_local import (  # noqa: E402
    COMMAND_FLAGS,
    MODEL_ID,
    CmdcLocal,
    CmdcLocalError,
)
from sdd_cmdc_opencode.execution_lifecycle import (  # noqa: E402
    ExecutionLifecycle,
    default_progress_deadline,
)
from sdd_cmdc_opencode.process_supervisor import (  # noqa: E402
    ProcessFailure,
    ProcessOutcome,
    ProcessRequest,
    ProcessStatus,
    StreamEvent,
    run_process,
)
from sdd_cmdc_opencode.run_record import (  # noqa: E402
    ExecutionPolicy,
    PlanProvenance,
    ReviewPolicy,
    RunContract,
    RunRecord,
    RunRecordError,
    RunResult,
    RunStatus,
    ScopeContract,
    SuccessPolicy,
    TaskContract,
    WorkspaceContract,
    workspace_fingerprint,
)

# The fixed backend model is owned by cmdc_local; keep the contract visible at
# this adapter boundary without maintaining a second model constant.
# deepseek/deepseek-v4-flash

PROTECTED_BRANCHES = ("main", "master")
LEDGER_CONSENT_MARKER = "ALLOW_PROTECTED_BRANCH"
DEPLOYED_CONSENT_MARKER = "ALLOW_DEPLOYED_EXECUTION"
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
def _stall_expired(last_activity: float, now: float, stall_timeout: float) -> bool:
    """Return whether no observable activity occurred within the stall budget."""
    return stall_timeout > 0 and now - last_activity >= stall_timeout


def build_command(
    cmd_path: Path,
    max_turns: int = DEFAULT_MAX_TURNS,
    allow_cmdc_yolo: bool = False,
) -> list[str]:
    """Build the Command Code invocation before any platform launcher is added.

    The explicit --allow-cmdc-yolo adapter option is the only gate that adds
    the unrestricted --yolo flag; the default command keeps the normal
    permission boundary and never assumes consent.
    """
    command = [
        *CmdcLocal._launcher_prefix(cmd_path),
        "-p",
        "--model",
        MODEL_ID,
        "--max-turns",
        str(max_turns),
        "--output-format",
        "json",
    ]
    if allow_cmdc_yolo:
        command.append("--yolo")
    command.extend(("--no-skills", "--trust", "--skip-onboarding"))
    return command


def _is_deployed_server_path(path: Path) -> bool:
    """Return whether a canonical path looks like a deployed/server location.

    Conservative pattern match on canonical absolute paths so production
    contexts stay fail-closed. Any directory under the canonical checkout
    (this repository or its worktrees) is never treated as deployed.
    """
    lowered = str(path).lower().replace("/", "\\")
    return any(
        marker in lowered
        for marker in (
            "\\www\\",
            "\\wwwroot\\",
            "\\inetpub\\",
            "\\var\\www\\",
            "\\srv\\",
            "\\deploy\\",
            "\\production\\",
            "\\prod\\",
            "c:\\windows\\system32\\",
        )
    )


def _ledger_authorizes(marker: str, ledger_file: Path | None) -> bool:
    """Require an explicit recorded ledger entry before continuing."""
    if ledger_file is None:
        return False
    try:
        content = ledger_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(
        line.strip().startswith(f"{marker}:")
        or line.strip().startswith(f"{marker} ")
        for line in content.splitlines()
    )


def _preflight_blocked(
    code: str,
    message: str,
    action: str,
    *,
    cwd: Path,
    plan_file: Path,
    mode: str,
    initial_git_state: dict[str, object] | None = None,
) -> dict[str, object]:
    blocked: dict[str, object] = {
        "STATUS": "BLOCKED",
        "BLOCKER_CODE": code,
        "MESSAGE": message,
        "ACTION": action,
        "MODE": mode,
        "CWD": str(cwd),
        "PLAN_FILE": str(plan_file),
    }
    if initial_git_state is not None:
        blocked["initial_git_state"] = initial_git_state
    return blocked


def _validate_artifact_path(
    path: Path,
    git_root: Path,
    *,
    kind: str,
    require_existing: bool,
    require_readable: bool = False,
    require_contained: bool = True,
) -> dict[str, str] | None:
    """Validate a prompt/input or mutable output path without touching it."""
    try:
        resolved = path.expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        return {
            "BLOCKER_CODE": f"{kind}_UNRESOLVABLE",
            "MESSAGE": f"{kind.lower()} path cannot be resolved: {exc}",
            "ACTION": f"pass a resolvable {kind.lower()} path",
        }
    if require_contained:
        try:
            resolved.relative_to(git_root)
        except ValueError:
            return {
                "BLOCKER_CODE": f"{kind}_OUTSIDE_REPOSITORY",
                "MESSAGE": f"{kind.lower()} path is outside the repository: {resolved}",
                "ACTION": f"keep the {kind.lower()} artifact inside the repository worktree",
            }
    if require_existing:
        if not resolved.exists():
            return {
                "BLOCKER_CODE": f"{kind}_NOT_FOUND",
                "MESSAGE": f"{kind.lower()} file does not exist: {resolved}",
                "ACTION": f"create the {kind.lower()} file or pass the correct path",
            }
        if not resolved.is_file():
            return {
                "BLOCKER_CODE": f"{kind}_NOT_REGULAR_FILE",
                "MESSAGE": f"{kind.lower()} path is not a regular file: {resolved}",
                "ACTION": f"pass a regular {kind.lower()} file",
            }
        if require_readable:
            try:
                with resolved.open("rb"):
                    pass
            except (OSError, PermissionError) as exc:
                return {
                    "BLOCKER_CODE": f"{kind}_UNREADABLE",
                    "MESSAGE": f"{kind.lower()} file cannot be read: {exc}",
                    "ACTION": f"grant read access to the {kind.lower()} file",
                }
    else:
        if resolved.exists() and not resolved.is_file():
            return {
                "BLOCKER_CODE": f"{kind}_NOT_REGULAR_FILE",
                "MESSAGE": f"{kind.lower()} output path is not a regular file: {resolved}",
                "ACTION": f"pass a file path for the {kind.lower()} output",
            }
        if not resolved.parent.is_dir():
            return {
                "BLOCKER_CODE": f"{kind}_PARENT_NOT_FOUND",
                "MESSAGE": f"{kind.lower()} output directory does not exist: {resolved.parent}",
                "ACTION": f"create the parent directory for the {kind.lower()} output",
            }
    return None


def capture_initial_git_state(cwd: Path) -> dict[str, object]:
    """Capture canonical worktree, branch, HEAD, and exact status lines."""
    git_root = _run_git(cwd, "rev-parse", "--show-toplevel")
    if not git_root:
        raise RuntimeError("git root was empty")
    branch = _run_git(cwd, "symbolic-ref", "--short", "-q", "HEAD") or None
    head = _run_git(cwd, "rev-parse", "HEAD")
    status = _run_git(cwd, "status", "--short", "--untracked-files=all")
    status_lines = status.splitlines() if status else []
    return {
        "git_root": str(Path(git_root).resolve()),
        "branch": branch,
        "head": head,
        "status": status_lines,
    }


def validate_execution_boundary(
    cwd: Path,
    plan_file: Path,
    *,
    allow_protected_branch: bool,
    ledger_file: Path | None,
    allow_dirty: bool = False,
    allow_cmdc_yolo: bool = False,
) -> dict[str, object]:
    """Fail-closed preflight: repository, cwd, plan, branch, status, mode.

    The checks run in the brief's order: canonical repository root, cwd
    directory and descendant relationship, plan regular file and descendant
    relationship, Git branch/HEAD/status, protected-branch policy, and
    explicit mode consent. The initial Git snapshot preserves every
    ``git status --short`` line verbatim and is never erased or normalized.
    """
    mode = "yolo" if allow_cmdc_yolo else "normal"

    # 1. Canonical repository root; the cwd must be a real directory that is
    #    a descendant of the repository root.
    if not cwd.is_dir():
        return _preflight_blocked(
            "CWD_NOT_DIRECTORY",
            f"the working directory does not exist: {cwd}",
            "create the directory or pass an existing --cwd",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
        )
    try:
        git_root = Path(_run_git(cwd, "rev-parse", "--show-toplevel")).resolve()
    except (RuntimeError, OSError):
        return _preflight_blocked(
            "CWD_OUTSIDE_REPOSITORY",
            "the working directory is not inside a Git repository",
            "run the implementer from inside the repository worktree",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
        )
    try:
        cwd.resolve().relative_to(git_root)
    except ValueError:
        return _preflight_blocked(
            "CWD_OUTSIDE_REPOSITORY",
            f"the working directory {cwd} is outside the repository {git_root}",
            "run the implementer from inside the repository worktree",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
        )

    # 2. The plan must be a regular file inside the repository, and it must
    #    be committed before execution starts.
    if not plan_file.is_file():
        return _preflight_blocked(
            "PLAN_NOT_FOUND",
            f"the plan file does not exist: {plan_file}",
            "create the plan or pass the correct --plan-file",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
        )
    if plan_file.is_dir():
        return _preflight_blocked(
            "PLAN_NOT_FOUND",
            f"the plan path is a directory: {plan_file}",
            "pass the plan markdown file, not a directory",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
        )
    try:
        plan_file.resolve().relative_to(git_root)
    except ValueError:
        return _preflight_blocked(
            "PLAN_OUTSIDE_REPOSITORY",
            f"the plan file {plan_file} is outside the repository {git_root}",
            "keep the plan inside the repository worktree",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
        )
    try:
        committed = _run_git(
            cwd, "ls-files", "--error-unmatch", "--", str(plan_file.resolve())
        )
    except RuntimeError:
        committed = ""
    if not committed:
        return _preflight_blocked(
            "PLAN_NOT_FOUND",
            f"the plan file is not committed to the repository: {plan_file}",
            "commit the plan before starting execution",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
        )

    # 3. Initial Git snapshot before any child process starts.
    try:
        initial_git_state = capture_initial_git_state(cwd)
    except RuntimeError as exc:
        return _preflight_blocked(
            "HEAD_UNAVAILABLE",
            f"the repository has no commit yet: {exc}",
            "create an initial commit before executing",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
        )
    branch = initial_git_state["branch"]

    # 4. Protected-branch policy: main/master need explicit consent recorded
    #    in the ledger, not merely the adapter option.
    if branch in PROTECTED_BRANCHES and not (
        allow_protected_branch and _ledger_authorizes(LEDGER_CONSENT_MARKER, ledger_file)
    ):
        return _preflight_blocked(
            "BRANCH_PROTECTED",
            f"branch {branch!r} is protected; a ledger entry containing "
            f"{LEDGER_CONSENT_MARKER} is required before execution",
            "record ALLOW_PROTECTED_BRANCH in the ledger and pass "
            "--allow-protected-branch",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
            initial_git_state=initial_git_state,
        )

    # 5. Dirty state is recorded and blocked unless explicitly tolerated.
    dirty = bool(initial_git_state["status"])
    if dirty and not allow_dirty:
        return _preflight_blocked(
            "DIRTY_WORKTREE",
            "the repository has pre-existing changes; refusing to run over "
            "an uncommitted worktree",
            "commit or stash the changes, or pass an explicit allow-dirty "
            "consent",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
            initial_git_state=initial_git_state,
        )

    # 6. Deployed/server paths stay fail-closed unless a separate explicit
    #    authorization is recorded in the ledger.
    if _is_deployed_server_path(git_root) and not _ledger_authorizes(
        DEPLOYED_CONSENT_MARKER, ledger_file
    ):
        return _preflight_blocked(
            "DEPLOYED_SERVER_PATH",
            "the repository root looks like a deployed/server path; direct "
            "execution there is refused without recorded authorization",
            "record ALLOW_DEPLOYED_EXECUTION in the ledger explicitly",
            cwd=cwd,
            plan_file=plan_file,
            mode=mode,
            initial_git_state=initial_git_state,
        )

    return {
        "git_root": str(git_root),
        "branch": branch,
        "head": initial_git_state["head"],
        "dirty": dirty,
        "mode": mode,
        "yolo_consent": allow_cmdc_yolo,
        "initial_git_state": initial_git_state,
    }


def _is_native_windows_cmd(path: Path) -> bool:
    return path.name.lower() == "cmd.exe" and "system32" in {
        part.lower() for part in path.parts
    }


def resolve_cmdc(cmd_bin: str = "cmdc") -> Path:
    """Resolve Command Code through the shared local launcher Module."""
    try:
        return CmdcLocal(cmd_bin).resolve_launcher()
    except CmdcLocalError as exc:
        if exc.code != "LAUNCHER_NOT_FOUND":
            raise
        raise FileNotFoundError(str(exc)) from exc


def classify_failure(
    returncode: int,
    stderr: str,
    report_exists: bool,
    cmd_found: bool = True,
    phase: str | None = None,
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
        code = "WORKER_TURN_LIMIT" if phase == "WORKER_TURN_LIMIT" else "TIMEOUT"
        action = "revisar o limite de turnos e reexecutar controladamente"
        message = (
            "o Command Code atingiu o limite de turnos"
            if code == "WORKER_TURN_LIMIT"
            else "o Command Code atingiu o limite de tempo/turnos"
        )
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

    diagnostic = {
        "BLOCKER_CODE": code,
        "MESSAGE": message,
        "COMMAND": "",
        "EXIT_CODE": str(returncode),
        "STDERR": stderr,
        "ACTION": action,
    }
    if phase:
        diagnostic["PHASE"] = phase
    return diagnostic


def render_blocked(diagnostic: dict[str, str]) -> str:
    """Render the stable seven-field diagnostic consumed by the orchestrator.

    The explicit mode and any captured initial Git state ride along so a
    blocked boundary still exposes root, branch, HEAD, and raw status lines
    without leaking secrets (the snapshot holds only Git-derived fields).
    """
    fields = [
        ("STATUS", "BLOCKED"),
        ("BLOCKER_CODE", diagnostic.get("BLOCKER_CODE", "PROCESS_FAILED")),
        ("MESSAGE", diagnostic.get("MESSAGE", "")),
        ("COMMAND", diagnostic.get("COMMAND", "")),
        ("EXIT_CODE", diagnostic.get("EXIT_CODE", "N/A")),
        ("STDERR", diagnostic.get("STDERR", "")),
        ("ACTION", diagnostic.get("ACTION", "")),
        ("MODE", diagnostic.get("MODE", "")),
    ]
    for key in (
        "PHASE",
        "PRIMARY_BLOCKER_CODE",
        "PRIMARY_PHASE",
        "PRIMARY_COMMAND",
        "RECOVERY_BLOCKER_CODE",
        "RECOVERY_PHASE",
        "RECOVERY_COMMAND",
        "RECOVERY_ERROR",
    ):
        value = diagnostic.get(key)
        if value:
            fields.append((key, str(value)))
    initial_git_state = diagnostic.get("INITIAL_GIT_STATE")
    if initial_git_state:
        fields.append(("INITIAL_GIT_STATE", str(initial_git_state)))
    return "\n".join(
        f"{key}: {value}" if value else f"{key}:"
        for key, value in fields
    )


def _enrich_blocked_context(
    diagnostic: dict[str, str], preflight_snapshot: dict[str, object]
) -> None:
    """Carry the explicit mode and the complete initial Git snapshot on any
    diagnostic that renders through the blocked/incomplete renderers.

    The snapshot holds only Git-derived fields (canonical root, branch, HEAD,
    and raw ``git status --short`` lines), so no secrets leak.
    """
    diagnostic["MODE"] = str(preflight_snapshot["mode"])
    if diagnostic.get("INITIAL_GIT_STATE") is None:
        diagnostic["INITIAL_GIT_STATE"] = json.dumps(
            preflight_snapshot["initial_git_state"],
            ensure_ascii=False,
            sort_keys=True,
        )


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
    # Preserve every output line verbatim. Only the terminal line ending is
    # removed; leading column whitespace (for example the first space of a
    # ``git status --short`` line) is never stripped.
    return result.stdout.rstrip("\r\n")


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


class _ProcessLifecycleError(RuntimeError):
    def __init__(self, outcome: ProcessOutcome) -> None:
        failure = outcome.primary_failure
        message = failure.message if failure is not None else "process lifecycle failed"
        super().__init__(message)
        self.outcome = outcome


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
    """Run CMDc through the shared supervisor and retain adapter evidence."""

    def on_output(event: StreamEvent) -> None:
        _record_activity(activity_state, "event")
        if event_log is None:
            return
        try:
            event_log_lock = activity_state.setdefault("event_log_lock", threading.Lock())
            with event_log_lock:
                with event_log.open("a", encoding="utf-8", newline="\n") as handle:
                    handle.write(
                        json.dumps(
                            {
                                "stream": event.stream,
                                "elapsed_seconds": round(event.elapsed_seconds, 1),
                                "text": event.text,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
        except OSError:
            pass

    outcome = run_process(
        ProcessRequest(
            command=tuple(process_command),
            cwd=cwd,
            stdin_text=prompt_text,
            wall_timeout_seconds=float(wall_timeout_seconds),
            stall_timeout_seconds=float(stall_timeout_seconds),
        ),
        on_output=on_output,
    )
    if outcome.status in {ProcessStatus.WALL_TIMEOUT, ProcessStatus.STALLED}:
        error = subprocess.TimeoutExpired(
            process_command,
            timeout=(
                wall_timeout_seconds
                if outcome.status is ProcessStatus.WALL_TIMEOUT
                else stall_timeout_seconds
            ),
            output=outcome.stdout,
            stderr=outcome.stderr,
        )
        error.watchdog_reason = outcome.status.value  # type: ignore[attr-defined]
        error.watchdog_pid = outcome.pid  # type: ignore[attr-defined]
        error.watchdog_cleanup_verified = outcome.cleanup_verified  # type: ignore[attr-defined]
        error.watchdog_drain_verified = outcome.drain_verified  # type: ignore[attr-defined]
        raise error
    if outcome.primary_failure is not None or outcome.secondary_failures:
        raise _ProcessLifecycleError(outcome)
    return subprocess.CompletedProcess(
        process_command,
        outcome.returncode,
        outcome.stdout,
        outcome.stderr,
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
    preflight_snapshot: dict[str, object] | None = None,
    mode: str = "normal",
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
        "mode": mode,
    }
    if preflight_snapshot is not None:
        payload["preflight_snapshot"] = preflight_snapshot
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
    preflight_snapshot: dict[str, object] | None = None,
    mode: str = "normal",
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
                    preflight_snapshot=preflight_snapshot,
                    mode=mode,
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
                preflight_snapshot=preflight_snapshot,
                mode=mode,
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
    """Normalize a compatibility command through the shared launcher logic."""
    return [*CmdcLocal._launcher_prefix(Path(command[0])), *command[1:]]


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
    plan_file: Path | None = None,
    allow_protected_branch: bool = False,
    ledger_file: Path | None = None,
    allow_cmdc_yolo: bool = False,
    allow_dirty: bool = False,
) -> int:
    """Run Command Code and return zero only after process/report success.

    The preflight runs before any child process starts. A blocked boundary
    emits the stable seven-field diagnostic and never spawns Command Code.
    """
    cwd = cwd.expanduser().resolve()
    prompt_file = prompt_file.expanduser().resolve()
    mode = "yolo" if allow_cmdc_yolo else "normal"
    preflight_snapshot: dict[str, object] | None = None
    if plan_file is None:
        # Fail closed: without a supplied plan there is no execution boundary
        # to preflight, so Command Code must never start.
        diagnostic = {
            "BLOCKER_CODE": "PLAN_REQUIRED",
            "MESSAGE": (
                "an explicit --plan-file is required so the execution boundary "
                "preflight can run before any child process starts"
            ),
            "COMMAND": "",
            "EXIT_CODE": "1",
            "STDERR": "",
            "ACTION": "pass --plan-file and re-run the implementer",
        }
        diagnostic["MODE"] = mode
        print(render_blocked(diagnostic), file=sys.stderr)
        return 1
    preflight = validate_execution_boundary(
        cwd,
        plan_file.expanduser().resolve(),
        allow_protected_branch=allow_protected_branch,
        ledger_file=ledger_file,
        allow_dirty=allow_dirty,
        allow_cmdc_yolo=allow_cmdc_yolo,
    )
    if "BLOCKER_CODE" in preflight:
        diagnostic = {
            "BLOCKER_CODE": str(preflight["BLOCKER_CODE"]),
            "MESSAGE": str(preflight["MESSAGE"]),
            "COMMAND": "",
            "EXIT_CODE": "1",
            "STDERR": "",
            "ACTION": str(preflight["ACTION"]),
        }
        diagnostic["MODE"] = str(preflight["MODE"])
        initial_git_state = preflight.get("initial_git_state")
        if initial_git_state is not None:
            diagnostic["INITIAL_GIT_STATE"] = json.dumps(
                initial_git_state,
                ensure_ascii=False,
                sort_keys=True,
            )
        print(render_blocked(diagnostic), file=sys.stderr)
        return 1
    preflight_snapshot = preflight
    git_root = Path(str(preflight["git_root"])).resolve()

    def emit_artifact_block(error: dict[str, str]) -> int:
        diagnostic = {
            "BLOCKER_CODE": error["BLOCKER_CODE"],
            "MESSAGE": error["MESSAGE"],
            "COMMAND": "",
            "EXIT_CODE": "1",
            "STDERR": "",
            "ACTION": error["ACTION"],
            "MODE": mode,
            "INITIAL_GIT_STATE": json.dumps(
                preflight["initial_git_state"],
                ensure_ascii=False,
                sort_keys=True,
            ),
        }
        print(render_blocked(diagnostic), file=sys.stderr)
        return 1

    prompt_error = _validate_artifact_path(
        prompt_file,
        git_root,
        kind="PROMPT",
        require_existing=True,
        require_readable=True,
        # Prompt files are controller-owned, read-only inputs and may live in
        # a temporary directory outside the worktree. Mutable outputs below
        # are always contained by the repository boundary.
        require_contained=False,
    )
    if prompt_error is not None:
        return emit_artifact_block(prompt_error)
    try:
        prompt_text = prompt_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return emit_artifact_block(
            {
                "BLOCKER_CODE": "PROMPT_UNREADABLE",
                "MESSAGE": f"prompt file cannot be decoded as UTF-8: {exc}",
                "ACTION": "rewrite the prompt file as readable UTF-8 and re-run",
            }
        )

    report_path = _extract_report_path(prompt_text, cwd)
    if report_path is None:
        return emit_artifact_block(
            {
                "BLOCKER_CODE": "REPORT_PATH_MISSING",
                "MESSAGE": "the prompt does not declare a report file path",
                "ACTION": "add 'Write your full report to <path>:' inside the prompt",
            }
        )
    report_error = _validate_artifact_path(
        report_path,
        git_root,
        kind="REPORT",
        require_existing=False,
    )
    if report_error is not None:
        return emit_artifact_block(report_error)
    if checkpoint_file is not None:
        checkpoint_file = checkpoint_file.expanduser().resolve()
        checkpoint_error = _validate_artifact_path(
            checkpoint_file,
            git_root,
            kind="CHECKPOINT",
            require_existing=False,
        )
        if checkpoint_error is not None:
            return emit_artifact_block(checkpoint_error)
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
        diagnostic["MODE"] = mode
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
    cmd_path: Path | None = None
    process_command: list[str] | None = None

    try:
        cmd_path = resolve_cmdc(cmd_bin)
        command = build_command(
            cmd_path,
            max_turns=max_turns,
            allow_cmdc_yolo=allow_cmdc_yolo,
        )
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
                preflight_snapshot=preflight_snapshot,
                mode=mode,
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
                    preflight_snapshot,
                    mode,
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
            phase=("WORKER_TURN_LIMIT" if completed.returncode == 8 else None),
        )
        if diagnostic and preflight_snapshot is not None:
            diagnostic["MODE"] = str(preflight_snapshot["mode"])
            diagnostic["INITIAL_GIT_STATE"] = json.dumps(
                preflight_snapshot["initial_git_state"],
                ensure_ascii=False,
                sort_keys=True,
            )
        if known_failure_evidence:
            diagnostic = {}
            exit_code = 0
        else:
            exit_code = completed.returncode
    except _ProcessLifecycleError as exc:
        outcome = exc.outcome
        failure = outcome.primary_failure or (
            outcome.secondary_failures[0] if outcome.secondary_failures else None
        )
        failure_code = failure.code if failure is not None else "PROCESS_LIFECYCLE_FAILED"
        failure_phase = failure.phase if failure is not None else "lifecycle"
        diagnostic = {
            "BLOCKER_CODE": failure_code,
            "MESSAGE": str(exc),
            "COMMAND": " ".join(str(part) for part in (process_command or command)),
            "EXIT_CODE": "1",
            "STDERR": outcome.stderr,
            "ACTION": "preservar as evidências e corrigir a fase indicada antes de repetir",
            "PHASE": failure_phase.upper(),
        }
        if outcome.stdout:
            diagnostic["STDOUT"] = outcome.stdout
        exit_code = 1
    except CmdcLocalError as exc:
        diagnostic = {
            "BLOCKER_CODE": exc.code,
            "MESSAGE": exc.message,
            "COMMAND": "",
            "EXIT_CODE": "1",
            "STDERR": str(exc),
            "ACTION": "corrigir o launcher local antes de repetir",
            "PHASE": "RESOLUTION",
        }
        exit_code = 1
    except FileNotFoundError as exc:
        command = [cmd_bin, *COMMAND_FLAGS]
        launcher_spawn_failed = cmd_path is not None and (
            process_command is None or process_command[0] != str(cmd_path)
        )
        if not launcher_spawn_failed:
            diagnostic = classify_failure(
                127, str(exc), report_exists=False, cmd_found=False
            )
        else:
            diagnostic = {
                "BLOCKER_CODE": "LAUNCHER_SPAWN_FAILED",
                "MESSAGE": "o launcher Windows do Command Code não pôde ser iniciado",
                "COMMAND": "",
                "EXIT_CODE": "127",
                "STDERR": str(exc),
                "ACTION": "verificar COMSPEC/PowerShell e a permissão de spawn",
                "PHASE": "SPAWN",
            }
        if diagnostic and preflight_snapshot is not None:
            diagnostic["MODE"] = str(preflight_snapshot["mode"])
            diagnostic["INITIAL_GIT_STATE"] = json.dumps(
                preflight_snapshot["initial_git_state"],
                ensure_ascii=False,
                sort_keys=True,
            )
        exit_code = 127
    except subprocess.TimeoutExpired as exc:
        command = build_command(
            Path(cmd_bin), max_turns=max_turns, allow_cmdc_yolo=allow_cmdc_yolo
        )
        timeout_stdout = _text_output(exc.stdout)
        timeout_stderr = _text_output(exc.stderr) or str(exc)
        timeout_output = "\n".join(
            part for part in (timeout_stdout, timeout_stderr) if part
        )
        watchdog_reason = getattr(exc, "watchdog_reason", "WALL_TIMEOUT")
        primary_command = build_command(
            Path(cmd_bin), max_turns=max_turns, allow_cmdc_yolo=allow_cmdc_yolo
        )
        primary_command_text = " ".join(str(part) for part in primary_command)
        watchdog_cleanup_verified = getattr(
            exc, "watchdog_cleanup_verified", True
        )
        # A timeout is never success. A diff (or commits) means partial work
        # exists and must be preserved deterministically; the diagnostic keeps
        # the explicit mode so the orchestrator can see how CMDc was invoked.
        watchdog_mode = "yolo" if allow_cmdc_yolo else "normal"
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
            diagnostic["MODE"] = watchdog_mode
            diagnostic["PHASE"] = "WATCHDOG_CLEANUP"
            diagnostic["PRIMARY_BLOCKER_CODE"] = diagnostic["BLOCKER_CODE"]
            diagnostic["PRIMARY_PHASE"] = "WATCHDOG_CLEANUP"
            diagnostic["PRIMARY_COMMAND"] = primary_command_text
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
            diagnostic["MODE"] = watchdog_mode
            diagnostic["PHASE"] = "STALLED"
            if event_log is not None:
                diagnostic["EVENT_LOG"] = str(event_log)
        else:
            diagnostic = classify_failure(
                8,
                timeout_stderr,
                report_exists=False,
                phase=watchdog_reason,
            )
            diagnostic["MODE"] = watchdog_mode
        diagnostic["PRIMARY_BLOCKER_CODE"] = diagnostic.get("BLOCKER_CODE", "")
        diagnostic["PRIMARY_PHASE"] = watchdog_reason
        diagnostic["PRIMARY_COMMAND"] = primary_command_text
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
                    preflight_snapshot=preflight_snapshot,
                    mode=watchdog_mode,
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
                recovery_process_command = list(recovery_command)
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
                        resolve_cmdc(cmd_bin),
                        max_turns=recovery_max_turns,
                        allow_cmdc_yolo=allow_cmdc_yolo,
                    )
                    recovery_process_command = _platform_command(recovery_command)
                    recovery_timeout = max(60, recovery_max_turns * 120)
                    recovery_activity = _fresh_activity_state(
                        _activity_fingerprint(snapshot)
                    )
                    recovery_completed = _run_cmdc_process(
                        recovery_process_command,
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
                        last_command=" ".join(str(part) for part in recovery_process_command),
                        last_output=recovery_output,
                        preflight_snapshot=preflight_snapshot,
                        mode=watchdog_mode,
                    )
                    if recovery_ready:
                        print("STATUS: RECOVERED")
                        print(
                            "RECOVERY_EVIDENCE: commit=true report=true tests=true"
                        )
                        return 0
                    snapshot = recovery_snapshot
                    recovery_diagnostic = classify_failure(
                        recovery_completed.returncode,
                        recovery_output,
                        report_exists=bool(recovery_snapshot["report_exists"]),
                        phase="RECOVERY",
                    )
                    if not recovery_diagnostic:
                        recovery_diagnostic = {
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
                    diagnostic["RECOVERY_BLOCKER_CODE"] = recovery_diagnostic.get(
                        "BLOCKER_CODE", "RECOVERY_INCOMPLETE"
                    )
                    diagnostic["RECOVERY_PHASE"] = "RECOVERY"
                    diagnostic["RECOVERY_COMMAND"] = " ".join(
                        str(part) for part in recovery_process_command
                    )
                    diagnostic["RECOVERY_ERROR"] = recovery_diagnostic.get(
                        "STDERR", recovery_output
                    )
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
                        last_command=" ".join(str(part) for part in recovery_process_command),
                        last_output=recovery_output.strip(),
                        preflight_snapshot=preflight_snapshot,
                        mode=watchdog_mode,
                    )
                    if isinstance(recovery_error, FileNotFoundError):
                        recovery_code = "RECOVERY_SPAWN_FAILED"
                    elif isinstance(recovery_error, subprocess.TimeoutExpired):
                        recovery_code = "RECOVERY_TIMEOUT"
                    else:
                        recovery_code = "RECOVERY_FAILED"
                    diagnostic["RECOVERY_BLOCKER_CODE"] = recovery_code
                    diagnostic["RECOVERY_PHASE"] = "RECOVERY"
                    diagnostic["RECOVERY_COMMAND"] = " ".join(
                        str(part) for part in recovery_process_command
                    )
                    diagnostic["RECOVERY_ERROR"] = str(recovery_error)
                    diagnostic["STDERR"] = (
                        f"{diagnostic.get('STDERR', '')}\n"
                        f"recovery failed: {recovery_error}"
                    ).strip()
            if preflight_snapshot is not None:
                _enrich_blocked_context(diagnostic, preflight_snapshot)
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
            final_snapshot["mode"] = mode
            if preflight_snapshot is not None:
                final_snapshot["preflight_snapshot"] = preflight_snapshot
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
                    preflight_snapshot=preflight_snapshot,
                    mode=mode,
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
                diagnostic["MODE"] = mode
                exit_code = 1

    if diagnostic:
        diagnostic["COMMAND"] = " ".join(str(part) for part in command)
        if diagnostic.get("BLOCKER_CODE") == "REPORT_MISSING":
            diagnostic["MODE"] = mode
        if diagnostic.get("INITIAL_GIT_STATE") is None and preflight_snapshot is not None:
            diagnostic["INITIAL_GIT_STATE"] = json.dumps(
                preflight_snapshot["initial_git_state"],
                ensure_ascii=False,
                sort_keys=True,
            )
        print(render_blocked(diagnostic), file=sys.stderr)
        return exit_code or 1
    return 0


def _contract_run_dir(contract: RunContract, contract_file: Path) -> Path:
    """Resolve the durable Run directory without copying plan authority."""

    contract_file = contract_file.expanduser().resolve()
    if contract_file.name == "contract.json" and contract_file.parent.name == contract.run_id:
        return contract_file.parent
    if contract_file.parent.name == "runs":
        return contract_file.parent / contract.run_id
    return (
        contract.workspace.repo_root
        / ".superpowers"
        / "sdd"
        / "canonical"
        / "runs"
        / contract.run_id
    )


def _load_or_create_run(contract_file: Path) -> RunRecord:
    contract_file = contract_file.expanduser().resolve()
    contract = RunContract.load(contract_file)
    run_dir = _contract_run_dir(contract, contract_file)
    existing = run_dir / "contract.json"
    if existing.is_file():
        record = RunRecord.load(run_dir)
        if record.contract_sha256 != contract.contract_sha256:
            raise RunRecordError("existing Run Contract differs from --contract-file")
        return record
    return RunRecord.create(run_dir, contract)


def render_run_result(result: RunResult, record: RunRecord) -> str:
    """Render canonical output while retaining the adapter's short summary."""

    lines = [f"STATUS: {result.status.value}"]
    if result.primary_blocker is not None:
        lines.extend(
            [
                f"BLOCKER_CODE: {result.primary_blocker.code}",
                f"MESSAGE: {result.primary_blocker.message}",
            ]
        )
    lines.extend(
        [
            f"RUN_ID: {result.run_id}",
            f"RESULT_FILE: {record.run_dir / 'result.json'}",
            f"EVENTS_FILE: {record.run_dir / 'events.jsonl'}",
            f"CHECKPOINTS_FILE: {record.run_dir / 'checkpoints.jsonl'}",
        ]
    )
    return "\n".join(lines)


def _derive_flat_run_id(cwd: Path, plan_file: Path, task_number: int) -> str:
    """Derive the deterministic legacy Run ID from exact workspace identity.

    The ID names the plan workspace and task so a later operator can find the
    persisted Run; it is not operational authority. The plan file name is
    normalized for the Run ID grammar (the plan workspace keeps the original
    plan stem) and the derived ID remains unique per task.
    """
    repo_root = Path(cwd).resolve()
    plan_stem = plan_file.resolve().name
    safe_stem = re.sub(r"[^A-Za-z0-9._-]", "-", plan_stem).strip(".-") or "plan"
    base = f"{safe_stem}-task-{int(task_number)}"
    return f"{base}-{_flat_run_sequence(repo_root, base)}"


def _flat_run_sequence(repo_root: Path, base: str) -> int:
    """Return the next monotonic flat-Run sequence under the plan workspace."""
    plan_workspace = repo_root / ".superpowers" / "sdd"
    highest = 0
    if plan_workspace.is_dir():
        for workspace in plan_workspace.iterdir():
            runs = workspace / "runs"
            if not runs.is_dir():
                continue
            for run_dir in runs.iterdir():
                if not run_dir.is_dir():
                    continue
                match = re.fullmatch(rf"{re.escape(base)}-(\d+)", run_dir.name)
                if match:
                    highest = max(highest, int(match.group(1)))
    return highest + 1


def _flat_task_number(plan_text: str) -> int:
    """Return the single task number a legacy plan must declare.

    Legacy dispatches name one task; the Run Contract requires a task ID and a
    heading/brief from the plan, so a plan that does not identify exactly one
    task cannot be normalized deterministically and fails closed.
    """
    headings = re.findall(
        r"^(?:#{1,6}[ \t]+)?(?:\d+[.)]?[ \t]+)?"
        r"(?:Task|Tarefa)[ \t]+(\d+)(?=$|[ \t:.)-])",
        plan_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if not headings:
        raise _FlatNormalizationError(
            "the plan declares no Task/Tarefa heading; legacy flat "
            "normalization requires exactly one task"
        )
    numbers = sorted({int(value) for value in headings})
    if len(numbers) != 1:
        raise _FlatNormalizationError(
            "the plan declares multiple tasks; legacy flat normalization "
            "requires exactly one task"
        )
    return numbers[0]


class _FlatNormalizationError(ValueError):
    """The legacy flat CLI cannot be normalized into a governed Run Contract."""


def _extract_report_path_legacy(prompt_text: str, cwd: Path) -> Path:
    """Reuse the legacy marker parser for the flat prompt only.

    New Runs always use ``task.report_path`` directly; this parser exists
    only so old invocations keep their report contract. A prompt without the
    explicit marker fails closed instead of guessing a report path.
    """
    report_path = _extract_report_path(prompt_text, cwd)
    if report_path is None:
        raise _FlatNormalizationError(
            "the prompt does not declare a report file path; legacy flat "
            "normalization requires 'Write your full report to <path>:'"
        )
    return report_path


def _load_task_brief_helper() -> Any:
    """Import the adjacent task-brief extractor as a private helper module."""
    helper_path = Path(__file__).resolve().parent / "task-brief.py"
    spec = importlib.util.spec_from_file_location("_cmdc_flat_task_brief", helper_path)
    if spec is None or spec.loader is None:
        raise _FlatNormalizationError("task-brief.py is unavailable")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def _flat_scope_and_brief(
    plan_path: Path,
    plan_text: str,
    task_number: int,
) -> tuple[tuple[str, ...], str]:
    """Derive deterministic allowed scope and the exact task brief.

    The scope comes only from the task's declared ``Files``/``Arquivos``
    section through the shared extractor. When the task declares no
    deterministic paths, normalization fails closed with
    ``SCOPE_CONTRACT_MISSING`` — there is never an implicit allow-all scope.
    """
    helper = _load_task_brief_helper()
    try:
        heading, body = helper.extract_task(plan_text, task_number)
    except Exception as error:  # noqa: BLE001 - helper taxonomy boundary
        raise _FlatNormalizationError(
            f"could not extract the flat task from the plan: {error}"
        ) from error
    brief = heading + "\n" + body
    try:
        allowed = helper.extract_declared_files(brief)
    except Exception as error:  # noqa: BLE001 - strict derivation boundary
        raise _FlatNormalizationError(
            f"the task has no deterministic Files/Arquivos scope: {error}"
        ) from error
    if not allowed:
        raise _FlatNormalizationError(
            "the task declares no allowed files; legacy flat normalization "
            "requires a deterministic Files/Arquivos scope"
        )
    return tuple(allowed), brief


def _flat_plan_provenance(
    repo_root: Path,
    plan_path: Path,
    task_number: int,
) -> PlanProvenance:
    """Record the plan's own repository, branch, HEAD, path, and SHA-256.

    Legacy dispatches execute inside the same repository that owns the plan,
    so the plan is its own source. The recorded identity is the exact current
    Git identity and file hash; the lifecycle re-verifies them before spawn.
    """
    try:
        source_repository = Path(
            _run_git(repo_root, "rev-parse", "--show-toplevel")
        ).resolve()
        source_head = _run_git(repo_root, "rev-parse", "HEAD")
        branch = _run_git(repo_root, "symbolic-ref", "--short", "-q", "HEAD") or ""
    except RuntimeError as error:
        raise _FlatNormalizationError(
            f"could not capture plan provenance: {error}"
        ) from error
    try:
        plan_hash = hashlib.sha256(plan_path.read_bytes()).hexdigest()
    except OSError as error:
        raise _FlatNormalizationError(
            f"could not hash the plan file: {error}"
        ) from error
    return PlanProvenance(
        source_path=plan_path.resolve(),
        source_repository=source_repository,
        source_branch=branch,
        source_head=source_head,
        sha256=plan_hash,
    )


def _normalize_flat_contract(
    cwd: Path,
    prompt_file: Path,
    plan_file: Path,
    *,
    max_turns: int,
    checkpoint_file: Path | None,
    wall_timeout_seconds: int,
    stall_timeout_seconds: int,
    recovery_max_turns: int,
    allow_cmdc_yolo: bool,
) -> RunContract:
    """Normalize one legacy flat invocation into an immutable v1 Run Contract.

    The legacy cwd, plan, prompt/brief/report paths, timeout/turn/recovery/
    yolo/no-skills settings, exact baseline, and derived scope are carried
    into the Contract. After the Contract exists, prompt prose and mutable CLI
    values are never operational authority again: the lifecycle renders its
    own prompt from the Contract and the task brief.
    """
    cwd = cwd.expanduser().resolve()
    plan_path = plan_file.expanduser().resolve()
    prompt_path = prompt_file.expanduser().resolve()
    if not cwd.is_dir():
        raise _FlatNormalizationError(f"the working directory does not exist: {cwd}")
    if not plan_path.is_file():
        raise _FlatNormalizationError(f"the plan file does not exist: {plan_path}")
    try:
        plan_text = plan_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise _FlatNormalizationError(f"the plan file cannot be read: {error}") from error
    prompt_error = _validate_artifact_path(
        prompt_path,
        cwd,
        kind="PROMPT",
        require_existing=True,
        require_readable=True,
        require_contained=False,
    )
    if prompt_error is not None:
        raise _FlatNormalizationError(prompt_error["MESSAGE"])
    try:
        prompt_text = prompt_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise _FlatNormalizationError(f"the prompt file cannot be read: {error}") from error
    report_path = _extract_report_path_legacy(prompt_text, cwd)
    report_error = _validate_artifact_path(
        report_path, cwd, kind="REPORT", require_existing=False
    )
    if report_error is not None:
        raise _FlatNormalizationError(report_error["MESSAGE"])
    if checkpoint_file is not None:
        checkpoint_error = _validate_artifact_path(
            checkpoint_file, cwd, kind="CHECKPOINT", require_existing=False
        )
        if checkpoint_error is not None:
            raise _FlatNormalizationError(checkpoint_error["MESSAGE"])

    task_number = _flat_task_number(plan_text)
    allowed, brief = _flat_scope_and_brief(plan_path, plan_text, task_number)
    plan_provenance = _flat_plan_provenance(cwd, plan_path, task_number)

    # The task brief is an owned workspace artifact and must exist before the
    # baseline fingerprint is captured: the lifecycle then treats it as a
    # recorded pre-existing change instead of an unknown post-contract write.
    # No RunRecord exists yet here, so the baseline captures the workspace
    # without any owner authority: every run directory already on disk stays
    # visible and fails closed.
    run_id = _derive_flat_run_id(cwd, plan_path, task_number)
    brief_path = cwd / ".superpowers" / "sdd" / plan_path.stem / f"task-{task_number}-brief.md"
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_bytes = brief.encode("utf-8").replace(b"\r\n", b"\n")
    try:
        brief_path.write_bytes(brief_bytes)
    except OSError as error:
        raise _FlatNormalizationError(f"could not write the flat task brief: {error}") from error

    baseline = workspace_fingerprint(cwd)

    contract = RunContract(
        schema_version=1,
        run_id=run_id,
        task=TaskContract(
            id=task_number,
            heading=re.sub(r"^#{1,6}[ \t]+", "", brief.splitlines()[0]),
            brief_path=brief_path,
            brief_sha256=hashlib.sha256(brief_bytes).hexdigest(),
            report_path=report_path,
        ),
        plan=plan_provenance,
        workspace=WorkspaceContract(
            repo_root=cwd,
            base_head=str(baseline.get("head", "")),
            branch=str(baseline.get("branch", "")),
            baseline_status=baseline,
        ),
        scope=ScopeContract(allowed_paths=allowed, denied_paths=()),
        execution=ExecutionPolicy(
            backend="cmdc-local",
            model=MODEL_ID,
            max_turns=max(1, int(max_turns)),
            wall_timeout_seconds=max(0, int(wall_timeout_seconds)),
            stall_timeout_seconds=max(0, int(stall_timeout_seconds)),
            progress_deadline_turns=default_progress_deadline(max_turns),
            max_resumes=max(0, int(recovery_max_turns)),
            no_skills=True,
            yolo=bool(allow_cmdc_yolo),
        ),
        success=SuccessPolicy(
            require_commit=True,
            require_report=True,
            require_test_evidence=True,
        ),
        review=ReviewPolicy(auto_fix_rounds=0),
        lineage=None,
    )
    return contract


def _render_flat_blocked(code: str, message: str, action: str, *, mode: str) -> int:
    """Render the stable structured BLOCKED diagnostic for a legacy invocation."""
    diagnostic = {
        "BLOCKER_CODE": code,
        "MESSAGE": message,
        "COMMAND": "",
        "EXIT_CODE": "1",
        "STDERR": "",
        "ACTION": action,
        "MODE": mode,
    }
    print(render_blocked(diagnostic), file=sys.stderr)
    return 1


def run_flat_compat(
    cwd: Path,
    prompt_file: Path,
    plan_file: Path,
    *,
    max_turns: int,
    cmd_bin: str,
    checkpoint_file: Path | None,
    wall_timeout_seconds: int,
    stall_timeout_seconds: int,
    recovery_max_turns: int,
    allow_cmdc_yolo: bool,
    allow_protected_branch: bool,
    ledger_file: Path | None,
) -> int:
    """Execute one legacy flat invocation through the canonical lifecycle.

    The legacy arguments are normalized into an immutable v1 Run Contract
    first; when normalization is impossible the adapter returns a structured
    BLOCKED result before any launcher smoke or child process. The old
    ``run_implementer`` child-process path is never used by this route. The
    same repository/plan/branch/dirty/deployed boundary used by the legacy
    adapter API runs before the derived brief or Contract is written.
    """
    mode = "yolo" if allow_cmdc_yolo else "normal"
    preflight = validate_execution_boundary(
        cwd.expanduser().resolve(),
        plan_file.expanduser().resolve(),
        allow_protected_branch=allow_protected_branch,
        ledger_file=ledger_file,
        allow_dirty=False,
        allow_cmdc_yolo=allow_cmdc_yolo,
    )
    if "BLOCKER_CODE" in preflight:
        diagnostic = {
            "BLOCKER_CODE": str(preflight["BLOCKER_CODE"]),
            "MESSAGE": str(preflight["MESSAGE"]),
            "COMMAND": "",
            "EXIT_CODE": "1",
            "STDERR": "",
            "ACTION": str(preflight["ACTION"]),
            "MODE": mode,
        }
        initial_git_state = preflight.get("initial_git_state")
        if initial_git_state is not None:
            diagnostic["INITIAL_GIT_STATE"] = json.dumps(
                initial_git_state,
                ensure_ascii=False,
                sort_keys=True,
            )
        print(render_blocked(diagnostic), file=sys.stderr)
        return 1
    try:
        contract = _normalize_flat_contract(
            cwd,
            prompt_file,
            plan_file,
            max_turns=max_turns,
            checkpoint_file=checkpoint_file,
            wall_timeout_seconds=wall_timeout_seconds,
            stall_timeout_seconds=stall_timeout_seconds,
            recovery_max_turns=recovery_max_turns,
            allow_cmdc_yolo=allow_cmdc_yolo,
        )
    except _FlatNormalizationError as error:
        return _render_flat_blocked(
            "FLAT_NORMALIZATION_FAILED",
            str(error),
            "pass a plan with exactly one task and a deterministic Files/Arquivos "
            "scope, or use start --contract-file/resume --run-id",
            mode=mode,
        )

    # The legacy adapter creates the immutable Contract file, then the
    # canonical start path loads it and owns Run Record creation: the Contract
    # baseline was captured before the Run artifacts existed, and the durable
    # run directory is a lifecycle-owned artifact that never enters the
    # workspace audit.
    contract_file = (
        cwd
        / ".superpowers"
        / "sdd"
        / contract.plan.source_path.stem
        / "runs"
        / contract.run_id
        / "contract.json"
    )
    contract_file.parent.mkdir(parents=True, exist_ok=True)
    contract_file.write_text(
        json.dumps(contract.to_mapping(), ensure_ascii=False, sort_keys=True, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return run_canonical_start(contract_file, cmd_bin=cmd_bin)


def run_canonical_start(contract_file: Path, *, cmd_bin: str = "cmdc") -> int:
    """Load one immutable Run Contract and execute its canonical start path."""

    try:
        record = _load_or_create_run(contract_file)
    except RunRecordError as error:
        print(
            "\n".join(
                [
                    "STATUS: BLOCKED",
                    "BLOCKER_CODE: RUN_CONTRACT_INVALID",
                    f"MESSAGE: {error}",
                ]
            ),
            file=sys.stderr,
        )
        return 1
    result = ExecutionLifecycle(record, CmdcLocal(cmd_bin)).start()
    print(render_run_result(result, record))
    return 0 if result.status is RunStatus.COMPLETE else 1


def run_canonical_resume(cwd: Path, run_id: str, *, cmd_bin: str = "cmdc") -> int:
    """Resume the one Run found under ``cwd`` without rebuilding its Contract."""

    try:
        record = RunRecord.locate(cwd, run_id)
    except RunRecordError as error:
        print(
            "\n".join(
                [
                    "STATUS: BLOCKED",
                    "BLOCKER_CODE: RESUME_INVARIANT_FAILED",
                    f"MESSAGE: {error}",
                ]
            ),
            file=sys.stderr,
        )
        return 1
    result = ExecutionLifecycle(record, CmdcLocal(cmd_bin)).resume()
    print(render_run_result(result, record))
    return 0 if result.status is RunStatus.COMPLETE else 1


def _positive_int(value: str) -> int:
    """Parse a CLI integer that must be strictly positive."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def parse_args() -> argparse.Namespace:
    if len(sys.argv) > 1 and sys.argv[1] in {"start", "resume"}:
        parser = argparse.ArgumentParser(description=__doc__)
        command = sys.argv[1]
        parser.add_argument("command", choices=("start", "resume"))
        if command == "start":
            parser.add_argument("--contract-file", required=True, type=Path)
        else:
            parser.add_argument("--cwd", required=True, type=Path)
            parser.add_argument("--run-id", required=True)
        parser.add_argument("--cmd-bin", default="cmdc")
        return parser.parse_args()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=".", type=Path)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--max-turns", default=DEFAULT_MAX_TURNS, type=int)
    parser.add_argument("--cmd-bin", default="cmdc")
    parser.add_argument("--checkpoint-file", type=Path)
    parser.add_argument("--heartbeat-interval", default=30.0, type=float)
    parser.add_argument(
        "--wall-timeout-seconds",
        "--timeout-seconds",
        dest="wall_timeout_seconds",
        default=DEFAULT_WALL_TIMEOUT_SECONDS,
        type=_positive_int,
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
    parser.add_argument(
        "--plan-file",
        required=True,
        type=Path,
        help="plan file the implementation belongs to; the execution boundary "
        "preflight always runs before any child process starts",
    )
    parser.add_argument(
        "--allow-protected-branch",
        action="store_true",
        default=False,
        help="allow execution on main/master only when the ledger records "
        "ALLOW_PROTECTED_BRANCH for the branch",
    )
    parser.add_argument(
        "--allow-cmdc-yolo",
        action="store_true",
        default=False,
        help="add --yolo to the Command Code invocation only when this "
        "explicit consent is supplied; the default keeps the normal "
        "permission boundary",
    )
    parser.add_argument(
        "--ledger-file",
        type=Path,
        default=None,
        help="ledger file consulted for recorded consent entries such as "
        "ALLOW_PROTECTED_BRANCH or ALLOW_DEPLOYED_EXECUTION",
    )
    return parser.parse_args()


def main() -> int:
    _configure_stdio()
    args = parse_args()
    if getattr(args, "command", None) == "start":
        return run_canonical_start(args.contract_file, cmd_bin=args.cmd_bin)
    if getattr(args, "command", None) == "resume":
        return run_canonical_resume(args.cwd, args.run_id, cmd_bin=args.cmd_bin)
    # The legacy flat form stays accepted but is normalized into a v1 Run
    # Contract and executed through the canonical lifecycle before any
    # launcher smoke or child process. The old run_implementer child-process
    # path is never used by this route; a legacy invocation that cannot be
    # normalized returns a structured BLOCKED result.
    return run_flat_compat(
        cwd=args.cwd,
        prompt_file=args.prompt_file,
        plan_file=args.plan_file,
        max_turns=args.max_turns,
        cmd_bin=args.cmd_bin,
        checkpoint_file=args.checkpoint_file,
        wall_timeout_seconds=args.wall_timeout_seconds,
        stall_timeout_seconds=args.stall_timeout_seconds,
        recovery_max_turns=args.recovery_max_turns,
        allow_cmdc_yolo=args.allow_cmdc_yolo,
        allow_protected_branch=args.allow_protected_branch,
        ledger_file=args.ledger_file,
    )


if __name__ == "__main__":
    raise SystemExit(main())
