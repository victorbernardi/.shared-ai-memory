# Hybrid Skill Platforms Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernizar a fabrica Stout para gerar skills portaveis para Codex, Claude Code e CommandCode, removendo o legado ativo do Antigravity.

**Architecture:** A fabrica continua usando `blueprint.json` e `skill.config.json` como contratos internos, mas produz uma unica fonte `SKILL.md` com frontmatter minimo. As diferencas de runtime ficam nas referencias; um validador independente impede o retorno de metadados, diretivas e caminhos legados.

**Tech Stack:** Python 3 standard library, PyYAML ja utilizado no repositorio, Markdown, JSON e YAML.

## Global Constraints

- Frontmatter de skills hibridas: somente `name` e `description`.
- Metadados `triggers` permanecem em blueprint, config e registry; nao no `SKILL.md` hibrido.
- Plataformas permitidas: `codex`, `claude-code`, `commandcode`.
- Nao usar `@if platform`, `@unless` ou preprocessamento de `SKILL.md`.
- O manager nao pode criar nem substituir junction para o diretorio global do Codex.
- Nao alterar `_archived` ou skills que nao sejam chamadas pelo pipeline.

---

## File Structure

- `stout-create-skill/scripts/blueprint_engine.py`: gera os contratos JSON para as tres plataformas e recebe diretorio de saida explicito.
- `stout-create-skill/scripts/hybrid_validator.py`: valida uma skill hibrida e referencias ativas do pipeline.
- `stout-create-skill/tests/test_blueprint_engine.py`: exercita o gerador por subprocesso em diretorio temporario.
- `stout-create-skill/tests/test_hybrid_validator.py`: cobre skills validas e violacoes de compatibilidade.
- `stout-create-skill/references/platform-*.md`: documentacao por runtime e contrato compartilhado.
- `stout-create-skill/templates/*.md` e `agents/*.md`: fontes de geracao alinhadas ao contrato hibrido.
- `stout-skill-manager/config/junction_map.yaml` e `SKILL.md`: remocao do legado de distribuicao.

### Task 1: Make Blueprint Generation Explicit and Testable

**Files:**
- Create: `stout-create-skill/tests/__init__.py`
- Create: `stout-create-skill/tests/test_blueprint_engine.py`
- Modify: `stout-create-skill/scripts/blueprint_engine.py`
- Modify: `stout-create-skill/scripts/create_pipeline.py`
- Modify: `stout-create-skill/blueprint.json`
- Modify: `stout-create-skill/skill.config.json`

**Interfaces:**
- Produces: `SUPPORTED_PLATFORMS: tuple[str, ...] = ("codex", "claude-code", "commandcode")`.
- Produces: `write_artifacts(output_dir: Path, blueprint: dict, skill_config: dict) -> None`.
- Consumes: `--output-dir` from `create_pipeline.py` and `blueprint_engine.py`.

- [ ] **Step 1: Write the failing generator tests**

```python
class BlueprintEngineTests(unittest.TestCase):
    def run_engine(self, output_dir: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ENGINE), "--tier", "2", "--name", "demo-skill",
             "--description", "Use quando precisar validar uma skill demo.",
             "--output-dir", str(output_dir), *extra],
            check=False, capture_output=True, text=True, encoding="utf-8",
        )

    def test_default_targets_are_the_three_supported_platforms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "artifacts"
            result = self.run_engine(output_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            blueprint = json.loads((output_dir / "blueprint.json").read_text(encoding="utf-8"))
            config = json.loads((output_dir / "skill.config.json").read_text(encoding="utf-8"))
            self.assertEqual(blueprint["target_platforms"], ["codex", "claude-code", "commandcode"])
            self.assertEqual(list(config["platforms"]), ["codex", "claude-code", "commandcode"])

    def test_engine_never_writes_artifacts_to_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "cwd"
            output_dir = Path(tmp) / "artifacts"
            cwd.mkdir()
            result = subprocess.run(`n                [sys.executable, str(ENGINE), "--tier", "2", "--name", "demo-skill",`n                 "--description", "Use quando precisar validar uma skill demo.",`n                 "--output-dir", str(output_dir)],`n                cwd=cwd, check=False, capture_output=True, text=True, encoding="utf-8",`n            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / "blueprint.json").exists())
            self.assertFalse((cwd / "blueprint.json").exists())
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest stout-create-skill.tests.test_blueprint_engine -v`

Expected: FAIL because `--output-dir` is unknown and the default includes Antigravity.

- [ ] **Step 3: Implement the minimal generator change**

```python
SUPPORTED_PLATFORMS = ("codex", "claude-code", "commandcode")


