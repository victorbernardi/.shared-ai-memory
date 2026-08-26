from __future__ import annotations

import subprocess
from dataclasses import dataclass, replace
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

import sdd_cmdc_opencode.execution_lifecycle as lifecycle_module
from sdd_cmdc_opencode.cmdc_local import CmdcEvent, CmdcOutcome
from sdd_cmdc_opencode.process_supervisor import (
    ProcessCallbackError,
    ProcessFailure,
    ProcessOutcome,
    ProcessStatus,
)
from sdd_cmdc_opencode.run_record import (
    ExecutionPolicy,
    PlanProvenance,
    ReviewPolicy,
    RunContract,
    RunRecord,
    RunStatus,
    ScopeContract,
    SuccessPolicy,
    TaskContract,
    WorkspaceContract,
    workspace_fingerprint,
)
from sdd_cmdc_opencode.execution_lifecycle import (
    NO_IMPLEMENTATION_PROGRESS,
    ExecutionLifecycle,
    LifecycleError,
    _render_contract_prompt,
    default_progress_deadline,
    evaluate_progress,
    normalize_test_evidence,
    persist_progress_checkpoint,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _run_fixture(
    tmp_path: Path,
    *,
    max_resumes: int = 0,
) -> tuple[RunRecord, Path, str]:
    repo = tmp_path / "run-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "feature", str(repo)], check=True)
    _git(repo, "config", "user.name", "Lifecycle Tests")
    _git(repo, "config", "user.email", "lifecycle@example.test")
    plan_dir = repo / ".superpowers" / "sdd" / "plan"
    plan_dir.mkdir(parents=True)
    plan = plan_dir / "plan.md"
    plan.write_text("# Plan\n\n## Task 5\nImplement the run.\n", encoding="utf-8")
    _git(repo, "add", "--", str(plan.relative_to(repo)))
    _git(repo, "commit", "-qm", "plan")
    head = _git(repo, "rev-parse", "HEAD")
    branch = _git(repo, "branch", "--show-current")
    brief = plan_dir / "task-5-brief.md"
    brief.write_text("## Task 5\nImplement the run.\n", encoding="utf-8")
    report = repo / "report.md"
    baseline = workspace_fingerprint(repo)
    contract = RunContract(
        schema_version=1,
        run_id="run-5",
        task=TaskContract(
            id=5,
            heading="Task 5",
            brief_path=brief,
            brief_sha256=hashlib.sha256(brief.read_bytes()).hexdigest(),
            report_path=report,
        ),
        plan=PlanProvenance(
            source_path=plan,
            source_repository=repo,
            source_branch=branch,
            source_head=head,
            sha256=hashlib.sha256(plan.read_bytes()).hexdigest(),
        ),
        workspace=WorkspaceContract(
            repo_root=repo,
            base_head=head,
            branch=branch,
            baseline_status=baseline,
        ),
        scope=ScopeContract(allowed_paths=("src/", "report.md"), denied_paths=()),
        execution=ExecutionPolicy(
            backend="cmdc-local",
            model="deepseek/deepseek-v4-flash",
            max_turns=5,
            wall_timeout_seconds=60,
            stall_timeout_seconds=30,
            progress_deadline_turns=1,
            max_resumes=max_resumes,
            no_skills=True,
            yolo=True,
        ),
        success=SuccessPolicy(
            require_commit=True,
            require_report=True,
            require_test_evidence=True,
        ),
        review=ReviewPolicy(auto_fix_rounds=0),
    )
    run_dir = repo / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id
    return RunRecord.create(run_dir, contract), repo, head


@pytest.mark.parametrize(
    ("require_commit", "expected_instruction"),
    (
        (
            True,
            "A task commit based on the Run base HEAD is required before reporting.",
        ),
        (
            False,
            "This Run does not require a task commit; do not create one solely to satisfy the Run.",
        ),
    ),
)
def test_contract_prompt_states_the_commit_policy(
    tmp_path: Path,
    require_commit: bool,
    expected_instruction: str,
) -> None:
    record, _, _ = _run_fixture(tmp_path)
    contract = replace(
        record.contract,
        success=SuccessPolicy(
            require_commit=require_commit,
            require_report=True,
            require_test_evidence=True,
        ),
    )

    prompt = _render_contract_prompt(contract)

    assert expected_instruction in prompt


def test_windows_contract_prompt_declares_cmd_shell_and_powershell_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record, _, _ = _run_fixture(tmp_path)
    monkeypatch.setattr(lifecycle_module.sys, "platform", "win32")

    prompt = _render_contract_prompt(record.contract)

    assert "shell_command executes through cmd.exe" in prompt
    assert "PowerShell" in prompt
    assert "powershell -NoProfile -Command" in prompt


def _process(
    *,
    failure: ProcessFailure | None = None,
    cleanup_verified: bool = True,
    drain_verified: bool = True,
    returncode: int = 0,
    status: ProcessStatus = ProcessStatus.EXITED,
) -> ProcessOutcome:
    return ProcessOutcome(
        pid=123,
        returncode=returncode,
        stdout="",
        stderr="",
        status=status,
        containment="test",
        cleanup_verified=cleanup_verified,
        drain_verified=drain_verified,
        primary_failure=failure,
        secondary_failures=(),
    )


@dataclass
class _FakeCmdc:
    outcome: object

    def __post_init__(self) -> None:
        self.requests: list[object] = []
        self.resume_calls: list[tuple[str, object]] = []
        self.resume_outcome: object | None = None
        self.resume_callback = None

    def resolve_launcher(self) -> Path:
        return Path("cmdc")

    def smoke_test(self, *_args: object, **_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(
            mod_hook_verified=True,
            smoke=SimpleNamespace(
                session_id="session-123",
                process=SimpleNamespace(
                    status="EXITED",
                    returncode=0,
                    primary_failure=None,
                    secondary_failures=(),
                    cleanup_verified=True,
                    drain_verified=True,
                ),
            ),
        )

    def start(self, request: object) -> object:
        self.requests.append(request)
        return self.outcome

    def resume(self, session_id: str, request: object) -> object:
        self.resume_calls.append((session_id, request))
        if self.resume_callback is not None:
            return self.resume_callback(session_id, request)
        return self.resume_outcome if self.resume_outcome is not None else self.outcome


def _event(
    command: str | None,
    stdout: str = "",
    *,
    session_id: str | None = None,
    exit_code: int | None = 0,
    event_type: str = "tool_result",
    tool: str | None = "shell_command",
    turn: int = 1,
    raw: dict[str, object] | None = None,
) -> CmdcEvent:
    return CmdcEvent(
        type=event_type,
        session_id=session_id,
        turn_number=turn,
        tool=tool,
        command=command,
        exit_code=exit_code,
        stdout=stdout,
        stderr="raw stderr",
        raw=raw or {},
    )


def _nested_tool_completed_events(
    *,
    tool_name: str,
    command: str | None,
    result: object,
    call_id: str = "call-nested-test",
) -> tuple[CmdcEvent, ...]:
    input_value: dict[str, object] = {}
    if command is not None:
        input_value["command"] = command
    return (
        CmdcEvent(
            type="message_update",
            turn_number=1,
            raw={
                "event": {
                    "type": "message_update",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": call_id,
                            "name": tool_name,
                            "input": input_value,
                        }
                    ],
                }
            },
        ),
        CmdcEvent(
            type="tool_queued",
            turn_number=1,
            raw={
                "event": {
                    "type": "tool_queued",
                    "toolCallId": call_id,
                    "toolName": tool_name,
                    "input": input_value,
                }
            },
        ),
        CmdcEvent(
            type="tool_completed",
            turn_number=1,
            raw={
                "event": {
                    "type": "tool_completed",
                    "toolCallId": call_id,
                    "toolName": tool_name,
                    "result": result,
                }
            },
        ),
    )


