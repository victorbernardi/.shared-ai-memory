# Horímetro Staleness — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use stout-executing-plans to implement this plan task-by-task.

**Goal:** Detectar máquinas com horímetro desatualizado (>120 dias) via `AOR Last Location Date`, validar estatisticamente o impacto, e reclassificar de `STATUS_USO = "REAL"` para `"ESTIMADO"` no pipeline M3.

**Architecture:** Fase 1 — script sandbox read-only que une POPS + parquet existente e roda 3 análises estatísticas; Fase 2 (bloqueada por gate humano) — expansão de `_preparar_pops` + `_imputar_horimetro` com threshold configurável em `shared/config.py`.

**Tech Stack:** Python 3.x, pandas, numpy, scipy.stats, pytest

**Spec:** `docs/specs/2026-05-29-spec-horimetro-staleness.md`

---

## FASE 1 — Sandbox de Validação Estatística

### Task 1: Criar estrutura sandbox e skeleton do script

**Files:**

- Create: `data/sandbox/.gitkeep`
- Create: `sandbox_horimetro_staleness.py`

**Step 1: Verificar se `AOR Last Location Date` existe no POPS**

```python
import pandas as pd
pops = pd.read_excel(r"C:\Projetos\Inova\shared\data\Product_details_full.xlsx", nrows=3)
print([c for c in pops.columns if "AOR" in c or "Location" in c or "Date" in c])
```

Run: `$env:PYTHONIOENCODING="utf-8"; python -c "<código acima>"`
Expected: lista contendo `"AOR Last Location Date"`. Se ausente, identificar o nome correto e ajustar o plano.

**Step 2: Criar `data/sandbox/` e `sandbox_horimetro_staleness.py`**

```python
#!/usr/bin/env python
# coding: utf-8
"""
Sandbox: Validação estatística do horímetro defasado.
READ-ONLY — não modifica nenhum parquet.
Spec: docs/specs/2026-05-29-spec-horimetro-staleness.md
"""
from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
import numpy as np
from scipy import stats

_shared_dir = Path(__file__).parents[3] / "shared"
if str(_shared_dir) not in sys.path:
    sys.path.insert(0, str(_shared_dir))

from config import SHARED_DATA

STAGE_DIR    = Path(__file__).parent
SANDBOX_OUT  = STAGE_DIR / "data" / "sandbox"
SANDBOX_OUT.mkdir(parents=True, exist_ok=True)

STALE_THRESHOLD_DAYS = 120
HOJE = pd.Timestamp.now().normalize()

POPS_PATH   = SHARED_DATA / "Product_details_full.xlsx"
CHASSI_PATH = SHARED_DATA / "dataset_ouro_potencial_chassi_v1.parquet"


def carregar_dados() -> pd.DataFrame:
    pops = pd.read_excel(POPS_PATH, usecols=["Serial Number", "AOR Last Location Date"])
    pops["Serial Number"] = pops["Serial Number"].astype(str).str.strip().str.upper()
    pops["AOR_Date"] = pd.to_datetime(pops["AOR Last Location Date"], errors="coerce")
    pops["Dias_Desde_Horimetro"] = (HOJE - pops["AOR_Date"]).dt.days.fillna(999).astype(int)

    chassi = pd.read_parquet(CHASSI_PATH)
    chassi["PIN"] = chassi["PIN"].astype(str).str.strip().str.upper()

    df = chassi.merge(pops, left_on="PIN", right_on="Serial Number", how="left")
    df["Dias_Desde_Horimetro"] = df["Dias_Desde_Horimetro"].fillna(999).astype(int)
    return df


if __name__ == "__main__":
    print("Carregando dados...")
    df = carregar_dados()
    n_real = (df["STATUS_USO"] == "REAL").sum()
    n_est  = (df["STATUS_USO"] == "ESTIMADO").sum()
    print(f"Dataset: {len(df)} registros | REAL: {n_real} | ESTIMADO: {n_est}")
    print("Skeleton OK.")
```

**Step 3: Rodar skeleton**

Run: `cd "C:\Projetos\Inova\pipelines\potencial-clientes\03_Potencial"; $env:PYTHONIOENCODING="utf-8"; python sandbox_horimetro_staleness.py`
Expected: linha com contagem de registros sem erro.

---

### Task 2: Análise A — Distribuição dos horímetros REAL

**Files:**

- Modify: `sandbox_horimetro_staleness.py`

**Step 1: Adicionar função `analise_distribuicao` antes do `if __name__ == "__main__":`**

