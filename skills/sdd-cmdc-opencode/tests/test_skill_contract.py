from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = REPO_ROOT / "skills" / "sdd-cmdc-opencode"
SOURCE = REPO_ROOT / "skills" / "sdd-cmdc"
REGISTRY = REPO_ROOT / "skills" / "stout-skill-registry" / "registry.json"


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


def test_review_templates_exist_and_are_distinct() -> None:
    task_reviewer = SKILL / "task-reviewer-prompt.md"
    re_review = SKILL / "re-review-prompt.md"

    assert task_reviewer.is_file(), "missing task-reviewer-prompt.md"
    assert re_review.is_file(), "missing re-review-prompt.md"
    assert digest(task_reviewer) != digest(re_review), (
        "task-reviewer-prompt.md and re-review-prompt.md must be distinct templates"
    )


def test_review_templates_are_separated_by_intent() -> None:
    task_reviewer = (SKILL / "task-reviewer-prompt.md").read_text(encoding="utf-8")
    re_review = (SKILL / "re-review-prompt.md").read_text(encoding="utf-8")

    # The initial review covers BASE..HEAD; the re-review covers only
    # FIX_BASE..HEAD, receives the previous findings, and verdicts each item
    # ADDRESSED or NOT ADDRESSED.
    assert "BASE..HEAD" in task_reviewer
    assert "FIX_BASE" not in task_reviewer
    assert "FIX_BASE..HEAD" in re_review
    assert "[FINDINGS]" in re_review
    assert "ADDRESSED" in re_review and "NOT ADDRESSED" in re_review
    # Both are instruction templates for the clean host session launcher, not
    # a new review backend and not Codex reviewer prompts.
    assert "review-session.py" in task_reviewer and "review-session.py" in re_review
    assert "not a Codex reviewer prompt" in task_reviewer
    assert "not a Codex reviewer prompt" in re_review


def test_skill_documents_windows_shell_for_exact_range_ocr() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # The delegated preview/rule flow must instruct a working shell for
    # exact-range OCR on Windows (PowerShell fails ref resolution with
    # "Needed a single revision"; Git Bash resolves the same ref).
    assert "Needed a single revision" in content
    assert "Git Bash" in content
    assert "PowerShell" in content
    # The exact BASE/FIX_BASE/MERGE_BASE range must be preserved, never
    # silently shifted, and the shell + command + exit code recorded.
    assert "BASE" in content and "FIX_BASE" in content and "MERGE_BASE" in content
    assert "never shift" in content.lower()
    assert "shell name" in content.lower()
    assert "exit code" in content.lower()
    # No silent Codex/API fallback when the shell or OCR fails.
    assert "fall back" in content.lower() and "never" in content.lower()


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


def test_skill_references_both_review_templates_by_name() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # SKILL.md must reference the versioned review templates by their exact
    # filenames; the initial review renders task-reviewer-prompt.md and the
    # re-review renders re-review-prompt.md.
    assert "task-reviewer-prompt.md" in content
    assert "re-review-prompt.md" in content


def test_skill_preserves_sdd_cmdc_workflow_sequence() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "worktree" in content.lower()
    assert "ledger" in content.lower()
    assert "task-brief" in content or "task brief" in content.lower()
    assert "review-package" in content
    assert "cmdc-implementer.py" in content
    assert "implementer-prompt.md" in content
    assert "--checkpoint-file" in content
    assert "--heartbeat-interval" in content
    assert "--wall-timeout-seconds" in content
    assert "--stall-timeout-seconds" in content
    assert "--recovery-max-turns" in content
    assert "STATUS: RECOVERED" in content
    assert "PERMISSION_DENIED" in content
    assert "IMPLEMENTATION INCOMPLETE" in content
    assert "TIMED_OUT" in content


def test_copied_implementation_files_match_sdd_cmdc_digests() -> None:
    # Files intentionally copied from the source skill must remain byte-identical.
    pairs = [
        ("implementer-prompt.md", "implementer-prompt.md"),
        ("scripts/sdd-workspace", "scripts/sdd-workspace"),
        ("scripts/task-brief", "scripts/task-brief"),
        ("scripts/review-package", "scripts/review-package"),
    ]

    for new_relative, source_relative in pairs:
        assert digest(SKILL / new_relative) == digest(SOURCE / source_relative), (
            f"digest mismatch for {new_relative}"
        )


def test_evolving_adapter_keeps_contract_and_never_infers_completion() -> None:
    # The target adapter evolves beyond the source adapter (recovery evidence);
    # it must not be required to byte-match the sibling, but it must keep the
    # fail-closed implementation contract and never claim completion from a
    # commit or report alone.
    adapter = (SKILL / "scripts" / "cmdc-implementer.py").read_text(encoding="utf-8")

    assert "deepseek/deepseek-v4-flash" in adapter
    assert "IMPLEMENTATION INCOMPLETE" in adapter
    assert "collect_workspace_snapshot" in adapter
    assert "_write_checkpoint" in adapter
    # The only failure state the adapter may claim is IMPLEMENTATION INCOMPLETE.
    # Completion requires validation evidence beyond the workspace snapshot, so
    # the adapter must never assign a COMPLETE state itself; it may only guard
    # against it.
    assert "state == \"COMPLETE\"" in adapter
    assert "state = \"COMPLETE\"" not in adapter
    assert "raise ValueError" in adapter


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


