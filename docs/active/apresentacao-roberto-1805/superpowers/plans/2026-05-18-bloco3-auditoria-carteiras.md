# Bloco 3 — Auditoria de Carteiras: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar `bloco3.md` e `bloco3.json` com visão geral de consultores, top 3 grupos por consultor e auditoria de migração de carteiras (Wenderson→Danilo Neto, Eliane→Danillo Bermudes/Vinicius Lenzi).

**Architecture:** Script independente `src/bloco3.py` que lê `Vendas_2025.xlsx` e `Vendas_2026.xlsx` por índice posicional, agrega em 3 dimensões e emite Markdown narrativo + JSON estruturado.

**Tech Stack:** Python 3, pandas, openpyxl, pytest

---

## File Structure

- Create: `src/bloco3.py`
- Create: `tests/test_bloco3.py`
- Generate (runtime): `bloco3.md`, `bloco3.json`

---

### Task 1: Esqueleto do script + load_and_clean

**Files:**

- Create: `src/bloco3.py`
- Create: `tests/test_bloco3.py`

- [ ] **Step 1: Escrever os testes de load_and_clean**

```python
# tests/test_bloco3.py
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from bloco3 import load_and_clean, _var_pct


def _make_df(rows):
    """Cria DataFrame com schema posicional (21 colunas) igual ao Excel real."""
    cols = list(range(21))
    data = []
    for r in rows:
        row = [None] * 21
        row[4] = r.get('nf')       # nf
        row[9] = r.get('consultor')
        row[10] = r.get('cod_cliente', 0)
        row[14] = r.get('liquido', 0.0)
        row[2] = r.get('grupo', '')
        data.append(row)
    return pd.DataFrame(data, columns=cols)


def test_load_and_clean_title_case(tmp_path):
    df = _make_df([
        {'nf': 'NF001', 'consultor': 'ANDRE BESSAS', 'cod_cliente': 1, 'liquido': 100.0},
    ])
    xlsx = tmp_path / 'test.xlsx'
    df.to_excel(xlsx, index=False)
    result = load_and_clean(str(xlsx))
    assert result['consultor'].iloc[0] == 'Andre Bessas'


def test_load_and_clean_filtra_totalizacao(tmp_path):
    df = _make_df([
        {'nf': 'NF001', 'consultor': 'ANDRE BESSAS', 'cod_cliente': 1, 'liquido': 100.0},
        {'nf': None,    'consultor': 'TOTAL',         'cod_cliente': 0, 'liquido': 999.0},
    ])
    xlsx = tmp_path / 'test.xlsx'
    df.to_excel(xlsx, index=False)
    result = load_and_clean(str(xlsx))
    assert len(result) == 1
    assert result['liquido'].sum() == 100.0


def test_load_and_clean_grupo_vazio_vira_outros(tmp_path):
    df = _make_df([
        {'nf': 'NF001', 'consultor': 'X', 'cod_cliente': 1, 'liquido': 50.0, 'grupo': ''},
        {'nf': 'NF002', 'consultor': 'X', 'cod_cliente': 2, 'liquido': 50.0, 'grupo': None},
    ])
    xlsx = tmp_path / 'test.xlsx'
    df.to_excel(xlsx, index=False)
    result = load_and_clean(str(xlsx))
    assert (result['grupo'] == 'OUTROS').all()


def test_var_pct_positivo():
    assert _var_pct(100.0, 150.0) == 50.0


def test_var_pct_negativo():
    assert _var_pct(100.0, 70.0) == -30.0


def test_var_pct_zero_base():
    assert _var_pct(0.0, 500.0) == 0.0
```

- [ ] **Step 2: Rodar testes — devem FALHAR (módulo não existe)**

```
pytest tests/test_bloco3.py -v
```

Esperado: `ModuleNotFoundError: No module named 'bloco3'`

- [ ] **Step 3: Criar src/bloco3.py com load_and_clean e _var_pct**

