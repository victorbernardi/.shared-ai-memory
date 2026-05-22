# Bloco 1 — Canais de Faturamento × Marca: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar `bloco1.md` (narrativo) e `bloco1.json` (indicadores para PPT) com faturamento Jan-Abr 2025 vs 2026 por canal × marca.

**Architecture:** Script único `src/bloco1.py` com funções separadas por responsabilidade: leitura, classificação, agregação, renderização Markdown narrativo e renderização JSON. Roda da raiz do projeto.

**Tech Stack:** Python, pandas, json (stdlib)

---

### Task 1: Leitura e classificação dos dados

**Files:**

- Create: `src/bloco1.py`
- Create: `tests/test_bloco1.py`

- [ ] **Step 1: Escrever o teste de leitura e classificação**

```python
# tests/test_bloco1.py
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from bloco1 import load_and_clean, classify

def make_df(dcc_values):
    n = len(dcc_values)
    data = {i: ["X"] * n for i in range(21)}
    data[7] = dcc_values          # dcc
    data[14] = [1000.0] * n       # liquido
    df = pd.DataFrame(data)
    return df

def test_classify_wirtgen():
    df = make_df(["PECAS WIRTGEN"])
    df = load_and_clean.__wrapped__(df) if hasattr(load_and_clean, '__wrapped__') else classify(load_and_clean.__wrapped__(df) if hasattr(load_and_clean, '__wrapped__') else df.rename(columns={7: 'dcc', 14: 'liquido'}))
    # forma direta: testar classify separado
    raw = pd.DataFrame({'dcc': ['PECAS WIRTGEN', 'PECAS CSN', 'PECAS CRC', 'PECAS SERVICOS', '', 'PECAS E ACESSORIOS'], 'liquido': [100]*6})
    result = classify(raw)
    assert result.loc[0, 'canal'] == 'Wirtgen'
    assert result.loc[0, 'marca'] == 'Wirtgen'
    assert result.loc[1, 'canal'] == 'CSN/Minerios'
    assert result.loc[1, 'marca'] == 'John Deere'
    assert result.loc[2, 'canal'] == 'CRC'
    assert result.loc[3, 'canal'] == 'Servicos'
    assert result.loc[4, 'canal'] == 'Balcao'
    assert result.loc[5, 'canal'] == 'Varejo JD'

def test_classify_marca_split():
    raw = pd.DataFrame({'dcc': ['PECAS WIRTGEN CONTRATOS', 'PECAS CSN'], 'liquido': [200.0, 300.0]})
    result = classify(raw)
    assert list(result['marca']) == ['Wirtgen', 'John Deere']
```

- [ ] **Step 2: Rodar o teste para confirmar que falha**

```
pytest tests/test_bloco1.py -v
```

Esperado: `ModuleNotFoundError: No module named 'bloco1'`

- [ ] **Step 3: Implementar `load_and_clean` e `classify`**

```python
# src/bloco1.py
import pandas as pd
import numpy as np
import json
from pathlib import Path

CANAL_RULES = [
    ('Wirtgen',      lambda dcc: dcc.str.contains('WIRTGEN', na=False)),
    ('CSN/Minerios', lambda dcc: dcc.str.contains('CSN',     na=False)),
    ('CRC',          lambda dcc: dcc.str.contains('CRC',     na=False)),
    ('Servicos',     lambda dcc: dcc.str.contains('SERVIC',  na=False)),
    ('Balcao',       lambda dcc: dcc == ''),
]

def load_and_clean(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    df.columns = list(range(len(df.columns)))
    df = df.rename(columns={7: 'dcc', 14: 'liquido'})
    df['dcc'] = df['dcc'].fillna('').astype(str).str.strip().str.upper()
    df['liquido'] = pd.to_numeric(df['liquido'], errors='coerce').fillna(0)
    return df[['dcc', 'liquido']]

def classify(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['canal'] = 'Varejo JD'
    df['marca'] = 'John Deere'
    for canal, mask_fn in reversed(CANAL_RULES):
        mask = mask_fn(df['dcc'])
        df.loc[mask, 'canal'] = canal
    df.loc[df['canal'] == 'Wirtgen', 'marca'] = 'Wirtgen'
    return df
```

- [ ] **Step 4: Rodar o teste para confirmar que passa**

```
pytest tests/test_bloco1.py::test_classify_wirtgen tests/test_bloco1.py::test_classify_marca_split -v
```

Esperado: 2 passed

- [ ] **Step 5: Commit**

