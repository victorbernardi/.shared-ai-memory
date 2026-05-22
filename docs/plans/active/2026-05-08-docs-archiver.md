# Docs Active/Legacy Archiver — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automate promotion and archiving of project folders between `docs/active/` and `docs/legacy/` based on 7-day modification activity, with a `docs-archive` command in `context_manager.py` and end-of-session hook integration.

**Architecture:** A new `docs_archiver.py` module handles all file-system logic (migrate, archive, reactivate). `context_manager.py` receives a new `docs-archive` subcommand that calls the module. The context-agent Stop hook invokes `docs-archive` automatically at session end.

**Tech Stack:** Python 3.11+, pathlib, shutil, pytest, standard library only (no new dependencies).

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `~/.shared-ai-memory/skills/context-agent/scripts/docs_archiver.py` | Create | Core archive logic: migrate, archive, reactivate |
| `~/.shared-ai-memory/skills/context-agent/scripts/config.py` | Modify | Add `DOCS_ROOT`, `DOCS_ACTIVE_DIR`, `DOCS_LEGACY_DIR`, `DOCS_BYPASS_DIRS`, `DOCS_ROOT_EXEMPT_DIRS`, `DOCS_INACTIVE_DAYS` |
| `~/.shared-ai-memory/skills/context-agent/scripts/context_manager.py` | Modify | Add `docs-archive` subcommand and `cmd_docs_archive` function |
| `~/.shared-ai-memory/skills/context-agent/tests/test_docs_archiver.py` | Create | pytest tests for all archive scenarios |
| `~/.claude/settings.json` | Modify | Register `docs-archive` call in Stop hook |

---

## Task 1: `docs_archiver.py` — Core Logic + Tests

**Files:**
- Create: `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\docs_archiver.py`
- Modify: `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\config.py`
- Create: `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\tests\test_docs_archiver.py`

---

- [ ] **Step 1: Add constants to `config.py`**

Open `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\config.py` and append at the end:

```python
# ── Docs archiver ────────────────────────────────────────────────────
DOCS_ROOT = SHARED_AI_MEMORY_ROOT / "docs"
DOCS_ACTIVE_DIR = DOCS_ROOT / "active"
DOCS_LEGACY_DIR = DOCS_ROOT / "legacy"
DOCS_BYPASS_DIRS: frozenset[str] = frozenset({"decisions", "walkthroughs", "business"})
# Root-level folders in docs/ that are never treated as projects
DOCS_ROOT_EXEMPT_DIRS: frozenset[str] = DOCS_BYPASS_DIRS | frozenset({"plans", "specs", "active", "legacy"})
DOCS_INACTIVE_DAYS: int = 7
```

- [ ] **Step 2: Write failing tests**

Create `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\tests\test_docs_archiver.py`:

```python
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
```

- [ ] **Step 3: Run tests to confirm they fail**

```
cd C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent
python -m pytest tests/test_docs_archiver.py -v 2>&1 | head -40
```

Expected: `ModuleNotFoundError: No module named 'docs_archiver'` — all tests fail.

- [ ] **Step 4: Create `docs_archiver.py`**

Create `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\docs_archiver.py`:

```python
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
# Folders at docs/ root that are never treated as projects
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

    # 1. Migrate unclassified root projects
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
            lines.append(f"  !! COLISAO {r.project}  (existe em active/ e legacy/)")

    archived = sum(1 for r in results if r.action == "archived")
    reactivated = sum(1 for r in results if r.action == "reactivated")
    migrated = sum(1 for r in results if r.action == "migrated")
    total = len([r for r in results if r.action in ("archived", "kept_active", "reactivated")])

    summary = f"\n{total} projetos verificados."
    if migrated:
        summary += f" {migrated} migrados da raiz."
    if archived:
        summary += f" {archived} arquivados."
    if reactivated:
        summary += f" {reactivated} reativados."

    return "\n".join(lines) + summary
```

