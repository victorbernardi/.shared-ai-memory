# Audit NF Parquet — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** For each email execution, save one folder of parquet files at NF level — one file per data source/period combination — so every indicator in the email can be fully reconstructed and audited.

**Architecture:** A new `src/audit_nf.py` module exposes a single public function `salvar_audit_nf()` that re-uses the already-cached M2 data (`fat.*`) and re-queries vw_VENDAS to produce six parquet files plus a manifest JSON per run. `run_daily.py` calls it after successful email generation. Storage goes to `data/audit_nf/<run_id>/` where `run_id` matches the output email filename stem.

**Tech Stack:** pandas, pathlib, json, pytest (monkeypatch), existing `src/faturamento.py` (in-memory cache), existing `src/db_utils.executar_query`.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `src/audit_nf.py` | Create | Saves NF-level parquets + manifest per execution |
| `src/config.py` | Modify (1 line) | Add `AUDIT_NF_DIR` constant |
| `run_daily.py` | Modify | Call `salvar_audit_nf()` after successful email |
| `tests/test_audit_nf.py` | Create | Unit tests for all save functions |

Parquet files created per execution (under `data/audit_nf/<run_id>/`):

| File | Source | Covers |
|------|--------|--------|
| `nf_dia_YYYYMMDD.parquet` | M2 (fat.por_dia) | total_dia, nfs, top_filiais_dia |
| `nf_mes_YYYYMM.parquet` | M2 (fat.por_mes) | acumulado_mes, tendencia base |
| `nf_sply_YYYYMM_d{DD}.parquet` | M2 (fat.por_periodo, ano-1) | sply_total |
| `nf_splm_YYYYMM_d{DD}.parquet` | M2 (fat.por_periodo, mes-1) | splm_total |
| `nf_vw_dia_YYYYMMDD.parquet` | vw_VENDAS | top_vendedores |
| `nf_recap_ant_YYYYMM.parquet` | M2 (fat.por_mes, ano-1) | recap total_ano_ant (only with --mes) |
| `manifest.json` | Generated | Maps each file → indicators it covers |

---

## Task 1: Add AUDIT_NF_DIR to config and create audit_nf.py

**Files:**

