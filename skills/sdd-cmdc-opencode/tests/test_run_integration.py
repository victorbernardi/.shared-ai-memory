from __future__ import annotations

from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

from sdd_cmdc_opencode.cmdc_local import CmdcLocal
from sdd_cmdc_opencode.execution_lifecycle import ExecutionLifecycle
from sdd_cmdc_opencode.run_record import (
    ExecutionPolicy,
    PlanProvenance,
    ReviewPolicy,
    RunContract,
    RunRecord,
    RunResult,
    RunStatus,
    ScopeContract,
    SuccessPolicy,
    TaskContract,
    WorkspaceContract,
    workspace_fingerprint,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = REPO_ROOT / "skills" / "sdd-cmdc-opencode"
ADAPTER_PATH = SKILL / "scripts" / "cmdc-implementer.py"


FAKE_CMDC_SOURCE = r'''from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


SESSION_ID = "session-123"
MARKER = "SDD_CMDC_MOD_HOOK_OK"
HANDSHAKE = "SDD_CMDC_MOD_HOOK_HANDSHAKE"


def value(argv: list[str], flag: str) -> str | None:
    try:
        index = argv.index(flag)
    except ValueError:
        return None
    return argv[index + 1] if index + 1 < len(argv) else None


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def event(
    *,
    event_type: str,
    tool: str | None = None,
    command: str | None = None,
    stdout: str = "",
    exit_code: int | None = 0,
    turn: int = 1,
) -> None:
    emit(
        {
            "type": "event",
            "event": {
                "type": event_type,
                "sessionId": SESSION_ID,
                "turnNumber": turn,
                "tool": tool,
                "command": command,
                "stdout": stdout,
                "stderr": "",
                "exitCode": exit_code,
            },
        }
    )


def terminal(
    *,
    subtype: str = "success",
    stop_reason: str = "end_turn",
    result: str = "done",
) -> None:
    emit(
        {
            "type": "result",
            "subtype": subtype,
            "sessionId": SESSION_ID,
            "stopReason": stop_reason,
            "result": result,
        }
    )


def log_call(argv: list[str], cwd: Path, resumed: bool) -> None:
    log_path = os.environ.get("FAKE_CMDC_LOG")
    if not log_path:
        return
    entry = {
        "argv": argv,
        "cwd": str(cwd.resolve()),
        "resumed": resumed,
        "mod": value(argv, "--mod"),
        "scope_contract": os.environ.get("SDD_CMDC_SCOPE_CONTRACT"),
        "scope_helper": os.environ.get("SDD_CMDC_SCOPE_HELPER"),
        "scope_python": os.environ.get("SDD_CMDC_SCOPE_PYTHON"),
    }
    with Path(log_path).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def commit_allowed(cwd: Path, *paths: str) -> None:
    subprocess.run(
        ["git", "-c", "core.hooksPath=", "-C", str(cwd), "add", "--", *paths],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "core.hooksPath=",
            "-C",
            str(cwd),
            "commit",
            "-qm",
            "fake implementation",
        ],
        check=True,
    )


def main() -> int:
    argv = sys.argv[1:]
    cwd = Path.cwd()
    resumed = value(argv, "--resume") is not None
    log_call(argv, cwd, resumed)
    if value(argv, "--output-format") != "json":
        terminal(subtype="error", stop_reason="invalid_flags", result="missing json")
        return 2

    if value(argv, "--max-turns") == "2":
        if value(argv, "--mod"):
            emit(
                {
                    "type": "event",
                    "event": {
                        "type": "tool_hook_blocked",
                        "toolName": "shell_command",
                        "hookOutput": HANDSHAKE,
                    },
                }
            )
        terminal(result="smoke")
        return 0

    mode = os.environ.get("FAKE_CMDC_MODE", "happy")
    if value(argv, "--mod"):
        emit(
            {
                "type": "event",
                "event": {
                    "type": "tool_hook_blocked",
                    "toolName": "shell_command",
                    "hookOutput": HANDSHAKE,
                },
            }
        )

    if mode == "malformed":
        print("{not-json", flush=True)
        terminal()
        return 0

    if mode == "no_progress":
        event(
            event_type="assistant_message",
            tool=None,
            command=None,
            stdout="all tests pass",
            exit_code=None,
        )
        terminal()
        return 0

    if resumed and mode in {"happy", "turn_limit"}:
        (cwd / "src").mkdir(exist_ok=True)
        (cwd / "src" / "final.py").write_text("FINAL = True\n", encoding="utf-8")
        (cwd / "report.md").write_text(
            "# Implementer Report\n\n246 passed in 0.01s\n", encoding="utf-8"
        )
        commit_allowed(cwd, "src/partial.py", "src/final.py", "report.md")
        event(
            event_type="tool_result",
            tool="shell_command",
            command="python -m pytest tests -q",
            stdout="246 passed in 0.01s",
            turn=2,
        )
        terminal(result="recovered")
        return 0

    if mode in {"turn_limit", "happy", "unknown_before_recovery", "exhausted"}:
        (cwd / "src").mkdir(exist_ok=True)
        if mode == "unknown_before_recovery":
            (cwd / "rogue-before-recovery.txt").write_text("must remain\n", encoding="utf-8")
        else:
            (cwd / "src" / "partial.py").write_text("PARTIAL = True\n", encoding="utf-8")
        event(
            event_type="tool_result",
            tool="shell_command",
            command="git status --short",
            stdout="partial implementation",
            turn=1,
        )
        terminal(subtype="max_turns", stop_reason="max_turns", result="turn limit")
        return 0

    if mode == "direct_denied":
        (cwd / "direct-denied.txt").write_text("must remain\n", encoding="utf-8")
        event(
            event_type="tool_result",
            tool="write_file",
            command="write_file",
            stdout="denied path attempted",
        )
        terminal()
        return 0

    if mode == "indirect_shell":
        (cwd / "indirect-denied.txt").write_text("must remain\n", encoding="utf-8")
        event(
            event_type="tool_result",
            tool="shell_command",
            command="python -c write_outside_scope",
            stdout="shell completed",
        )
        terminal()
        return 0

    if mode == "report_without_commit":
        (cwd / "report.md").write_text("report without commit\n", encoding="utf-8")
        event(
            event_type="tool_result",
            tool="shell_command",
            command="python -m pytest tests -q",
            stdout="246 passed",
        )
        terminal()
        return 0

    if mode == "commit_without_report":
        (cwd / "src").mkdir(exist_ok=True)
        (cwd / "src" / "committed.py").write_text("COMMITTED = True\n", encoding="utf-8")
        commit_allowed(cwd, "src/committed.py")
        event(
            event_type="tool_result",
            tool="shell_command",
            command="python -m pytest tests -q",
            stdout="246 passed",
        )
        terminal()
        return 0

    if mode == "prose_without_test":
        (cwd / "src").mkdir(exist_ok=True)
        (cwd / "src" / "prose.py").write_text("PROSE = True\n", encoding="utf-8")
        (cwd / "report.md").write_text("all tests pass\n", encoding="utf-8")
        commit_allowed(cwd, "src/prose.py", "report.md")
        event(
            event_type="assistant_message",
            tool=None,
            command=None,
            stdout="all tests pass",
            exit_code=None,
        )
        terminal()
        return 0

    terminal()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "core.hooksPath=", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _adapter_module():
    spec = importlib.util.spec_from_file_location("cmdc_implementer_integration", ADAPTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_fixture(
    tmp_path: Path,
    *,
    mode: str,
    max_resumes: int = 1,
) -> tuple[RunRecord, Path, Path, Path, Path]:
    repo = tmp_path / "workspace unicode & dados"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "feature")
    _git(repo, "config", "user.name", "Integration Tests")
    _git(repo, "config", "user.email", "integration@example.invalid")

    plan_dir = repo / ".superpowers" / "sdd" / "integration-plan"
    plan_dir.mkdir(parents=True)
    plan = plan_dir / "plan.md"
    plan.write_text(
        "# Integration Plan\n\n## Task 1\nImplement the governed transaction.\n",
        encoding="utf-8",
    )
    _git(repo, "add", "--", str(plan.relative_to(repo)))
    _git(repo, "commit", "-qm", "plan")
    head = _git(repo, "rev-parse", "HEAD")
    branch = _git(repo, "branch", "--show-current")

    brief = plan_dir / "task-1-brief.md"
    brief.write_text("## Task 1\nImplement the governed transaction.\n", encoding="utf-8")
    baseline_path = repo / "pre-existing & unicode.txt"
    baseline_path.write_text("preserve me\n", encoding="utf-8")
    report = repo / "report.md"
    baseline = workspace_fingerprint(repo)

    contract = RunContract(
        schema_version=1,
        run_id="integration-run-1",
        task=TaskContract(
            id=1,
            heading="Task 1",
            brief_path=brief,
            brief_sha256=_sha256(brief),
            report_path=report,
        ),
        plan=PlanProvenance(
            source_path=plan,
            source_repository=repo,
            source_branch=branch,
            source_head=head,
            sha256=_sha256(plan),
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
            wall_timeout_seconds=30,
            stall_timeout_seconds=5,
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
    contract = RunContract.from_mapping(contract.to_mapping())
    run_dir = plan_dir / "runs" / contract.run_id
    record = RunRecord.create(run_dir, contract)
    launcher = tmp_path / "fake_cmdc.py"
    launcher.write_text(FAKE_CMDC_SOURCE, encoding="utf-8", newline="\n")
    log_path = tmp_path / "cmdc-argv.jsonl"
    # The caller owns these values; the fake launcher only observes inherited
    # environment and cannot widen the lifecycle's allowlisted scope env.
    return record, repo, launcher, log_path, baseline_path


def _run_cli_start(
    record: RunRecord,
    launcher: Path,
    log_path: Path,
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[int, RunResult, object]:
    monkeypatch.setenv("FAKE_CMDC_MODE", mode)
    monkeypatch.setenv("FAKE_CMDC_LOG", str(log_path))
    adapter = _adapter_module()
    exit_code = adapter.run_canonical_start(
        record.run_dir / "contract.json", cmd_bin=str(launcher)
    )
    result = record.read_result()
    assert result is not None
    return exit_code, result, adapter


def _run_unclean_start(
    record: RunRecord,
    launcher: Path,
    log_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> RunResult:
    monkeypatch.setenv("FAKE_CMDC_MODE", "cleanup")
    monkeypatch.setenv("FAKE_CMDC_LOG", str(log_path))
    real = CmdcLocal(str(launcher))

    class UncleanCmdc:
        def resolve_launcher(self):
            return real.resolve_launcher()

        def smoke_test(self, *args, **kwargs):
            return real.smoke_test(*args, **kwargs)

        def start(self, request):
            outcome = real.start(request)
            return replace(
                outcome,
                process=replace(outcome.process, cleanup_verified=False),
            )

        def resume(self, session_id, request):
            return real.resume(session_id, request)

    result = ExecutionLifecycle(record, UncleanCmdc()).start()
    persisted = record.read_result()
    assert persisted is not None
    return persisted


def _run_log(log_path: Path, repo: Path) -> list[dict[str, object]]:
    values = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [value for value in values if value["cwd"] == str(repo.resolve())]


def test_complete_run_transaction_uses_one_run_and_one_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    record, repo, launcher, log_path, baseline_path = _make_fixture(
        tmp_path, mode="happy"
    )
    contract_bytes = (record.run_dir / "contract.json").read_bytes()
    baseline_bytes = baseline_path.read_bytes()

    exit_code, result, adapter = _run_cli_start(
        record, launcher, log_path, "happy", monkeypatch
    )
    captured = capsys.readouterr().out
    assert exit_code == 0
    assert result.status is RunStatus.COMPLETE
    assert result.run_id == record.contract.run_id
    assert result.session_id == "session-123"
    assert result.primary_blocker is None
    assert result.recoveries and result.recoveries[0].same_session is True
    assert result.tests[-1].passed == 246
    assert result.tests[-1].command == "python -m pytest tests -q"
    assert (record.run_dir / "contract.json").read_bytes() == contract_bytes
    assert baseline_path.read_bytes() == baseline_bytes

    events = record.read_events()
    checkpoints = record.read_checkpoints()
    assert events and [item["sequence"] for item in events] == list(range(1, len(events) + 1))
    assert checkpoints and [item["sequence"] for item in checkpoints] == list(
        range(1, len(checkpoints) + 1)
    )
    assert checkpoints[0]["phase"] == "PREFLIGHT"
    assert any(item.get("kind") == "recovery" for item in checkpoints)
    session_ids = {
        item["session_id"]
        for item in checkpoints
        if isinstance(item.get("session_id"), str)
    }
    assert session_ids == {"session-123"}
    assert {item["run_id"] for item in (*events, *checkpoints)} == {
        record.contract.run_id
    }

    assert result.artifact_hashes["contract"] == record.contract_sha256
    assert result.artifact_hashes["report"] == _sha256(repo / "report.md")
    assert result.artifact_hashes["events"] == _sha256(record.run_dir / "events.jsonl")
    assert result.artifact_hashes["checkpoints"] == _sha256(
        record.run_dir / "checkpoints.jsonl"
    )
    assert "STATUS: COMPLETE" in captured
    assert "RUN_ID: integration-run-1" in captured
    assert "RESULT_FILE:" in captured
    assert "EVENTS_FILE:" in captured
    assert "CHECKPOINTS_FILE:" in captured

    calls = _run_log(log_path, repo)
    assert len(calls) == 2
    assert calls[0]["resumed"] is False
    assert calls[1]["resumed"] is True
    assert calls[1]["argv"][calls[1]["argv"].index("--resume") + 1] == "session-123"
    assert calls[0]["mod"] == calls[1]["mod"]
    assert calls[0]["scope_contract"] == calls[1]["scope_contract"]
    assert calls[0]["scope_helper"] == calls[1]["scope_helper"]
    assert calls[0]["scope_python"] == calls[1]["scope_python"]
    assert "--continue" not in calls[1]["argv"]

    rendered = adapter.render_run_result(result, record)
    assert rendered.startswith("STATUS: COMPLETE\n")
    assert rendered.count("RUN_ID:") == 1


@pytest.mark.parametrize(
    ("mode", "expected_primary", "expected_status"),
    (
        ("no_progress", "NO_IMPLEMENTATION_PROGRESS", RunStatus.BLOCKED),
        ("direct_denied", "SCOPE_VIOLATION", RunStatus.BLOCKED),
        ("indirect_shell", "SCOPE_VIOLATION", RunStatus.BLOCKED),
        ("report_without_commit", "COMMIT_REQUIREMENT_FAILED", RunStatus.BLOCKED),
        ("commit_without_report", "REPORT_INVALID", RunStatus.BLOCKED),
        ("prose_without_test", "TEST_EVIDENCE_INVALID", RunStatus.BLOCKED),
        ("malformed", "CMD_CODE_PROTOCOL_ERROR", RunStatus.BLOCKED),
        ("exhausted", "WORKER_TURN_LIMIT", RunStatus.BLOCKED),
    ),
)
def test_fail_closed_run_variants_preserve_evidence_without_review_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    expected_primary: str,
    expected_status: RunStatus,
) -> None:
    max_resumes = 0 if mode == "exhausted" else 1
    record, repo, launcher, log_path, _ = _make_fixture(
        tmp_path, mode=mode, max_resumes=max_resumes
    )

    exit_code, result, _ = _run_cli_start(
        record, launcher, log_path, mode, monkeypatch
    )

    assert exit_code == 1
    assert result.status is expected_status
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == expected_primary
    assert (record.run_dir / "result.json").is_file()
    assert not any(
        path.is_file() and "review" in path.name.casefold()
        for path in repo.rglob("*")
    )
    if mode in {"direct_denied", "indirect_shell"}:
        assert any(path.name.endswith("denied.txt") for path in repo.iterdir())
    if mode == "exhausted":
        assert "RECOVERY_EXHAUSTED" in [
            blocker.code for blocker in result.secondary_blockers
        ]


def test_unknown_workspace_change_blocks_automatic_recovery_before_launcher(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record, repo, launcher, log_path, _ = _make_fixture(
        tmp_path, mode="unknown_before_recovery"
    )

    exit_code, result, _ = _run_cli_start(
        record, launcher, log_path, "unknown_before_recovery", monkeypatch
    )

    assert exit_code == 1
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "RESUME_INVARIANT_FAILED"
    assert (repo / "rogue-before-recovery.txt").is_file()
    assert len(_run_log(log_path, repo)) == 1


def test_failed_cleanup_is_blocked_and_does_not_create_review_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record, repo, launcher, log_path, _ = _make_fixture(tmp_path, mode="cleanup")

    result = _run_unclean_start(record, launcher, log_path, monkeypatch)

    assert result.status is RunStatus.BLOCKED
    assert result.primary_blocker is not None
    assert result.primary_blocker.code == "CLEANUP_UNVERIFIED"
    assert not any(
        path.is_file() and "review" in path.name.casefold()
        for path in repo.rglob("*")
    )
