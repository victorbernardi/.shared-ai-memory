from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).parents[2]
PROJECT_MAIN = Path("skills/orca-project-main")
WORKFLOW_ROUTER = Path("skills/orca-workflow-router")
CONTROL = Path("skills/orca-project-control")
INTEGRATION = Path("docs/orca-project-memory")
DESIGN = Path("docs/superpowers/specs/2026-09-02-orca-project-memory-routing-design.md")

FROZEN_EVENTS = (
    "RUN_CHARTER_ACCEPTED",
    "TASK_READY",
    "IMPLEMENTATION_REPORTED",
    "VERIFICATION_PASSED",
    "VERIFICATION_FAILED",
    "REVIEW_ACCEPTED",
    "REVIEW_CHANGES_REQUESTED",
    "REVIEW_BLOCKED",
    "REMEDIATION_REPORTED",
    "ALL_TASKS_ACCEPTED",
    "FINAL_VERIFICATION_PASSED",
    "FINAL_REVIEW_ACCEPTED",
    "FINAL_REVIEW_CHANGES_REQUESTED",
    "EXECUTOR_UNAVAILABLE",
)

PROJECT_MAIN_FILES = (
    PROJECT_MAIN / "SKILL.md",
    PROJECT_MAIN / "references/context-scope.md",
    PROJECT_MAIN / "references/memory-policy.md",
    PROJECT_MAIN / "references/project-snapshot.md",
    PROJECT_MAIN / "references/run-charter.md",
    PROJECT_MAIN / "templates/PROJECT_BOOTSTRAP.md",
    PROJECT_MAIN / "templates/CONTROL_BOOTSTRAP.md",
    PROJECT_MAIN / "templates/project-registry.example.yaml",
    PROJECT_MAIN / "templates/project-ledger.example.yaml",
)

ROUTER_FILES = (
    WORKFLOW_ROUTER / "SKILL.md",
    WORKFLOW_ROUTER / "references/events-and-transitions.md",
    WORKFLOW_ROUTER / "references/executor-policy.md",
    WORKFLOW_ROUTER / "references/review-routing.md",
    WORKFLOW_ROUTER / "templates/task-brief.md",
    WORKFLOW_ROUTER / "templates/review-brief.md",
    WORKFLOW_ROUTER / "templates/completion-report.md",
)

CONTROL_FILES = (
    CONTROL / "SKILL.md",
    CONTROL / "references/control-protocol.md",
)

ALL_CONTRACT_FILES = PROJECT_MAIN_FILES + ROUTER_FILES + CONTROL_FILES + (
    INTEGRATION / "AGENTS-role-router.md",
    INTEGRATION / "bootstrap-contracts.md",
)


def _read(path: str | Path) -> str:
    resolved = REPO_ROOT / Path(path)
    assert resolved.is_file(), f"missing contract file: {resolved}"
    return resolved.read_text(encoding="utf-8")


def _all_contract_text() -> str:
    return "\n".join(_read(path) for path in ALL_CONTRACT_FILES)


def _active_route_lines(text: str) -> list[str]:
    excluded = ("do not", "never", "not adopted", "legacy", "prohibited", "forbidden")
    return [
        line.lower()
        for line in text.splitlines()
        if "->" in line or "route" in line.lower() or "chamar" in line.lower()
        if not any(marker in line.lower() for marker in excluded)
    ]


def _assert_terms(text: str, *terms: str) -> None:
    for term in terms:
        assert term in text, f"missing contract term: {term}"


def _frontmatter(text: str) -> dict[str, str]:
    assert text.startswith("---\n")
    _, body, _ = text.split("---", 2)
    result: dict[str, str] = {}
    for line in body.strip().splitlines():
        key, separator, value = line.partition(":")
        if separator:
            result[key.strip()] = value.strip()
    return result


