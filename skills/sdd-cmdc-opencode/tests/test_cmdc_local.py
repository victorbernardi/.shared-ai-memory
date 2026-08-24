from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from sdd_cmdc_opencode.cmdc_local import (
    CmdcEvent,
    CmdcLocal,
    CmdcLocalError,
    CmdcOutcome,
    CmdcRequest,
)
from sdd_cmdc_opencode.process_supervisor import ProcessOutcome, ProcessStatus, StreamEvent


FAKE = Path(__file__).parent / "helpers" / "fake_cmdc.py"


def request(tmp_path: Path, **kwargs: object) -> CmdcRequest:
    values: dict[str, object] = {
        "cwd": tmp_path,
        "prompt": "hello",
        "max_turns": 12,
        "allow_yolo": False,
        "wall_timeout_seconds": 5.0,
        "stall_timeout_seconds": 1.0,
    }
    values.update(kwargs)
    return CmdcRequest(**values)  # type: ignore[arg-type]


def test_direct_launcher_builds_stable_start_arguments(tmp_path: Path) -> None:
    local = CmdcLocal(str(FAKE))
    command = local.build_start_command(request(tmp_path))

    assert command[:2] == (sys.executable, str(FAKE))
    assert command[2:] == (
        "-p",
        "--model",
        "deepseek/deepseek-v4-flash",
        "--max-turns",
        "12",
        "--output-format",
        "json",
        "--yolo",
        "--no-skills",
        "--trust",
        "--skip-onboarding",
        "--no-auto-update",
    )
    # Every generated command carries exactly one --yolo: CMDc writes are part
    # of the governed worker contract, so the default request cannot downgrade
    # to a weaker launcher mode.
    assert command.count("--yolo") == 1


def test_yolo_mod_and_resume_are_explicit(tmp_path: Path) -> None:
    mod = tmp_path / "probe.ts"
    mod.write_text("export default {}", encoding="utf-8")
    local = CmdcLocal(str(FAKE))
    start = local.build_start_command(
        request(tmp_path, allow_yolo=True, mod_path=mod)
    )
    resume = local.build_resume_command("session-123", request(tmp_path))

    assert "--yolo" in start
    assert start.count("--yolo") == 1
    assert start[-2:] == ("--mod", str(mod.resolve()))
    assert "--continue" not in resume
    assert resume[2:5] == ("-p", "--resume", "session-123")
    assert resume.count("--yolo") == 1


@pytest.mark.parametrize("suffix", [".exe", ".cmd", ".bat", ".ps1"])
def test_wrapper_suffixes_are_resolved(tmp_path: Path, suffix: str) -> None:
    launcher = tmp_path / f"cmdc{suffix}"
    launcher.write_text("placeholder", encoding="utf-8")
    local = CmdcLocal(str(launcher))
    resolved = local.resolve_launcher()
    assert resolved == launcher.resolve()