```python
# src/bloco3.py
import pandas as pd
import json
from pathlib import Path

_CONSULTORES_EXCLUIDOS = {'Samara Souza'}

_MIGRACOES = [
    {'legado': 'Wenderson Silva', 'herdeiros': ['Danilo Neto']},
    {'legado': 'Eliane Gils', 'herdeiros': ['Danillo Bermudes', 'Vinicius Lenzi']},
]


def load_and_clean(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    df.columns = list(range(len(df.columns)))
    df = df.rename(columns={
        4: 'nf',
        9: 'consultor',
        10: 'cod_cliente',
        14: 'liquido',
        2: 'grupo',
    })
    df = df[df['nf'].notna()].copy()
    df['consultor'] = df['consultor'].fillna('SEM CONSULTOR').astype(str).str.strip().str.title()
    df['cod_cliente'] = df['cod_cliente'].fillna(0)
    df['liquido'] = pd.to_numeric(df['liquido'], errors='coerce').fillna(0)
    df['grupo'] = df['grupo'].fillna('OUTROS').astype(str).str.strip().str.upper()
    df.loc[df['grupo'] == '', 'grupo'] = 'OUTROS'
    return df[['nf', 'consultor', 'cod_cliente', 'liquido', 'grupo']]


def _var_pct(a: float, b: float) -> float:
    if a == 0:
        return 0.0
    return round((b - a) / a * 100, 2)
```

- [ ] **Step 4: Rodar testes — devem PASSAR**

```
pytest tests/test_bloco3.py::test_load_and_clean_title_case tests/test_bloco3.py::test_load_and_clean_filtra_totalizacao tests/test_bloco3.py::test_load_and_clean_grupo_vazio_vira_outros tests/test_bloco3.py::test_var_pct_positivo tests/test_bloco3.py::test_var_pct_negativo tests/test_bloco3.py::test_var_pct_zero_base -v
```

Esperado: 6 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/bloco3.py tests/test_bloco3.py
git commit -m "feat(bloco3): esqueleto + load_and_clean + _var_pct com testes"
```

---

### Task 2: aggregate_consultores

**Files:**

- Modify: `src/bloco3.py`
- Modify: `tests/test_bloco3.py`

- [ ] **Step 1: Escrever testes de aggregate_consultores**

Adicionar em `tests/test_bloco3.py`:

```python
from bloco3 import aggregate_consultores


def _make_clean_df(rows):
    """DataFrame já no formato pós load_and_clean."""
    return pd.DataFrame(rows, columns=['nf', 'consultor', 'cod_cliente', 'liquido', 'grupo'])


def test_aggregate_consultores_structure():
    df25 = _make_clean_df([
        {'nf': 'A', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 1000.0, 'grupo': 'FILTROS'},
    ])
    df26 = _make_clean_df([
        {'nf': 'B', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 1500.0, 'grupo': 'FILTROS'},
        {'nf': 'C', 'consultor': 'Andre Bessas', 'cod_cliente': 2, 'liquido': 500.0,  'grupo': 'OUTROS'},
    ])
    result = aggregate_consultores(df25, df26)
    assert len(result) == 1
    r = result[0]
    assert set(r.keys()) == {'consultor', 'fat_2025', 'fat_2026', 'var_pct', 'n_clientes_2026', 'ticket_medio_2026', 'share_2026'}
    assert r['fat_2025'] == 1000.0
    assert r['fat_2026'] == 2000.0
    assert r['var_pct'] == 100.0
    assert r['n_clientes_2026'] == 2
    assert r['ticket_medio_2026'] == 1000.0  # 2000/2 NFs
    assert r['share_2026'] == 100.0


def test_aggregate_consultores_exclui_samara():
    df25 = _make_clean_df([])
    df26 = _make_clean_df([
        {'nf': 'A', 'consultor': 'Samara Souza', 'cod_cliente': 1, 'liquido': 5000.0, 'grupo': 'OUTROS'},
        {'nf': 'B', 'consultor': 'Andre Bessas',  'cod_cliente': 2, 'liquido': 1000.0, 'grupo': 'FILTROS'},
    ])
    result = aggregate_consultores(df25, df26)
    nomes = [r['consultor'] for r in result]
    assert 'Samara Souza' not in nomes
    assert 'Andre Bessas' in nomes


def test_aggregate_consultores_exclui_desligados():
    df25 = _make_clean_df([
        {'nf': 'A', 'consultor': 'Ex Consultor', 'cod_cliente': 1, 'liquido': 500.0, 'grupo': 'FILTROS'},
    ])
    df26 = _make_clean_df([
        {'nf': 'B', 'consultor': 'Andre Bessas', 'cod_cliente': 2, 'liquido': 1000.0, 'grupo': 'FILTROS'},
    ])
    result = aggregate_consultores(df25, df26)
    nomes = [r['consultor'] for r in result]
    assert 'Ex Consultor' not in nomes
