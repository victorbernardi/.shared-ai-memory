from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    REPO_ROOT
    / "skills"
    / "sdd-cmdc-opencode"
    / "scripts"
    / "sdd_cmdc_opencode"
    / "run_record.py"
)


def _module():
    if not MODULE_PATH.is_file():
        pytest.fail("run_record.py is absent")
    spec = importlib.util.spec_from_file_location("run_record_under_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        pytest.fail("could not load run_record.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=text,
        check=True,
    )
    return result.stdout.strip() if text else result.stdout


def _init_repo(tmp_path: Path) -> dict[str, object]:
    repo = tmp_path / "workspace"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Run Record Tests")
    _git(repo, "branch", "-M", "main")

    plan_dir = repo / ".superpowers" / "sdd" / "plan"
    plan_dir.mkdir(parents=True)
    plan = plan_dir / "implementation.md"
    plan.write_text(
        """# Plan

## Task 5
Implement the persisted run.

## Task 6
Do not include this task.
""",
        encoding="utf-8",
    )
    _git(repo, "add", "--", str(plan.relative_to(repo)))
    _git(repo, "commit", "-qm", "plan")
    head = str(_git(repo, "rev-parse", "HEAD"))
    branch = str(_git(repo, "branch", "--show-current"))

    brief = plan_dir / "task-5-brief.md"
    brief.write_text(
        "## Task 5\nImplement the persisted run.\n",
        encoding="utf-8",
    )
    report = plan_dir / "task-5-report.md"
    return {
        "repo": repo,
        "plan": plan,
        "brief": brief,
        "report": report,
        "head": head,
        "branch": branch,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _valid_mapping(tmp_path: Path) -> tuple[object, dict[str, object], dict[str, object]]:
    module = _module()
    fixture = _init_repo(tmp_path)
    repo = fixture["repo"]
    plan = fixture["plan"]
    brief = fixture["brief"]
    report = fixture["report"]
    assert isinstance(repo, Path)
    assert isinstance(plan, Path)
    assert isinstance(brief, Path)
    assert isinstance(report, Path)
    mapping: dict[str, object] = {
        "schema_version": 1,
        "run_id": "run-123",
        "task": {
            "id": 5,
            "heading": "Task 5",
            "brief_path": str(brief),
            "brief_sha256": _sha256(brief),
            "report_path": str(report),
        },
        "plan": {
            "source_path": str(plan),
            "source_repository": str(repo),
            "source_branch": str(fixture["branch"]),
            "source_head": str(fixture["head"]),
            "sha256": _sha256(plan),
        },
        "workspace": {
            "repo_root": str(repo),
            "base_head": str(fixture["head"]),
            "branch": str(fixture["branch"]),
            "baseline_status": {},
        },
        "scope": {
            "allowed_paths": ["src/"],
            "denied_paths": ["src/private.py"],
        },
        "execution": {
            "backend": "cmdc-local",
            "model": "deepseek/deepseek-v4-flash",
            "max_turns": 20,
            "wall_timeout_seconds": 120,
            "stall_timeout_seconds": 30,
            "progress_deadline_turns": 4,
            "max_resumes": 2,
            "no_skills": True,
            "yolo": True,
        },
        "success": {
            "require_commit": True,
            "require_report": True,
            "require_test_evidence": True,
        },
        "review": {"auto_fix_rounds": 0},
    }
    return module, mapping, fixture


def _valid_result(module, contract):
    return module.RunResult(
        schema_version=1,
        run_id=contract.run_id,
        backend="cmdc-local",
        session_id="session-123",
        status=module.RunStatus.COMPLETE,
        primary_blocker=None,
        secondary_blockers=(),
        base_head=contract.workspace.base_head,
        final_head=contract.workspace.base_head,
        scope_valid=True,
        violating_paths=(),
        report_valid=True,
        test_evidence_valid=True,
        cleanup_verified=True,
        tests=(
            module.TestEvidence(
                command="pytest tests -q",
                exit_code=0,
                summary="246 passed in 23.67s",
                passed=246,
                failed=0,
                event_sequence=3,
            ),
        ),
        recoveries=(),
        artifact_hashes={"contract": contract.contract_sha256},
    )


def test_valid_contract_loads_as_frozen_nested_values_and_roundtrips(tmp_path: Path) -> None:
    module, mapping, _ = _valid_mapping(tmp_path)

    contract = module.RunContract.from_mapping(mapping)

    assert contract.schema_version == 1
    assert contract.execution.backend == "cmdc-local"
    assert contract.task.heading == "Task 5"
    assert contract.scope.allowed_paths == ("src/",)
    assert contract.workspace.base_head == mapping["workspace"]["base_head"]
    with pytest.raises((AttributeError, TypeError)):
        contract.run_id = "changed"
    assert module.RunContract.from_mapping(contract.to_mapping()).contract_sha256 == (
        contract.contract_sha256
    )


@pytest.mark.parametrize(
    "mutation",
    (
        lambda value: value.pop("review"),
        lambda value: value.update({"unexpected": True}),
        lambda value: value.update({"schema_version": True}),
        lambda value: value.update({"schema_version": 2}),
        lambda value: value["execution"].update({"backend": "other"}),
        lambda value: value["execution"].update({"max_turns": 0}),
        lambda value: value["execution"].update({"wall_timeout_seconds": -1}),
        lambda value: value["execution"].update({"max_resumes": -1}),
        lambda value: value["execution"].update({"progress_deadline_turns": 21}),
    ),
)
def test_contract_rejects_unknown_schema_backend_and_inconsistent_limits(
    tmp_path: Path,
    mutation,
) -> None:
    module, mapping, _ = _valid_mapping(tmp_path)
    candidate = copy.deepcopy(mapping)
    mutation(candidate)

    with pytest.raises(ValueError):
        module.RunContract.from_mapping(candidate)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda value: value["workspace"].update({"repo_root": "relative/repo"}),
        lambda value: value["plan"].update({"source_repository": "relative/source"}),
        lambda value: value["task"].update({"brief_path": "C:/outside/brief.md"}),
        lambda value: value["task"].update({"report_path": "C:/outside/report.md"}),
        lambda value: value["workspace"].update({"base_head": "not-a-commit"}),
        lambda value: value["plan"].update({"source_head": "0" * 39}),
        lambda value: value["plan"].update({"sha256": "0" * 63}),
        lambda value: value["task"].update({"brief_sha256": "0" * 63}),
    ),
)
def test_contract_rejects_unsafe_paths_and_malformed_hashes(tmp_path: Path, mutation) -> None:
    module, mapping, _ = _valid_mapping(tmp_path)
    candidate = copy.deepcopy(mapping)
    mutation(candidate)

    with pytest.raises(ValueError):
        module.RunContract.from_mapping(candidate)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda value: value["plan"].update({"sha256": "0" * 64}),
        lambda value: value["task"].update({"heading": "Task 4"}),
        lambda value: value["task"].update({"brief_sha256": "0" * 64}),
    ),
)
def test_contract_rechecks_plan_heading_and_source_and_brief_hashes(
    tmp_path: Path,
    mutation,
) -> None:
    module, mapping, _ = _valid_mapping(tmp_path)
    candidate = copy.deepcopy(mapping)
    mutation(candidate)

    with pytest.raises(ValueError):
        module.RunContract.from_mapping(candidate)


