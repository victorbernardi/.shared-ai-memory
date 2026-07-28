# Superpowers Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a skill `superpowers-update` que compara `obra/superpowers/main` com a fonte local e os quatro runtimes do usuário, atualizando somente skills divergentes com rollback e sem poluir o repositório com relatórios.

**Architecture:** Um script Python somente com biblioteca padrão fará clone temporário, descoberta, comparação normalizada por LF e sincronização transacional. O `SKILL.md` será a interface operacional, com modos `check` e `apply`; a atualização não fará commit, push, merge ou exclusão de arquivos extras. Testes `unittest` cobrirão o comparador, preservação de extras, relatório temporário e rollback.

**Tech Stack:** Python 3.10+ stdlib (`argparse`, `hashlib`, `json`, `shutil`, `subprocess`, `tempfile`, `unittest`), Git CLI, Agent Skills Markdown, registry JSON Stout.

## Global Constraints

- Fonte obrigatória: `https://github.com/obra/superpowers.git`, branch `main`.
- Destinos padrão: `.shared-ai-memory\skills`, `.agents\skills`, `.codex\skills`, `.claude\skills`, `.commandcode\skills`.
- Comparação ignora somente CRLF/LF; conteúdo diferente continua divergente.
- Atualizar somente skills afetadas; nunca apagar arquivos extras locais.
- Skills presentes apenas nos destinos são `extra_skills`; `removed` só é usado quando a entrada informa que a skill era gerenciada pelo Superpowers.
- Relatório padrão somente em `%TEMP%\superpowers-update\<run-id>` e removido ao terminar.
- Persistir relatório apenas quando `--report` for informado.
- Não executar `git reset`, `git clean`, `git push`, `git merge`, `git force-push` ou exclusão de branches.
- A instalação usa `skills/` como caminho canônico; `.claude\skills` e `.commandcode\skills` são junctions para ele. Cópias físicas adicionais, quando necessárias para os runtimes atuais, serão feitas somente em `.agents\skills` e `.codex\skills`, depois do `junction_guard`.

## File Map

- Create: `skills/superpowers-update/SKILL.md` — gatilhos, modos, segurança e comandos.
- Create: `skills/superpowers-update/scripts/superpowers_update.py` — CLI, clone, comparação, sincronização e relatório.
- Create: `skills/superpowers-update/tests/test_superpowers_update.py` — testes unitários sem dependências externas.
- Modify: `skills/stout-skill-registry/registry.json` — registrar a nova skill e seus gatilhos.
- Create: `docs/superpowers/specs/2026-07-28-superpowers-update-design.md` — especificação aprovada.
- Create: `docs/superpowers/plans/2026-07-28-superpowers-update.md` — este plano.

### Task 1: Comparador puro e contrato do relatório

**Files:**
- Create: `skills/superpowers-update/scripts/superpowers_update.py`
- Create: `skills/superpowers-update/tests/test_superpowers_update.py`

**Interfaces:**
- Produces `normalize_content(data: bytes) -> bytes`.
- Produces `snapshot_skill(root: Path) -> dict[str, bytes]`.
- Produces `compare_skill(source: dict[str, bytes], target: dict[str, bytes]) -> dict[str, list[str]]` with keys `missing`, `changed`, `extra`, `equal`.
- Produces `build_report(source_sha: str, comparisons: dict[str, dict]) -> dict` with `status`, `source_sha`, `changed_skills`, `comparisons`.

- [ ] **Step 1: Write the failing tests**

```python
def test_compare_ignores_crlf_but_detects_content_change():
    source = {"SKILL.md": b"line 1\nline 2\n"}
    target = {"SKILL.md": b"line 1\r\nline 2\r\n"}
    assert compare_skill(source, target)["equal"] is True

    target["SKILL.md"] = b"line 1\r\nlegacy\r\n"
    result = compare_skill(source, target)
    assert result["changed"] == ["SKILL.md"]
    assert result["equal"] is False
```

```python
def test_compare_reports_missing_and_extra_files():
    result = compare_skill(
        {"SKILL.md": b"current", "scripts/run.py": b"run"},
        {"SKILL.md": b"current", "legacy.md": b"keep"},
    )
    assert result["missing"] == ["scripts/run.py"]
    assert result["extra"] == ["legacy.md"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s skills/superpowers-update/tests -v`
Expected: FAIL because the package and comparison functions do not exist.

- [ ] **Step 3: Implement the minimal pure functions**

