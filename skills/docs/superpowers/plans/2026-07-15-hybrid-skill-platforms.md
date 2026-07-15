# Multi-Format Skill Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate one canonical Stout skill source into independent Codex, Claude Code, and CommandCode packages, then safely install those packages in their global skill directories.

**Architecture:** `SKILL.md` remains the portable source and `skill.platforms.yaml` declares targets and opt-in extensions. The create-skill package validates and renders artifacts to an explicit output directory; the skill manager promotes only validated artifacts to global targets with preflight, backups, and rollback. No junction participates in discovery or installation.

**Tech Stack:** Python 3 standard library, PyYAML, JSON, YAML, Markdown, `unittest`.

## Global Constraints

- Supported platform IDs are exactly `codex`, `claude-code`, and `commandcode`.
- Canonical sources stay under `skills/<skill-name>/`; installed copies are never edited as a source of truth.
- Default targets are all three platforms: `~/.agents/skills`, `~/.claude/skills`, and `~/.commandcode/skills`.
- `SKILL.md` source frontmatter contains only `name` and `description` by default.
- Extensions are absent by default and can add only catalogued, documented platform-specific output.
- Unknown, malformed, or unsupported required extensions fail before any installation.
- `--output-dir` is required for every build-producing CLI.
- A destination collision fails unless `--replace` is explicit; promotion preflights all selected destinations and rolls back on any copy failure.
- Do not use, create, validate, or restore junctions. Do not scan `_archived`, tests, fixtures, or the legacy detector itself for active Antigravity references.

---

## File Structure

- `skills/stout-create-skill/scripts/platform_contract.py`: shared platform IDs, manifest parsing, capability catalog parsing, and report models.
- `skills/stout-create-skill/scripts/platform_renderer.py`: copies a canonical source into one artifact per platform and applies registered extensions.
- `skills/stout-create-skill/scripts/hybrid_validator.py`: validates canonical sources, rendered packages, extension compatibility, and active legacy references.
- `skills/stout-create-skill/config/platform_capabilities.yaml`: catalogued extensions, schemas, output mappings, and official documentation URLs.
- `skills/stout-create-skill/references/platform-*.md`: current authoring rules for the three runtimes and the common contract.
- `skills/stout-create-skill/tests/`: `unittest` suite for creation, rendering, validation, and authoring assets.
- `skills/stout-skill-manager/config/global_targets.yaml`: the three global targets; replaces `junction_map.yaml`.
- `skills/stout-skill-manager/scripts/global_installer.py`: preflight, diff, backup, copy, rollback, and source-side state recording.
- `skills/stout-skill-manager/tests/`: tests for target configuration and transactional deployment.
- `skills/stout-promote-skill/scripts/promote_skills.py`: delegates promotion to the global installer instead of a golden-copy junction model.

### Task 1: Make Canonical Source Metadata Explicit

**Files:**
- Create: `skills/stout-create-skill/tests/__init__.py`
- Create: `skills/stout-create-skill/tests/test_blueprint_engine.py`
- Create: `skills/stout-create-skill/scripts/platform_contract.py`
- Modify: `skills/stout-create-skill/scripts/blueprint_engine.py`
- Modify: `skills/stout-create-skill/scripts/create_pipeline.py`
- Modify: `skills/stout-create-skill/blueprint.json`
- Modify: `skills/stout-create-skill/skill.config.json`

**Interfaces:**

```python
SUPPORTED_PLATFORMS: tuple[str, ...] = ("codex", "claude-code", "commandcode")

@dataclass(frozen=True)
class PlatformManifest:
    targets: tuple[str, ...]
    extensions: tuple[ExtensionRequest, ...]

def write_artifacts(output_dir: Path, blueprint: dict, skill_config: dict) -> None: ...
def create_default_manifest() -> dict: ...
```

- [ ] **Step 1: Write failing blueprint and pipeline tests**

```python
def test_engine_requires_output_dir(self) -> None:
    result = self.run_engine_without_output_dir()
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("--output-dir", result.stderr)

def test_engine_writes_three_targets_and_default_manifest(self) -> None:
    result = self.run_engine(self.output_dir)
    self.assertEqual(result.returncode, 0, result.stderr)
    blueprint = json.loads((self.output_dir / "blueprint.json").read_text())
    config = json.loads((self.output_dir / "skill.config.json").read_text())
    manifest = yaml.safe_load((self.output_dir / "skill.platforms.yaml").read_text())
    self.assertEqual(blueprint["target_platforms"], list(SUPPORTED_PLATFORMS))
    self.assertEqual(list(config["platforms"]), list(SUPPORTED_PLATFORMS))
    self.assertEqual(manifest, {"targets": list(SUPPORTED_PLATFORMS), "extensions": []})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -v`