@pytest.mark.parametrize(
    "lineage",
    (
        {
            "kind": "review-fix",
            "parent_run_id": "run-1",
            "parent_review_id": "review-1",
            "parent_review_result_sha256": "a" * 64,
            "parent_brief_sha256": "b" * 64,
            "finding_ids": ["F-1"],
            "findings_sha256": "c" * 64,
        },
        {
            "kind": "fix-round",
            "parent_run_id": "run-1",
            "parent_review_id": "review-1",
            "parent_review_result_sha256": "invalid",
            "parent_brief_sha256": "b" * 64,
            "finding_ids": ["F-1"],
            "findings_sha256": "c" * 64,
        },
        {
            "kind": "fix-round",
            "parent_run_id": "run-1",
            "parent_review_id": "review-1",
            "parent_review_result_sha256": "a" * 64,
            "parent_brief_sha256": "b" * 64,
            "finding_ids": ["F-1"],
            "findings_sha256": "c" * 64,
        },
    ),
)
def test_contract_rejects_invalid_fix_round_lineage(tmp_path: Path, lineage) -> None:
    module, mapping, _ = _valid_mapping(tmp_path)
    candidate = copy.deepcopy(mapping)
    candidate["lineage"] = lineage

    with pytest.raises(ValueError):
        module.RunContract.from_mapping(candidate)


