# dataset_ouro_potencial_clientes — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `stout-executing-plans` to implement this plan task-by-task.

**Goal:** Gerar `dataset_ouro_potencial_clientes` no nível cliente individual (CNPJ + NOME_CLIENTE), sem alterar nenhum arquivo de produção existente.

**Architecture:** Adicionar `df_potencial_clientes` na função `build_exports` de `transform.py`, propagar pelo retorno de `run_transform`, persistir em `load.py` e passar em `run.py`. Tudo aditivo — zero alteração nos datasets existentes.

**Tech Stack:** Python 3.x, pandas, pytest, parquet (pyarrow)

**Spec:** `docs/specs/2026-06-01-spec-dataset-potencial-clientes.md`

---

## Pré-condição: Sandbox

Antes de qualquer tarefa, confirme que está trabalhando em worktree isolado ou cópia local do motor — **NÃO no diretório de produção**.

```bash
# Verificar que não está em produção
pwd  # deve ser worktree/sandbox, não C:\Projetos\Inova\pipelines\potencial-clientes\03_Potencial
```

---

## Task 1: Escrever o teste que valida `df_potencial_clientes`

**Arquivo:**

- Criar: `tests/test_potencial_clientes.py`

**Step 1: Criar o arquivo de teste**

```python
# tests/test_potencial_clientes.py
"""Testes para dataset_ouro_potencial_clientes — granularidade nível cliente."""
import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.insert(0, str(Path(__file__).parents[4] / "shared"))

from transform import build_exports


def _make_df_potencial() -> pd.DataFrame:
    """DataFrame mínimo com 3 chassis: 2 do mesmo grupo, clientes distintos."""
    return pd.DataFrame({
        "PIN":                          ["PIN001", "PIN002", "PIN003"],
        "Customer":                     ["CLIENTE A", "CLIENTE B", "CLIENTE A"],
        "CNPJ":                         ["12345678000100", "12345678000200", "12345678000100"],
        "CNPJ_Raiz_Local":              ["12345678",       "12345678",       "12345678"],
        "CNPJ_GRUPO":                   ["12345678",       "12345678",       "99999999"],
        "Razao_Social_Grupo":           ["GRUPO X",        "GRUPO X",        "GRUPO Y"],
        "NOME_GRUPO_ORIGINAL":          ["GRUPO X",        "GRUPO X",        "GRUPO Y"],
        "Potencial Total Anual":        [1000.0,           2000.0,           500.0],
        "Potencial Total Proporcional": [800.0,            1600.0,           400.0],
        "Potencial Peças Anual":        [600.0,            1200.0,           300.0],
        "Potencial Pneus Anual":        [100.0,            200.0,            50.0],
        "Potencial Material Rodante Anual": [100.0,        200.0,            50.0],
        "Potencial Lubrificantes Anual":    [100.0,        200.0,            50.0],
        "Potencial Peças de Desgaste Anual":[100.0,        200.0,            50.0],
        "Horimetro_Final":              [1000.0,           1500.0,           800.0],
        "AOR Indicator":                ["Inside dealer AOR", "Inside dealer AOR", "Inside dealer AOR"],
        "Model Grupo":                  ["310L",           "624K",           "770G"],
        "Potencial Proporcional":       [800.0,            1600.0,           400.0],
        "Segmento de Atuacao":          ["Construcao",     "Construcao",     "Construcao"],
        "Potencial_Benchmark":          [None,             None,             None],
        "Ano Fabricacao":               [2018,             2019,             2020],
        "METODO_HORIMETRO":             ["TELEMETRIA",     "TELEMETRIA",     "MEDIANA"],
        "STATUS_USO":                   ["REAL",           "REAL",           "ESTIMADO"],
        "Dias_Desde_Horimetro":         [10,               20,               999],
        "Cidade":                       ["BH",             "SP",             "RJ"],
    })


def test_potencial_clientes_colunas_obrigatorias():
    """Novo dataset deve ter NOME_CLIENTE, CNPJ, CNPJ_GRUPO, Razao_Social_Grupo."""
    df = _make_df_potencial()
    _, _, df_clientes, _, _ = build_exports(df, pd.DataFrame())
    colunas_esperadas = {"NOME_CLIENTE", "CNPJ", "CNPJ_GRUPO", "Razao_Social_Grupo", "Potencial Total"}
    assert colunas_esperadas.issubset(set(df_clientes.columns)), (
        f"Colunas ausentes: {colunas_esperadas - set(df_clientes.columns)}"
    )


def test_potencial_clientes_granularidade_cliente():
    """Uma linha por CNPJ + NOME_CLIENTE — não por grupo."""
    df = _make_df_potencial()
    _, _, df_clientes, _, _ = build_exports(df, pd.DataFrame())
    # PIN001 e PIN003 têm mesmo CNPJ+Customer → 1 linha; PIN002 → 1 linha; total: 2
    assert len(df_clientes) == 2, f"Esperado 2 clientes, obtido {len(df_clientes)}"


def test_potencial_clientes_soma_potencial():
    """Potencial Total de CLIENTE A deve somar PIN001 + PIN003 = 1500."""
    df = _make_df_potencial()
    _, _, df_clientes, _, _ = build_exports(df, pd.DataFrame())
    cliente_a = df_clientes[df_clientes["NOME_CLIENTE"] == "CLIENTE A"]
    assert not cliente_a.empty
    assert cliente_a["Potencial Total"].iloc[0] == pytest.approx(1500.0)


def test_potencial_clientes_cnpj_grupo_preservado():
    """CNPJ_GRUPO deve ser propagado corretamente do M0."""
    df = _make_df_potencial()
    _, _, df_clientes, _, _ = build_exports(df, pd.DataFrame())
    cliente_b = df_clientes[df_clientes["NOME_CLIENTE"] == "CLIENTE B"]
    assert cliente_b["CNPJ_GRUPO"].iloc[0] == "12345678"


def test_potencial_clientes_sem_alteracao_v1():
    """df_cliente (v1, nível grupo) deve continuar intacto."""
    df = _make_df_potencial()
    _, df_v1, _, _, _ = build_exports(df, pd.DataFrame())
    assert "NOME_CLIENTE" not in df_v1.columns, "df_cliente (v1) não deve ter NOME_CLIENTE"
    assert "CNPJ_GRUPO" in df_v1.columns
```

