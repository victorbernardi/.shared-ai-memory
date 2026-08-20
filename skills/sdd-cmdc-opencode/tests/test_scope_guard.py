from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

from sdd_cmdc_opencode import workspace_fingerprint


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    REPO_ROOT
    / "skills"
    / "sdd-cmdc-opencode"
    / "scripts"
    / "sdd_cmdc_opencode"
    / "_scope_guard.py"
)
MOD_PATH = MODULE_PATH.with_name("_scope_mod.ts")


def _module():
    if not MODULE_PATH.is_file():
        pytest.fail("_scope_guard.py is absent")
    spec = importlib.util.spec_from_file_location("scope_guard_under_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        pytest.fail("could not load _scope_guard.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "scope-repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Scope Guard Tests")
    _git(repo, "branch", "-M", "main")
    (repo / "src").mkdir()
    (repo / "src" / "run.py").write_text("print('run')\n", encoding="utf-8")
    (repo / "src" / "private.py").write_text("secret\n", encoding="utf-8")
    _git(repo, "add", "--all")
    _git(repo, "commit", "-qm", "base")
    return repo


def _contract(
    module,
    repo: Path,
    *,
    explicit: list[str] | None = None,
    derived: list[str] | None = None,
    denied: list[str] | None = None,
    baseline: dict[str, object] | None = None,
) -> dict[str, object]:
    return module.build_scope_contract(
        repo,
        explicit_allowed_paths=explicit,
        derived_allowed_paths=derived,
        denied_paths=denied or [],
        baseline=baseline if baseline is not None else workspace_fingerprint(repo),
    )


