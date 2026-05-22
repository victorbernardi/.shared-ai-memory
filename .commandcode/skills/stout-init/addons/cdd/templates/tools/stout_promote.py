"""Stout Artifact Promoter v3.0

Discovers AI-generated artifacts from Antigravity/Gemini/Claude sessions and
promotes them into the project's docs/ tree with deterministic, deduplicated
naming. See spec: spec_2026-05-20_fix-stout-promote-antigravity-brain-path_v1.md
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

# Imports used by functions added in Tasks 3-7
# (sha256, json log, shutil copy, subprocess git, datetime mtime, os.path)

def slugify(text: str, max_len: int = 60) -> str:
    """Sanitize a git branch name to a filesystem-safe slug."""
    text = text.lower()
    text = text.replace("/", "-").replace("\\", "-")
    text = re.sub(r"[^a-z0-9\-_]", "", text)
    text = re.sub(r"-{2,}", "-", text)
    return text[:max_len].strip("-")


TYPE_MARKERS = {
    "plan": [
        "tipo: plan",
        "type: plan",
        "# plano de implementação",
        "# implementation plan",
    ],
    "spec": ["tipo: spec", "type: spec", "# spec técnica", "# spec"],
    "walkthrough": ["tipo: walkthrough", "type: walkthrough", "# walkthrough"],
}

FILENAME_HINTS = {
    "implementation_plan": "plan",
    "spec": "spec",
    "walkthrough": "walkthrough",
}


def detect_type(filepath: Path) -> str:
    """Classify artifact type: content markers, then filename, then default."""
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


def file_sha256(filepath: Path) -> str:
    """Calculate SHA-256 hash of file content in chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _log_path(project_root: Path) -> Path:
    return project_root / "docs" / ".promote_log.json"


def load_promote_log(project_root: Path) -> dict:
    """Load promotion log, return empty structure if absent."""
    path = _log_path(project_root)
    if path.exists():
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"promotions": [], "content_hashes": {}}


def save_promote_log(project_root: Path, log: dict) -> None:
    """Persist promotion log to docs/.promote_log.json."""
    path = _log_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)


def encode_claude_path(path_str: str) -> str:
    """Encode absolute path to Claude project directory format."""
    return (
        path_str.replace(":\\", "--").replace("\\", "-")
        .replace(":", "--").replace("/", "-")
    )


def get_claude_memory_dir(project_root: Path) -> Path | None:
    """Locate Claude native memory directory for the project."""
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


def is_session_for_current_project(session_dir: Path, project_root: Path) -> bool:
    """True if a session belongs to the current project (CON-004).

    Matches on BOTH project folder name AND absolute path to avoid collisions
    between same-named folders in different locations.
    """
    project_name = project_root.name.lower()
    project_path = str(project_root).lower()

    overview = session_dir / ".system_generated" / "logs" / "overview.txt"
    if overview.exists():
        try:
            text = overview.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            text = ""
        if project_path in text or project_name in text:
            return True

    plans = session_dir / "plans"
    if plans.exists():
        for f in plans.iterdir():
            if project_name in f.name.lower():
                return True
    return False


def discover_sessions(project_root: Path) -> list:
    """Return [(src_dir, origin), ...] for the current project per spec §2.1.

    Scanned:
      ~/.gemini/antigravity-cli/brain/<id>/   (artifacts at session root)
      ~/.shared-ai-memory/brain/<id>/artifacts/  (legacy fallback)
      Claude memory dir                           (concepts)

    NOT scanned: ~/.gemini/antigravity/brain, ~/.gemini/antigravity-ide/brain
    """
    home = Path.home()
    found: list = []

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


def next_version(dest_dir: Path, artifact_type: str, slug: str) -> int:
    """Return next version number: max existing v{N} for this type+slug, plus 1.

    Uses date-agnostic glob: {tipo}_*_{slug}_v*.md (F5 fix).
    """
    pattern = re.compile(
        rf"^{re.escape(artifact_type)}_.+_{re.escape(slug)}_v(\d+)\.md$"
    )
    highest = 0
    if dest_dir.exists():
        for f in dest_dir.iterdir():
            m = pattern.match(f.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def get_promoted_filename(filepath: Path, branch: str, version: int = 1) -> str:
    """Generate deterministic filename: {tipo}_{YYYY-MM-DD}_{branch-slug}_v{N}.md"""
    artifact_type = detect_type(filepath)
    date_str = datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%Y-%m-%d")
    return f"{artifact_type}_{date_str}_{slugify(branch)}_v{version}.md"

IGNORED_NAMES = {"task.md", "implementation_plan.md.resolved"}
DEST_SUBDIR = {
    "plan": "plans",
    "spec": "specs",
    "walkthrough": "walkthroughs",
    "concept": "concepts",
}


def get_current_branch(project_root: Path) -> str:
    """Get current git branch name, fallback to project folder name."""
    try:
        out = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        branch = out.stdout.strip()
        if branch:
            return branch
    except (OSError, subprocess.SubprocessError):
        pass
    return project_root.name


def promote_artifacts(
    project_root: Path | None = None,
    branch: str | None = None,
    session_dirs: list | None = None,
    dry_run: bool = False,
) -> int:
    """Promote artifacts from all project sessions. Returns count promoted.

    Zero-arg callable: auto-discovers project_root (cwd), branch (git),
    and session_dirs (discover_sessions). Args are injection points for tests.
    """
    project_root = Path(project_root) if project_root else Path(os.getcwd())
    branch = branch or get_current_branch(project_root)
    if session_dirs is None:
        session_dirs = discover_sessions(project_root)

    log = load_promote_log(project_root)
    seen_hashes: set = set(log.get("content_hashes", {}).keys())
    promoted = 0

    for src_dir, _origin in session_dirs:
        src_dir = Path(src_dir)
        if not src_dir.exists():
            continue
        for artifact in sorted(src_dir.rglob("*.md")):
            if artifact.name in IGNORED_NAMES:
                continue
            content_hash = file_sha256(artifact)
            if content_hash in seen_hashes:
                continue

            artifact_type = detect_type(artifact)
            subdir = DEST_SUBDIR.get(artifact_type, "concepts")
            dest_dir = project_root / "docs" / subdir

            if dry_run:
                promoted += 1
                seen_hashes.add(content_hash)
                continue

            dest_dir.mkdir(parents=True, exist_ok=True)
            slug = slugify(branch)
            version = next_version(dest_dir, artifact_type, slug)
            dest_path = dest_dir / get_promoted_filename(artifact, branch, version)
            shutil.copy2(artifact, dest_path)

            log.setdefault("promotions", []).append({
                "promoted_at": datetime.now().isoformat(),
                "src": str(artifact),
                "dest": str(dest_path.relative_to(project_root)),
                "content_hash": content_hash,
            })
            log.setdefault("content_hashes", {})[content_hash] = str(
                dest_path.relative_to(project_root)
            )
            seen_hashes.add(content_hash)
            promoted += 1

    if promoted and not dry_run:
        save_promote_log(project_root, log)
    return promoted


if __name__ == "__main__":
    print("--- Stout Artifact Promoter v3.0 ---")
    n = promote_artifacts()
    print(f"\nResumo: {n} artefato(s) sincronizado(s).")
