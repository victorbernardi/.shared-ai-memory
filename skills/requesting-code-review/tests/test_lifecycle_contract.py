from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def test_review_skill_documents_terminal_and_intermediate_states() -> None:
    content = SKILL.read_text(encoding="utf-8")

    for state in (
        "SPAWN_FAILED",
        "QUEUED",
        "RUNNING",
        "POLL_TIMEOUT",
        "READY",
        "FAILED",
        "INTERRUPTED",
        "REVIEW INCOMPLETE",
    ):
        assert state in content


def test_review_skill_preserves_same_agent_after_poll_timeout() -> None:
    content = SKILL.read_text(encoding="utf-8").lower()

    assert "wait_agent" in content
    assert "same `agent_id`" in content or "same id" in content
    assert (
        "do not dispatch a duplicate" in content
        or "do not dispatch a second reviewer" in content
    )
    assert "do not interrupt" in content
    assert "late" in content or "tard" in content


def test_review_skill_records_dispatch_and_terminal_metadata() -> None:
    content = SKILL.read_text(encoding="utf-8").lower()

    for field in (
        "agent_id",
        "requested_model",
        "resolved_model",
        "reasoning_effort",
        "service_tier",
        "started_at",
        "finished_at",
        "report",
        "error",
    ):
        assert field in content


def test_review_skill_uses_luna_max_priority_as_the_default_route() -> None:
    content = SKILL.read_text(encoding="utf-8")

    assert 'model="gpt-5.6-luna"' in content
    assert 'reasoning_effort="max"' in content
    assert 'service_tier="priority"' in content
    assert "without asking a blocking question" in content.lower()
    assert "gpt-5.6-sol" not in content
    assert "terra" not in content.lower()


def test_review_skill_fails_closed_without_a_terminal_report() -> None:
    content = SKILL.read_text(encoding="utf-8").lower()

    assert "report missing" in content or "missing report" in content
    assert "never approval" in content or "never approve" in content
    assert "explicit error" in content or "terminal error" in content