```python
def analise_distribuicao(df: pd.DataFrame) -> None:
    real = df[df["STATUS_USO"] == "REAL"]["Horimetro_Final"].dropna()

    q1, q3 = real.quantile(0.25), real.quantile(0.75)
    iqr = q3 - q1
    fence_low  = q1 - 1.5 * iqr
    fence_high = q3 + 1.5 * iqr
    outliers = real[(real < fence_low) | (real > fence_high)]

    print("\n=== ANÁLISE A: Distribuição Horímetros REAL ===")
    print(f"N          : {len(real)}")
    print(f"Média      : {real.mean():.1f} h/ano")
    print(f"Mediana    : {real.median():.1f} h/ano")
    print(f"Desvio Pad : {real.std():.1f}")
    skew_val = real.skew()
    print(f"Skewness   : {skew_val:.2f}  ({'ATENÇÃO: assimétrico' if abs(skew_val) > 1 else 'OK'})")
    print(f"Q1/Q3      : {q1:.1f} / {q3:.1f}")
    print(f"Fences     : {fence_low:.1f} / {fence_high:.1f}")
    print(f"Outliers   : {len(outliers)} ({len(outliers)/max(len(real),1)*100:.1f}%)")

    grp = (
        df[df["STATUS_USO"] == "REAL"]
        .groupby("Model Grupo")["Horimetro_Final"]
        .agg(n="count", mediana="median", media="mean", std="std",
             skew=lambda x: x.skew())
        .reset_index()
        .sort_values("n", ascending=False)
    )
    grp.to_csv(SANDBOX_OUT / "analise_a_distribuicao.csv", index=False)
    print(f"\nTop 5 por volume:\n{grp.head(5).to_string(index=False)}")
    print(f"CSV: {SANDBOX_OUT / 'analise_a_distribuicao.csv'}")
```

**Step 2: Chamar no `__main__`**

```python
    analise_distribuicao(df)
```

**Step 3: Rodar e verificar**

Run: `$env:PYTHONIOENCODING="utf-8"; python sandbox_horimetro_staleness.py`
Expected: N, média, mediana, skewness exibidos. CSV criado em `data/sandbox/analise_a_distribuicao.csv`.

---

### Task 3: Análise B — Impacto do Corte de 120 Dias

**Files:**

- Modify: `sandbox_horimetro_staleness.py`

**Step 1: Adicionar função `analise_impacto_corte`**

```python
def analise_impacto_corte(df: pd.DataFrame) -> None:
    real = df[df["STATUS_USO"] == "REAL"].copy()

    real["BUCKET"] = np.where(
        real["AOR_Date"].isna(), "NULA",
        np.where(real["Dias_Desde_Horimetro"] <= STALE_THRESHOLD_DAYS, "RECENTE", "DEFASADA")
    )

    mediana_modelo = (
        real[real["BUCKET"] == "RECENTE"]
        .groupby("Model Grupo")["Horimetro_Final"]
        .median().to_dict()
    )
    mediana_global = real[real["BUCKET"] == "RECENTE"]["Horimetro_Final"].median()

    real["Mediana_Modelo"] = real["Model Grupo"].map(mediana_modelo).fillna(mediana_global)
    real["Potencial_com_Mediana"] = (
        real["Potencial Total"]
        * (real["Mediana_Modelo"] / real["Horimetro_Final"].replace(0, np.nan))
    ).fillna(real["Potencial Total"])
    real["Delta_R$"] = real["Potencial_com_Mediana"] - real["Potencial Total"]

    resumo = real.groupby("BUCKET").agg(
        Qtd=("PIN", "count"),
        Horimetro_Medio=("Horimetro_Final", "mean"),
        Potencial_Atual_R$=("Potencial Total", "sum"),
        Potencial_Mediana_R$=("Potencial_com_Mediana", "sum"),
        Delta_Total_R$=("Delta_R$", "sum"),
    ).reset_index()
    resumo["Pct_Volume"] = (resumo["Qtd"] / resumo["Qtd"].sum() * 100).round(1)

    print("\n=== ANÁLISE B: Impacto do Corte de 120 Dias ===")
    print(resumo.to_string(index=False))
    reclassificadas = resumo[resumo["BUCKET"].isin(["DEFASADA", "NULA"])]["Qtd"].sum()
    print(f"\nTotal a reclassificar: {reclassificadas} máquinas")

    real.to_csv(SANDBOX_OUT / "analise_b_impacto_corte.csv", index=False)
    print(f"CSV: {SANDBOX_OUT / 'analise_b_impacto_corte.csv'}")
```

