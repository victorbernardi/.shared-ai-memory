# Bloco 2 — Eficiência Operacional: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar `bloco2.md` (prosa narrativa) e `bloco2.json` (estruturado para PPT) com faturamento por filial, métricas de eficiência por consultor e por filial, e mix de grupos de peças — comparativo Jan-Abr 2025 vs Jan-Abr 2026.

**Architecture:** Script `src/bloco2.py` independente, seguindo o mesmo padrão do `src/bloco1.py`. Lê `Vendas_2025.xlsx` e `Vendas_2026.xlsx` por índice posicional de coluna, filtra linhas de totalização via `nf.notna()`, agrega em três dimensões (filiais, consultores, grupos) e renderiza em Markdown narrativo + JSON.

**Tech Stack:** Python 3.x, pandas, openpyxl, json, pathlib, pytest

---

## File Structure

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `src/bloco2.py` | Criar | Pipeline completo: load → aggregate → render |
| `tests/test_bloco2.py` | Criar | 6 testes cobrindo todas as funções |
| `bloco2.md` | Gerado por `main()` | Saída narrativa |
| `bloco2.json` | Gerado por `main()` | Saída estruturada |

**Colunas do Excel (índice posicional):**

| Índice | Nome | Uso |
|---|---|---|
| 4 | `nf` | filtro anti-totalização |
| 5 | `filial` | breakdown por loja |
| 2 | `grupo` | mix de peças |
| 9 | `consultor` | clientes e ticket médio |
| 10 | `cod_cliente` | contagem de clientes distintos |
| 14 | `liquido` | valor líquido |

---

## Task 1: load_and_clean + _var_pct

**Files:**

- Create: `src/bloco2.py`
- Create: `tests/test_bloco2.py`

- [ ] **Step 1: Criar arquivo de teste com helper e primeiro teste**

```python
# tests/test_bloco2.py
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from bloco2 import load_and_clean, _var_pct


def _make_df(**kwargs):
    defaults = {
        'nf':         ['NF001', 'NF002', 'NF003'],
        'filial':     ['0201 - Contagem', '0201 - Contagem', '0212 - CSN'],
        'grupo':      ['FILTROS', 'LUBRIFICANTE', 'FILTROS'],
        'consultor':  ['Ana Silva', 'Ana Silva', 'Bruno Costa'],
        'cod_cliente': [1001, 1002, 1001],
        'liquido':    [1000.0, 500.0, 2000.0],
    }
    defaults.update(kwargs)
    return pd.DataFrame(defaults)


def test_var_pct_positivo():
    assert _var_pct(100.0, 110.0) == 10.0

def test_var_pct_negativo():
    assert _var_pct(100.0, 90.0) == -10.0

def test_var_pct_zero_base():
    assert _var_pct(0.0, 100.0) == 0.0
```

- [ ] **Step 2: Rodar teste para verificar FAIL**

```
pytest tests/test_bloco2.py -v
```

Expected: `ImportError: No module named 'bloco2'`

- [ ] **Step 3: Criar `src/bloco2.py` com `load_and_clean` e `_var_pct`**

```python
# src/bloco2.py
import pandas as pd
import json
from pathlib import Path


def load_and_clean(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    df.columns = list(range(len(df.columns)))
    df = df.rename(columns={
        4: 'nf',
        5: 'filial',
        2: 'grupo',
        9: 'consultor',
        10: 'cod_cliente',
        14: 'liquido',
    })
    df = df[df['nf'].notna()].copy()
    df['filial'] = df['filial'].fillna('').astype(str).str.strip()
    df['grupo'] = df['grupo'].fillna('OUTROS').astype(str).str.strip().str.upper()
    df['consultor'] = df['consultor'].fillna('SEM CONSULTOR').astype(str).str.strip()
    df['cod_cliente'] = df['cod_cliente'].fillna(0)
    df['liquido'] = pd.to_numeric(df['liquido'], errors='coerce').fillna(0)
    return df[['nf', 'filial', 'grupo', 'consultor', 'cod_cliente', 'liquido']]


def _var_pct(a: float, b: float) -> float:
    if a == 0:
        return 0.0
    return round((b - a) / a * 100, 2)
```

- [ ] **Step 4: Rodar testes para verificar PASS**

