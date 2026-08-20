"""Private Run scope policy exposed to the packaged Command Code Mod."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import argparse
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

try:
    from .run_record import RunRecordError, workspace_fingerprint
except ImportError:  # Direct CLI execution from the packaged scripts directory.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from sdd_cmdc_opencode.run_record import RunRecordError, workspace_fingerprint


_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_WILDCARDS = frozenset("*?[]")
_SCOPE_SCHEMA_VERSION = 1
_SCOPE_ENV_NAMES = frozenset(
    {
        "SDD_CMDC_SCOPE_PYTHON",
        "SDD_CMDC_SCOPE_HELPER",
        "SDD_CMDC_SCOPE_CONTRACT",
        "SDD_CMDC_SCOPE_RUN_OWNER",
    }
)


class ScopeGuardError(ValueError):
    """A scope contract or helper input cannot be evaluated safely."""

    def __init__(self, message: str, code: str = "SCOPE_GUARD_FAILED") -> None:
        super().__init__(message)
        self.code = code


def canonicalize_path(repo_root: Path, raw_path: str) -> str:
    """Return a canonical repository-relative POSIX path.

    The resolved target, including symlinks and missing future paths, must stay
    below the repository root. Drive-relative and UNC spellings fail closed.
    """

    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ScopeGuardError("scope path must be a non-empty string")
    value = unicodedata.normalize("NFC", raw_path.strip()).replace("\\", "/")
    if any(character in value for character in _WILDCARDS):
        raise ScopeGuardError(f"scope path contains a wildcard: {raw_path}")
    if value.startswith("//"):
        raise ScopeGuardError(f"UNC scope path is not accepted: {raw_path}")
    if _DRIVE_RE.match(value) and (len(value) < 3 or value[2] != "/"):
        raise ScopeGuardError(f"drive-relative scope path is not accepted: {raw_path}")

    root = Path(repo_root).expanduser().resolve(strict=True)
    candidate = Path(value) if Path(value).is_absolute() else root / value
    resolved = candidate.resolve(strict=False)
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as error:
        raise ScopeGuardError(f"scope path resolves outside repository: {raw_path}") from error
    relative = unicodedata.normalize("NFC", relative)
    if not relative or relative == ".":
        raise ScopeGuardError("repository root is not a file scope")
    return relative


def build_scope_contract(
    repo_root: Path,
    *,
    explicit_allowed_paths: Sequence[str] | None = None,
    derived_allowed_paths: Sequence[str] | None = None,
    denied_paths: Sequence[str],
    baseline: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build a complete scope contract with explicit-over-derived precedence."""

    if explicit_allowed_paths is not None:
        source = "explicit"
        raw_allowed = explicit_allowed_paths
    elif derived_allowed_paths is not None:
        source = "task-files-section"
        raw_allowed = derived_allowed_paths
    else:
        raise ScopeGuardError(
            "no explicit or deterministically derived allowed paths",
            "SCOPE_CONTRACT_MISSING",
        )

    root = Path(repo_root).expanduser().resolve(strict=True)
    allowed = _normalize_entries(root, raw_allowed)
    denied = _normalize_entries(root, denied_paths)
    if baseline is not None and not isinstance(baseline, Mapping):
        raise ScopeGuardError("scope baseline must be a JSON object")
    return {
        "schema_version": _SCOPE_SCHEMA_VERSION,
        "source": source,
        "repo_root": root.as_posix(),
        "allowed_paths": allowed,
        "denied_paths": denied,
        "baseline": dict(baseline or {}),
    }


def check_tool(contract: Mapping[str, object], payload: Mapping[str, object]) -> dict[str, object]:
    """Decide whether a direct write/edit tool may execute."""

    normalized = _validated_contract(contract)
    tool_name = payload.get("toolName") or payload.get("tool_name")
    if tool_name not in {"write_file", "edit_file"}:
        return _allow()
    raw_paths = _tool_paths(payload)
    if not raw_paths:
        raise ScopeGuardError("direct scope tool did not expose a target path")
    violations = _policy_violations(normalized, raw_paths)
    if not violations:
        return _allow()
    return _block(violations, "direct tool target is outside the Run scope")


