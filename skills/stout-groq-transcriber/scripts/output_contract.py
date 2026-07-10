#!/usr/bin/env python3
"""
output_contract.py — Artifact-management layer for stout-groq-transcriber.

Responsible for mode resolution, project-root detection, session naming,
output-path planning, archive timestamp collision handling, source-copy policy,
and final Markdown rendering.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Public data type
# ---------------------------------------------------------------------------


@dataclass
class OutputPlan:
    """Describes where and how output artifacts should be written."""

    final_path: Path
    artifact_dir: Path | None
    mode: str
    session_name: str
    source_copy_path: Path | None
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Mode resolution
# ---------------------------------------------------------------------------


def resolve_mode(mode: str | None) -> str:
    """Resolve effective mode, defaulting to ``clean``."""
    return mode if mode in ("debug", "archive") else "clean"


# ---------------------------------------------------------------------------
# Project-root detection
# ---------------------------------------------------------------------------


def resolve_project_root(cwd: Path) -> Path:
    """Walk upward from *cwd* until a directory containing ``.git`` is found.

    If no ``.git`` directory is found, *cwd* is returned as the fallback.
    """
    for candidate in [cwd, *cwd.parents]:
        if (candidate / ".git").is_dir():
            return candidate
    return cwd


# ---------------------------------------------------------------------------
# Session naming
# ---------------------------------------------------------------------------


def derive_session_name(
    input_path: Path, session_name_override: str | None
) -> str:
    """Produce the session name used for session paths and final filename."""
    if session_name_override:
        return session_name_override
    return input_path.stem


# ---------------------------------------------------------------------------
# Base output directory resolution
# ---------------------------------------------------------------------------


def resolve_base_output_dir(
    project_root: Path, mode: str, out_dir_override: Path | None
) -> Path:
    """Resolve the base output directory.

    If *out_dir_override* is given, that is used as-is.
    Otherwise ``research/`` is preferred when it exists (for clean mode),
    and ``transcriptions/`` is used as fallback for all modes.
    """
    if out_dir_override is not None:
        return out_dir_override

    research_dir = project_root / "research"
    if mode == "clean" and research_dir.is_dir():
        return research_dir

    return project_root / "transcriptions"


# ---------------------------------------------------------------------------
# Output-plan builder (core logic)
# ---------------------------------------------------------------------------


def build_output_plan(
    *,
    input_path: Path,
    cwd: Path,
    mode: str,
    out_dir_override: Path | None,
    session_name_override: str | None,
    keep_source_copy: bool,
    clock: callable | None = None,
) -> OutputPlan:
    """Build an ``OutputPlan`` describing every artifact path for the run.

    Parameters
    ----------
    input_path:
        Path to the input media file.
    cwd:
        Current working directory (used for project-root detection).
    mode:
        Effective mode (``clean``, ``debug``, or ``archive``).
    out_dir_override:
        If set, overrides the resolved base output destination.
    session_name_override:
        If set, overrides the session name and final filename stem.
    keep_source_copy:
        Whether the caller requested a source-file copy.
    clock:
        Callable returning ``datetime`` (for deterministic tests).
    """
    if clock is None:
        clock = datetime.now

    project_root = resolve_project_root(cwd)
    session_name = derive_session_name(input_path, session_name_override)
    base_dir = resolve_base_output_dir(project_root, mode, out_dir_override)

    artifact_dir: Path | None = None
    source_copy_path: Path | None = None
    warnings: list[str] = []

    if mode == "clean":
        final_path = base_dir / f"{session_name}.md"
        if keep_source_copy:
            warnings.append("--keep-source-copy has no effect in clean mode")
    elif mode == "debug":
        artifact_dir = base_dir / session_name / "debug"
        final_path = artifact_dir / f"{session_name}.md"
        if keep_source_copy:
            source_copy_path = artifact_dir / input_path.name
    elif mode == "archive":
        ts = clock()
        ts_str = ts.strftime("%Y%m%d-%H%M%S")
        artifact_dir = base_dir / session_name / "archive" / ts_str
        suffix = 0
        while artifact_dir.exists():
            suffix += 1
            artifact_dir = (
                base_dir / session_name / "archive" / f"{ts_str}-{suffix:02d}"
            )
        final_path = artifact_dir / f"{session_name}.md"
        if keep_source_copy:
            source_copy_path = artifact_dir / input_path.name

    return OutputPlan(
        final_path=final_path,
        artifact_dir=artifact_dir,
        mode=mode,
        session_name=session_name,
        source_copy_path=source_copy_path,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Source-copy helper
# ---------------------------------------------------------------------------


def copy_source_if_requested(
    plan: OutputPlan, input_path: Path
) -> Path | None:
    """Copy *input_path* to ``plan.source_copy_path`` if set.

    Returns the destination path, or ``None`` if no copy was requested.
    """
    if plan.source_copy_path is None or plan.mode == "clean":
        return None
    plan.source_copy_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_path, plan.source_copy_path)
    return plan.source_copy_path


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------


def render_markdown(
    *,
    title: str,
    metadata_lines: list[str],
    summary: str,
    action_items: list[str],
    transcript: str,
) -> str:
    """Render the canonical final Markdown document.

    Sections appear in the required order:

    1. Title (``# <title>``)
    2. Metadata (``## Metadata``)
    3. Meeting Summary (``## Meeting Summary``)
    4. Key Action Items (``## Key Action Items``)
    5. Full Transcript (``## Full Transcript``)
    """
    parts: list[str] = []

    parts.append(f"# {title}")
    parts.append("")

    parts.append("## Metadata")
    for line in metadata_lines:
        parts.append(line)
    parts.append("")

    parts.append("## Meeting Summary")
    parts.append(summary)
    parts.append("")

    parts.append("## Key Action Items")
    for item in action_items:
        parts.append(f"- {item}")
    parts.append("")

    parts.append("## Full Transcript")
    parts.append(transcript)
    parts.append("")

    return "\n".join(parts)