Implement byte normalization, recursive text snapshotting, deterministic sorted paths, comparison classification, and the report contract without invoking Git or writing files.

- [ ] **Step 4: Run the focused tests**

Run: `python -m unittest discover -s skills/superpowers-update/tests -v`
Expected: PASS for normalization, missing/changed/extra classification, and report status.

- [ ] **Step 5: Commit the testable unit**

```powershell
git add skills/superpowers-update/scripts/superpowers_update.py skills/superpowers-update/tests/test_superpowers_update.py
git commit -m "test: define superpowers update comparison contract"
```

### Task 2: Clone, discovery, check mode and temporary reports

**Files:**
- Modify: `skills/superpowers-update/scripts/superpowers_update.py`
- Modify: `skills/superpowers-update/tests/test_superpowers_update.py`

**Interfaces:**
- Produces `discover_skill_dirs(repo_root: Path) -> dict[str, Path]`.
- Produces `clone_source(url: str, branch: str, temp_root: Path) -> tuple[Path, str]`.
- Produces `default_targets(home: Path) -> list[Path]`.
- Produces `run_check(source_root: Path, targets: list[Path]) -> dict`.
- Produces `emit_report(report: dict, report_path: Path | None) -> None`.

- [ ] **Step 1: Add failing tests for discovery and report hygiene**

```python
def test_discover_only_skill_directories_with_skill_md(tmp_path):
    (tmp_path / "skills" / "valid").mkdir(parents=True)
    (tmp_path / "skills" / "valid" / "SKILL.md").write_text("x", encoding="utf-8")
    (tmp_path / "skills" / "not-a-skill").mkdir()
    assert list(discover_skill_dirs(tmp_path).keys()) == ["valid"]
```

```python
def test_report_is_written_only_when_explicit_path_is_given(tmp_path):
    report = {"status": "NO_OP"}
    emit_report(report, None)
    assert list(tmp_path.iterdir()) == []
    path = tmp_path / "report.json"
    emit_report(report, path)
    assert json.loads(path.read_text(encoding="utf-8")) == report
```

- [ ] **Step 2: Run the tests to verify the new cases fail**

Run: `python -m unittest discover -s skills/superpowers-update/tests -v`
Expected: FAIL for missing discovery and report functions.

- [ ] **Step 3: Implement check mode**

Use `tempfile.TemporaryDirectory(prefix="superpowers-update-")`, `git clone --depth 1 --branch main --single-branch`, and `git rev-parse HEAD`. Resolve default targets from `Path.home()`, add repeated `--target` paths, compare every discovered skill, and print one JSON summary to stdout. Do not create files below the source repository unless `--report` is provided.

- [ ] **Step 4: Run focused tests and a local check fixture**

Run: `python -m unittest discover -s skills/superpowers-update/tests -v`
Expected: PASS.
Run: `python skills/superpowers-update/scripts/superpowers_update.py --help`
Expected: help lists `check`, `apply`, repeated `--target`, `--source-root`, and `--report`.

- [ ] **Step 5: Commit check mode**

```powershell
git add skills/superpowers-update/scripts/superpowers_update.py skills/superpowers-update/tests/test_superpowers_update.py
git commit -m "feat: add superpowers update check mode"
```

### Task 3: Transactional apply mode

**Files:**
- Modify: `skills/superpowers-update/scripts/superpowers_update.py`
- Modify: `skills/superpowers-update/tests/test_superpowers_update.py`

**Interfaces:**
- Produces `copy_skill_files(source_dir: Path, target_dir: Path) -> None`.
- Produces `sync_skill_to_targets(source_dir: Path, targets: list[Path]) -> None`.
- CLI `apply` calls preflight, exits `NO_OP` without writing when equal, and returns `UPDATED` after post-copy verification.

- [ ] **Step 1: Add failing tests for selective copy, extras, and rollback**

```python
def test_apply_updates_only_changed_skill_and_preserves_extra(tmp_path):
    source = make_skill_tree(tmp_path / "source", {"SKILL.md": "new"})
    target = make_skill_tree(tmp_path / "target", {"SKILL.md": "old", "legacy.md": "keep"})
    sync_skill_to_targets(source, [target])
    assert (target / "SKILL.md").read_text() == "new"
    assert (target / "legacy.md").read_text() == "keep"
```