def test_skill_metadata_is_discoverable_without_summarizing_workflow():
    expected_names = {
        PROJECT_MAIN / "SKILL.md": "orca-project-main",
        WORKFLOW_ROUTER / "SKILL.md": "orca-workflow-router",
    }
    for path, name in expected_names.items():
        metadata = _frontmatter(_read(path))
        assert metadata["name"] == name
        assert metadata["description"].startswith("Use when ")
        assert len(metadata["description"]) < 500


def test_case_01_missing_bootstrap_routes_to_ordinary():
    text = _read(INTEGRATION / "AGENTS-role-router.md")
    _assert_terms(text, "ORDINARY", "read-only")
    assert "sem bootstrap" in text.lower()


def test_case_02_project_bootstrap_is_project_key_bound():
    text = _read(PROJECT_MAIN / "templates/PROJECT_BOOTSTRAP.md")
    _assert_terms(text, "role: PROJECT_LEAD", "project_key", "Project Key")
    assert "root location" in _read(INTEGRATION / "bootstrap-contracts.md")


def test_case_03_control_bootstrap_is_run_bound():
    text = _read(PROJECT_MAIN / "templates/CONTROL_BOOTSTRAP.md")
    _assert_terms(text, "role: CONTROL", "run_id", "Run Charter", "collision")


def test_case_04_dispatch_precedence_overrides_bootstraps():
    text = _read(INTEGRATION / "bootstrap-contracts.md")
    assert text.index("Dispatch preamble") < text.index("CONTROL_BOOTSTRAP")
    assert text.index("CONTROL_BOOTSTRAP") < text.index("PROJECT_BOOTSTRAP")
    _assert_terms(text, "precedence", "overrides", "history")


def test_case_05_implementer_dispatch_is_explicit():
    text = _read(INTEGRATION / "bootstrap-contracts.md")
    _assert_terms(text, "IMPLEMENTER", "Task Brief", "owned paths")


def test_case_06_reviewer_dispatch_is_explicit():
    text = _read(INTEGRATION / "bootstrap-contracts.md")
    _assert_terms(text, "REVIEWER", "Review Brief", "fresh")


def test_case_07_investigator_dispatch_is_read_only():
    text = _read(INTEGRATION / "bootstrap-contracts.md")
    _assert_terms(text, "INVESTIGATOR", "read-only", "investigation scope")


def test_case_08_project_lead_receives_broad_context():
    text = _read(PROJECT_MAIN / "references/context-scope.md").lower()
    _assert_terms(text, "project_lead", "broad", "all relevant runs", "directed mem0")


def test_case_09_control_receives_minimum_run_context():
    text = _read(PROJECT_MAIN / "references/context-scope.md")
    _assert_terms(text, "CONTROL", "selected Run", "minimal collision index", "read-only")
    assert "full history" in text.lower()


def test_case_10_worker_does_not_receive_superior_context():
    text = _read(PROJECT_MAIN / "references/context-scope.md")
    _assert_terms(text, "IMPLEMENTER", "minimum sufficient context", "no Mem0", "no transcript")
    _assert_terms(_read(WORKFLOW_ROUTER / "templates/task-brief.md"), "only", "Task Brief")


def test_case_11_missing_executor_blocks_only_dispatch():
    text = _read(WORKFLOW_ROUTER / "references/executor-policy.md")
    _assert_terms(text, "missing", "invalid", "TASK_READY", "block only the dispatch", "Victor")


def test_case_12_agy_routes_to_delegate_to_agy():
    text = _read(WORKFLOW_ROUTER / "references/executor-policy.md")
    _assert_terms(text, "agy", "$delegate-to-agy")


def test_case_13_command_code_routes_to_commandcode_delegate():
    text = _read(WORKFLOW_ROUTER / "references/executor-policy.md")
    _assert_terms(text, "command-code", "$commandcode-delegate")


def test_case_14_agy_failure_has_no_command_code_fallback():
    text = _read(WORKFLOW_ROUTER / "references/executor-policy.md")
    _assert_terms(text, "AgY", "failure", "never", "Command Code", "EXECUTOR_UNAVAILABLE")


