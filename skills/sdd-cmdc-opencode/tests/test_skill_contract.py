from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = REPO_ROOT / "skills" / "sdd-cmdc-opencode"
SOURCE = REPO_ROOT / "skills" / "sdd-cmdc"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frontmatter_identifies_sdd_cmdc_opencode() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert content.startswith("---\n")
    frontmatter = content.split("---\n", 2)[1]
    assert "name: sdd-cmdc-opencode" in frontmatter
    description_line = next(
        line for line in frontmatter.splitlines() if line.startswith("description:")
    )
    assert description_line.startswith("description: Use when")


def test_skill_requires_delegated_open_code_review() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "open-code-review-delegate" in content
    assert "ocr delegate preview" in content
    assert "ocr delegate rule" in content


def test_skill_defines_failure_states() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "REVIEW INCOMPLETE" in content
    assert "BLOCKED" in content
    assert "FIX_BASE" in content


def test_skill_forbids_codex_review_fallback() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "não substituir" in content.lower() or "never replace" in content.lower()


def test_implementation_files_exist() -> None:
    implementation_files = [
        "SKILL.md",
        "implementer-prompt.md",
        "scripts/__init__.py",
        "scripts/cmdc-implementer.py",
        "scripts/sdd-workspace",
        "scripts/task-brief",
        "scripts/review-package",
        "tests/test_cmdc_implementer.py",
    ]

    for relative in implementation_files:
        assert (SKILL / relative).is_file(), f"missing implementation file: {relative}"


def test_no_codex_reviewer_prompts_in_new_skill() -> None:
    for filename in ("task-reviewer-prompt.md", "re-review-prompt.md"):
        assert not (SKILL / filename).exists(), (
            f"{filename} must not exist in the new skill directory"
        )


def test_skill_requires_delegate_subskill_for_every_review() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "open-code-review-delegate" in content
    assert "ocr delegate preview" in content
    assert "ocr delegate rule" in content
    assert "task review" in content.lower()
    assert "re-review" in content.lower() or "re-review" in content
    assert "final" in content.lower()


def test_skill_documents_delegated_ocr_flow() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # preview first, then rule, then diff reading, on the exact range.
    assert "ocr delegate preview" in content
    assert "ocr delegate rule" in content
    assert "mode" in content and "merge_base" in content
    assert "merge-base" in content.lower() or "merge_base" in content
    assert "diff" in content.lower()


def test_skill_forbids_executable_llm_config_and_fallback() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # The forbidden LLM tools must only ever appear as documented prohibitions.
    assert "ocr review" in content
    assert "ocr llm test" in content
    assert "OCR_LLM_" in content
    assert "OPENAI_API_KEY" in content
    # The agent must never substitute OCR with an ordinary Codex review.
    assert "não substituir" in content.lower() or "never replace" in content.lower()


def test_skill_governance_states_and_scope_rules() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "BLOCKED" in content
    assert "REVIEW INCOMPLETE" in content
    assert "REVIEW CLEAN" in content
    assert "FIX_BASE" in content
    assert "BASE" in content
    assert "HEAD~1" in content or "never infer" in content.lower()
    assert "never" in content.lower() or "nunca" in content.lower()


def test_skill_requires_tests_in_report_and_fresh_implementer_per_round() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "five" in content.lower() or "5" in content
    assert "fresh" in content.lower()
    assert "report" in content.lower()
    assert "tests" in content.lower() or "test" in content.lower()


def test_skill_does_not_reference_codex_reviewer_prompts() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    for prompt_name in ("task-reviewer-prompt.md", "re-review-prompt.md"):
        assert prompt_name not in content, (
            f"{prompt_name} must not be referenced in SKILL.md"
        )


def test_skill_preserves_sdd_cmdc_workflow_sequence() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "worktree" in content.lower()
    assert "ledger" in content.lower()
    assert "task-brief" in content or "task brief" in content.lower()
    assert "review-package" in content
    assert "cmdc-implementer.py" in content
    assert "implementer-prompt.md" in content


def test_implementation_files_match_sdd_cmdc_digests() -> None:
    pairs = [
        ("scripts/cmdc-implementer.py", "scripts/cmdc-implementer.py"),
        ("implementer-prompt.md", "implementer-prompt.md"),
        ("scripts/sdd-workspace", "scripts/sdd-workspace"),
        ("scripts/task-brief", "scripts/task-brief"),
        ("scripts/review-package", "scripts/review-package"),
    ]

    for new_relative, source_relative in pairs:
        assert digest(SKILL / new_relative) == digest(SOURCE / source_relative), (
            f"digest mismatch for {new_relative}"
        )


def test_source_skills_have_no_worktree_diff() -> None:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--",
            "skills/sdd-cmdc",
            "skills/subagent-driven-development",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == ""
