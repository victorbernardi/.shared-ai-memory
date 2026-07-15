# Validation Evidence: Hybrid Skill Platforms

**Date:** 2026-07-15
**Branch:** chore/multiformat-skill-platforms
**Base commit:** 3befe24

---

## Test Results

| ID | Test | Command | Exit Code | Result |
|----|------|---------|-----------|--------|
| T-001 | Blueprint engine requires --output-dir | `python -m unittest test_blueprint_engine.TestBlueprintEngine.test_engine_requires_output_dir` | 0 | PASS |
| T-002 | Blueprint writes 3 targets and manifest | `python -m unittest test_blueprint_engine.TestBlueprintEngine.test_engine_writes_three_targets_and_default_manifest` | 0 | PASS |
| T-003 | Renderer copies files to each platform | `python -m unittest test_platform_renderer.TestPlatformRenderer.test_renderer_copies_common_files_to_each_target` | 0 | PASS |
| T-004 | Renderer skips manifest and install file | `python -m unittest test_platform_renderer.TestPlatformRenderer.test_skips_manifest_and_install_file` | 0 | PASS |
| T-005 | Claude extension skipped on other platforms | `python -m unittest test_platform_renderer.TestPlatformRenderer.test_optional_claude_extension_is_skipped_elsewhere` | 0 | PASS |
| T-006 | Validator blocks unsupported extensions | `python -m unittest test_hybrid_validator.TestHybridValidator.test_required_unsupported_extension_blocks` | 0 | PASS |
| T-007 | Validator ignores fixtures and archives | `python -m unittest test_hybrid_validator.TestHybridValidator.test_active_legacy_scan_ignores_fixture_and_archive` | 0 | PASS |
| T-008 | Global installer creates all targets | `python -m unittest test_global_installer.TestGlobalInstaller.test_install_creates_all_targets` | 0 | PASS |
| T-009 | Collision requires replace flag | `python -m unittest test_global_installer.TestGlobalInstaller.test_collision_requires_replace` | 0 | PASS |

---

## E2E Verification

### Blueprint Generation

```
Command: python stout-create-skill/scripts/blueprint_engine.py --tier 2 --name demo-skill --description "Use quando precisar testar a skill demo." --output-dir $env:TEMP/stout-multiformat-demo
Exit code: 0
Output: [OK] Blueprint gerado em C:\Users\VICTOR~1.BER\AppData\Local\Temp\stout-multiformat-demo
```

### Rendering with Compatible Extension

```
Command: python stout-create-skill/scripts/platform_renderer.py --source-path $env:TEMP/stout-multiformat-source --output-dir $env:TEMP/stout-multiformat-demo
Exit code: 0
Compatibility: claude-code=included, codex=skipped, commandcode=skipped (for claude.allowed-tools)
```

### Validation of Unknown Extension

```
Command: python stout-create-skill/scripts/hybrid_validator.py --source-path $env:TEMP/stout-multiformat-source
Exit code: 1
Output: [ERRO] Extensao obrigatoria nao catalogada: unknown.extension
```

### Legacy Reference Scan

```
Command: validate_active_pipeline((stout-create-skill, stout-skill-manager, stout-promote-skill))
Exit code: 0
Result: 0 active legacy references
```

---

## Compatibility Report

Located at: `$env:TEMP/stout-multiformat-demo/compatibility-report.md`

| Extension | Platform | Status | Reason |
|-----------|----------|--------|--------|
| claude.allowed-tools | claude-code | included | platform supported |
| claude.allowed-tools | codex | skipped | extension not supported |
| claude.allowed-tools | commandcode | skipped | extension not supported |
| codex.openai-ui-metadata | codex | included | platform supported |
| codex.openai-ui-metadata | claude-code | skipped | extension not supported |
| commandcode.metadata | commandcode | included | platform supported |
| commandcode.metadata | codex | skipped | extension not supported |

---

## Rollback Test

```
Test: test_second_copy_failure_restores_first_target
Result: PASS - Installation rolled back after simulated failure
```

---

## Files Created/Modified

- `stout-create-skill/scripts/platform_contract.py` - Shared platform IDs and models
- `stout-create-skill/scripts/platform_renderer.py` - Multi-platform renderer
- `stout-create-skill/scripts/hybrid_validator.py` - Source and legacy validation
- `stout-create-skill/config/platform_capabilities.yaml` - Extension catalog
- `stout-skill-manager/scripts/global_installer.py` - Transactional global installer
- `stout-skill-manager/config/global_targets.yaml` - Platform target paths
- `stout-promote-skill/scripts/promote_skills.py` - Updated promotion workflow

## Files Deleted

- `stout-create-skill/references/platform-antigravity.md`
- `stout-skill-manager/config/junction_map.yaml`
- `stout-skill-manager/scripts/junction_guard.py`