def test_execution_lifecycle_exposes_the_canonical_interface() -> None:
    lifecycle = ExecutionLifecycle(object(), object())

    assert callable(lifecycle.start)
    assert callable(lifecycle.resume)


def test_preflight_uses_the_dedicated_mod_hook_probe(tmp_path: Path) -> None:
    record, repo, _ = _run_fixture(tmp_path)

    class PreflightCmdc:
        def __init__(self) -> None:
            self.smoke_mod_path: Path | None = None

        def resolve_launcher(self) -> Path:
            return Path("cmdc")

        def smoke_test(
            self,
            _cwd: Path,
            *,
            require_mod_hook: bool,
            mod_path: Path,
        ) -> SimpleNamespace:
            assert require_mod_hook is True
            self.smoke_mod_path = mod_path
            return SimpleNamespace(
                mod_hook_verified=True,
                smoke=SimpleNamespace(
                    session_id="session-123",
                    process=SimpleNamespace(
                        status="EXITED",
                        returncode=0,
                        primary_failure=None,
                        secondary_failures=(),
                        cleanup_verified=True,
                        drain_verified=True,
                    ),
                ),
            )

    cmdc = PreflightCmdc()

    ExecutionLifecycle(record, cmdc)._preflight_cmdc(repo)

    assert cmdc.smoke_mod_path == (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "sdd_cmdc_opencode"
        / "_mod_probe.ts"
    )


