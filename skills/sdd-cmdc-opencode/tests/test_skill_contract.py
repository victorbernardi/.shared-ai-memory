from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = REPO_ROOT / "skills" / "sdd-cmdc-opencode"
REGISTRY = REPO_ROOT / "skills" / "stout-skill-registry" / "registry.json"


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


def test_skill_documents_shared_process_and_real_smoke_gates() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    for token in (
        "process_supervisor.py",
        "cmdc_local.py",
        "Job Object",
        "LAUNCHER_NOT_FOUND",
        "PROCESS_SPAWN_FAILED",
        "PROCESS_CLEANUP_UNVERIFIABLE",
        "CMD_CODE_PROTOCOL_ERROR",
        "SDD_CMDC_REAL_SMOKE",
        "cleanup_verified",
        "drain_verified",
    ):
        assert token in content

    assert "single process" in content and "lifecycle Module" in content
    assert "Deterministic fake-launcher tests are separate" in content


def test_skill_documents_the_canonical_resumable_run_contract() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    for token in (
        "Run Contract schema version 1",
        "contract.json",
        "events.jsonl",
        "checkpoints.jsonl",
        "result.json",
        "start --contract-file",
        "resume --cwd",
        "--run-id",
        "SCOPE_CONTRACT_MISSING",
        "pre-tool Mod",
        "post-shell audit",
        "final audit",
        "NO_IMPLEMENTATION_PROGRESS",
        "same Command Code Session",
        "external plan",
        "normalized test events",
        "scripts/task-brief.py",
        "no generic allow-dirty Recovery bypass",
    ):
        assert token in content, f"missing canonical Run contract token: {token}"


def test_skill_forbids_codex_review_fallback() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    assert "não substituir" in content.lower() or "never replace" in content.lower()


def test_implementation_files_exist() -> None:
    implementation_files = [
        "SKILL.md",
        "implementer-prompt.md",
        "scripts/__init__.py",
        "scripts/cmdc-implementer.py",
        "scripts/verify-install-parity.py",
        "scripts/sdd-workspace",
        "scripts/task-brief",
        "scripts/review-package",
        "tests/test_cmdc_implementer.py",
    ]

    for relative in implementation_files:
        assert (SKILL / relative).is_file(), f"missing implementation file: {relative}"


def test_no_codex_reviewer_prompts_in_new_skill() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # The brief replaces Codex reviews with the delegated flow: no review is
    # routed to a Codex reviewer, and this skill ships no Codex reviewer
    # prompts. Reviews run only through the open-code-review-delegate
    # subskill (ocr delegate preview -> ocr delegate rule -> exact diff).
    assert "open-code-review-delegate" in content
    assert "ocr delegate preview" in content
    assert "ocr delegate rule" in content
    assert (
        "no review is ever routed to a codex reviewer"
        in content.lower().replace("\n", " ")
    )
    assert "Never dispatch a Codex reviewer" in content


def test_skill_does_not_reference_codex_reviewer_prompts() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # SKILL.md must not name or route reviews through Codex reviewer prompt
    # templates; every review uses the delegated open-code-review-delegate
    # flow instead. The versioned host-session instruction template for the
    # initial review (task-reviewer-prompt.md) may be named only as an
    # instruction template rendered into the clean host session — never as a
    # Codex reviewer prompt — and the re-review is the scoped counterpart.
    assert "task-reviewer-prompt.md" in content
    assert "re-review" in content.lower()
    assert "instruction template" in content.lower()


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


def test_skill_has_no_executable_llm_configuration() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # No executable LLM configuration: the forbidden strings may only appear
    # inside documented prohibitions (outside this workflow / must never be
    # executed or set / must not use / must not publish), never as an
    # assignment, invocation, or configuration line. Prohibition text may span
    # lines, so the whole paragraph containing the token is checked.
    paragraphs = content.split("\n\n")
    executable_markers = ("=", "export ", "set ", "run ", "exec ")
    for token in ("ocr review", "ocr llm test", "OCR_LLM_", "OPENAI_API_KEY"):
        matching = [p for p in paragraphs if token in p]
        assert matching, f"expected a documented prohibition for {token!r}"
        for paragraph in matching:
            lower = paragraph.lower()
            assert (
                "must never be executed" in lower
                or "must not use" in lower
                or "outside this workflow" in lower
                or "must not publish" in lower
            ), f"paragraph containing {token!r} is not a documented prohibition"
            assert not any(marker in lower for marker in executable_markers), (
                f"paragraph containing {token!r} looks like executable config"
            )


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


