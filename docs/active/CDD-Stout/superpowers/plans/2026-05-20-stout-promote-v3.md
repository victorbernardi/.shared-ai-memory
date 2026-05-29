# stout_promote v3.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `stout_promote.py` (v2.2 → v3.0) so it discovers artifacts across **all** project sessions from the correct Antigravity brain paths (§2.1), filters sessions by project identity using both folder name AND absolute path (CON-004), names deterministically with the git branch slug, deduplicates by SHA-256 against a persistent log (CON-001), and ships `post_approve.py` for automated promotion + commit after plan approval.

**Architecture:**

- **Pure helpers** (no I/O coupling): `slugify()`, `detect_type()` (first 5 lines only), `file_sha256()`.
- **Log layer:** `load_promote_log()` / `save_promote_log()` over `docs/.promote_log.json` keyed by content hash.
- **Discovery layer:** `is_session_for_current_project()` (name AND abs-path match) + `discover_sessions()` implementing the §2.1 environment map. This is the **core of the fix** — the old code only read the wrong/legacy path and only the latest session.
- **Orchestration:** `promote_artifacts(project_root=None, branch=None, session_dirs=None)` — callable with **zero args** for the real script (discovers everything) and with injected args for tests.
- **Wrapper:** `post_approve.py` reuses `promote_artifacts()` for both real and `--dry-run` paths (no duplicated scan logic).

**Tech Stack:** Python 3.8+, pathlib, hashlib (SHA-256), json, datetime, subprocess (git).

---

## Critical decisions baked into this plan (fixes from review)

| Fix | Decision |
|-----|----------|
| F1 | `discover_sessions()` implements §2.1 paths: scan `~/.gemini/antigravity-cli/brain/*` (root layout) and `~/.shared-ai-memory/brain/*/artifacts/` (fallback). **Never** scan `~/.gemini/antigravity/brain` or `antigravity-ide`. |
| F2 | `promote_artifacts()` keeps a **zero-arg** call path; `__main__` calls it bare. Args are optional injection points for tests. |
| F3 | `is_session_for_current_project()` matches on `project_root.name` AND `str(project_root).lower()` (CON-004). |
| F4 | `detect_type()` reads **only the first 5 lines**, lowercased+stripped, before searching markers. |
| F5 | Version resolution globs `{tipo}_*_{slug}_v*.md` (date-agnostic), takes max existing `N`, compares hash. Date never affects collision. |
| F6 | Test computes expected date from the same `datetime.fromtimestamp(mtime)` it sets — no hardcoded epoch. |
| F7 | `post_approve.py` has **no TODO stubs**; it calls `discover_sessions()` via `promote_artifacts()`. |
| F8 | Claude memory promotion retained: `*.md` from the project's Claude memory dir → `docs/concepts/`. |
| F9 | `--dry-run` calls `promote_artifacts(dry_run=True)` — same code path, no copy/commit. |
| F10 | Commit message format: `docs: Promote {summary}` where summary lists `{tipo}_{slug}_v{N}` per spec §3.6. |
| F11 | Tests inject `project_root`/`branch`/`session_dirs` as **arguments** (no dead `monkeypatch.setenv`). |
| F12 | Automated test covers `post_approve` commit path using a real temp git repo. |

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `tests/test_stout_promote_v3.py` | Create | TDD suite, one behavior per cycle, integration-style |
| `src/tools/stout_promote.py` | Rewrite | v3.0 pure helpers + discovery + orchestration |
| `src/tools/post_approve.py` | Create | Wrapper: real promote + commit, and `--dry-run` |
| `GEMINI.md` | Modify | Document the post-approval workflow |

---

## Task 1: slugify() — tracer bullet

**Files:**

- Create: `tests/test_stout_promote_v3.py`
- Modify: `src/tools/stout_promote.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_stout_promote_v3.py`:

```python
"""TDD: stout_promote v3.0 — vertical slices, one behavior per cycle."""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

import pytest

# Make src/tools importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "tools"))

class TestSlugify:
    def test_converts_slashes_to_hyphens(self):
        from stout_promote import slugify
        assert slugify("feature/new-thing") == "feature-new-thing"

    def test_removes_parentheses(self):
        from stout_promote import slugify
        assert slugify("fix/bug-(m3)") == "fix-bug-m3"

    def test_collapses_double_hyphens(self):
        from stout_promote import slugify
        assert slugify("fix--double--hyphen") == "fix-double-hyphen"

    def test_respects_max_length(self):
        from stout_promote import slugify
        assert len(slugify("fix/" + "very-long-branch-name-" * 5)) <= 60

    def test_lowercases_input(self):
        from stout_promote import slugify
        assert slugify("Fix/MyFeature") == "fix-myfeature"

    def test_strips_trailing_hyphens(self):
        from stout_promote import slugify
        assert not slugify("feature/" + "a-" * 40).endswith("-")

    def test_preserves_underscores(self):
        from stout_promote import slugify
        assert slugify("fix/feature_name") == "fix-feature_name"
```text

