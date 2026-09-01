from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

CODEX_REVIEW_ROUTES = (
    "skills/requesting-code-review/SKILL.md",
    "skills/requesting-code-review/code-reviewer.md",
    "skills/matt-code-review/SKILL.md",
    "skills/subagent-driven-development/SKILL.md",
    "skills/subagent-driven-development/task-reviewer-prompt.md",
    "skills/subagent-driven-development/re-review-prompt.md",
    "skills/brainstorming/spec-document-reviewer-prompt.md",
    "skills/writing-plans/plan-document-reviewer-prompt.md",
    "skills/impeccable/agents/impeccable_finish_reviewer.toml",
    "skills/impeccable/reference/new-work.md",
)


def _content(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_codex_review_routes_use_luna_max_priority_defaults() -> None:
    for relative_path in CODEX_REVIEW_ROUTES:
        content = _content(relative_path)
        lowered = content.lower()

        assert 'model="gpt-5.6-luna"' in lowered, relative_path
        assert 'reasoning_effort="max"' in lowered, relative_path
        assert 'service_tier="priority"' in lowered, relative_path
        assert "gpt-5.6-sol" not in lowered, relative_path


def test_review_routes_keep_explicit_per_review_overrides() -> None:
    for relative_path in CODEX_REVIEW_ROUTES:
        lowered = _content(relative_path).lower()

        assert "explicit" in lowered, relative_path
        assert "override" in lowered, relative_path


def test_subagent_implementer_route_remains_terra_medium() -> None:
    content = _content("skills/subagent-driven-development/SKILL.md").lower()

    assert "gpt-5.6-terra" in content
    assert 'reasoning_effort="medium"' in content