def test_preflight_rejects_hook_proof_without_clean_smoke_evidence(
    tmp_path: Path,
) -> None:
    record, repo, _ = _run_fixture(tmp_path)

    class UncleanPreflightCmdc:
        def resolve_launcher(self) -> Path:
            return Path("cmdc")

        def smoke_test(
            self,
            _cwd: Path,
            *,
            require_mod_hook: bool,
            mod_path: Path,
        ) -> SimpleNamespace:
            assert require_mod_hook is True
            assert mod_path.is_file()
            return SimpleNamespace(
                mod_hook_verified=True,
                smoke=SimpleNamespace(
                    session_id="session-123",
                    process=SimpleNamespace(
                        status="WALL_TIMEOUT",
                        returncode=None,
                        primary_failure=None,
                        secondary_failures=(),
                        cleanup_verified=False,
                        drain_verified=False,
                    ),
                ),
            )

    with pytest.raises(LifecycleError) as error:
        ExecutionLifecycle(record, UncleanPreflightCmdc())._preflight_cmdc(repo)

    assert getattr(error.value, "code", None) == "SMOKE_FAILED"


def test_preflight_rejects_backend_without_smoke_probe(tmp_path: Path) -> None:
    record, repo, _ = _run_fixture(tmp_path)

    class NoSmokeCmdc:
        def resolve_launcher(self) -> Path:
            return Path("cmdc")

    with pytest.raises(LifecycleError) as error:
        ExecutionLifecycle(record, NoSmokeCmdc())._preflight_cmdc(repo)

    assert getattr(error.value, "code", None) == "MOD_HOOK_UNVERIFIED"


def test_invalid_state_transition_is_fail_closed() -> None:
    lifecycle = ExecutionLifecycle(object(), object())

    with pytest.raises(LifecycleError, match="invalid lifecycle transition"):
        lifecycle._transition("RUNNING")  # type: ignore[attr-defined]


def test_start_reaches_complete_only_after_transaction_evidence(tmp_path: Path) -> None:
    record, repo, base_head = _run_fixture(tmp_path)
    (repo / "src").mkdir()

    def start(_request: object) -> CmdcOutcome:
        (repo / "src" / "implemented.py").write_text("VALUE = 1\n", encoding="utf-8")
        (repo / "report.md").write_text("STATUS: DONE\n", encoding="utf-8")
        _git(repo, "add", "--", "src/implemented.py", "report.md")
        _git(repo, "commit", "-qm", "implement task")
        return CmdcOutcome(
            process=_process(),
            subtype="success",
            stop_reason="completed",
            session_id="session-123",
            final_text="done",
            events=(_event("pytest tests -q", "1 passed"),),
        )

    cmdc = _FakeCmdc(None)
    cmdc.start = start  # type: ignore[method-assign]

    result = ExecutionLifecycle(record, cmdc).start()

    assert result.status is RunStatus.COMPLETE
    assert result.primary_blocker is None
    assert result.base_head == base_head
    assert result.final_head != base_head
    assert result.scope_valid is True
    assert result.report_valid is True
    assert result.test_evidence_valid is True
    assert record.read_result() == result
    assert (record.run_dir / "events.jsonl").read_text(encoding="utf-8").strip()
    assert (record.run_dir / "checkpoints.jsonl").read_text(encoding="utf-8").strip()


def test_lifecycle_wires_live_event_sink_before_cmdc_finishes(tmp_path: Path) -> None:
    record, _, _ = _run_fixture(tmp_path)
    event = _event("git status --short", turn=1)

    class LiveEventCmdc(_FakeCmdc):
        def start(self, request: object) -> object:
            self.requests.append(request)
            request.event_sink(event)  # type: ignore[attr-defined]
            return self.outcome

    outcome = CmdcOutcome(
        process=_process(),
        subtype="success",
        stop_reason="completed",
        session_id="session-123",
        final_text="done",
        events=(),
    )

    result = ExecutionLifecycle(record, LiveEventCmdc(outcome)).start()

    assert result.status is RunStatus.BLOCKED
    assert [
        item["command"]
        for item in record.read_events()
        if item["type"] == "tool_result"
    ] == ["git status --short"]