def test_fix_round_lineage_loads_and_verifies_the_authoritative_brief_hash(
    tmp_path: Path,
) -> None:
    """A valid fix-round Contract loads only when ``parent_brief_sha256`` is
    the authoritative SHA-256 of the source plan's extracted task brief.

    The hash is computed from the extracted ``heading + body`` of the
    recorded source plan (normalized LF), never from an undefined or
    caller-supplied value.
    """
    module, mapping, fixture = _valid_mapping(tmp_path)
    candidate = copy.deepcopy(mapping)
    plan = fixture["plan"]
    assert isinstance(plan, Path)
    helper_path = (
        REPO_ROOT / "skills" / "sdd-cmdc-opencode" / "scripts" / "task-brief.py"
    )
    helper_spec = importlib.util.spec_from_file_location("task_brief_fixture", helper_path)
    assert helper_spec is not None and helper_spec.loader is not None
    helper = importlib.util.module_from_spec(helper_spec)
    sys.modules[helper_spec.name] = helper
    helper_spec.loader.exec_module(helper)
    heading, body = helper.extract_task(plan.read_text(encoding="utf-8"), 5)
    source_brief = (heading + "\n" + body).encode("utf-8").replace(b"\r\n", b"\n")
    authoritative = hashlib.sha256(source_brief).hexdigest()
    candidate["lineage"] = {
        "kind": "fix-round",
        "parent_run_id": "run-1",
        "parent_review_id": "review-1",
        "parent_review_result_sha256": "a" * 64,
        "parent_brief_sha256": authoritative,
        "finding_ids": ["F-1"],
        "findings_sha256": hashlib.sha256(
            json.dumps(["F-1"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }

    contract = module.RunContract.from_mapping(candidate)
    assert contract.lineage is not None
    assert contract.lineage.parent_brief_sha256 == authoritative

    # A mismatched parent brief hash must raise the domain validation error,
    # never NameError or another incidental exception.
    candidate["lineage"]["parent_brief_sha256"] = "f" * 64
    with pytest.raises(ValueError) as raised:
        module.RunContract.from_mapping(candidate)
    assert "fix-round parent brief hash does not match the source task" in str(
        raised.value
    )
    assert not isinstance(raised.value, NameError)


def test_run_record_create_is_exclusive_and_writes_immutable_contract(tmp_path: Path) -> None:
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    run_dir = fixture["repo"] / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id

    record = module.RunRecord.create(run_dir, contract)

    assert record.run_dir == run_dir
    assert (run_dir / "contract.json").is_file()
    assert (run_dir / "events.jsonl").read_bytes() == b""
    assert (run_dir / "checkpoints.jsonl").read_bytes() == b""
    before = (run_dir / "contract.json").read_bytes()
    with pytest.raises((FileExistsError, ValueError)):
        module.RunRecord.create(run_dir, contract)
    assert (run_dir / "contract.json").read_bytes() == before


def test_run_record_streams_are_owned_and_monotonic(tmp_path: Path) -> None:
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    run_dir = fixture["repo"] / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id
    record = module.RunRecord.create(run_dir, contract)

    assert record.append_event({"type": "assistant_progress", "turn": 1}) == 1
    assert record.append_event({"type": "assistant_progress", "turn": 2}) == 2
    assert record.append_checkpoint({"kind": "session", "session_id": "session-123"}) == 1
    assert record.append_checkpoint({"kind": "progress", "turn": 2}) == 2

    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines()]
    checkpoints = [
        json.loads(line) for line in (run_dir / "checkpoints.jsonl").read_text().splitlines()
    ]
    assert [event["sequence"] for event in events] == [1, 2]
    assert [checkpoint["sequence"] for checkpoint in checkpoints] == [1, 2]
    for item in [*events, *checkpoints]:
        assert item["run_id"] == contract.run_id
        assert item["contract_sha256"] == contract.contract_sha256
        assert item["timestamp"].endswith("Z")

    with pytest.raises(ValueError):
        record.append_event({"run_id": "other-run", "type": "bad"})
    with pytest.raises(ValueError):
        record.append_checkpoint(
            {"contract_sha256": "0" * 64, "kind": "bad"}
        )

    assert record.read_events()[0]["sequence"] == 1
    assert record.latest_checkpoint()["kind"] == "progress"

    checkpoint_path = run_dir / "checkpoints.jsonl"
    tampered = json.loads(checkpoint_path.read_text(encoding="utf-8").splitlines()[0])
    tampered["run_id"] = "foreign-run"
    lines = checkpoint_path.read_text(encoding="utf-8").splitlines()
    lines[0] = json.dumps(tampered, sort_keys=True)
    checkpoint_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="foreign run_id"):
        record.read_checkpoints()


def test_result_replacement_is_atomic_and_prior_streams_remain_append_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    run_dir = fixture["repo"] / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id
    record = module.RunRecord.create(run_dir, contract)
    record.append_event({"type": "outcome", "status": "BLOCKED"})
    record.append_checkpoint({"kind": "outcome", "status": "BLOCKED"})
    first = _valid_result(module, contract)
    record.write_result(first)
    before = (run_dir / "result.json").read_bytes()

    second = module.RunResult(
        **{
            **first.__dict__,
            "status": module.RunStatus.INCOMPLETE,
        }
    )

    def interrupted_replace(source: str | bytes | os.PathLike, destination: str | bytes | os.PathLike):
        raise OSError("simulated interrupted replacement")

    monkeypatch.setattr(module.os, "replace", interrupted_replace)
    with pytest.raises(OSError):
        record.write_result(second)
    assert (run_dir / "result.json").read_bytes() == before
    assert record.read_result().status is module.RunStatus.COMPLETE
    event_records = [
        json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines()
    ]
    checkpoint_records = [
        json.loads(line)
        for line in (run_dir / "checkpoints.jsonl").read_text().splitlines()
    ]
    assert event_records[0]["status"] == "BLOCKED"
    assert checkpoint_records[0]["status"] == "BLOCKED"


def test_locate_scans_only_one_repo_scoped_plan_workspace(tmp_path: Path) -> None:
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    repo = fixture["repo"]
    first_dir = repo / ".superpowers" / "sdd" / "plan-a" / "runs" / contract.run_id
    module.RunRecord.create(first_dir, contract)

    located = module.RunRecord.locate(repo, contract.run_id)
    assert located.run_dir == first_dir

    with pytest.raises(ValueError):
        module.RunRecord.locate(repo, "missing-run")

    second_dir = repo / ".superpowers" / "sdd" / "plan-b" / "runs" / contract.run_id
    module.RunRecord.create(second_dir, contract)
    with pytest.raises(ValueError):
        module.RunRecord.locate(repo, contract.run_id)

    outside = tmp_path / "outside" / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id
    outside.mkdir(parents=True)
    (outside / "contract.json").write_bytes((first_dir / "contract.json").read_bytes())
    with pytest.raises(ValueError):
        module.RunRecord.locate(tmp_path, contract.run_id)


def test_workspace_fingerprint_captures_git_status_and_changed_path_evidence(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = tmp_path / "fingerprint-测试"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Run Record Tests")
    _git(repo, "branch", "-M", "main")
    (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
    (repo / "rename me & ü.txt").write_text("rename\n", encoding="utf-8")
    (repo / "delete.txt").write_text("delete\n", encoding="utf-8")
    _git(repo, "add", "--all")
    _git(repo, "commit", "-qm", "base")

    baseline = module.workspace_fingerprint(repo)
    (repo / "tracked.txt").write_text("staged\n", encoding="utf-8")
    _git(repo, "add", "--", "tracked.txt")
    (repo / "tracked.txt").write_text("unstaged\n", encoding="utf-8")
    (repo / "new & caminho.txt").write_text("untracked\n", encoding="utf-8")
    _git(repo, "mv", "rename me & ü.txt", "renamed & ü.txt")
    (repo / "delete.txt").unlink()

    fingerprint = module.workspace_fingerprint(repo)

    assert fingerprint["head"] == baseline["head"]
    assert fingerprint["branch"] == "main"
    assert fingerprint["status_sha256"] != baseline["status_sha256"]
    paths = fingerprint["paths"]
    assert "tracked.txt" in paths
    assert "new & caminho.txt" in paths
    assert "renamed & ü.txt" in paths
    assert "rename me & ü.txt" in paths
    assert "delete.txt" in paths
    assert paths["tracked.txt"]["git_diff_sha256"] == hashlib.sha256(
        subprocess.run(
            ["git", "-C", str(repo), "diff", "--binary", "HEAD", "--", "tracked.txt"],
            capture_output=True,
            check=True,
        ).stdout
    ).hexdigest()
    assert paths["new & caminho.txt"]["sha256"] == _sha256(repo / "new & caminho.txt")
    assert paths["delete.txt"]["kind"] == "missing"


def test_workspace_fingerprint_detects_nested_files_in_a_mixed_untracked_container(
    tmp_path: Path,
) -> None:
    """A new allowed artifact must not disappear behind a pre-existing folder."""
    module = _module()
    repo = tmp_path / "mixed-untracked-container"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Run Record Tests")
    (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "--all")
    _git(repo, "commit", "-qm", "base")

    foreign = repo / ".superpowers" / "foreign" / "keep.txt"
    foreign.parent.mkdir(parents=True)
    foreign.write_text("pre-existing\n", encoding="utf-8")
    baseline = module.workspace_fingerprint(repo)

    generated = repo / ".superpowers" / "planetfone-hybrid" / "baseline" / "pages.json"
    generated.parent.mkdir(parents=True)
    generated.write_text("{}\n", encoding="utf-8")
    current = module.workspace_fingerprint(repo)

    assert ".superpowers/foreign/keep.txt" in baseline["paths"]
    assert ".superpowers/planetfone-hybrid/baseline/pages.json" in current["paths"]
    assert baseline["paths"] != current["paths"]


def test_run_record_owned_artifacts_do_not_appear_in_workspace_fingerprint(
    tmp_path: Path,
) -> None:
    """The lifecycle-owned run directory created after Contract creation is
    never mistaken for an external post-contract change."""
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    repo = fixture["repo"]
    assert isinstance(repo, Path)
    run_dir = repo / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id

    module.RunRecord.create(run_dir, contract)

    owned = module.workspace_fingerprint(repo, owner_run_dir=run_dir)
    assert all(
        not str(path).startswith(".superpowers/sdd/plan/runs/")
        for path in owned["paths"]
    ), "owned run artifacts leaked into the workspace fingerprint"
    without_owner = module.workspace_fingerprint(repo)
    assert any(
        str(path).startswith(".superpowers/sdd/plan/runs/")
        for path in without_owner["paths"]
    ), "without an explicit owner the run directory must remain visible"


def test_workspace_fingerprint_without_owner_hides_no_run_directory(
    tmp_path: Path,
) -> None:
    """``workspace_fingerprint(repo)`` without an explicit owner must never
    hide any run directory, including one that is structurally valid and
    looks exactly like a lifecycle run."""
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    repo = fixture["repo"]
    assert isinstance(repo, Path)

    module.RunRecord.create(
        repo / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id,
        contract,
    )
    rogue = repo / ".superpowers" / "sdd" / "rogue" / "runs" / "fake-run"
    rogue.mkdir(parents=True)
    (rogue / "evil.txt").write_text("evil\n", encoding="utf-8")

    fingerprint = module.workspace_fingerprint(repo)

    paths = fingerprint["paths"]
    assert any(
        str(path).startswith(".superpowers/sdd/plan/runs/")
        for path in paths
    ), "the run directory itself must remain visible without an owner"
    assert any(
        str(path).startswith(".superpowers/sdd/rogue/") for path in paths
    ), "the rogue run directory must remain visible without an owner"


def test_workspace_fingerprint_explicit_owner_reconciles_only_its_own_run(
    tmp_path: Path,
) -> None:
    """With the current run passed explicitly as owner, only that run's
    artifacts are excluded; a forged sibling with a syntactically valid
    workspace and run-id stays present even when git collapses the parent
    directory into one untracked entry."""
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    repo = fixture["repo"]
    assert isinstance(repo, Path)
    run_dir = repo / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id

    module.RunRecord.create(run_dir, contract)
    rogue = repo / ".superpowers" / "sdd" / "rogue" / "runs" / "fake-run"
    rogue.mkdir(parents=True)
    (rogue / "evil.txt").write_text("evil\n", encoding="utf-8")

    fingerprint = module.workspace_fingerprint(repo, owner_run_dir=run_dir)

    assert all(
        not str(path).startswith(".superpowers/sdd/plan/runs/")
        for path in fingerprint["paths"]
    ), "the owner run artifacts must not leak into the fingerprint"
    assert any(
        str(path).startswith(".superpowers/sdd/rogue/") for path in fingerprint["paths"]
    ), "a forged sibling run must remain visible even with an owner"


def test_workspace_fingerprint_owner_outside_or_ambiguous_fails_closed(
    tmp_path: Path,
) -> None:
    """An owner outside the repository, an owner that is not a run directory,
    and an owner with an unsafe run-id must all raise instead of silently
    excluding paths."""
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    repo = fixture["repo"]
    assert isinstance(repo, Path)
    run_dir = repo / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id

    module.RunRecord.create(run_dir, contract)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "contract.json").write_text("{}", encoding="utf-8")
    bad_owner = repo / ".superpowers" / "sdd" / "plan"
    bad_owner.mkdir(parents=True, exist_ok=True)
    (bad_owner / "contract.json").write_text("{}", encoding="utf-8")

    for owner in (
        outside,
        bad_owner,
        repo / ".superpowers" / "sdd" / "plan" / "runs" / "bad id",
    ):
        with pytest.raises(ValueError):
            module.workspace_fingerprint(repo, owner_run_dir=owner)


def test_run_artifact_fingerprint_owner_other_run_does_not_hide_paths(
    tmp_path: Path,
) -> None:
    """Passing another run as the owner must never exclude that other run's
    paths from the reconciled fingerprint."""
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    repo = fixture["repo"]
    assert isinstance(repo, Path)
    run_dir = repo / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id
    other_dir = repo / ".superpowers" / "sdd" / "plan" / "runs" / "other-run"

    module.RunRecord.create(run_dir, contract)
    other_dir.mkdir(parents=True, exist_ok=True)
    (other_dir / "evil.txt").write_text("evil\n", encoding="utf-8")

    fingerprint = module.run_artifact_fingerprint(
        repo, run_dir, module.workspace_fingerprint(repo)
    )
    assert any(
        str(path).startswith(".superpowers/sdd/plan/runs/")
        for path in fingerprint.get("paths", {})
    ), "a sibling run must keep the shared untracked container visible"


def test_run_artifact_fingerprint_merges_owned_run_artifacts_and_keeps_external_changes(
    tmp_path: Path,
) -> None:
    """``run_artifact_fingerprint`` reconciles the Contract-time baseline with
    the run directory ``RunRecord.create`` added afterwards, while still
    exposing any external post-contract change."""
    module, mapping, fixture = _valid_mapping(tmp_path)
    contract = module.RunContract.from_mapping(mapping)
    repo = fixture["repo"]
    assert isinstance(repo, Path)
    baseline = module.workspace_fingerprint(repo)
    run_dir = repo / ".superpowers" / "sdd" / "plan" / "runs" / contract.run_id

    module.RunRecord.create(run_dir, contract)
    clean = module.run_artifact_fingerprint(repo, run_dir, baseline)
    assert clean == module.workspace_fingerprint(repo, owner_run_dir=run_dir), (
        "expected run artifacts must not change the reconciled fingerprint"
    )

    tracked = repo / "tracked.py"
    tracked.write_text("VALUE = 2\n", encoding="utf-8")
    external = repo / "external.txt"
    external.write_text("external\n", encoding="utf-8")
    rogue = repo / ".superpowers" / "rogue.txt"
    rogue.write_text("rogue\n", encoding="utf-8")
    changed = module.run_artifact_fingerprint(repo, run_dir, baseline)
    changed_paths = changed.get("paths", {})
    assert changed_paths != clean.get("paths", {})
    assert "tracked.py" in changed_paths
    assert "external.txt" in changed_paths
    assert ".superpowers/rogue.txt" in changed_paths
    assert all(
        not str(path).startswith(".superpowers/sdd/plan/runs/")
        for path in changed_paths
    ), "run artifacts are not merged into the reconciled fingerprint"


def test_workspace_fingerprint_preserves_preexisting_dirty_and_symlink_evidence(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = tmp_path / "dirty-workspace"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Run Record Tests")
    _git(repo, "branch", "-M", "main")
    dirty = repo / "pre-existing.txt"
    dirty.write_text("base\n", encoding="utf-8")
    _git(repo, "add", "--all")
    _git(repo, "commit", "-qm", "base")
    dirty.write_text("pre-existing dirty\n", encoding="utf-8")

    baseline = module.workspace_fingerprint(repo)
    unchanged = module.workspace_fingerprint(repo)

    assert baseline == unchanged
    assert baseline["paths"]["pre-existing.txt"]["kind"] == "file"

    target = repo / "target.txt"
    target.write_text("target\n", encoding="utf-8")
    link = repo / "link.txt"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"symlink creation unavailable: {error}")
    linked = module.workspace_fingerprint(repo)
    assert linked["paths"]["link.txt"]["kind"] == "symlink"
    assert linked["paths"]["link.txt"]["target"]