**Step 2: Rodar o teste para confirmar FAIL**

```bash
cd C:\Projetos\Inova\pipelines\potencial-clientes\03_Potencial
$env:PYTHONIOENCODING="utf-8"
python -m pytest tests/test_potencial_clientes.py -v
```

Esperado: **FAIL** — `ValueError: not enough values to unpack` (build_exports retorna 4, teste espera 5)

---

## Task 2: Adicionar `df_potencial_clientes` em `build_exports`

**Arquivo:**

- Modificar: `transform.py` — função `build_exports` (linha ~413)

**Step 1: Adicionar geração de `df_potencial_clientes` após o bloco de `df_cliente`**

Localizar o bloco que termina com `df_cliente = df_cliente[[c for c in cols_grupo if c in df_cliente.columns]]` e adicionar logo depois:

```python
    # --- dataset nível cliente individual (CNPJ + Customer) ---
    df_potencial_clientes = (
        df.groupby(["CNPJ", "Customer"], sort=False)
        .agg(
            NOME_CLIENTE=("Customer", "first"),
            CNPJ_GRUPO=("CNPJ_GRUPO", "first"),
            Razao_Social_Grupo=("Razao_Social_Grupo", "first"),
            Qtd_Maquinas=("PIN", "count"),
            Horimetro_Medio=("Horimetro_Final", "mean"),
            Potencial_Pecas_Anual=("Potencial Peças Anual", "sum"),
            Potencial_Pneus_Anual=("Potencial Pneus Anual", "sum"),
            Potencial_Mat_Rodante_Anual=("Potencial Material Rodante Anual", "sum"),
            Potencial_Lubrificantes_Anual=("Potencial Lubrificantes Anual", "sum"),
            Potencial_Desgaste_Anual=("Potencial Peças de Desgaste Anual", "sum"),
            Potencial_Total_Anual=("Potencial Total Anual", "sum"),
            Potencial_Total_Proporcional=("Potencial Total Proporcional", "sum"),
        )
        .reset_index(drop=True)
    )
    df_potencial_clientes.columns = [
        "NOME_CLIENTE", "CNPJ_GRUPO", "Razao_Social_Grupo", "Qtd_Maquinas", "Horimetro_Medio",
        "Potencial Peças Anual", "Potencial Pneus Anual", "Potencial Material Rodante Anual",
        "Potencial Lubrificantes Anual", "Potencial Peças de Desgaste Anual",
        "Potencial Total", "Potencial Proporcional",
    ]
    # Adicionar CNPJ após reset — recuperar do groupby key
    _cnpj_map = (
        df.sort_values("Potencial Total Anual", ascending=False)
        .drop_duplicates(subset=["Customer"])
        .set_index("Customer")["CNPJ"]
        .to_dict()
    )
    df_potencial_clientes.insert(1, "CNPJ", df_potencial_clientes["NOME_CLIENTE"].map(_cnpj_map))
    cols_clientes = [
        "NOME_CLIENTE", "CNPJ", "CNPJ_GRUPO", "Razao_Social_Grupo", "Qtd_Maquinas", "Horimetro_Medio",
        "Potencial Peças Anual", "Potencial Proporcional", "Potencial Total",
        "Potencial Pneus Anual", "Potencial Material Rodante Anual",
        "Potencial Lubrificantes Anual", "Potencial Peças de Desgaste Anual",
    ]
    df_potencial_clientes = df_potencial_clientes[[c for c in cols_clientes if c in df_potencial_clientes.columns]]
```

