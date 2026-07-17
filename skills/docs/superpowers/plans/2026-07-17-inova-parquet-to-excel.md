# inova-parquet-to-excel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar e registrar uma skill que converte um `.parquet` válido em um `.xlsx` de aba única, resolvendo ou solicitando os caminhos de entrada e saída.

**Architecture:** A skill declarativa (`SKILL.md`) orienta a interação e chama um conversor Python (`scripts/convert.py`). O conversor concentra validação, leitura com pandas e gravação via `openpyxl`; testes unitários usam arquivos Parquet temporários e verificam que falhas não deixam saída parcial. `skill.config.json` descreve os três destinos de plataforma e o Ledger recebe uma entrada ativa após a validação.

**Tech Stack:** Python 3, pandas, pyarrow (leitura Parquet), openpyxl (escrita XLSX), pytest, JSON/YAML.

## Global Constraints

- Exportar todos os dados em uma única aba.
- Solicitar caminhos quando não forem inequívocos; sugerir a mesma pasta e o mesmo nome-base para um destino ausente.
- Recusar arquivos com mais de 1.048.576 linhas antes de criar a saída.
- Não sobrescrever um `.xlsx` existente sem confirmação explícita.
- Não apagar nem criar arquivo parcial em caso de erro.
- Manter a skill compatível com `claude-code`, `antigravity` e `commandcode`.

---

### Task 1: Implementar conversor validável

**Files:**
- Create: `inova-parquet-to-excel/scripts/convert.py`
- Create: `inova-parquet-to-excel/tests/test_convert.py`

**Interfaces:**
- Produces `convert(input_path: Path, output_path: Path, *, overwrite: bool = False) -> ConversionResult`.
- `ConversionResult` contém `input_path`, `output_path`, `rows`, `columns` e `sheet_name`.
- Erros de contrato usam `ConversionError` com mensagens acionáveis.

- [ ] **Step 1: Write the failing tests**

```python
def test_convert_writes_one_sheet(tmp_path):
    source = tmp_path / "dados.parquet"
    target = tmp_path / "dados.xlsx"
    pd.DataFrame({"codigo": [1, 2], "nome": ["A", "B"]}).to_parquet(source)
    result = convert(source, target)
    assert result.rows == 2 and result.columns == 2
    assert pd.read_excel(target, sheet_name="Dados").to_dict("records") == [
        {"codigo": 1, "nome": "A"}, {"codigo": 2, "nome": "B"}
    ]
    assert pd.ExcelFile(target).sheet_names == ["Dados"]

def test_convert_rejects_invalid_extension_and_missing_source(tmp_path):
    with pytest.raises(ConversionError, match="\.parquet"):
        convert(tmp_path / "dados.csv", tmp_path / "dados.xlsx")
    with pytest.raises(ConversionError, match="não existe"):
        convert(tmp_path / "ausente.parquet", tmp_path / "dados.xlsx")

def test_convert_rejects_existing_output_without_overwrite(tmp_path):
    source = tmp_path / "dados.parquet"; target = tmp_path / "dados.xlsx"
    pd.DataFrame({"a": [1]}).to_parquet(source); target.write_bytes(b"original")
    with pytest.raises(ConversionError, match="já existe"):
        convert(source, target)
    assert target.read_bytes() == b"original"

def test_convert_rejects_excel_row_limit_before_write(tmp_path, monkeypatch):
    source = tmp_path / "dados.parquet"; target = tmp_path / "dados.xlsx"
    monkeypatch.setattr("convert.EXCEL_MAX_ROWS", 1)
    pd.DataFrame({"a": [1, 2]}).to_parquet(source)
    with pytest.raises(ConversionError, match="1.048.576|limite"):
        convert(source, target)
    assert not target.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest inova-parquet-to-excel/tests/test_convert.py -v`
Expected: FAIL because `convert.py` and its public interfaces do not exist.

- [ ] **Step 3: Implement the minimal converter**