def write_artifacts(output_dir: Path, blueprint: dict, skill_config: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "blueprint.json").write_text(
        json.dumps(blueprint, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "skill.config.json").write_text(
        json.dumps(skill_config, indent=2, ensure_ascii=False), encoding="utf-8"
    )
```

Add `--output-dir` with a default of the factory directory, reject every value outside `SUPPORTED_PLATFORMS`, and generate `body.sections` with `"all"` for every supported platform. Pass the same output directory from `create_pipeline.py`; its HITL message must name the generated artifact directory.

- [ ] **Step 4: Update checked-in example artifacts**

Replace the Antigravity target in both JSON examples with `codex`. Preserve the `triggers` data model where it exists; do not add it to `SKILL.md` content.

- [ ] **Step 5: Run the generator tests**

Run: `python -m unittest stout-create-skill.tests.test_blueprint_engine -v`

Expected: both tests PASS.

- [ ] **Step 6: Commit**

```bash
git add stout-create-skill/scripts/blueprint_engine.py stout-create-skill/scripts/create_pipeline.py stout-create-skill/blueprint.json stout-create-skill/skill.config.json stout-create-skill/tests
git commit -m "fix(skills): target hybrid platforms"
```

### Task 2: Enforce the Hybrid Skill Contract

**Files:**
- Create: `stout-create-skill/scripts/hybrid_validator.py`
- Create: `stout-create-skill/tests/test_hybrid_validator.py`
- Modify: `stout-create-skill/scripts/skill_validator.py`

**Interfaces:**
- Produces: `validate_skill(skill_path: Path) -> list[str]`.
- Produces: `validate_pipeline(pipeline_root: Path) -> list[str]`.
- Consumes: a skill directory containing `SKILL.md` and the active factory/manager directories.

- [ ] **Step 1: Write the failing validator tests**

```python
class HybridValidatorTests(unittest.TestCase):
    def write_skill(self, root: Path, frontmatter: str, body: str = "# Demo\n") -> Path:
        skill = root / "demo-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}", encoding="utf-8")
        return skill

    def test_accepts_minimal_portable_frontmatter(self) -> None:
        skill = self.write_skill(Path(self.tempdir.name), "name: demo-skill\ndescription: Use quando precisar de uma demo portatil.")
        self.assertEqual(validate_skill(skill), [])

    def test_rejects_runtime_only_frontmatter_and_conditional_directives(self) -> None:
        skill = self.write_skill(Path(self.tempdir.name), "name: demo-skill\ndescription: Use quando precisar de uma demo.\ntriggers: [demo]", "<!-- @if platform=codex -->")
        errors = validate_skill(skill)
        self.assertTrue(any("triggers" in error for error in errors))
        self.assertTrue(any("@if platform" in error for error in errors))

    def test_rejects_antigravity_in_active_pipeline_files(self) -> None:
        root = Path(self.tempdir.name)
        (root / "SKILL.md").write_text("antigravity", encoding="utf-8")
        self.assertTrue(validate_pipeline(root))
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest stout-create-skill.tests.test_hybrid_validator -v`

Expected: FAIL because `hybrid_validator.py` does not exist.

- [ ] **Step 3: Implement the validator and connect it to the quality gate**

```python
ALLOWED_FRONTMATTER = {"name", "description"}
LEGACY_MARKERS = ("antigravity", ".gemini/antigravity", "@if platform", "@unless platform")