```python
def test_sync_rolls_back_previous_target_when_later_target_fails(tmp_path):
    source = make_skill_tree(tmp_path / "source", {"SKILL.md": "new"})
    first = make_skill_tree(tmp_path / "first", {"SKILL.md": "old"})
    failing_target = tmp_path / "failing-file"
    failing_target.write_text("not a directory")
    with self.assertRaises(SyncError):
        sync_skill_to_targets(source, [first, failing_target])
    assert (first / "SKILL.md").read_text() == "old"
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python -m unittest discover -s skills/superpowers-update/tests -v`
Expected: FAIL because copying and rollback are not implemented.

- [ ] **Step 3: Implement transactional synchronization**

Before copying, back up each affected target skill below the temporary run directory. Copy only files from the public skill tree, leave destination-only files untouched, and restore all backups if any copy or post-copy hash fails. Include the canonical `.shared-ai-memory\skills` root as the first target.

- [ ] **Step 4: Run all tests and a dry-run against the real source**

Run: `python -m unittest discover -s skills/superpowers-update/tests -v`
Expected: PASS.
Run: `python skills/superpowers-update/scripts/superpowers_update.py check`
Expected: JSON status with source SHA and changed-skill classification, no repository report file.

- [ ] **Step 5: Commit apply mode**

```powershell
git add skills/superpowers-update/scripts/superpowers_update.py skills/superpowers-update/tests/test_superpowers_update.py
git commit -m "feat: add transactional superpowers skill updates"
```

### Task 4: Skill instructions and registry integration

**Files:**
- Create: `skills/superpowers-update/SKILL.md`
- Modify: `skills/stout-skill-registry/registry.json`

**Interfaces:**
- `SKILL.md` invokes `python scripts/superpowers_update.py check|apply` from the skill directory.
- Registry entry uses name `superpowers-update`, role focused on public Superpowers synchronization, and triggers for update/sync/modified skills.

- [ ] **Step 1: Write the skill instructions**

Document trigger conditions, source-of-truth rule, `check` before `apply`, no-op behavior, preserved extras, temporary-report behavior, failure/rollback handling, and the fact that Git publication is outside the skill.

- [ ] **Step 2: Register the skill**

Add one registry entry with the exact canonical path `skills/superpowers-update`, without modifying existing entries or generated audit artifacts.

- [ ] **Step 3: Validate skill metadata and registry JSON**

Run: `python -m json.tool skills/stout-skill-registry/registry.json`
Run: `python skills/stout-skill-manager/scripts/install_validator.py --help`
Run: `python -c "from pathlib import Path; print(Path('skills/superpowers-update/SKILL.md').read_text(encoding='utf-8').splitlines()[:8])"`
Expected: valid JSON, validator help, and frontmatter containing `name: superpowers-update` plus a `Use when...` description.

- [ ] **Step 4: Commit skill and registry**

```powershell
git add skills/superpowers-update/SKILL.md skills/stout-skill-registry/registry.json
git commit -m "feat: add superpowers update skill"
```

### Task 5: Audit, quality gate, installation and final verification

**Files:**
- Verify: `skills/superpowers-update/SKILL.md`
- Verify: `skills/superpowers-update/scripts/superpowers_update.py`
- Verify: `skills/superpowers-update/tests/test_superpowers_update.py`

- [ ] **Step 1: Run the full stdlib test suite and checks**

Run:

```powershell
python -m unittest discover -s skills/superpowers-update/tests -v
python -m json.tool skills/stout-skill-registry/registry.json > $null
git diff --check
```

Expected: all tests pass, JSON parses, and no whitespace errors occur.

- [ ] **Step 2: Run the Stout quality audit**

Run: `python skills/audit-skill-sentinel/scripts/run_audit.py --skill superpowers-update`
Expected: score at least 70; if lower, revise the skill before installation.

- [ ] **Step 3: Validate and install through the manager**

Run `junction_guard.py`, validate the canonical skill, then copy only `skills/superpowers-update` into the physical `.agents\skills` and `.codex\skills` targets. Validate the installed copies; `.claude\skills` and `.commandcode\skills` must resolve to the canonical junction target and are not written directly.

- [ ] **Step 4: Run the installed skill's check mode**

Run: `python C:\Users\victor.bernardi\.agents\skills\superpowers-update\scripts\superpowers_update.py check`
Expected: it reads the public source, reports its SHA, and does not leave `report.json` or `audit_result.json` inside any skill directory.

- [ ] **Step 5: Review the final diff and prepare integration**

Verify only the design, plan, new skill, tests, script, and registry entry are staged; keep all pre-existing untracked files outside the commit. Then use the repository branch workflow to push, integrate into the remote `master`, and delete the work branch without publishing unrelated local commits.