- Modify: `src/config.py:10` (add constant after `OUTPUT_DIR`)
- Create: `src/audit_nf.py`
- Create: `tests/test_audit_nf.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_audit_nf.py
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

# ---------- fixtures ----------

DF_DIA = pd.DataFrame({
    "DATA_EMISSAO_NF": pd.to_datetime(["2026-05-14", "2026-05-14"]),
    "NUMERO_DA_NF": ["NF001", "NF002"],
    "FILIAL": ["201", "202"],
    "VALOR_DO_PRODUTO": [500_000.0, 125_141.0],
    "CODIGO_TES": ["501", "504"],
    "NOME_DO_CLIENTE": ["Fazenda A", "Fazenda B"],
    "CPF_CNPJ_DO_CLIENTE": ["111", "222"],
    "DESCRICAO_DO_PRODUTO": ["FILTRO", "OLEO"],
})

DF_MES = pd.DataFrame({
    "DATA_EMISSAO_NF": pd.to_datetime(["2026-05-01", "2026-05-14"]),
    "NUMERO_DA_NF": ["NF000", "NF001"],
    "FILIAL": ["201", "201"],
    "VALOR_DO_PRODUTO": [300_000.0, 500_000.0],
    "CODIGO_TES": ["501", "501"],
    "NOME_DO_CLIENTE": ["Fazenda A", "Fazenda A"],
    "CPF_CNPJ_DO_CLIENTE": ["111", "111"],
    "DESCRICAO_DO_PRODUTO": ["FILTRO", "FILTRO"],
})

DF_VW = pd.DataFrame({
    "NF": ["NF001", "NF002"],
    "NOME_VENDEDOR": ["Joao", "Maria"],
    "FILIAL_NOME": ["Contagem", "Tangua"],
    "RECEITA": [500_000.0, 125_141.0],
})


@pytest.fixture()
def mock_fat(monkeypatch):
    import src.audit_nf as anf
    monkeypatch.setattr("src.audit_nf.fat.por_dia", lambda d: DF_DIA.copy())
    monkeypatch.setattr("src.audit_nf.fat.por_mes", lambda ano, mes: DF_MES.copy())
    monkeypatch.setattr(
        "src.audit_nf.fat.por_periodo",
        lambda ano, mes, ate_dia: DF_MES.copy(),
    )
    monkeypatch.setattr(
        "src.audit_nf.executar_query",
        lambda q, label: DF_VW.copy(),
    )


# ---------- tests ----------

def test_salvar_cria_pasta_run(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    paths = salvar_audit_nf(
        data_ontem=date(2026, 5, 14),
        mes=None,
        run_id="DAILY_ROBERTO_20260515_1823",
        audit_dir=tmp_path,
    )
    pastas = list(tmp_path.iterdir())
    assert len(pastas) == 1
    assert pastas[0].name == "DAILY_ROBERTO_20260515_1823"


def test_salvar_cria_nf_dia(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    pasta = tmp_path / "RUN01"
    assert (pasta / "nf_dia_20260514.parquet").exists()


def test_nf_dia_contem_colunas_obrigatorias(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    df = pd.read_parquet(tmp_path / "RUN01" / "nf_dia_20260514.parquet")
    for col in ["DATA_EMISSAO_NF", "NUMERO_DA_NF", "FILIAL", "VALOR_DO_PRODUTO",
                "CODIGO_TES", "NOME_DO_CLIENTE", "CPF_CNPJ_DO_CLIENTE", "DESCRICAO_DO_PRODUTO"]:
        assert col in df.columns, f"Coluna ausente: {col}"


def test_salvar_cria_nf_mes(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    assert (tmp_path / "RUN01" / "nf_mes_202605.parquet").exists()


def test_salvar_cria_sply(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    assert (tmp_path / "RUN01" / "nf_sply_202505_d14.parquet").exists()


def test_salvar_cria_splm(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    assert (tmp_path / "RUN01" / "nf_splm_202604_d14.parquet").exists()


def test_splm_janeiro_usa_dezembro_ano_anterior(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 1, 10), mes=None, run_id="RUN01", audit_dir=tmp_path)
    assert (tmp_path / "RUN01" / "nf_splm_202512_d10.parquet").exists()


def test_salvar_cria_nf_vw(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    assert (tmp_path / "RUN01" / "nf_vw_dia_20260514.parquet").exists()


def test_sem_recap_nao_cria_recap_ant(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    pasta = tmp_path / "RUN01"
    recap_files = list(pasta.glob("nf_recap_ant_*.parquet"))
    assert recap_files == []


def test_com_mes_cria_recap_ant(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=1, run_id="RUN01", audit_dir=tmp_path)
    assert (tmp_path / "RUN01" / "nf_recap_ant_202501.parquet").exists()


def test_manifest_criado(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    manifest_path = tmp_path / "RUN01" / "manifest.json"
    assert manifest_path.exists()


def test_manifest_json_valido(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    data = json.loads((tmp_path / "RUN01" / "manifest.json").read_text(encoding="utf-8"))
    assert "run_id" in data
    assert "data_ontem" in data
    assert "arquivos" in data
    assert isinstance(data["arquivos"], list)
    assert len(data["arquivos"]) >= 5


def test_manifest_cada_arquivo_tem_indicadores(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    data = json.loads((tmp_path / "RUN01" / "manifest.json").read_text(encoding="utf-8"))
    for entry in data["arquivos"]:
        assert "arquivo" in entry
        assert "indicadores" in entry
        assert isinstance(entry["indicadores"], list)
        assert len(entry["indicadores"]) >= 1


def test_retorna_lista_de_paths(tmp_path, mock_fat):
    from src.audit_nf import salvar_audit_nf
    result = salvar_audit_nf(date(2026, 5, 14), mes=None, run_id="RUN01", audit_dir=tmp_path)
    assert isinstance(result, list)
    assert all(isinstance(p, Path) for p in result)
    assert len(result) >= 5
```

- [ ] **Step 2: Run tests to verify they fail**

```
cd C:\Projetos\Inova
pytest projects/Inova-Daily/tests/test_audit_nf.py -v 2>&1 | head -30
```

Expected: `ImportError: cannot import name 'salvar_audit_nf' from 'src.audit_nf'` (or ModuleNotFoundError)

- [ ] **Step 3: Add AUDIT_NF_DIR to config.py**

In `src/config.py`, add after the `OUTPUT_DIR` line (line 10):

```python
AUDIT_NF_DIR = PROJECT_ROOT / "data" / "audit_nf"
```

- [ ] **Step 4: Create src/audit_nf.py**