def audit_workspace(
    contract: Mapping[str, object],
    payload: Mapping[str, object] | None = None,
    *,
    owner_run_dir: Path | str | None = None,
) -> dict[str, object]:
    """Compare the current Git fingerprint with the Run baseline.

    The optional ``owner_run_dir`` is the explicit lifecycle owner passed to
    the fingerprint: only the current Run's own artifacts are excluded from
    the comparison, and a forged sibling run always stays visible and fails
    closed. When no owner is supplied the fingerprint hides nothing.
    """

    del payload
    normalized = _validated_contract(contract)
    root = normalized["repo_root"]
    owner = _owner_from_value(root, owner_run_dir)
    try:
        current = workspace_fingerprint(root, owner_run_dir=owner)
    except (OSError, RunRecordError, ValueError) as error:
        raise ScopeGuardError(
            f"workspace fingerprint failed closed: {error}",
            "SCOPE_FINGERPRINT_FAILED",
        ) from error
    current_paths = current.get("paths")
    if not isinstance(current_paths, Mapping):
        raise ScopeGuardError("workspace fingerprint has no path evidence")
    baseline = normalized["baseline"]
    baseline_paths = baseline.get("paths", {}) if isinstance(baseline, Mapping) else {}
    if not isinstance(baseline_paths, Mapping):
        raise ScopeGuardError("scope baseline paths are not an object")

    violations: list[str] = []
    for raw_path, evidence in current_paths.items():
        if not isinstance(raw_path, str) or not isinstance(evidence, Mapping):
            raise ScopeGuardError("workspace fingerprint contains malformed path evidence")
        try:
            canonical = canonicalize_path(root, raw_path)
        except ScopeGuardError:
            violations.append(_display_path(raw_path))
            continue
        if _is_allowed(normalized, canonical):
            continue
        previous = _baseline_value(baseline_paths, canonical)
        if previous is not None and previous == evidence:
            continue
        violations.append(canonical)

    for raw_path, previous in baseline_paths.items():
        if not isinstance(raw_path, str) or not isinstance(previous, Mapping):
            raise ScopeGuardError("scope baseline contains malformed path evidence")
        canonical = _display_path(raw_path)
        if _is_allowed(normalized, canonical):
            continue
        if _current_has_same_path(current_paths, canonical):
            continue
        previous_kind = previous.get("kind")
        if previous_kind in {"file", "symlink"}:
            candidate = root / Path(canonical)
            if not candidate.exists() and not candidate.is_symlink():
                violations.append(canonical)

    unique = sorted(set(violations), key=_path_sort_key)
    if unique:
        return _terminate(unique, "workspace audit detected an out-of-scope change")
    return _allow("workspace audit is inside the Run scope")


def load_scope_contract(path: Path) -> dict[str, object]:
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ScopeGuardError(f"could not load scope contract: {path}") from error
    return _validated_contract(value)