- [ ] **Step 2: Run — expect failure**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestSlugify -v`
Expected: FAIL `cannot import name 'slugify'`

- [ ] **Step 3: Create v3.0 skeleton with slugify()**

Rewrite `src/tools/stout_promote.py` header (replace the whole file's top section; full file is assembled across Tasks 1–6):

```python
"""Stout Artifact Promoter v3.0

Discovers AI-generated artifacts from Antigravity/Gemini/Claude sessions and
promotes them into the project's docs/ tree with deterministic, deduplicated
naming. See docs/specs/spec_2026-05-20_fix-stout-promote-antigravity-brain-path_v1.md
"""
import io
import os
import re
import sys
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def slugify(text: str, max_len: int = 60) -> str:
    """Sanitize a git branch name to a filesystem-safe slug."""
    text = text.lower()
    text = text.replace("/", "-").replace("\\", "-")
    text = re.sub(r"[^a-z0-9\-_]", "", text)
    text = re.sub(r"-{2,}", "-", text)
    return text[:max_len].strip("-")
```text

- [ ] **Step 4: Run — expect pass**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestSlugify -v`
Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/test_stout_promote_v3.py src/tools/stout_promote.py
git commit -m "feat: stout_promote v3.0 skeleton with slugify()"
```text

---

## Task 2: detect_type() — first 5 lines only (F4)

**Files:**

- Modify: `tests/test_stout_promote_v3.py`
- Modify: `src/tools/stout_promote.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_stout_promote_v3.py`:

```python
class TestDetectType:
    def test_detects_plan_by_content_marker(self, tmp_path):
        from stout_promote import detect_type
        f = tmp_path / "implementation_plan.md"
        f.write_text("# Implementation Plan\n\nDetails", encoding="utf-8")
        assert detect_type(f) == "plan"

    def test_detects_spec_by_content_marker(self, tmp_path):
        from stout_promote import detect_type
        f = tmp_path / "anything.md"
        f.write_text("tipo: spec\n\nRequirements", encoding="utf-8")
        assert detect_type(f) == "spec"

    def test_detects_walkthrough_by_content(self, tmp_path):
        from stout_promote import detect_type
        f = tmp_path / "anything.md"
        f.write_text("# Walkthrough\n\nSteps", encoding="utf-8")
        assert detect_type(f) == "walkthrough"

    def test_ignores_marker_after_first_5_lines(self, tmp_path):
        """A plan that merely MENTIONS '# spec' in the body stays a plan (F4)."""
        from stout_promote import detect_type
        f = tmp_path / "implementation_plan.md"
        f.write_text(
            "# Implementation Plan\n\nline2\nline3\nline4\nline5\n# spec\nbody",
            encoding="utf-8",
        )
        assert detect_type(f) == "plan"

    def test_falls_back_to_filename(self, tmp_path):
        from stout_promote import detect_type
        f = tmp_path / "implementation_plan.md"
        f.write_text("random content no marker", encoding="utf-8")
        assert detect_type(f) == "plan"

    def test_defaults_to_concept(self, tmp_path):
        from stout_promote import detect_type
        f = tmp_path / "random.md"
        f.write_text("random markdown", encoding="utf-8")
        assert detect_type(f) == "concept"

    def test_case_insensitive_marker(self, tmp_path):
        from stout_promote import detect_type
        f = tmp_path / "doc.md"
        f.write_text("TIPO: SPEC\n\nContent", encoding="utf-8")
        assert detect_type(f) == "spec"
```text

- [ ] **Step 2: Run — expect failure**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestDetectType -v`
Expected: FAIL `cannot import name 'detect_type'`

- [ ] **Step 3: Implement detect_type()**

Append to `src/tools/stout_promote.py`:

```python
TYPE_MARKERS = {
    "plan": ["tipo: plan", "type: plan", "# plano de implementação", "# implementation plan"],
    "spec": ["tipo: spec", "type: spec", "# spec técnica", "# spec"],
    "walkthrough": ["tipo: walkthrough", "type: walkthrough", "# walkthrough"],
}

FILENAME_HINTS = {
    "implementation_plan": "plan",
    "spec": "spec",
    "walkthrough": "walkthrough",
}

def detect_type(filepath: Path) -> str:
    """Classify an artifact: content markers (first 5 lines) → filename → 'concept'."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
            head = "".join(fh.readline() for _ in range(5)).lower().strip()
        for artifact_type, markers in TYPE_MARKERS.items():
            if any(m.lower() in head for m in markers):
                return artifact_type
    except OSError:
        pass

    name = filepath.stem.lower()
    for hint, hint_type in FILENAME_HINTS.items():
        if hint in name:
            return hint_type
    return "concept"
```text

