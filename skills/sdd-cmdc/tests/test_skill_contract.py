from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_SKILL = REPO_ROOT / "skills" / "subagent-driven-development"
CMDC_SKILL = REPO_ROOT / "skills" / "sdd-cmdc"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frontmatter_identifies_sdd_cmdc() -> None:
    content = (CMDC_SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert content.startswith("---\n")
    frontmatter = content.split("---\n", 2)[1]
    assert "name: sdd-cmdc" in frontmatter
    assert (
        "description: Use when executing implementation plans with independent tasks"
        in frontmatter
    )


def test_implementation_path_uses_cmdc_and_fixed_model() -> None:
    skill = (CMDC_SKILL / "SKILL.md").read_text(encoding="utf-8")
    adapter = (CMDC_SKILL / "scripts" / "cmdc-implementer.py").read_text(
        encoding="utf-8"
    )

    assert "scripts/cmdc-implementer.py" in skill
    assert "cmdc" in skill
    assert "deepseek/deepseek-v4-flash" in skill
    assert 'MODEL_ID = "deepseek/deepseek-v4-flash"' in adapter
    assert "--yolo" in adapter


def test_reviewer_prompts_are_identical_to_source() -> None:
    for filename in ("task-reviewer-prompt.md", "re-review-prompt.md"):
        assert (CMDC_SKILL / filename).read_bytes() == (
            SOURCE_SKILL / filename
        ).read_bytes()


def test_support_scripts_are_identical_to_source() -> None:
    for filename in ("sdd-workspace", "task-brief", "review-package"):
        assert digest(CMDC_SKILL / "scripts" / filename) == digest(
            SOURCE_SKILL / "scripts" / filename
        )


def test_original_skill_has_no_worktree_diff() -> None:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", "skills/subagent-driven-development"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_skill_does_not_route_implementation_to_codex() -> None:
    content = (CMDC_SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "Codex implementer" not in content
    assert "gpt-5.6-terra" not in content
    assert "fresh cmdc implementer" in content