```
git add src/bloco1.py tests/test_bloco1.py
git commit -m "feat(bloco1): load_and_clean + classify por canal e marca"
```

---

### Task 2: Agregação dos indicadores

**Files:**

- Modify: `src/bloco1.py`
- Modify: `tests/test_bloco1.py`

- [ ] **Step 1: Escrever o teste de agregação**

```python
# adicionar em tests/test_bloco1.py
from bloco1 import aggregate

def test_aggregate_basic():
    df25 = pd.DataFrame({'dcc': ['', 'PECAS CSN', 'PECAS WIRTGEN'], 'liquido': [1000.0, 500.0, 200.0]})
    df26 = pd.DataFrame({'dcc': ['', 'PECAS CSN', 'PECAS WIRTGEN'], 'liquido': [1100.0, 400.0, 250.0]})
    result = aggregate(df25, df26)

    # total geral
    assert result['total_geral']['fat_2025'] == 1700.0
    assert result['total_geral']['fat_2026'] == 1750.0
    assert abs(result['total_geral']['var_pct'] - 2.94) < 0.1

    # John Deere total
    jd = result['marcas']['John Deere']
    assert jd['fat_2025'] == 1500.0
    assert jd['fat_2026'] == 1500.0

    # canal Balcao dentro de JD
    balcao = next(c for c in jd['canais'] if c['canal'] == 'Balcao')
    assert balcao['fat_2025'] == 1000.0
    assert balcao['fat_2026'] == 1100.0
    assert abs(balcao['share_2026'] - (1100 / 1500 * 100)) < 0.1
```

- [ ] **Step 2: Rodar para confirmar falha**

```
pytest tests/test_bloco1.py::test_aggregate_basic -v
```

Esperado: `ImportError: cannot import name 'aggregate'`

- [ ] **Step 3: Implementar `aggregate`**

```python
# adicionar em src/bloco1.py

def _var_pct(a: float, b: float) -> float:
    if a == 0:
        return 0.0
    return round((b - a) / a * 100, 2)

def _canal_row(canal: str, f25: float, f26: float, total_marca_26: float) -> dict:
    return {
        'canal': canal,
        'fat_2025': round(f25, 2),
        'fat_2026': round(f26, 2),
        'var_pct': _var_pct(f25, f26),
        'share_2026': round(f26 / total_marca_26 * 100, 2) if total_marca_26 else 0.0,
    }

def aggregate(df25: pd.DataFrame, df26: pd.DataFrame) -> dict:
    df25 = classify(df25)
    df26 = classify(df26)

    result = {'marcas': {}, 'total_geral': {}}
    total_25 = df25['liquido'].sum()
    total_26 = df26['liquido'].sum()
    result['total_geral'] = {
        'fat_2025': round(total_25, 2),
        'fat_2026': round(total_26, 2),
        'var_pct': _var_pct(total_25, total_26),
    }

    for marca in ['John Deere', 'Wirtgen']:
        m25 = df25[df25['marca'] == marca]
        m26 = df26[df26['marca'] == marca]
        fat25 = m25['liquido'].sum()
        fat26 = m26['liquido'].sum()
        total_marca_26 = fat26

        canais = []
        for canal in ['Balcao', 'CSN/Minerios', 'CRC', 'Servicos', 'Varejo JD', 'Wirtgen']:
            f25 = m25[m25['canal'] == canal]['liquido'].sum()
            f26 = m26[m26['canal'] == canal]['liquido'].sum()
            if f25 > 0 or f26 > 0:
                canais.append(_canal_row(canal, f25, f26, total_marca_26))

        result['marcas'][marca] = {
            'fat_2025': round(fat25, 2),
            'fat_2026': round(fat26, 2),
            'var_pct': _var_pct(fat25, fat26),
            'share_no_total_2026': round(fat26 / total_26 * 100, 2) if total_26 else 0.0,
            'canais': canais,
        }

    return result
```

- [ ] **Step 4: Rodar o teste**

```
pytest tests/test_bloco1.py::test_aggregate_basic -v
```

Esperado: 1 passed

- [ ] **Step 5: Commit**

```
git add src/bloco1.py tests/test_bloco1.py
git commit -m "feat(bloco1): aggregate por marca x canal com share e var%"
```

---

### Task 3: Renderização JSON

**Files:**

- Modify: `src/bloco1.py`
- Modify: `tests/test_bloco1.py`

- [ ] **Step 1: Escrever o teste**