def test_canonical_path_policy_allows_exact_files_and_directories_and_denies_precedence(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = _repo(tmp_path)
    contract = _contract(
        module,
        repo,
        explicit=["src/run.py", "future/"],
        denied=["src/private.py"],
    )

    assert module.canonicalize_path(repo, str(repo / "src" / "run.py")) == "src/run.py"
    assert module.canonicalize_path(repo, r"src\run.py") == "src/run.py"
    assert module.canonicalize_path(repo, "./future/new.py") == "future/new.py"
    assert module.check_tool(
        contract,
        {"toolName": "write_file", "input": {"path": "src/run.py"}},
    ) == {
        "decision": "allow",
        "code": "",
        "paths": [],
        "message": "path is inside the Run scope",
    }
    denied_result = module.check_tool(
        contract,
        {"toolName": "write_file", "input": {"path": "src/private.py"}},
    )
    assert denied_result["decision"] == "block"
    assert denied_result["code"] == "SCOPE_VIOLATION"
    assert denied_result["paths"] == ["src/private.py"]


@pytest.mark.parametrize(
    "raw_path",
    (
        "/outside/file.py",
        "C:relative\\file.py",
        r"\\server\share\file.py",
        "../outside.py",
        "src/../../outside.py",
        "src/*.py",
    ),
)
def test_canonical_path_policy_rejects_absolute_parent_drive_unc_and_wildcard_paths(
    tmp_path: Path,
    raw_path: str,
) -> None:
    module = _module()
    repo = _repo(tmp_path)

    with pytest.raises(ValueError):
        module.canonicalize_path(repo, raw_path)


def test_canonical_path_policy_normalizes_unicode_and_returns_sorted_violations(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = _repo(tmp_path)
    composed = "café.py"
    decomposed = unicodedata.normalize("NFD", composed)
    contract = _contract(module, repo, explicit=["allowed.py"])

    assert module.canonicalize_path(repo, decomposed) == composed
    result = module.check_tool(
        contract,
        {
            "toolName": "edit_file",
            "input": {"paths": ["z.py", "a.py", "é.py"]},
        },
    )
    assert result["decision"] == "block"
    assert result["paths"] == ["a.py", "z.py", "é.py"]


def test_canonical_path_policy_rejects_symlink_resolving_outside_repo(tmp_path: Path) -> None:
    module = _module()
    repo = _repo(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("outside\n", encoding="utf-8")
    link = repo / "src" / "link.py"
    try:
        link.symlink_to(outside)
    except OSError as error:
        pytest.skip(f"symlink creation unavailable: {error}")

    with pytest.raises(ValueError):
        module.canonicalize_path(repo, "src/link.py")


def test_scope_construction_prefers_explicit_then_derived_and_fails_closed_without_either(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = _repo(tmp_path)
    explicit = _contract(module, repo, explicit=["explicit.py"], derived=["derived.py"])
    derived = _contract(module, repo, derived=["derived.py"])

    assert explicit["source"] == "explicit"
    assert explicit["allowed_paths"] == ["explicit.py"]
    assert derived["source"] == "task-files-section"
    assert derived["allowed_paths"] == ["derived.py"]
    with pytest.raises(module.ScopeGuardError) as error:
        module.build_scope_contract(repo, denied_paths=[])
    assert error.value.code == "SCOPE_CONTRACT_MISSING"


def test_audit_accepts_unchanged_preexisting_dirty_path_and_detects_new_effects(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = _repo(tmp_path)
    preexisting = repo / "pre-existing.txt"
    preexisting.write_text("dirty before run\n", encoding="utf-8")
    baseline = workspace_fingerprint(repo)
    contract = _contract(module, repo, explicit=["src/run.py"], baseline=baseline)

    unchanged = module.audit_workspace(contract, {})
    assert unchanged["decision"] == "allow"

    preexisting.write_text("changed during run\n", encoding="utf-8")
    new_file = repo / "new out-of-scope.txt"
    new_file.write_text("must remain for audit\n", encoding="utf-8")
    changed = module.audit_workspace(contract, {})
    assert changed["decision"] == "terminate"
    assert changed["code"] == "SCOPE_VIOLATION"
    assert changed["paths"] == ["new out-of-scope.txt", "pre-existing.txt"]
    assert new_file.read_text(encoding="utf-8") == "must remain for audit\n"


def test_audit_allows_allowed_workspace_delta_and_detects_denied_delta(tmp_path: Path) -> None:
    module = _module()
    repo = _repo(tmp_path)
    baseline = workspace_fingerprint(repo)
    contract = _contract(
        module,
        repo,
        explicit=["src/"],
        denied=["src/private.py"],
        baseline=baseline,
    )
    (repo / "src" / "new.py").write_text("allowed\n", encoding="utf-8")
    assert module.audit_workspace(contract, {})["decision"] == "allow"
    (repo / "src" / "private.py").write_text("changed secret\n", encoding="utf-8")
    result = module.audit_workspace(contract, {})
    assert result["decision"] == "terminate"
    assert result["paths"] == ["src/private.py"]


def test_audit_with_explicit_owner_keeps_forged_sibling_run_visible(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = _repo(tmp_path)
    baseline = workspace_fingerprint(repo)
    contract = _contract(module, repo, explicit=["src/"], baseline=baseline)

    owner = repo / ".superpowers" / "sdd" / "plan" / "runs" / "run-123"
    owner.mkdir(parents=True)
    (owner / "contract.json").write_text("{}\n", encoding="utf-8")
    rogue = repo / ".superpowers" / "sdd" / "rogue" / "runs" / "fake-run"
    rogue.mkdir(parents=True)
    (rogue / "evil.txt").write_text("must remain visible\n", encoding="utf-8")

    result = module.audit_workspace(contract, {}, owner_run_dir=owner)

    assert result["decision"] == "terminate"
    # This fixture has no tracked anchor below ``.superpowers``; Git therefore
    # reports the forged subtree as the collapsed ``.superpowers`` container.
    # Its presence proves the sibling was not hidden by the explicit owner.
    assert ".superpowers" in result["paths"]


def test_scope_guard_cli_uses_explicit_run_owner_environment(tmp_path: Path) -> None:
    module = _module()
    repo = _repo(tmp_path)
    baseline = workspace_fingerprint(repo)
    contract = _contract(module, repo, explicit=["src/"], baseline=baseline)
    contract_path = tmp_path / "scope-contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")

    owner = repo / ".superpowers" / "sdd" / "plan" / "runs" / "run-123"
    owner.mkdir(parents=True)
    (owner / "contract.json").write_text("{}\n", encoding="utf-8")
    rogue = repo / ".superpowers" / "sdd" / "rogue" / "runs" / "fake-run"
    rogue.mkdir(parents=True)
    (rogue / "evil.txt").write_text("must remain visible\n", encoding="utf-8")

    environment = os.environ.copy()
    environment["SDD_CMDC_SCOPE_RUN_OWNER"] = str(owner.resolve())
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "audit-workspace",
            "--contract",
            str(contract_path),
        ],
        input="{}",
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )

    assert result.returncode == 0, result.stderr
    decision = json.loads(result.stdout)
    assert decision["decision"] == "terminate"
    assert ".superpowers" in decision["paths"]


def test_scope_guard_json_cli_returns_decision_without_shell_parsing(tmp_path: Path) -> None:
    module = _module()
    repo = _repo(tmp_path)
    contract = _contract(module, repo, explicit=["src/run.py"])
    contract_path = tmp_path / "scope-contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "check-tool",
            "--contract",
            str(contract_path),
        ],
        input=json.dumps(
            {"toolName": "write_file", "input": {"path": "outside & file.py"}}
        ),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    decision = json.loads(result.stdout)
    assert decision["decision"] == "block"
    assert decision["code"] == "SCOPE_VIOLATION"
    assert decision["paths"] == ["outside & file.py"]


def test_scope_guard_mod_is_immutable_and_uses_argument_array_helper_calls() -> None:
    if not MOD_PATH.is_file():
        pytest.fail("_scope_mod.ts is absent")
    source = MOD_PATH.read_text(encoding="utf-8")

    for token in (
        "spawnSync",
        "SDD_CMDC_SCOPE_PYTHON",
        "SDD_CMDC_SCOPE_HELPER",
        "SDD_CMDC_SCOPE_CONTRACT",
        "SDD_CMDC_SCOPE_RUN_OWNER",
        "const runOwner = requiredPath('SDD_CMDC_SCOPE_RUN_OWNER')",
        "SDD_CMDC_SCOPE_RUN_OWNER: runOwner",
        "beforeToolCall",
        "afterToolCall",
        "check-tool",
        "audit-workspace",
        "shell: false",
        "process.env",
        "SCOPE_GUARD_FAILED",
    ):
        assert token in source
    assert "cmd.exe" not in source