def test_skill_command_example_documents_timeout_alias_and_outer_window() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # The dispatch example must show the explicit bounded timeout spelling
    # alongside the canonical watchdog, and must bind the caller's outer
    # process window to be at least as long as the adapter watchdog.
    assert "--timeout-seconds" in content
    assert "--wall-timeout-seconds" in content
    assert "outer" in content.lower() or "outer process" in content.lower()


def test_implementer_prompt_orders_work_before_host_owned_checks() -> None:
    prompt = (SKILL / "implementer-prompt.md").read_text(encoding="utf-8")

    # The prompt is a sequencing contract: focused tests, commit and report
    # come before broad suite/Ruff/review work that the brief assigns to the
    # host. Verify the sequence through the source document boundaries, not a
    # standalone regex over the file text.
    job_section = prompt.split("## Your Job")[1].split("## Escalation")[0]
    focused_idx = job_section.index("focused")
    commit_idx = job_section.index("commit")
    report_idx = job_section.index("report")
    broad_idx = job_section.index("broad")
    host_idx = job_section.index("host")
    assert focused_idx < commit_idx < report_idx < broad_idx < host_idx, (
        "the prompt must order focused tests -> commit -> report before "
        "broad suite/Ruff/review work assigned to the host"
    )
    assert prompt.index("focused") < prompt.index("broad"), (
        "the sequencing contract must appear in the job section, not only "
        "as a later reiteration"
    )


def test_skill_review_flow_uses_preview_metadata_for_diffs() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # Diffs must be obtained per the mode, merge_base, commit and `to`
    # metadata returned by the preview (brief interface contract).
    assert "ocr delegate preview" in content
    assert "ocr delegate rule" in content
    assert "mode" in content
    assert "merge_base" in content
    assert "commit" in content
    assert "`to`" in content or "to`" in content
    assert "diff" in content.lower()


def test_skill_preserves_command_code_workflow_sequence() -> None:
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
    assert "Task N" in content and "Tarefa N" in content
    assert "PROMPT_UNREADABLE" in content
    assert "PRIMARY_BLOCKER_CODE" in content
    assert "verify-install-parity.py" in content


def test_support_scripts_keep_their_local_contract() -> None:
    workspace = (SKILL / "scripts" / "sdd-workspace").read_text(encoding="utf-8")
    review_package = (SKILL / "scripts" / "review-package").read_text(encoding="utf-8")

    assert "git rev-parse --show-toplevel" in workspace
    assert ".superpowers/sdd" in workspace
    assert "git diff -U10" in review_package
    assert "review-" in review_package

    # The implementer prompt is an evolving contract owned by this skill.
    prompt = (SKILL / "implementer-prompt.md").read_text(encoding="utf-8")
    assert "focused" in prompt.lower()
    assert "commit" in prompt.lower()
    assert "report" in prompt.lower()
    assert "host" in prompt.lower()
    assert "## Your Job" in prompt
    assert "## Escalation" in prompt
    assert "## Report Format" in prompt
    assert "deepseek/deepseek-v4-flash" in prompt


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


def test_subagent_workflow_has_no_worktree_diff() -> None:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--",
            "skills/subagent-driven-development",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_legacy_sdd_cmdc_skill_directory_is_absent() -> None:
    assert not (REPO_ROOT / "skills" / "sdd-cmdc").exists()


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


def test_stout_registry_has_no_legacy_sdd_cmdc_entry() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    sdd_cmdc_entries = [
        entry for entry in registry["skills"] if entry.get("name") == "sdd-cmdc"
    ]

    assert sdd_cmdc_entries == []


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


def test_skill_documents_review_only_command_with_historical_fixture() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    # Task 4: the review-only command is documented with the historical
    # fixture range 0f3d86c..d5eddb8, as an example only.
    assert "0f3d86c" in content
    assert "d5eddb8" in content
    assert "Worked example (historical fixture)" in content
    assert "scripts/review-package PLAN_FILE 0f3d86c d5eddb8" in content
    assert "ocr delegate preview --from 0f3d86c --to d5eddb8" in content
    assert "ocr delegate rule" in content
    assert "review-session.py PLAN_FILE 0f3d86c d5eddb8" in content
    assert "--timeout-seconds 1800" in content


def test_fixture_range_is_not_hardcoded_in_scripts() -> None:
    # The fixture range appears in SKILL.md as documentation only; no script
    # may embed 0f3d86c/d5eddb8 as a default or constant.
    for script in (SKILL / "scripts").glob("*.py"):
        source = script.read_text(encoding="utf-8")
        assert "0f3d86c" not in source
        assert "d5eddb8" not in source