```python
# adicionar em tests/test_bloco1.py
import json
from bloco1 import render_json

def test_render_json_structure():
    agg = {
        'periodo': 'Jan-Abr 2025 vs Jan-Abr 2026',
        'total_geral': {'fat_2025': 1000.0, 'fat_2026': 1100.0, 'var_pct': 10.0},
        'marcas': {
            'John Deere': {'fat_2025': 1000.0, 'fat_2026': 1100.0, 'var_pct': 10.0, 'share_no_total_2026': 100.0, 'canais': []},
            'Wirtgen': {'fat_2025': 0.0, 'fat_2026': 0.0, 'var_pct': 0.0, 'share_no_total_2026': 0.0, 'canais': []},
        }
    }
    output = render_json(agg)
    parsed = json.loads(output)
    assert parsed['periodo'] == 'Jan-Abr 2025 vs Jan-Abr 2026'
    assert 'total_geral' in parsed
    assert 'marcas' in parsed
    assert 'John Deere' in parsed['marcas']
```

- [ ] **Step 2: Rodar para confirmar falha**

```
pytest tests/test_bloco1.py::test_render_json_structure -v
```

- [ ] **Step 3: Implementar `render_json`**

```python
# adicionar em src/bloco1.py

def render_json(agg: dict) -> str:
    return json.dumps(agg, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: Rodar o teste**

```
pytest tests/test_bloco1.py::test_render_json_structure -v
```

Esperado: 1 passed

- [ ] **Step 5: Commit**

```
git add src/bloco1.py tests/test_bloco1.py
git commit -m "feat(bloco1): render_json com estrutura para PPT"
```

---

### Task 4: Renderização Markdown narrativo

**Files:**

- Modify: `src/bloco1.py`
- Modify: `tests/test_bloco1.py`

- [ ] **Step 1: Escrever o teste**

```python
# adicionar em tests/test_bloco1.py
from bloco1 import render_markdown

def test_render_markdown_contains_sections():
    agg = {
        'periodo': 'Jan-Abr 2025 vs Jan-Abr 2026',
        'total_geral': {'fat_2025': 120000000.0, 'fat_2026': 131000000.0, 'var_pct': 9.17},
        'marcas': {
            'John Deere': {
                'fat_2025': 115000000.0, 'fat_2026': 125000000.0, 'var_pct': 8.7,
                'share_no_total_2026': 95.4,
                'canais': [
                    {'canal': 'Balcao', 'fat_2025': 80000000.0, 'fat_2026': 86000000.0, 'var_pct': 7.5, 'share_2026': 68.8},
                    {'canal': 'CSN/Minerios', 'fat_2025': 22000000.0, 'fat_2026': 25000000.0, 'var_pct': 13.6, 'share_2026': 20.0},
                ]
            },
            'Wirtgen': {
                'fat_2025': 5000000.0, 'fat_2026': 6000000.0, 'var_pct': 20.0,
                'share_no_total_2026': 4.6,
                'canais': []
            }
        }
    }
    md = render_markdown(agg)
    assert '# Bloco 1' in md
    assert 'John Deere' in md
    assert 'Wirtgen' in md
    assert 'Balcao' in md or 'Balcão' in md
    assert 'R$' in md
```

- [ ] **Step 2: Rodar para confirmar falha**

```
pytest tests/test_bloco1.py::test_render_markdown_contains_sections -v
```

- [ ] **Step 3: Implementar `render_markdown`**

```python
# adicionar em src/bloco1.py