def test_case_15_command_code_failure_has_no_agy_fallback():
    text = _read(WORKFLOW_ROUTER / "references/executor-policy.md")
    _assert_terms(text, "Command Code", "failure", "never", "AgY", "EXECUTOR_UNAVAILABLE")


def test_case_16_implementation_report_requires_verification():
    text = _read(WORKFLOW_ROUTER / "references/events-and-transitions.md")
    _assert_terms(text, "IMPLEMENTATION_REPORTED", "$verification-before-completion", "fresh evidence")


def test_case_17_green_verification_creates_fresh_reviewer():
    text = _read(WORKFLOW_ROUTER / "references/review-routing.md")
    _assert_terms(text, "VERIFICATION_PASSED", "fresh", "REVIEWER", "Task/Dispatch")


def test_case_18_reviewer_loads_existing_review_skill():
    text = _read(WORKFLOW_ROUTER / "references/review-routing.md")
    _assert_terms(text, "$open-code-review-delegate", "load", "copy")


def test_case_19_findings_route_to_receiving_review_and_remediation():
    text = _read(WORKFLOW_ROUTER / "references/review-routing.md")
    _assert_terms(text, "REVIEW_CHANGES_REQUESTED", "$receiving-code-review", "remediation")


def test_case_20_remediation_requires_reverification_and_scoped_rereview():
    text = _read(WORKFLOW_ROUTER / "references/review-routing.md")
    _assert_terms(text, "REMEDIATION_REPORTED", "reverify", "scoped re-review")


def test_case_21_all_tasks_require_final_verification_and_whole_branch_review():
    text = _read(WORKFLOW_ROUTER / "references/review-routing.md")
    _assert_terms(text, "ALL_TASKS_ACCEPTED", "final verification", "whole-branch review")


def test_case_22_finishing_without_valid_final_review_is_blocked():
    text = _read(WORKFLOW_ROUTER / "references/review-routing.md")
    _assert_terms(text, "$finishing-a-development-branch", "blocked", "valid final review")


def test_case_23_old_head_makes_final_review_stale():
    text = _read(WORKFLOW_ROUTER / "references/review-routing.md")
    _assert_terms(text, "base_sha", "head_sha", "stale", "HEAD")


def test_case_24_current_head_allows_finishing_gate():
    text = _read(WORKFLOW_ROUTER / "references/review-routing.md")
    _assert_terms(text, "current HEAD", "finishing", "FINAL_REVIEW_ACCEPTED")


def test_case_25_pending_local_review_blocks_only_dependents():
    text = _read(WORKFLOW_ROUTER / "references/events-and-transitions.md")
    _assert_terms(text, "pending", "dependent", "independent", "continue")


def test_case_26_mem0_unavailable_degrades_without_invented_memory():
    text = _read(PROJECT_MAIN / "references/memory-policy.md").lower()
    _assert_terms(text, "unavailable", "degraded", "orca", "git", "do not invent")


def test_case_27_age_alone_does_not_mark_legacy():
    text = _read(PROJECT_MAIN / "references/project-snapshot.md")
    _assert_terms(text, "legacy", "explicit", "age", "evidence")


def test_case_28_legacy_sdd_route_is_excluded():
    text = _all_contract_text()
    assert "$sdd-cmdc-opencode" in text
    assert not any("sdd-cmdc-opencode" in line for line in _active_route_lines(text))


def test_case_29_pi_is_not_adopted_in_active_routes():
    text = _all_contract_text()
    assert "Pi" in text
    assert not any(re.search(r"\bpi\b", line) for line in _active_route_lines(text))


def test_case_30_native_orca_skills_are_protected():
    text = _all_contract_text()
    for skill in ("$orca-cli", "$orchestration"):
        assert skill in text
    _assert_terms(text.lower(), "protected", "not copied", "unchanged")


def test_case_31_writer_concurrency_is_bounded_at_two():
    text = _read(WORKFLOW_ROUTER / "references/events-and-transitions.md")
    _assert_terms(text, "MAX_PARALLEL_WRITERS", "2", "worktree", "path conflict")


