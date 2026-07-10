#!/usr/bin/env python3
"""Tests for output_contract.py -- mode resolution, path planning, project-root walking."""

from datetime import datetime
from pathlib import Path

from scripts.output_contract import (
    build_output_plan,
    derive_session_name,
    resolve_mode,
    resolve_project_root,
)


def test_clean_prefers_research_directory(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    (project_root / ".git").mkdir(parents=True)
    (project_root / "research").mkdir()
    cwd = project_root / "notes"
    cwd.mkdir()
    input_path = cwd / "phx_review_prd_alertas.mp4"
    input_path.write_bytes(b"audio")

    plan = build_output_plan(
        input_path=input_path,
        cwd=cwd,
        mode=resolve_mode(None),
        out_dir_override=None,
        session_name_override=None,
        keep_source_copy=False,
        clock=lambda: datetime(2026, 7, 9, 10, 30, 45),
    )

    assert resolve_project_root(cwd) == project_root
    assert derive_session_name(input_path, None) == "phx_review_prd_alertas"
    assert plan.mode == "clean"
    assert plan.final_path == project_root / "research" / "phx_review_prd_alertas.md"
    assert plan.artifact_dir is None
    assert plan.source_copy_path is None
    assert plan.warnings == []


def test_archive_collision_and_clean_warning(tmp_path: Path) -> None:
    from scripts.output_contract import (
        build_output_plan,
        copy_source_if_requested,
        render_markdown,
    )

    project_root = tmp_path / "repo"
    (project_root / ".git").mkdir(parents=True)
    cwd = project_root / "work"
    cwd.mkdir()
    input_path = cwd / "meeting.mp4"
    input_path.write_bytes(b"audio")

    first = build_output_plan(
        input_path=input_path,
        cwd=cwd,
        mode="archive",
        out_dir_override=None,
        session_name_override=None,
        keep_source_copy=True,
        clock=lambda: datetime(2026, 7, 9, 12, 0, 0),
    )
    first.artifact_dir.mkdir(parents=True)

    second = build_output_plan(
        input_path=input_path,
        cwd=cwd,
        mode="archive",
        out_dir_override=None,
        session_name_override=None,
        keep_source_copy=True,
        clock=lambda: datetime(2026, 7, 9, 12, 0, 0),
    )
    copied = copy_source_if_requested(second, input_path)
    markdown = render_markdown(
        title="meeting",
        metadata_lines=["- File: meeting.mp4"],
        summary="Resumo",
        action_items=["Enviar follow-up"],
        transcript="Speaker 1: Ola",
    )

    clean_plan = build_output_plan(
        input_path=input_path,
        cwd=cwd,
        mode="clean",
        out_dir_override=None,
        session_name_override=None,
        keep_source_copy=True,
        clock=lambda: datetime(2026, 7, 9, 12, 0, 0),
    )

    assert second.artifact_dir.name == "20260709-120000-01"
    assert copied == second.source_copy_path
    assert copied.read_bytes() == b"audio"
    assert clean_plan.warnings == ["--keep-source-copy has no effect in clean mode"]
    assert markdown.splitlines()[:5] == [
        "# meeting",
        "",
        "## Metadata",
        "- File: meeting.mp4",
        "",
    ]
    assert "## Meeting Summary" in markdown
    assert "## Key Action Items" in markdown
    assert "## Full Transcript" in markdown