def _fmt(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _destaque_canal(canais: list, chave: str) -> dict | None:
    validos = [c for c in canais if c['fat_2025'] > 0 or c['fat_2026'] > 0]
    if not validos:
        return None
    return max(validos, key=lambda c: c[chave])

def render_markdown(agg: dict) -> str:
    tg = agg['total_geral']
    jd = agg['marcas']['John Deere']
    wirt = agg['marcas']['Wirtgen']
    sinal = '+' if tg['var_pct'] >= 0 else ''
    linhas = []

    linhas.append("# Bloco 1 — Canais de Faturamento")
    linhas.append(f"\n**Periodo:** {agg['periodo']}\n")

    # Visao Geral
    linhas.append("## Visao Geral")
    linhas.append(
        f"O faturamento liquido total passou de {_fmt(tg['fat_2025'])} em 2025 para "
        f"{_fmt(tg['fat_2026'])} em 2026, variacao de {sinal}{tg['var_pct']:.1f}%. "
        f"A operacao John Deere representa {jd['share_no_total_2026']:.1f}% do faturamento total "
        f"e Wirtgen responde pelos {wirt['share_no_total_2026']:.1f}% restantes."
    )

    # John Deere
    linhas.append("\n## John Deere")
    sinal_jd = '+' if jd['var_pct'] >= 0 else ''
    linhas.append(
        f"A marca John Deere faturou {_fmt(jd['fat_2026'])} em 2026 contra "
        f"{_fmt(jd['fat_2025'])} em 2025 ({sinal_jd}{jd['var_pct']:.1f}%)."
    )
    for c in jd['canais']:
        sinal_c = '+' if c['var_pct'] >= 0 else ''
        linhas.append(
            f"\n**{c['canal']}:** {_fmt(c['fat_2026'])} em 2026 vs {_fmt(c['fat_2025'])} em 2025 "
            f"({sinal_c}{c['var_pct']:.1f}%). Representa {c['share_2026']:.1f}% do mix John Deere em 2026."
        )

    # Destaques automaticos JD
    maior_alta = _destaque_canal(jd['canais'], 'var_pct')
    maior_queda = min([c for c in jd['canais'] if c['fat_2025'] > 0], key=lambda c: c['var_pct'], default=None)
    maior_share = _destaque_canal(jd['canais'], 'share_2026')
    if maior_alta:
        linhas.append(f"\n*Canal de maior crescimento:* {maior_alta['canal']} (+{maior_alta['var_pct']:.1f}%)")
    if maior_queda and maior_queda['var_pct'] < 0:
        linhas.append(f"*Canal de maior queda:* {maior_queda['canal']} ({maior_queda['var_pct']:.1f}%)")
    if maior_share:
        linhas.append(f"*Canal dominante:* {maior_share['canal']} com {maior_share['share_2026']:.1f}% do mix")

    # Wirtgen
    linhas.append("\n## Wirtgen")
    sinal_w = '+' if wirt['var_pct'] >= 0 else ''
    linhas.append(
        f"A operacao Wirtgen faturou {_fmt(wirt['fat_2026'])} em 2026 contra "
        f"{_fmt(wirt['fat_2025'])} em 2025 ({sinal_w}{wirt['var_pct']:.1f}%). "
        f"Representa {wirt['share_no_total_2026']:.1f}% do faturamento total da Inova."
    )

    return "\n".join(linhas)
```

- [ ] **Step 4: Rodar o teste**

```
pytest tests/test_bloco1.py::test_render_markdown_contains_sections -v
```

Esperado: 1 passed

- [ ] **Step 5: Commit**

```
git add src/bloco1.py tests/test_bloco1.py
git commit -m "feat(bloco1): render_markdown narrativo com destaques automaticos"
```

---

### Task 5: Orquestrador `main()` e geração dos arquivos finais

**Files:**

- Modify: `src/bloco1.py`

- [ ] **Step 1: Implementar `main()`**

```python
# adicionar em src/bloco1.py

def main():
    root = Path(__file__).parents[1]
    df25 = load_and_clean(str(root / 'Vendas_2025.xlsx'))
    df26 = load_and_clean(str(root / 'Vendas_2026.xlsx'))

    agg = aggregate(df25, df26)
    agg['periodo'] = 'Jan-Abr 2025 vs Jan-Abr 2026'

    md_path = root / 'bloco1.md'
    json_path = root / 'bloco1.json'

    md_path.write_text(render_markdown(agg), encoding='utf-8')
    json_path.write_text(render_json(agg), encoding='utf-8')

    print(f"OK bloco1.md gerado: {md_path}")
    print(f"OK bloco1.json gerado: {json_path}")

if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Rodar o script completo**

```
python src/bloco1.py
```

Esperado:

```
OK bloco1.md gerado: ...
OK bloco1.json gerado: ...
```

- [ ] **Step 3: Verificar os arquivos gerados**

Abrir `bloco1.md` e confirmar:

- Tem seções Visao Geral, John Deere, Wirtgen
- Valores em R$ formatados (ex: `R$ 80.699.555,95`)
- Destaques de maior alta, maior queda, canal dominante

Abrir `bloco1.json` e confirmar:

- Tem `periodo`, `total_geral`, `marcas`
- Cada canal tem `fat_2025`, `fat_2026`, `var_pct`, `share_2026`

- [ ] **Step 4: Rodar todos os testes**

```
pytest tests/test_bloco1.py -v
```

Esperado: todos passando

- [ ] **Step 5: Commit final**

```
git add src/bloco1.py bloco1.md bloco1.json
git commit -m "feat(bloco1): main() completo — gera bloco1.md e bloco1.json"
```
