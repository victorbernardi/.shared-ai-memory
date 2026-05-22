# Manifest Divergência M2 vs vw_VENDAS — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detectar automaticamente quando o cache M2 está desatualizado comparando seu total com o total do vw_VENDAS (mesma query já feita), logar no JSONL de auditoria e exibir aviso no email se divergência > 0.05%.

**Architecture:** `foto_ontem()` já consulta ambas as fontes; basta expor os totais como campos no dict de retorno. `registrar_execucao()` recebe esses campos e os grava no JSONL. `generator.py` injeta aviso condicional no email via placeholder `{{ aviso_divergencia }}`.

**Tech Stack:** Python 3.11, pandas, pytest, pathlib. Sem dependências novas.

---

## Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `src/snapshot_diario.py` | +3 campos no dict: `m2_total`, `vw_total`, `divergencia_pct` |
| `src/auditor.py` | Corrigir `_RECONCILIACAO_TOLERANCIA` para 0.0005 (0.05%); `registrar_execucao()` recebe e loga `divergencia` |
| `src/generator.py` | Injetar `{{ aviso_divergencia }}` com string condicional |
| `templates/email_template_v3.md` | Adicionar `{{ aviso_divergencia }}` no rodapé |
| `tests/test_snapshot_diario.py` | +3 testes para os novos campos |
| `tests/test_auditor.py` | +2 testes: tolerância correta + divergência no JSONL |
| `tests/test_generator.py` | +2 testes: aviso presente/ausente conforme divergencia_pct |

---

## Task 1: Expor divergência em `foto_ontem()`

**Files:**

- Modify: `src/snapshot_diario.py`
- Test: `tests/test_snapshot_diario.py`

- [ ] **Step 1: Escrever os testes que falharão**

Adicionar ao final de `tests/test_snapshot_diario.py`:

```python
def test_divergencia_campos_presentes():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    assert "m2_total" in r
    assert "vw_total" in r
    assert "divergencia_pct" in r

def test_divergencia_zero_quando_fontes_iguais():
    """DF_VW.RECEITA.sum() == 15_000 == DF_M2_DIA.VALOR_DO_PRODUTO.sum() → divergência 0."""
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    assert r["divergencia_pct"] == pytest.approx(0.0)

def test_divergencia_detecta_diferenca():
    """vw_total diferente de m2_total → divergencia_pct > 0."""
    import pandas as pd
    from src.snapshot_diario import foto_ontem

    df_vw_diferente = pd.DataFrame({
        "NF": ["NF001"],
        "NOME_VENDEDOR": ["Joao"],
        "FILIAL_NOME": ["CONTAGEM"],
        "RECEITA": [20_000.0],  # diferente de 15_000 do M2
    })

    import src.snapshot_diario as sd
    original = sd.executar_query
    sd.executar_query = lambda q, l: df_vw_diferente.copy()
    try:
        r = foto_ontem(date(2026, 5, 14))
        assert r["divergencia_pct"] == pytest.approx(abs(20_000.0 - 15_000.0) / 15_000.0 * 100)
    finally:
        sd.executar_query = original
```

- [ ] **Step 2: Rodar para confirmar falha**

```bash
pytest tests/test_snapshot_diario.py::test_divergencia_campos_presentes -v
```

Esperado: `FAILED` com `KeyError: 'm2_total'`

- [ ] **Step 3: Implementar em `snapshot_diario.py`**

Após a linha `top_fil = {FILIAL_MAP.get(str(k), str(k)): float(v) for k, v in top_fil.items()}` (linha ~81), adicionar cálculo de divergência:

```python
vw_total = float(df_vw["RECEITA"].sum()) if not df_vw.empty else 0.0
divergencia_pct = abs((vw_total - total) / total * 100) if total > 0 else 0.0
```

No dict de retorno, adicionar após `"ritmo_necessario": ritmo_necessario,`:

```python
"m2_total": total,
"vw_total": vw_total,
"divergencia_pct": divergencia_pct,
```

- [ ] **Step 4: Rodar para confirmar aprovação**

```bash
pytest tests/test_snapshot_diario.py -v
```

Esperado: todos os testes PASS (incluindo os 3 novos)

- [ ] **Step 5: Commit**

```bash
git add src/snapshot_diario.py tests/test_snapshot_diario.py
git commit -m "feat(inova-daily): expor m2_total, vw_total e divergencia_pct no snapshot"
```

---

## Task 2: Corrigir tolerância e logar divergência no JSONL

**Files:**

- Modify: `src/auditor.py`
- Test: `tests/test_auditor.py`

- [ ] **Step 1: Escrever os testes que falharão**