**Step 2: Chamar no `__main__`**

```python
    analise_impacto_corte(df)
```

**Step 3: Rodar e verificar**

Run: `$env:PYTHONIOENCODING="utf-8"; python sandbox_horimetro_staleness.py`
Expected: tabela com 3 buckets (RECENTE, DEFASADA, NULA) com volume e delta R$. CSV em `data/sandbox/analise_b_impacto_corte.csv`.

---

### Task 4: Análise C — Validação Cruzada

**Files:**

- Modify: `sandbox_horimetro_staleness.py`

**Step 1: Adicionar função `analise_validacao_cruzada`**

```python
def analise_validacao_cruzada(df: pd.DataFrame) -> None:
    df = df.copy()
    df["POPULACAO"] = np.where(
        df["STATUS_USO"] == "ESTIMADO", "ESTIMADO",
        np.where(
            df["AOR_Date"].isna(), "DEFASADA",
            np.where(df["Dias_Desde_Horimetro"] <= STALE_THRESHOLD_DAYS, "RECENTE", "DEFASADA")
        )
    )

    resultados = []
    for modelo, grp in df.groupby("Model Grupo"):
        recente  = grp[grp["POPULACAO"] == "RECENTE"]["Horimetro_Final"].dropna()
        defasada = grp[grp["POPULACAO"] == "DEFASADA"]["Horimetro_Final"].dropna()
        estimado = grp[grp["POPULACAO"] == "ESTIMADO"]["Horimetro_Final"].dropna()

        p_value = np.nan
        if len(recente) >= 3 and len(defasada) >= 3:
            _, p_value = stats.mannwhitneyu(recente, defasada, alternative="two-sided")

        cobertura = len(recente) / max(len(recente) + len(defasada), 1) * 100
        mediana_confiavel = (pd.isna(p_value) or p_value > 0.05) and cobertura >= 20.0

        resultados.append({
            "Model Grupo"         : modelo,
            "N_Recente"           : len(recente),
            "N_Defasada"          : len(defasada),
            "N_Estimado"          : len(estimado),
            "Cobertura_Recente_%" : round(cobertura, 1),
            "Mediana_Recente"     : round(recente.median(), 1) if len(recente) else np.nan,
            "Mediana_Defasada"    : round(defasada.median(), 1) if len(defasada) else np.nan,
            "Mediana_Estimado"    : round(estimado.median(), 1) if len(estimado) else np.nan,
            "Mann_Whitney_p"      : round(p_value, 4) if pd.notna(p_value) else np.nan,
            "MEDIANA_CONFIAVEL"   : mediana_confiavel,
        })

    df_res = pd.DataFrame(resultados).sort_values("N_Recente", ascending=False)
    problemas = df_res[(~df_res["MEDIANA_CONFIAVEL"]) & (df_res["N_Recente"] >= 5)]

    print("\n=== ANÁLISE C: Validação Cruzada por Modelo ===")
    print(df_res.to_string(index=False))
    if not problemas.empty:
        print(f"\n*** GATE BLOQUEADO: {len(problemas)} modelo(s) com N_Recente>=5 e MEDIANA_CONFIAVEL=False ***")
        print(problemas[["Model Grupo", "N_Recente", "Cobertura_Recente_%", "Mann_Whitney_p"]].to_string(index=False))
    else:
        print("\n✓ Gate OK — todos os modelos com N_Recente>=5 têm MEDIANA_CONFIAVEL=True")

    df_res.to_csv(SANDBOX_OUT / "analise_c_validacao_cruzada.csv", index=False)
    print(f"CSV: {SANDBOX_OUT / 'analise_c_validacao_cruzada.csv'}")
```

**Step 2: Chamar no `__main__`**

```python
    analise_validacao_cruzada(df)
```

**Step 3: Rodar sandbox completo e confirmar 3 CSVs gerados**

Run: `$env:PYTHONIOENCODING="utf-8"; python sandbox_horimetro_staleness.py`
Expected: 3 análises impressas em sequência, 3 arquivos CSV em `data/sandbox/`. Mensagem final "Gate OK" ou lista de modelos problemáticos.

---

### Task 5: [GATE HUMANO] Revisar resultados do sandbox

**Não há código nesta task.** Victor revisa os CSVs e confirma:

- `analise_b_impacto_corte.csv`: delta de potencial R$ aceitável
- `analise_c_validacao_cruzada.csv`: nenhum `Model Grupo` com `N_Recente >= 5` e `MEDIANA_CONFIAVEL = False`