- [ ] **Step 4: Run — expect pass**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestDetectType -v`
Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/test_stout_promote_v3.py src/tools/stout_promote.py
git commit -m "feat: detect_type() classifies by first 5 lines then filename"
```text

---

## Task 3: SHA-256 + promote log helpers

**Files:**

- Modify: `tests/test_stout_promote_v3.py`
- Modify: `src/tools/stout_promote.py`

- [ ] **Step 1: Write failing tests**

Append:

```python
class TestLogAndHash:
    def test_sha256_is_stable_for_same_content(self, tmp_path):
        from stout_promote import file_sha256
        a = tmp_path / "a.md"; a.write_text("same", encoding="utf-8")
        b = tmp_path / "b.md"; b.write_text("same", encoding="utf-8")
        assert file_sha256(a) == file_sha256(b)

    def test_sha256_differs_for_different_content(self, tmp_path):
        from stout_promote import file_sha256
        a = tmp_path / "a.md"; a.write_text("x", encoding="utf-8")
        b = tmp_path / "b.md"; b.write_text("y", encoding="utf-8")
        assert file_sha256(a) != file_sha256(b)

    def test_load_log_returns_empty_when_absent(self, tmp_path):
        from stout_promote import load_promote_log
        log = load_promote_log(tmp_path)
        assert log == {"promotions": [], "content_hashes": {}}

    def test_save_then_load_roundtrip(self, tmp_path):
        from stout_promote import load_promote_log, save_promote_log
        log = {"promotions": [{"src": "x"}], "content_hashes": {"abc": "y"}}
        save_promote_log(tmp_path, log)
        assert load_promote_log(tmp_path) == log
        assert (tmp_path / "docs" / ".promote_log.json").exists()
```text

- [ ] **Step 2: Run — expect failure**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestLogAndHash -v`
Expected: FAIL on imports

- [ ] **Step 3: Implement helpers**

Append to `src/tools/stout_promote.py`:

```python
def file_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def _log_path(project_root: Path) -> Path:
    return project_root / "docs" / ".promote_log.json"

def load_promote_log(project_root: Path) -> dict:
    path = _log_path(project_root)
    if path.exists():
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"promotions": [], "content_hashes": {}}

def save_promote_log(project_root: Path, log: dict) -> None:
    path = _log_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)
```text

- [ ] **Step 4: Run — expect pass**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestLogAndHash -v`
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/test_stout_promote_v3.py src/tools/stout_promote.py
git commit -m "feat: add file_sha256 and promote-log persistence"
```text

---

## Task 4: Session discovery — THE CORE FIX (§2.1 + CON-004)

**Files:**

- Modify: `tests/test_stout_promote_v3.py`
- Modify: `src/tools/stout_promote.py`

- [ ] **Step 1: Write failing tests**

Append:

```python
class TestSessionFilter:
    def test_matches_by_project_name_in_overview(self, tmp_path):
        from stout_promote import is_session_for_current_project
        project_root = tmp_path / "MyProject"
        project_root.mkdir()
        session = tmp_path / "sessions" / "s1"
        logs = session / ".system_generated" / "logs"
        logs.mkdir(parents=True)
        (logs / "overview.txt").write_text("working on MyProject today", encoding="utf-8")
        assert is_session_for_current_project(session, project_root) is True

    def test_matches_by_absolute_path(self, tmp_path):
        from stout_promote import is_session_for_current_project
        project_root = tmp_path / "Proj"
        project_root.mkdir()
        session = tmp_path / "sessions" / "s1"
        logs = session / ".system_generated" / "logs"
        logs.mkdir(parents=True)
        (logs / "overview.txt").write_text(str(project_root).lower(), encoding="utf-8")
        assert is_session_for_current_project(session, project_root) is True

    def test_rejects_unrelated_session(self, tmp_path):
        from stout_promote import is_session_for_current_project
        project_root = tmp_path / "Alpha"
        project_root.mkdir()
        session = tmp_path / "sessions" / "s1"
        logs = session / ".system_generated" / "logs"
        logs.mkdir(parents=True)
        (logs / "overview.txt").write_text("totally different project Beta", encoding="utf-8")
        assert is_session_for_current_project(session, project_root) is False