def test_lifecycle_persists_live_event_when_cmdc_is_interrupted(tmp_path: Path) -> None:
    record, _, _ = _run_fixture(tmp_path, max_resumes=1)
    event = _event("write_file", session_id="session-123", turn=1)

    class InterruptingCmdc(_FakeCmdc):
        def start(self, request: object) -> object:
            self.requests.append(request)
            request.event_sink(event)  # type: ignore[attr-defined]
            raise KeyboardInterrupt("simulated worker interruption")

    result = ExecutionLifecycle(record, InterruptingCmdc(None)).start()

    assert result.status is RunStatus.BLOCKED
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "INTERRUPTED"
    assert result.session_id == "session-123"
    assert result.cleanup_verified is False
    assert record.read_result() == result
    assert [
        item["command"]
        for item in record.read_events()
        if item["type"] == "tool_result"
    ] == ["write_file"]
    session_checkpoints = [
        item for item in record.read_checkpoints() if item.get("kind") == "session"
    ]
    assert session_checkpoints[-1]["session_id"] == "session-123"
    assert session_checkpoints[-1]["state"] == "INTERRUPTED"

    resume_cmdc = InterruptingCmdc(None)
    interrupted = ExecutionLifecycle(record, resume_cmdc)
    resume_cmdc.resume_outcome = CmdcOutcome(
        process=_process(),
        subtype="success",
        stop_reason="completed",
        session_id="session-123",
        final_text="resume attempted",
        events=(),
    )
    resumed = interrupted.resume()

    assert resumed.primary_blocker is not None
    assert resumed.primary_blocker.code == "RESUME_INVARIANT_FAILED"
    assert resume_cmdc.resume_calls == []


def test_lifecycle_persists_result_when_live_event_persistence_is_interrupted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record, _, _ = _run_fixture(tmp_path)
    event = _event("write_file", session_id="session-123", turn=1)

    def interrupted_append(*_args: object, **_kwargs: object) -> tuple[int, ...]:
        raise KeyboardInterrupt("simulated event persistence interruption")

    monkeypatch.setattr(
        "sdd_cmdc_opencode.execution_lifecycle.append_event_records",
        interrupted_append,
    )

    class InterruptingPersistenceCmdc(_FakeCmdc):
        def start(self, request: object) -> object:
            self.requests.append(request)
            request.event_sink(event)  # type: ignore[attr-defined]
            return self.outcome

    result = ExecutionLifecycle(record, InterruptingPersistenceCmdc(None)).start()

    assert result.status is RunStatus.BLOCKED
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "INTERRUPTED"
    assert result.session_id == "session-123"
    assert result.cleanup_verified is False
    assert record.read_result() == result
    assert record.read_checkpoints()


def test_session_checkpoint_persistence_failure_remains_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record, _, _ = _run_fixture(tmp_path, max_resumes=1)

    original_append_checkpoint = record.append_checkpoint

    def fail_session_checkpoint(value: dict[str, object]) -> int:
        if value.get("kind") == "session":
            raise OSError("session checkpoint unavailable")
        return original_append_checkpoint(value)

    monkeypatch.setattr(record, "append_checkpoint", fail_session_checkpoint)

    class InterruptingCmdc(_FakeCmdc):
        def start(self, request: object) -> object:
            self.requests.append(request)
            request.event_sink(_event("write_file", session_id="session-123"))  # type: ignore[attr-defined]
            raise KeyboardInterrupt("simulated worker interruption")

    result = ExecutionLifecycle(record, InterruptingCmdc(None)).start()

    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "INTERRUPTED"
    codes = [item.code for item in result.secondary_blockers]
    assert "CHECKPOINT_PERSISTENCE_FAILED" in codes
    assert "SESSION_CHECKPOINT_UNVERIFIED" in codes
    assert result.session_id == "session-123"


def test_lifecycle_recovers_terminal_session_after_verified_callback_interrupt(
    tmp_path: Path,
) -> None:
    record, _, _ = _run_fixture(tmp_path, max_resumes=1)
    event = _event("write_file", turn=1)
    process = ProcessOutcome(
        pid=123,
        returncode=-2,
        stdout=(
            '{"type":"result","subtype":"error",'
            '"stopReason":"interrupted","sessionId":"session-123",'
            '"result":""}\n'
        ),
        stderr="",
        status=ProcessStatus.INTERRUPTED,
        containment="test",
        cleanup_verified=True,
        drain_verified=True,
        primary_failure=ProcessFailure(
            "INTERRUPTED", "callback", "callback interrupted"
        ),
        secondary_failures=(),
    )
    callback_error = ProcessCallbackError(
        KeyboardInterrupt("callback interrupted"), process
    )

    class InterruptingSupervisorCmdc(_FakeCmdc):
        def start(self, request: object) -> object:
            self.requests.append(request)
            request.event_sink(event)  # type: ignore[attr-defined]
            raise callback_error

    cmdc = InterruptingSupervisorCmdc(None)
    result = ExecutionLifecycle(record, cmdc).start()

    assert result.status is RunStatus.BLOCKED
    assert result.session_id == "session-123"
    assert result.cleanup_verified is True
    assert any(
        checkpoint.get("session_id") == "session-123"
        for checkpoint in record.read_checkpoints()
    )

    cmdc.resume_outcome = CmdcOutcome(
        process=_process(),
        subtype="success",
        stop_reason="completed",
        session_id="session-123",
        final_text="resume attempted",
        events=(),
    )
    resumed = ExecutionLifecycle(record, cmdc).resume()

    assert resumed.primary_blocker is not None
    assert resumed.primary_blocker.code == "INTERRUPTED"
    assert [session for session, _ in cmdc.resume_calls] == ["session-123"]