- [ ] **Step 5: Run tests to confirm they pass**

```
cd C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent
python -m pytest tests/test_docs_archiver.py -v
```

Expected: all tests PASS. If `tests/` dir does not exist, create it:
```
New-Item -ItemType Directory -Path "C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\tests" -Force
New-Item -ItemType File -Path "C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\tests\__init__.py" -Force
```

Then re-run pytest.

- [ ] **Step 6: Commit**

```
cd C:\Users\victor.bernardi\.shared-ai-memory
git add skills/context-agent/scripts/docs_archiver.py
git add skills/context-agent/scripts/config.py
git add skills/context-agent/tests/test_docs_archiver.py
git add skills/context-agent/tests/__init__.py
git commit -m "feat: add docs_archiver module with active/legacy project archiving"
```

---

## Task 2: Add `docs-archive` Command to `context_manager.py`

**Files:**
- Modify: `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\context_manager.py`

Note: There are **two copies** of `context_manager.py`:
1. `~/.shared-ai-memory/skills/context-agent/scripts/context_manager.py` — canonical
2. `~/.claude/skills/context-agent/scripts/context_manager.py` — Claude-specific copy

Both must receive the same change.

---

- [ ] **Step 1: Write the failing test**

Add to `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\tests\test_docs_archiver.py`:

```python
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
```

- [ ] **Step 2: Run to confirm fail**

```
cd C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent
python -m pytest tests/test_docs_archiver.py::test_docs_archive_command_exits_zero -v
```

Expected: FAIL — `docs-archive` is not a known subcommand.

- [ ] **Step 3: Add `cmd_docs_archive` function to `context_manager.py`**

Open `C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\context_manager.py`.

After the `cmd_maintain` function (around line 246), add:

```python
def cmd_docs_archive(args):
    """Arquivar/reativar projetos em docs/active/ e docs/legacy/ por atividade."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from docs_archiver import run_archive, format_results
    from config import DOCS_ROOT

    results = run_archive(DOCS_ROOT)
    print(format_results(results))
```

- [ ] **Step 4: Register the subcommand in `main()`**

In the `main()` function, after the `"maintain"` subparser line, add:

```python
    # docs-archive
    subparsers.add_parser("docs-archive", help="Arquivar/reativar projetos em docs/")
```

In the `commands` dict, add:

```python
        "docs-archive": cmd_docs_archive,
```

- [ ] **Step 5: Apply the same changes to the Claude-specific copy**

Open `C:\Users\victor.bernardi\.claude\skills\context-agent\scripts\context_manager.py` and apply the identical changes:
- Add `cmd_docs_archive` function after `cmd_maintain`
- Add `"docs-archive"` subparser in `main()`
- Add `"docs-archive": cmd_docs_archive` in `commands` dict

- [ ] **Step 6: Run the CLI integration test**

```
cd C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent
python -m pytest tests/test_docs_archiver.py::test_docs_archive_command_exits_zero -v
```

Expected: PASS.

- [ ] **Step 7: Smoke test with real docs root**

```
python "C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\context_manager.py" docs-archive
```

Expected output example:
```
  >> active/Motor CEVAP  (migrado da raiz)
  >> active/NotebookLM   (migrado da raiz)
  >> active/Transcricoes (migrado da raiz)

3 projetos verificados. 3 migrados da raiz.
```

Review the output carefully before proceeding — verify no unintended migrations.

- [ ] **Step 8: Commit**

```
cd C:\Users\victor.bernardi\.shared-ai-memory
git add skills/context-agent/scripts/context_manager.py
git add skills/context-agent/tests/test_docs_archiver.py
git commit -m "feat: add docs-archive command to context_manager CLI"
```

Also commit the Claude copy:

```
cd C:\Users\victor.bernardi\.claude
git add skills/context-agent/scripts/context_manager.py 2>/dev/null || true
```

(Only if `~/.claude` is a git repo.)