class TestDiscoverSessions:
    def test_scans_antigravity_cli_root_layout(self, tmp_path, monkeypatch):
        """antigravity-cli brain sessions expose artifacts at session root (§2.1)."""
        from stout_promote import discover_sessions
        home = tmp_path / "home"
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        project_root = tmp_path / "Proj"
        project_root.mkdir()

        sess = home / ".gemini" / "antigravity-cli" / "brain" / "abc"
        logs = sess / ".system_generated" / "logs"; logs.mkdir(parents=True)
        (logs / "overview.txt").write_text("Proj", encoding="utf-8")
        (sess / "implementation_plan.md").write_text("# Implementation Plan", encoding="utf-8")

        found = discover_sessions(project_root)
        assert any(src_dir == sess for src_dir, origin in found)

    def test_ignores_antigravity_ide_path(self, tmp_path, monkeypatch):
        """antigravity (IDE) and antigravity-ide must NOT be scanned (§2.1)."""
        from stout_promote import discover_sessions
        home = tmp_path / "home"
        monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
        project_root = tmp_path / "Proj"; project_root.mkdir()

        sess = home / ".gemini" / "antigravity" / "brain" / "ide1"
        logs = sess / ".system_generated" / "logs"; logs.mkdir(parents=True)
        (logs / "overview.txt").write_text("Proj", encoding="utf-8")
        (sess / "implementation_plan.md").write_text("# Implementation Plan", encoding="utf-8")

        found = discover_sessions(project_root)
        assert all("antigravity\\brain" not in str(src) and "antigravity/brain" not in str(src)
                   for src, _ in found)
```text

- [ ] **Step 2: Run — expect failure**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestSessionFilter tests/test_stout_promote_v3.py::TestDiscoverSessions -v`
Expected: FAIL on imports

- [ ] **Step 3: Implement discovery (§2.1) + filter (CON-004)**

Append to `src/tools/stout_promote.py`:

```python
def is_session_for_current_project(session_dir: Path, project_root: Path) -> bool:
    """True if a session belongs to the current project.

    CON-004: match on BOTH project folder name AND absolute path to avoid
    collisions between same-named folders in different locations.
    """
    project_name = project_root.name.lower()
    project_path = str(project_root).lower()

    overview = session_dir / ".system_generated" / "logs" / "overview.txt"
    if overview.exists():
        try:
            text = overview.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            text = ""
        if project_path in text:
            return True
        if project_name in text:
            return True

    plans = session_dir / "plans"
    if plans.exists():
        for f in plans.iterdir():
            if project_name in f.name.lower():
                return True
    return False

def discover_sessions(project_root: Path) -> list:
    """Return [(src_dir, origin), ...] for the current project, per spec §2.1.

    Scanned:
      ~/.gemini/antigravity-cli/brain/<id>/            (artifacts at root)
      ~/.shared-ai-memory/brain/<id>/artifacts/        (legacy fallback)
      ~/.gemini/.../tmp/.../plans/                      (Gemini TMP plans)
      Claude memory dir                                 (concepts)
    Explicitly NOT scanned: ~/.gemini/antigravity/brain, antigravity-ide.
    """
    home = Path.home()
    found = []

    brain_roots = [
        (home / ".gemini" / "antigravity-cli" / "brain", "root"),
        (home / ".shared-ai-memory" / "brain", "artifacts"),
    ]
    for base, layout in brain_roots:
        if not base.exists():
            continue
        for session in sorted(base.iterdir(), key=os.path.getmtime, reverse=True):
            if not session.is_dir():
                continue
            src_dir = session if layout == "root" else session / "artifacts"
            if not src_dir.exists():
                continue
            if is_session_for_current_project(session, project_root):
                found.append((src_dir, f"brain-{layout}"))

    claude_dir = get_claude_memory_dir(project_root)
    if claude_dir:
        found.append((claude_dir, "claude"))

    return found
```text

- [ ] **Step 4: Run — expect pass**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestSessionFilter tests/test_stout_promote_v3.py::TestDiscoverSessions -v`
Expected: `5 passed`

(Note: `get_claude_memory_dir` is implemented in Task 5; until then the call is forward-referenced — implement Task 5 before running discover_sessions outside these tests. To keep this task green in isolation, also add the Task 5 `get_claude_memory_dir` + `encode_claude_path` now.)

- [ ] **Step 5: Add Claude memory locator (F8) so discover_sessions resolves**

Append to `src/tools/stout_promote.py`:

```python
def encode_claude_path(path_str: str) -> str:
    return (path_str.replace(":\\", "--").replace("\\", "-")
            .replace(":", "--").replace("/", "-"))