Expected: failures because `--output-dir` is currently optional/unknown and no manifest is produced.

- [ ] **Step 3: Implement the canonical metadata contract**

```python
SUPPORTED_PLATFORMS = ("codex", "claude-code", "commandcode")


def parse_targets(value: str | None) -> tuple[str, ...]:
    targets = SUPPORTED_PLATFORMS if value is None else tuple(p.strip() for p in value.split(",") if p.strip())
    invalid = set(targets) - set(SUPPORTED_PLATFORMS)
    if invalid or not targets:
        raise ValueError(f"targets invalidos: {', '.join(sorted(invalid))}")
    return targets


def create_default_manifest(targets: tuple[str, ...] = SUPPORTED_PLATFORMS) -> dict:
    return {"targets": list(targets), "extensions": []}
```

Require `--output-dir` in both CLIs. Write `blueprint.json`, `skill.config.json`, and `skill.platforms.yaml` only below that directory. Update the HITL message in `create_pipeline.py` to print the resolved artifact directory.

- [ ] **Step 4: Update checked-in examples**

Replace every active Antigravity/Gemini platform target in the two JSON examples with the three supported IDs. Retain governance `triggers` only in JSON/registry data.

- [ ] **Step 5: Run the focused tests**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -v`

Expected: blueprint tests pass; no `blueprint.json` or `skill.config.json` appears in the test process CWD.

- [ ] **Step 6: Commit**

```bash
git add skills/stout-create-skill/scripts/platform_contract.py skills/stout-create-skill/scripts/blueprint_engine.py skills/stout-create-skill/scripts/create_pipeline.py skills/stout-create-skill/blueprint.json skills/stout-create-skill/skill.config.json skills/stout-create-skill/tests
git commit -m "feat(skills): add platform source contract"
```

### Task 2: Catalog Capabilities and Render Per-Platform Packages

**Files:**
- Create: `skills/stout-create-skill/config/platform_capabilities.yaml`
- Create: `skills/stout-create-skill/scripts/platform_renderer.py`
- Create: `skills/stout-create-skill/tests/test_platform_renderer.py`
- Modify: `skills/stout-create-skill/scripts/platform_contract.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class Capability:
    id: str
    platforms: tuple[str, ...]
    kind: Literal["frontmatter", "file"]
    output: str
    documentation_url: str

@dataclass(frozen=True)
class CompatibilityItem:
    extension_id: str
    platform: str
    status: Literal["included", "skipped", "error"]
    reason: str

def render_source(source_dir: Path, output_dir: Path, catalog: dict) -> list[CompatibilityItem]: ...
```

- [ ] **Step 1: Write failing renderer tests**

```python
def test_renderer_copies_common_files_to_each_target(self) -> None:
    report = render_source(self.source, self.output, self.catalog)
    for platform in SUPPORTED_PLATFORMS:
        artifact = self.output / "rendered" / platform / "demo-skill"
        self.assertTrue((artifact / "SKILL.md").exists())
        self.assertTrue((artifact / "scripts" / "check.py").exists())
    self.assertEqual({item.status for item in report}, {"included"})

def test_optional_claude_extension_is_skipped_elsewhere(self) -> None:
    report = render_source(self.source_with_allowed_tools, self.output, self.catalog)
    statuses = {(item.platform, item.status) for item in report}
    self.assertIn(("claude-code", "included"), statuses)
    self.assertIn(("codex", "skipped"), statuses)
    self.assertIn(("commandcode", "skipped"), statuses)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -p "test_platform_renderer.py" -v`

Expected: module import failure because the renderer and catalog do not exist.

- [ ] **Step 3: Add the capability catalog and renderer**

Use this initial catalog shape; every record must include its official URL:

```yaml
extensions:
  claude.allowed-tools:
    platforms: [claude-code]
    kind: frontmatter
    output: allowed-tools
    value_type: string_list
    documentation_url: https://code.claude.com/docs/en/skills
  codex.openai-ui-metadata:
    platforms: [codex]
    kind: file
    output: agents/openai.yaml
    value_type: mapping
    documentation_url: https://learn.chatgpt.com/docs/build-skills.md
  commandcode.metadata:
    platforms: [commandcode]
    kind: frontmatter
    output: metadata
    value_type: mapping
    documentation_url: https://commandcode.ai/docs/skills
