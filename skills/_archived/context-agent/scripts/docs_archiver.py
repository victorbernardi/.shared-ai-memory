"""
Docs Active/Legacy Archiver.

Moves project folders between docs/active/ and docs/legacy/ based on
7-day modification activity. Bypass subdirs (decisions, walkthroughs,
business) do not count toward activity.
"""

import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Sequence

BYPASS_DIRS: frozenset[str] = frozenset({"decisions", "walkthroughs", "business"})
ROOT_EXEMPT_DIRS: frozenset[str] = BYPASS_DIRS | frozenset({"plans", "specs", "active", "legacy"})


@dataclass(frozen=True)
class ArchiveResult:
    project: str
    action: str  # "migrated" | "archived" | "kept_active" | "reactivated" | "collision"
    last_modified: datetime | None


def get_latest_mtime(project_dir: Path, bypass_dirs: frozenset[str]) -> datetime | None:
    """Return most recent mtime of files in project_dir, excluding bypass subdirs."""
    latest: datetime | None = None
    for item in project_dir.rglob("*"):
        if not item.is_file():
            continue
        relative = item.relative_to(project_dir)
        if relative.parts and relative.parts[0] in bypass_dirs:
            continue
        mtime = datetime.fromtimestamp(item.stat().st_mtime)
        if latest is None or mtime > latest:
            latest = mtime
    return latest


def _safe_move(src: Path, dest: Path) -> bool:
    """Move src to dest only if dest does not exist. Returns True on success."""
    if dest.exists():
        return False
    shutil.move(str(src), str(dest))
    return True


def run_archive(
    docs_root: Path,
    inactive_days: int = 7,
    bypass_dirs: frozenset[str] = BYPASS_DIRS,
    root_exempt_dirs: frozenset[str] = ROOT_EXEMPT_DIRS,
) -> list[ArchiveResult]:
    """
    Run one archive cycle:
    1. Migrate unclassified root project folders to active/.
    2. Archive inactive projects from active/ to legacy/.
    3. Reactivate recently modified projects from legacy/ to active/.
    """
    active_dir = docs_root / "active"
    legacy_dir = docs_root / "legacy"
    active_dir.mkdir(parents=True, exist_ok=True)
    legacy_dir.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.now() - timedelta(days=inactive_days)
    results: list[ArchiveResult] = []

    # 1. Migrate unclassified root projects to active/.
    # Projects migrated here are still subject to step 2 activity check,
    # so a stale project may be migrated and immediately archived in one run.
    for item in sorted(docs_root.iterdir()):
        if not item.is_dir():
            continue
        if item.name in root_exempt_dirs:
            continue
        dest = active_dir / item.name
        if _safe_move(item, dest):
            results.append(ArchiveResult(item.name, "migrated", None))

    # 2. Archive inactive projects from active/
    for project in sorted(active_dir.iterdir()):
        if not project.is_dir():
            continue
        mtime = get_latest_mtime(project, bypass_dirs)
        if mtime is None or mtime < cutoff:
            dest = legacy_dir / project.name
            if _safe_move(project, dest):
                results.append(ArchiveResult(project.name, "archived", mtime))
            else:
                results.append(ArchiveResult(project.name, "collision", mtime))
        else:
            results.append(ArchiveResult(project.name, "kept_active", mtime))

    # 3. Reactivate recently modified legacy projects
    for project in sorted(legacy_dir.iterdir()):
        if not project.is_dir():
            continue
        mtime = get_latest_mtime(project, bypass_dirs)
        if mtime is not None and mtime >= cutoff:
            dest = active_dir / project.name
            if _safe_move(project, dest):
                results.append(ArchiveResult(project.name, "reactivated", mtime))
            else:
                results.append(ArchiveResult(project.name, "collision", mtime))

    return results


def format_results(results: Sequence[ArchiveResult]) -> str:
    """Format archive results for CLI output."""
    lines: list[str] = []
    for r in results:
        date_str = r.last_modified.strftime("%Y-%m-%d") if r.last_modified else "sem arquivos"
        if r.action == "migrated":
            lines.append(f"  >> active/{r.project}  (migrado da raiz)")
        elif r.action == "archived":
            lines.append(f"  << legacy/{r.project}  (inativo desde {date_str})")
        elif r.action == "kept_active":
            lines.append(f"  -> active/{r.project}  (modificado em {date_str})")
        elif r.action == "reactivated":
            lines.append(f"  ** active/{r.project}  (reativado, modificado em {date_str})")
        elif r.action == "collision":
            lines.append(f"  !! COLISÃO {r.project}  (existe em active/ e legacy/)")

    archived = sum(1 for r in results if r.action == "archived")
    reactivated = sum(1 for r in results if r.action == "reactivated")
    migrated = sum(1 for r in results if r.action == "migrated")
    total_classified = len([r for r in results if r.action in ("archived", "kept_active", "reactivated")])

    summary = f"\n{total_classified} projetos verificados."
    if migrated:
        summary += f" {migrated} migrados da raiz."
    if archived:
        summary += f" {archived} arquivados."
    if reactivated:
        summary += f" {reactivated} reativados."

    return "\n".join(lines) + summary