def _validated_contract(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ScopeGuardError("scope contract must be a JSON object")
    required = {"schema_version", "source", "repo_root", "allowed_paths", "denied_paths", "baseline"}
    if set(value) != required:
        raise ScopeGuardError("scope contract has missing or unknown keys")
    if value["schema_version"] != _SCOPE_SCHEMA_VERSION:
        raise ScopeGuardError("unsupported scope contract schema")
    source = value["source"]
    if not isinstance(source, str) or not source:
        raise ScopeGuardError("scope contract source is invalid")
    repo_root_value = value["repo_root"]
    if not isinstance(repo_root_value, (str, Path)):
        raise ScopeGuardError("scope contract repo_root is invalid")
    root = Path(repo_root_value).expanduser()
    if not root.is_absolute() or not root.is_dir():
        raise ScopeGuardError("scope contract repo_root must be an existing absolute directory")
    root = root.resolve(strict=True)
    allowed = _normalize_entries(root, _sequence(value["allowed_paths"], "allowed_paths"))
    denied = _normalize_entries(root, _sequence(value["denied_paths"], "denied_paths"))
    baseline = value["baseline"]
    if not isinstance(baseline, Mapping):
        raise ScopeGuardError("scope contract baseline must be an object")
    return {
        "schema_version": _SCOPE_SCHEMA_VERSION,
        "source": source,
        "repo_root": root,
        "allowed_paths": allowed,
        "denied_paths": denied,
        "baseline": dict(baseline),
    }


def _normalize_entries(root: Path, values: Sequence[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            raise ScopeGuardError("scope paths must be strings")
        directory = value.rstrip().replace("\\", "/").endswith("/")
        canonical = canonicalize_path(root, value)
        normalized = canonical + "/" if directory else canonical
        key = normalized.casefold() if os.name == "nt" else normalized
        if key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def _tool_paths(payload: Mapping[str, object]) -> list[str]:
    target = payload.get("input", payload)
    if isinstance(target, str):
        return [target]
    if not isinstance(target, Mapping):
        return []
    paths: list[str] = []
    for key in (
        "path",
        "file",
        "filename",
        "filePath",
        "file_path",
        "target",
        "targetPath",
        "target_path",
        "paths",
    ):
        if key not in target:
            continue
        value = target[key]
        if isinstance(value, str):
            paths.append(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            paths.extend(item for item in value if isinstance(item, str))
    return paths


def _policy_violations(contract: Mapping[str, object], raw_paths: Sequence[str]) -> list[str]:
    root = contract["repo_root"]
    violations: list[str] = []
    for raw_path in raw_paths:
        try:
            canonical = canonicalize_path(root, raw_path)
        except ScopeGuardError:
            violations.append(_display_path(raw_path))
            continue
        if not _is_allowed(contract, canonical):
            violations.append(canonical)
    return sorted(set(violations), key=_path_sort_key)


def _is_allowed(contract: Mapping[str, object], path: str) -> bool:
    allowed = contract["allowed_paths"]
    denied = contract["denied_paths"]
    if _matches_any(path, denied):
        return False
    return _matches_any(path, allowed)


def _matches_any(path: str, entries: object) -> bool:
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
        raise ScopeGuardError("scope entries must be a list")
    path_key = _path_key(path)
    for entry in entries:
        if not isinstance(entry, str):
            raise ScopeGuardError("scope entry must be a string")
        directory = entry.endswith("/")
        entry_key = _path_key(entry.rstrip("/"))
        if path_key == entry_key:
            return True
        if directory and path_key.startswith(entry_key + "/"):
            return True
    return False


def _baseline_value(paths: Mapping[object, object], path: str) -> object | None:
    for raw_path, value in paths.items():
        if isinstance(raw_path, str) and _path_key(raw_path) == _path_key(path):
            return value
    return None


def _current_has_same_path(paths: Mapping[object, object], path: str) -> bool:
    return any(
        isinstance(raw_path, str) and _path_key(raw_path) == _path_key(path)
        for raw_path in paths
    )


def _path_key(path: str) -> str:
    value = unicodedata.normalize("NFC", path.replace("\\", "/")).rstrip("/")
    return value.casefold() if os.name == "nt" else value


def _path_sort_key(path: str) -> tuple[str, str]:
    return (_path_key(path), path)


def _display_path(path: str) -> str:
    return unicodedata.normalize("NFC", path.strip().replace("\\", "/"))


def _sequence(value: object, name: str) -> Sequence[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ScopeGuardError(f"{name} must be a list")
    return value


def _allow(message: str = "path is inside the Run scope") -> dict[str, object]:
    return {"decision": "allow", "code": "", "paths": [], "message": message}


def _validate_scope_environment() -> None:
    """Reject unrecognized scope variables before evaluating the helper."""
    supplied = {
        key: value
        for key, value in os.environ.items()
        if key.startswith("SDD_CMDC_SCOPE_")
    }
    unexpected = set(supplied) - _SCOPE_ENV_NAMES
    if unexpected:
        raise ScopeGuardError(
            f"unexpected scope environment variables: {sorted(unexpected)}",
            "SCOPE_ENV_INVALID",
        )


def _env_run_owner(repo_root: Path) -> Path | None:
    """Return the run-owner authority from the validated Mod environment.

    The owner is a lifecycle-controlled absolute path; it is validated
    against the repository root and the safe run-directory format by
    ``workspace_fingerprint``, so child-controlled or ambiguous values fail
    closed instead of silently hiding paths.
    """
    raw = os.environ.get("SDD_CMDC_SCOPE_RUN_OWNER")
    if raw is None:
        return None
    path = Path(raw)
    if not path.is_absolute():
        raise ScopeGuardError(
            "run owner environment value must be an absolute path",
            "SCOPE_RUN_OWNER_INVALID",
        )
    return _owner_from_value(repo_root, path)


def _owner_from_value(
    repo_root: Path, owner_run_dir: Path | str | None
) -> Path | None:
    """Normalize an explicit run-owner value against a repository root.

    The raw value may be an absolute path or a repository-relative run path
    (``.superpowers/sdd/<workspace>/runs/<run_id>``); the resolved owner is
    validated against the repository root and the safe run-directory format
    by ``workspace_fingerprint``.
    """
    if owner_run_dir is None:
        return None
    root = Path(repo_root).expanduser().resolve(strict=True)
    if isinstance(owner_run_dir, Path):
        value = owner_run_dir.expanduser()
        return value if value.is_absolute() else root / value
    if not isinstance(owner_run_dir, str) or not owner_run_dir.strip():
        raise ScopeGuardError("run owner must be an absolute or repository-relative path")
    value = unicodedata.normalize("NFC", owner_run_dir.strip()).replace("\\", "/")
    if value.startswith("//"):
        raise ScopeGuardError(f"run owner is not a repository path: {owner_run_dir}")
    path_value = Path(value)
    path = path_value if path_value.is_absolute() else root / path_value
    return path


def _block(paths: Sequence[str], message: str) -> dict[str, object]:
    return {
        "decision": "block",
        "code": "SCOPE_VIOLATION",
        "paths": list(paths),
        "message": message,
    }


def _terminate(paths: Sequence[str], message: str) -> dict[str, object]:
    return {
        "decision": "terminate",
        "code": "SCOPE_VIOLATION",
        "paths": list(paths),
        "message": message,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run scope guard JSON helper")
    parser.add_argument("operation", choices=("check-tool", "audit-workspace"))
    parser.add_argument("--contract", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, Mapping):
            raise ScopeGuardError("helper input must be a JSON object")
        _validate_scope_environment()
        contract = load_scope_contract(Path(args.contract))
        decision = (
            check_tool(contract, payload)
            if args.operation == "check-tool"
            else audit_workspace(contract, payload, owner_run_dir=_env_run_owner(contract["repo_root"]))
        )
        print(json.dumps(decision, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, ScopeGuardError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