```

Copy every common source entry except `.stout-install.json`, `skill.platforms.yaml`, and `platform-overrides/`. Apply an extension only to catalogued target platforms. Create rendered artifacts under `<output-dir>/rendered/<platform>/<skill-name>/`. Expose a CLI with required `--source-path` and `--output-dir`; it loads `platform_capabilities.yaml`, validates the source, writes both compatibility reports, and returns `1` on any `error` item.

- [ ] **Step 4: Emit deterministic compatibility reports**

```python
def write_compatibility_reports(output_dir: Path, items: list[CompatibilityItem]) -> None:
    payload = [asdict(item) for item in sorted(items, key=lambda item: (item.extension_id, item.platform))]
    (output_dir / "compatibility-report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    rows = ["| Extensao | Plataforma | Status | Motivo |", "| --- | --- | --- | --- |"]
    rows.extend(f"| {item.extension_id} | {item.platform} | {item.status} | {item.reason} |" for item in payload)
    (output_dir / "compatibility-report.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
```

- [ ] **Step 5: Run the focused tests**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -v`

Expected: all renderer tests pass and reports contain stable ordering.

- [ ] **Step 6: Commit**

```bash
git add skills/stout-create-skill/config/platform_capabilities.yaml skills/stout-create-skill/scripts/platform_contract.py skills/stout-create-skill/scripts/platform_renderer.py skills/stout-create-skill/tests/test_platform_renderer.py
git commit -m "feat(skills): render platform packages"
```

### Task 3: Enforce Source, Extension, and Legacy Validation

**Files:**
- Create: `skills/stout-create-skill/scripts/hybrid_validator.py`
- Create: `skills/stout-create-skill/tests/test_hybrid_validator.py`
- Modify: `skills/stout-create-skill/scripts/skill_validator.py`

**Interfaces:**

```python
def validate_source(source_dir: Path, catalog: dict) -> list[str]: ...
def validate_rendered_package(platform: str, package_dir: Path, catalog: dict) -> list[str]: ...
def validate_active_pipeline(roots: tuple[Path, ...]) -> list[str]: ...
```

- [ ] **Step 1: Write failing validator tests**

```python
def test_required_unsupported_extension_blocks_all_artifacts(self) -> None:
    errors = validate_source(self.source_with_required_unsupported_extension, self.catalog)
    self.assertTrue(any("obrigatoria" in error for error in errors))

def test_active_legacy_scan_ignores_fixture_and_archive(self) -> None:
    errors = validate_active_pipeline(self.active_roots)
    self.assertFalse(any("fixture" in error or "_archived" in error for error in errors))
    self.active_factory_file.write_text("<!-- @if platform=antigravity -->", encoding="utf-8")
    self.assertTrue(validate_active_pipeline(self.active_roots))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -p "test_hybrid_validator.py" -v`

Expected: import failure because `hybrid_validator.py` does not exist.

- [ ] **Step 3: Implement validation rules and CLI**

Validate non-empty `name` and `description`, match the directory name, accept only catalogued extension IDs and exact value types, and require `required` to be boolean. Scan only these roots: `skills/stout-create-skill`, `skills/stout-skill-manager`, and `skills/stout-promote-skill`; exclude `tests`, `fixtures`, `_archived`, and `hybrid_validator.py`.

The CLI must print one `[ERRO]` per violation and exit `1` before it calls the renderer or installer.

- [ ] **Step 4: Connect the existing quality gate**

Call `hybrid_validator.py --source-path <path>` from `skill_validator.py` before its existing filesystem/security checks. Retain the old checks but remove requirements for `version`, `tools`, and `tier` from portable source frontmatter.

- [ ] **Step 5: Run validation tests**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -v`

Expected: valid source and optional extensions pass; all invalid extension, frontmatter, junction, preprocessing, and active Antigravity cases fail with code `1`.

- [ ] **Step 6: Commit**

```bash
git add skills/stout-create-skill/scripts/hybrid_validator.py skills/stout-create-skill/scripts/skill_validator.py skills/stout-create-skill/tests/test_hybrid_validator.py
git commit -m "feat(skills): validate platform compatibility"
```

### Task 4: Replace Junction Distribution with Transactional Global Installation

**Files:**
- Create: `skills/stout-skill-manager/config/global_targets.yaml`
- Create: `skills/stout-skill-manager/scripts/global_installer.py`
- Create: `skills/stout-skill-manager/tests/__init__.py`
- Create: `skills/stout-skill-manager/tests/test_global_installer.py`
- Modify: `skills/stout-skill-manager/scripts/orchestrator.py`
- Delete: `skills/stout-skill-manager/config/junction_map.yaml`
- Delete: `skills/stout-skill-manager/scripts/junction_guard.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class GlobalTarget:
    platform: str
    path: Path

def load_global_targets(config_path: Path) -> dict[str, GlobalTarget]: ...
def install_artifacts(source_dir: Path, artifacts_dir: Path, targets: tuple[str, ...], replace: bool) -> dict: ...
```

- [ ] **Step 1: Write failing installer tests**

```python
def test_collision_requires_replace(self) -> None:
    self.create_destination("codex", "demo-skill", "old")
    result = install_artifacts(self.source, self.artifacts, ("codex",), replace=False)
    self.assertEqual(result["status"], "collision")
    self.assertEqual(self.destination_text("codex"), "old")

def test_second_copy_failure_restores_first_target(self) -> None:
    self.fail_copy_for("claude-code")
    result = install_artifacts(self.source, self.artifacts, ("codex", "claude-code"), replace=True)
    self.assertEqual(result["status"], "rolled_back")
    self.assertEqual(self.destination_text("codex"), "old-codex")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s skills/stout-skill-manager/tests -t . -v`

Expected: import failure because global target configuration and installer do not exist.

- [ ] **Step 3: Implement global target configuration and installation**

```yaml
targets:
  codex: "%USERPROFILE%/.agents/skills"
  claude-code: "%USERPROFILE%/.claude/skills"
  commandcode: "%USERPROFILE%/.commandcode/skills"
```

Resolve `%USERPROFILE%` in one function. Preflight every selected target, render a text diff on an existing destination, and return `collision` unless `replace=True`. For replacement, move existing destinations into a temporary backup directory, copy every artifact, and restore all backups if any copy fails.

Write `.stout-install.json` only in the canonical source with the artifact hashes, installed targets, and timestamp; never copy it to global destinations.

- [ ] **Step 4: Integrate the manager CLI**

Replace `run_junction_guard` and `run_skillfish_install` in `orchestrator.py` with staging import, render/validation, and `install_artifacts`. Add `--platforms`, `--replace`, and `--artifact-dir`; default `--platforms` to all three. The direct external-import path must first copy the fetched source into `skills/<skill-name>/`, then build and install its artifacts.

- [ ] **Step 5: Run installer tests**

Run: `python -m unittest discover -s skills/stout-skill-manager/tests -t . -v`

Expected: configuration has exactly three targets; collision is non-destructive; `--replace` works; a simulated failure restores every prior destination.

- [ ] **Step 6: Commit**

```bash
git add skills/stout-skill-manager/config/global_targets.yaml skills/stout-skill-manager/scripts/global_installer.py skills/stout-skill-manager/scripts/orchestrator.py skills/stout-skill-manager/tests
git rm skills/stout-skill-manager/config/junction_map.yaml skills/stout-skill-manager/scripts/junction_guard.py
git commit -m "feat(skills): install rendered packages globally"
```

### Task 5: Align Promotion, Templates, Agents, and References

**Files:**
- Modify: `skills/stout-promote-skill/scripts/promote_skills.py`
- Modify: `skills/stout-create-skill/SKILL.md`
- Modify: `skills/stout-skill-manager/SKILL.md`
- Create: `skills/stout-create-skill/references/platform-codex.md`
- Create: `skills/stout-create-skill/references/platform-hybrid.md`
- Modify: `skills/stout-create-skill/references/platform-claude.md`
- Modify: `skills/stout-create-skill/references/platform-commandcode.md`
- Delete: `skills/stout-create-skill/references/platform-antigravity.md`
- Modify: `skills/stout-create-skill/references/skill-anatomy.md`
- Modify: `skills/stout-create-skill/references/template-engine.md`
- Modify: both `skills/stout-create-skill/agents/*drafter*.md` and both scaffolder prompts
- Modify: `skills/stout-create-skill/templates/tier-1-utility.md`, `tier-2-feature.md`, `tier-3-platform.md`, `tier-4-orchestrator.md`
- Modify: `skills/stout-create-skill/tests/test_hybrid_validator.py`

- [ ] **Step 1: Write failing documentation assertions**

```python
def test_all_authoring_assets_name_the_multiformat_contract(self) -> None:
    for reference in ("platform-codex.md", "platform-claude.md", "platform-commandcode.md", "platform-hybrid.md"):
        self.assertTrue((REFERENCES / reference).exists())
    for agent in DRAFTER_AGENTS:
        text = agent.read_text(encoding="utf-8")
        self.assertIn("platform-hybrid.md", text)
        self.assertIn("skill.platforms.yaml", text)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -v`

Expected: Codex/hybrid references and multi-format authoring instructions are absent.

- [ ] **Step 3: Rewrite authoring material**

Every tier template must start with only:

```yaml
---
name: PLACEHOLDER_NAME
description: Use quando PLACEHOLDER_TRIGGER. Executa PLACEHOLDER_ACTION para PLACEHOLDER_DOMINIO.
---
```

The hybrid reference defines the common body and `skill.platforms.yaml`. Platform references define only catalogued additions. Agents must read all four references, create source manifests with empty `extensions`, write outputs under the explicit artifact directory, and never emit `@if`, `@unless`, `triggers`, Antigravity paths, or junction instructions in source `SKILL.md`.

- [ ] **Step 4: Update promotion**

Make `promote_skills.py` invoke the renderer and `global_installer.install_artifacts` for each promoted source. Remove `GOLDEN_COPY`, source-equals-destination behavior, and archive behavior that assumes the golden copy is an installation directory. Preserve registry updates after all selected targets install successfully.

- [ ] **Step 5: Run authoring and promotion tests**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -v; python -m unittest discover -s skills/stout-skill-manager/tests -t . -v`

Expected: templates validate as portable sources; no active authoring text contains legacy distribution instructions.

- [ ] **Step 6: Commit**

```bash
git add skills/stout-promote-skill skills/stout-create-skill/SKILL.md skills/stout-skill-manager/SKILL.md skills/stout-create-skill/references skills/stout-create-skill/agents skills/stout-create-skill/templates skills/stout-create-skill/tests
git rm skills/stout-create-skill/references/platform-antigravity.md
git commit -m "docs(skills): author multiformat sources"
```

### Task 6: Run End-to-End Verification and Record Evidence

**Files:**
- Create: `skills/docs/superpowers/validation/2026-07-15-hybrid-skill-platforms.md`
- Modify: `skills/docs/superpowers/specs/2026-07-15-hybrid-skill-platforms-design.md` only if validation reveals a specification correction

- [ ] **Step 1: Run all unit suites**

Run: `python -m unittest discover -s skills/stout-create-skill/tests -t . -v; python -m unittest discover -s skills/stout-skill-manager/tests -t . -v`

Expected: every test passes.

- [ ] **Step 2: Build a portable fixture**

Run: `python skills/stout-create-skill/scripts/blueprint_engine.py --tier 2 --name demo-skill --description "Use quando precisar testar a skill demo." --output-dir $env:TEMP/stout-multiformat-demo`

Expected: exit `0`; the output contains only `blueprint.json`, `skill.config.json`, and `skill.platforms.yaml`, all below `$env:TEMP/stout-multiformat-demo`.

- [ ] **Step 3: Verify extension compatibility and failure handling**

Run: `python skills/stout-create-skill/scripts/platform_renderer.py --source-path $env:TEMP/stout-multiformat-source --output-dir $env:TEMP/stout-multiformat-demo`; prepare the source with `extensions: [{id: claude.allowed-tools, required: false, value: [Read, Grep]}]`, then repeat with `{id: unknown.extension, required: true, value: {}}`.

Expected: the first build reports Claude `included` and the other two `skipped`; the second exits `1` before it creates any global destination.

- [ ] **Step 4: Verify legacy and junction removal**

Run: `python skills/stout-create-skill/scripts/hybrid_validator.py --pipeline-root .; rg -n -i 'antigravity|\.gemini/antigravity|@if platform|@unless platform|junction_guard|junction_map' skills/stout-create-skill skills/stout-skill-manager skills/stout-promote-skill --glob '!tests/**' --glob '!fixtures/**'`

Expected: validator exits `0`; the search has no active matches except the detector's explicit legacy-marker constants.

- [ ] **Step 5: Record evidence**

Create a table mapping T-001 through T-009 to the exact command, exit code, and PASS result. Include the compatibility report path and rollback test name; do not include unrelated command output.

- [ ] **Step 6: Commit**

```bash
git add skills/docs/superpowers/validation
git commit -m "test(skills): verify multiformat platform flow"
```

## Plan Self-Review

| Requirement | Implementing tasks |
| --- | --- |
| FR-001 / direct three-platform configuration and no junctions | 1, 4, 6 |
| FR-002 / required output directory and internal metadata | 1 |
| FR-003 / canonical source and manifest | 1, 2 |
| FR-004 / independent rendered packages | 2 |
| FR-005 / catalog, statuses, and early failure | 2, 3, 6 |
| FR-006 / collision, backups, rollback, installation state | 4, 6 |
| FR-007 / documented authoring and agents | 5 |
| FR-008 / scoped active legacy detection | 3, 6 |

The plan contains no placeholders. All paths use the actual `skills/` repository prefix and all public interfaces are defined before the tasks that consume them.