def test_skill_has_approved_audit_artifact() -> None:
    audit_path = SKILL / "audit_result.json"

    assert audit_path.is_file(), "missing audit_result.json in the new skill directory"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))

    assert audit["verdict"] == "APPROVED"
    assert audit["proposed_name"] == "sdd-cmdc-opencode"
    assert audit["proposed_tier"] == 4
    assert "open-code-review" in audit["proposed_role"].lower() or "delegation" in audit[
        "proposed_role"
    ].lower()


def test_skill_is_registered_active_in_stout_registry() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    matches = [
        entry for entry in registry["skills"] if entry.get("name") == "sdd-cmdc-opencode"
    ]

    assert len(matches) == 1, f"expected exactly one registry entry, got {len(matches)}"
    entry = matches[0]

    assert entry["path"] == "skills/sdd-cmdc-opencode"
    assert entry["tier"] == 4
    assert entry["category"] == "meta-factory"
    assert entry["status"] == "active"
    assert entry["triggers"] == [
        "sdd-cmdc-opencode",
        "open-code-review",
        "revisão delegada",
        "revisão por tarefa",
        "executar plano",
    ]
    assert "OPENAI_API_KEY" in entry["notes"]


def test_stout_registry_preserves_sdd_cmdc_entry() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    sdd_cmdc_entries = [
        entry for entry in registry["skills"] if entry.get("name") == "sdd-cmdc"
    ]

    assert len(sdd_cmdc_entries) == 1, (
        f"expected exactly one sdd-cmdc entry, got {len(sdd_cmdc_entries)}"
    )
    assert sdd_cmdc_entries[0]["status"] == "active"
    assert sdd_cmdc_entries[0]["tier"] == 4


def test_skill_defines_review_only_section() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "## Review-only" in content


def test_skill_review_only_requires_full_inputs_and_sequence() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # Review-only required inputs: plan, BASE (or MERGE_BASE), HEAD, review
    # package, preview output, rule groups, diffs, report path.
    assert "plan file" in content.lower()
    assert "BASE" in content and "MERGE_BASE" in content and "HEAD" in content
    assert "review package" in content.lower()
    assert "preview" in content.lower()
    assert "rule groups" in content.lower() or "resolved rule groups" in content.lower()
    assert "diff" in content.lower()
    assert "report file path" in content.lower()
    # The review-only sequence: package, preview, scope validation, rules,
    # diffs, clean host session, verdict.
    assert "validate the scope" in content.lower()
    assert "fresh, clean host session" in content.lower()
    assert "record the verdict" in content.lower()


def test_skill_review_only_never_runs_implementer_or_fix_round() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # Review-only must not invoke CMDc, fix findings, or start a re-review
    # without explicit authorization.
    assert "never invokes the implementer" in content
    assert "never fixes findings" in content
    assert "without explicit authorization" in content
    assert "cmdc-implementer.py" in content
    assert "start a fix round" in content.lower()


def test_skill_review_only_is_independent_and_not_ocr_fallback() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # New ephemeral process, no history from the implementing session,
    # read-only access to the same worktree and range. This is not a fallback
    # for OCR; OCR remains a prerequisite.
    assert "ephemeral" in content
    assert "no history" in content.lower()
    assert "read-only" in content.lower()
    assert "same worktree" in content.lower()
    assert "same range" in content.lower()
    assert "not a fallback for OCR" in content
    assert "prerequisite" in content.lower()


def test_skill_review_only_report_contract() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # Report contract: Files reviewed, Excluded files, Commands, Exit codes,
    # Critical/High, Medium, Review status, BASE/HEAD evidence, and
    # recommendations with path/start_line/end_line.
    assert "Files reviewed" in content
    assert "Excluded files" in content
    assert "Commands" in content and "Exit codes" in content
    assert "Critical/High" in content
    assert "Medium" in content
    assert "Review status" in content
    assert "start_line" in content and "end_line" in content


def test_skill_review_only_forbids_fallback_and_github() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # Review-only must not use an API/LLM fallback and must not publish
    # GitHub comments.
    assert "fallback" in content.lower()
    assert "OPENAI_API_KEY" in content
    assert "never publish" in content.lower() or "must not publish" in content.lower()


def test_skill_review_only_clean_host_launcher_reference() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # The clean host session launcher and its fail-closed flags/states.
    assert "review-session.py" in content
    assert "--ephemeral" in content
    assert "--sandbox read-only" in content
    assert "REVIEW INCOMPLETE" in content
    assert "BLOCKED" in content
    assert "REVIEW CLEAN" in content
