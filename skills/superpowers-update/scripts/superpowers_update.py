"""Compare and synchronize Superpowers skills without touching Git state."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable


SOURCE_URL = "https://github.com/obra/superpowers.git"
SOURCE_BRANCH = "main"
DEFAULT_TARGET_NAMES = (
    ".shared-ai-memory/skills",
    ".agents/skills",
    ".codex/skills",
    ".claude/skills",
    ".commandcode/skills",
)


class SyncError(RuntimeError):
    """Raised when synchronization or post-copy verification fails."""


def normalize_content(data: bytes) -> bytes:
    """Normalize line endings while preserving all other bytes."""

    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def snapshot_skill(root: Path) -> dict[str, bytes]:
    """Return a deterministic, normalized snapshot of every file below root."""

    if not root.exists():
        return {}
    if not root.is_dir():
        return {}

    snapshot: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise SyncError(f"Symlink não suportado na skill: {path}")
        if path.is_file():
            snapshot[path.relative_to(root).as_posix()] = normalize_content(path.read_bytes())
    return snapshot


def compare_skill(source: dict[str, bytes], target: dict[str, bytes]) -> dict:
    """Classify canonical files; destination-only files are reported as extras."""

    source_normalized = {path: normalize_content(data) for path, data in source.items()}
    target_normalized = {path: normalize_content(data) for path, data in target.items()}
    source_paths = set(source_normalized)
    target_paths = set(target_normalized)
    missing = sorted(source_paths - target_paths)
    changed = sorted(
        path
        for path in source_paths & target_paths
        if source_normalized[path] != target_normalized[path]
    )
    extra = sorted(target_paths - source_paths)
    return {
        "missing": missing,
        "changed": changed,
        "extra": extra,
        "equal": not missing and not changed,
        "source_present": bool(source_normalized),
        "target_present": bool(target_normalized),
    }


def _skill_files(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        return {}
    return {
        path.name: path
        for path in sorted(root.iterdir(), key=lambda item: item.name)
        if path.is_dir() and not path.is_symlink() and (path / "SKILL.md").is_file()
    }


def discover_skill_dirs(repo_root: Path) -> dict[str, Path]:
    """Discover repository skills under repo_root/skills."""

    return _skill_files(repo_root / "skills")


def _build_comparisons(source_root: Path, targets: list[Path]) -> dict[str, dict[str, dict]]:
    source_skills = discover_skill_dirs(source_root)
    comparisons: dict[str, dict[str, dict]] = {}
    for target_root in targets:
        target_skills = _skill_files(target_root)
        names = sorted(set(source_skills) | set(target_skills))
        target_comparisons: dict[str, dict] = {}
        for name in names:
            source_dir = source_skills.get(name)
            target_dir = target_skills.get(name)
            source_snapshot = snapshot_skill(source_dir) if source_dir else {}
            target_snapshot = snapshot_skill(target_dir) if target_dir else {}
            comparison = compare_skill(source_snapshot, target_snapshot)
            comparison["source_present"] = source_dir is not None
            comparison["target_present"] = target_dir is not None
            target_comparisons[name] = comparison
        comparisons[str(target_root)] = target_comparisons
    return comparisons


def build_report(source_sha: str, comparisons: dict[str, dict[str, dict]]) -> dict:
    """Build a stable report from target-by-target comparison results."""

    new: set[str] = set()
    modified: set[str] = set()
    removed: set[str] = set()
    equal: set[str] = set()
    extras: dict[str, dict[str, list[str]]] = {}
    extra_skills: dict[str, list[str]] = {}
    report_comparisons: dict[str, dict[str, dict]] = {}
    for target, skill_comparisons in comparisons.items():
        target_report: dict[str, dict] = {}
        for name, comparison in skill_comparisons.items():
            source_present = comparison.get("source_present", bool(comparison["missing"]))
            target_present = comparison.get("target_present", bool(comparison["extra"]))
            if not source_present and target_present:
                if comparison.get("source_managed", False):
                    removed.add(name)
                    classification = "removed"
                else:
                    extra_skills.setdefault(target, []).append(name)
                    classification = "extra"
            elif source_present and not target_present:
                new.add(name)
                classification = "new"
            elif comparison["missing"] or comparison["changed"]:
                modified.add(name)
                classification = "modified"
            else:
                equal.add(name)
                classification = "equal"
            report_comparison = dict(comparison)
            report_comparison["classification"] = classification
            target_report[name] = report_comparison
            if comparison["extra"]:
                extras.setdefault(target, {})[name] = comparison["extra"]
        report_comparisons[target] = target_report

    changed = new | modified

    return {
        "status": "CHANGES_AVAILABLE" if changed or removed else "NO_OP",
        "source_sha": source_sha,
        "changed_skills": sorted(changed),
        "new_skills": sorted(new),
        "modified_skills": sorted(modified),
        "removed_skills": sorted(removed),
        "equal_skills": sorted(equal),
        "extra_skills": {target: sorted(names) for target, names in sorted(extra_skills.items())},
        "extra_files": extras,
        "comparisons": report_comparisons,
    }


def default_targets(home: Path) -> list[Path]:
    return [home / Path(relative) for relative in DEFAULT_TARGET_NAMES]


def _snapshot_digest(snapshot: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(snapshot):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(snapshot[relative])
        digest.update(b"\0")
    return digest.hexdigest()


def copy_skill_files(source_dir: Path, target_dir: Path) -> None:
    """Copy source files into a target skill while retaining destination extras."""

    if not source_dir.is_dir():
        raise SyncError(f"Fonte da skill inexistente: {source_dir}")
    if target_dir.exists() and not target_dir.is_dir():
        raise SyncError(f"Destino não é um diretório: {target_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)
    for source_path in sorted(source_dir.rglob("*")):
        if source_path.is_symlink():
            raise SyncError(f"Symlink não suportado na fonte: {source_path}")
        relative = source_path.relative_to(source_dir)
        target_path = target_dir / relative
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        elif source_path.is_file():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _backup_path(source: Path, backup: Path) -> str:
    if source.is_symlink():
        raise SyncError(f"Symlink não suportado no destino: {source}")
    if source.is_dir():
        shutil.copytree(source, backup)
        return "directory"
    shutil.copy2(source, backup)
    return "file"


def _restore_entry(destination: Path, backup: Path, existed: bool, kind: str | None) -> None:
    if destination.exists() or destination.is_symlink():
        _remove_path(destination)
    if not existed:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if kind == "directory":
        shutil.copytree(backup, destination)
    else:
        shutil.copy2(backup, destination)


def _sync_operations(operations: Iterable[tuple[Path, Path]]) -> None:
    operations = list(operations)
    if not operations:
        return

    with tempfile.TemporaryDirectory(prefix="superpowers-update-rollback-") as temporary:
        backup_root = Path(temporary)
        journal: list[tuple[Path, Path, bool, str | None]] = []
        try:
            for index, (source_dir, target_dir) in enumerate(operations):
                backup_path = backup_root / str(index)
                existed = target_dir.exists() or target_dir.is_symlink()
                kind = _backup_path(target_dir, backup_path) if existed else None
                journal.append((target_dir, backup_path, existed, kind))
                copy_skill_files(source_dir, target_dir)

                source_snapshot = snapshot_skill(source_dir)
                target_snapshot = snapshot_skill(target_dir)
                canonical_target = {
                    path: target_snapshot[path]
                    for path in source_snapshot
                    if path in target_snapshot
                }
                if _snapshot_digest(source_snapshot) != _snapshot_digest(canonical_target):
                    raise SyncError(f"Verificação pós-cópia falhou: {target_dir}")
        except Exception as error:
            rollback_errors: list[str] = []
            for destination, backup_path, existed, kind in reversed(journal):
                try:
                    _restore_entry(destination, backup_path, existed, kind)
                except Exception as rollback_error:  # pragma: no cover - defensive path
                    rollback_errors.append(str(rollback_error))
            detail = f"; rollback incompleto: {' | '.join(rollback_errors)}" if rollback_errors else ""
            if isinstance(error, SyncError):
                raise SyncError(f"{error}{detail}") from error
            raise SyncError(f"Falha na sincronização: {error}{detail}") from error


def sync_skill_to_targets(source_dir: Path, targets: list[Path]) -> None:
    """Synchronize one source skill to all target skill directories transactionally."""

    _sync_operations((source_dir, target_dir) for target_dir in targets)


def _write_json(report: dict, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def emit_report(report: dict, report_path: Path | None) -> None:
    """Print a report and persist it only when the caller explicitly asks."""

    print(json.dumps(report, ensure_ascii=False))
    if report_path is not None:
        _write_json(report, report_path)


def clone_source(url: str, branch: str, temp_root: Path) -> tuple[Path, str]:
    destination = temp_root / "source"
    command = [
        "git",
        "clone",
        "--depth",
        "1",
        "--branch",
        branch,
        "--single-branch",
        url,
        str(destination),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "erro desconhecido"
        raise RuntimeError(f"Falha ao clonar {url}@{branch}: {detail}")

    revision = subprocess.run(
        ["git", "-C", str(destination), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return destination, revision


def run_check(source_root: Path, targets: list[Path], source_sha: str = "local") -> dict:
    comparisons = _build_comparisons(source_root, targets)
    report = build_report(source_sha, comparisons)
    report["source_root"] = str(source_root)
    report["targets"] = [str(target) for target in targets]
    return report


def run_apply(source_root: Path, targets: list[Path], source_sha: str = "local") -> dict:
    report = run_check(source_root, targets, source_sha)
    if report["status"] == "NO_OP":
        return report

    source_skills = discover_skill_dirs(source_root)
    operations: list[tuple[Path, Path]] = []
    for target_name, skill_comparisons in report["comparisons"].items():
        target_root = Path(target_name)
        for skill_name, comparison in skill_comparisons.items():
            if (comparison["missing"] or comparison["changed"]) and comparison.get("source_present"):
                operations.append((source_skills[skill_name], target_root / skill_name))

    if not operations:
        return report

    try:
        _sync_operations(operations)
    except SyncError as error:
        report["status"] = "FAILED"
        report["error"] = str(error)
        return report

    verification = run_check(source_root, targets, source_sha)
    if verification["changed_skills"]:
        report["status"] = "FAILED"
        report["error"] = "Verificação final ainda encontrou skills divergentes."
        return report

    report["status"] = "UPDATED"
    report["post_update"] = verification["comparisons"]
    return report


def _source_revision(source_root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "local"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compara e sincroniza skills do obra/superpowers main."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)
    for mode in ("check", "apply"):
        command = subparsers.add_parser(mode, help=f"Executa o modo {mode}.")
        command.add_argument(
            "--target",
            action="append",
            type=Path,
            default=[],
            help="Destino adicional; pode ser repetido.",
        )
        command.add_argument(
            "--source-root",
            type=Path,
            help="Raiz local de clone para teste offline; deve conter skills/.",
        )
        command.add_argument(
            "--report",
            type=Path,
            help="Persiste o relatório neste caminho; por padrão ele não fica no repositório.",
        )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    targets: list[Path] = []
    for target in [*default_targets(Path.home()), *args.target]:
        resolved = target.expanduser().resolve()
        if resolved not in targets:
            targets.append(resolved)

    try:
        with tempfile.TemporaryDirectory(prefix="superpowers-update-") as temporary:
            temporary_root = Path(temporary)
            if args.source_root is not None:
                source_root = args.source_root.expanduser().resolve()
                source_sha = _source_revision(source_root)
            else:
                source_root, source_sha = clone_source(SOURCE_URL, SOURCE_BRANCH, temporary_root)

            if args.mode == "check":
                report = run_check(source_root, targets, source_sha)
            else:
                report = run_apply(source_root, targets, source_sha)

            _write_json(report, temporary_root / "report.json")
            emit_report(report, args.report.expanduser().resolve() if args.report else None)
            return 1 if report["status"] == "FAILED" else 0
    except Exception as error:
        report = {"status": "FAILED", "error": str(error)}
        emit_report(report, args.report.expanduser().resolve() if args.report else None)
        return 1


if __name__ == "__main__":
    sys.exit(main())
