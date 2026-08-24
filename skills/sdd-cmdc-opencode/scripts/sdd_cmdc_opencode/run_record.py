"""Durable, schema-validated Run Contract and append-only Run Record."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import unicodedata
from types import MappingProxyType
from typing import Any


SCHEMA_VERSION = 1
_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_WILDCARDS = frozenset("*?[]")


class RunRecordError(ValueError):
    """A Run Contract, artifact, or workspace record is invalid."""


class RunStatus(str, Enum):
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class Blocker:
    code: str
    phase: str
    message: str


@dataclass(frozen=True)
class TestEvidence:
    command: str
    exit_code: int
    summary: str
    passed: int | None
    failed: int
    event_sequence: int


@dataclass(frozen=True)
class RecoveryEvidence:
    attempt: int
    trigger: str
    session_id: str
    checkpoint_sequence: int
    same_session: bool


@dataclass(frozen=True)
class RunLineage:
    kind: str
    parent_run_id: str
    parent_review_id: str
    parent_review_result_sha256: str
    parent_brief_sha256: str
    finding_ids: tuple[str, ...]
    findings_sha256: str


@dataclass(frozen=True)
class TaskContract:
    id: int
    heading: str
    brief_path: Path
    brief_sha256: str
    report_path: Path


@dataclass(frozen=True)
class PlanProvenance:
    source_path: Path
    source_repository: Path
    source_branch: str
    source_head: str
    sha256: str


@dataclass(frozen=True)
class WorkspaceContract:
    repo_root: Path
    base_head: str
    branch: str
    baseline_status: Mapping[str, object]


@dataclass(frozen=True)
class ScopeContract:
    allowed_paths: tuple[str, ...]
    denied_paths: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionPolicy:
    backend: str
    model: str
    max_turns: int
    wall_timeout_seconds: int
    stall_timeout_seconds: int
    progress_deadline_turns: int
    max_resumes: int
    no_skills: bool
    yolo: bool


@dataclass(frozen=True)
class SuccessPolicy:
    require_commit: bool
    require_report: bool
    require_test_evidence: bool


@dataclass(frozen=True)
class ReviewPolicy:
    auto_fix_rounds: int


@dataclass(frozen=True)
class RunContract:
    schema_version: int
    run_id: str
    task: TaskContract
    plan: PlanProvenance
    workspace: WorkspaceContract
    scope: ScopeContract
    execution: ExecutionPolicy
    success: SuccessPolicy
    review: ReviewPolicy
    lineage: RunLineage | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "RunContract":
        if not isinstance(value, Mapping):
            raise RunRecordError("Run Contract must be a JSON object")
        _exact_keys(
            value,
            {
                "schema_version",
                "run_id",
                "task",
                "plan",
                "workspace",
                "scope",
                "execution",
                "success",
                "review",
            },
            {"lineage"},
            "Run Contract",
        )
        schema_version = _int(value["schema_version"], "schema_version")
        if schema_version != SCHEMA_VERSION:
            raise RunRecordError(f"unsupported Run Contract schema: {schema_version}")
        run_id = _string(value["run_id"], "run_id")
        if not _RUN_ID_RE.fullmatch(run_id):
            raise RunRecordError("run_id contains unsafe characters")

        task_mapping = _mapping(value["task"], "task")
        _exact_keys(
            task_mapping,
            {"id", "heading", "brief_path", "brief_sha256", "report_path"},
            set(),
            "task",
        )
        task_id = _int(task_mapping["id"], "task.id")
        if task_id < 1:
            raise RunRecordError("task.id must be positive")
        task_heading = _string(task_mapping["heading"], "task.heading")
        if not task_heading.strip():
            raise RunRecordError("task.heading must not be empty")
        task_brief_hash = _sha256_value(task_mapping["brief_sha256"], "task.brief_sha256")
        task_brief_path = _path(task_mapping["brief_path"], "task.brief_path")
        task_report_path = _path(task_mapping["report_path"], "task.report_path")

        plan_mapping = _mapping(value["plan"], "plan")
        _exact_keys(
            plan_mapping,
            {"source_path", "source_repository", "source_branch", "source_head", "sha256"},
            set(),
            "plan",
        )
        source_path = _absolute_path(plan_mapping["source_path"], "plan.source_path")
        source_repository = _absolute_path(
            plan_mapping["source_repository"], "plan.source_repository"
        )
        source_branch = _string(plan_mapping["source_branch"], "plan.source_branch")
        if not source_branch.strip():
            raise RunRecordError("plan.source_branch must not be empty")
        source_head = _commit_value(plan_mapping["source_head"], "plan.source_head")
        plan_hash = _sha256_value(plan_mapping["sha256"], "plan.sha256")

        workspace_mapping = _mapping(value["workspace"], "workspace")
        _exact_keys(
            workspace_mapping,
            {"repo_root", "base_head", "branch", "baseline_status"},
            set(),
            "workspace",
        )
        repo_root = _absolute_path(workspace_mapping["repo_root"], "workspace.repo_root")
        base_head = _commit_value(workspace_mapping["base_head"], "workspace.base_head")
        branch = _string(workspace_mapping["branch"], "workspace.branch")
        if not branch.strip():
            raise RunRecordError("workspace.branch must not be empty")
        baseline_status = _json_object(workspace_mapping["baseline_status"], "workspace.baseline_status")

        scope_mapping = _mapping(value["scope"], "scope")
        _exact_keys(scope_mapping, {"allowed_paths", "denied_paths"}, set(), "scope")
        allowed_paths = _path_list(scope_mapping["allowed_paths"], "scope.allowed_paths")
        denied_paths = _path_list(scope_mapping["denied_paths"], "scope.denied_paths")

        execution_mapping = _mapping(value["execution"], "execution")
        _exact_keys(
            execution_mapping,
            {
                "backend",
                "model",
                "max_turns",
                "wall_timeout_seconds",
                "stall_timeout_seconds",
                "progress_deadline_turns",
                "max_resumes",
                "no_skills",
                "yolo",
            },
            set(),
            "execution",
        )
        backend = _string(execution_mapping["backend"], "execution.backend")
        if backend != "cmdc-local":
            raise RunRecordError("execution.backend must be 'cmdc-local'")
        model = _string(execution_mapping["model"], "execution.model")
        if not model.strip():
            raise RunRecordError("execution.model must not be empty")
        max_turns = _int(execution_mapping["max_turns"], "execution.max_turns")
        wall_timeout = _int(
            execution_mapping["wall_timeout_seconds"],
            "execution.wall_timeout_seconds",
        )
        stall_timeout = _int(
            execution_mapping["stall_timeout_seconds"],
            "execution.stall_timeout_seconds",
        )
        progress_deadline = _int(
            execution_mapping["progress_deadline_turns"],
            "execution.progress_deadline_turns",
        )
        max_resumes = _int(execution_mapping["max_resumes"], "execution.max_resumes")
        if max_turns < 1:
            raise RunRecordError("execution.max_turns must be at least one")
        if wall_timeout < 0 or stall_timeout < 0:
            raise RunRecordError("execution timeouts must not be negative")
        if max_resumes < 0:
            raise RunRecordError("execution.max_resumes must not be negative")
        if progress_deadline < 1 or progress_deadline > max_turns:
            raise RunRecordError(
                "execution.progress_deadline_turns must be between one and max_turns"
            )
        no_skills = _bool(execution_mapping["no_skills"], "execution.no_skills")
        yolo = _bool(execution_mapping["yolo"], "execution.yolo")
        if not yolo:
            raise RunRecordError(
                "execution.yolo cannot be false; the governed launcher always "
                "runs with --yolo because CMDc writes are part of the worker "
                "contract"
            )

        success_mapping = _mapping(value["success"], "success")
        _exact_keys(
            success_mapping,
            {"require_commit", "require_report", "require_test_evidence"},
            set(),
            "success",
        )
        success = SuccessPolicy(
            require_commit=_bool(success_mapping["require_commit"], "success.require_commit"),
            require_report=_bool(success_mapping["require_report"], "success.require_report"),
            require_test_evidence=_bool(
                success_mapping["require_test_evidence"],
                "success.require_test_evidence",
            ),
        )

        review_mapping = _mapping(value["review"], "review")
        _exact_keys(review_mapping, {"auto_fix_rounds"}, set(), "review")
        auto_fix_rounds = _int(review_mapping["auto_fix_rounds"], "review.auto_fix_rounds")
        if auto_fix_rounds < 0:
            raise RunRecordError("review.auto_fix_rounds must not be negative")

        lineage = _parse_lineage(value.get("lineage")) if "lineage" in value else None
        contract = cls(
            schema_version=schema_version,
            run_id=run_id,
            task=TaskContract(
                id=task_id,
                heading=task_heading,
                brief_path=task_brief_path,
                brief_sha256=task_brief_hash,
                report_path=task_report_path,
            ),
            plan=PlanProvenance(
                source_path=source_path,
                source_repository=source_repository,
                source_branch=source_branch,
                source_head=source_head,
                sha256=plan_hash,
            ),
            workspace=WorkspaceContract(
                repo_root=repo_root,
                base_head=base_head,
                branch=branch,
                baseline_status=MappingProxyType(dict(baseline_status)),
            ),
            scope=ScopeContract(allowed_paths=allowed_paths, denied_paths=denied_paths),
            execution=ExecutionPolicy(
                backend=backend,
                model=model,
                max_turns=max_turns,
                wall_timeout_seconds=wall_timeout,
                stall_timeout_seconds=stall_timeout,
                progress_deadline_turns=progress_deadline,
                max_resumes=max_resumes,
                no_skills=no_skills,
                yolo=yolo,
            ),
            success=success,
            review=ReviewPolicy(auto_fix_rounds=auto_fix_rounds),
            lineage=lineage,
        )
        _validate_provenance(contract)
        return contract

    @classmethod
    def load(cls, path: Path) -> "RunContract":
        path = Path(path)
        try:
            with path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)
        except (OSError, json.JSONDecodeError) as error:
            raise RunRecordError(f"could not load Run Contract: {path}") from error
        return cls.from_mapping(value)

    @property
    def contract_sha256(self) -> str:
        return _sha256_bytes(_canonical_json(self.to_mapping()))

    def to_mapping(self) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "task": {
                "id": self.task.id,
                "heading": self.task.heading,
                "brief_path": _path_string(self.task.brief_path),
                "brief_sha256": self.task.brief_sha256,
                "report_path": _path_string(self.task.report_path),
            },
            "plan": {
                "source_path": _path_string(self.plan.source_path),
                "source_repository": _path_string(self.plan.source_repository),
                "source_branch": self.plan.source_branch,
                "source_head": self.plan.source_head,
                "sha256": self.plan.sha256,
            },
            "workspace": {
                "repo_root": _path_string(self.workspace.repo_root),
                "base_head": self.workspace.base_head,
                "branch": self.workspace.branch,
                "baseline_status": dict(self.workspace.baseline_status),
            },
            "scope": {
                "allowed_paths": list(self.scope.allowed_paths),
                "denied_paths": list(self.scope.denied_paths),
            },
            "execution": {
                "backend": self.execution.backend,
                "model": self.execution.model,
                "max_turns": self.execution.max_turns,
                "wall_timeout_seconds": self.execution.wall_timeout_seconds,
                "stall_timeout_seconds": self.execution.stall_timeout_seconds,
                "progress_deadline_turns": self.execution.progress_deadline_turns,
                "max_resumes": self.execution.max_resumes,
                "no_skills": self.execution.no_skills,
                "yolo": self.execution.yolo,
            },
            "success": {
                "require_commit": self.success.require_commit,
                "require_report": self.success.require_report,
                "require_test_evidence": self.success.require_test_evidence,
            },
            "review": {"auto_fix_rounds": self.review.auto_fix_rounds},
        }
        if self.lineage is not None:
            value["lineage"] = {
                "kind": self.lineage.kind,
                "parent_run_id": self.lineage.parent_run_id,
                "parent_review_id": self.lineage.parent_review_id,
                "parent_review_result_sha256": self.lineage.parent_review_result_sha256,
                "parent_brief_sha256": self.lineage.parent_brief_sha256,
                "finding_ids": list(self.lineage.finding_ids),
                "findings_sha256": self.lineage.findings_sha256,
            }
        return value


@dataclass(frozen=True)
class RunResult:
    schema_version: int
    run_id: str
    backend: str
    session_id: str | None
    status: RunStatus
    primary_blocker: Blocker | None
    secondary_blockers: tuple[Blocker, ...]
    base_head: str
    final_head: str
    scope_valid: bool
    violating_paths: tuple[str, ...]
    report_valid: bool
    test_evidence_valid: bool
    cleanup_verified: bool
    tests: tuple[TestEvidence, ...]
    recoveries: tuple[RecoveryEvidence, ...]
    artifact_hashes: Mapping[str, str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "RunResult":
        if not isinstance(value, Mapping):
            raise RunRecordError("Run Result must be a JSON object")
        required = {
            "schema_version",
            "run_id",
            "backend",
            "session_id",
            "status",
            "primary_blocker",
            "secondary_blockers",
            "base_head",
            "final_head",
            "scope_valid",
            "violating_paths",
            "report_valid",
            "test_evidence_valid",
            "cleanup_verified",
            "tests",
            "recoveries",
            "artifact_hashes",
        }
        _exact_keys(value, required, set(), "Run Result")
        schema_version = _int(value["schema_version"], "result.schema_version")
        if schema_version != SCHEMA_VERSION:
            raise RunRecordError("unsupported Run Result schema")
        backend = _string(value["backend"], "result.backend")
        if backend != "cmdc-local":
            raise RunRecordError("result.backend must be 'cmdc-local'")
        session_raw = value["session_id"]
        if session_raw is not None and not isinstance(session_raw, str):
            raise RunRecordError("result.session_id must be a string or null")
        blockers_raw = value["secondary_blockers"]
        if not isinstance(blockers_raw, list):
            raise RunRecordError("result.secondary_blockers must be a list")
        tests_raw = value["tests"]
        recoveries_raw = value["recoveries"]
        if not isinstance(tests_raw, list) or not isinstance(recoveries_raw, list):
            raise RunRecordError("result tests and recoveries must be lists")
        artifact_raw = _mapping(value["artifact_hashes"], "result.artifact_hashes")
        artifacts: dict[str, str] = {}
        for key, item in artifact_raw.items():
            artifacts[_string(key, "result artifact key")] = _string(
                item, f"result.artifact_hashes.{key}"
            )
        return cls(
            schema_version=schema_version,
            run_id=_string(value["run_id"], "result.run_id"),
            backend=backend,
            session_id=session_raw,
            status=_parse_run_status(value["status"]),
            primary_blocker=_parse_blocker(value["primary_blocker"], "result.primary_blocker"),
            secondary_blockers=tuple(
                _parse_blocker(item, "result.secondary_blocker") for item in blockers_raw
            ),
            base_head=_commit_value(value["base_head"], "result.base_head"),
            final_head=_commit_value(value["final_head"], "result.final_head"),
            scope_valid=_bool(value["scope_valid"], "result.scope_valid"),
            violating_paths=tuple(
                _string(item, "result.violating_paths[]") for item in _list(value["violating_paths"], "result.violating_paths")
            ),
            report_valid=_bool(value["report_valid"], "result.report_valid"),
            test_evidence_valid=_bool(value["test_evidence_valid"], "result.test_evidence_valid"),
            cleanup_verified=_bool(value["cleanup_verified"], "result.cleanup_verified"),
            tests=tuple(_parse_test_evidence(item) for item in tests_raw),
            recoveries=tuple(_parse_recovery(item) for item in recoveries_raw),
            artifact_hashes=MappingProxyType(artifacts),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "backend": self.backend,
            "session_id": self.session_id,
            "status": self.status.value,
            "primary_blocker": _blocker_mapping(self.primary_blocker),
            "secondary_blockers": [_blocker_mapping(item) for item in self.secondary_blockers],
            "base_head": self.base_head,
            "final_head": self.final_head,
            "scope_valid": self.scope_valid,
            "violating_paths": list(self.violating_paths),
            "report_valid": self.report_valid,
            "test_evidence_valid": self.test_evidence_valid,
            "cleanup_verified": self.cleanup_verified,
            "tests": [
                {
                    "command": item.command,
                    "exit_code": item.exit_code,
                    "summary": item.summary,
                    "passed": item.passed,
                    "failed": item.failed,
                    "event_sequence": item.event_sequence,
                }
                for item in self.tests
            ],
            "recoveries": [
                {
                    "attempt": item.attempt,
                    "trigger": item.trigger,
                    "session_id": item.session_id,
                    "checkpoint_sequence": item.checkpoint_sequence,
                    "same_session": item.same_session,
                }
                for item in self.recoveries
            ],
            "artifact_hashes": dict(self.artifact_hashes),
        }


class RunRecord:
    """Own one immutable contract and its append-only transaction streams."""

    def __init__(self, run_dir: Path, contract: RunContract) -> None:
        self._run_dir = Path(run_dir)
        self._contract = contract
        self._lock = threading.RLock()

    @classmethod
    def create(cls, run_dir: Path, contract: RunContract) -> "RunRecord":
        if not isinstance(contract, RunContract):
            raise RunRecordError("RunRecord.create requires a RunContract")
        run_dir = Path(run_dir)
        if run_dir.name != contract.run_id:
            raise RunRecordError("Run directory name must equal contract.run_id")
        run_dir.mkdir(parents=True, exist_ok=True)
        contract_path = run_dir / "contract.json"
        contract_bytes = _pretty_json(contract.to_mapping())
        try:
            _exclusive_write(contract_path, contract_bytes)
        except FileExistsError:
            raise
        _exclusive_write(run_dir / "events.jsonl", b"")
        _exclusive_write(run_dir / "checkpoints.jsonl", b"")
        _exclusive_write(
            run_dir / "scope-contract.json",
            _pretty_json(
                {
                    "allowed_paths": list(contract.scope.allowed_paths),
                    "denied_paths": list(contract.scope.denied_paths),
                }
            ),
        )
        return cls(run_dir, contract)

    @classmethod
    def load(cls, run_dir: Path) -> "RunRecord":
        run_dir = Path(run_dir)
        contract_path = run_dir / "contract.json"
        if not contract_path.is_file():
            raise RunRecordError(f"Run Contract is missing: {contract_path}")
        contract = RunContract.load(contract_path)
        if run_dir.name != contract.run_id:
            raise RunRecordError("Run directory does not match contract.run_id")
        return cls(run_dir, contract)

    @classmethod
    def locate(cls, repo_root: Path, run_id: str) -> "RunRecord":
        repo_root = Path(repo_root).resolve()
        if not _RUN_ID_RE.fullmatch(run_id):
            raise RunRecordError("run_id contains unsafe characters")
        workspace_root = repo_root / ".superpowers" / "sdd"
        matches: list[Path] = []
        if workspace_root.is_dir():
            for plan_workspace in workspace_root.iterdir():
                candidate = plan_workspace / "runs" / run_id
                try:
                    candidate.resolve().relative_to(repo_root)
                except ValueError:
                    continue
                if candidate.is_dir() and (candidate / "contract.json").is_file():
                    matches.append(candidate)
        if not matches:
            raise RunRecordError(f"Run not found in repository: {run_id}")
        if len(matches) != 1:
            raise RunRecordError(f"multiple Runs found for run_id: {run_id}")
        return cls.load(matches[0])

    @property
    def contract(self) -> RunContract:
        return self._contract

    @property
    def contract_sha256(self) -> str:
        return self._contract.contract_sha256

    @property
    def run_dir(self) -> Path:
        return self._run_dir

    def append_event(self, event: dict[str, object]) -> int:
        return self._append(self._run_dir / "events.jsonl", event, "event")

    def append_events(self, events: Iterable[dict[str, object]]) -> tuple[int, ...]:
        return self._append_many(self._run_dir / "events.jsonl", events, "event")

    def append_checkpoint(self, checkpoint: dict[str, object]) -> int:
        return self._append(self._run_dir / "checkpoints.jsonl", checkpoint, "checkpoint")

    def read_events(self) -> tuple[dict[str, object], ...]:
        return self._read_stream(self._run_dir / "events.jsonl", "event")

    def read_checkpoints(self) -> tuple[dict[str, object], ...]:
        return self._read_stream(self._run_dir / "checkpoints.jsonl", "checkpoint")

    def latest_checkpoint(self) -> dict[str, object] | None:
        checkpoints = self.read_checkpoints()
        return dict(checkpoints[-1]) if checkpoints else None

    def _read_stream(self, path: Path, kind: str) -> tuple[dict[str, object], ...]:
        if not path.is_file():
            raise RunRecordError(f"{kind} stream is missing: {path}")
        values: list[dict[str, object]] = []
        expected_sequence = 1
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as error:
            raise RunRecordError(f"could not read {kind} stream: {path}") from error
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise RunRecordError(
                    f"invalid {kind} JSON at {path}:{line_number}"
                ) from error
            if not isinstance(value, dict):
                raise RunRecordError(f"{kind} record must be a JSON object")
            if value.get("run_id") != self._contract.run_id:
                raise RunRecordError(f"{kind} record has foreign run_id")
            if value.get("contract_sha256") != self.contract_sha256:
                raise RunRecordError(f"{kind} record has foreign contract hash")
            if value.get("sequence") != expected_sequence:
                raise RunRecordError(f"{kind} sequence is not monotonic")
            values.append(value)
            expected_sequence += 1
        return tuple(values)

    def _append(self, path: Path, value: dict[str, object], kind: str) -> int:
        return self._append_many(path, (value,), kind)[0]

    def _append_many(
        self,
        path: Path,
        values: Iterable[dict[str, object]],
        kind: str,
    ) -> tuple[int, ...]:
        pending = tuple(values)
        if not pending:
            return ()
        with self._lock:
            next_sequence = _last_sequence(path) + 1
            payloads: list[bytes] = []
            sequences: list[int] = []
            for value in pending:
                if not isinstance(value, dict):
                    raise RunRecordError(f"{kind} must be a JSON object")
                supplied_run = value.get("run_id")
                if supplied_run is not None and supplied_run != self._contract.run_id:
                    raise RunRecordError(f"{kind} run_id does not belong to this Run")
                supplied_hash = value.get("contract_sha256")
                if supplied_hash is not None and supplied_hash != self.contract_sha256:
                    raise RunRecordError(f"{kind} contract hash does not belong to this Run")
                supplied_sequence = value.get("sequence")
                if supplied_sequence is not None and supplied_sequence != next_sequence:
                    raise RunRecordError(f"{kind} sequence is not monotonic")
                record = dict(value)
                record["sequence"] = next_sequence
                record["run_id"] = self._contract.run_id
                record["contract_sha256"] = self.contract_sha256
                record["timestamp"] = record.get("timestamp") or _utc_timestamp()
                payloads.append(_canonical_json(record) + b"\n")
                sequences.append(next_sequence)
                next_sequence += 1
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("ab") as handle:
                handle.write(b"".join(payloads))
                handle.flush()
                os.fsync(handle.fileno())
            return tuple(sequences)

    def write_result(self, result: RunResult) -> None:
        if not isinstance(result, RunResult):
            raise RunRecordError("RunRecord.write_result requires a RunResult")
        if result.run_id != self._contract.run_id:
            raise RunRecordError("Run Result run_id does not belong to this Run")
        if result.backend != self._contract.execution.backend:
            raise RunRecordError("Run Result backend does not match its Contract")
        _atomic_write(self._run_dir / "result.json", _pretty_json(result.to_mapping()))

    def read_result(self) -> RunResult | None:
        path = self._run_dir / "result.json"
        if not path.is_file():
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)
        except (OSError, json.JSONDecodeError) as error:
            raise RunRecordError(f"could not load Run Result: {path}") from error
        result = RunResult.from_mapping(value)
        if result.run_id != self._contract.run_id:
            raise RunRecordError("Run Result run_id does not belong to its Contract")
        return result


def workspace_fingerprint(
    repo_root: Path, owner_run_dir: Path | None = None
) -> dict[str, object]:
    """Capture exact Git state and evidence for every changed path.

    Only paths at or below the *explicit* lifecycle owner — the run directory
    the caller proves it executes — are excluded, together with the untracked
    directory containers git collapses them into. The owner is an authority
    of the running lifecycle, never a pattern: a structurally similar sibling
    run (``.superpowers/sdd/<workspace>/runs/<run_id>/``) is NOT owned by this
    Run and stays visible in the evidence and the raw status hash. Without an
    explicit owner, no path is hidden at all.

    A container is excluded only when every path below it is a proven owned
    artifact of the explicit owner; anything else keeps the container visible
    so unauthorized content fails closed. Tracked files inside the plan
    workspace remain fingerprintable and are never excluded.
    """

    repo_root = Path(repo_root).resolve()
    owner = _validate_run_owner(repo_root, owner_run_dir)
    head = _git_text(repo_root, "rev-parse", "HEAD")
    branch = _git_text(repo_root, "branch", "--show-current")
    # Expand untracked files instead of accepting Git's default directory
    # collapse. A pre-existing mixed untracked container (for example
    # ``.superpowers/``) must not hide a new permitted artifact from the
    # progress fingerprint.
    raw_status = _git_bytes(
        repo_root,
        "status",
        "--porcelain=v2",
        "--untracked-files=all",
        "-z",
    )
    entries = _parse_status(raw_status)
    owned_paths = _owned_run_artifact_paths(repo_root, entries, owner)
    filtered_status = _filter_owned_status_tokens(raw_status, owned_paths)
    paths: dict[str, dict[str, object]] = {}
    for entry in entries:
        path = entry["path"]
        if path in owned_paths:
            continue
        paths[path] = _path_fingerprint(repo_root, path, entry["status"], entry["untracked"])
        renamed_from = entry.get("renamed_from")
        if isinstance(renamed_from, str):
            old_evidence = _path_fingerprint(
                repo_root,
                renamed_from,
                entry["status"],
                False,
            )
            old_evidence["renamed_to"] = path
            paths[renamed_from] = old_evidence
            paths[path]["renamed_from"] = renamed_from
    return {
        "head": head,
        "branch": branch,
        "status_sha256": _sha256_bytes(filtered_status),
        "paths": {key: paths[key] for key in sorted(paths)},
    }


def _validate_run_owner(
    repo_root: Path, owner_run_dir: Path | None
) -> Path | None:
    """Validate the explicit Run owner and return its canonical path.

    The owner must resolve inside the repository root, must be a repository
    run directory (``.superpowers/sdd/<plan-workspace>/runs/<run_id>`` with
    the safe Run-ID grammar and no nested ``runs``), and must contain an
    immutable ``contract.json`` so the authority is the lifecycle's own
    record. Any other owner — outside the repository, ambiguous, or another
    Run — raises ``RunRecordError`` and never silently hides a path.
    """
    if owner_run_dir is None:
        return None
    root = repo_root.resolve()
    owner = Path(owner_run_dir).expanduser().resolve(strict=False)
    try:
        relative = owner.relative_to(root)
    except ValueError as error:
        raise RunRecordError(
            f"Run owner is outside the repository: {owner}"
        ) from error
    parts = relative.parts
    if (
        len(parts) < 4
        or parts[0] != ".superpowers"
        or parts[1] != "sdd"
        or parts[-2] != "runs"
    ):
        raise RunRecordError(
            f"Run owner is not a repository run directory: {owner}"
        )
    if not _RUN_ID_RE.fullmatch(parts[-1]):
        raise RunRecordError(f"Run owner has an unsafe run-id: {parts[-1]}")
    if "runs" in parts[:-2]:
        raise RunRecordError(f"Run owner is ambiguous: {owner}")
    if not (owner / "contract.json").is_file():
        raise RunRecordError(f"Run owner has no immutable contract: {owner}")
    return owner


def _owned_run_artifact_paths(
    repo_root: Path,
    entries: list[dict[str, object]],
    owner_run_dir: Path | None,
) -> set[str]:
    """Return the untracked status entries that are proven lifecycle-owned.

    Only untracked paths at or below the explicit owner's run directory
    qualify; an untracked *container* directory (the ``runs/`` subtree git
    collapses into one entry) qualifies only when every path below it is a
    proven owned artifact of that same owner. Without an explicit owner
    nothing is owned, so every run — including forged siblings — stays
    visible and fails closed.
    """
    if owner_run_dir is None:
        return set()
    owned: set[str] = set()
    owner_relative = owner_run_dir.relative_to(Path(repo_root).resolve()).as_posix()
    for entry in entries:
        if not bool(entry.get("untracked")):
            continue
        path = entry["path"]
        if not isinstance(path, str):
            continue
        if _is_owned_run_artifact_path(owner_relative, path):
            owned.add(path)
            continue
        if path.endswith("/") and _untracked_container_is_owned(
            repo_root, path, owner_relative
        ):
            owned.add(path)
    return owned


def _is_owned_run_artifact_path(owner_relative: str, relative_path: str) -> bool:
    """Return whether an untracked path belongs to the explicit Run owner.

    The path must be strictly at or below the owner's canonical run directory
    (the owner itself was already validated against the repository root and
    the safe run-directory format). Structural lookalikes under other
    workspaces or run IDs never match the explicit owner and stay visible.
    """
    normalized = unicodedata.normalize("NFC", relative_path.replace("\\", "/"))
    if normalized == owner_relative or normalized.startswith(owner_relative + "/"):
        return True
    owner_key = _path_key(owner_relative)
    path_key = _path_key(normalized)
    if path_key == owner_key or path_key.startswith(owner_key + "/"):
        return True
    return False


def _path_key(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value.replace("\\", "/")).rstrip("/")
    return normalized.casefold() if os.name == "nt" else normalized


def _untracked_container_is_owned(
    repo_root: Path,
    container_relative: str,
    owner_relative: str,
) -> bool:
    """Return whether an untracked directory container holds only owned artifacts.

    Git collapses a fully untracked subtree into a single container entry (for
    example ``.superpowers/sdd/plan/runs/``). The container is excluded only
    when every path below it is a proven artifact of the explicit owner; any
    foreign content — a rogue file, a foreign run, a sibling workspace — keeps
    the container visible so the mismatch fails closed.
    """
    root = Path(repo_root).resolve()
    container = root / Path(container_relative)
    try:
        container = container.resolve(strict=True)
    except OSError:
        return False
    for current_dir, dirs, files in os.walk(container):
        relative = Path(current_dir).relative_to(root)
        for name in (*dirs, *files):
            if not _is_owned_run_artifact_path(
                owner_relative,
                (relative / name).as_posix(),
            ):
                return False
    return True


def _filter_owned_status_tokens(raw_status: bytes, owned_paths: set[str]) -> bytes:
    """Drop the owned untracked entries from the raw porcelain stream.

    The filtered stream is byte-identical to the raw stream when nothing is
    owned, so Contract-time baselines (captured before the Run artifacts
    existed) hash unchanged; the filtered stream is canonical for both the
    workspace fingerprint and the reconciled run-artifact fingerprint.
    """
    kept: list[bytes] = []
    for token in raw_status.split(b"\0"):
        if not token:
            continue
        if token.startswith(b"? "):
            if _canonical_git_path(token[2:]) in owned_paths:
                continue
        kept.append(token)
    return b"\0".join(kept) + b"\0"


def run_artifact_fingerprint(
    repo_root: Path, run_dir: Path, baseline: Mapping[str, object]
) -> Mapping[str, object]:
    """Return the fingerprint the workspace must have after the owned artifacts.

    ``RunRecord.create`` writes ``contract.json``, ``events.jsonl``,
    ``checkpoints.jsonl``, and ``scope-contract.json`` into the run directory
    after the Contract baseline was captured. The reconciled fingerprint
    captures the current tree with the explicit ``run_dir`` owner (so only
    this Run's artifacts are excluded) and merges the current path evidence
    over the immutable Contract-time baseline: every baseline path stays
    authoritative when it vanished or changed (deletions and modifications
    stay visible and fail closed), and every current path outside the owned
    run area is kept verbatim. The status hash is the immutable Contract-time
    baseline value, so any external post-contract change — including a forged
    sibling run, which never matches this owner — still makes the current
    fingerprint differ and fails closed.
    """
    current = workspace_fingerprint(repo_root, owner_run_dir=run_dir)
    baseline_paths = baseline.get("paths")
    if not isinstance(baseline_paths, Mapping):
        raise RunRecordError("baseline fingerprint has no path evidence")
    if not isinstance(baseline.get("status_sha256"), str):
        raise RunRecordError("baseline fingerprint has no status hash")
    run_relative = Path(run_dir).resolve().relative_to(Path(repo_root).resolve())
    owned_prefix = tuple(Path(".superpowers", "sdd").parts)
    if not run_relative.parts[:2] == owned_prefix:
        raise RunRecordError("Run directory is outside the owned plan workspace")
    merged = dict(baseline_paths)
    for raw_path, evidence in current.get("paths", {}).items():
        if not isinstance(raw_path, str) or not isinstance(evidence, Mapping):
            raise RunRecordError("current fingerprint contains malformed path evidence")
        merged[raw_path] = evidence
    return {
        "head": current.get("head"),
        "branch": current.get("branch"),
        "status_sha256": baseline.get("status_sha256"),
        "paths": {key: merged[key] for key in sorted(merged)},
    }


def _validate_provenance(contract: RunContract) -> None:
    repo_root = contract.workspace.repo_root.resolve(strict=False)
    if not repo_root.is_dir():
        raise RunRecordError(f"workspace.repo_root does not exist: {repo_root}")
    for name, path in (
        ("task.brief_path", contract.task.brief_path),
        ("task.report_path", contract.task.report_path),
    ):
        resolved = _resolve_path(path, repo_root)
        try:
            resolved.relative_to(repo_root)
        except ValueError as error:
            raise RunRecordError(f"{name} is outside workspace.repo_root") from error

    source_repo = contract.plan.source_repository.resolve(strict=False)
    source_path = contract.plan.source_path.resolve(strict=False)
    if not source_repo.is_dir():
        raise RunRecordError(f"plan.source_repository does not exist: {source_repo}")
    try:
        source_path.relative_to(source_repo)
    except ValueError as error:
        raise RunRecordError("plan.source_path is outside plan.source_repository") from error
    if not source_path.is_file():
        raise RunRecordError(f"plan.source_path does not exist: {source_path}")
    if _sha256_file(source_path) != contract.plan.sha256.lower():
        raise RunRecordError("plan source file SHA-256 does not match the Contract")
    actual_root = Path(_git_text(source_repo, "rev-parse", "--show-toplevel")).resolve()
    if actual_root != source_repo:
        raise RunRecordError("plan.source_repository is not the Git repository root")
    resolved_source_head = _git_text(
        source_repo,
        "rev-parse",
        "--verify",
        f"{contract.plan.source_head}^{{commit}}",
    )
    if resolved_source_head.casefold() != contract.plan.source_head.casefold():
        raise RunRecordError("plan.source_head does not resolve to the recorded commit")

    brief_path = _resolve_path(contract.task.brief_path, repo_root)
    if not brief_path.is_file():
        raise RunRecordError(f"task.brief_path does not exist: {brief_path}")
    if _sha256_file(brief_path) != contract.task.brief_sha256.lower():
        raise RunRecordError("task brief SHA-256 does not match the Contract")
    _verify_task_heading_and_brief(contract, source_path, brief_path)


def _verify_task_heading_and_brief(
    contract: RunContract,
    source_path: Path,
    brief_path: Path,
) -> None:
    helper_path = Path(__file__).resolve().parents[1] / "task-brief.py"
    if not helper_path.is_file():
        raise RunRecordError("task-brief.py is required for plan provenance verification")
    spec = importlib.util.spec_from_file_location("_run_record_task_brief", helper_path)
    if spec is None or spec.loader is None:
        raise RunRecordError("could not load task-brief.py for plan provenance verification")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    try:
        with source_path.open("r", encoding="utf-8", newline="") as handle:
            plan_text = handle.read()
        heading, body = helper.extract_task(plan_text, contract.task.id)
    except Exception as error:
        raise RunRecordError("could not extract the Contract task from the source plan") from error
    normalized_heading = re.sub(r"^#{1,6}[ \t]+", "", heading)
    if normalized_heading != contract.task.heading:
        raise RunRecordError("task heading does not match the source plan")
    source_brief = (heading + "\n" + body).encode("utf-8")
    source_brief_normalized = source_brief.replace(b"\r\n", b"\n")
    source_brief_hash = _sha256_bytes(source_brief_normalized)
    if contract.lineage is None:
        try:
            brief_bytes = brief_path.read_bytes()
        except OSError as error:
            raise RunRecordError("could not read the task brief") from error
        if brief_bytes.replace(b"\r\n", b"\n") != source_brief_normalized:
            raise RunRecordError("task brief content does not match the extracted source task")
    else:
        if contract.lineage.parent_brief_sha256.lower() != source_brief_hash:
            raise RunRecordError("fix-round parent brief hash does not match the source task")


def _parse_lineage(value: object) -> RunLineage:
    data = _mapping(value, "lineage")
    _exact_keys(
        data,
        {
            "kind",
            "parent_run_id",
            "parent_review_id",
            "parent_review_result_sha256",
            "parent_brief_sha256",
            "finding_ids",
            "findings_sha256",
        },
        set(),
        "lineage",
    )
    kind = _string(data["kind"], "lineage.kind")
    if kind != "fix-round":
        raise RunRecordError("lineage.kind must be 'fix-round'")
    parent_run_id = _string(data["parent_run_id"], "lineage.parent_run_id")
    parent_review_id = _string(data["parent_review_id"], "lineage.parent_review_id")
    if not parent_run_id or not parent_review_id:
        raise RunRecordError("lineage parent identifiers must not be empty")
    parent_result_hash = _sha256_value(
        data["parent_review_result_sha256"],
        "lineage.parent_review_result_sha256",
    )
    parent_brief_hash = _sha256_value(data["parent_brief_sha256"], "lineage.parent_brief_sha256")
    raw_ids = _list(data["finding_ids"], "lineage.finding_ids")
    finding_ids = tuple(_string(item, "lineage.finding_ids[]") for item in raw_ids)
    if not finding_ids or len(set(finding_ids)) != len(finding_ids):
        raise RunRecordError("lineage.finding_ids must be unique and non-empty")
    findings_hash = _sha256_value(data["findings_sha256"], "lineage.findings_sha256")
    expected_hash = _sha256_bytes(_canonical_json(list(finding_ids)))
    if findings_hash.lower() != expected_hash:
        raise RunRecordError("lineage.findings_sha256 does not match finding_ids")
    return RunLineage(
        kind=kind,
        parent_run_id=parent_run_id,
        parent_review_id=parent_review_id,
        parent_review_result_sha256=parent_result_hash,
        parent_brief_sha256=parent_brief_hash,
        finding_ids=finding_ids,
        findings_sha256=findings_hash,
    )


def _parse_blocker(value: object, name: str) -> Blocker | None:
    if value is None:
        return None
    data = _mapping(value, name)
    _exact_keys(data, {"code", "phase", "message"}, set(), name)
    return Blocker(
        code=_string(data["code"], f"{name}.code"),
        phase=_string(data["phase"], f"{name}.phase"),
        message=_string(data["message"], f"{name}.message"),
    )


def _blocker_mapping(value: Blocker | None) -> dict[str, str] | None:
    if value is None:
        return None
    return {"code": value.code, "phase": value.phase, "message": value.message}


def _parse_test_evidence(value: object) -> TestEvidence:
    data = _mapping(value, "result.tests[]")
    _exact_keys(data, {"command", "exit_code", "summary", "passed", "failed", "event_sequence"}, set(), "result.tests[]")
    passed = data["passed"]
    if passed is not None:
        passed = _int(passed, "result.tests[].passed")
    return TestEvidence(
        command=_string(data["command"], "result.tests[].command"),
        exit_code=_int(data["exit_code"], "result.tests[].exit_code"),
        summary=_string(data["summary"], "result.tests[].summary"),
        passed=passed,
        failed=_int(data["failed"], "result.tests[].failed"),
        event_sequence=_int(data["event_sequence"], "result.tests[].event_sequence"),
    )


def _parse_recovery(value: object) -> RecoveryEvidence:
    data = _mapping(value, "result.recoveries[]")
    _exact_keys(
        data,
        {"attempt", "trigger", "session_id", "checkpoint_sequence", "same_session"},
        set(),
        "result.recoveries[]",
    )
    return RecoveryEvidence(
        attempt=_int(data["attempt"], "result.recoveries[].attempt"),
        trigger=_string(data["trigger"], "result.recoveries[].trigger"),
        session_id=_string(data["session_id"], "result.recoveries[].session_id"),
        checkpoint_sequence=_int(
            data["checkpoint_sequence"],
            "result.recoveries[].checkpoint_sequence",
        ),
        same_session=_bool(data["same_session"], "result.recoveries[].same_session"),
    )


def _parse_run_status(value: object) -> RunStatus:
    try:
        return RunStatus(_string(value, "result.status"))
    except ValueError as error:
        raise RunRecordError("result.status is not a known RunStatus") from error


def _parse_status(raw: bytes) -> list[dict[str, object]]:
    tokens = raw.split(b"\0")
    entries: list[dict[str, object]] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token:
            continue
        if token.startswith((b"1 ", b"2 ", b"u ")):
            split_count = 9 if token.startswith(b"2 ") else 8
            parts = token.split(b" ", split_count)
            if len(parts) <= split_count:
                raise RunRecordError("malformed Git porcelain v2 status entry")
            status = os.fsdecode(b" ".join(parts[:2]))
            path = _canonical_git_path(parts[split_count])
            entry: dict[str, object] = {
                "path": path,
                "status": status,
                "untracked": False,
            }
            if token.startswith(b"2 "):
                if index >= len(tokens):
                    raise RunRecordError("renamed Git status entry has no original path")
                entry["renamed_from"] = _canonical_git_path(tokens[index])
                index += 1
            entries.append(entry)
        elif token.startswith(b"? "):
            entries.append(
                {
                    "path": _canonical_git_path(token[2:]),
                    "status": "? ?",
                    "untracked": True,
                }
            )
        else:
            raise RunRecordError("unknown Git porcelain v2 status entry")
    return entries


def _path_fingerprint(
    repo_root: Path,
    relative_path: str,
    status: object,
    untracked: object,
) -> dict[str, object]:
    path = repo_root / Path(relative_path)
    if path.is_symlink():
        evidence: dict[str, object] = {
            "kind": "symlink",
            "target": os.readlink(path),
        }
    elif not path.exists():
        evidence = {"kind": "missing"}
    elif path.is_file():
        evidence = {
            "kind": "file",
            "sha256": _sha256_file(path),
            "size": path.stat().st_size,
        }
    elif path.is_dir():
        evidence = {"kind": "directory"}
    else:
        evidence = {"kind": "other"}
    evidence["status"] = status
    if bool(untracked):
        evidence["git_diff_sha256"] = None
    else:
        diff = _git_bytes(repo_root, "diff", "--binary", "HEAD", "--", relative_path)
        evidence["git_diff_sha256"] = _sha256_bytes(diff)
    return evidence


def _canonical_git_path(value: bytes) -> str:
    return unicodedata.normalize("NFC", os.fsdecode(value).replace("\\", "/"))


def _git_text(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        check=False,
    )
    if result.returncode != 0:
        raise RunRecordError(
            f"git {' '.join(args)} failed with exit code {result.returncode}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def _git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = os.fsdecode(result.stderr).strip()
        raise RunRecordError(
            f"git {' '.join(args)} failed with exit code {result.returncode}: {stderr}"
        )
    return result.stdout


def _exact_keys(
    value: Mapping[str, object],
    required: set[str],
    optional: set[str],
    name: str,
) -> None:
    keys = set(value)
    missing = required - keys
    unknown = keys - required - optional
    if missing:
        raise RunRecordError(f"{name} is missing keys: {sorted(missing)}")
    if unknown:
        raise RunRecordError(f"{name} has unknown keys: {sorted(unknown)}")


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RunRecordError(f"{name} must be a JSON object")
    if any(not isinstance(key, str) for key in value):
        raise RunRecordError(f"{name} keys must be strings")
    return value


def _json_object(value: object, name: str) -> Mapping[str, object]:
    data = _mapping(value, name)
    try:
        json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError) as error:
        raise RunRecordError(f"{name} is not JSON serializable") from error
    return data


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise RunRecordError(f"{name} must be a list")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise RunRecordError(f"{name} must be a string")
    return value


def _int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RunRecordError(f"{name} must be an integer")
    return value


def _bool(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise RunRecordError(f"{name} must be a boolean")
    return value


def _path(value: object, name: str) -> Path:
    return Path(_string(value, name)).expanduser()


def _absolute_path(value: object, name: str) -> Path:
    path = _path(value, name)
    if not path.is_absolute():
        raise RunRecordError(f"{name} must be absolute")
    return path


def _path_list(value: object, name: str) -> tuple[str, ...]:
    values = _list(value, name)
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        raw = _string(item, f"{name}[]")
        normalized = _normalize_repo_path(raw, name)
        key = normalized.casefold() if os.name == "nt" else normalized
        if key in seen:
            raise RunRecordError(f"duplicate path in {name}: {raw}")
        seen.add(key)
        result.append(normalized)
    return tuple(result)


def _normalize_repo_path(raw: str, name: str) -> str:
    value = unicodedata.normalize("NFC", raw.strip()).replace("\\", "/")
    if not value or value.startswith("/") or _DRIVE_RE.match(value):
        raise RunRecordError(f"{name} must contain repository-relative paths")
    if any(character in value for character in _WILDCARDS):
        raise RunRecordError(f"{name} contains a wildcard path")
    trailing = value.endswith("/")
    parts: list[str] = []
    for part in value.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            raise RunRecordError(f"{name} contains a parent path")
        parts.append(part)
    if not parts:
        raise RunRecordError(f"{name} contains an empty path")
    normalized = "/".join(parts)
    return normalized + "/" if trailing else normalized


def _path_string(path: Path) -> str:
    return path.as_posix()


def _resolve_path(path: Path, root: Path) -> Path:
    return (path if path.is_absolute() else root / path).resolve(strict=False)


def _commit_value(value: object, name: str) -> str:
    result = _string(value, name)
    if not _COMMIT_RE.fullmatch(result):
        raise RunRecordError(f"{name} must be a 40-character commit ID")
    return result.lower()


def _sha256_value(value: object, name: str) -> str:
    result = _string(value, name)
    if not _SHA256_RE.fullmatch(result):
        raise RunRecordError(f"{name} must be a 64-character SHA-256")
    return result.lower()


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _pretty_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _last_sequence(path: Path) -> int:
    if not path.is_file():
        return 0
    last = 0
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                value = json.loads(line)
                sequence = value.get("sequence")
                if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence <= last:
                    raise RunRecordError(f"invalid sequence in append-only stream: {path}")
                last = sequence
    except (OSError, json.JSONDecodeError) as error:
        raise RunRecordError(f"could not read append-only stream: {path}") from error
    return last


def _exclusive_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


__all__ = [
    "Blocker",
    "ExecutionPolicy",
    "PlanProvenance",
    "RecoveryEvidence",
    "ReviewPolicy",
    "RunContract",
    "RunLineage",
    "RunRecord",
    "RunRecordError",
    "RunResult",
    "RunStatus",
    "ScopeContract",
    "SuccessPolicy",
    "TaskContract",
    "TestEvidence",
    "WorkspaceContract",
    "run_artifact_fingerprint",
    "workspace_fingerprint",
]