def get_claude_memory_dir(project_root: Path):
    root = Path.home() / ".claude" / "projects"
    if not root.exists():
        return None
    encoded = encode_claude_path(str(project_root))
    candidate = root / encoded / "memory"
    if candidate.exists():
        return candidate
    for d in root.iterdir():
        if d.is_dir() and project_root.name.lower() in d.name.lower():
            mem = d / "memory"
            if mem.exists():
                return mem
    return None
```text

- [ ] **Step 6: Commit**

```bash
git add tests/test_stout_promote_v3.py src/tools/stout_promote.py
git commit -m "feat: brain-path session discovery and project filter (core fix)"
```text

---

## Task 5: Deterministic naming + version resolution (F5, F6)

**Files:**

- Modify: `tests/test_stout_promote_v3.py`
- Modify: `src/tools/stout_promote.py`

- [ ] **Step 1: Write failing tests**

Append:

```python
class TestNaming:
    def test_filename_format_v1(self, tmp_path):
        from stout_promote import get_promoted_filename
        f = tmp_path / "implementation_plan.md"
        f.write_text("# Implementation Plan", encoding="utf-8")
        mtime = datetime(2026, 5, 20, 12, 0, 0).timestamp()
        os.utime(f, (mtime, mtime))
        expected_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        name = get_promoted_filename(f, "fix/stout-promote-antigravity-brain-path")
        assert name == f"plan_{expected_date}_fix-stout-promote-antigravity-brain-path_v1.md"

    def test_next_version_ignores_date_in_existing_files(self, tmp_path):
        """Version detection must not depend on the date segment (F5)."""
        from stout_promote import next_version, slugify
        dest = tmp_path / "plans"; dest.mkdir()
        slug = slugify("fix/test")
        (dest / f"plan_2026-01-01_{slug}_v1.md").write_text("old", encoding="utf-8")
        (dest / f"plan_2026-02-02_{slug}_v2.md").write_text("older", encoding="utf-8")
        assert next_version(dest, "plan", slug) == 3
```text

- [ ] **Step 2: Run — expect failure**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestNaming -v`
Expected: FAIL on imports

- [ ] **Step 3: Implement naming + version resolution**

Append to `src/tools/stout_promote.py`:

```python
def next_version(dest_dir: Path, artifact_type: str, slug: str) -> int:
    """Highest existing version for {type}_*_{slug}_v*.md, plus one (date-agnostic)."""
    pattern = re.compile(rf"^{re.escape(artifact_type)}_.+_{re.escape(slug)}_v(\d+)\.md$")
    highest = 0
    if dest_dir.exists():
        for f in dest_dir.iterdir():
            m = pattern.match(f.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1

def get_promoted_filename(filepath: Path, branch: str, version: int = 1) -> str:
    """{tipo}_{YYYY-MM-DD(mtime)}_{branch-slug}_v{N}.md"""
    artifact_type = detect_type(filepath)
    date_str = datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%Y-%m-%d")
    return f"{artifact_type}_{date_str}_{slugify(branch)}_v{version}.md"
```text

- [ ] **Step 4: Run — expect pass**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestNaming -v`
Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/test_stout_promote_v3.py src/tools/stout_promote.py
git commit -m "feat: deterministic naming with date-agnostic version resolution"
```text

---

## Task 6: promote_artifacts() orchestration (F1, F2, F9 hook, CON-001)

**Files:**

- Modify: `tests/test_stout_promote_v3.py`
- Modify: `src/tools/stout_promote.py`

- [ ] **Step 1: Write failing tests**

Append:

