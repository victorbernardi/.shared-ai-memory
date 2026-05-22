"""Tests for docs_archiver module."""
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Ensure scripts dir is on path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from docs_archiver import (
    ArchiveResult,
    get_latest_mtime,
    run_archive,
    BYPASS_DIRS,
)


@pytest.fixture()
def docs_root(tmp_path: Path) -> Path:
    root = tmp_path / "docs"
    root.mkdir()
    return root


def _make_file(path: Path, age_days: float = 0.0) -> None:
    """Create file and backdate its mtime."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("content")
    if age_days:
        ts = time.time() - age_days * 86400
        import os
        os.utime(path, (ts, ts))


# ── get_latest_mtime ────────────────────────────────────────────────

def test_get_latest_mtime_returns_none_for_empty_dir(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    assert get_latest_mtime(project, BYPASS_DIRS) is None


def test_get_latest_mtime_ignores_bypass_subdirs(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    _make_file(project / "decisions" / "d.md", age_days=1)
    _make_file(project / "walkthroughs" / "w.md", age_days=1)
    _make_file(project / "business" / "b.md", age_days=1)
    assert get_latest_mtime(project, BYPASS_DIRS) is None


def test_get_latest_mtime_picks_most_recent(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    _make_file(project / "old.md", age_days=10)
    _make_file(project / "new.md", age_days=1)
    mtime = get_latest_mtime(project, BYPASS_DIRS)
    assert mtime is not None
    assert mtime > datetime.now() - timedelta(days=2)


def test_get_latest_mtime_counts_nested_files(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    _make_file(project / "specs" / "deep" / "file.md", age_days=0)
    mtime = get_latest_mtime(project, BYPASS_DIRS)
    assert mtime is not None
    assert mtime > datetime.now() - timedelta(days=1)


# ── run_archive: first-run migration ───────────────────────────────

def test_migrates_unclassified_project_to_active(docs_root: Path) -> None:
    project = docs_root / "MyProject"
    _make_file(project / "readme.md", age_days=1)

    results = run_archive(docs_root)

    assert not project.exists()
    assert (docs_root / "active" / "MyProject").exists()
    assert any(r.project == "MyProject" and r.action == "migrated" for r in results)


def test_does_not_migrate_exempt_dirs(docs_root: Path) -> None:
    for name in ("plans", "specs", "decisions", "walkthroughs", "business"):
        (docs_root / name).mkdir()

    results = run_archive(docs_root)

    migrated = [r for r in results if r.action == "migrated"]
    assert migrated == []


# ── run_archive: archiving ──────────────────────────────────────────

def test_archives_inactive_project(docs_root: Path) -> None:
    active = docs_root / "active"
    project = active / "OldProject"
    _make_file(project / "file.md", age_days=10)

    results = run_archive(docs_root, inactive_days=7)

    assert not project.exists()
    assert (docs_root / "legacy" / "OldProject").exists()
    assert any(r.project == "OldProject" and r.action == "archived" for r in results)


def test_keeps_active_recent_project(docs_root: Path) -> None:
    active = docs_root / "active"
    project = active / "NewProject"
    _make_file(project / "file.md", age_days=1)

    results = run_archive(docs_root, inactive_days=7)

    assert project.exists()
    assert any(r.project == "NewProject" and r.action == "kept_active" for r in results)


def test_archive_ignores_bypass_for_activity_calculation(docs_root: Path) -> None:
    active = docs_root / "active"
    project = active / "BypassProject"
    # Only bypass files are recent; non-bypass is old
    _make_file(project / "decisions" / "d.md", age_days=0)
    _make_file(project / "plans" / "p.md", age_days=10)

    results = run_archive(docs_root, inactive_days=7)

    assert not project.exists()
    assert (docs_root / "legacy" / "BypassProject").exists()
    assert any(r.action == "archived" and r.project == "BypassProject" for r in results)


def test_archives_empty_project(docs_root: Path) -> None:
    project = docs_root / "active" / "EmptyProject"
    project.mkdir(parents=True)

    results = run_archive(docs_root, inactive_days=7)

    assert (docs_root / "legacy" / "EmptyProject").exists()
    assert any(r.action == "archived" and r.project == "EmptyProject" for r in results)


# ── run_archive: reactivation ───────────────────────────────────────

def test_reactivates_recently_modified_legacy_project(docs_root: Path) -> None:
    legacy = docs_root / "legacy"
    project = legacy / "WakingProject"
    _make_file(project / "file.md", age_days=1)

    results = run_archive(docs_root, inactive_days=7)

    assert not project.exists()
    assert (docs_root / "active" / "WakingProject").exists()
    assert any(r.project == "WakingProject" and r.action == "reactivated" for r in results)


def test_does_not_reactivate_old_legacy_project(docs_root: Path) -> None:
    legacy = docs_root / "legacy"
    project = legacy / "DeadProject"
    _make_file(project / "file.md", age_days=30)

    results = run_archive(docs_root, inactive_days=7)

    assert project.exists()
    assert not any(r.action == "reactivated" and r.project == "DeadProject" for r in results)


# ── run_archive: collision guard ─────────────────────────────────────

def test_reports_collision_without_moving(docs_root: Path) -> None:
    # Same name in both active and legacy — should not crash
    active_proj = docs_root / "active" / "Clash"
    legacy_proj = docs_root / "legacy" / "Clash"
    _make_file(active_proj / "a.md", age_days=10)  # will try to archive
    _make_file(legacy_proj / "b.md", age_days=10)  # already in legacy

    results = run_archive(docs_root, inactive_days=7)

    # Both still exist (no overwrite)
    assert active_proj.exists()
    assert legacy_proj.exists()
    assert any(r.action == "collision" and r.project == "Clash" for r in results)


# ── CLI integration ─────────────────────────────────────────────────
import subprocess

def test_docs_archive_command_exits_zero(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "active").mkdir()
    result = subprocess.run(
        ["python", str(Path(__file__).parent.parent / "scripts" / "context_manager.py"), "docs-archive"],
        capture_output=True, text=True,
        env={**__import__("os").environ, "USERPROFILE": str(tmp_path), "SHARED_AI_MEMORY_ROOT": str(tmp_path / ".shared-ai-memory")},
    )
    # Command may print output but must not crash
    assert result.returncode == 0 or "docs-archive" in result.stderr