def test_node_wrapper_uses_declared_package_bin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    launcher = tmp_path / "cmdc.js"
    launcher.write_text("wrapper", encoding="utf-8")
    entry = tmp_path / "cli" / "actual-entry.js"
    entry.parent.mkdir()
    entry.write_text("console.log('ok')", encoding="utf-8")
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "cmdc", "bin": {"cmdc": "cli/actual-entry.js"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr("sdd_cmdc_opencode.cmdc_local.shutil.which", lambda name: name)

    command = CmdcLocal(str(launcher)).build_start_command(request(tmp_path))
    assert command[:2] == ("node", str(entry.resolve()))


def test_native_cmd_and_unsupported_or_missing_launchers_fail_closed(tmp_path: Path) -> None:
    native_cmd = Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32" / "cmd.exe"
    if native_cmd.is_file():
        with pytest.raises(CmdcLocalError) as native:
            CmdcLocal(str(native_cmd)).resolve_launcher()
        assert native.value.code == "LAUNCHER_UNSUPPORTED"

    with pytest.raises(CmdcLocalError) as missing:
        CmdcLocal(str(tmp_path / "missing" / "cmdc")).resolve_launcher()
    assert missing.value.code == "LAUNCHER_NOT_FOUND"

    unsupported = tmp_path / "cmdc.txt"
    unsupported.write_text("not executable", encoding="utf-8")
    with pytest.raises(CmdcLocalError) as error:
        CmdcLocal(str(unsupported)).resolve_launcher()
    assert error.value.code == "LAUNCHER_UNSUPPORTED"

    with pytest.raises(CmdcLocalError) as missing_unsupported:
        CmdcLocal(str(tmp_path / "missing.cmdc")).resolve_launcher()
    assert missing_unsupported.value.code == "LAUNCHER_UNSUPPORTED"


def test_ndjson_success_preserves_events_and_normalizes_result(tmp_path: Path) -> None:
    outcome = CmdcLocal(str(FAKE)).start(request(tmp_path))

    assert outcome.session_id == "session-123"
    assert outcome.subtype == "success"
    assert outcome.stop_reason == "end_turn"
    assert outcome.final_text == "done"
    assert outcome.events[0].type == "assistant_progress"
    assert outcome.events[0].turn_number == 1
    assert outcome.events[0].raw["type"] == "event"
    assert outcome.process.primary_failure is None
    assert outcome.process.cleanup_verified is True
    assert outcome.process.drain_verified is True


def test_ndjson_events_are_forwarded_to_the_live_event_sink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[CmdcEvent] = []

    def fake_run_process(process_request, *, on_output=None):
        assert on_output is not None
        event_line = (
            '{"type":"event","event":{"type":"assistant_progress",'
            '"sessionId":"session-123","turn":1}}\n'
        )
        result_line = (
            '{"type":"result","subtype":"success","stopReason":"end_turn",'
            '"sessionId":"session-123","result":"done"}\n'
        )
        on_output(
            StreamEvent(
                "stdout",
                event_line,
                0.1,
            )
        )
        on_output(
            StreamEvent(
                "stdout",
                result_line,
                0.2,
            )
        )
        return ProcessOutcome(
            pid=123,
            returncode=0,
            stdout=event_line + result_line,
            stderr="",
            status=ProcessStatus.EXITED,
            containment="test",
            cleanup_verified=True,
            drain_verified=True,
            primary_failure=None,
            secondary_failures=(),
        )

    monkeypatch.setattr("sdd_cmdc_opencode.cmdc_local.run_process", fake_run_process)

    outcome = CmdcLocal(str(FAKE)).start(request(tmp_path, event_sink=seen.append))

    assert outcome.process.primary_failure is None
    assert [event.type for event in seen] == ["assistant_progress"]
    assert seen[0].session_id == "session-123"


@pytest.mark.parametrize(
    ("variant", "subtype", "stop_reason"),
    [("error", "error", "end_turn"), ("max_turns", "max_turns", "max_turns")],
)
def test_terminal_subtypes_are_data_not_launcher_failures(
    tmp_path: Path, variant: str, subtype: str, stop_reason: str
) -> None:
    outcome = CmdcLocal(str(FAKE)).start(
        request(tmp_path, env={"FAKE_CMDC_VARIANT": variant})
    )
    assert outcome.subtype == subtype
    assert outcome.stop_reason == stop_reason
    assert outcome.process.primary_failure is None


def test_resume_uses_session_and_never_continue(tmp_path: Path) -> None:
    outcome = CmdcLocal(str(FAKE)).resume("session-123", request(tmp_path))
    assert outcome.session_id == "session-123"
    assert outcome.final_text == "done"


@pytest.mark.parametrize("variant", ["malformed", "no_session"])
def test_invalid_protocol_is_primary_after_clean_process(
    tmp_path: Path, variant: str
) -> None:
    outcome = CmdcLocal(str(FAKE)).start(
        request(tmp_path, env={"FAKE_CMDC_VARIANT": variant})
    )
    assert outcome.process.primary_failure is not None
    assert outcome.process.primary_failure.code == "CMD_CODE_PROTOCOL_ERROR"


def test_process_failure_remains_primary_when_protocol_is_incomplete(tmp_path: Path) -> None:
    outcome = CmdcLocal(str(FAKE)).start(
        request(
            tmp_path,
            env={"FAKE_CMDC_VARIANT": "stall"},
            stall_timeout_seconds=0.1,
        )
    )
    assert outcome.process.primary_failure is not None
    assert outcome.process.primary_failure.code == "STALLED"
    assert any(
        failure.code == "CMD_CODE_PROTOCOL_ERROR"
        for failure in outcome.process.secondary_failures
    )


def test_stderr_is_retained(tmp_path: Path) -> None:
    outcome = CmdcLocal(str(FAKE)).start(
        request(tmp_path, env={"FAKE_CMDC_VARIANT": "stderr"})
    )
    assert "fake-stderr" in outcome.process.stderr
    assert outcome.process.primary_failure is None


def test_fake_smoke_initializes_git_and_verifies_mod_hook(tmp_path: Path) -> None:
    preflight = CmdcLocal(str(FAKE)).smoke_test(tmp_path, require_mod_hook=True)
    assert (tmp_path / ".git").is_dir()
    assert preflight.mod_hook_verified is True
    assert preflight.smoke.session_id == "session-123"
    assert preflight.smoke.process.cleanup_verified is True
    assert preflight.smoke.process.drain_verified is True
    assert "--output-format" in preflight.command
    assert "2" in preflight.command
    # The worker mode is unconditional --yolo; the probe itself stays harmless
    # and separately scoped by its temporary workspace and blocking Mod hook.
    assert "--yolo" in preflight.command


def test_smoke_failure_reports_actionable_hook_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A completed smoke that omits the protocolar hook event fails closed with
    bounded, actionable evidence instead of only the legacy marker sentence."""
    monkeypatch.setenv("FAKE_CMDC_VARIANT", "no_hook")
    local = CmdcLocal(str(FAKE))
    with pytest.raises(CmdcLocalError) as error:
        local.smoke_test(tmp_path, require_mod_hook=True)
    assert error.value.code == "MOD_HOOK_UNVERIFIED"
    assert "smoke did not emit SDD_CMDC_MOD_HOOK_OK" in str(error.value)
    assert "expected tool_hook_blocked" in str(error.value)
    assert "session_id=session-123" in str(error.value)
    assert "remediation" in str(error.value).lower()


def test_smoke_rejects_hook_proof_when_process_cleanup_is_unverified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = CmdcLocal(str(FAKE))
    outcome = CmdcOutcome(
        process=ProcessOutcome(
            pid=1,
            returncode=None,
            stdout="",
            stderr="",
            status=ProcessStatus.WALL_TIMEOUT,
            containment="test",
            cleanup_verified=False,
            drain_verified=False,
            primary_failure=None,
            secondary_failures=(),
        ),
        subtype="success",
        stop_reason="end_turn",
        session_id="session-123",
        final_text="done",
        events=(
            CmdcEvent(
                type="tool_hook_blocked",
                tool="shell_command",
                raw={
                    "type": "event",
                    "event": {
                        "type": "tool_hook_blocked",
                        "toolName": "shell_command",
                        "hookOutput": CmdcLocal.MOD_HOOK_HANDSHAKE,
                    },
                },
            ),
        ),
    )
    monkeypatch.setattr(local, "start", lambda _request: outcome)

    with pytest.raises(CmdcLocalError) as error:
        local.smoke_test(tmp_path, require_mod_hook=True)

    assert error.value.code == "SMOKE_FAILED"
    assert "WALL_TIMEOUT" in str(error.value)
    assert "cleanup_verified=False" in str(error.value)
    assert "drain_verified=False" in str(error.value)


def test_smoke_rejects_missing_session_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = CmdcLocal(str(FAKE))
    outcome = CmdcOutcome(
        process=ProcessOutcome(
            pid=1,
            returncode=0,
            stdout="",
            stderr="",
            status=ProcessStatus.EXITED,
            containment="test",
            cleanup_verified=True,
            drain_verified=True,
            primary_failure=None,
            secondary_failures=(),
        ),
        subtype="success",
        stop_reason="end_turn",
        session_id=None,
        final_text="done",
        events=(
            CmdcEvent(
                type="tool_hook_blocked",
                tool="shell_command",
                raw={
                    "type": "event",
                    "event": {
                        "type": "tool_hook_blocked",
                        "toolName": "shell_command",
                        "hookOutput": CmdcLocal.MOD_HOOK_HANDSHAKE,
                    },
                },
            ),
        ),
    )
    monkeypatch.setattr(local, "start", lambda _request: outcome)

    with pytest.raises(CmdcLocalError) as error:
        local.smoke_test(tmp_path, require_mod_hook=True)

    assert error.value.code == "SMOKE_FAILED"
    assert "session_id=null" in str(error.value)


def test_real_smoke_allows_model_startup_burst_but_stays_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The installed launcher can spend >10s before its first turn event."""
    local = CmdcLocal(str(FAKE))
    captured: dict[str, CmdcRequest] = {}
    outcome = CmdcOutcome(
        process=ProcessOutcome(
            pid=1,
            returncode=0,
            stdout="",
            stderr="",
            status=ProcessStatus.EXITED,
            containment="test",
            cleanup_verified=True,
            drain_verified=True,
            primary_failure=None,
            secondary_failures=(),
        ),
        subtype="success",
        stop_reason="end_turn",
        session_id="session-123",
        final_text="done",
        events=(
            CmdcEvent(
                type="tool_hook_blocked",
                tool="shell_command",
                raw={
                    "type": "event",
                    "event": {
                        "type": "tool_hook_blocked",
                        "toolName": "shell_command",
                        "hookOutput": CmdcLocal.MOD_HOOK_HANDSHAKE,
                    },
                },
            ),
        ),
    )

    def fake_start(request_value: CmdcRequest) -> CmdcOutcome:
        captured["request"] = request_value
        return outcome

    monkeypatch.setattr(local, "start", fake_start)
    local.smoke_test(tmp_path, require_mod_hook=True)

    smoke_request = captured["request"]
    assert smoke_request.stall_timeout_seconds >= 90.0
    assert smoke_request.wall_timeout_seconds >= 120.0


def test_child_controlled_marker_text_never_satisfies_hook_proof() -> None:
    """The smoke proof is the Mod hook's protocolar event, not marker text.

    A child that prints the marker on stdout/stderr, or fabricates an event
    carrying the marker in its command or streams, must never satisfy
    ``mod_hook_verified``: only the exact ``tool_hook_blocked`` event with
    the exact ``hookOutput`` handshake, emitted by the core for a blocked
    ``beforeToolCall``, counts. The complete old-format fabrication
    (``reason`` + ``blocked: True``) and every partial or mismatched shape
    are rejected.
    """
    process = ProcessOutcome(
        pid=1,
        returncode=0,
        stdout=f"echo {CmdcLocal.MOD_HOOK_MARKER}\n{CmdcLocal.MOD_HOOK_MARKER}\n",
        stderr=CmdcLocal.MOD_HOOK_MARKER,
        status=ProcessStatus.EXITED,
        containment="test",
        cleanup_verified=True,
        drain_verified=True,
        primary_failure=None,
        secondary_failures=(),
    )
    from sdd_cmdc_opencode.cmdc_local import CmdcEvent, CmdcOutcome

    fabrications = (
        # Marker text in streams, command, and stdout fields.
        CmdcEvent(
            type="tool_result",
            tool="shell_command",
            command=f"echo {CmdcLocal.MOD_HOOK_MARKER}",
            stdout=CmdcLocal.MOD_HOOK_MARKER,
        ),
        # Handshake as child-controlled stream text.
        CmdcEvent(
            type="tool_result",
            tool="shell_command",
            command="echo " + CmdcLocal.MOD_HOOK_HANDSHAKE,
            stdout=CmdcLocal.MOD_HOOK_HANDSHAKE,
        ),
        # Handshake in a fabricated generic reason field.
        CmdcEvent(
            type="tool_result",
            tool="shell_command",
            command="echo x",
            raw={"reason": CmdcLocal.MOD_HOOK_HANDSHAKE},
        ),
        # The COMPLETE old-format fabrication: reason handshake + blocked.
        CmdcEvent(
            type="tool_result",
            tool="shell_command",
            command="echo x",
            raw={
                "reason": f"{CmdcLocal.MOD_HOOK_HANDSHAKE}: probe",
                "blocked": True,
                "event": {
                    "type": "tool_call",
                    "tool": "shell",
                    "command": f"echo {CmdcLocal.MOD_HOOK_MARKER}",
                    "blocked": True,
                },
            },
        ),
        # Old-format tool_call event with block markers inside the payload.
        CmdcEvent(
            type="tool_call",
            tool="shell",
            command="echo x",
            raw={
                "type": "event",
                "reason": f"{CmdcLocal.MOD_HOOK_HANDSHAKE}: probe",
                "event": {
                    "type": "tool_call",
                    "tool": "shell",
                    "command": f"echo {CmdcLocal.MOD_HOOK_MARKER}",
                    "blocked": True,
                },
            },
        ),
        # Protocolar event type but wrong toolName.
        CmdcEvent(
            type="tool_hook_blocked",
            tool="shell_command",
            raw={
                "type": "event",
                "event": {
                    "type": "tool_hook_blocked",
                    "toolName": "read_file",
                    "hookOutput": CmdcLocal.MOD_HOOK_HANDSHAKE,
                },
            },
        ),
        # Protocolar event but hookOutput is not the handshake constant.
        CmdcEvent(
            type="tool_hook_blocked",
            tool="shell_command",
            raw={
                "type": "event",
                "event": {
                    "type": "tool_hook_blocked",
                    "toolName": "shell_command",
                    "hookOutput": CmdcLocal.MOD_HOOK_MARKER,
                },
            },
        ),
        # Protocolar event missing the inner event object.
        CmdcEvent(
            type="tool_hook_blocked",
            tool="shell_command",
            raw={"type": "event"},
        ),
        # Inner type mismatch: a fabricated tool_hook_blocked inside another
        # event type.
        CmdcEvent(
            type="assistant_progress",
            raw={
                "type": "event",
                "event": {
                    "type": "tool_hook_blocked",
                    "toolName": "shell_command",
                    "hookOutput": CmdcLocal.MOD_HOOK_HANDSHAKE,
                },
            },
        ),
        # Normalized tool field contradicts the protocolar event.
        CmdcEvent(
            type="tool_hook_blocked",
            tool="shell",
            raw={
                "type": "event",
                "event": {
                    "type": "tool_hook_blocked",
                    "toolName": "shell_command",
                    "hookOutput": CmdcLocal.MOD_HOOK_HANDSHAKE,
                },
            },
        ),
    )
    for event in fabrications:
        outcome = CmdcOutcome(
            process=process,
            subtype="success",
            stop_reason="end_turn",
            session_id="session-123",
            final_text="done",
            events=(event,),
        )
        assert CmdcLocal._hook_seen(outcome) is False, event


def test_hook_handshake_proof_requires_exact_tool_hook_blocked_event() -> None:
    """The real handshake: the core's ``tool_hook_blocked`` event carries the
    ``hookOutput`` handshake the blocking ``beforeToolCall`` returned. Only
    that exact protocolar event satisfies the proof."""
    from sdd_cmdc_opencode.cmdc_local import CmdcEvent, CmdcOutcome

    event = CmdcEvent(
        type="tool_hook_blocked",
        tool="shell_command",
        raw={
            "type": "event",
            "event": {
                "type": "tool_hook_blocked",
                "toolName": "shell_command",
                "hookOutput": CmdcLocal.MOD_HOOK_HANDSHAKE,
            },
        },
    )
    outcome = CmdcOutcome(
        process=ProcessOutcome(
            pid=1,
            returncode=0,
            stdout="",
            stderr="",
            status=ProcessStatus.EXITED,
            containment="test",
            cleanup_verified=True,
            drain_verified=True,
            primary_failure=None,
            secondary_failures=(),
        ),
        subtype="success",
        stop_reason="end_turn",
        session_id="session-123",
        final_text="done",
        events=(event,),
    )
    assert CmdcLocal._hook_seen(outcome) is True


def test_scope_mod_environment_is_forwarded_to_start_and_resume(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod = tmp_path / "_scope_mod.ts"
    helper = tmp_path / "_scope_guard.py"
    contract = tmp_path / "scope-contract.json"
    for path in (mod, helper, contract):
        path.write_text("fixture\n", encoding="utf-8")
    captured: list[object] = []

    def fake_run(request):
        captured.append(request)
        return ProcessOutcome(
            pid=1,
            returncode=0,
            stdout=(
                '{"type":"result","subtype":"success",'
                '"sessionId":"session-123","stopReason":"end_turn","result":"done"}\n'
            ),
            stderr="",
            status=ProcessStatus.EXITED,
            containment="test",
            cleanup_verified=True,
            drain_verified=True,
            primary_failure=None,
            secondary_failures=(),
        )

    monkeypatch.setattr("sdd_cmdc_opencode.cmdc_local.run_process", fake_run)
    scope_env = {
        "SDD_CMDC_SCOPE_PYTHON": str(Path(sys.executable).resolve()),
        "SDD_CMDC_SCOPE_HELPER": str(helper.resolve()),
        "SDD_CMDC_SCOPE_CONTRACT": str(contract.resolve()),
    }
    monkeypatch.setenv("SDD_CMDC_SCOPE_FOREIGN", "must-not-leak")
    request_value = request(tmp_path, mod_path=mod, scope_env=scope_env)
    local = CmdcLocal(str(FAKE))

    local.start(request_value)
    local.resume("session-123", request_value)

    assert len(captured) == 2
    for process_request in captured:
        assert process_request.env is not None
        # Assert every requested scope variable is forwarded with its exact
        # value and foreign parent scope variables are not leaked into the
        # child, where the Mod would terminate the Run.
        for key, value in scope_env.items():
            assert process_request.env.get(key) == value
        assert "SDD_CMDC_SCOPE_FOREIGN" not in process_request.env


def test_scope_mod_environment_rejects_unexpected_scope_variables(tmp_path: Path) -> None:
    local = CmdcLocal(str(FAKE))

    with pytest.raises(CmdcLocalError) as error:
        local.start(
            request(
                tmp_path,
                scope_env={"SDD_CMDC_SCOPE_SECRET": "must-not-pass"},
            )
        )
    assert error.value.code == "SCOPE_ENV_INVALID"


@pytest.mark.skipif(
    os.environ.get("SDD_CMDC_REAL_SMOKE") != "1",
    reason="set SDD_CMDC_REAL_SMOKE=1 to run the installed local launcher",
)
def test_real_launcher_smoke(tmp_path: Path) -> None:
    preflight = CmdcLocal().smoke_test(tmp_path, require_mod_hook=True)
    assert preflight.smoke.session_id
    assert preflight.mod_hook_verified is True
    assert preflight.smoke.process.cleanup_verified is True
    assert preflight.smoke.process.drain_verified is True