```python
# src/audit_nf.py
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from src import faturamento as fat
from src.config import AUDIT_NF_DIR, TES_ALL_VALID
from src.db_utils import executar_query


def salvar_audit_nf(
    data_ontem: date,
    mes: Optional[int],
    run_id: str,
    audit_dir: Optional[Path] = None,
) -> list[Path]:
    """Salva parquets NF-nível para auditoria de uma execução do Inova Daily.

    Retorna lista dos arquivos criados (incluindo manifest.json).
    """
    base = (audit_dir if audit_dir is not None else AUDIT_NF_DIR) / run_id
    base.mkdir(parents=True, exist_ok=True)

    ano = data_ontem.year
    mes_ref = data_ontem.month
    dia = data_ontem.day
    mes_ant = mes_ref - 1 if mes_ref > 1 else 12
    ano_mes_ant = ano if mes_ref > 1 else ano - 1

    saved: list[Path] = []
    manifesto: list[dict] = []

    def _salvar(nome: str, df: pd.DataFrame, indicadores: list[str]) -> Path:
        p = base / nome
        df.to_parquet(p, index=False)
        manifesto.append({"arquivo": nome, "indicadores": indicadores})
        return p

    # 1 — NFs do dia (M2)
    df_dia = fat.por_dia(data_ontem)
    saved.append(_salvar(
        f"nf_dia_{data_ontem.strftime('%Y%m%d')}.parquet",
        df_dia,
        ["total_dia", "nfs", "top_filiais_dia"],
    ))

    # 2 — NFs do mês corrente até hoje (M2) — acumulado
    df_mes = fat.por_mes(ano, mes_ref)
    saved.append(_salvar(
        f"nf_mes_{ano}{mes_ref:02d}.parquet",
        df_mes,
        ["acumulado_mes", "pct_meta", "tendencia_base"],
    ))

    # 3 — SPLY: mesmo período ano anterior
    df_sply = fat.por_periodo(ano - 1, mes_ref, dia)
    saved.append(_salvar(
        f"nf_sply_{ano - 1}{mes_ref:02d}_d{dia:02d}.parquet",
        df_sply,
        ["sply_total", "sply_pct"],
    ))

    # 4 — SPLM: mesmo período mês anterior
    df_splm = fat.por_periodo(ano_mes_ant, mes_ant, dia)
    saved.append(_salvar(
        f"nf_splm_{ano_mes_ant}{mes_ant:02d}_d{dia:02d}.parquet",
        df_splm,
        ["splm_total", "splm_pct"],
    ))

    # 5 — vw_VENDAS do dia (para top_vendedores)
    tes_sql = "(" + ",".join([f"'{t}'" for t in TES_ALL_VALID]) + ")"
    df_vw = executar_query(
        f"""
        SELECT
            NUMERO_DA_NF as NF,
            NOME_VENDEDOR,
            NOME_DA_FILIAL as FILIAL_NOME,
            VALOR_DO_PRODUTO as RECEITA
        FROM [dbo].[vw_VENDAS]
        WHERE CAST(DATA_EMISSAO_NF AS DATE) = '{data_ontem}'
          AND CAST(CODIGO_TES AS VARCHAR) IN {tes_sql}
        """,
        "Audit NF vw_VENDAS",
    )
    saved.append(_salvar(
        f"nf_vw_dia_{data_ontem.strftime('%Y%m%d')}.parquet",
        df_vw,
        ["top_vendedores"],
    ))

    # 6 — Recap ano anterior (apenas quando --mes é passado)
    if mes is not None:
        df_recap_ant = fat.por_mes(ano - 1, mes)
        saved.append(_salvar(
            f"nf_recap_ant_{ano - 1}{mes:02d}.parquet",
            df_recap_ant,
            ["recap_total_ano_ant", "recap_yoy_pct"],
        ))

    # Manifest
    manifest_data = {
        "run_id": run_id,
        "data_ontem": data_ontem.isoformat(),
        "mes_recap": mes,
        "arquivos": manifesto,
    }
    manifest_path = base / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest_data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    saved.append(manifest_path)

    return saved
```

- [ ] **Step 5: Run tests to verify they pass**

```
cd C:\Projetos\Inova
pytest projects/Inova-Daily/tests/test_audit_nf.py -v
```

Expected: all 15 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add projects/Inova-Daily/src/audit_nf.py \
        projects/Inova-Daily/src/config.py \
        projects/Inova-Daily/tests/test_audit_nf.py