```python
DEST_SUBDIR = {"plan": "plans", "spec": "specs", "walkthrough": "walkthroughs", "concept": "concepts"}

def _make_brain_session(tmp_path, project_root, files: dict):
    """Create an antigravity-cli-style session whose overview names the project."""
    sess = tmp_path / "brain" / "sess1"
    logs = sess / ".system_generated" / "logs"; logs.mkdir(parents=True)
    (logs / "overview.txt").write_text(project_root.name, encoding="utf-8")
    for fname, content in files.items():
        (sess / fname).write_text(content, encoding="utf-8")
    return sess

class TestPromoteArtifacts:
    def test_promotes_and_is_idempotent(self, tmp_path):
        from stout_promote import promote_artifacts
        project_root = tmp_path / "Proj"; project_root.mkdir()
        sess = _make_brain_session(tmp_path, project_root,
                                    {"implementation_plan.md": "# Implementation Plan\nbody"})
        c1 = promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        assert c1 == 1
        c2 = promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        assert c2 == 0  # CON-006

    def test_modified_content_makes_v2(self, tmp_path):
        from stout_promote import promote_artifacts
        project_root = tmp_path / "Proj"; project_root.mkdir()
        sess = _make_brain_session(tmp_path, project_root,
                                    {"implementation_plan.md": "# Implementation Plan\nv1"})
        promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        (sess / "implementation_plan.md").write_text("# Implementation Plan\nv2", encoding="utf-8")
        promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        v2 = list((project_root / "docs" / "plans").glob("*_v2.md"))
        assert len(v2) == 1

    def test_reverted_content_no_v3(self, tmp_path):
        from stout_promote import promote_artifacts
        project_root = tmp_path / "Proj"; project_root.mkdir()
        sess = _make_brain_session(tmp_path, project_root,
                                    {"implementation_plan.md": "# Implementation Plan\norig"})
        promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        (sess / "implementation_plan.md").write_text("# Implementation Plan\nmodified", encoding="utf-8")
        promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        (sess / "implementation_plan.md").write_text("# Implementation Plan\norig", encoding="utf-8")
        promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        assert list((project_root / "docs" / "plans").glob("*_v3.md")) == []  # CON-001

    def test_ignores_task_and_resolved(self, tmp_path):
        from stout_promote import promote_artifacts
        project_root = tmp_path / "Proj"; project_root.mkdir()
        sess = _make_brain_session(tmp_path, project_root, {
            "task.md": "# Task",
            "implementation_plan.md.resolved": "# Resolved",
            "implementation_plan.md": "# Implementation Plan",
        })
        promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        plans = list((project_root / "docs" / "plans").glob("*.md"))
        assert len(plans) == 1
        assert not list((project_root / "docs").rglob("*resolved*"))
        assert not list((project_root / "docs").rglob("*task*"))

    def test_promotes_spec_to_specs(self, tmp_path):
        from stout_promote import promote_artifacts
        project_root = tmp_path / "Proj"; project_root.mkdir()
        sess = _make_brain_session(tmp_path, project_root,
                                    {"spec.md": "tipo: spec\n# Technical Spec"})
        promote_artifacts(project_root, "fix/test", [(sess, "brain-root")])
        specs = list((project_root / "docs" / "specs").glob("*.md"))
        assert len(specs) == 1 and specs[0].name.startswith("spec_")

    def test_dry_run_copies_nothing(self, tmp_path):
        from stout_promote import promote_artifacts
        project_root = tmp_path / "Proj"; project_root.mkdir()
        sess = _make_brain_session(tmp_path, project_root,
                                    {"implementation_plan.md": "# Implementation Plan"})
        count = promote_artifacts(project_root, "fix/test", [(sess, "brain-root")], dry_run=True)
        assert count == 1  # would-promote count
        assert not (project_root / "docs" / "plans").exists()
        assert not (project_root / "docs" / ".promote_log.json").exists()
```text

- [ ] **Step 2: Run — expect failure**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestPromoteArtifacts -v`
Expected: FAIL on imports

- [ ] **Step 3: Implement orchestration**

Append to `src/tools/stout_promote.py`:

```python
IGNORED_NAMES = {"task.md", "implementation_plan.md.resolved"}
DEST_SUBDIR = {"plan": "plans", "spec": "specs", "walkthrough": "walkthroughs", "concept": "concepts"}

def get_current_branch(project_root: Path) -> str:
    try:
        out = subprocess.run(["git", "branch", "--show-current"],
                             cwd=project_root, capture_output=True, text=True)
        branch = out.stdout.strip()
        if branch:
            return branch
    except (OSError, subprocess.SubprocessError):
        pass
    return project_root.name

def promote_artifacts(project_root=None, branch=None, session_dirs=None, dry_run=False) -> int:
    """Promote artifacts from all project sessions. Returns count promoted (or would-promote).

    Zero-arg callable: discovers project_root (cwd), branch (git), and sessions (§2.1).
    """
    project_root = Path(project_root) if project_root else Path(os.getcwd())
    branch = branch or get_current_branch(project_root)
    if session_dirs is None:
        session_dirs = discover_sessions(project_root)

    log = load_promote_log(project_root)
    seen_hashes = set(log.get("content_hashes", {}).keys())
    promoted = 0

    for src_dir, _origin in session_dirs:
        if not Path(src_dir).exists():
            continue
        for artifact in sorted(Path(src_dir).rglob("*.md")):
            if artifact.name in IGNORED_NAMES:
                continue
            content_hash = file_sha256(artifact)
            if content_hash in seen_hashes:
                continue  # CON-001: hash anywhere in log → skip

            artifact_type = detect_type(artifact)
            dest_dir = project_root / "docs" / DEST_SUBDIR.get(artifact_type, "concepts")

            if dry_run:
                promoted += 1
                seen_hashes.add(content_hash)  # avoid double-count within one dry run
                continue

            dest_dir.mkdir(parents=True, exist_ok=True)
            version = next_version(dest_dir, artifact_type, slugify(branch))
            dest_path = dest_dir / get_promoted_filename(artifact, branch, version)
            shutil.copy2(artifact, dest_path)

            log.setdefault("promotions", []).append({
                "promoted_at": datetime.now().isoformat(),
                "src": str(artifact),
                "dest": str(dest_path.relative_to(project_root)),
                "content_hash": content_hash,
            })
            log.setdefault("content_hashes", {})[content_hash] = str(dest_path.relative_to(project_root))
            seen_hashes.add(content_hash)
            promoted += 1

    if promoted and not dry_run:
        save_promote_log(project_root, log)
    return promoted