def validate_skill(skill_path: Path) -> list[str]:
    metadata, body = parse_skill(skill_path / "SKILL.md")
    errors = [f"frontmatter field not portable: {key}" for key in metadata if key not in ALLOWED_FRONTMATTER]
    errors.extend(f"legacy directive found: {marker}" for marker in LEGACY_MARKERS[2:] if marker in body.lower())
    return errors
```

Parse YAML with `yaml.safe_load`, require non-empty `name` and `description`, and make the CLI print one `[ERRO]` per violation before returning `1`. Update `skill_validator.py` to run `hybrid_validator.py --skill-path <path>` before its existing security checks and fail when the hybrid contract fails.

- [ ] **Step 4: Run the validator tests**

Run: `python -m unittest stout-create-skill.tests.test_hybrid_validator -v`

Expected: all three tests PASS.

- [ ] **Step 5: Commit**

```bash
git add stout-create-skill/scripts/hybrid_validator.py stout-create-skill/scripts/skill_validator.py stout-create-skill/tests/test_hybrid_validator.py
git commit -m "feat(skills): validate hybrid contract"
```

### Task 3: Replace Legacy Authoring Guidance and Templates

**Files:**
- Create: `stout-create-skill/references/platform-codex.md`
- Create: `stout-create-skill/references/platform-hybrid.md`
- Delete: `stout-create-skill/references/platform-antigravity.md`
- Modify: `stout-create-skill/references/platform-claude.md`
- Modify: `stout-create-skill/references/platform-commandcode.md`
- Modify: `stout-create-skill/references/skill-anatomy.md`
- Modify: `stout-create-skill/references/template-engine.md`
- Modify: `stout-create-skill/agents/code_drafter_agent.md`
- Modify: `stout-create-skill/agents/code-drafter-agent.md`
- Modify: `stout-create-skill/agents/scaffolder_agent.md`
- Modify: `stout-create-skill/agents/scaffold-agent.md`
- Modify: `stout-create-skill/templates/tier-1-utility.md`
- Modify: `stout-create-skill/templates/tier-2-feature.md`
- Modify: `stout-create-skill/templates/tier-3-platform.md`
- Modify: `stout-create-skill/templates/tier-4-orchestrator.md`

**Interfaces:**
- Consumes: `references/platform-hybrid.md` as the shared authoring contract.
- Produces: template frontmatter with exactly `name` and `description`.

- [ ] **Step 1: Write failing content assertions**

Add assertions to `test_hybrid_validator.py` that each tier template validates after replacing the name and description sample values, that the four supported reference files exist, and that `code_drafter_agent.md` lists all four references.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest stout-create-skill.tests.test_hybrid_validator -v`

Expected: FAIL because Codex and hybrid references are absent and templates retain non-portable fields or directives.

- [ ] **Step 3: Write the portable references**

`platform-codex.md` must state that Codex activates skills from `name` and `description`, favors progressive disclosure, and uses `scripts/`, `references/` and `assets/` only for their defined roles. `platform-hybrid.md` must define the common frontmatter, description-writing rules, body structure and prohibition on runtime-only instructions. Claude and CommandCode references must contain only their documented, optional differences and point back to `platform-hybrid.md`.

- [ ] **Step 4: Rewrite the templates and agent prompts**

Use this frontmatter in every tier template:

```yaml
---
name: PLACEHOLDER_NAME
description: >
  Use quando PLACEHOLDER_TRIGGER. Executa PLACEHOLDER_ACTION
  para PLACEHOLDER_DOMINIO.
---
```

