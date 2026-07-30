#!/usr/bin/env python3
"""Run one bounded Command Code implementer and expose fail-closed diagnostics."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MODEL_ID = "deepseek/deepseek-v4-flash"
DEFAULT_MAX_TURNS = 20
COMMAND_FLAGS = ("-p", "--model", MODEL_ID, "--trust", "--skip-onboarding", "--yolo")
REPORT_MARKER = "Write your full report to "


def build_command(cmd_path: Path, max_turns: int = DEFAULT_MAX_TURNS) -> list[str]:
    """Build the Command Code invocation before any platform launcher is added."""
    return [
        str(cmd_path),
        "-p",
        "--model",
        MODEL_ID,
        "--max-turns",
        str(max_turns),
        "--trust",
        "--skip-onboarding",
        "--yolo",
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


def _extract_report_path(prompt_text: str, cwd: Path) -> Path | None:
    for line in prompt_text.splitlines():
        if REPORT_MARKER not in line:
            continue
        candidate = line.split(REPORT_MARKER, 1)[1].strip().rstrip(":")
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
) -> int:
    """Run Command Code and return zero only after process/report success."""
    cwd = cwd.expanduser().resolve()
    prompt_file = prompt_file.expanduser().resolve()
    prompt_text = prompt_file.read_text(encoding="utf-8")
    report_path = _extract_report_path(prompt_text, cwd)

    try:
        cmd_path = resolve_cmdc(cmd_bin)
        command = build_command(cmd_path, max_turns=max_turns)
        process_command = _platform_command(command)
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
            sys.stdout.write(completed.stdout)
            if not completed.stdout.endswith("\n"):
                sys.stdout.write("\n")
        if completed.stderr:
            sys.stderr.write(completed.stderr)
            if not completed.stderr.endswith("\n"):
                sys.stderr.write("\n")
        report_exists = report_path is not None and report_path.is_file()
        diagnostic = classify_failure(
            completed.returncode,
            completed.stderr,
            report_exists=report_exists,
        )
        exit_code = completed.returncode
    except FileNotFoundError as exc:
        command = [cmd_bin, *COMMAND_FLAGS]
        diagnostic = classify_failure(127, str(exc), report_exists=False, cmd_found=False)
        exit_code = 127
    except subprocess.TimeoutExpired as exc:
        command = build_command(Path(cmd_bin), max_turns=max_turns)
        diagnostic = classify_failure(8, str(exc), report_exists=False)
        exit_code = 8

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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_implementer(
        cwd=args.cwd,
        prompt_file=args.prompt_file,
        max_turns=args.max_turns,
        cmd_bin=args.cmd_bin,
    )


if __name__ == "__main__":
    raise SystemExit(main())