Adicionar ao final de `tests/test_auditor.py`:

```python
def test_reconciliar_fontes_tolerancia_005_pct():
    """Divergência de 0.1% deve ser flagada (tolerância é 0.05%)."""
    from src.auditor import reconciliar_fontes
    total_vw = 100_000.0
    total_m2 = 99_900.0  # divergência exata de 0.1%
    resultado = reconciliar_fontes(total_vw, total_m2)
    assert not resultado.passed

def test_reconciliar_fontes_dentro_da_tolerancia():
    """Divergência de 0.03% não deve ser flagada."""
    from src.auditor import reconciliar_fontes
    total_vw = 100_000.0
    total_m2 = 99_970.0  # divergência de 0.03%
    resultado = reconciliar_fontes(total_vw, total_m2)
    assert resultado.passed

def test_registrar_execucao_inclui_divergencia(tmp_path):
    """JSONL deve conter m2_total, vw_total e divergencia_pct."""
    from src.auditor import AuditResult, registrar_execucao
    snap_result = AuditResult(passed=True, context="snapshot")
    arquivo = registrar_execucao(
        snap_result,
        recap_result=None,
        log_dir=tmp_path,
        m2_total=15_000.0,
        vw_total=15_001.0,
        divergencia_pct=0.007,
    )
    import json
    linha = json.loads(arquivo.read_text(encoding="utf-8").strip())
    assert linha["divergencia"]["m2_total"] == 15_000.0
    assert linha["divergencia"]["vw_total"] == 15_001.0
    assert linha["divergencia"]["divergencia_pct"] == pytest.approx(0.007)
```

- [ ] **Step 2: Rodar para confirmar falha**

```bash
pytest tests/test_auditor.py::test_reconciliar_fontes_tolerancia_005_pct tests/test_auditor.py::test_registrar_execucao_inclui_divergencia -v
```

Esperado: `FAILED` — tolerância errada e `registrar_execucao` não aceita kwargs de divergência

- [ ] **Step 3: Corrigir tolerância em `auditor.py`**

Alterar linha:

```python
_RECONCILIACAO_TOLERANCIA = 0.05  # 5%
```

Para:

```python
_RECONCILIACAO_TOLERANCIA = 0.0005  # 0.05%
```

- [ ] **Step 4: Atualizar assinatura de `registrar_execucao()`**

Substituir a assinatura atual:

```python
def registrar_execucao(
    snap_result: AuditResult,
    recap_result: AuditResult | None,
    log_dir: Path | None = None,
) -> Path:
```

Por:

```python
def registrar_execucao(
    snap_result: AuditResult,
    recap_result: AuditResult | None,
    log_dir: Path | None = None,
    m2_total: float | None = None,
    vw_total: float | None = None,
    divergencia_pct: float | None = None,
) -> Path:
```

E dentro da função, após a linha `"snapshot": _result_to_dict(snap_result),`, adicionar:

```python
if m2_total is not None:
    entry["divergencia"] = {
        "m2_total": m2_total,
        "vw_total": vw_total,
        "divergencia_pct": divergencia_pct,
    }
```

- [ ] **Step 5: Rodar para confirmar aprovação**

```bash
pytest tests/test_auditor.py -v
```

Esperado: todos PASS

- [ ] **Step 6: Commit**

```bash
git add src/auditor.py tests/test_auditor.py
git commit -m "feat(inova-daily): logar divergencia M2 vs vw_VENDAS no JSONL; tolerancia 0.05%"
```

---

## Task 3: Aviso condicional no email

**Files:**

- Modify: `templates/email_template_v3.md`
- Modify: `src/generator.py`
- Test: `tests/test_generator.py`

- [ ] **Step 1: Adicionar placeholder no template**

Em `templates/email_template_v3.md`, substituir a última linha:

```markdown
*Gerado automaticamente pelo Inova Daily em {{ hora_geracao }}*
```

Por:

```markdown
{{ aviso_divergencia }}*Gerado automaticamente pelo Inova Daily em {{ hora_geracao }}*
```

- [ ] **Step 2: Escrever os testes que falharão**

Verificar se `tests/test_generator.py` existe; se não, criar. Adicionar:

```python
import pytest
from datetime import date
from pathlib import Path
from unittest.mock import patch, MagicMock


def _snap_base() -> dict:
    from datetime import timedelta
    ontem = date(2026, 5, 14)
    return {
        "data_ontem": ontem,
        "total": 15_000.0,
        "nfs": 2,
        "top_vendedores": {"Joao": 10_000.0},
        "top_filiais": {"Contagem": 15_000.0},
        "acumulado_mes": 80_000.0,
        "meta_mes": 13_646_411.88,
        "pct_meta": 0.59,
        "dias_restantes": 10,
        "sply_pct": -5.0,
        "sply_total": 84_000.0,
        "sply_mes": 5,
        "sply_ano": 2025,
        "splm_pct": 3.0,
        "splm_total": 77_000.0,
        "splm_mes": 4,
        "splm_ano": 2026,
        "tendencia": "Estável →",
        "delta_tendencia": 1.2,
        "ritmo_atual": 8_000.0,
        "projecao_mes": 192_000.0,
        "projecao_pct": 1.4,
        "ritmo_necessario": 1_356_641.0,
        "m2_total": 15_000.0,
        "vw_total": 15_000.0,
        "divergencia_pct": 0.0,
    }


def test_aviso_divergencia_ausente_quando_dentro_da_tolerancia(tmp_path):
    snap = _snap_base()
    snap["divergencia_pct"] = 0.03  # abaixo do threshold de 0.05%

    with patch("src.generator.foto_ontem", return_value=snap), \
         patch("src.generator.highlight_mes", return_value=None), \
         patch("src.generator.OUTPUT_DIR", tmp_path):
        from src.generator import gerar_email
        path = gerar_email(data_ontem=date(2026, 5, 14))
        content = path.read_text(encoding="utf-8")

    assert "⚠️" not in content


def test_aviso_divergencia_presente_quando_acima_do_threshold(tmp_path):
    snap = _snap_base()
    snap["divergencia_pct"] = 1.5
    snap["vw_total"] = 15_225.0

    with patch("src.generator.foto_ontem", return_value=snap), \
         patch("src.generator.highlight_mes", return_value=None), \
         patch("src.generator.OUTPUT_DIR", tmp_path):
        from src.generator import gerar_email
        path = gerar_email(data_ontem=date(2026, 5, 14))
        content = path.read_text(encoding="utf-8")

    assert "⚠️" in content
    assert "1.5" in content
```

- [ ] **Step 3: Rodar para confirmar falha**

```bash
pytest tests/test_generator.py::test_aviso_divergencia_ausente_quando_dentro_da_tolerancia -v
```

Esperado: `FAILED` — `KeyError` ou placeholder `{{ aviso_divergencia }}` não substituído

- [ ] **Step 4: Implementar em `generator.py`**

Adicionar constante após os imports:

```python
_DIVERGENCIA_THRESHOLD_PCT = 0.05
```

Adicionar helper após `_anomalia_md()`:

```python
def _aviso_divergencia(divergencia_pct: float, vw_total: float) -> str:
    if divergencia_pct <= _DIVERGENCIA_THRESHOLD_PCT:
        return ""
    return (
        f"\n> ⚠️ M2 pode estar desatualizado — divergência de {divergencia_pct:.1f}% "
        f"em relação ao banco ao vivo (vw_VENDAS: R$ {_brl(vw_total)}).\n\n"
    )
```

Em `gerar_email()`, após a linha `content = content.replace("{{ hora_geracao }}", ...)`, adicionar:

```python
content = content.replace(
    "{{ aviso_divergencia }}",
    _aviso_divergencia(snap.get("divergencia_pct", 0.0), snap.get("vw_total", 0.0)),
)
```

- [ ] **Step 5: Rodar para confirmar aprovação**

```bash
pytest tests/test_generator.py -v
```

Esperado: todos PASS

- [ ] **Step 6: Commit**

```bash
git add templates/email_template_v3.md src/generator.py tests/test_generator.py
git commit -m "feat(inova-daily): aviso condicional de divergencia M2 vs vw_VENDAS no email"
```

---

## Task 4: Integrar no `run_daily.py`

**Files:**

- Modify: `run_daily.py`

- [ ] **Step 1: Localizar chamada de `registrar_execucao` em `run_daily.py`**

```bash
grep -n "registrar_execucao" run_daily.py
```

- [ ] **Step 2: Passar campos de divergência**

Onde `registrar_execucao(snap_result, recap_result, ...)` é chamado, adicionar os novos kwargs:

```python
registrar_execucao(
    snap_result,
    recap_result,
    m2_total=snap.get("m2_total"),
    vw_total=snap.get("vw_total"),
    divergencia_pct=snap.get("divergencia_pct"),
)
```

- [ ] **Step 3: Rodar suite completa**

```bash
pytest -v
```

Esperado: todos PASS (79 testes anteriores + novos)

- [ ] **Step 4: Commit final**

```bash
git add run_daily.py
git commit -m "feat(inova-daily): integrar divergencia M2 vs vw_VENDAS no run_daily"
```