git commit -m "feat(inova-daily): audit NF parquet — src/audit_nf.py + AUDIT_NF_DIR"
```

---

## Task 2: Wire audit_nf into run_daily.py

**Files:**

- Modify: `run_daily.py:105-121` (after `output_path = gerar_email(...)`)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_run_daily_audit.py
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


def _make_snap():
    return {
        "data_ontem": date(2026, 5, 14),
        "total": 625_000.0,
        "nfs": 128,
        "top_vendedores": {"Joao": 400_000.0},
        "top_filiais": {"Contagem": 513_000.0},
        "acumulado_mes": 5_000_000.0,
        "meta_mes": 13_646_411.88,
        "pct_meta": 36.6,
        "dias_restantes": 12,
        "sply_pct": 12.5,
        "sply_total": 4_400_000.0,
        "sply_mes": 5,
        "sply_ano": 2025,
        "splm_pct": -5.0,
        "splm_total": 5_300_000.0,
        "splm_mes": 4,
        "splm_ano": 2026,
        "tendencia": "Crescendo ↑",
        "delta_tendencia": 8.0,
    }


@pytest.fixture()
def mock_run_env(tmp_path, monkeypatch):
    """Patches everything run_daily.main() touches."""
    # Prevent M2 check
    monkeypatch.setattr("run_daily._m2_atualizado", lambda: True)

    snap = _make_snap()

    monkeypatch.setattr("src.snapshot_diario.foto_ontem", lambda **kw: snap)
    monkeypatch.setattr("src.auditor.validar_snapshot", lambda s: MagicMock(passed=True, issues=[]))
    monkeypatch.setattr("src.auditor.registrar_execucao", lambda *a, **kw: tmp_path / "audit.jsonl")
    monkeypatch.setattr("src.auditor.validar_markdown", lambda p: MagicMock(passed=True, issues=[]))

    fake_output = tmp_path / "DAILY_ROBERTO_20260515_1823.md"
    fake_output.write_text("## Foto de Ontem\nFaturamento R$ 625k", encoding="utf-8")
    monkeypatch.setattr("src.generator.gerar_email", lambda **kw: fake_output)

    audit_calls = []
    def _fake_salvar(data_ontem, mes, run_id, audit_dir=None):
        audit_calls.append({"data_ontem": data_ontem, "mes": mes, "run_id": run_id})
        return [tmp_path / "dummy.parquet"]

    monkeypatch.setattr("src.audit_nf.salvar_audit_nf", _fake_salvar)
    return audit_calls, tmp_path


def test_run_daily_chama_salvar_audit_nf(mock_run_env, monkeypatch):
    audit_calls, tmp_path = mock_run_env
    import importlib, run_daily
    importlib.reload(run_daily)

    monkeypatch.setattr(sys, "argv", ["run_daily.py", "--skip-m2-check"])
    try:
        run_daily.main()
    except SystemExit:
        pass

    assert len(audit_calls) == 1


def test_run_daily_passa_run_id_correto(mock_run_env, monkeypatch):
    audit_calls, tmp_path = mock_run_env
    import importlib, run_daily
    importlib.reload(run_daily)

    monkeypatch.setattr(sys, "argv", ["run_daily.py", "--skip-m2-check"])
    try:
        run_daily.main()
    except SystemExit:
        pass

    assert audit_calls[0]["run_id"] == "DAILY_ROBERTO_20260515_1823"


def test_run_daily_passa_mes_quando_flag_usada(mock_run_env, monkeypatch):
    audit_calls, tmp_path = mock_run_env
    import importlib, run_daily
    importlib.reload(run_daily)

    monkeypatch.setattr(sys, "argv", ["run_daily.py", "--skip-m2-check", "--mes", "1"])

    from unittest.mock import MagicMock
    monkeypatch.setattr("src.recap_mensal.highlight_mes", lambda m, ano=2026: {
        "mes": m, "ano": ano, "total": 19_000_000.0, "meta": 13_000_000.0,
        "pct_meta": 108.0, "yoy_pct": 11.9, "total_ano_ant": 17_000_000.0,
        "melhor_dia": None, "melhor_dia_valor": 0.0,
        "top_filiais": [("Contagem", 8_000_000.0)],
        "cliente_destaque": ("Fazenda X", 1_000_000.0),
        "anomalia": None,
    })
    monkeypatch.setattr("src.auditor.validar_recap", lambda r: MagicMock(passed=True, issues=[]))

    try:
        run_daily.main()
    except SystemExit:
        pass

    assert audit_calls[0]["mes"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

```
cd C:\Projetos\Inova
pytest projects/Inova-Daily/tests/test_run_daily_audit.py -v 2>&1 | head -20
```

Expected: FAIL — `salvar_audit_nf` not called from `run_daily.main()`.

- [ ] **Step 3: Modify run_daily.py**

In `run_daily.py`, after the block starting at line 64 (`from src.generator import gerar_email`), add one more import:

```python
    from src.audit_nf import salvar_audit_nf
