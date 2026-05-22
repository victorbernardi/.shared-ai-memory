# Tendência por Filial — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir o "top 3 filiais" por ranking completo de todas as filiais ativas no dia, com receita de ontem, média diária do mês e desvio percentual.

**Architecture:** Nova função `receita_por_filial()` em `faturamento.py` agrega sem limite; `foto_ontem()` usa `df_mes` (já carregado) para calcular média por filial e monta lista ordenada; `generator.py` renderiza o novo formato no email.

**Tech Stack:** Python 3.11, pandas, pytest.

---

## Arquivos

| Arquivo | Mudança |
|---|---|
| `src/faturamento.py` | +`receita_por_filial(df) -> dict[str, float]` |
| `src/snapshot_diario.py` | Substituir bloco `top_fil` por `filiais_ranking` (lista de dicts) |
| `src/generator.py` | +`_filiais_ranking_md()`; substituir `snap_top_filiais` por `snap_filiais_ranking` |
| `templates/email_template_v3.md` | Label + placeholder |
| `tests/test_faturamento.py` | +1 teste para `receita_por_filial` |
| `tests/test_snapshot_diario.py` | +4 testes para `filiais_ranking` |
| `tests/test_generator.py` | +1 teste para `_filiais_ranking_md` |

---

## Task 1: `receita_por_filial()` em `faturamento.py`

**Files:**

- Modify: `src/faturamento.py`
- Test: `tests/test_faturamento.py`

- [ ] **Step 1: Escrever o teste que falhará**

Adicionar ao final de `tests/test_faturamento.py`:

```python
def test_receita_por_filial_retorna_todas_filiais():
    from src.faturamento import por_mes, receita_por_filial

    df = por_mes(2026, 1)
    resultado = receita_por_filial(df)
    # FIXTURE_DF jan/2026: 0201=2000, 0202=500
    assert resultado == {"0201": pytest.approx(2000.0), "0202": pytest.approx(500.0)}
```

- [ ] **Step 2: Rodar para confirmar FAIL**

```bash
pytest tests/test_faturamento.py::test_receita_por_filial_retorna_todas_filiais -v
```

Esperado: `FAILED` com `ImportError: cannot import name 'receita_por_filial'`

- [ ] **Step 3: Implementar em `src/faturamento.py`**

Adicionar após `top_filiais()`:

```python
def receita_por_filial(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {}
    return (
        df.groupby("FILIAL")["VALOR_DO_PRODUTO"]
        .sum()
        .to_dict()
    )
```

- [ ] **Step 4: Rodar para confirmar PASS**

```bash
pytest tests/test_faturamento.py -v
```

Esperado: todos PASS.

- [ ] **Step 5: Commit**

```bash
git add src/faturamento.py tests/test_faturamento.py
git commit -m "feat(inova-daily): receita_por_filial sem limite de n"
```

---

## Task 2: `filiais_ranking` em `snapshot_diario.py`

**Files:**

- Modify: `src/snapshot_diario.py`
- Test: `tests/test_snapshot_diario.py`

- [ ] **Step 1: Escrever os testes que falharão**

Adicionar ao final de `tests/test_snapshot_diario.py`:

```python
def test_filiais_ranking_presente():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    assert "filiais_ranking" in r
    assert isinstance(r["filiais_ranking"], list)


def test_filiais_ranking_ordenado_por_ontem_desc():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    valores = [f["ontem"] for f in r["filiais_ranking"]]
    assert valores == sorted(valores, reverse=True)


def test_filiais_ranking_campos_obrigatorios():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    for f in r["filiais_ranking"]:
        assert "nome" in f
        assert "ontem" in f
        assert "media_dia" in f
        assert "delta_pct" in f


def test_filiais_ranking_delta_zero_quando_media_zero():
    """Filial sem histórico no mês → media_dia = 0 → delta_pct = 0.0."""
    import pandas as pd
    from unittest.mock import patch
    from src.snapshot_diario import foto_ontem

    # df_mes vazio → acumulado por filial = 0 para todas
    df_mes_vazio = pd.DataFrame({
        "DATA_EMISSAO_NF": pd.Series([], dtype="datetime64[ns]"),
        "FILIAL": pd.Series([], dtype=str),
        "VALOR_DO_PRODUTO": pd.Series([], dtype=float),
    })

    with patch("src.snapshot_diario.fat.por_mes", return_value=df_mes_vazio):
        r = foto_ontem(date(2026, 5, 14))

    for f in r["filiais_ranking"]:
        assert f["delta_pct"] == pytest.approx(0.0)
```

Nota: os mocks do fixture `mock_deps` em `tests/test_snapshot_diario.py` já mockam `fat.por_dia` e `fat.por_mes`, então os testes básicos usarão os dados mockados existentes (DF_M2_DIA tem FILIAL "201" e "202").

- [ ] **Step 2: Rodar para confirmar FAIL**

```bash
pytest tests/test_snapshot_diario.py::test_filiais_ranking_presente -v
```

Esperado: `FAILED` com `KeyError: 'filiais_ranking'`

- [ ] **Step 3: Implementar em `src/snapshot_diario.py`**

**3a)** Adicionar import de `receita_por_filial` no topo do arquivo (após `from src import faturamento as fat`):

O import já é feito via `fat.receita_por_filial` — nenhuma mudança de import necessária.

**3b)** Substituir o bloco atual (linhas 75–81):