if __name__ == "__main__":
    print("--- Stout Artifact Promoter v3.0 ---")
    n = promote_artifacts()
    print(f"\nResumo: {n} artefatos sincronizados.")
```text

- [ ] **Step 4: Run — expect pass**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestPromoteArtifacts -v`
Expected: `6 passed`

- [ ] **Step 5: Run full suite**

Run: `python -m pytest tests/test_stout_promote_v3.py -v`
Expected: all green (≈31 tests)

- [ ] **Step 6: Commit**

```bash
git add tests/test_stout_promote_v3.py src/tools/stout_promote.py
git commit -m "feat: promote_artifacts orchestration with dedup, dry-run, zero-arg main"
```text

---

## Task 7: post_approve.py (F7, F9, F10, F12)

**Files:**

- Create: `src/tools/post_approve.py`
- Modify: `tests/test_stout_promote_v3.py`

- [ ] **Step 1: Write failing test (real temp git repo)**

Append:

```python
class TestPostApprove:
    def test_commits_promoted_docs(self, tmp_path, monkeypatch):
        import importlib
        project_root = tmp_path / "Proj"; project_root.mkdir()
        subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@e.com"], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "T"], cwd=project_root, check=True, capture_output=True)
        (project_root / "README.md").write_text("x", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", "feat/x"], cwd=project_root, check=True, capture_output=True)

        sess = _make_brain_session(tmp_path, project_root,
                                   {"implementation_plan.md": "# Implementation Plan"})

        import post_approve
        importlib.reload(post_approve)
        rc = post_approve.run(project_root=project_root,
                              session_dirs=[(sess, "brain-root")],
                              dry_run=False)
        assert rc == 0
        # docs committed → working tree clean
        status = subprocess.run(["git", "status", "--porcelain"],
                                cwd=project_root, capture_output=True, text=True)
        assert status.stdout.strip() == ""
        assert list((project_root / "docs" / "plans").glob("*.md"))

    def test_dry_run_makes_no_commit(self, tmp_path):
        project_root = tmp_path / "Proj"; project_root.mkdir()
        subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@e.com"], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "T"], cwd=project_root, check=True, capture_output=True)
        sess = _make_brain_session(tmp_path, project_root,
                                   {"implementation_plan.md": "# Implementation Plan"})
        import importlib, post_approve; importlib.reload(post_approve)
        rc = post_approve.run(project_root=project_root,
                              session_dirs=[(sess, "brain-root")], dry_run=True)
        assert rc == 0
        assert not (project_root / "docs" / "plans").exists()
        log = subprocess.run(["git", "log", "--oneline"], cwd=project_root,
                             capture_output=True, text=True)
        assert "Promote" not in log.stdout
```text

- [ ] **Step 2: Run — expect failure**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestPostApprove -v`
Expected: FAIL `No module named 'post_approve'`

- [ ] **Step 3: Implement post_approve.py**

Create `src/tools/post_approve.py`:

```python
"""post_approve.py — promote artifacts after plan approval, then commit.

Usage:
    python src/tools/post_approve.py            # promote + git commit
    python src/tools/post_approve.py --dry-run  # list candidates, no copy, no commit
"""
import sys
import argparse
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stout_promote import promote_artifacts, get_current_branch  # noqa: E402