**Fase 2 só inicia após confirmação explícita.**

---

## FASE 2 — Implementação no Pipeline

> PRÉ-REQUISITO: Gate da Task 5 aprovado.

### Task 6: Adicionar HORIMETRO_STALE_THRESHOLD_DAYS em config.py

**Files:**

- Modify: `C:\Projetos\Inova\shared\config.py`

**Step 1: Adicionar constante no final do arquivo**

```python
# Horímetro: dias máximos sem atualização para manter STATUS_USO = "REAL"
HORIMETRO_STALE_THRESHOLD_DAYS = 120
```

**Step 2: Verificar sintaxe**

Run: `python -c "from config import HORIMETRO_STALE_THRESHOLD_DAYS; print(HORIMETRO_STALE_THRESHOLD_DAYS)"`
Expected: `120`

---

### Task 7: TDD — _preparar_pops com Dias_Desde_Horimetro (T-001, T-002)

**Files:**

- Modify: `tests/test_horimetro_oficina.py` (adicionar 2 testes)
- Modify: `transform.py` (função `_preparar_pops`, linha ~72)

**Step 1: Escrever testes T-001 e T-002**

Adicionar ao final de `tests/test_horimetro_oficina.py`:

```python
def test_preparar_pops_dias_desde_horimetro_defasado():
    """T-001: AOR Date de 200 dias atrás → Dias_Desde_Horimetro > 120."""
    from transform import _preparar_pops
    data_antiga = (pd.Timestamp.now() - pd.Timedelta(days=200)).strftime("%Y-%m-%d")
    df = pd.DataFrame([{
        "Serial Number": "CHASSI1",
        "Basic Warranty Expiration": pd.Timestamp("2025-01-01"),
        "Forecasted Machine Hours": 1000.0,
        "AOR Last Location Date": data_antiga,
    }])
    out = _preparar_pops(df)
    assert "Dias_Desde_Horimetro" in out.columns
    assert out.iloc[0]["Dias_Desde_Horimetro"] > 120


def test_preparar_pops_dias_nulos_viram_999():
    """T-002: AOR Last Location Date nulo → Dias_Desde_Horimetro == 999."""
    from transform import _preparar_pops
    df = pd.DataFrame([{
        "Serial Number": "CHASSI2",
        "Basic Warranty Expiration": pd.Timestamp("2025-01-01"),
        "Forecasted Machine Hours": 500.0,
        "AOR Last Location Date": None,
    }])
    out = _preparar_pops(df)
    assert out.iloc[0]["Dias_Desde_Horimetro"] == 999
```

**Step 2: Confirmar falha**

Run: `$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/test_horimetro_oficina.py::test_preparar_pops_dias_desde_horimetro_defasado tests/test_horimetro_oficina.py::test_preparar_pops_dias_nulos_viram_999 -v`
Expected: FAIL com `KeyError` ou `AssertionError`.

**Step 3: Implementar em `_preparar_pops` (transform.py)**

Adicionar ao final da função, antes do `return df`:

```python
    aor_date = pd.to_datetime(
        df.get("AOR Last Location Date", pd.Series(dtype="object")),
        errors="coerce"
    )
    df["Dias_Desde_Horimetro"] = (
        pd.Timestamp.now().normalize() - aor_date
    ).dt.days.fillna(999).astype(int)
```

**Step 4: Confirmar PASS**

Run: `$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/test_horimetro_oficina.py::test_preparar_pops_dias_desde_horimetro_defasado tests/test_horimetro_oficina.py::test_preparar_pops_dias_nulos_viram_999 -v`
Expected: PASS nos 2 testes.

---

### Task 8: TDD — _imputar_horimetro com staleness check (T-003, T-004)

**Files:**

- Modify: `tests/test_horimetro_oficina.py` (adicionar 2 testes)
- Modify: `transform.py` (função `_imputar_horimetro`, linha ~238 + import config)

**Step 1: Escrever testes T-003 e T-004**