```

- [ ] **Step 2: Rodar testes — devem FALHAR**

```
pytest tests/test_bloco3.py::test_aggregate_consultores_structure tests/test_bloco3.py::test_aggregate_consultores_exclui_samara tests/test_bloco3.py::test_aggregate_consultores_exclui_desligados -v
```

Esperado: `ImportError` ou `AttributeError`

- [ ] **Step 3: Implementar aggregate_consultores em src/bloco3.py**

```python
def aggregate_consultores(df25: pd.DataFrame, df26: pd.DataFrame) -> list:
    total_26 = df26['liquido'].sum()
    consultores = sorted(set(df25['consultor'].unique()) | set(df26['consultor'].unique()))
    result = []
    for consultor in consultores:
        if consultor in _CONSULTORES_EXCLUIDOS:
            continue
        f26 = df26[df26['consultor'] == consultor]['liquido'].sum()
        if f26 == 0:
            continue
        f25 = df25[df25['consultor'] == consultor]['liquido'].sum()
        clientes_26 = df26[df26['consultor'] == consultor]['cod_cliente'].nunique()
        nfs_26 = len(df26[df26['consultor'] == consultor])
        ticket_26 = round(f26 / nfs_26, 2) if nfs_26 > 0 else 0.0
        result.append({
            'consultor': consultor,
            'fat_2025': round(f25, 2),
            'fat_2026': round(f26, 2),
            'var_pct': _var_pct(f25, f26),
            'n_clientes_2026': int(clientes_26),
            'ticket_medio_2026': ticket_26,
            'share_2026': round(f26 / total_26 * 100, 2) if total_26 else 0.0,
        })
    return sorted(result, key=lambda x: x['fat_2026'], reverse=True)
```

- [ ] **Step 4: Rodar testes — devem PASSAR**

```
pytest tests/test_bloco3.py -v
```

Esperado: todos PASSED

- [ ] **Step 5: Commit**

```bash
git add src/bloco3.py tests/test_bloco3.py
git commit -m "feat(bloco3): aggregate_consultores com testes"
```

---

### Task 3: aggregate_grupos_por_consultor

**Files:**

- Modify: `src/bloco3.py`
- Modify: `tests/test_bloco3.py`

- [ ] **Step 1: Escrever teste**

Adicionar em `tests/test_bloco3.py`:

```python
from bloco3 import aggregate_grupos_por_consultor


def test_aggregate_grupos_por_consultor_top3():
    df25 = _make_clean_df([
        {'nf': 'A', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 200.0, 'grupo': 'FILTROS'},
        {'nf': 'B', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 100.0, 'grupo': 'LUBRIFICANTE'},
    ])
    df26 = _make_clean_df([
        {'nf': 'C', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 300.0, 'grupo': 'FILTROS'},
        {'nf': 'D', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 150.0, 'grupo': 'LUBRIFICANTE'},
        {'nf': 'E', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 80.0,  'grupo': 'RODANTE'},
        {'nf': 'F', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 50.0,  'grupo': 'BATERIA'},
    ])
    result = aggregate_grupos_por_consultor(df25, df26)
    assert len(result) == 1
    r = result[0]
    assert r['consultor'] == 'Andre Bessas'
    assert len(r['top3']) <= 3
    grupos = [g['grupo'] for g in r['top3']]
    assert grupos[0] == 'FILTROS'   # maior fat_2026
    assert grupos[1] == 'LUBRIFICANTE'
    for g in r['top3']:
        assert set(g.keys()) == {'grupo', 'fat_2025', 'fat_2026', 'var_pct'}