def test_post_contract_workspace_change_fails_closed_before_launcher(
    tmp_path: Path,
) -> None:
    """An unauthorized change introduced after Contract creation must fail
    closed with BASELINE_FINGERPRINT_MISMATCH before any launcher starts,
    while the lifecycle-owned run artifacts alone never trigger it."""
    record, repo, _ = _run_fixture(tmp_path)
    cmdc = _FakeCmdc(None)
    (repo / "tracked.py").write_text("VALUE = 2\n", encoding="utf-8")

    result = ExecutionLifecycle(record, cmdc).start()

    assert result.status is RunStatus.BLOCKED
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "BASELINE_FINGERPRINT_MISMATCH"
    assert cmdc.requests == []


@pytest.mark.parametrize(
    ("failure", "cleanup_verified", "expected_primary", "expected_status"),
    (
        (
            ProcessFailure("CMD_CODE_PROTOCOL_ERROR", "protocol", "bad result"),
            False,
            "CMD_CODE_PROTOCOL_ERROR",
            RunStatus.BLOCKED,
        ),
        (None, False, "CLEANUP_UNVERIFIED", RunStatus.BLOCKED),
    ),
)
def test_first_failure_remains_primary_and_cleanup_is_secondary(
    tmp_path: Path,
    failure: ProcessFailure | None,
    cleanup_verified: bool,
    expected_primary: str,
    expected_status: RunStatus,
) -> None:
    record, repo, _ = _run_fixture(tmp_path)
    outcome = CmdcOutcome(
        process=_process(failure=failure, cleanup_verified=cleanup_verified),
        subtype="success",
        stop_reason="completed",
        session_id="session-123",
        final_text="",
        events=(),
    )

    result = ExecutionLifecycle(record, _FakeCmdc(outcome)).start()

    assert result.status is expected_status
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == expected_primary
    if failure is not None:
        assert [item.code for item in result.secondary_blockers] == ["CLEANUP_UNVERIFIED"]
    assert result.final_head == _git(repo, "rev-parse", "HEAD")


def test_success_without_report_or_tests_is_a_blocked_result(tmp_path: Path) -> None:
    record, _, _ = _run_fixture(tmp_path)
    outcome = CmdcOutcome(
        process=_process(),
        subtype="success",
        stop_reason="completed",
        session_id="session-123",
        final_text="",
        events=(),
    )

    result = ExecutionLifecycle(record, _FakeCmdc(outcome)).start()

    assert result.status is RunStatus.BLOCKED
    assert result.primary_blocker is not None
    assert result.primary_blocker.code in {"REPORT_INVALID", "TEST_EVIDENCE_INVALID"}
    assert record.read_result() == result


def test_end_turn_is_not_misclassified_as_worker_turn_limit(tmp_path: Path) -> None:
    record, _, _ = _run_fixture(tmp_path)
    outcome = CmdcOutcome(
        process=_process(),
        subtype="success",
        stop_reason="end_turn",
        session_id="session-123",
        final_text="done",
        events=(),
    )

    result = ExecutionLifecycle(record, _FakeCmdc(outcome)).start()

    codes = [
        blocker.code
        for blocker in (result.primary_blocker, *result.secondary_blockers)
        if blocker is not None
    ]
    assert "WORKER_TURN_LIMIT" not in codes


def _successful_recovery(repo: Path) -> CmdcOutcome:
    (repo / "src").mkdir(exist_ok=True)
    (repo / "src" / "recovered.py").write_text("VALUE = 2\n", encoding="utf-8")
    (repo / "report.md").write_text("STATUS: RECOVERED\n", encoding="utf-8")
    _git(repo, "add", "--", "src/recovered.py", "report.md")
    _git(repo, "commit", "-qm", "recovery")
    return CmdcOutcome(
        process=_process(),
        subtype="success",
        stop_reason="completed",
        session_id="session-123",
        final_text="recovered",
        events=(_event("pytest tests -q", "2 passed", turn=1),),
    )