def test_case_32_global_router_patch_is_idempotent():
    text = _read(INTEGRATION / "AGENTS-role-router.md")
    begin = "<!-- ORCA-PROJECT-ROUTER:BEGIN -->"
    end = "<!-- ORCA-PROJECT-ROUTER:END -->"
    block = text[text.index(begin) : text.index(end) + len(end)]
    original = "# existing instructions\n"

    def apply_once(document: str) -> str:
        if begin in document and end in document:
            return document
        return document + block + "\n"

    assert apply_once(apply_once(original)) == apply_once(original)


def test_case_33_removing_global_router_block_restores_previous_content():
    text = _read(INTEGRATION / "AGENTS-role-router.md")
    begin = "<!-- ORCA-PROJECT-ROUTER:BEGIN -->"
    end = "<!-- ORCA-PROJECT-ROUTER:END -->"
    block = text[text.index(begin) : text.index(end) + len(end)]
    original = "# existing instructions\n"
    patched = original + block + "\n"
    restored = patched.replace(block + "\n", "")
    assert restored == original


def test_case_34_windows_crlf_and_powershell_forms_are_documented():
    text = _all_contract_text()
    _assert_terms(text, "Windows", "PowerShell", "CRLF", "%USERPROFILE%")
    assert "\\" in text


def test_case_35_contracts_contain_no_real_credentials_or_private_data():
    text = _all_contract_text()
    forbidden = (
        r"sk-[A-Za-z0-9]{20,}",
        r"Bearer\s+[A-Za-z0-9._-]{20,}",
        r"client_secret\s*[:=]",
        r"password\s*[:=]\s*\S+",
        r"https://[^\s]+oauth[^\s]*",
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    )
    for pattern in forbidden:
        assert not re.search(pattern, text, flags=re.IGNORECASE), pattern
    _assert_terms(text.lower(), "credential", "authenticated url", "pii")


def test_case_36_control_source_is_canonical_and_documented():
    decision = _read(INTEGRATION / "control-canonical-source-decision.md")
    _assert_terms(decision, "skills/orca-project-control/", "repository", "canonical")
    _assert_terms(decision.lower(), "later", "promotion", "not", "approval")
    assert (REPO_ROOT / "skills/orca-project-control/SKILL.md").is_file()
    assert (REPO_ROOT / "skills/orca-project-control/references/control-protocol.md").is_file()


def test_case_37_run_charter_schema_matches_frozen_top_level_contract():
    text = _read(PROJECT_MAIN / "references/run-charter.md")
    example = text[text.index("```yaml") : text.index("```", text.index("```yaml") + 7)]
    expected_top_level = [
        "schema_version",
        "run_id",
        "project_key",
        "work_slug",
        "objective",
        "why_now",
        "repository",
        "branch",
        "base_sha",
        "head_sha",
        "worktree",
        "dirty_baseline",
        "executor_policy",
        "relevant_memory",
        "relevant_decisions",
        "in_scope",
        "out_of_scope",
        "protected_paths",
        "acceptance",
        "verification",
        "rollback",
    ]
    top_level = [
        match.group(1)
        for line in example.splitlines()
        if (match := re.match(r"^  ([a-z_]+):", line))
    ]
    assert top_level == expected_top_level
    nested_executor = [
        match.group(1)
        for line in example.splitlines()
        if (match := re.match(r"^    ([a-z_]+):", line))
    ]
    assert nested_executor == [
        "selected_by",
        "value",
        "automatic_fallback",
        "task_override",
    ]
    _assert_terms(
        example,
        "run_id:",
        "repository:",
        "branch:",
        "base_sha:",
        "head_sha:",
        "worktree:",
        "dirty_baseline:",
        "executor_policy:",
        "selected_by: victor",
        "value: agy | command-code",
        "automatic_fallback: false",
        "task_override: user_only",
    )
    assert not re.search(
        r"^\s+(?:baseline|scope|constraints|sources|implementation|review):",
        example,
        flags=re.MULTILINE,
    )
    assert "selected_by: user" not in example
    assert "executor: agy | command-code" not in example