```

- [ ] **Step 2: Rodar teste — deve FALHAR**

```
pytest tests/test_bloco3.py::test_aggregate_grupos_por_consultor_top3 -v
```

- [ ] **Step 3: Implementar aggregate_grupos_por_consultor**

```python
def aggregate_grupos_por_consultor(df25: pd.DataFrame, df26: pd.DataFrame) -> list:
    consultores_ativos = [
        c for c in df26['consultor'].unique()
        if c not in _CONSULTORES_EXCLUIDOS and df26[df26['consultor'] == c]['liquido'].sum() > 0
    ]
    result = []
    for consultor in sorted(consultores_ativos):
        c25 = df25[df25['consultor'] == consultor]
        c26 = df26[df26['consultor'] == consultor]
        grupos = sorted(set(c25['grupo'].unique()) | set(c26['grupo'].unique()))
        grupo_data = []
        for grupo in grupos:
            f26 = c26[c26['grupo'] == grupo]['liquido'].sum()
            if f26 == 0:
                continue
            f25 = c25[c25['grupo'] == grupo]['liquido'].sum()
            grupo_data.append({
                'grupo': grupo,
                'fat_2025': round(f25, 2),
                'fat_2026': round(f26, 2),
                'var_pct': _var_pct(f25, f26),
            })
        grupo_data.sort(key=lambda x: x['fat_2026'], reverse=True)
        result.append({'consultor': consultor, 'top3': grupo_data[:3]})
    return result
```

- [ ] **Step 4: Rodar testes — devem PASSAR**

```
pytest tests/test_bloco3.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/bloco3.py tests/test_bloco3.py
git commit -m "feat(bloco3): aggregate_grupos_por_consultor com testes"
```

---

### Task 4: aggregate_migracao

**Files:**

- Modify: `src/bloco3.py`
- Modify: `tests/test_bloco3.py`

- [ ] **Step 1: Escrever teste**

Adicionar em `tests/test_bloco3.py`:

```python
from bloco3 import aggregate_migracao


def test_aggregate_migracao_structure():
    df25 = _make_clean_df([
        {'nf': 'A', 'consultor': 'Wenderson Silva', 'cod_cliente': 10, 'liquido': 500.0, 'grupo': 'FILTROS'},
        {'nf': 'B', 'consultor': 'Wenderson Silva', 'cod_cliente': 20, 'liquido': 300.0, 'grupo': 'FILTROS'},
        {'nf': 'C', 'consultor': 'Wenderson Silva', 'cod_cliente': 30, 'liquido': 200.0, 'grupo': 'FILTROS'},
    ])
    df26 = _make_clean_df([
        {'nf': 'D', 'consultor': 'Danilo Neto',   'cod_cliente': 10, 'liquido': 600.0, 'grupo': 'FILTROS'},  # herdado
        {'nf': 'E', 'consultor': 'Outro Consultor', 'cod_cliente': 20, 'liquido': 400.0, 'grupo': 'FILTROS'},  # disperso
        # cliente 30 sumiu → churn
    ])
    migracoes_test = [{'legado': 'Wenderson Silva', 'herdeiros': ['Danilo Neto']}]
    result = aggregate_migracao(df25, df26, migracoes_test)
    assert len(result) == 1
    r = result[0]
    expected_keys = {'legado', 'herdeiros', 'fat_legado_2025', 'fat_herdado_2026', 'fat_disperso_2026',
                     'n_clientes_legado', 'n_clientes_herdado', 'n_clientes_disperso', 'n_clientes_churn'}
    assert set(r.keys()) == expected_keys
    assert r['n_clientes_legado'] == 3
    assert r['n_clientes_herdado'] == 1
    assert r['n_clientes_disperso'] == 1
    assert r['n_clientes_churn'] == 1
    assert r['n_clientes_herdado'] + r['n_clientes_disperso'] + r['n_clientes_churn'] == r['n_clientes_legado']
    assert r['fat_legado_2025'] == 1000.0
    assert r['fat_herdado_2026'] == 600.0
    assert r['fat_disperso_2026'] == 400.0