def run(project_root=None, session_dirs=None, dry_run=False) -> int:
    project_root = Path(project_root) if project_root else Path.cwd()
    branch = get_current_branch(project_root)

    count = promote_artifacts(project_root, branch, session_dirs, dry_run=dry_run)

    if dry_run:
        print(f"[dry-run] {count} artefato(s) seriam promovidos (branch '{branch}'). "
              f"Nada copiado, nada commitado.")
        return 0

    if count == 0:
        print("Nenhum artefato novo para promover.")
        return 0

    subprocess.run(["git", "add", "docs/"], cwd=project_root, check=True)
    msg = f"docs: Promote {count} artifact(s) [{branch}]"
    subprocess.run(["git", "commit", "-m", msg], cwd=project_root, check=True)
    print(f"OK: {count} artefato(s) promovido(s) e commitado(s). Branch: {branch}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Promote artifacts after plan approval")
    parser.add_argument("--dry-run", action="store_true",
                        help="List candidates without copying or committing")
    args = parser.parse_args()
    return run(dry_run=args.dry_run)

if __name__ == "__main__":
    sys.exit(main())
```text

- [ ] **Step 4: Run — expect pass**

Run: `python -m pytest tests/test_stout_promote_v3.py::TestPostApprove -v`
Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add src/tools/post_approve.py tests/test_stout_promote_v3.py
git commit -m "feat: post_approve.py reuses promote_artifacts for run and dry-run"
```text

---

## Task 8: GEMINI.md workflow docs

**Files:**

- Modify: `GEMINI.md`

- [ ] **Step 1: Read the current promotion section**

Run: `python -c "print(open(r'GEMINI.md', encoding='utf-8').read())"` and locate the artifact-promotion lines (~line 48).

- [ ] **Step 2: Replace with v3.0 workflow**

Insert/replace with:

```markdown
### Promoção de Artefatos (Pós-Aprovação) — stout_promote v3.0

Após aprovar um plano:

1. Rode `python src/tools/post_approve.py`. Isso:
   - Descobre artefatos em TODAS as sessões do projeto (Antigravity CLI brain, fallback shared-brain, Claude memory).
   - Deduplica por SHA-256 (idempotente) via `docs/.promote_log.json`.
   - Nomeia de forma determinística: `{tipo}_{YYYY-MM-DD}_{branch-slug}_v{N}.md`.
   - Faz `git add docs/` e commita.
2. Prévia sem efeitos: `python src/tools/post_approve.py --dry-run`.
```text

- [ ] **Step 3: Commit**

```bash
git add GEMINI.md
git commit -m "docs: document stout_promote v3.0 post-approval workflow"
```text

---

## Task 9: Final validation against acceptance criteria

**Files:** none (validation only)

- [ ] **Step 1: Full suite green**

Run: `python -m pytest tests/test_stout_promote_v3.py -v --tb=short`
Expected: all pass.

- [ ] **Step 2: Coverage**

Run: `python -m pytest tests/test_stout_promote_v3.py --cov=stout_promote --cov-report=term-missing`
Expected: ≥80% on `stout_promote.py`.

- [ ] **Step 3: Map results to spec §7 acceptance criteria**

Confirm each criterion has a passing test:

- All sessions, `{tipo}_{data}_{slug}_v{N}` → `TestPromoteArtifacts`, `TestNaming`, `TestDiscoverSessions`
- Second run = 0 (CON-006) → `test_promotes_and_is_idempotent`
- Modify → `_v2` → `test_modified_content_makes_v2`
- Revert → no `_v3` (CON-001) → `test_reverted_content_no_v3`
- `spec.md` → `docs/specs/` (CON-008) → `test_promotes_spec_to_specs`
- `.promote_log.json` with SHA-256 → `TestLogAndHash` + orchestration
- `post_approve` promotes + commits → `test_commits_promoted_docs`
- `--dry-run` no changes (CON-003) → `test_dry_run_makes_no_commit`, `test_dry_run_copies_nothing`

- [ ] **Step 4: Working tree clean**

Run: `git status`
Expected: clean (the suite uses tmp_path; nothing leaks into the repo).

---

## Spec coverage checklist

- [x] §2.1 brain-path discovery (antigravity-cli + shared fallback; ide ignored) — Task 4
- [x] §3.1 deterministic naming — Task 5
- [x] §3.2 type by first 5 lines → filename → concept — Task 2
- [x] §3.3 destination mapping incl. Claude memory → concepts — Tasks 4, 6
- [x] §3.4 multi-session + CON-004 name AND path match — Task 4
- [x] §3.5 `.promote_log.json` with SHA-256 — Tasks 3, 6
- [x] §3.6 `post_approve.py` promote + commit — Task 7
- [x] §3.7 slugify — Task 1
- [x] §7 acceptance criteria mapped — Task 9

---

## Out of scope (later, separate plans)

1. Fix template `~/.shared-ai-memory/templates/scripts/stout_promote.py`.
2. Update `process-stout-init` skill to ship v3.0.
3. Batch-propagate v3.0 to the 7 mapped projects.