**Step 2: Atualizar o `return` de `build_exports`**

Localizar:

```python
    return df_chassi, df_cliente, df_feedback, auditoria
```

Substituir por:

```python
    return df_chassi, df_cliente, df_potencial_clientes, df_feedback, auditoria
```

**Step 3: Rodar o teste**

```bash
python -m pytest tests/test_potencial_clientes.py -v
```

Esperado: todos os 5 testes **PASS**

---

## Task 3: Propagar o novo retorno em `run_transform`

**Arquivo:**

- Modificar: `transform.py` — função `run_transform` (linha ~542)

**Step 1: Atualizar chamada e retorno**

Localizar:

```python
    df_chassi_b, df_cliente, df_feedback, auditoria = build_exports(df_potencial_b, df_pops)
```

Substituir por:

```python
    df_chassi_b, df_cliente, df_potencial_clientes, df_feedback, auditoria = build_exports(df_potencial_b, df_pops)
```

Localizar:

```python
    return df_chassi_b, df_cliente, df_feedback, auditoria, df_nao_classificados, df_resumo_ab, df_detalhe_ab
```

Substituir por:

```python
    return df_chassi_b, df_cliente, df_potencial_clientes, df_feedback, auditoria, df_nao_classificados, df_resumo_ab, df_detalhe_ab
```

**Step 2: Rodar todos os testes do M3**

```bash
python -m pytest tests/ -v
```

Esperado: todos os testes existentes continuam **PASS**, novos também **PASS**

---

## Task 4: Persistir o novo dataset em `load.py`

**Arquivo:**

- Modificar: `load.py` — assinatura e corpo da função `save`

**Step 1: Adicionar parâmetro `df_potencial_clientes` na assinatura**

Localizar:

```python
def save(
    df_chassi: pd.DataFrame,
    df_cliente: pd.DataFrame,
    df_feedback: pd.DataFrame,
    auditoria: dict,
    data_dir: Path,
    shared_data_dir: Path,
    df_nao_classificados: pd.DataFrame = None,
    df_resumo_ab: pd.DataFrame = None,
    df_detalhe_ab: pd.DataFrame = None,
) -> None:
```

Substituir por:

```python
def save(
    df_chassi: pd.DataFrame,
    df_cliente: pd.DataFrame,
    df_potencial_clientes: pd.DataFrame,
    df_feedback: pd.DataFrame,
    auditoria: dict,
    data_dir: Path,
    shared_data_dir: Path,
    df_nao_classificados: pd.DataFrame = None,
    df_resumo_ab: pd.DataFrame = None,
    df_detalhe_ab: pd.DataFrame = None,
) -> None:
```

**Step 2: Adicionar persistência após o bloco de `df_cliente`**

Localizar:

```python
    _safe_excel(df_cliente, data_dir / "dataset_ouro_potencial_v1.xlsx")
    log.info("Potencial Total Anual: R$ %.2f", df_cliente["Potencial Total"].sum())
```

Adicionar logo depois:

```python
    df_potencial_clientes.to_parquet(shared_data_dir / "dataset_ouro_potencial_clientes.parquet", index=False)
    df_potencial_clientes.to_parquet(data_dir / "dataset_ouro_potencial_clientes.parquet", index=False)
    _safe_excel(df_potencial_clientes, data_dir / "dataset_ouro_potencial_clientes.xlsx")
    log.info("Potencial Clientes: %d clientes, R$ %.2f", len(df_potencial_clientes), df_potencial_clientes["Potencial Total"].sum())
```