def test_case_38_task_brief_schema_has_dispatch_identity_and_scope_fields():
    text = _read(WORKFLOW_ROUTER / "templates/task-brief.md")
    _assert_terms(
        text,
        "role: IMPLEMENTER",
        "project_key:",
        "run_id:",
        "task_id:",
        "dispatch_id:",
        "run_charter_ref:",
        "executor_policy:",
        "selected_by: victor",
        "value: agy | command-code",
        "automatic_fallback: false",
        "task_override: user_only",
        "required_sources:",
        "owned_paths:",
        "protected_paths:",
        "pre_existing_dirty_paths:",
        "project_closure_gates:",
        "expected_completion_report:",
    )


def test_case_39_review_brief_schema_has_exact_review_identity_and_range():
    text = _read(WORKFLOW_ROUTER / "templates/review-brief.md")
    _assert_terms(
        text,
        "role: REVIEWER",
        "review_skill: open-code-review-delegate",
        "project_id:",
        "run_id:",
        "implementation_id:",
        "review_id:",
        "repository:",
        "worktree:",
        "branch:",
        "base_sha:",
        "head_sha:",
        "business_context:",
        "contract_refs:",
        "verification_evidence:",
        "disposition: ACCEPT | CHANGES_REQUESTED | BLOCKED",
    )


def test_case_40_dispatch_role_requires_current_identity_proof():
    text = _read(INTEGRATION / "bootstrap-contracts.md")
    _assert_terms(
        text,
        "current valid Dispatch preamble",
        "role:",
        "project_key:",
        "run_id:",
        "task_id:",
        "dispatch_id:",
        "worktree:",
        "branch:",
        "current/live",
        "invalid",
        "read-only",
    )
    lowered = text.lower()
    assert "title establishes" not in lowered
    assert "root location establishes" not in lowered


def test_case_41_cmdc_is_normalized_without_executor_fallback():
    text = "\n".join(
        (
            _read(PROJECT_MAIN / "references/run-charter.md"),
            _read(WORKFLOW_ROUTER / "references/executor-policy.md"),
            _read(CONTROL / "references/control-protocol.md"),
        )
    )
    _assert_terms(text, "cmdc", "conversational alias", "Normalize", "command-code", "automatic_fallback: false")
    assert not any("cmdc" in line and "->" in line for line in text.splitlines())


def test_case_42_remediation_is_one_pass_then_replan_or_split():
    text = "\n".join(
        (
            _read(WORKFLOW_ROUTER / "references/review-routing.md"),
            _read(CONTROL / "references/control-protocol.md"),
        )
    )
    _assert_terms(
        text,
        "MAX_REMEDIATION_PASSES = 1",
        "one remediation pass",
        "REPLAN_OR_SPLIT",
        "second rejection",
        "scope change",
        "architectural contradiction",
    )
    assert "MAX_REMEDIATION_PASSES = 2" not in text


def test_case_43_security_regexes_detect_synthetic_secrets_and_use_single_escapes():
    patterns = (
        r"Bearer\s+[A-Za-z0-9._-]{20,}",
        r"password\s*[:=]\s*\S+",
        r"https://[^\s]+oauth[^\s]*",
    )
    samples = (
        "Bearer " + ("x" * 24),
        "password=" + ("x" * 8),
        "https://example.invalid/oauth/token",
    )
    for pattern, sample in zip(patterns, samples):
        assert r"\\s" not in pattern
        assert re.search(pattern, sample, flags=re.IGNORECASE), pattern