```

- [ ] **Step 2: Rodar teste — deve FALHAR**

```
pytest tests/test_bloco3.py::test_aggregate_migracao_structure -v
```

- [ ] **Step 3: Implementar aggregate_migracao**

```python
def aggregate_migracao(df25: pd.DataFrame, df26: pd.DataFrame, migracoes: list = None) -> list:
    if migracoes is None:
        migracoes = _MIGRACOES
    result = []
    for m in migracoes:
        legado = m['legado']
        herdeiros = m['herdeiros']
        clientes_legado = set(df25[df25['consultor'] == legado]['cod_cliente'].unique())
        fat_legado_2025 = df25[df25['consultor'] == legado]['liquido'].sum()

        herdado_clientes = set()
        disperso_clientes = set()
        fat_herdado = 0.0
        fat_disperso = 0.0

        for cliente in clientes_legado:
            rows_26 = df26[df26['cod_cliente'] == cliente]
            if rows_26.empty:
                continue
            consultores_26 = set(rows_26['consultor'].unique())
            if consultores_26 & set(herdeiros):
                herdado_clientes.add(cliente)
                fat_herdado += rows_26[rows_26['consultor'].isin(herdeiros)]['liquido'].sum()
            else:
                disperso_clientes.add(cliente)
                fat_disperso += rows_26['liquido'].sum()

        n_churn = len(clientes_legado) - len(herdado_clientes) - len(disperso_clientes)
        result.append({
            'legado': legado,
            'herdeiros': herdeiros,
            'fat_legado_2025': round(fat_legado_2025, 2),
            'fat_herdado_2026': round(fat_herdado, 2),
            'fat_disperso_2026': round(fat_disperso, 2),
            'n_clientes_legado': len(clientes_legado),
            'n_clientes_herdado': len(herdado_clientes),
            'n_clientes_disperso': len(disperso_clientes),
            'n_clientes_churn': n_churn,
        })
    return result
```

- [ ] **Step 4: Rodar testes — devem PASSAR**

```
pytest tests/test_bloco3.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/bloco3.py tests/test_bloco3.py
git commit -m "feat(bloco3): aggregate_migracao com testes"
```

---

### Task 5: render_markdown + render_json + main + testes de render

**Files:**

- Modify: `src/bloco3.py`
- Modify: `tests/test_bloco3.py`

- [ ] **Step 1: Escrever testes de render**

Adicionar em `tests/test_bloco3.py`:

```python
from bloco3 import aggregate, render_markdown, render_json


def _build_agg():
    df25 = _make_clean_df([
        {'nf': 'A', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 1000.0, 'grupo': 'FILTROS'},
        {'nf': 'B', 'consultor': 'Wenderson Silva', 'cod_cliente': 10, 'liquido': 500.0, 'grupo': 'FILTROS'},
    ])
    df26 = _make_clean_df([
        {'nf': 'C', 'consultor': 'Andre Bessas', 'cod_cliente': 1, 'liquido': 1500.0, 'grupo': 'FILTROS'},
        {'nf': 'D', 'consultor': 'Danilo Neto', 'cod_cliente': 10, 'liquido': 600.0, 'grupo': 'FILTROS'},
    ])
    return aggregate(df25, df26)


def test_render_markdown_sections():
    agg = _build_agg()
    md = render_markdown(agg, 'Jan-Abr 2025 vs Jan-Abr 2026')
    assert '## Visão Geral de Consultores' in md
    assert '## Top 3 Grupos por Consultor' in md
    assert '## Auditoria de Migração de Carteiras' in md


def test_render_json_structure():
    agg = _build_agg()
    js = render_json(agg, 'Jan-Abr 2025 vs Jan-Abr 2026')
    import json
    data = json.loads(js)
    assert 'consultores' in data
    assert 'grupos_por_consultor' in data
    assert 'migracao' in data
    assert data['periodo'] == 'Jan-Abr 2025 vs Jan-Abr 2026'
```

- [ ] **Step 2: Rodar testes — devem FALHAR**

```
pytest tests/test_bloco3.py::test_render_markdown_sections tests/test_bloco3.py::test_render_json_structure -v
```

- [ ] **Step 3: Implementar aggregate + _fmt + render_markdown + render_json + main**

```python
def aggregate(df25: pd.DataFrame, df26: pd.DataFrame) -> dict:
    return {
        'consultores': aggregate_consultores(df25, df26),
        'grupos_por_consultor': aggregate_grupos_por_consultor(df25, df26),
        'migracao': aggregate_migracao(df25, df26),
    }


