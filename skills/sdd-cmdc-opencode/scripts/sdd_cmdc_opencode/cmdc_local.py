from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from .process_supervisor import (
    ProcessFailure,
    ProcessOutcome,
    ProcessRequest,
    run_process,
)


MODEL_ID = "deepseek/deepseek-v4-flash"
COMMAND_FLAGS = ("--no-skills", "--trust", "--skip-onboarding")
MOD_HOOK_MARKER = "SDD_CMDC_MOD_HOOK_OK"
MOD_HOOK_HANDSHAKE = "SDD_CMDC_MOD_HOOK_HANDSHAKE"
SCOPE_ENV_NAMES = frozenset(
    {
        "SDD_CMDC_SCOPE_PYTHON",
        "SDD_CMDC_SCOPE_HELPER",
        "SDD_CMDC_SCOPE_CONTRACT",
        "SDD_CMDC_SCOPE_RUN_OWNER",
    }
)

__all__ = [
    "CmdcEvent",
    "CmdcLocal",
    "CmdcLocalError",
    "CmdcOutcome",
    "CmdcPreflight",
    "CmdcRequest",
]


class CmdcLocalError(RuntimeError):
    """A fail-closed launcher or local protocol error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class CmdcEvent:
    type: str
    session_id: str | None = None
    turn_number: int | None = None
    tool: str | None = None
    command: str | None = None
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    raw: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class CmdcRequest:
    cwd: Path
    prompt: str
    max_turns: int
    allow_yolo: bool
    wall_timeout_seconds: float
    stall_timeout_seconds: float
    mod_path: Path | None = None
    env: Mapping[str, str] | None = None
    scope_env: Mapping[str, str] | None = None


@dataclass(frozen=True)
class CmdcOutcome:
    process: ProcessOutcome
    subtype: str | None
    stop_reason: str | None
    session_id: str | None
    final_text: str
    events: tuple[CmdcEvent, ...]


@dataclass(frozen=True)
class CmdcPreflight:
    launcher: Path
    command: tuple[str, ...]
    smoke: CmdcOutcome
    mod_hook_verified: bool


def _is_native_cmd(path: Path) -> bool:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        resolved = path
    return (
        resolved.name.casefold() == "cmd.exe"
        and "system32" in {part.casefold() for part in resolved.parts}
    )


def _is_explicit_path(value: str) -> bool:
    path = Path(value)
    return path.is_absolute() or len(path.parts) > 1 or "/" in value or "\\" in value


def _find_node_bin(package_json: Path, launcher: Path) -> Path | None:
    try:
        metadata = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(metadata, dict):
        return None
    bin_value = metadata.get("bin")
    if isinstance(bin_value, str):
        entry = bin_value
    elif isinstance(bin_value, dict):
        package_name = str(metadata.get("name", "")).rsplit("/", 1)[-1]
        candidates = (package_name, launcher.stem, "cmdc")
        entry = next(
            (str(bin_value[name]) for name in candidates if name in bin_value),
            next((str(value) for value in bin_value.values() if isinstance(value, str)), ""),
        )
    else:
        return None
    if not entry:
        return None
    return (package_json.parent / entry).resolve(strict=False)


def _package_json_for(path: Path) -> Path | None:
    current = path.parent
    for _ in range(7):
        candidate = current / "package.json"
        if candidate.is_file():
            return candidate
        if current.parent == current:
            break
        current = current.parent
    return None


def _string_value(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _int_value(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _mapping_value(mapping: Mapping[str, object], *names: str) -> object:
    for name in names:
        if name in mapping:
            return mapping[name]
    return None


def _text_value(value: object) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        return str(value)


class CmdcLocal:
    """Concrete local Command Code launcher and NDJSON protocol adapter."""

    MOD_HOOK_MARKER = MOD_HOOK_MARKER
    MOD_HOOK_HANDSHAKE = MOD_HOOK_HANDSHAKE

    def __init__(self, cmd_bin: str = "cmdc") -> None:
        self.cmd_bin = cmd_bin

    def resolve_launcher(self) -> Path:
        requested = Path(self.cmd_bin).expanduser()
        explicit = _is_explicit_path(self.cmd_bin)
        candidates: list[Path] = []

        if explicit:
            candidates.append(requested)
        else:
            on_path = shutil.which(self.cmd_bin)
            if on_path:
                candidates.append(Path(on_path))
            if os.name == "nt":
                appdata = os.environ.get("APPDATA")
                if appdata:
                    npm_dir = Path(appdata) / "npm"
                    candidates.extend(
                        npm_dir / f"{self.cmd_bin}{suffix}"
                        for suffix in (".cmd", ".ps1", ".bat", "")
                    )

        for candidate in candidates:
            if candidate.is_file():
                resolved = candidate.resolve()
                if _is_native_cmd(resolved):
                    raise CmdcLocalError(
                        "LAUNCHER_UNSUPPORTED",
                        "native Windows cmd.exe is not a Command Code launcher",
                    )
                self._validate_suffix(resolved)
                return resolved

        if explicit and requested.suffix.casefold() not in {
            "",
            ".bat",
            ".cmd",
            ".exe",
            ".js",
            ".ps1",
            ".py",
        }:
            raise CmdcLocalError(
                "LAUNCHER_UNSUPPORTED",
                f"unsupported launcher suffix: {requested.suffix}",
            )
        raise CmdcLocalError(
            "LAUNCHER_NOT_FOUND",
            f"Command Code launcher not found: {self.cmd_bin}",
        )

    @staticmethod
    def _validate_suffix(path: Path) -> None:
        suffix = path.suffix.casefold()
        supported = {"", ".bat", ".cmd", ".exe", ".js", ".ps1", ".py"}
        if suffix not in supported:
            raise CmdcLocalError(
                "LAUNCHER_UNSUPPORTED",
                f"unsupported launcher suffix: {path.suffix}",
            )

    @staticmethod
    def _launcher_prefix(launcher: Path) -> tuple[str, ...]:
        suffix = launcher.suffix.casefold()
        if suffix == ".ps1":
            if os.name != "nt":
                return (str(launcher),)
            powershell = shutil.which("pwsh") or shutil.which("powershell")
            if not powershell:
                raise CmdcLocalError(
                    "LAUNCHER_UNSUPPORTED",
                    "PowerShell is required for a .ps1 launcher",
                )
            return (
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(launcher),
            )
        if suffix in {".cmd", ".bat"}:
            if os.name != "nt":
                return (str(launcher),)
            shell = os.environ.get("COMSPEC") or shutil.which("cmd.exe")
            if not shell:
                raise CmdcLocalError(
                    "LAUNCHER_UNSUPPORTED",
                    "cmd.exe is required for a Windows shell launcher",
                )
            return (shell, "/d", "/c", str(launcher))
        if suffix == ".js":
            package_json = _package_json_for(launcher)
            entry = _find_node_bin(package_json, launcher) if package_json else None
            node = shutil.which("node") or "node"
            return (node, str(entry or launcher))
        if suffix == ".py":
            return (sys.executable, str(launcher))
        return (str(launcher),)

    @staticmethod
    def _validate_mod(mod_path: Path | None) -> Path | None:
        if mod_path is None:
            return None
        try:
            resolved = mod_path.expanduser().resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise CmdcLocalError(
                "MOD_PATH_INVALID", f"Command Code Mod is not readable: {mod_path}"
            ) from exc
        if not resolved.is_file():
            raise CmdcLocalError(
                "MOD_PATH_INVALID", f"Command Code Mod is not a file: {resolved}"
            )
        return resolved

    def _build_command(
        self,
        request: CmdcRequest,
        *,
        session_id: str | None = None,
    ) -> tuple[str, ...]:
        if request.max_turns <= 0:
            raise ValueError("max_turns must be positive")
        launcher = self.resolve_launcher()
        command = list(self._launcher_prefix(launcher))
        command.extend(("-p",))
        if session_id is not None:
            if not session_id:
                raise ValueError("session_id must not be empty")
            command.extend(("--resume", session_id))
        command.extend(
            (
                "--model",
                MODEL_ID,
                "--max-turns",
                str(request.max_turns),
                "--output-format",
                "json",
            )
        )
        if request.allow_yolo:
            command.append("--yolo")
        command.extend(COMMAND_FLAGS)
        mod_path = self._validate_mod(request.mod_path)
        if mod_path is not None:
            command.extend(("--mod", str(mod_path)))
        return tuple(command)

    def build_start_command(self, request: CmdcRequest) -> tuple[str, ...]:
        return self._build_command(request)

    def build_resume_command(
        self, session_id: str, request: CmdcRequest
    ) -> tuple[str, ...]:
        return self._build_command(request, session_id=session_id)

    @staticmethod
    def _event_from_mapping(
        event: Mapping[str, object], raw: Mapping[str, object]
    ) -> CmdcEvent:
        return CmdcEvent(
            type=_string_value(event.get("type")) or "unknown",
            session_id=_string_value(
                _mapping_value(event, "sessionId", "session_id")
            ),
            turn_number=_int_value(
                _mapping_value(event, "turnNumber", "turn_number", "turn")
            ),
            tool=_string_value(event.get("tool")),
            command=_string_value(event.get("command")),
            exit_code=_int_value(_mapping_value(event, "exitCode", "exit_code")),
            stdout=_text_value(event.get("stdout")),
            stderr=_text_value(event.get("stderr")),
            raw=raw,
        )

    @staticmethod
    def _protocol_failure(message: str) -> ProcessFailure:
        return ProcessFailure(
            code="CMD_CODE_PROTOCOL_ERROR",
            phase="protocol",
            message=message,
        )

    @classmethod
    def _parse_output(
        cls, process: ProcessOutcome
    ) -> tuple[tuple[CmdcEvent, ...], dict[str, object], list[str]]:
        events: list[CmdcEvent] = []
        result: dict[str, object] = {}
        diagnostics: list[str] = []
        result_count = 0
        for line_number, line in enumerate(process.stdout.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                diagnostics.append(f"line {line_number}: malformed JSON: {exc.msg}")
                continue
            if not isinstance(payload, dict):
                diagnostics.append(f"line {line_number}: NDJSON value is not an object")
                continue
            payload_type = payload.get("type")
            if payload_type == "result":
                result_count += 1
                if result_count == 1:
                    result = payload
                continue
            if payload_type == "event":
                inner = payload.get("event")
                if not isinstance(inner, dict):
                    diagnostics.append(
                        f"line {line_number}: event payload is not an object"
                    )
                    continue
                events.append(cls._event_from_mapping(inner, payload))
                continue
            if isinstance(payload_type, str):
                events.append(cls._event_from_mapping(payload, payload))
            else:
                diagnostics.append(f"line {line_number}: missing event type")

        if result_count == 0:
            diagnostics.append("missing terminal result")
        elif result_count > 1:
            diagnostics.append("more than one terminal result")
        return tuple(events), result, diagnostics

    @classmethod
    def _translate(
        cls, process: ProcessOutcome
    ) -> CmdcOutcome:
        events, result, diagnostics = cls._parse_output(process)
        subtype = _string_value(result.get("subtype"))
        stop_reason = _string_value(
            _mapping_value(result, "stopReason", "stop_reason")
        )
        session_id = _string_value(
            _mapping_value(result, "sessionId", "session_id")
        )
        final_text = _text_value(result.get("result"))
        if result and session_id is None:
            diagnostics.append("terminal result is missing sessionId")

        translated = process
        if diagnostics:
            diagnostic = cls._protocol_failure("; ".join(diagnostics))
            if translated.primary_failure is None:
                translated = replace(translated, primary_failure=diagnostic)
            else:
                translated = replace(
                    translated,
                    secondary_failures=translated.secondary_failures + (diagnostic,),
                )
        return CmdcOutcome(
            process=translated,
            subtype=subtype,
            stop_reason=stop_reason,
            session_id=session_id,
            final_text=final_text,
            events=events,
        )

    def _run(
        self, request: CmdcRequest, command: tuple[str, ...]
    ) -> CmdcOutcome:
        process_env = self._process_environment(request)
        process = run_process(
            ProcessRequest(
                command=command,
                cwd=request.cwd,
                stdin_text=request.prompt,
                wall_timeout_seconds=request.wall_timeout_seconds,
                stall_timeout_seconds=request.stall_timeout_seconds,
                env=process_env,
            )
        )
        return self._translate(process)

    @staticmethod
    def _process_environment(request: CmdcRequest) -> Mapping[str, str] | None:
        if request.scope_env is None:
            return request.env
        unexpected = set(request.scope_env) - SCOPE_ENV_NAMES
        if unexpected:
            raise CmdcLocalError(
                "SCOPE_ENV_INVALID",
                f"unexpected scope environment variables: {sorted(unexpected)}",
            )
        if any(not isinstance(key, str) or not isinstance(value, str) for key, value in request.scope_env.items()):
            raise CmdcLocalError(
                "SCOPE_ENV_INVALID",
                "scope environment keys and values must be strings",
            )
        environment = dict(os.environ)
        if request.env is not None:
            environment.update(request.env)
        environment.update(request.scope_env)
        return environment

    def start(self, request: CmdcRequest) -> CmdcOutcome:
        return self._run(request, self.build_start_command(request))

    def resume(self, session_id: str, request: CmdcRequest) -> CmdcOutcome:
        return self._run(request, self.build_resume_command(session_id, request))

    @staticmethod
    def _run_git_init(cwd: Path) -> None:
        cwd.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ("git", "init", "--quiet"),
                cwd=cwd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise CmdcLocalError("SMOKE_FAILED", f"git repository setup failed: {exc}") from exc

    @classmethod
    def _hook_seen(cls, outcome: CmdcOutcome) -> bool:
        # Authoritative hook proof: the installed Command Code emits the
        # protocolar `tool_hook_blocked` event when a mod's beforeToolCall
        # returns `block: true`, and `hookOutput` carries exactly the
        # additionalContext the mod returned. The whole object still comes
        # from the child's NDJSON stream, so nothing child-controlled is
        # trusted: the event type, the exact hookOutput value, and the
        # toolName normalization are all required. The normalized toolName
        # only mirrors the documented protocol (the event's own toolName is
        # the registered tool name); it never widens the proof.
        for event in outcome.events:
            if event.type != "tool_hook_blocked":
                continue
            raw = event.raw
            if not isinstance(raw, Mapping):
                continue
            inner = raw.get("event")
            if not isinstance(inner, Mapping):
                continue
            if inner.get("type") != "tool_hook_blocked":
                continue
            hook_output = inner.get("hookOutput")
            if hook_output != MOD_HOOK_HANDSHAKE:
                continue
            tool_name = inner.get("toolName")
            if tool_name != "shell_command":
                continue
            if event.tool not in (None, "shell_command"):
                continue
            return True
        return False

    def smoke_test(
        self,
        cwd: Path,
        require_mod_hook: bool,
        mod_path: Path | None = None,
    ) -> CmdcPreflight:
        smoke_cwd = Path(cwd).expanduser().resolve()
        self._run_git_init(smoke_cwd)
        selected_mod_path = mod_path or Path(__file__).with_name("_mod_probe.ts")
        request = CmdcRequest(
            cwd=smoke_cwd,
            prompt=(
                f"Run the harmless marker command: echo {MOD_HOOK_MARKER}. "
                "Expect the beforeToolCall hook to block it."
            ),
            max_turns=2,
            allow_yolo=True,
            wall_timeout_seconds=120.0,
            stall_timeout_seconds=90.0,
            mod_path=selected_mod_path,
        )
        command = self.build_start_command(request)
        outcome = self.start(request)
        hook_seen = self._hook_seen(outcome)
        if require_mod_hook and not hook_seen:
            raise CmdcLocalError(
                "MOD_HOOK_UNVERIFIED",
                f"smoke did not emit {MOD_HOOK_MARKER}",
            )
        return CmdcPreflight(
            launcher=self.resolve_launcher(),
            command=command,
            smoke=outcome,
            mod_hook_verified=hook_seen,
        )