Remove `tools`, `triggers`, tier metadata, `.gemini` prerequisites, `@if` blocks and all Antigravity references. Keep `triggers` as data only in the JSON artifacts. Make both scaffolder prompts consume the explicit artifact directory rather than the current working directory.

- [ ] **Step 5: Run the content assertions**

Run: `python -m unittest stout-create-skill.tests.test_hybrid_validator -v`

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add stout-create-skill/references stout-create-skill/agents stout-create-skill/templates stout-create-skill/tests/test_hybrid_validator.py
git commit -m "docs(skills): add hybrid authoring guidance"
```

### Task 4: Remove Active Antigravity Distribution and Verify the Pipeline

**Files:**
- Modify: `stout-skill-manager/config/junction_map.yaml`
- Modify: `stout-skill-manager/SKILL.md`
- Modify: `stout-create-skill/SKILL.md`
- Modify: `docs/superpowers/specs/2026-07-15-hybrid-skill-platforms-design.md`
- Create: `docs/superpowers/validation/2026-07-15-hybrid-skill-platforms.md`

**Interfaces:**
- Consumes: `junction_map.yaml` with only `claude-code` and `commandcode` junctions.
- Produces: a validation report mapping T-001 through T-005 to command output.

- [ ] **Step 1: Write the failing manager configuration assertion**

Add this test to `test_hybrid_validator.py`:

```python
def test_junction_map_has_no_legacy_runtime(self) -> None:
    data = yaml.safe_load(JUNCTION_MAP.read_text(encoding="utf-8"))
    rendered = json.dumps(data).lower()
    self.assertNotIn("antigravity", rendered)
    self.assertNotIn(".gemini", rendered)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest stout-create-skill.tests.test_hybrid_validator.HybridValidatorTests.test_junction_map_has_no_legacy_runtime -v`

Expected: FAIL because the map still declares two Antigravity junctions.

- [ ] **Step 3: Update manager and factory instructions**

Remove both Antigravity junction entries. Do not add a Codex junction: `~/.codex/skills` is locally managed and must not be renamed or replaced by `junction_guard.py`. Rewrite the manager and factory skill instructions to present Codex, Claude Code and CommandCode as supported formats; state that activation phrases belong in `description` and governance triggers stay in JSON/registry.

- [ ] **Step 4: Run the complete verification suite**

Run: `python -m unittest discover -s stout-create-skill/tests -v`

Expected: all tests PASS.

Run: `python stout-create-skill/scripts/blueprint_engine.py --tier 2 --name demo-skill --description "Use quando precisar testar a skill demo." --output-dir $env:TEMP/stout-hybrid-demo`

Expected: exit `0`; both JSON files exist only under `$env:TEMP/stout-hybrid-demo` and list `codex`, `claude-code`, `commandcode`.

Run: `$fixture = Join-Path $env:TEMP "stout-hybrid-valid-skill"; New-Item -ItemType Directory -Force $fixture | Out-Null; "---`nname: valid-skill`ndescription: Use quando precisar validar uma skill hibrida.`n---`n# Valid skill" | Set-Content "$fixture/SKILL.md"; python stout-create-skill/scripts/hybrid_validator.py --skill-path $fixture --pipeline-root .`

Expected: exit `0` and `[OK]` output.

Run: `rg -n -i 'antigravity|\.gemini/antigravity|@if platform|@unless platform' stout-create-skill stout-skill-manager stout-promote-skill --glob '!audit_result.json'`

Expected: no active matches.

- [ ] **Step 5: Record validation evidence**

Create `docs/superpowers/validation/2026-07-15-hybrid-skill-platforms.md` with a row for T-001 through T-005, the exact command run, its exit code and PASS status. Do not include command output unrelated to this branch.

- [ ] **Step 6: Commit**

```bash
git add stout-skill-manager stout-create-skill/SKILL.md docs/superpowers/specs docs/superpowers/validation
git commit -m "chore(skills): remove antigravity pipeline"
```