def test_case_44_registry_and_ledger_examples_are_staged_only_in_tmp_dir(tmp_path: Path):
    for source in (
        PROJECT_MAIN / "templates/project-registry.example.yaml",
        PROJECT_MAIN / "templates/project-ledger.example.yaml",
    ):
        staged = tmp_path / source.name
        staged.write_text(_read(source), encoding="utf-8")
        assert staged.parent == tmp_path
        assert staged.read_text(encoding="utf-8")
    assert not (REPO_ROOT / "registry.yaml").exists()
    assert not (REPO_ROOT / "projects").exists()


def test_case_45_role_router_has_exact_markers_and_no_active_alias_route():
    text = _read(INTEGRATION / "AGENTS-role-router.md")
    assert text.count("<!-- ORCA-PROJECT-ROUTER:BEGIN -->") == 1
    assert text.count("<!-- ORCA-PROJECT-ROUTER:END -->") == 1
    active = _active_route_lines(text)
    assert not any("cmdc" in line or "sdd-cmdc-opencode" in line for line in active)


def test_case_46_missing_executor_table_row_blocks_only_dispatch_and_preserves_state():
    text = _read(WORKFLOW_ROUTER / "references/events-and-transitions.md")
    missing_executor_row = (
        "| `TASK_READY` + missing/invalid executor | Block only the dispatch; "
        "request Victor's choice; never choose or substitute. |"
    )
    unavailable_row = (
        "| `EXECUTOR_UNAVAILABLE` | Preserve the current Run state and ask Victor "
        "for a new executor decision; no automatic fallback. |"
    )
    assert missing_executor_row in text
    assert unavailable_row in text
    assert text.index(missing_executor_row) < text.index(unavailable_row)
    assert "choose a provider from availability" not in missing_executor_row


def test_case_47_completion_report_requires_bounded_outcome():
    text = _read(WORKFLOW_ROUTER / "templates/completion-report.md")
    _assert_terms(
        text,
        "outcome: succeeded | failed",
        "`outcome` is required",
        "only `succeeded` or `failed`",
        "failed outcome",
        "not acceptance",
    )
    assert re.search(r"^outcome:\s+succeeded \| failed$", text, flags=re.MULTILINE)
    assert "outcome: true" not in text
    assert "outcome: complete" not in text


def test_case_48_event_table_matches_frozen_events_exactly():
    text = _read(WORKFLOW_ROUTER / "references/events-and-transitions.md")
    table = text[text.index("| Event / condition |") : text.index("## Evidence boundary")]
    covered = set(re.findall(r"^\| `([A-Z_]+)`", table, flags=re.MULTILINE))
    assert covered == set(FROZEN_EVENTS)
    assert len(FROZEN_EVENTS) == len(set(FROZEN_EVENTS)) == 14
    assert "The following 14 events are frozen." in text


def test_case_49_design_run_charter_ordering_and_work_slug():
    text = _read(DESIGN)
    match = re.search(
        r"run_charter:\n.*?project_key:\s*\"\"\n\s*work_slug:\s*\"\"\n\s*objective:\s*\"\"",
        text,
        re.DOTALL,
    )
    assert match is not None, "design Run Charter must have project_key then work_slug then objective"


def test_case_50_design_review_brief_uses_singular_disposition():
    text = _read(DESIGN)
    assert "disposition: ACCEPT | CHANGES_REQUESTED | BLOCKED" in text
    assert "dispositions:" not in text


def test_case_51_design_transition_table_covers_all_frozen_events():
    design_text = _read(DESIGN)
    table = design_text[
        design_text.index("### Transitions (frozen, exact)") : design_text.index("### Concurrency and staleness rules")
    ]
    design_covered = set(re.findall(r"\| `([A-Z_]+)`", table))
    assert design_covered == set(FROZEN_EVENTS)
    canonical_text = _read(WORKFLOW_ROUTER / "references/events-and-transitions.md")
    canonical_table = canonical_text[
        canonical_text.index("| Event / condition |") : canonical_text.index("## Evidence boundary")
    ]
    canonical_covered = set(re.findall(r"^\| `([A-Z_]+)`", canonical_table, flags=re.MULTILINE))
    assert design_covered == canonical_covered

