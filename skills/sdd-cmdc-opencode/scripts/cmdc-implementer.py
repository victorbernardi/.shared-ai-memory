#!/usr/bin/env python3
"""Run one bounded Command Code implementer and expose fail-closed diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

MODEL_ID = "deepseek/deepseek-v4-flash"
DEFAULT_MAX_TURNS = 20
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
COMMAND_FLAGS = (
    "--no-skills",
    "--trust",
    "--skip-onboarding",
    "--yolo",
)


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


def _has_test_evidence(output: str) -> bool:
    return not TEST_FAILURE_RE.search(output) and bool(TEST_EVIDENCE_RE.search(output))


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
    }


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
    checkpoint_file: Path,
    command: str,
    interval: float,
    stop_event: threading.Event,
) -> None:
    while not stop_event.wait(interval):
        try:
            snapshot = collect_workspace_snapshot(
                cwd,
                baseline_head=baseline_head,
                report_path=report_path,
                checkpoint_file=checkpoint_file,
            )
        except RuntimeError as exc:
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
            if heartbeat_interval > 0:
                heartbeat_thread = threading.Thread(
                    target=_heartbeat_loop,
                    args=(
                        cwd,
                        str(baseline_snapshot["head"]),
                        report_path,
                        checkpoint_file,
                        command_text,
                        heartbeat_interval,
                        heartbeat_stop,
                    ),
                    daemon=True,
                )
                heartbeat_thread.start()
        completed = subprocess.run(
            process_command,
            input=prompt_text,
            text=True,
            cwd=str(cwd),
            capture_output=True,
            check=False,
            timeout=max(60, max_turns * 120),
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
        diagnostic = classify_failure(
            completed.returncode,
            stderr if completed.stderr else "",
            report_exists=report_exists,
        )
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
            if checkpoint_file and partial_workspace:
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
                    recovery_completed = subprocess.run(
                        _platform_command(recovery_command),
                        input=recovery_text,
                        text=True,
                        cwd=str(cwd),
                        capture_output=True,
                        check=False,
                        timeout=max(60, recovery_max_turns * 120),
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
            transaction_ready = (
                completed.returncode == 0
                and bool(final_snapshot["commits_since_baseline"])
                and bool(final_snapshot["report_exists"])
                and bool(final_snapshot["tests_detectable"])
            )
            if checkpoint_file:
                _write_checkpoint(
                    checkpoint_file,
                    "FINISHED",
                    final_snapshot,
                    state=(
                        "CHECKPOINT"
                        if transaction_ready
                        else "IMPLEMENTATION INCOMPLETE"
                    ),
                    phase="FINISHED",
                    last_command=" ".join(str(part) for part in command),
                    last_output="\n".join(
                        part for part in (completed.stdout, completed.stderr) if part
                    ),
                )
            if completed.returncode == 0 and not transaction_ready:
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
        "--recovery-max-turns", default=DEFAULT_RECOVERY_MAX_TURNS, type=int
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_implementer(
        cwd=args.cwd,
        prompt_file=args.prompt_file,
        max_turns=args.max_turns,
        cmd_bin=args.cmd_bin,
        checkpoint_file=args.checkpoint_file,
        heartbeat_interval=args.heartbeat_interval,
        recovery_max_turns=args.recovery_max_turns,
    )


if __name__ == "__main__":
    raise SystemExit(main())