```

Then, after the successful email check block (after line 117, inside the `if not md_result.passed ... sys.exit(1)` block exits), add before the final `print` statements:

```python
    # Salvar audit NF: prova quais NFs compuseram cada indicador
    run_id = output_path.stem  # e.g. DAILY_ROBERTO_20260515_1823
    audit_nf_paths = salvar_audit_nf(
        data_ontem=snap["data_ontem"],
        mes=args.mes,
        run_id=run_id,
    )
    print(f"Audit NF:      {audit_nf_paths[0].parent}  ({len(audit_nf_paths)} arquivo(s))")
```

The full modified block at the bottom of `main()` (lines 105–122) becomes:

```python
    output_path = gerar_email(mes=args.mes)

    # Checagem final: valida o Markdown gerado antes de liberar
    md_result = validar_markdown(output_path)
    if not md_result.passed:
        print("\n[AUDITORIA] ALERTAS no arquivo gerado:")
        for issue in md_result.issues:
            print(f"  - {issue.field}: {issue.message}")
        if not args.force:
            print("[AUDITORIA] E-mail BLOQUEADO — arquivo com problemas. Use --force para ignorar.")
            print(f"Arquivo:   {output_path}")
            print(f"Audit log: {log_path}")
            sys.exit(1)

    # Salvar audit NF: prova quais NFs compuseram cada indicador
    run_id = output_path.stem  # e.g. DAILY_ROBERTO_20260515_1823
    audit_nf_paths = salvar_audit_nf(
        data_ontem=snap["data_ontem"],
        mes=args.mes,
        run_id=run_id,
    )
    print(f"Audit NF:      {audit_nf_paths[0].parent}  ({len(audit_nf_paths)} arquivo(s))")

    print(f"\nE-mail gerado: {output_path}")
    print(f"Audit log:     {log_path}")
    print("Abra o arquivo, copie o conteudo e envie para Roberto.")
```

- [ ] **Step 4: Run tests to verify they pass**

```
cd C:\Projetos\Inova
pytest projects/Inova-Daily/tests/test_run_daily_audit.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 5: Run the full test suite**

```
cd C:\Projetos\Inova
pytest projects/Inova-Daily/tests/ -v --tb=short
```

Expected: all tests PASS (54 existing + 15 audit_nf + 3 run_daily_audit = 72 total).

- [ ] **Step 6: Commit**

```bash
git add projects/Inova-Daily/run_daily.py \
        projects/Inova-Daily/tests/test_run_daily_audit.py
git commit -m "feat(inova-daily): integrar salvar_audit_nf no run_daily.py"
```

---

## Task 3: Smoke test with real data

**Files:** none (runtime verification only)

- [ ] **Step 1: Run with real M2 cache**

```
cd C:\Projetos\Inova\projects\Inova-Daily
python run_daily.py --skip-m2-check --mes 1
```

Expected output includes a line like:

```
Audit NF:      data\audit_nf\DAILY_ROBERTO_20260515_HHMM  (7 arquivo(s))
```

- [ ] **Step 2: Verify parquet files exist and have rows**

```python
# Run in Python REPL or paste into a scratch script
from pathlib import Path
import pandas as pd

pasta = sorted(Path("data/audit_nf").iterdir())[-1]
print(f"Pasta: {pasta}")
for f in sorted(pasta.iterdir()):
    if f.suffix == ".parquet":
        df = pd.read_parquet(f)
        print(f"  {f.name}: {len(df)} linhas, R$ {df.get('VALOR_DO_PRODUTO', df.get('RECEITA', pd.Series([0]))).sum():,.0f}")
    else:
        print(f"  {f.name}")
```

Expected: each parquet has > 0 rows; NFs visible; totals match the email values.

- [ ] **Step 3: Commit**

```bash
git add -u
git commit -m "test(inova-daily): smoke test audit NF parquet — validado com dados reais"
```

---

## Self-Review Checklist

**Spec coverage:**

- [x] NF-level granularity: each parquet is at transaction/NF level, never aggregated
- [x] All indicator sources covered: dia, mês, sply, splm, vw_VENDAS, recap_ant
- [x] Reuse where possible: `nf_mes` covers acumulado_mes + recap base (same query)
- [x] `data/audit_nf/` storage path
- [x] Rigid audit: filename includes run_id matching email stem — one folder per execution
- [x] Manifest links each file to indicators it covers
- [x] January SPLM edge case: `mes_ant=12, ano_mes_ant=ano-1` handled

**Placeholder scan:** No TBD or vague steps found.

**Type consistency:** `salvar_audit_nf` signature used identically in Task 1 (implementation) and Task 2 (test mock). `audit_dir` parameter added for testability — defaults to `AUDIT_NF_DIR` from config.