Implement `ConversionError`, `ConversionResult`, and `convert` with `Path` checks, `pd.read_parquet`, `len(frame)`, `frame.to_excel(output_path, sheet_name="Dados", index=False, engine="openpyxl")`, and cleanup of a newly-created target when the write raises. Use `EXCEL_MAX_ROWS = 1_048_576` and reject `output_path == input_path`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest inova-parquet-to-excel/tests/test_convert.py -v`
Expected: all conversion tests PASS.

- [ ] **Step 5: Commit**

```bash
git add inova-parquet-to-excel/scripts/convert.py inova-parquet-to-excel/tests/test_convert.py
git commit -m "feat: add parquet to excel converter"
```

### Task 2: Criar a definição declarativa da skill

**Files:**
- Create: `inova-parquet-to-excel/SKILL.md`
- Create: `inova-parquet-to-excel/skill.config.json`

**Interfaces:**
- `SKILL.md` chama `python scripts/convert.py --input <parquet> --output <xlsx>` após resolver os caminhos.
- `skill.config.json` usa `SKILL.md` como `body.source` e habilita as três plataformas ativas.

- [ ] **Step 1: Write the metadata validation test**

```python
def test_skill_metadata_is_valid():
    text = Path("inova-parquet-to-excel/SKILL.md").read_text(encoding="utf-8")
    assert "name: inova-parquet-to-excel" in text
    assert "parquet" in text.lower() and "xlsx" in text.lower()
    config = json.loads(Path("inova-parquet-to-excel/skill.config.json").read_text())
    assert config["body"]["source"] == "SKILL.md"
    assert all(config["platforms"][p]["enabled"] for p in ("claude-code", "antigravity", "commandcode"))
```

- [ ] **Step 2: Run the metadata test to verify it fails**

Run: `pytest inova-parquet-to-excel/tests/test_metadata.py -v`
Expected: FAIL because the skill files are absent.

- [ ] **Step 3: Write `SKILL.md` and `skill.config.json`**

Document triggers (`converter parquet para excel`, `parquet xlsx`, `inova-parquet-to-excel`), path detection/clarification, default destination proposal, one-sheet behavior, overwrite confirmation, row-limit rule, command invocation, and final summary. Mirror the existing platform outputs in `inova-motor-orcamentos/skill.config.json`.

- [ ] **Step 4: Run metadata and structure validation**

Run: `pytest inova-parquet-to-excel/tests/test_metadata.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add inova-parquet-to-excel/SKILL.md inova-parquet-to-excel/skill.config.json inova-parquet-to-excel/tests/test_metadata.py
git commit -m "feat: define parquet to excel skill"
```

### Task 3: Integrar auditoria, Ledger e renderização

**Files:**
- Modify: `stout-skill-registry/registry.json`
- Create: `inova-parquet-to-excel/audit_result.json` (copy the approved auditor result)

**Interfaces:**
- Registry entry uses role `Converte Parquet em Excel de aba única com resolução de caminhos` and triggers matching the skill metadata.

- [ ] **Step 1: Validate the approved audit artifact**

Run: `python stout-create-skill/scripts/create_pipeline.py --check-audit`
Expected: the artifact verdict is `APPROVED`.

- [ ] **Step 2: Add the active Ledger entry**

Append an entry with `name`, canonical path, tier 1, category `utility`, version `1.0.0`, status `active`, role, triggers, and author `Victor`; preserve valid JSON and do not modify deprecated entries.

- [ ] **Step 3: Run registry and platform validators**

Run: `python stout-create-skill/scripts/skill_validator.py inova-parquet-to-excel` and the relevant platform renderer tests.
Expected: valid frontmatter, valid config, and compatible outputs for all three platforms.

- [ ] **Step 4: Commit**

```bash
git add stout-skill-registry/registry.json inova-parquet-to-excel/audit_result.json
git commit -m "chore: register parquet to excel skill"
```

### Task 4: End-to-end verification

**Files:**
- Modify: `inova-parquet-to-excel/tests/test_convert.py` only if a discovered defect requires a focused regression test.

**Interfaces:**
- The CLI documented by `SKILL.md` returns a success summary containing output path, row count, column count, and sheet name.

- [ ] **Step 1: Run the complete focused suite**

Run: `pytest inova-parquet-to-excel/tests -v`
Expected: all tests PASS.

- [ ] **Step 2: Run whitespace and JSON checks**

Run: `git diff --check` and `python -m json.tool inova-parquet-to-excel/skill.config.json`.
Expected: no whitespace errors and valid JSON.

- [ ] **Step 3: Exercise the real CLI with a temporary Parquet**

Run a temporary fixture through `python inova-parquet-to-excel/scripts/convert.py --input <fixture.parquet> --output <fixture.xlsx>` and inspect with pandas that the output has exactly one sheet named `Dados` and the expected row count.

- [ ] **Step 4: Commit any regression test fix**

```bash
git add inova-parquet-to-excel/tests
git commit -m "test: verify parquet to excel output"
```