def _fmt(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_markdown(agg: dict, periodo: str) -> str:
    linhas = []
    linhas.append("# Bloco 3 — Auditoria de Carteiras")
    linhas.append(f"\n**Período:** {periodo}\n")
    linhas.append("---\n")

    # Visão Geral de Consultores
    linhas.append("## Visão Geral de Consultores\n")
    for c in agg['consultores']:
        sinal = '+' if c['var_pct'] >= 0 else ''
        linhas.append(
            f"**{c['consultor']}**: {_fmt(c['fat_2026'])} em 2026 vs {_fmt(c['fat_2025'])} em 2025 "
            f"({sinal}{c['var_pct']:.1f}%). Atendeu {c['n_clientes_2026']} clientes com ticket médio de "
            f"{_fmt(c['ticket_medio_2026'])} por NF. Representa {c['share_2026']:.1f}% do faturamento total.\n"
        )
    if agg['consultores']:
        maior_fat = max(agg['consultores'], key=lambda x: x['fat_2026'])
        maior_ticket = max(agg['consultores'], key=lambda x: x['ticket_medio_2026'])
        mais_clientes = max(agg['consultores'], key=lambda x: x['n_clientes_2026'])
        linhas.append(f"*Consultor de maior faturamento:* {maior_fat['consultor']} ({_fmt(maior_fat['fat_2026'])})")
        linhas.append(f"*Maior ticket médio:* {maior_ticket['consultor']} ({_fmt(maior_ticket['ticket_medio_2026'])} por NF)")
        linhas.append(f"*Mais clientes atendidos:* {mais_clientes['consultor']} ({mais_clientes['n_clientes_2026']} clientes)")

    linhas.append("\n---\n")

    # Top 3 Grupos por Consultor
    linhas.append("## Top 3 Grupos por Consultor\n")
    for c in agg['grupos_por_consultor']:
        if not c['top3']:
            continue
        grupos_txt = ', '.join(
            f"{g['grupo']} ({_fmt(g['fat_2026'])}, {'+' if g['var_pct'] >= 0 else ''}{g['var_pct']:.1f}%)"
            for g in c['top3']
        )
        linhas.append(f"**{c['consultor']}**: {grupos_txt}\n")

    linhas.append("---\n")

    # Auditoria de Migração de Carteiras
    linhas.append("## Auditoria de Migração de Carteiras\n")
    for m in agg['migracao']:
        herdeiros_str = ' e '.join(m['herdeiros'])
        linhas.append(
            f"**{m['legado']} → {herdeiros_str}**: Carteira de {m['n_clientes_legado']} clientes em 2025 "
            f"({_fmt(m['fat_legado_2025'])}). Em 2026: {m['n_clientes_herdado']} clientes migraram para {herdeiros_str} "
            f"({_fmt(m['fat_herdado_2026'])}), {m['n_clientes_disperso']} foram para outros consultores "
            f"({_fmt(m['fat_disperso_2026'])}), {m['n_clientes_churn']} não compraram (churn).\n"
        )

    return "\n".join(linhas)


def render_json(agg: dict, periodo: str) -> str:
    data = {'periodo': periodo}
    data.update(agg)
    return json.dumps(data, ensure_ascii=False, indent=2)


def main() -> None:
    root = Path(__file__).parents[1]
    df25 = load_and_clean(str(root / 'Vendas_2025.xlsx'))
    df26 = load_and_clean(str(root / 'Vendas_2026.xlsx'))

    periodo = 'Jan-Abr 2025 vs Jan-Abr 2026'
    agg = aggregate(df25, df26)

    md_path = root / 'bloco3.md'
    json_path = root / 'bloco3.json'

    md_path.write_text(render_markdown(agg, periodo), encoding='utf-8')
    json_path.write_text(render_json(agg, periodo), encoding='utf-8')

    print(f"OK bloco3.md gerado: {md_path}")
    print(f"OK bloco3.json gerado: {json_path}")


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Rodar todos os testes — devem PASSAR**

```
pytest tests/test_bloco3.py -v
```

Esperado: todos os testes PASSED (mínimo 9)

- [ ] **Step 5: Rodar o script com os dados reais**

```
python src/bloco3.py
```

Esperado: `OK bloco3.md gerado` e `OK bloco3.json gerado`

- [ ] **Step 6: Verificar bloco3.md gerado**

Confirmar que contém:

- Seção `## Visão Geral de Consultores` com nomes em Title Case
- Seção `## Top 3 Grupos por Consultor`
- Seção `## Auditoria de Migração de Carteiras` com Wenderson Silva e Eliane Gils

- [ ] **Step 7: Commit**

```bash
git add src/bloco3.py tests/test_bloco3.py bloco3.md bloco3.json
git commit -m "feat(bloco3): render_markdown + render_json + main — bloco3 completo"
```