```python
top_fil = (
    df_dia_m2.groupby("FILIAL")["VALOR_DO_PRODUTO"].sum()
    .sort_values(ascending=False).head(3)
    if not df_dia_m2.empty else {}
)
from src.config import FILIAL_MAP
top_fil = {FILIAL_MAP.get(str(k), str(k)): float(v) for k, v in top_fil.items()}
```

Por:

```python
from src.config import FILIAL_MAP
receita_ontem_por_filial = fat.receita_por_filial(df_dia_m2)
```

**3c)** Após o bloco `df_mes = fat.por_mes(ano, mes)` / `acumulado_mes = fat.total_faturado(df_mes)` (linhas 90–91), adicionar:

```python
receita_mes_por_filial = fat.receita_por_filial(df_mes)
```

**3d)** Após `dias_corridos = len(pd.bdate_range(...))` (linha 112), adicionar:

```python
filiais_ranking = []
for cod_filial, ontem_val in sorted(
    receita_ontem_por_filial.items(), key=lambda x: x[1], reverse=True
):
    acumulado_filial = receita_mes_por_filial.get(cod_filial, 0.0)
    media_dia = acumulado_filial / dias_corridos if dias_corridos > 0 else 0.0
    delta_pct = ((ontem_val - media_dia) / media_dia * 100) if media_dia > 0 else 0.0
    filiais_ranking.append({
        "nome": FILIAL_MAP.get(str(cod_filial), str(cod_filial)),
        "ontem": float(ontem_val),
        "media_dia": float(media_dia),
        "delta_pct": round(delta_pct, 1),
    })
```

**3e)** No dict de retorno, substituir `"top_filiais": top_fil,` por:

```python
"filiais_ranking": filiais_ranking,
```

- [ ] **Step 4: Rodar para confirmar PASS**

```bash
pytest tests/test_snapshot_diario.py -v
```

Esperado: todos PASS. Se `test_top_filiais*` quebrar (chave removida), deletar esse teste — ele foi substituído pelos novos.

- [ ] **Step 5: Commit**

```bash
git add src/snapshot_diario.py tests/test_snapshot_diario.py
git commit -m "feat(inova-daily): filiais_ranking com tendencia vs media do mes"
```

---

## Task 3: Email — renderização e template

**Files:**

- Modify: `src/generator.py`
- Modify: `templates/email_template_v3.md`
- Test: `tests/test_generator.py`

- [ ] **Step 1: Escrever o teste que falhará**

Adicionar ao final de `tests/test_generator.py`:

```python
def test_filiais_ranking_md_formata_linha_corretamente():
    from src.generator import _filiais_ranking_md
    filiais = [
        {"nome": "Contagem", "ontem": 513_494.26, "media_dia": 458_000.0, "delta_pct": 12.1},
        {"nome": "Uberlândia", "ontem": 70_797.0, "media_dia": 95_200.0, "delta_pct": -25.6},
    ]
    resultado = _filiais_ranking_md(filiais)
    assert "1. **Contagem:**" in resultado
    assert "+12.1%" in resultado
    assert "2. **Uberlândia:**" in resultado
    assert "-25.6%" in resultado
```

- [ ] **Step 2: Rodar para confirmar FAIL**

```bash
pytest tests/test_generator.py::test_filiais_ranking_md_formata_linha_corretamente -v
```

Esperado: `FAILED` com `ImportError: cannot import name '_filiais_ranking_md'`

- [ ] **Step 3: Implementar `_filiais_ranking_md()` em `src/generator.py`**

Adicionar após `_vendedores_md()`:

```python
def _filiais_ranking_md(filiais: list[dict]) -> str:
    linhas = []
    for i, f in enumerate(filiais, 1):
        sinal = "+" if f["delta_pct"] >= 0 else ""
        linhas.append(
            f"{i}. **{f['nome']}:** R$ {_brl(f['ontem'])} "
            f"| média do mês: R$ {_brl(f['media_dia'])} "
            f"({sinal}{f['delta_pct']:.1f}%)"
        )
    return "\n".join(linhas)
```

- [ ] **Step 4: Atualizar `gerar_email()` em `src/generator.py`**

Substituir a linha:

```python
content = content.replace("{{ snap_top_filiais }}", _vendedores_md(snap["top_filiais"]))
```

Por:

```python
content = content.replace("{{ snap_filiais_ranking }}", _filiais_ranking_md(snap["filiais_ranking"]))
```

- [ ] **Step 5: Atualizar `templates/email_template_v3.md`**

Substituir:

```markdown
**Top filiais:**
{{ snap_top_filiais }}
```

Por:

```markdown
**Filiais** *(por receita de ontem)*:
{{ snap_filiais_ranking }}
```

- [ ] **Step 6: Atualizar o snap_base nos testes existentes de generator**

Em `tests/test_generator.py`, na função `_snap_base()`, substituir:

```python
"top_filiais": {"Contagem": 15_000.0},
```

Por:

```python
"filiais_ranking": [
    {"nome": "Contagem", "ontem": 15_000.0, "media_dia": 12_000.0, "delta_pct": 25.0},
],
```

- [ ] **Step 7: Rodar suite completa**

```bash
pytest -v
```

Esperado: todos PASS.

- [ ] **Step 8: Commit**

```bash
git add src/generator.py templates/email_template_v3.md tests/test_generator.py
git commit -m "feat(inova-daily): renderizar filiais_ranking no email com tendencia"
```
