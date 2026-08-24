"""Evidence and progress primitives for the resumable Command Code Run."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Any

from .cmdc_local import CmdcEvent, CmdcLocal
from .run_record import (
    Blocker,
    RecoveryEvidence,
    RunContract,
    RunRecord,
    RunRecordError,
    RunResult,
    RunStatus,
    TestEvidence,
    run_artifact_fingerprint,
    workspace_fingerprint,
)


NO_IMPLEMENTATION_PROGRESS = "NO_IMPLEMENTATION_PROGRESS"

_RESULT_TYPES = frozenset(
    {
        "command_result",
        "exec_result",
        "shell_result",
        "shell_command_result",
        "tool_result",
    }
)
_SHELL_TOOLS = frozenset(
    {
        "bash",
        "cmd",
        "command",
        "execute",
        "execute_command",
        "powershell",
        "shell",
        "shell_command",
        "terminal",
    }
)
_WRITE_TOOLS = frozenset(
    {
        "apply_patch",
        "edit_file",
        "file_edit",
        "write_file",
        "writefile",
    }
)
_FAILURE_PATTERNS = (
    re.compile(r"(?<![\w])(?P<count>\d+)\s+(?:failed|failures?|errors?)(?![\w])", re.I),
    re.compile(r"(?:failed|failures?|errors?)\s*:\s*(?P<count>\d+)", re.I),
)
_PASSED_PATTERN = re.compile(
    r"(?<![\w])(?P<count>\d+)\s+(?:passed|passing|pass)(?![\w])", re.I
)
_PASSED_COLON_PATTERN = re.compile(r"(?:passed|passing)\s*:\s*(?P<count>\d+)", re.I)
_TOTAL_PATTERN = re.compile(r"tests?\s+run\s*:\s*(?P<count>\d+)", re.I)
_COMPLETED_PATTERN = re.compile(
    r"(?P<count>\d+)\s+tests?\s+(?:completed|executed)", re.I
)
_SUCCESS_PATTERN = re.compile(r"\b(?:ok|build\s+success|tests?\s+passed)\b", re.I)
_FAILURE_COLON_PATTERN = re.compile(
    r"(?:failed|failures?|errors?)\s*:\s*(?P<count>\d+)", re.I
)
_MAVEN_PATTERN = re.compile(
    r"tests?\s+run\s*:\s*(?P<total>\d+).*?failures?\s*:\s*(?P<failed>\d+).*?errors?\s*:\s*(?P<errors>\d+)",
    re.I | re.S,
)


@dataclass(frozen=True)
class ProgressSignal:
    """The first durable signal that an Implementer changed the task state."""

    kind: str
    event_sequence: int | None
    turn_number: int | None
    detail: str


@dataclass(frozen=True)
class ProgressAssessment:
    first_progress: ProgressSignal | None
    signals: tuple[ProgressSignal, ...]
    deadline_turn: int
    blocker: str | None


class LifecycleError(RuntimeError):
    """A lifecycle operation cannot be performed safely."""


def default_progress_deadline(max_turns: int) -> int:
    """Return the conservative early-turn deadline from the Run Contract."""

    if isinstance(max_turns, bool) or not isinstance(max_turns, int) or max_turns <= 0:
        raise ValueError("max_turns must be a positive integer")
    return min(10, max(1, (max_turns + 4) // 5))


def normalize_test_evidence(events: Iterable[CmdcEvent]) -> tuple[TestEvidence, ...]:
    """Extract only conservative, zero-failure test evidence from Cmdc events.

    The original command and stream values remain on the source ``CmdcEvent``;
    this function stores only the normalized fields accepted by ``TestEvidence``.
    It never splits a shell command on ``;``.
    """

    normalized: list[TestEvidence] = []
    for event_sequence, event in enumerate(events, start=1):
        if not isinstance(event, CmdcEvent):
            continue
        if not _is_command_result(event) or event.exit_code != 0:
            continue
        command = event.command
        if not command or not _is_test_command(command):
            continue
        parsed = _parse_test_summary(event.stdout, event.stderr)
        if parsed is None:
            continue
        summary, passed, failed = parsed
        if failed != 0:
            continue
        normalized.append(
            TestEvidence(
                command=command,
                exit_code=0,
                summary=summary,
                passed=passed,
                failed=failed,
                event_sequence=event_sequence,
            )
        )
    return tuple(normalized)


def evaluate_progress(
    events: Sequence[CmdcEvent] | Iterable[CmdcEvent],
    *,
    max_turns: int,
    progress_deadline_turns: int | None = None,
    baseline_fingerprint: Mapping[str, object] | None = None,
    current_fingerprint: Mapping[str, object] | None = None,
    base_head: str | None = None,
    current_head: str | None = None,
) -> ProgressAssessment:
    """Classify durable implementation signals and enforce the early deadline.

    Reads, searches, narration, ``git status``, and ``git diff`` are activity but
    not progress. A workspace snapshot supplied here is assumed to have already
    passed scope validation; scope policy remains the responsibility of the
    private scope guard.

    The deadline comes from the immutable Run Contract's
    ``execution.progress_deadline_turns`` when supplied; ``max_turns`` alone
    falls back to the conservative derived deadline only when the caller does
    not own a Contract policy value.
    """

    event_list = tuple(events)
    if progress_deadline_turns is None:
        deadline = default_progress_deadline(max_turns)
    else:
        if isinstance(progress_deadline_turns, bool) or not isinstance(
            progress_deadline_turns, int
        ):
            raise ValueError("progress_deadline_turns must be a positive integer")
        if progress_deadline_turns < 1 or progress_deadline_turns > max_turns:
            raise ValueError(
                "progress_deadline_turns must be between one and max_turns"
            )
        deadline = progress_deadline_turns
    signals: list[ProgressSignal] = []
    for event_sequence, event in enumerate(event_list, start=1):
        if not isinstance(event, CmdcEvent):
            continue
        kind = classify_progress_event(event)
        if kind is None:
            continue
        signals.append(
            ProgressSignal(
                kind=kind,
                event_sequence=event_sequence,
                turn_number=event.turn_number,
                detail=event.command or event.tool or event.type,
            )
        )

    if baseline_fingerprint is not None and current_fingerprint is not None:
        baseline_paths = _mapping_value(baseline_fingerprint, "paths")
        current_paths = _mapping_value(current_fingerprint, "paths")
        if baseline_paths != current_paths:
            signals.append(
                ProgressSignal(
                    kind="workspace_delta",
                    event_sequence=None,
                    turn_number=None,
                    detail="workspace fingerprint paths changed",
                )
            )
        elif (
            base_head is not None
            and current_head is not None
            and base_head != current_head
        ):
            signals.append(
                ProgressSignal(
                    kind="task_commit",
                    event_sequence=None,
                    turn_number=None,
                    detail="HEAD advanced from the Run base",
                )
            )

    first = signals[0] if signals else None
    observed_turns = [
        event.turn_number
        for event in event_list
        if isinstance(event, CmdcEvent) and isinstance(event.turn_number, int)
    ]
    reached_deadline = first is None and bool(observed_turns) and max(observed_turns) >= deadline
    return ProgressAssessment(
        first_progress=first,
        signals=tuple(signals),
        deadline_turn=deadline,
        blocker=NO_IMPLEMENTATION_PROGRESS if reached_deadline else None,
    )


def classify_progress_event(event: CmdcEvent) -> str | None:
    """Classify one event without treating generic shell activity as progress."""

    if not isinstance(event, CmdcEvent):
        return None
    tool = (event.tool or "").casefold().replace("-", "_")
    raw = event.raw if isinstance(event.raw, Mapping) else {}
    raw_tool = str(raw.get("tool", "")).casefold().replace("-", "_")
    operation = str(raw.get("operation", raw.get("action", ""))).casefold()
    if tool in _WRITE_TOOLS or raw_tool in _WRITE_TOOLS or operation in {
        "apply_patch",
        "edit_file",
        "write_file",
    }:
        if _is_command_result(event) and (event.exit_code is None or event.exit_code == 0):
            return "permitted_write"
        return None
    if event.command and _is_validation_command(event.command):
        if _is_command_result(event) and (event.exit_code is None or event.exit_code in range(0, 256)):
            return "recognized_validation"
    return None


def append_event_records(record: RunRecord, events: Iterable[CmdcEvent]) -> tuple[int, ...]:
    """Append raw Cmdc events while retaining exact command and streams."""

    records: list[dict[str, object]] = []
    for event in events:
        if not isinstance(event, CmdcEvent):
            continue
        records.append(
            {
                "type": event.type,
                "session_id": event.session_id,
                "turn": event.turn_number,
                "tool": event.tool,
                "command": event.command,
                "exit_code": event.exit_code,
                "stdout": event.stdout,
                "stderr": event.stderr,
                "raw": dict(event.raw),
            }
        )
    return record.append_events(records)


def persist_progress_checkpoint(record: Any, assessment: ProgressAssessment) -> int | None:
    """Persist exactly the first progress signal, or the deadline blocker."""

    if not isinstance(assessment, ProgressAssessment):
        raise TypeError("assessment must be a ProgressAssessment")
    if assessment.first_progress is not None:
        signal = assessment.first_progress
        return record.append_checkpoint(
            {
                "kind": "progress",
                "state": "PROGRESS",
                "progress_kind": signal.kind,
                "event_sequence": signal.event_sequence,
                "turn": signal.turn_number,
                "detail": signal.detail,
            }
        )
    if assessment.blocker is not None:
        return record.append_checkpoint(
            {
                "kind": "progress_deadline",
                "state": "BLOCKED",
                "blocker": assessment.blocker,
                "deadline_turn": assessment.deadline_turn,
            }
        )
    return None


class _LifecycleState(str, Enum):
    PREFLIGHT = "PREFLIGHT"
    SPAWN = "SPAWN"
    RUNNING = "RUNNING"
    NO_IMPLEMENTATION_PROGRESS = NO_IMPLEMENTATION_PROGRESS
    STALLED = "STALLED"
    WALL_TIMEOUT = "WALL_TIMEOUT"
    TERMINATING = "TERMINATING"
    CLEANUP_VERIFICATION = "CLEANUP_VERIFICATION"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    INCOMPLETE = "INCOMPLETE"


class _LifecycleFault(LifecycleError):
    def __init__(self, code: str, phase: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.phase = phase
        self.message = message


_TRANSITIONS: dict[_LifecycleState | None, frozenset[_LifecycleState]] = {
    None: frozenset({_LifecycleState.PREFLIGHT}),
    _LifecycleState.PREFLIGHT: frozenset(
        {_LifecycleState.SPAWN, _LifecycleState.TERMINATING}
    ),
    _LifecycleState.SPAWN: frozenset(
        {_LifecycleState.RUNNING, _LifecycleState.TERMINATING}
    ),
    _LifecycleState.RUNNING: frozenset(
        {
            _LifecycleState.NO_IMPLEMENTATION_PROGRESS,
            _LifecycleState.STALLED,
            _LifecycleState.WALL_TIMEOUT,
            _LifecycleState.TERMINATING,
            _LifecycleState.CLEANUP_VERIFICATION,
        }
    ),
    _LifecycleState.NO_IMPLEMENTATION_PROGRESS: frozenset(
        {_LifecycleState.TERMINATING}
    ),
    _LifecycleState.STALLED: frozenset({_LifecycleState.TERMINATING}),
    _LifecycleState.WALL_TIMEOUT: frozenset({_LifecycleState.TERMINATING}),
    _LifecycleState.TERMINATING: frozenset({_LifecycleState.CLEANUP_VERIFICATION}),
    _LifecycleState.CLEANUP_VERIFICATION: frozenset(
        {
            _LifecycleState.COMPLETE,
            _LifecycleState.BLOCKED,
            _LifecycleState.INCOMPLETE,
        }
    ),
    _LifecycleState.COMPLETE: frozenset(),
    _LifecycleState.BLOCKED: frozenset(),
    _LifecycleState.INCOMPLETE: frozenset(),
}


class ExecutionLifecycle:
    """Execute one immutable Run Contract through the local Cmdc adapter."""

    def __init__(self, record: RunRecord, cmdc: CmdcLocal) -> None:
        self.record = record
        self.cmdc = cmdc
        self._state: _LifecycleState | None = None
        self._history: list[_LifecycleState] = []
        self._primary: Blocker | None = None
        self._secondary: list[Blocker] = []
        self._incomplete = False
        self._scope_contract: dict[str, object] | None = None
        self._baseline_fingerprint: Mapping[str, object] | None = None
        self._baseline_verified = False
        self._current_fingerprint: Mapping[str, object] | None = None
        self._request: Any | None = None
        self._recovery_prior: RunResult | None = None
        self._recovery_attempt = 0
        self._recovery_checkpoint_sequence: int | None = None
        self._recovery_expected_session: str | None = None
        self._recovery_trigger = "explicit-resume"

    @property
    def state(self) -> str | None:
        return self._state.value if self._state is not None else None

    @property
    def history(self) -> tuple[str, ...]:
        return tuple(state.value for state in self._history)

    def _transition(self, target: _LifecycleState | str) -> None:
        if isinstance(target, str):
            try:
                target = _LifecycleState(target)
            except ValueError as error:
                raise LifecycleError(f"unknown lifecycle state: {target}") from error
        if target not in _TRANSITIONS.get(self._state, frozenset()):
            current = self._state.value if self._state is not None else "<initial>"
            raise LifecycleError(f"invalid lifecycle transition {current} -> {target.value}")
        self._state = target
        self._history.append(target)
        self._checkpoint(
            {
                "kind": "lifecycle",
                "phase": target.value,
                "state": target.value,
            }
        )

    def _checkpoint(self, value: dict[str, object]) -> int:
        try:
            return self.record.append_checkpoint(value)
        except (OSError, RunRecordError) as error:
            self._add_blocker(
                "CHECKPOINT_PERSISTENCE_FAILED",
                "CHECKPOINT",
                f"could not persist lifecycle checkpoint: {error}",
            )
            return 0

    def _add_blocker(self, code: str, phase: str, message: str) -> None:
        blocker = Blocker(code=code, phase=phase, message=message)
        if self._primary is None:
            self._primary = blocker
        else:
            self._secondary.append(blocker)

    def _reset(self) -> None:
        self._state = None
        self._history.clear()
        self._primary = None
        self._secondary.clear()
        self._incomplete = False
        self._scope_contract = None
        self._baseline_fingerprint = None
        self._baseline_verified = False
        self._current_fingerprint = None
        self._request = None
        self._recovery_prior = None
        self._recovery_attempt = 0
        self._recovery_checkpoint_sequence = None
        self._recovery_expected_session = None
        self._recovery_trigger = "explicit-resume"

    def start(self) -> RunResult:
        self._reset()
        self._transition(_LifecycleState.PREFLIGHT)
        try:
            request = self._preflight()
        except _LifecycleFault as error:
            self._add_blocker(error.code, error.phase, error.message)
            return self._finish_without_process()

        self._transition(_LifecycleState.SPAWN)
        try:
            outcome = self.cmdc.start(request)
        except _LifecycleFault as error:
            self._add_blocker(error.code, error.phase, error.message)
            return self._finish_without_process()
        except Exception as error:  # noqa: BLE001 - convert adapter failures to a stable Result
            self._add_blocker(
                "RUNTIME_FAILED",
                "SPAWN",
                f"cmdc-local execution failed: {error}",
            )
            return self._finish_without_process()

        self._transition(_LifecycleState.RUNNING)
        result = self._finish_outcome(outcome)
        if self._eligible_for_automatic_recovery(result):
            return ExecutionLifecycle(self.record, self.cmdc)._resume_internal(
                trigger="WORKER_TURN_LIMIT",
                automatic=True,
            )
        return result

    def resume(self) -> RunResult:
        self._reset()
        return self._resume_internal(trigger="explicit-resume", automatic=False)

    def _eligible_for_automatic_recovery(self, result: RunResult) -> bool:
        return bool(
            result.primary_blocker is not None
            and result.primary_blocker.code == "WORKER_TURN_LIMIT"
            and result.cleanup_verified
            and len(result.recoveries) < self.record.contract.execution.max_resumes
        )

    def _resume_internal(self, *, trigger: str, automatic: bool) -> RunResult:
        self._recovery_trigger = trigger
        self._transition(_LifecycleState.PREFLIGHT)
        try:
            session_id, request = self._validate_recovery(trigger=trigger, automatic=automatic)
        except _LifecycleFault as error:
            self._add_blocker(error.code, error.phase, error.message)
            return self._finish_without_process()
        self._transition(_LifecycleState.SPAWN)
        try:
            outcome = self.cmdc.resume(session_id, request)
        except Exception as error:  # noqa: BLE001 - convert adapter failures to a stable Result
            self._add_blocker(
                "RUNTIME_FAILED",
                "SPAWN",
                f"cmdc-local Recovery failed: {error}",
            )
            return self._finish_without_process()
        self._transition(_LifecycleState.RUNNING)
        return self._finish_outcome(outcome)

    def _validate_recovery(
        self,
        *,
        trigger: str,
        automatic: bool,
    ) -> tuple[str, Any]:
        try:
            prior = self.record.read_result()
            checkpoints = self.record.read_checkpoints()
        except RunRecordError as error:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                f"Run record ownership or sequence validation failed: {error}",
            ) from error
        if prior is None:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "Recovery requires an existing persisted Result",
            )
        contract = self.record.contract
        try:
            persisted_contract = RunContract.load(self.record.run_dir / "contract.json")
        except RunRecordError as error:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                f"immutable Run Contract could not be revalidated: {error}",
            ) from error
        if persisted_contract != contract:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "persisted Run Contract differs from the loaded Contract",
            )
        if prior.run_id != contract.run_id or prior.base_head != contract.workspace.base_head:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "Result run_id or base_head does not match the immutable Contract",
            )
        if prior.artifact_hashes.get("contract") != self.record.contract_sha256:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "Result contract SHA-256 does not match the immutable Contract",
            )
        if prior.status is RunStatus.COMPLETE:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "a COMPLETE Run cannot be resumed",
            )
        primary_code = prior.primary_blocker.code if prior.primary_blocker else ""
        resumable_codes = {"STALLED", "WALL_TIMEOUT", "WORKER_TURN_LIMIT", "INTERRUPTED"}
        if primary_code not in resumable_codes:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                f"primary blocker {primary_code or '<none>'} is not resumable",
            )
        attempt = len(prior.recoveries)
        if attempt >= contract.execution.max_resumes:
            raise _LifecycleFault(
                "RECOVERY_EXHAUSTED",
                "PREFLIGHT",
                "the Run has exhausted its configured Recovery attempts",
            )
        session_checkpoints = [
            checkpoint
            for checkpoint in checkpoints
            if checkpoint.get("kind") == "session"
            and isinstance(checkpoint.get("session_id"), str)
            and bool(str(checkpoint.get("session_id")).strip())
        ]
        if not session_checkpoints:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "no owned Checkpoint captured a Command Code Session ID",
            )
        session_checkpoint = session_checkpoints[-1]
        session_id = str(session_checkpoint["session_id"])
        checkpoint_sequence = session_checkpoint.get("sequence")
        if not isinstance(checkpoint_sequence, int) or checkpoint_sequence < 1:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "captured Session Checkpoint has no valid sequence",
            )
        expected_head = session_checkpoint.get("head")
        expected_branch = session_checkpoint.get("branch")
        checkpoint_fingerprint = session_checkpoint.get("workspace_fingerprint")
        if not isinstance(expected_head, str) or not isinstance(
            expected_branch, str
        ) or not isinstance(checkpoint_fingerprint, Mapping):
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "Session Checkpoint lacks the expected workspace identity",
            )
        current = self._capture_fingerprint(contract.workspace.repo_root)
        if current.get("branch") != expected_branch or current.get("head") != expected_head:
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "current branch or HEAD differs from the Recovery Checkpoint",
            )
        from ._scope_guard import ScopeGuardError, audit_workspace, check_tool, load_scope_contract

        scope_path = self.record.run_dir / "scope-contract.json"
        try:
            scope = load_scope_contract(scope_path)
            audit = audit_workspace(scope, {}, owner_run_dir=self.record.run_dir)
        except ScopeGuardError as error:
            raise _LifecycleFault(error.code, "PREFLIGHT", str(error)) from error
        if audit.get("decision") != "allow":
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "workspace scope changed outside the known baseline and allowed Run paths",
            )
        checkpoint_paths = checkpoint_fingerprint.get("paths", {})
        current_paths = current.get("paths", {})
        if not isinstance(checkpoint_paths, Mapping) or not isinstance(current_paths, Mapping):
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "Recovery workspace fingerprint paths are malformed",
            )
        for raw_path in set(checkpoint_paths) | set(current_paths):
            if not isinstance(raw_path, str):
                raise _LifecycleFault(
                    "RESUME_INVARIANT_FAILED",
                    "PREFLIGHT",
                    "Recovery workspace fingerprint contains a non-string path",
                )
            if checkpoint_paths.get(raw_path) == current_paths.get(raw_path):
                continue
            decision = check_tool(scope, {"toolName": "write_file", "input": {"path": raw_path}})
            if decision.get("decision") != "allow":
                raise _LifecycleFault(
                    "RESUME_INVARIANT_FAILED",
                    "PREFLIGHT",
                    f"workspace path changed outside allowed Recovery scope: {raw_path}",
                )
        if checkpoint_paths == current_paths and (
            checkpoint_fingerprint.get("status_sha256")
            != current.get("status_sha256")
        ):
            raise _LifecycleFault(
                "RESUME_INVARIANT_FAILED",
                "PREFLIGHT",
                "Recovery workspace fingerprint status hash does not match the current tree",
            )
        if prior.recoveries:
            previous_recovery = prior.recoveries[-1]
            if not previous_recovery.same_session or previous_recovery.session_id != session_id:
                raise _LifecycleFault(
                    "RESUME_INVARIANT_FAILED",
                    "PREFLIGHT",
                    "the previous Recovery did not preserve the same Command Code Session",
                )
        self._recovery_prior = prior
        self._recovery_attempt = attempt + 1
        self._recovery_expected_session = session_id
        self._baseline_fingerprint = checkpoint_fingerprint
        self._baseline_verified = True
        self._current_fingerprint = current
        self._scope_contract = scope
        request = self._build_request(contract.workspace.repo_root)
        request = replace(request, prompt=_render_recovery_prompt(contract, prior))
        self._request = request
        self._recovery_checkpoint_sequence = self._checkpoint(
            {
                "kind": "recovery",
                "state": "RUNNING",
                "attempt": self._recovery_attempt,
                "trigger": trigger,
                "session_id": session_id,
                "same_session": True,
                "automatic": automatic,
                "checkpoint_sequence": checkpoint_sequence,
            }
        )
        return session_id, request

    def _preflight(self) -> Any:
        contract = self.record.contract
        repo_root = contract.workspace.repo_root.expanduser().resolve()
        if not repo_root.is_dir():
            raise _LifecycleFault("WORKSPACE_ROOT_INVALID", "PREFLIGHT", "workspace root is not a directory")
        try:
            self.record.run_dir.resolve().relative_to(repo_root)
        except ValueError as error:
            raise _LifecycleFault(
                "RUN_OUTSIDE_REPOSITORY",
                "PREFLIGHT",
                "Run artifacts are outside the contract workspace",
            ) from error

        current = self._capture_fingerprint(repo_root)
        self._baseline_fingerprint = current
        branch = str(current.get("branch", ""))
        head = str(current.get("head", ""))
        if branch != contract.workspace.branch:
            raise _LifecycleFault(
                "WORKSPACE_BRANCH_MISMATCH",
                "PREFLIGHT",
                f"current branch {branch!r} does not match {contract.workspace.branch!r}",
            )
        if branch.casefold() in {"main", "master"}:
            raise _LifecycleFault(
                "BRANCH_PROTECTED",
                "PREFLIGHT",
                "protected branches require an explicit governed authorization",
            )
        if head != contract.workspace.base_head:
            raise _LifecycleFault(
                "BASE_HEAD_MISMATCH",
                "PREFLIGHT",
                "current HEAD does not match the Run Contract base_head",
            )
        self._validate_baseline_fingerprint(repo_root, current)
        if contract.execution.model != "deepseek/deepseek-v4-flash":
            raise _LifecycleFault(
                "MODEL_UNAVAILABLE",
                "PREFLIGHT",
                "Run Contract model is not the fixed cmdc-local model",
            )
        if _looks_deployed_path(repo_root):
            raise _LifecycleFault(
                "DEPLOYED_SERVER_PATH",
                "PREFLIGHT",
                "direct execution on a deployed/server path is not authorized",
            )
        self._validate_artifacts(repo_root)
        self._write_scope_contract(repo_root, current)
        self._preflight_cmdc(repo_root)
        request = self._build_request(repo_root)
        self._request = request
        return request

    def _validate_baseline_fingerprint(
        self, repo_root: Path, current: Mapping[str, object]
    ) -> None:
        """Require the current workspace to match the Contract baseline exactly.

        The Contract's ``baseline_status`` was captured before
        ``RunRecord.create`` added the lifecycle-owned Run artifacts, so the
        expected untracked Run files are merged into the baseline before the
        comparison. Any remaining difference — including a tracked file
        changed after Contract creation — is an unauthorized change and fails
        closed with ``BASELINE_FINGERPRINT_MISMATCH`` before the lifecycle
        baseline is assigned.
        """
        contract = self.record.contract
        baseline = contract.workspace.baseline_status
        try:
            expected = run_artifact_fingerprint(repo_root, self.record.run_dir, baseline)
        except (RunRecordError, OSError, ValueError) as error:
            raise _LifecycleFault(
                "BASELINE_FINGERPRINT_MISMATCH",
                "PREFLIGHT",
                f"workspace baseline could not be validated: {error}",
            ) from error
        current_paths = current.get("paths")
        expected_paths = expected.get("paths")
        if not isinstance(current_paths, Mapping) or not isinstance(expected_paths, Mapping):
            raise _LifecycleFault(
                "BASELINE_FINGERPRINT_MISMATCH",
                "PREFLIGHT",
                "workspace baseline or current fingerprint lacks path evidence",
            )
        if current_paths != expected_paths:
            raise _LifecycleFault(
                "BASELINE_FINGERPRINT_MISMATCH",
                "PREFLIGHT",
                "workspace changed after the Run Contract was created",
            )
        if str(current.get("status_sha256", "")) != str(
            expected.get("status_sha256", "")
        ):
            raise _LifecycleFault(
                "BASELINE_FINGERPRINT_MISMATCH",
                "PREFLIGHT",
                "workspace status hash changed after the Run Contract was created",
            )
        self._baseline_fingerprint = current
        self._baseline_verified = True

    def _validate_artifacts(self, repo_root: Path) -> None:
        contract = self.record.contract
        for label, path, require_file in (
            ("task brief", contract.task.brief_path, True),
            ("report", contract.task.report_path, False),
        ):
            resolved = path.expanduser().resolve(strict=False)
            try:
                resolved.relative_to(repo_root)
            except ValueError as error:
                raise _LifecycleFault(
                    f"{label.upper().replace(' ', '_')}_OUTSIDE_REPOSITORY",
                    "PREFLIGHT",
                    f"{label} path is outside the workspace: {resolved}",
                ) from error
            if require_file and not resolved.is_file():
                raise _LifecycleFault(
                    f"{label.upper().replace(' ', '_')}_INVALID",
                    "PREFLIGHT",
                    f"{label} file is missing: {resolved}",
                )
            if not require_file and not resolved.parent.is_dir():
                raise _LifecycleFault(
                    "REPORT_INVALID",
                    "PREFLIGHT",
                    f"report parent directory is missing: {resolved.parent}",
                )
        plan = contract.plan.source_path.expanduser().resolve(strict=False)
        source_repo = contract.plan.source_repository.expanduser().resolve(strict=False)
        try:
            plan.relative_to(source_repo)
        except ValueError as error:
            raise _LifecycleFault(
                "PLAN_PROVENANCE_INVALID",
                "PREFLIGHT",
                "plan source is outside its recorded source repository",
            ) from error
        if not plan.is_file():
            raise _LifecycleFault(
                "PLAN_INVALID",
                "PREFLIGHT",
                f"plan source file is missing: {plan}",
            )
        plan_hash = _file_sha256(plan)
        if plan_hash is None or plan_hash.casefold() != contract.plan.sha256.casefold():
            raise _LifecycleFault(
                "PLAN_HASH_MISMATCH",
                "PREFLIGHT",
                "plan source SHA-256 does not match the Run Contract",
            )
        brief_hash = _file_sha256(contract.task.brief_path)
        if brief_hash is None or brief_hash.casefold() != contract.task.brief_sha256.casefold():
            raise _LifecycleFault(
                "TASK_BRIEF_HASH_MISMATCH",
                "PREFLIGHT",
                "task brief SHA-256 does not match the Run Contract",
            )

    def _write_scope_contract(
        self, repo_root: Path, baseline: Mapping[str, object]
    ) -> None:
        from ._scope_guard import ScopeGuardError, build_scope_contract

        contract = self.record.contract
        allowed = list(contract.scope.allowed_paths)
        if not allowed:
            raise _LifecycleFault(
                "SCOPE_CONTRACT_MISSING",
                "PREFLIGHT",
                "Run Contract has no explicit allowed paths",
            )
        run_relative = self.record.run_dir.resolve().relative_to(repo_root).as_posix()
        allowed.append(run_relative + "/")
        try:
            scope = build_scope_contract(
                repo_root,
                explicit_allowed_paths=allowed,
                denied_paths=contract.scope.denied_paths,
                baseline=baseline,
            )
        except ScopeGuardError as error:
            raise _LifecycleFault(error.code, "PREFLIGHT", str(error)) from error
        self._scope_contract = scope
        _atomic_json_write(self.record.run_dir / "scope-contract.json", scope)

    def _preflight_cmdc(self, repo_root: Path) -> None:
        mod_path = Path(__file__).with_name("_mod_probe.ts")
        if not mod_path.is_file():
            raise _LifecycleFault(
                "MOD_NOT_FOUND",
                "PREFLIGHT",
                f"Run-specific Command Code Mod is missing: {mod_path}",
            )
        resolver = getattr(self.cmdc, "resolve_launcher", None)
        if callable(resolver):
            try:
                launcher = resolver()
            except Exception as error:  # noqa: BLE001 - adapter taxonomy boundary
                code = getattr(error, "code", "LAUNCHER_RESOLUTION_FAILED")
                raise _LifecycleFault(str(code), "PREFLIGHT", str(error)) from error
            if launcher is None:
                raise _LifecycleFault(
                    "LAUNCHER_RESOLUTION_FAILED",
                    "PREFLIGHT",
                    "cmdc-local did not resolve a launcher",
                )
        smoke = getattr(self.cmdc, "smoke_test", None)
        if callable(smoke):
            try:
                with tempfile.TemporaryDirectory(prefix="sdd-cmdc-smoke-") as path:
                    try:
                        result = smoke(
                            Path(path),
                            require_mod_hook=True,
                            mod_path=mod_path,
                        )
                    except TypeError as error:
                        if "mod_path" not in str(error):
                            raise
                        result = smoke(Path(path), require_mod_hook=True)
            except Exception as error:  # noqa: BLE001 - adapter taxonomy boundary
                code = getattr(error, "code", "MOD_HOOK_UNVERIFIED")
                raise _LifecycleFault(str(code), "PREFLIGHT", str(error)) from error
            if hasattr(result, "mod_hook_verified") and not result.mod_hook_verified:
                raise _LifecycleFault(
                    "MOD_HOOK_UNVERIFIED",
                    "PREFLIGHT",
                    "Command Code Mod hook capability was not verified",
                )

    def _build_request(self, repo_root: Path) -> Any:
        from .cmdc_local import CmdcRequest

        contract = self.record.contract
        if self._scope_contract is None:
            raise _LifecycleFault(
                "SCOPE_CONTRACT_MISSING",
                "PREFLIGHT",
                "scope contract was not persisted before spawn",
            )
        scope_path = self.record.run_dir / "scope-contract.json"
        helper = Path(__file__).with_name("_scope_guard.py")
        try:
            prompt = _render_contract_prompt(contract)
        except OSError as error:
            raise _LifecycleFault("TASK_BRIEF_INVALID", "PREFLIGHT", str(error)) from error
        return CmdcRequest(
            cwd=repo_root,
            prompt=prompt,
            max_turns=contract.execution.max_turns,
            # The Contract loader rejects execution.yolo=false, so the
            # launcher mode is always yolo here; keep the request explicit.
            allow_yolo=True,
            wall_timeout_seconds=float(contract.execution.wall_timeout_seconds),
            stall_timeout_seconds=float(contract.execution.stall_timeout_seconds),
            mod_path=Path(__file__).with_name("_scope_mod.ts"),
            scope_env={
                "SDD_CMDC_SCOPE_PYTHON": sys.executable,
                "SDD_CMDC_SCOPE_HELPER": str(helper),
                "SDD_CMDC_SCOPE_CONTRACT": str(scope_path),
                "SDD_CMDC_SCOPE_RUN_OWNER": str(self.record.run_dir.resolve()),
            },
        )

    def _finish_without_process(self) -> RunResult:
        if self._state in {
            _LifecycleState.PREFLIGHT,
            _LifecycleState.SPAWN,
            _LifecycleState.RUNNING,
        }:
            self._transition(_LifecycleState.TERMINATING)
        if self._state is _LifecycleState.TERMINATING:
            self._transition(_LifecycleState.CLEANUP_VERIFICATION)
        return self._write_result(
            status=RunStatus.BLOCKED,
            session_id=None,
            tests=(),
            scope_valid=False,
            violating_paths=(),
            report_valid=False,
            test_evidence_valid=False,
            cleanup_verified=True,
        )

    def _finish_outcome(self, outcome: Any) -> RunResult:
        if not self._baseline_verified:
            self._add_blocker(
                "BASELINE_FINGERPRINT_MISMATCH",
                "PREFLIGHT",
                "lifecycle baseline was not verified before execution",
            )
            return self._finish_without_process()
        if not hasattr(outcome, "process") or not hasattr(outcome, "events"):
            self._add_blocker(
                "CMD_CODE_PROTOCOL_ERROR",
                "RUNNING",
                "cmdc-local returned an invalid outcome shape",
            )
            return self._finish_without_process()
        if (
            self._recovery_expected_session is not None
            and getattr(outcome, "session_id", None) != self._recovery_expected_session
        ):
            self._add_blocker(
                "CMD_CODE_PROTOCOL_ERROR",
                "RUNNING",
                "Recovery returned a different Command Code Session ID",
            )
        self._append_outcome(outcome)
        tests = normalize_test_evidence(outcome.events)
        current = self._capture_fingerprint(self.record.contract.workspace.repo_root)
        self._current_fingerprint = current
        assessment = evaluate_progress(
            outcome.events,
            max_turns=self.record.contract.execution.max_turns,
            progress_deadline_turns=self.record.contract.execution.progress_deadline_turns,
            baseline_fingerprint=self._baseline_fingerprint,
            current_fingerprint=current,
            base_head=self.record.contract.workspace.base_head,
            current_head=str(current.get("head", "")),
        )
        persist_progress_checkpoint(self.record, assessment)
        timed_out = self._process_blockers(outcome)
        if assessment.blocker is not None:
            if self._state is _LifecycleState.RUNNING:
                self._transition(_LifecycleState.NO_IMPLEMENTATION_PROGRESS)
            self._add_blocker(
                NO_IMPLEMENTATION_PROGRESS,
                "NO_IMPLEMENTATION_PROGRESS",
                "the configured progress deadline elapsed without implementation progress",
            )
        should_terminate = self._primary is not None or timed_out
        if should_terminate and self._state is _LifecycleState.RUNNING:
            if timed_out and self._state is _LifecycleState.RUNNING:
                # The specific timeout state was recorded by _process_blockers.
                self._transition(_LifecycleState.TERMINATING)
            else:
                self._transition(_LifecycleState.TERMINATING)
        elif self._state in {
            _LifecycleState.NO_IMPLEMENTATION_PROGRESS,
            _LifecycleState.STALLED,
            _LifecycleState.WALL_TIMEOUT,
        }:
            self._transition(_LifecycleState.TERMINATING)
        if self._state is _LifecycleState.RUNNING:
            self._transition(_LifecycleState.CLEANUP_VERIFICATION)
        elif self._state is _LifecycleState.TERMINATING:
            self._transition(_LifecycleState.CLEANUP_VERIFICATION)

        scope_valid, violating_paths = self._audit_scope()
        report_valid = self._report_valid()
        test_valid = bool(tests)
        if not timed_out and not self._has_runtime_failure(outcome):
            self._validate_success_requirements(
                outcome,
                report_valid=report_valid,
                test_valid=test_valid,
                scope_valid=scope_valid,
            )
        cleanup_verified = bool(
            outcome.process.cleanup_verified and outcome.process.drain_verified
        )
        if self._incomplete:
            status = RunStatus.INCOMPLETE
        elif self._primary is not None:
            status = RunStatus.BLOCKED
        else:
            status = RunStatus.COMPLETE
        terminal = {
            RunStatus.COMPLETE: _LifecycleState.COMPLETE,
            RunStatus.BLOCKED: _LifecycleState.BLOCKED,
            RunStatus.INCOMPLETE: _LifecycleState.INCOMPLETE,
        }[status]
        self._transition(terminal)
        return self._write_result(
            status=status,
            session_id=getattr(outcome, "session_id", None),
            tests=tests,
            scope_valid=scope_valid,
            violating_paths=violating_paths,
            report_valid=report_valid,
            test_evidence_valid=test_valid,
            cleanup_verified=cleanup_verified,
        )

    def _append_outcome(self, outcome: Any) -> None:
        append_event_records(self.record, outcome.events)
        self.record.append_event(
            {
                "type": "terminal_result",
                "subtype": getattr(outcome, "subtype", None),
                "stop_reason": getattr(outcome, "stop_reason", None),
                "session_id": getattr(outcome, "session_id", None),
                "final_text": getattr(outcome, "final_text", ""),
                "process_status": getattr(outcome.process.status, "value", outcome.process.status),
                "returncode": outcome.process.returncode,
                "stdout": outcome.process.stdout,
                "stderr": outcome.process.stderr,
            }
        )
        if getattr(outcome, "session_id", None):
            fingerprint = self._capture_fingerprint(
                self.record.contract.workspace.repo_root
            )
            self._checkpoint(
                {
                    "kind": "session",
                    "state": "RUNNING",
                    "session_id": outcome.session_id,
                    "head": fingerprint.get("head"),
                    "branch": fingerprint.get("branch"),
                    "workspace_fingerprint": fingerprint,
                }
            )
            if self._recovery_expected_session is not None:
                self._current_fingerprint = fingerprint

    def _process_blockers(self, outcome: Any) -> bool:
        process = outcome.process
        timed_out = False
        if process.primary_failure is not None:
            failure = process.primary_failure
            self._add_blocker(failure.code, failure.phase, failure.message)
            if failure.code in {"STALLED", "WALL_TIMEOUT", "TIMEOUT"}:
                self._incomplete = True
                timed_out = True
        for failure in process.secondary_failures:
            self._add_blocker(failure.code, failure.phase, failure.message)
        status = getattr(process.status, "value", str(process.status))
        if status == "STALLED":
            self._incomplete = True
            timed_out = True
            if self._state is _LifecycleState.RUNNING:
                self._transition(_LifecycleState.STALLED)
            self._add_blocker("STALLED", "STALLED", "cmdc-local reported a stall")
        elif status == "WALL_TIMEOUT":
            self._incomplete = True
            timed_out = True
            if self._state is _LifecycleState.RUNNING:
                self._transition(_LifecycleState.WALL_TIMEOUT)
            self._add_blocker("WALL_TIMEOUT", "WALL_TIMEOUT", "wall timeout expired")
        elif status != "EXITED":
            self._add_blocker("PROCESS_FAILED", status, f"process ended in {status}")
        elif process.returncode not in {0, None} and process.primary_failure is None:
            self._add_blocker(
                "PROCESS_FAILED",
                "RUNNING",
                f"cmdc-local exited with code {process.returncode}",
            )
        stop_reason = str(getattr(outcome, "stop_reason", "") or "").casefold()
        turn_limited = stop_reason in {
            "max_turns",
            "max_turn",
            "turn_limit",
            "turn-limit",
            "worker_turn_limit",
            "worker-turn-limit",
        } or "turn limit" in stop_reason or (
            "max" in stop_reason and "turn" in stop_reason
        )
        subtype = str(getattr(outcome, "subtype", "") or "").casefold()
        if process.primary_failure is None and process.returncode == 0 and subtype not in {
            "success",
            "complete",
            "completed",
            "done",
        } and not turn_limited:
            self._add_blocker(
                "CMD_CODE_PROTOCOL_ERROR",
                "RUNNING",
                "terminal Command Code subtype is not success",
            )
        if turn_limited:
            self._add_blocker(
                "WORKER_TURN_LIMIT",
                "WORKER_TURN_LIMIT",
                "Command Code reached the worker turn limit",
            )
            attempts_used = (
                len(self._recovery_prior.recoveries)
                if self._recovery_prior is not None
                else 0
            ) + (1 if self._recovery_prior is not None else 0)
            if self.record.contract.execution.max_resumes <= attempts_used:
                self._add_blocker(
                    "RECOVERY_EXHAUSTED",
                    "WORKER_TURN_LIMIT",
                    "the configured Recovery attempt budget is exhausted",
                )
        if not process.cleanup_verified:
            self._add_blocker(
                "CLEANUP_UNVERIFIED",
                "CLEANUP_VERIFICATION",
                "process cleanup was not verified",
            )
        if not process.drain_verified:
            self._add_blocker(
                "DRAIN_UNVERIFIED",
                "CLEANUP_VERIFICATION",
                "process output drain was not verified",
            )
        return timed_out

    def _has_runtime_failure(self, outcome: Any) -> bool:
        return bool(
            outcome.process.primary_failure
            or outcome.process.returncode not in {0, None}
            or getattr(outcome.process.status, "value", outcome.process.status) != "EXITED"
            or not outcome.process.cleanup_verified
            or not outcome.process.drain_verified
        )

    def _audit_scope(self) -> tuple[bool, tuple[str, ...]]:
        if self._scope_contract is None:
            self._add_blocker(
                "SCOPE_CONTRACT_MISSING",
                "CLEANUP_VERIFICATION",
                "scope contract was not available for final audit",
            )
            return False, ()
        from ._scope_guard import ScopeGuardError, audit_workspace

        try:
            decision = audit_workspace(
                self._scope_contract,
                {},
                owner_run_dir=self.record.run_dir,
            )
        except ScopeGuardError as error:
            self._add_blocker(error.code, "CLEANUP_VERIFICATION", str(error))
            return False, ()
        paths = tuple(
            sorted(
                str(path)
                for path in decision.get("paths", [])
                if isinstance(path, str)
            )
        )
        if decision.get("decision") != "allow":
            self._add_blocker(
                str(decision.get("code") or "SCOPE_VIOLATION"),
                "CLEANUP_VERIFICATION",
                str(decision.get("message") or "workspace is outside the Run scope"),
            )
            return False, paths
        return True, ()

    def _report_valid(self) -> bool:
        path = self.record.contract.task.report_path.expanduser().resolve(strict=False)
        try:
            return path.is_file() and bool(path.read_text(encoding="utf-8").strip())
        except (OSError, UnicodeError):
            return False

    def _validate_success_requirements(
        self,
        outcome: Any,
        *,
        report_valid: bool,
        test_valid: bool,
        scope_valid: bool,
    ) -> None:
        contract = self.record.contract
        if contract.success.require_report and not report_valid:
            self._add_blocker(
                "REPORT_INVALID",
                "RESULT",
                "Implementer Report is missing, empty, or unreadable",
            )
        if contract.success.require_test_evidence and not test_valid:
            self._add_blocker(
                "TEST_EVIDENCE_INVALID",
                "RESULT",
                "no conservative passing test evidence was observed",
            )
        if not scope_valid:
            return
        if contract.success.require_commit and not self._commit_valid():
            self._add_blocker(
                "COMMIT_REQUIREMENT_FAILED",
                "RESULT",
                "required task commit is missing or is not based on base_head",
            )

    def _commit_valid(self) -> bool:
        current = self._current_fingerprint or {}
        current_head = str(current.get("head", ""))
        base_head = self.record.contract.workspace.base_head
        if not current_head or current_head == base_head:
            return False
        result = subprocess.run(
            [
                "git",
                "-C",
                str(self.record.contract.workspace.repo_root),
                "merge-base",
                "--is-ancestor",
                base_head,
                current_head,
            ],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0

    def _capture_fingerprint(self, repo_root: Path) -> Mapping[str, object]:
        try:
            return workspace_fingerprint(repo_root, owner_run_dir=self.record.run_dir)
        except (OSError, RunRecordError, RuntimeError, subprocess.SubprocessError):
            return {
                "head": self.record.contract.workspace.base_head,
                "branch": self.record.contract.workspace.branch,
                "paths": {},
            }

    def _write_result(
        self,
        *,
        status: RunStatus,
        session_id: str | None,
        tests: tuple[TestEvidence, ...],
        scope_valid: bool,
        violating_paths: tuple[str, ...],
        report_valid: bool,
        test_evidence_valid: bool,
        cleanup_verified: bool,
    ) -> RunResult:
        current = self._current_fingerprint or self._capture_fingerprint(
            self.record.contract.workspace.repo_root
        )
        final_head = str(current.get("head") or self.record.contract.workspace.base_head)
        recoveries: tuple[RecoveryEvidence, ...] = ()
        result_tests = tests
        if self._recovery_prior is not None:
            prior = self._recovery_prior
            if self._primary is not None and prior.primary_blocker is not None:
                current_primary = self._primary
                self._primary = prior.primary_blocker
                self._secondary = [
                    *prior.secondary_blockers,
                    current_primary,
                    *self._secondary,
                ]
            result_tests = (*prior.tests, *tests)
            prior_recoveries = list(prior.recoveries)
            if self._recovery_checkpoint_sequence is not None:
                prior_recoveries.append(
                    RecoveryEvidence(
                        attempt=self._recovery_attempt,
                        trigger=self._recovery_trigger,
                        session_id=self._recovery_expected_session or session_id or "",
                        checkpoint_sequence=self._recovery_checkpoint_sequence,
                        same_session=(
                            self._recovery_expected_session is not None
                            and session_id == self._recovery_expected_session
                        ),
                    )
                )
            recoveries = tuple(prior_recoveries)
        result = RunResult(
            schema_version=1,
            run_id=self.record.contract.run_id,
            backend=self.record.contract.execution.backend,
            session_id=session_id,
            status=status,
            primary_blocker=self._primary,
            secondary_blockers=tuple(self._secondary),
            base_head=self.record.contract.workspace.base_head,
            final_head=final_head,
            scope_valid=scope_valid,
            violating_paths=violating_paths,
            report_valid=report_valid,
            test_evidence_valid=test_evidence_valid,
            cleanup_verified=cleanup_verified,
            tests=result_tests,
            recoveries=recoveries,
            artifact_hashes=self._artifact_hashes(),
        )
        self.record.write_result(result)
        return result

    def _finish_preflight_artifacts(self) -> dict[str, str]:
        return self._artifact_hashes()

    def _artifact_hashes(self) -> dict[str, str]:
        values = {"contract": self.record.contract_sha256}
        for name in ("scope-contract.json", "events.jsonl", "checkpoints.jsonl"):
            path = self.record.run_dir / name
            digest = _file_sha256(path)
            if digest is not None:
                values[name.removesuffix(".jsonl").removesuffix(".json")] = digest
        report = self.record.contract.task.report_path
        report_digest = _file_sha256(report)
        if report_digest is not None:
            values["report"] = report_digest
        return values


def _render_contract_prompt(contract: Any) -> str:
    brief_path = contract.task.brief_path.expanduser().resolve()
    brief = brief_path.read_text(encoding="utf-8")
    report_path = contract.task.report_path.expanduser().resolve(strict=False)
    if contract.success.require_commit:
        commit_policy = (
            "A task commit based on the Run base HEAD is required before reporting. "
            "Commit only files permitted by the Run Contract."
        )
    else:
        commit_policy = (
            "This Run does not require a task commit; do not create one solely to "
            "satisfy the Run."
        )
    return (
        "Implement the structured task below inside the governed Run scope.\n\n"
        f"{brief.rstrip()}\n\n"
        f"Write your full report to {report_path}:\n"
        "The report must state the implementation result and exact validation evidence.\n"
        f"{commit_policy}"
    )


def _render_recovery_prompt(contract: Any, prior: RunResult) -> str:
    report_path = contract.task.report_path.expanduser().resolve(strict=False)
    obligations = [
        f"write or update the Implementer Report at {report_path}",
        "run the required validation and emit conservative passing evidence",
        "preserve the exact Run scope and commit only permitted task files",
    ]
    return (
        "Continue the existing Command Code Session for the same governed Run.\n"
        f"The prior primary condition was {prior.primary_blocker.code if prior.primary_blocker else 'INCOMPLETE'}.\n"
        "Complete only these remaining obligations:\n"
        + "\n".join(f"- {item}" for item in obligations)
        + "\nDo not change the Run Contract, scope, model, or policy."
    )


def _atomic_json_write(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _file_sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _looks_deployed_path(path: Path) -> bool:
    lowered = str(path).casefold().replace("/", "\\")
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


def _is_command_result(event: CmdcEvent) -> bool:
    event_type = event.type.casefold().replace("-", "_")
    tool = (event.tool or "").casefold().replace("-", "_")
    return event_type in _RESULT_TYPES or (
        event_type in {"command", "exec", "shell", "shell_command"}
        and tool in _SHELL_TOOLS
    )


def _is_test_command(command: str) -> bool:
    tokens = _command_tokens(command)
    if not tokens:
        return False
    first = _basename(tokens[0])
    lowered = [token.casefold() for token in tokens]
    if first in {"pytest", "py.test"}:
        return True
    if first in {"python", "python3", "py"} and len(lowered) >= 3:
        return lowered[1] in {"-m", "--module"} and _basename(lowered[2]) in {
            "pytest",
            "py.test",
        }
    if first in {"npm", "yarn", "pnpm"}:
        return len(lowered) >= 2 and (
            lowered[1] == "test"
            or len(lowered) >= 3 and lowered[1] == "run" and lowered[2] == "test"
        )
    if first in {"go", "cargo", "dotnet"}:
        return len(lowered) >= 2 and lowered[1] == "test"
    if first in {"mvn", "mvnw", "gradle", "gradlew"}:
        return "test" in lowered[1:]
    return False


def _is_validation_command(command: str) -> bool:
    tokens = _command_tokens(command)
    if not tokens:
        return False
    first = _basename(tokens[0])
    lowered = [token.casefold() for token in tokens]
    if _is_test_command(command):
        return True
    if first in {"ruff", "mypy", "tsc"}:
        return True
    if first == "go" and len(lowered) > 1 and lowered[1] == "build":
        return True
    if first == "cargo" and len(lowered) > 1 and lowered[1] == "check":
        return True
    if first == "dotnet" and len(lowered) > 1 and lowered[1] == "build":
        return True
    if first in {"npm", "yarn", "pnpm"} and len(lowered) >= 3:
        return lowered[1] == "run" and lowered[2] in {"build", "lint", "typecheck"}
    if first in {"mvn", "mvnw", "gradle", "gradlew"}:
        return any(token in {"verify", "check", "build", "lint"} for token in lowered[1:])
    return False


def _parse_test_summary(
    stdout: str,
    stderr: str,
) -> tuple[str, int | None, int] | None:
    summary = stdout.strip() or stderr.strip()
    combined = "\n".join(value for value in (stdout, stderr) if value)
    if not summary or not combined.strip():
        return None
    failures = [int(match.group("count")) for pattern in _FAILURE_PATTERNS for match in pattern.finditer(combined)]
    failed = max(failures, default=0)
    passed_matches = list(_PASSED_PATTERN.finditer(combined))
    passed_matches.extend(_PASSED_COLON_PATTERN.finditer(combined))
    passed = max((int(match.group("count")) for match in passed_matches), default=None)
    maven = _MAVEN_PATTERN.search(combined)
    if maven:
        total = int(maven.group("total"))
        failed = max(failed, int(maven.group("failed")) + int(maven.group("errors")))
        passed = total - int(maven.group("failed")) - int(maven.group("errors"))
    total_match = _TOTAL_PATTERN.search(combined)
    if passed is None and total_match:
        passed = max(int(total_match.group("count")) - failed, 0)
    completed_match = _COMPLETED_PATTERN.search(combined)
    if passed is None and completed_match:
        passed = max(int(completed_match.group("count")) - failed, 0)
    if passed is None:
        if not _SUCCESS_PATTERN.search(combined):
            return None
    return summary, passed, failed


def _command_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return command.split()


def _basename(value: str) -> str:
    return value.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1].casefold()


def _mapping_value(value: Mapping[str, object], key: str) -> object:
    return value.get(key)