def test_explicit_resume_uses_the_same_session_after_stall(tmp_path: Path) -> None:
    record, repo, _ = _run_fixture(tmp_path, max_resumes=1)
    stalled = CmdcOutcome(
        process=_process(status=ProcessStatus.STALLED),
        subtype="partial",
        stop_reason="stalled",
        session_id="session-123",
        final_text="partial",
        events=(_event("git status --short", turn=1),),
    )
    cmdc = _FakeCmdc(stalled)
    cmdc.resume_callback = lambda _session, _request: _successful_recovery(repo)

    first = ExecutionLifecycle(record, cmdc).start()
    recovered = ExecutionLifecycle(record, cmdc).resume()

    assert first.status is RunStatus.INCOMPLETE
    assert first.primary_blocker is not None
    assert first.primary_blocker.code == "STALLED"
    assert recovered.status is RunStatus.COMPLETE
    assert [session for session, _ in cmdc.resume_calls] == ["session-123"]
    request = cmdc.resume_calls[0][1]
    assert request.mod_path is not None
    assert request.scope_env["SDD_CMDC_SCOPE_CONTRACT"].endswith("scope-contract.json")
    assert request.scope_env["SDD_CMDC_SCOPE_RUN_OWNER"] == str(record.run_dir.resolve())
    assert "--continue" not in request.prompt
    assert len((record.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()) >= 3


def test_resume_rejects_result_session_mismatch_before_launcher(tmp_path: Path) -> None:
    record, _, _ = _run_fixture(tmp_path, max_resumes=1)
    stalled = CmdcOutcome(
        process=_process(status=ProcessStatus.STALLED),
        subtype="partial",
        stop_reason="stalled",
        session_id="session-123",
        final_text="partial",
        events=(_event("git status --short", turn=1),),
    )
    cmdc = _FakeCmdc(stalled)
    ExecutionLifecycle(record, cmdc).start()

    stored = record.read_result()
    assert stored is not None
    record.write_result(replace(stored, session_id="session-other"))

    result = ExecutionLifecycle(record, cmdc).resume()

    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "RESUME_INVARIANT_FAILED"
    assert cmdc.resume_calls == []


def test_resume_fails_before_launcher_without_an_owned_checkpoint(tmp_path: Path) -> None:
    record, _, _ = _run_fixture(tmp_path, max_resumes=1)
    cmdc = _FakeCmdc(None)

    result = ExecutionLifecycle(record, cmdc).resume()

    assert result.status is RunStatus.BLOCKED
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "RESUME_INVARIANT_FAILED"
    assert cmdc.resume_calls == []


def test_different_recovery_session_is_a_protocol_failure(tmp_path: Path) -> None:
    record, repo, _ = _run_fixture(tmp_path, max_resumes=1)
    stalled = CmdcOutcome(
        process=_process(status=ProcessStatus.STALLED),
        subtype="partial",
        stop_reason="stalled",
        session_id="session-123",
        final_text="partial",
        events=(_event("git status --short", turn=1),),
    )
    cmdc = _FakeCmdc(stalled)
    def wrong_session(_session: str, _request: object) -> CmdcOutcome:
        outcome = _successful_recovery(repo)
        return CmdcOutcome(
            process=outcome.process,
            subtype="success",
            stop_reason="completed",
            session_id="session-other",
            final_text=outcome.final_text,
            events=outcome.events,
        )

    cmdc.resume_callback = wrong_session

    ExecutionLifecycle(record, cmdc).start()
    result = ExecutionLifecycle(record, cmdc).resume()

    assert result.status is RunStatus.BLOCKED
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "STALLED"
    assert "CMD_CODE_PROTOCOL_ERROR" in [item.code for item in result.secondary_blockers]


def test_worker_turn_limit_automatically_recovers_within_policy(tmp_path: Path) -> None:
    record, repo, _ = _run_fixture(tmp_path, max_resumes=1)
    turn_limit = CmdcOutcome(
        process=_process(),
        subtype="partial",
        stop_reason="max turns reached",
        session_id="session-123",
        final_text="turn limit",
        events=(_event("git status --short", turn=1),),
    )
    cmdc = _FakeCmdc(turn_limit)
    cmdc.resume_callback = lambda _session, _request: _successful_recovery(repo)

    result = ExecutionLifecycle(record, cmdc).start()

    assert result.status is RunStatus.COMPLETE
    assert [session for session, _ in cmdc.resume_calls] == ["session-123"]
    assert result.recoveries[0].same_session is True


def test_worker_turn_limit_exhaustion_keeps_primary_and_blocks_recovery(
    tmp_path: Path,
) -> None:
    record, _, _ = _run_fixture(tmp_path, max_resumes=0)
    turn_limit = CmdcOutcome(
        process=_process(),
        subtype="partial",
        stop_reason="max turns reached",
        session_id="session-123",
        final_text="turn limit",
        events=(_event("git status --short", turn=1),),
    )
    cmdc = _FakeCmdc(turn_limit)

    result = ExecutionLifecycle(record, cmdc).start()

    assert result.status is RunStatus.BLOCKED
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "WORKER_TURN_LIMIT"
    assert "RECOVERY_EXHAUSTED" in [item.code for item in result.secondary_blockers]
    assert cmdc.resume_calls == []


def test_resume_rejects_unknown_workspace_change_before_launcher(tmp_path: Path) -> None:
    record, repo, _ = _run_fixture(tmp_path, max_resumes=1)
    stalled = CmdcOutcome(
        process=_process(status=ProcessStatus.STALLED),
        subtype="partial",
        stop_reason="stalled",
        session_id="session-123",
        final_text="partial",
        events=(_event("git status --short", turn=1),),
    )
    cmdc = _FakeCmdc(stalled)
    ExecutionLifecycle(record, cmdc).start()
    (repo / "outside-recovery.txt").write_text("untrusted\n", encoding="utf-8")

    result = ExecutionLifecycle(record, cmdc).resume()

    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "RESUME_INVARIANT_FAILED"
    assert cmdc.resume_calls == []


def test_evidence_requires_a_successful_recognized_test_event() -> None:
    cases = (
        ("pytest tests/unit -q", "246 passed in 23.67s", 246),
        ("python -m pytest tests/test_a.py -q; Write-Output done", "12 passed", 12),
        ("npm test", "31 passed, 0 failed", 31),
        ("dotnet test", "Failed: 0, Passed: 18", 18),
    )

    for command, stdout, passed in cases:
        evidence = normalize_test_evidence((_event(command, stdout),))

        assert len(evidence) == 1
        assert evidence[0].command == command
        assert evidence[0].passed == passed
        assert evidence[0].failed == 0
        assert evidence[0].summary == stdout
        assert evidence[0].event_sequence == 1


def test_nested_tool_completed_result_reconstructs_shell_test_evidence() -> None:
    command = (
        "set PYTHONHOME=& uv run --offline --no-project --with pytest "
        "python -m pytest -q tests/test_a.py"
    )
    events = _nested_tool_completed_events(
        tool_name="shell_command",
        command=command,
        result=[{"type": "text", "text": "17 passed in 6.21s"}],
    )

    evidence = normalize_test_evidence(events)

    assert len(evidence) == 1
    assert evidence[0].command == command
    assert evidence[0].exit_code == 0
    assert evidence[0].passed == 17
    assert evidence[0].failed == 0
    assert evidence[0].event_sequence == 3
    assessment = evaluate_progress(events, max_turns=10)
    assert assessment.first_progress is not None
    assert assessment.first_progress.kind == "recognized_validation"
    assert events[2].command is None
    assert events[2].raw["event"]["result"] == [
        {"type": "text", "text": "17 passed in 6.21s"}
    ]


@pytest.mark.parametrize(
    ("tool_name", "command", "result"),
    (
        (
            "shell_command",
            "python -m pytest -q tests/test_a.py",
            [{"type": "text", "text": "Exit code: 2\\n17 passed"}],
        ),
        (
            "read_file",
            "python -m pytest -q tests/test_a.py",
            [{"type": "text", "text": "17 passed"}],
        ),
        (
            "write_file",
            "python -m pytest -q tests/test_a.py",
            [{"type": "text", "text": "17 passed"}],
        ),
        (
            "shell_command",
            "python -m pytest -q tests/test_a.py",
            {"type": "text", "text": "17 passed"},
        ),
        (
            "shell_command",
            "python -m pytest -q tests/test_a.py",
            [{"type": "image", "data": "not-test-output"}],
        ),
    ),
)
def test_nested_tool_completed_rejects_failures_reads_writes_and_malformed_results(
    tool_name: str,
    command: str,
    result: object,
) -> None:
    events = _nested_tool_completed_events(
        tool_name=tool_name,
        command=command,
        result=result,
    )

    assert normalize_test_evidence(events) == ()


def test_evidence_rejects_failures_and_assistant_prose() -> None:
    events = (
        _event("pytest", "245 passed, 1 failed"),
        _event(None, "all tests pass", event_type="assistant_message", tool=None),
    )

    assert normalize_test_evidence(events) == ()


def test_evidence_preserves_raw_streams_and_shell_separators() -> None:
    command = "python -m pytest tests/test_a.py -q; Write-Output done"
    event = _event(command, "12 passed")

    evidence = normalize_test_evidence((event,))

    assert evidence[0].command == command
    assert evidence[0].summary == "12 passed"
    assert event.stdout == "12 passed"
    assert event.stderr == "raw stderr"


def test_default_progress_deadline_is_bounded_and_deterministic() -> None:
    assert [default_progress_deadline(turns) for turns in (1, 5, 6, 46, 100)] == [1, 1, 2, 10, 10]


def test_configured_contract_deadline_controls_the_progress_decision() -> None:
    """``evaluate_progress`` must honor the immutable Contract's
    ``progress_deadline_turns``: with the configured deadline, exploration
    past the derived default still blocks, and the deadline turn is the
    configured value."""
    events = (
        _event("Get-ChildItem", turn=1),
        _event("git status --short", turn=2),
        _event("git diff --stat", turn=3),
    )

    derived = evaluate_progress(events, max_turns=100)
    assert derived.deadline_turn == default_progress_deadline(100)
    assert derived.blocker is None

    configured = evaluate_progress(
        events, max_turns=100, progress_deadline_turns=3
    )
    assert configured.deadline_turn == 3
    assert configured.blocker == NO_IMPLEMENTATION_PROGRESS

    relaxed = evaluate_progress(events, max_turns=100, progress_deadline_turns=10)
    assert relaxed.deadline_turn == 10
    assert relaxed.blocker is None


def test_configured_progress_deadline_is_contract_immutable_and_validated() -> None:
    with pytest.raises(ValueError, match="between one and max_turns"):
        evaluate_progress((), max_turns=5, progress_deadline_turns=0)
    with pytest.raises(ValueError, match="between one and max_turns"):
        evaluate_progress((), max_turns=5, progress_deadline_turns=6)
    with pytest.raises(ValueError, match="positive integer"):
        evaluate_progress((), max_turns=5, progress_deadline_turns=True)  # type: ignore[arg-type]


def test_exploration_only_events_reach_the_progress_deadline() -> None:
    events = (
        _event("Get-ChildItem", turn=1),
        _event("git status --short", turn=2),
    )

    assessment = evaluate_progress(events, max_turns=10)

    assert assessment.first_progress is None
    assert assessment.blocker == NO_IMPLEMENTATION_PROGRESS
    assert assessment.deadline_turn == 2


def test_permitted_write_is_the_first_progress_signal() -> None:
    event = _event(
        None,
        event_type="tool_result",
        tool="write_file",
        turn=2,
        raw={"path": "src/run.py", "success": True},
    )

    assessment = evaluate_progress((event,), max_turns=10)

    assert assessment.first_progress is not None
    assert assessment.first_progress.kind == "permitted_write"
    assert assessment.blocker is None


def test_allowed_workspace_delta_and_task_commit_count_as_progress() -> None:
    baseline = {"head": "a" * 40, "paths": {}}
    changed = {
        "head": "b" * 40,
        "paths": {"src/run.py": {"kind": "tracked", "sha256": "1"}},
    }

    assessment = evaluate_progress(
        (),
        max_turns=10,
        baseline_fingerprint=baseline,
        current_fingerprint=changed,
        base_head="a" * 40,
        current_head="b" * 40,
    )

    assert assessment.first_progress is not None
    assert assessment.first_progress.kind == "workspace_delta"


def test_recognized_test_build_and_lint_events_count_but_status_does_not() -> None:
    events = (
        _event("git status --short", turn=1),
        _event("ruff check .", "1 error", exit_code=1, turn=2),
    )

    assessment = evaluate_progress(events, max_turns=10)

    assert assessment.first_progress is not None
    assert assessment.first_progress.kind == "recognized_validation"


def test_arbitrary_shell_output_and_directory_listing_do_not_count() -> None:
    events = (
        _event("Get-ChildItem", "src", turn=1),
        _event("git diff --stat", "file changed", turn=2),
    )

    assessment = evaluate_progress(events, max_turns=10)

    assert assessment.first_progress is None
    assert assessment.blocker == NO_IMPLEMENTATION_PROGRESS


class _CheckpointRecord:
    def __init__(self) -> None:
        self.values: list[dict[str, object]] = []

    def append_checkpoint(self, value: dict[str, object]) -> int:
        self.values.append(value)
        return len(self.values)


def test_first_progress_or_deadline_is_persisted_as_a_checkpoint() -> None:
    record = _CheckpointRecord()
    assessment = evaluate_progress((_event("ruff check .", turn=2),), max_turns=10)

    sequence = persist_progress_checkpoint(record, assessment)

    assert sequence == 1
    assert record.values == [
        {
            "kind": "progress",
            "state": "PROGRESS",
            "progress_kind": "recognized_validation",
            "event_sequence": 1,
            "turn": 2,
            "detail": "ruff check .",
        }
    ]


def test_no_progress_deadline_is_persisted_with_its_primary_blocker() -> None:
    record = _CheckpointRecord()
    assessment = evaluate_progress(
        (_event("git status --short", turn=1), _event("Get-ChildItem", turn=2)),
        max_turns=10,
    )

    persist_progress_checkpoint(record, assessment)

    assert record.values[0]["kind"] == "progress_deadline"
    assert record.values[0]["blocker"] == NO_IMPLEMENTATION_PROGRESS