```
pytest tests/test_bloco2.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/bloco2.py tests/test_bloco2.py
git commit -m "feat(bloco2): load_and_clean + _var_pct"
```

---

## Task 2: aggregate_filiais

**Files:**

- Modify: `src/bloco2.py`
- Modify: `tests/test_bloco2.py`

- [ ] **Step 1: Adicionar teste de agregação por filial**

Adicionar ao final de `tests/test_bloco2.py`:

```python
from bloco2 import aggregate_filiais


def test_aggregate_filiais_structure():
    df25 = _make_df()
    df26 = _make_df(liquido=[1200.0, 600.0, 2200.0])

    result = aggregate_filiais(df25, df26)

    assert isinstance(result, list)
    assert len(result) == 2  # 0201 - Contagem e 0212 - CSN

    contagem = next(r for r in result if '0201' in r['filial'])
    assert contagem['marca'] == 'John Deere'
    assert contagem['fat_2025'] == 1500.0   # 1000 + 500
    assert contagem['fat_2026'] == 1800.0   # 1200 + 600
    assert contagem['var_pct'] == 20.0
    assert contagem['n_clientes_2026'] == 2  # cod_cliente 1001 e 1002
    assert contagem['ticket_medio_2026'] == 900.0  # 1800 / 2 NFs

    csn = next(r for r in result if '0212' in r['filial'])
    assert csn['fat_2026'] == 2200.0
    assert csn['share_2026'] > 0


def test_aggregate_filiais_wirtgen_marca():
    df25 = _make_df(filial=['0301 - Contagem', '0301 - Contagem', '0301 - Contagem'])
    df26 = _make_df(filial=['0301 - Contagem', '0301 - Contagem', '0301 - Contagem'])

    result = aggregate_filiais(df25, df26)
    assert result[0]['marca'] == 'Wirtgen'
```

- [ ] **Step 2: Rodar teste para verificar FAIL**

```
pytest tests/test_bloco2.py::test_aggregate_filiais_structure -v
```

Expected: `ImportError` ou `AttributeError`

- [ ] **Step 3: Implementar `aggregate_filiais` em `src/bloco2.py`**

Adicionar após `_var_pct`:

```python
def aggregate_filiais(df25: pd.DataFrame, df26: pd.DataFrame) -> list:
    total_26 = df26['liquido'].sum()
    filiais = sorted(set(df25['filial'].unique()) | set(df26['filial'].unique()))
    result = []
    for filial in filiais:
        if not filial:
            continue
        f25 = df25[df25['filial'] == filial]['liquido'].sum()
        f26 = df26[df26['filial'] == filial]['liquido'].sum()
        if f25 == 0 and f26 == 0:
            continue
        clientes_26 = df26[df26['filial'] == filial]['cod_cliente'].nunique()
        nfs_26 = len(df26[df26['filial'] == filial])
        ticket_26 = round(f26 / nfs_26, 2) if nfs_26 > 0 else 0.0
        marca = 'Wirtgen' if filial.startswith('03') else 'John Deere'
        result.append({
            'filial': filial,
            'marca': marca,
            'fat_2025': round(f25, 2),
            'fat_2026': round(f26, 2),
            'var_pct': _var_pct(f25, f26),
            'share_2026': round(f26 / total_26 * 100, 2) if total_26 else 0.0,
            'n_clientes_2026': int(clientes_26),
            'ticket_medio_2026': ticket_26,
        })
    return sorted(result, key=lambda x: x['fat_2026'], reverse=True)
```

- [ ] **Step 4: Rodar testes**

```
pytest tests/test_bloco2.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/bloco2.py tests/test_bloco2.py
git commit -m "feat(bloco2): aggregate_filiais"
```

---

## Task 3: aggregate_consultores

**Files:**

- Modify: `src/bloco2.py`
- Modify: `tests/test_bloco2.py`

- [ ] **Step 1: Adicionar teste de agregação por consultor**

Adicionar ao final de `tests/test_bloco2.py`:

```python
from bloco2 import aggregate_consultores


def test_aggregate_consultores_ticket_medio():
    df25 = _make_df()
    # df26: Ana tem 2 NFs com liquido [1200, 600] = 1800, Bruno tem 1 NF com 2200
    df26 = _make_df(liquido=[1200.0, 600.0, 2200.0])

    result = aggregate_consultores(df25, df26)

    assert isinstance(result, list)
    # ordenado por fat_2026 desc: Bruno (2200) > Ana (1800)
    assert result[0]['consultor'] == 'Bruno Costa'

    ana = next(r for r in result if r['consultor'] == 'Ana Silva')
    assert ana['fat_2025'] == 1500.0   # 1000 + 500
    assert ana['fat_2026'] == 1800.0   # 1200 + 600
    assert ana['n_clientes_2026'] == 2  # cod_cliente 1001 e 1002
    assert ana['ticket_medio_2026'] == 900.0  # 1800 / 2 NFs

    bruno = next(r for r in result if r['consultor'] == 'Bruno Costa')
    assert bruno['ticket_medio_2026'] == 2200.0  # 2200 / 1 NF
    assert bruno['n_clientes_2026'] == 1
```

- [ ] **Step 2: Rodar teste para verificar FAIL**

```
pytest tests/test_bloco2.py::test_aggregate_consultores_ticket_medio -v
```

Expected: `ImportError`

- [ ] **Step 3: Implementar `aggregate_consultores` em `src/bloco2.py`**

Adicionar após `aggregate_filiais`:

```python
def aggregate_consultores(df25: pd.DataFrame, df26: pd.DataFrame) -> list:
    consultores = sorted(set(df25['consultor'].unique()) | set(df26['consultor'].unique()))
    result = []
    for consultor in consultores:
        f25 = df25[df25['consultor'] == consultor]['liquido'].sum()
        f26 = df26[df26['consultor'] == consultor]['liquido'].sum()
        if f25 == 0 and f26 == 0:
            continue
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
        })
    return sorted(result, key=lambda x: x['fat_2026'], reverse=True)
```

- [ ] **Step 4: Rodar testes**

```
pytest tests/test_bloco2.py -v
```

Expected: `6 passed`

- [ ] **Step 5: Commit**

```bash
git add src/bloco2.py tests/test_bloco2.py
git commit -m "feat(bloco2): aggregate_consultores"
```

---

## Task 4: aggregate_grupos + aggregate

**Files:**

- Modify: `src/bloco2.py`
- Modify: `tests/test_bloco2.py`

- [ ] **Step 1: Adicionar testes de grupos e aggregate**

Adicionar ao final de `tests/test_bloco2.py`:

```python
from bloco2 import aggregate_grupos, aggregate


def test_aggregate_grupos_structure():
    df25 = _make_df()
    df26 = _make_df(liquido=[1200.0, 600.0, 2200.0])

    result = aggregate_grupos(df25, df26)

    assert isinstance(result, list)
    # FILTROS: linhas 0 e 2 → fat_2026 = 1200 + 2200 = 3400
    # LUBRIFICANTE: linha 1 → fat_2026 = 600
    assert result[0]['grupo'] == 'FILTROS'
    assert result[0]['fat_2026'] == 3400.0
    assert result[0]['fat_2025'] == 3000.0  # 1000 + 2000

    total_share = sum(r['share_2026'] for r in result)
    assert abs(total_share - 100.0) < 0.1  # share soma ~100%


def test_aggregate_structure():
    df25 = _make_df()
    df26 = _make_df(liquido=[1200.0, 600.0, 2200.0])

    result = aggregate(df25, df26)

    assert 'filiais' in result
    assert 'consultores' in result
    assert 'grupos' in result
    assert isinstance(result['filiais'], list)
    assert isinstance(result['consultores'], list)
    assert isinstance(result['grupos'], list)
```

- [ ] **Step 2: Rodar testes para verificar FAIL**

```
pytest tests/test_bloco2.py::test_aggregate_grupos_structure -v
```

Expected: `ImportError`

- [ ] **Step 3: Implementar `aggregate_grupos` e `aggregate` em `src/bloco2.py`**

Adicionar após `aggregate_consultores`:

```python
def aggregate_grupos(df25: pd.DataFrame, df26: pd.DataFrame) -> list:
    total_26 = df26['liquido'].sum()
    grupos = sorted(set(df25['grupo'].unique()) | set(df26['grupo'].unique()))
    result = []
    for grupo in grupos:
        f25 = df25[df25['grupo'] == grupo]['liquido'].sum()
        f26 = df26[df26['grupo'] == grupo]['liquido'].sum()
        if f25 == 0 and f26 == 0:
            continue
        result.append({
            'grupo': grupo,
            'fat_2025': round(f25, 2),
            'fat_2026': round(f26, 2),
            'var_pct': _var_pct(f25, f26),
            'share_2026': round(f26 / total_26 * 100, 2) if total_26 else 0.0,
        })
    return sorted(result, key=lambda x: x['fat_2026'], reverse=True)


def aggregate(df25: pd.DataFrame, df26: pd.DataFrame) -> dict:
    return {
        'filiais': aggregate_filiais(df25, df26),
        'consultores': aggregate_consultores(df25, df26),
        'grupos': aggregate_grupos(df25, df26),
    }
```

- [ ] **Step 4: Rodar testes**

```
pytest tests/test_bloco2.py -v
```

Expected: `8 passed`

- [ ] **Step 5: Commit**

```bash
git add src/bloco2.py tests/test_bloco2.py
git commit -m "feat(bloco2): aggregate_grupos + aggregate"
```

---

## Task 5: render_markdown + render_json + main

**Files:**

- Modify: `src/bloco2.py`
- Modify: `tests/test_bloco2.py`

- [ ] **Step 1: Adicionar testes de render**

Adicionar ao final de `tests/test_bloco2.py`:

```python
from bloco2 import render_markdown, render_json


def test_render_markdown_sections():
    df25 = _make_df()
    df26 = _make_df(liquido=[1200.0, 600.0, 2200.0])
    agg = aggregate(df25, df26)
    periodo = 'Jan-Abr 2025 vs Jan-Abr 2026'

    md = render_markdown(agg, periodo)

    assert '# Bloco 2' in md
    assert '## Filiais' in md
    assert '## Consultores' in md
    assert '## Mix de Peças' in md
    assert 'Jan-Abr 2025 vs Jan-Abr 2026' in md
    assert 'R$' in md
    assert 'ticket médio' in md


def test_render_json_structure():
    df25 = _make_df()
    df26 = _make_df(liquido=[1200.0, 600.0, 2200.0])
    agg = aggregate(df25, df26)
    periodo = 'Jan-Abr 2025 vs Jan-Abr 2026'

    import json
    data = json.loads(render_json(agg, periodo))

    assert data['periodo'] == periodo
    assert 'filiais' in data
    assert 'consultores' in data
    assert 'grupos' in data
    assert len(data['filiais']) == 2
    # Verificar chaves de cada filial
    filial = data['filiais'][0]
    for key in ['filial', 'marca', 'fat_2025', 'fat_2026', 'var_pct', 'share_2026', 'n_clientes_2026', 'ticket_medio_2026']:
        assert key in filial, f"chave '{key}' ausente em filial"
    # Verificar chaves de consultor
    consultor = data['consultores'][0]
    for key in ['consultor', 'fat_2025', 'fat_2026', 'var_pct', 'n_clientes_2026', 'ticket_medio_2026']:
        assert key in consultor, f"chave '{key}' ausente em consultor"
```

- [ ] **Step 2: Rodar testes para verificar FAIL**

```
pytest tests/test_bloco2.py::test_render_markdown_sections -v
```

Expected: `ImportError`

- [ ] **Step 3: Implementar `_fmt`, `render_markdown`, `render_json` e `main` em `src/bloco2.py`**

Adicionar após `aggregate`:

```python
def _fmt(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_markdown(agg: dict, periodo: str) -> str:
    linhas = []
    linhas.append("# Bloco 2 — Eficiencia Operacional")
    linhas.append(f"\n**Periodo:** {periodo}\n")
    linhas.append("---\n")

    # Filiais
    linhas.append("## Filiais")
    for f in agg['filiais']:
        sinal = '+' if f['var_pct'] >= 0 else ''
        linhas.append(
            f"\n**{f['filial']}** ({f['marca']}): {_fmt(f['fat_2026'])} em 2026 vs {_fmt(f['fat_2025'])} em 2025 "
            f"({sinal}{f['var_pct']:.1f}%). Representa {f['share_2026']:.1f}% do faturamento total. "
            f"Atendeu {f['n_clientes_2026']} clientes distintos com ticket medio de {_fmt(f['ticket_medio_2026'])} por NF."
        )
    if agg['filiais']:
        maior_alta = max(agg['filiais'], key=lambda x: x['var_pct'])
        maior_queda = min(agg['filiais'], key=lambda x: x['var_pct'])
        maior_share = max(agg['filiais'], key=lambda x: x['share_2026'])
        linhas.append(f"\n*Filial de maior crescimento:* {maior_alta['filial']} (+{maior_alta['var_pct']:.1f}%)")
        if maior_queda['var_pct'] < 0:
            linhas.append(f"*Filial de maior queda:* {maior_queda['filial']} ({maior_queda['var_pct']:.1f}%)")
        linhas.append(f"*Filial dominante:* {maior_share['filial']} com {maior_share['share_2026']:.1f}% do mix")

    linhas.append("\n---\n")

    # Consultores
    linhas.append("## Consultores")
    for c in agg['consultores']:
        sinal = '+' if c['var_pct'] >= 0 else ''
        linhas.append(
            f"\n**{c['consultor']}**: {_fmt(c['fat_2026'])} em 2026 vs {_fmt(c['fat_2025'])} em 2025 "
            f"({sinal}{c['var_pct']:.1f}%). Atendeu {c['n_clientes_2026']} clientes com ticket medio de {_fmt(c['ticket_medio_2026'])} por NF."
        )
    if agg['consultores']:
        maior_fat = max(agg['consultores'], key=lambda x: x['fat_2026'])
        maior_ticket = max(agg['consultores'], key=lambda x: x['ticket_medio_2026'])
        mais_clientes = max(agg['consultores'], key=lambda x: x['n_clientes_2026'])
        linhas.append(f"\n*Consultor de maior faturamento:* {maior_fat['consultor']} ({_fmt(maior_fat['fat_2026'])})")
        linhas.append(f"*Maior ticket medio:* {maior_ticket['consultor']} ({_fmt(maior_ticket['ticket_medio_2026'])} por NF)")
        linhas.append(f"*Mais clientes atendidos:* {mais_clientes['consultor']} ({mais_clientes['n_clientes_2026']} clientes)")

    linhas.append("\n---\n")

    # Grupos
    linhas.append("## Mix de Pecas")
    for g in agg['grupos']:
        sinal = '+' if g['var_pct'] >= 0 else ''
        linhas.append(
            f"\n**{g['grupo']}**: {_fmt(g['fat_2026'])} em 2026 vs {_fmt(g['fat_2025'])} em 2025 "
            f"({sinal}{g['var_pct']:.1f}%). Representa {g['share_2026']:.1f}% do faturamento total."
        )
    if agg['grupos']:
        maior_grupo = max(agg['grupos'], key=lambda x: x['share_2026'])
        maior_cresc_grupo = max(agg['grupos'], key=lambda x: x['var_pct'])
        linhas.append(f"\n*Grupo dominante:* {maior_grupo['grupo']} com {maior_grupo['share_2026']:.1f}% do total")
        linhas.append(f"*Maior crescimento:* {maior_cresc_grupo['grupo']} (+{maior_cresc_grupo['var_pct']:.1f}%)")

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

    md_path = root / 'bloco2.md'
    json_path = root / 'bloco2.json'

    md_path.write_text(render_markdown(agg, periodo), encoding='utf-8')
    json_path.write_text(render_json(agg, periodo), encoding='utf-8')

    print(f"OK bloco2.md gerado: {md_path}")
    print(f"OK bloco2.json gerado: {json_path}")


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Rodar todos os testes**

```
pytest tests/test_bloco2.py -v
```

Expected: `10 passed`

- [ ] **Step 5: Rodar o script completo contra os dados reais**

```
python src/bloco2.py
```

Expected:

```
OK bloco2.md gerado: ...\bloco2.md
OK bloco2.json gerado: ...\bloco2.json
```

Abrir `bloco2.md` e verificar:

- Seção Filiais contém todas as filiais (Contagem, Uberlândia, Serra, Tanguá, Pouso Alegre, CRC, CSN, Wirtgen)
- Seção Consultores lista consultores com fat, clientes, ticket médio
- Seção Mix de Peças mostra FILTROS, LUBRIFICANTE, FPS, RODANTE, BATERIA
- Valores em R$ formatados corretamente (vírgula decimal, ponto milhar)

- [ ] **Step 6: Commit final**

```bash
git add src/bloco2.py tests/test_bloco2.py bloco2.md bloco2.json
git commit -m "feat(bloco2): render_markdown + render_json + main — bloco2 completo"
```