---

## Task 5: Atualizar `run.py`

**Arquivo:**

- Modificar: `run.py` — desempacotamento de `run_transform` e chamada de `save`

**Step 1: Atualizar desempacotamento**

Localizar:

```python
        df_chassi, df_cliente, df_feedback, auditoria, df_nao_classificados, df_resumo_ab, df_detalhe_ab = run_transform(raw)
```

Substituir por:

```python
        df_chassi, df_cliente, df_potencial_clientes, df_feedback, auditoria, df_nao_classificados, df_resumo_ab, df_detalhe_ab = run_transform(raw)
```

**Step 2: Atualizar chamada de `save`**

Localizar:

```python
        save(
            df_chassi,
            df_cliente,
            df_feedback,
            auditoria,
            DATA_DIR,
            SHARED_DATA,
            df_nao_classificados=df_nao_classificados,
            df_resumo_ab=df_resumo_ab,
            df_detalhe_ab=df_detalhe_ab
        )
```

Substituir por:

```python
        save(
            df_chassi,
            df_cliente,
            df_potencial_clientes,
            df_feedback,
            auditoria,
            DATA_DIR,
            SHARED_DATA,
            df_nao_classificados=df_nao_classificados,
            df_resumo_ab=df_resumo_ab,
            df_detalhe_ab=df_detalhe_ab
        )
```

---

## Task 6: Rodar suite completa de testes

```bash
cd C:\Projetos\Inova\pipelines\potencial-clientes\03_Potencial
$env:PYTHONIOENCODING="utf-8"
python -m pytest tests/ -v
```

Esperado: **todos PASS**, nenhuma regressão

---

## Task 7: Verificação de integridade do novo dataset (sandbox)

Rodar o motor em sandbox com dados reais e validar:

```bash
$env:PYTHONIOENCODING="utf-8"
python run.py
```

Então verificar:

```python
import pandas as pd
from pathlib import Path

v1 = pd.read_parquet("data/dataset_ouro_potencial_v1.parquet")
clientes = pd.read_parquet("data/dataset_ouro_potencial_clientes.parquet")

print("V1 (grupos):", len(v1), "| Potencial:", v1["Potencial Total"].sum())
print("Clientes:   ", len(clientes), "| Potencial:", clientes["Potencial Total"].sum())

# Caso de teste CSN — deve ter múltiplos clientes
csn = clientes[clientes["CNPJ_GRUPO"] == "08902291"]
print("\nCSN - clientes distintos:", len(csn))
print(csn[["NOME_CLIENTE","CNPJ","CNPJ_GRUPO","Razao_Social_Grupo","Potencial Total"]].to_string())

# Soma de potencial deve ser igual nos dois datasets
assert abs(v1["Potencial Total"].sum() - clientes["Potencial Total"].sum()) < 1.0, "Potencial diverge!"
print("\n✅ Potencial consistente entre V1 e Clientes")
```

Esperado:

- Clientes > Grupos (mais linhas)
- Soma de `Potencial Total` ≈ igual entre os dois
- CSN aparece com ao menos 2 clientes distintos

---

## Task 8: Commit

```bash
git add pipelines/potencial-clientes/03_Potencial/transform.py \
        pipelines/potencial-clientes/03_Potencial/load.py \
        pipelines/potencial-clientes/03_Potencial/run.py \
        pipelines/potencial-clientes/03_Potencial/tests/test_potencial_clientes.py \
        pipelines/potencial-clientes/03_Potencial/docs/specs/2026-06-01-spec-dataset-potencial-clientes.md \
        pipelines/potencial-clientes/03_Potencial/docs/plans/2026-06-01-plan-dataset-potencial-clientes.md

git commit -m "feat(m3): adicionar dataset_ouro_potencial_clientes nivel cliente individual

Cria dataset_ouro_potencial_clientes (CNPJ + NOME_CLIENTE) como alternativa
ao dataset_ouro_potencial_v1 (nivel grupo). Permite que M4/M5 consumam
potencial por cliente e façam agrupamento por CNPJ_GRUPO downstream.
Dataset v1 intacto — mudança puramente aditiva."
```