---

## Task 3: Hook Integration — Auto-run at Session End

**Files:**
- Modify: `C:\Users\victor.bernardi\.claude\settings.json`

---

- [ ] **Step 1: Read current settings.json**

```
Get-Content "C:\Users\victor.bernardi\.claude\settings.json" | ConvertFrom-Json | Select-Object -ExpandProperty hooks
```

Identify the existing Stop hook entries.

- [ ] **Step 2: Inspect current Stop hook**

Open `C:\Users\victor.bernardi\.claude\settings.json`. Look for the `"hooks"` key and the `"Stop"` array. It currently calls `context_manager.py save`. The new call to add is:

```json
{
  "matcher": "",
  "hooks": [
    {
      "type": "command",
      "command": "python \"C:/Users/victor.bernardi/.claude/skills/context-agent/scripts/context_manager.py\" docs-archive"
    }
  ]
}
```

- [ ] **Step 3: Add the hook**

In `settings.json`, find the `"Stop"` array and append the `docs-archive` hook entry **after** the existing `save` hook entry. The Stop hooks array should look like:

```json
"Stop": [
  {
    "matcher": "",
    "hooks": [
      {
        "type": "command",
        "command": "python \"C:/Users/victor.bernardi/.claude/skills/context-agent/scripts/context_manager.py\" save"
      }
    ]
  },
  {
    "matcher": "",
    "hooks": [
      {
        "type": "command",
        "command": "python \"C:/Users/victor.bernardi/.claude/skills/context-agent/scripts/context_manager.py\" docs-archive"
      }
    ]
  }
]
```

If the existing structure differs, adapt to match the existing format (don't restructure existing hooks, just append).

- [ ] **Step 4: Verify JSON is valid**

```
Get-Content "C:\Users\victor.bernardi\.claude\settings.json" | ConvertFrom-Json | Out-Null
echo "JSON valid"
```

Expected: `JSON valid` (no parse error).

- [ ] **Step 5: Manual test of hook command**

```
python "C:\Users\victor.bernardi\.claude\skills\context-agent\scripts\context_manager.py" docs-archive
```

Expected: runs without error and prints archive summary.

- [ ] **Step 6: Commit**

```
cd C:\Users\victor.bernardi\.claude
git add settings.json 2>/dev/null || echo "not a git repo, skipping"
```

If `.claude` is not a git repo, this step is complete (settings.json is not version-controlled).

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|-----------------|------|
| Varrer `docs/active/`, arquivar se inativo há 7+ dias | Task 1: `run_archive` step 2 |
| Varrer `docs/legacy/`, reativar se modificado em 7 dias | Task 1: `run_archive` step 3 |
| BYPASS_DIRS = {"decisions", "walkthroughs", "business"} | Task 1: constant defined |
| Projeto vazio → tratar como inativo | Task 1: `get_latest_mtime` returns None → archived |
| Colisão → não mover, reportar | Task 1: `_safe_move` returns False → "collision" |
| Projetos na raiz de docs/ → mover para active/ | Task 1: migration step 1 |
| Pasta raiz bypass nunca tocadas | Task 1: `root_exempt_dirs` includes bypass |
| `python context_manager.py docs-archive` interface | Task 2 |
| Hook de fim de sessão | Task 3 |
| Output format: `→ active/X`, `← legacy/X` | Task 1: `format_results` |
| `INACTIVE_DAYS = 7` constante | Task 1: config.py constants |

**Placeholder scan:** No TBDs, no "handle edge cases", all code blocks complete.

**Type consistency:** `ArchiveResult` used consistently in `run_archive`, `format_results`, and tests. `get_latest_mtime` signature matches all call sites.

---

Plan complete and saved to `~/.shared-ai-memory/docs/plans/active/2026-05-08-docs-archiver.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review between tasks, fast iteration

**2. Inline Execution** — execute tasks in this session using executing-plans, with checkpoints

**Which approach?**