```python
def test_imputar_horimetro_real_defasado_vira_estimado():
    """T-003: JDLink presente mas AOR > 120 dias → STATUS_USO = ESTIMADO."""
    from transform import _imputar_horimetro
    df_frota = pd.DataFrame([{
        "Serial Number": "CHASSI1", "Model": "310P",
        "Data_NF_Venda": pd.Timestamp("2024-01-01"),
        "Forecasted Machine Hours": 2000.0, "Ano_Venda": 2024,
        "Dias_Desde_Horimetro": 200,
    }])
    df_base = pd.DataFrame([{"Model #": "310P", "Custo hora Sobratema Peças": 50.0}])
    out = _imputar_horimetro(df_frota, df_base)
    assert out.iloc[0]["STATUS_USO"] == "ESTIMADO"
    assert out.iloc[0]["METODO_HORIMETRO"] == "MEDIANA"


def test_imputar_horimetro_real_recente_permanece_real():
    """T-004: JDLink presente e AOR <= 120 dias → STATUS_USO = REAL."""
    from transform import _imputar_horimetro
    df_frota = pd.DataFrame([{
        "Serial Number": "CHASSI2", "Model": "310P",
        "Data_NF_Venda": pd.Timestamp("2024-01-01"),
        "Forecasted Machine Hours": 2000.0, "Ano_Venda": 2024,
        "Dias_Desde_Horimetro": 30,
    }])
    df_base = pd.DataFrame([{"Model #": "310P", "Custo hora Sobratema Peças": 50.0}])
    out = _imputar_horimetro(df_frota, df_base)
    assert out.iloc[0]["STATUS_USO"] == "REAL"
```

**Step 2: Confirmar falha**

Run: `$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/test_horimetro_oficina.py::test_imputar_horimetro_real_defasado_vira_estimado tests/test_horimetro_oficina.py::test_imputar_horimetro_real_recente_permanece_real -v`
Expected: FAIL — T-003 chega como REAL (comportamento antigo).

**Step 3: Adicionar import de config no topo de `transform.py`**

Logo após os imports existentes de `config_inova_identity`:

```python
from config import HORIMETRO_STALE_THRESHOLD_DAYS
```

**Step 4: Atualizar lógica em `_imputar_horimetro` (linha ~238)**

Substituir:

```python
    mask_zerado = df["Forecasted Machine Hours"] < 10
    df["STATUS_USO"] = np.where(mask_zerado, "ESTIMADO", "REAL")
```

Por:

```python
    mask_zerado   = df["Forecasted Machine Hours"] < 10
    mask_defasado = df.get("Dias_Desde_Horimetro", pd.Series(999, index=df.index)) > HORIMETRO_STALE_THRESHOLD_DAYS
    df["STATUS_USO"] = np.where(mask_zerado | mask_defasado, "ESTIMADO", "REAL")
```

**Step 5: Confirmar PASS nos 2 novos testes**

Run: `$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/test_horimetro_oficina.py::test_imputar_horimetro_real_defasado_vira_estimado tests/test_horimetro_oficina.py::test_imputar_horimetro_real_recente_permanece_real -v`
Expected: PASS.

---

### Task 9: Exportar Dias_Desde_Horimetro + suite completa + commit (T-005, T-006)

**Files:**

- Modify: `transform.py` (`cols_chassi` em `build_exports`, linha ~404)

**Step 1: Adicionar `Dias_Desde_Horimetro` em `cols_chassi`**

Localizar:

```python
        "Horimetro_Final", "METODO_HORIMETRO", "STATUS_USO",
```

Substituir por:

```python
        "Horimetro_Final", "METODO_HORIMETRO", "STATUS_USO", "Dias_Desde_Horimetro",
```

**Step 2: Rodar suite completa (T-006)**

Run: `$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/ -v`
Expected: PASS em todos os testes (4 novos + todos os existentes).

**Step 3: Commit**

```bash
git add shared/config.py
git add pipelines/potencial-clientes/03_Potencial/transform.py
git add pipelines/potencial-clientes/03_Potencial/tests/test_horimetro_oficina.py
git add pipelines/potencial-clientes/03_Potencial/sandbox_horimetro_staleness.py
git add pipelines/potencial-clientes/03_Potencial/docs/specs/2026-05-29-spec-horimetro-staleness.md
git add pipelines/potencial-clientes/03_Potencial/docs/plans/2026-05-29-horimetro-staleness.md
git commit -m "feat(m3): reclassificar horimetro defasado >120d como ESTIMADO"
```

---

## Critérios de Saída

- [ ] 3 CSVs em `data/sandbox/` gerados e revisados
- [ ] Gate humano (T5) aprovado por Victor
- [ ] `HORIMETRO_STALE_THRESHOLD_DAYS = 120` em `shared/config.py`
- [ ] `Dias_Desde_Horimetro` calculado em `_preparar_pops`
- [ ] `mask_defasado` ativa em `_imputar_horimetro`
- [ ] `Dias_Desde_Horimetro` exportado no parquet chassi
- [ ] 4 novos testes (T-001..T-004) PASS
- [ ] Suite completa PASS
- [ ] Commit limpo
