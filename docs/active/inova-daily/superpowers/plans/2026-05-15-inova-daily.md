# Inova Daily — Briefing Executivo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar diariamente um e-mail executivo de vendas de peças com recap mensal (semana 1) + foto do dia anterior com comparativos históricos.

**Architecture:** `run_daily.py` verifica/atualiza o cache do Motor Faturamento (M2), depois chama `generator.py` que compõe dois blocos: recap mensal (de `recap_mensal.py`) e snapshot diário (de `snapshot_diario.py`). Ambos consomem dados via `faturamento.py` (M2 cache) e consultas diretas ao `vw_VENDAS` (para dados com vendedor do dia anterior).

**Tech Stack:** Python 3.11+, pandas, openpyxl, pyarrow, subprocess, argparse

---

## File Map

| Arquivo | Ação | Responsabilidade |
|---------|------|-----------------|
| `src/config.py` | Modificar | Adicionar paths M2, metas, FILIAL_MAP |
| `src/faturamento.py` | Criar | Loader do M2 cache + funções de consulta históricas |
| `src/recap_mensal.py` | Criar | Bloco 1: highlights do mês (usa faturamento.py + metas Excel) |
| `src/snapshot_diario.py` | Criar | Bloco 2: foto de ontem (vw_VENDAS + faturamento.py) |
| `templates/email_template_v3.md` | Criar | Template com placeholders para os dois blocos |
| `src/generator.py` | Modificar | Orquestrar recap + snapshot → preencher template → salvar |
| `run_daily.py` | Criar | CLI: verifica M2, gera e-mail |
| `tests/test_faturamento.py` | Criar | Testes unitários com DataFrame de fixture |
| `tests/test_recap_mensal.py` | Criar | Testes unitários com dados mockados |
| `tests/test_snapshot_diario.py` | Criar | Testes unitários com dados mockados |

---

## Task 1: Descobrir FILIAL_MAP e atualizar src/config.py

**Files:**

- Modify: `src/config.py`

- [ ] **Step 1: Descobrir códigos de filial no parquet**

```bash
python -c "
import pandas as pd
df = pd.read_parquet(r'C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\data\cache_vendas_rfm.parquet')
print(df[['FILIAL']].drop_duplicates().sort_values('FILIAL').to_string())
"
```

Anote os códigos retornados — você vai precisar deles no próximo step.

- [ ] **Step 2: Adicionar constantes em `src/config.py`**

Abra `src/config.py` e adicione ao final:

```python
# --- MOTOR FATURAMENTO (M2) ---
M2_CACHE_PATH = Path(r"C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\data\cache_vendas_rfm.parquet")
M2_LOG_PATH = Path(r"C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\data\run.log")
M2_RUN_SCRIPT = Path(r"C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\run.py")

# --- METAS ---
METAS_PATH = Path(r"C:\Projetos\Inova\projects\metas-pecas\data\Metas de peças John Deere 2026 - Revisão março.xlsx")

# --- FILIAL MAP: código → nome amigável ---
# Preencher com os códigos retornados no Step 1
FILIAL_MAP: dict[str, str] = {
    # Exemplo: "0201": "Contagem", "0202": "Tanguá"
    # Substitua com os valores reais do Step 1
}
```

- [ ] **Step 3: Confirmar que config importa sem erro**

```bash
cd "C:\Projetos\Inova\projects\Inova-Daily"
python -c "from src.config import M2_CACHE_PATH, METAS_PATH, FILIAL_MAP; print('OK', M2_CACHE_PATH.exists(), METAS_PATH.exists())"
```

Esperado: `OK True True`

- [ ] **Step 4: Commit**

```bash
git add src/config.py
git commit -m "feat(config): adicionar paths M2, metas e FILIAL_MAP"
```

---

## Task 2: Criar src/faturamento.py (TDD)

**Files:**

- Create: `src/faturamento.py`
- Create: `tests/test_faturamento.py`

- [ ] **Step 1: Escrever o teste**

Crie `tests/test_faturamento.py`:

```python
import pandas as pd
import pytest
from datetime import date
from unittest.mock import patch

FIXTURE_DF = pd.DataFrame({
    "CPF_CNPJ_DO_CLIENTE": ["12345678000100", "12345678000100", "99999999000199"],
    "NOME_DO_CLIENTE": ["Cliente A", "Cliente A", "Cliente B"],
    "FILIAL": ["0201", "0201", "0202"],
    "DATA_EMISSAO_NF": pd.to_datetime(["2025-01-10", "2026-01-15", "2026-01-20"]),
    "CODIGO_TES": ["501", "501", "504"],
    "DESCRICAO_CC": ["PECAS - CONTAGEM", "PECAS - CONTAGEM", "PECAS - TANGUÁ"],
    "CENTRO_CUSTO": ["CC01", "CC01", "CC02"],
    "COD_GRUPO": ["G1", "G1", "G2"],
    "NUMERO_DA_NF": ["NF001", "NF002", "NF003"],
    "DESCRICAO_DO_PRODUTO": ["FILTRO", "FILTRO", "OLEO"],
    "VALOR_DO_PRODUTO": [1000.0, 2000.0, 500.0],
})

@pytest.fixture(autouse=True)
def mock_parquet(monkeypatch):
    import src.faturamento as fat
    fat._df_cache = None  # reset cache between tests
    monkeypatch.setattr("src.faturamento._ler_parquet", lambda: FIXTURE_DF.copy())

def test_por_mes_filtra_ano_e_mes():
    from src.faturamento import por_mes
    df = por_mes(2026, 1)
    assert len(df) == 2
    assert all(df["DATA_EMISSAO_NF"].dt.year == 2026)
    assert all(df["DATA_EMISSAO_NF"].dt.month == 1)

def test_por_mes_ano_anterior():
    from src.faturamento import por_mes
    df = por_mes(2025, 1)
    assert len(df) == 1
    assert df.iloc[0]["VALOR_DO_PRODUTO"] == 1000.0

def test_total_faturado():
    from src.faturamento import por_mes, total_faturado
    df = por_mes(2026, 1)
    assert total_faturado(df) == pytest.approx(2500.0)

def test_top_filiais_ordem():
    from src.faturamento import por_mes, top_filiais
    df = por_mes(2026, 1)
    resultado = top_filiais(df, 2)
    # 0201 tem 2000, 0202 tem 500 → 0201 vem primeiro
    assert resultado[0][1] == pytest.approx(2000.0)

def test_por_dia_filtra_data_exata():
    from src.faturamento import por_dia
    df = por_dia(date(2026, 1, 15))
    assert len(df) == 1
    assert df.iloc[0]["VALOR_DO_PRODUTO"] == 2000.0
```

- [ ] **Step 2: Rodar o teste — deve falhar**

```bash
cd "C:\Projetos\Inova\projects\Inova-Daily"
python -m pytest tests/test_faturamento.py -v
```

Esperado: `ERROR` ou `ImportError` (módulo ainda não existe)

- [ ] **Step 3: Criar `src/faturamento.py`**

```python
from __future__ import annotations
import pandas as pd
from datetime import date
from src.config import M2_CACHE_PATH, TES_ALL_VALID, FILIAL_MAP

_df_cache: pd.DataFrame | None = None


def _ler_parquet() -> pd.DataFrame:
    return pd.read_parquet(M2_CACHE_PATH)


def _carregar() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        df = _ler_parquet()
        df["DATA_EMISSAO_NF"] = pd.to_datetime(df["DATA_EMISSAO_NF"])
        tes_validos = {str(t) for t in TES_ALL_VALID}
        df = df[df["CODIGO_TES"].astype(str).isin(tes_validos)]
        _df_cache = df
    return _df_cache


def por_mes(ano: int, mes: int) -> pd.DataFrame:
    df = _carregar()
    mask = (df["DATA_EMISSAO_NF"].dt.year == ano) & (df["DATA_EMISSAO_NF"].dt.month == mes)
    return df[mask].copy()


def por_dia(data: date) -> pd.DataFrame:
    df = _carregar()
    return df[df["DATA_EMISSAO_NF"].dt.date == data].copy()


def total_faturado(df: pd.DataFrame) -> float:
    return float(df["VALOR_DO_PRODUTO"].sum())


def top_filiais(df: pd.DataFrame, n: int = 3) -> list[tuple[str, float]]:
    resultado = (
        df.groupby("FILIAL")["VALOR_DO_PRODUTO"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
    )
    return [(FILIAL_MAP.get(k, k), float(v)) for k, v in resultado.items()]


def dias_uteis_restantes(mes: int, ano: int) -> int:
    ultimo_dia = pd.Timestamp(ano, mes, 1) + pd.offsets.MonthEnd(0)
    hoje = pd.Timestamp.today().normalize()
    datas = pd.bdate_range(start=hoje + pd.Timedelta(days=1), end=ultimo_dia)
    return len(datas)
```

- [ ] **Step 4: Rodar os testes — devem passar**

```bash
python -m pytest tests/test_faturamento.py -v
```

Esperado: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/faturamento.py tests/test_faturamento.py
git commit -m "feat(faturamento): loader M2 cache com consultas por dia/mes/filial"
```

---

## Task 3: Criar src/recap_mensal.py (TDD)

**Files:**

- Create: `src/recap_mensal.py`
- Create: `tests/test_recap_mensal.py`

- [ ] **Step 1: Escrever o teste**

Crie `tests/test_recap_mensal.py`:

```python
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

METAS_MOCK = {1: 12_850_235.99, 2: 12_850_235.99, 3: 13_381_474.99,
              4: 13_466_411.88, 5: 13_646_411.88}

DF_JAN_2026 = pd.DataFrame({
    "NOME_DO_CLIENTE": ["A", "A", "B"],
    "FILIAL": ["0201", "0201", "0202"],
    "DATA_EMISSAO_NF": pd.to_datetime(["2026-01-05", "2026-01-20", "2026-01-25"]),
    "VALOR_DO_PRODUTO": [5_000_000.0, 4_000_000.0, 3_000_000.0],
})

DF_JAN_2025 = pd.DataFrame({
    "NOME_DO_CLIENTE": ["A"],
    "FILIAL": ["0201"],
    "DATA_EMISSAO_NF": pd.to_datetime(["2025-01-10"]),
    "VALOR_DO_PRODUTO": [15_000_000.0],  # maior que 2026 (12M) → YoY negativo
})

@pytest.fixture(autouse=True)
def mock_deps(monkeypatch):
    monkeypatch.setattr("src.recap_mensal.carregar_metas", lambda: METAS_MOCK)
    def fake_por_mes(ano, mes):
        if ano == 2026 and mes == 1:
            return DF_JAN_2026.copy()
        if ano == 2025 and mes == 1:
            return DF_JAN_2025.copy()
        return pd.DataFrame(columns=DF_JAN_2026.columns)
    monkeypatch.setattr("src.recap_mensal.fat.por_mes", fake_por_mes)
    monkeypatch.setattr("src.recap_mensal.fat.top_filiais", lambda df, n=3: [("Contagem", 9_000_000.0), ("Tanguá", 3_000_000.0)])
    monkeypatch.setattr("src.recap_mensal.fat.total_faturado", lambda df: float(df["VALOR_DO_PRODUTO"].sum()))

def test_total_correto():
    from src.recap_mensal import highlight_mes
    r = highlight_mes(1, 2026)
    assert r["total"] == pytest.approx(12_000_000.0)

def test_yoy_negativo_quando_ano_ant_maior():
    from src.recap_mensal import highlight_mes
    r = highlight_mes(1, 2026)
    assert r["yoy_pct"] < 0

def test_pct_meta_calculada():
    from src.recap_mensal import highlight_mes
    r = highlight_mes(1, 2026)
    assert r["pct_meta"] == pytest.approx(12_000_000 / 12_850_235.99 * 100)

def test_melhor_dia_identificado():
    from src.recap_mensal import highlight_mes
    r = highlight_mes(1, 2026)
    import datetime
    assert r["melhor_dia"] == datetime.date(2026, 1, 5)
    assert r["melhor_dia_valor"] == pytest.approx(5_000_000.0)

def test_cliente_destaque():
    from src.recap_mensal import highlight_mes
    r = highlight_mes(1, 2026)
    assert r["cliente_destaque"][0] == "A"
    assert r["cliente_destaque"][1] == pytest.approx(9_000_000.0)
```

- [ ] **Step 2: Rodar — deve falhar**

```bash
python -m pytest tests/test_recap_mensal.py -v
```

Esperado: `ImportError` (módulo não existe)

- [ ] **Step 3: Criar `src/recap_mensal.py`**

```python
from __future__ import annotations
import pandas as pd
from src import faturamento as fat
from src.config import METAS_PATH


def carregar_metas() -> dict[int, float]:
    df = pd.read_excel(METAS_PATH, header=None)
    linha = df[df.iloc[:, 0].astype(str).str.strip().str.lower() == "total"]
    if linha.empty:
        raise ValueError("Linha 'Total' não encontrada no arquivo de metas")
    row = linha.iloc[0]
    # Col index 2 = Janeiro (mes 1), col index 3 = Fevereiro (mes 2), ...
    return {mes: float(row.iloc[mes + 1]) for mes in range(1, 13)}


def highlight_mes(mes: int, ano: int = 2026) -> dict:
    df = fat.por_mes(ano, mes)
    df_ant = fat.por_mes(ano - 1, mes)
    metas = carregar_metas()
    meta = metas.get(mes, 0.0)

    total = fat.total_faturado(df)
    total_ant = fat.total_faturado(df_ant)
    yoy = ((total - total_ant) / total_ant * 100) if total_ant > 0 else 0.0

    por_dia = df.groupby(df["DATA_EMISSAO_NF"].dt.date)["VALOR_DO_PRODUTO"].sum()
    melhor_dia = por_dia.idxmax() if not por_dia.empty else None
    melhor_dia_valor = float(por_dia.max()) if not por_dia.empty else 0.0

    top_f = fat.top_filiais(df, 3)

    top_cliente = df.groupby("NOME_DO_CLIENTE")["VALOR_DO_PRODUTO"].sum().sort_values(ascending=False)
    cliente_nome = top_cliente.index[0] if not top_cliente.empty else "N/A"
    cliente_valor = float(top_cliente.iloc[0]) if not top_cliente.empty else 0.0

    media_diaria = float(por_dia.mean()) if not por_dia.empty else 0.0
    anomalia = None
    if media_diaria > 0:
        picos = por_dia[por_dia > media_diaria * 2]
        quedas = por_dia[por_dia < media_diaria * 0.3]
        if not picos.empty:
            d = picos.idxmax()
            anomalia = {"tipo": "pico", "data": d, "valor": float(por_dia[d]),
                        "fator": round(por_dia[d] / media_diaria, 1)}
        elif not quedas.empty:
            d = quedas.idxmin()
            anomalia = {"tipo": "queda", "data": d, "valor": float(por_dia[d]),
                        "fator": round(por_dia[d] / media_diaria, 1)}

    return {
        "mes": mes,
        "ano": ano,
        "total": total,
        "meta": meta,
        "pct_meta": (total / meta * 100) if meta > 0 else 0.0,
        "yoy_pct": yoy,
        "total_ano_ant": total_ant,
        "melhor_dia": melhor_dia,
        "melhor_dia_valor": melhor_dia_valor,
        "top_filiais": top_f,
        "cliente_destaque": (cliente_nome, cliente_valor),
        "anomalia": anomalia,
    }
```

- [ ] **Step 4: Rodar — devem passar**

```bash
python -m pytest tests/test_recap_mensal.py -v
```

Esperado: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/recap_mensal.py tests/test_recap_mensal.py
git commit -m "feat(recap-mensal): highlights mensais com YoY, meta e anomalia"
```

---

## Task 4: Criar src/snapshot_diario.py (TDD)

**Files:**

- Create: `src/snapshot_diario.py`
- Create: `tests/test_snapshot_diario.py`

- [ ] **Step 1: Escrever o teste**

Crie `tests/test_snapshot_diario.py`:

```python
import pandas as pd
import pytest
from datetime import date
from unittest.mock import patch

DF_ONTEM = pd.DataFrame({
    "NF": ["NF001", "NF001", "NF002"],
    "NOME_VENDEDOR": ["Joao", "Joao", "Maria"],
    "FILIAL_NOME": ["PECAS - CONTAGEM", "PECAS - CONTAGEM", "PECAS - TANGUÁ"],
    "RECEITA": [8_000.0, 2_000.0, 5_000.0],
})

@pytest.fixture(autouse=True)
def mock_deps(monkeypatch):
    monkeypatch.setattr("src.snapshot_diario.executar_query", lambda q, l: DF_ONTEM.copy())
    monkeypatch.setattr("src.snapshot_diario.fat.por_mes", lambda ano, mes: pd.DataFrame({
        "DATA_EMISSAO_NF": pd.to_datetime(["2026-05-10", "2026-05-12"]),
        "VALOR_DO_PRODUTO": [50_000.0, 30_000.0],
    }))
    monkeypatch.setattr("src.snapshot_diario.fat.por_dia", lambda d: pd.DataFrame({
        "DATA_EMISSAO_NF": pd.to_datetime([f"{d}"]),
        "VALOR_DO_PRODUTO": [10_000.0],
    }))
    monkeypatch.setattr("src.snapshot_diario.fat.total_faturado", lambda df: float(df["VALOR_DO_PRODUTO"].sum()))
    monkeypatch.setattr("src.snapshot_diario.fat.dias_uteis_restantes", lambda mes, ano: 10)
    monkeypatch.setattr("src.snapshot_diario.carregar_metas", lambda: {5: 13_646_411.88})

def test_total_ontem_correto():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    assert r["total"] == pytest.approx(15_000.0)

def test_nfs_contagem_unica():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    assert r["nfs"] == 2

def test_top_vendedores_ordenado():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    vendedores = list(r["top_vendedores"].keys())
    assert vendedores[0] == "Joao"

def test_tendencia_retorna_string_valida():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    assert r["tendencia"] in ["Crescendo ↑", "Estável →", "Caindo ↓"]

def test_pct_meta_calculada():
    from src.snapshot_diario import foto_ontem
    r = foto_ontem(date(2026, 5, 14))
    acumulado = 80_000.0  # 50k + 30k do mock por_mes
    assert r["pct_meta"] == pytest.approx(acumulado / 13_646_411.88 * 100)
```

- [ ] **Step 2: Rodar — deve falhar**

```bash
python -m pytest tests/test_snapshot_diario.py -v
```

Esperado: `ImportError`

- [ ] **Step 3: Criar `src/snapshot_diario.py`**

```python
from __future__ import annotations
import pandas as pd
from datetime import date, timedelta
from src.db_utils import executar_query
from src import faturamento as fat
from src.config import TES_ALL_VALID
from src.recap_mensal import carregar_metas


def _ultimo_dia_util(referencia: date) -> date:
    d = referencia - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def _dias_uteis_anteriores(a_partir_de: date, n: int) -> list[date]:
    datas: list[date] = []
    d = a_partir_de - timedelta(days=1)
    while len(datas) < n:
        if d.weekday() < 5:
            datas.append(d)
        d -= timedelta(days=1)
    return datas


def _calcular_tendencia(data_ref: date) -> tuple[str, float]:
    recentes = _dias_uteis_anteriores(data_ref, 3)
    passados = _dias_uteis_anteriores(recentes[-1], 3)

    def media(dias: list[date]) -> float:
        vals = [fat.total_faturado(fat.por_dia(d)) for d in dias]
        return sum(vals) / len(vals) if vals else 0.0

    m_recente = media(recentes)
    m_passada = media(passados)
    delta = ((m_recente - m_passada) / m_passada * 100) if m_passada > 0 else 0.0

    if delta > 5:
        return "Crescendo ↑", delta
    elif delta < -5:
        return "Caindo ↓", delta
    return "Estável →", delta


def foto_ontem(data_ontem: date | None = None) -> dict:
    if data_ontem is None:
        data_ontem = _ultimo_dia_util(date.today())

    tes_sql = "(" + ",".join([f"'{t}'" for t in TES_ALL_VALID]) + ")"
    query = f"""
        SELECT
            NUMERO_DA_NF as NF,
            NOME_VENDEDOR,
            DESCRICAO_CC as FILIAL_NOME,
            VALOR_DO_PRODUTO as RECEITA
        FROM [dbo].[vw_VENDAS]
        WHERE CAST(DATA_EMISSAO_NF AS DATE) = '{data_ontem}'
          AND CAST(CODIGO_TES AS VARCHAR) IN {tes_sql}
    """
    df = executar_query(query, "Snapshot Ontem")

    total = float(df["RECEITA"].sum()) if not df.empty else 0.0
    nfs = int(df["NF"].nunique()) if not df.empty else 0
    top_vend = (
        df.groupby("NOME_VENDEDOR")["RECEITA"].sum()
        .sort_values(ascending=False).head(3).to_dict()
        if not df.empty else {}
    )
    top_fil = (
        df.groupby("FILIAL_NOME")["RECEITA"].sum()
        .sort_values(ascending=False).head(3).to_dict()
        if not df.empty else {}
    )

    mes = data_ontem.month
    ano = data_ontem.year
    df_mes = fat.por_mes(ano, mes)
    acumulado_mes = fat.total_faturado(df_mes)

    df_mes_ant = fat.por_mes(ano - 1, mes)
    total_mes_ant = fat.total_faturado(df_mes_ant)
    yoy = ((acumulado_mes - total_mes_ant) / total_mes_ant * 100) if total_mes_ant > 0 else 0.0

    metas = carregar_metas()
    meta_mes = metas.get(mes, 0.0)
    pct_meta = (acumulado_mes / meta_mes * 100) if meta_mes > 0 else 0.0
    dias_restantes = fat.dias_uteis_restantes(mes, ano)

    tendencia, delta_tend = _calcular_tendencia(data_ontem)

    return {
        "data_ontem": data_ontem,
        "total": total,
        "nfs": nfs,
        "top_vendedores": top_vend,
        "top_filiais": top_fil,
        "acumulado_mes": acumulado_mes,
        "meta_mes": meta_mes,
        "pct_meta": pct_meta,
        "dias_restantes": dias_restantes,
        "yoy_pct": yoy,
        "total_mes_ano_ant": total_mes_ant,
        "tendencia": tendencia,
        "delta_tendencia": delta_tend,
    }
```

- [ ] **Step 4: Rodar — devem passar**

```bash
python -m pytest tests/test_snapshot_diario.py -v
```

Esperado: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/snapshot_diario.py tests/test_snapshot_diario.py
git commit -m "feat(snapshot-diario): foto do dia com YoY, meta e tendência"
```

---

## Task 5: Criar templates/email_template_v3.md

**Files:**

- Create: `templates/email_template_v3.md`

- [ ] **Step 1: Criar o template**

Crie `templates/email_template_v3.md` com o conteúdo abaixo. Os placeholders `{{ ... }}` são substituídos pelo `generator.py`:

```markdown
# Inova Daily — {{ data_hoje }} | {{ tendencia }}

---

## 📅 RECAP: {{ mes_nome }} {{ ano }}

**Faturamento do mês:** R$ {{ recap_total }}
**Meta:** R$ {{ recap_meta }} → **{{ recap_pct_meta }}% atingido**
**vs {{ mes_nome }} {{ ano_ant }}:** {{ recap_yoy_sinal }}{{ recap_yoy_abs }}% (R$ {{ recap_total_ant }} no mesmo mês)

**Melhor dia:** {{ recap_melhor_dia }} — R$ {{ recap_melhor_dia_valor }}

**Top filiais:**
{{ recap_top_filiais }}

**Cliente destaque:** {{ recap_cliente_nome }} — R$ {{ recap_cliente_valor }}

{{ recap_anomalia }}

---

## 📊 FOTO DE ONTEM — {{ data_ontem }}

**Faturamento:** R$ {{ snap_total }} | {{ snap_nfs }} NFs emitidas

**Top vendedores:**
{{ snap_top_vendedores }}

**Top filiais:**
{{ snap_top_filiais }}

---

**Mês acumulado:** R$ {{ snap_acumulado_mes }}
**Meta {{ mes_atual_nome }}:** R$ {{ snap_meta_mes }} → **{{ snap_pct_meta }}% atingido** ({{ snap_dias_restantes }} dias úteis restantes)
**vs {{ mes_atual_nome }} 2025:** {{ snap_yoy_sinal }}{{ snap_yoy_abs }}% (R$ {{ snap_total_ano_ant }})

**Tendência (últimos 3 dias úteis):** {{ tendencia }} ({{ snap_delta_tend_sinal }}{{ snap_delta_tend }}%)

---
*Gerado automaticamente pelo Inova Daily em {{ hora_geracao }}*
```

- [ ] **Step 2: Verificar que o arquivo foi salvo**

```bash
python -c "from pathlib import Path; p = Path('templates/email_template_v3.md'); print('OK', p.exists(), p.stat().st_size, 'bytes')"
```

Esperado: `OK True` com tamanho > 0

- [ ] **Step 3: Commit**

```bash
git add templates/email_template_v3.md
git commit -m "feat(template): email_template_v3 com dois blocos e placeholders"
```

---

## Task 6: Atualizar src/generator.py

**Files:**

- Modify: `src/generator.py`

- [ ] **Step 1: Substituir o conteúdo de `src/generator.py`**

```python
import locale
from datetime import datetime, date
from pathlib import Path

from src.config import TEMPLATE_DIR, OUTPUT_DIR
from src.recap_mensal import highlight_mes
from src.snapshot_diario import foto_ontem

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


def _brl(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _sinal(valor: float) -> str:
    return "+" if valor >= 0 else ""


def _filiais_md(filiais: list[tuple[str, float]]) -> str:
    linhas = [f"- **{nome}:** R$ {_brl(valor)}" for nome, valor in filiais]
    return "\n".join(linhas)


def _vendedores_md(vendedores: dict[str, float]) -> str:
    linhas = [f"- **{nome}:** R$ {_brl(valor)}" for nome, valor in vendedores.items()]
    return "\n".join(linhas)


def _anomalia_md(anomalia: dict | None) -> str:
    if anomalia is None:
        return ""
    tipo = "🔴 Queda atípica" if anomalia["tipo"] == "queda" else "🟢 Pico atípico"
    return (
        f"\n**{tipo}:** {anomalia['data'].strftime('%d/%m')} — "
        f"R$ {_brl(anomalia['valor'])} ({anomalia['fator']}x a média diária)"
    )


def gerar_email(mes: int | None = None, data_ontem: date | None = None) -> Path:
    snap = foto_ontem(data_ontem)
    recap = highlight_mes(mes) if mes else None

    template_path = TEMPLATE_DIR / "email_template_v3.md"
    content = template_path.read_text(encoding="utf-8")

    hoje = datetime.now()
    mes_snap = snap["data_ontem"].month

    # Placeholders globais
    content = content.replace("{{ data_hoje }}", hoje.strftime("%d/%m/%Y"))
    content = content.replace("{{ tendencia }}", snap["tendencia"])
    content = content.replace("{{ hora_geracao }}", hoje.strftime("%H:%M"))

    # Bloco RECAP
    if recap:
        content = content.replace("{{ mes_nome }}", MESES_PT[recap["mes"]])
        content = content.replace("{{ ano }}", str(recap["ano"]))
        content = content.replace("{{ ano_ant }}", str(recap["ano"] - 1))
        content = content.replace("{{ recap_total }}", _brl(recap["total"]))
        content = content.replace("{{ recap_meta }}", _brl(recap["meta"]))
        content = content.replace("{{ recap_pct_meta }}", f"{recap['pct_meta']:.1f}")
        content = content.replace("{{ recap_yoy_sinal }}", _sinal(recap["yoy_pct"]))
        content = content.replace("{{ recap_yoy_abs }}", f"{abs(recap['yoy_pct']):.1f}")
        content = content.replace("{{ recap_total_ant }}", _brl(recap["total_ano_ant"]))
        content = content.replace("{{ recap_melhor_dia }}", recap["melhor_dia"].strftime("%d/%m") if recap["melhor_dia"] else "N/A")
        content = content.replace("{{ recap_melhor_dia_valor }}", _brl(recap["melhor_dia_valor"]))
        content = content.replace("{{ recap_top_filiais }}", _filiais_md(recap["top_filiais"]))
        content = content.replace("{{ recap_cliente_nome }}", recap["cliente_destaque"][0])
        content = content.replace("{{ recap_cliente_valor }}", _brl(recap["cliente_destaque"][1]))
        content = content.replace("{{ recap_anomalia }}", _anomalia_md(recap["anomalia"]))
    else:
        # Semana 2 em diante: remover seção recap
        import re
        content = re.sub(r"## 📅 RECAP.*?---\n", "", content, flags=re.DOTALL)

    # Bloco SNAPSHOT
    _DIAS_PT = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
    data_ontem_fmt = f"{snap['data_ontem'].strftime('%d/%m/%Y')} ({_DIAS_PT[snap['data_ontem'].weekday()]})"
    content = content.replace("{{ data_ontem }}", data_ontem_fmt)
    content = content.replace("{{ snap_total }}", _brl(snap["total"]))
    content = content.replace("{{ snap_nfs }}", str(snap["nfs"]))
    content = content.replace("{{ snap_top_vendedores }}", _vendedores_md(snap["top_vendedores"]))
    content = content.replace("{{ snap_top_filiais }}", _vendedores_md(snap["top_filiais"]))
    content = content.replace("{{ snap_acumulado_mes }}", _brl(snap["acumulado_mes"]))
    content = content.replace("{{ mes_atual_nome }}", MESES_PT[mes_snap])
    content = content.replace("{{ snap_meta_mes }}", _brl(snap["meta_mes"]))
    content = content.replace("{{ snap_pct_meta }}", f"{snap['pct_meta']:.1f}")
    content = content.replace("{{ snap_dias_restantes }}", str(snap["dias_restantes"]))
    content = content.replace("{{ snap_yoy_sinal }}", _sinal(snap["yoy_pct"]))
    content = content.replace("{{ snap_yoy_abs }}", f"{abs(snap['yoy_pct']):.1f}")
    content = content.replace("{{ snap_total_ano_ant }}", _brl(snap["total_mes_ano_ant"]))
    content = content.replace("{{ snap_delta_tend_sinal }}", _sinal(snap["delta_tendencia"]))
    content = content.replace("{{ snap_delta_tend }}", f"{abs(snap['delta_tendencia']):.1f}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"DAILY_ROBERTO_{hoje.strftime('%Y%m%d_%H%M')}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mes", type=int, default=None)
    args = parser.parse_args()
    path = gerar_email(mes=args.mes)
    print(f"[OK] {path}")
```

- [ ] **Step 2: Verificar importações sem erro**

```bash
python -c "from src.generator import gerar_email; print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/generator.py
git commit -m "feat(generator): orquestrar recap + snapshot com template v3"
```

---

## Task 7: Criar run_daily.py

**Files:**

- Create: `run_daily.py`

- [ ] **Step 1: Criar `run_daily.py` na raiz do projeto**

```python
"""
run_daily.py — ponto de entrada do Inova Daily.

Uso:
    python run_daily.py --mes 1   # semana 1: recap Janeiro + snapshot
    python run_daily.py --mes 2   # semana 1: recap Fevereiro + snapshot
    python run_daily.py           # após semana 1: apenas snapshot
"""
import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

# Garantir que src/ é encontrado
sys.path.insert(0, str(Path(__file__).parent))

from src.config import M2_LOG_PATH, M2_CACHE_PATH, M2_RUN_SCRIPT


def _m2_atualizado() -> bool:
    hoje_str = date.today().strftime("%Y-%m-%d")
    if M2_LOG_PATH.exists():
        ultima_linha = M2_LOG_PATH.read_text(encoding="utf-8", errors="ignore").strip().split("\n")[-1]
        return hoje_str in ultima_linha
    if M2_CACHE_PATH.exists():
        import os
        mtime = date.fromtimestamp(os.path.getmtime(M2_CACHE_PATH))
        return mtime == date.today()
    return False


def _atualizar_m2() -> None:
    print("[M2] Cache desatualizado. Executando motor de faturamento (~90s)...")
    result = subprocess.run(
        [sys.executable, str(M2_RUN_SCRIPT), "--no-cache"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[ERRO M2]\n{result.stderr}")
        sys.exit(1)
    print("[M2] Atualizado com sucesso.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerar e-mail executivo Inova Daily")
    parser.add_argument("--mes", type=int, default=None,
                        help="Mês do recap semana 1 (1=Jan, 2=Fev, ..., 5=Mai)")
    parser.add_argument("--skip-m2-check", action="store_true",
                        help="Pular verificação de atualização do M2 (usar cache existente)")
    args = parser.parse_args()

    if not args.skip_m2_check and not _m2_atualizado():
        _atualizar_m2()

    from src.generator import gerar_email
    output_path = gerar_email(mes=args.mes)
    print(f"\n✅ E-mail gerado: {output_path}")
    print("   → Abra o arquivo, copie o conteúdo e envie para Roberto.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Testar o help**

```bash
python run_daily.py --help
```

Esperado: exibir usage com `--mes` e `--skip-m2-check`

- [ ] **Step 3: Commit**

```bash
git add run_daily.py
git commit -m "feat(run-daily): CLI com verificação M2 e geração do e-mail"
```

---

## Task 8: Smoke test — gerar e-mail de segunda-feira

**Files:** nenhum novo arquivo

- [ ] **Step 1: Rodar todos os testes unitários**

```bash
python -m pytest tests/test_faturamento.py tests/test_recap_mensal.py tests/test_snapshot_diario.py -v
```

Esperado: `15 passed`

- [ ] **Step 2: Gerar e-mail de segunda (Janeiro + snapshot sexta 15/05)**

```bash
python run_daily.py --mes 1 --skip-m2-check
```

Esperado: `✅ E-mail gerado: data\outputs\DAILY_ROBERTO_YYYYMMDD_HHMM.md`

- [ ] **Step 3: Abrir e inspecionar o output**

```bash
python -c "
from pathlib import Path
import os, glob
files = sorted(glob.glob('data/outputs/DAILY_ROBERTO_*.md'))
latest = files[-1]
print(Path(latest).read_text(encoding='utf-8'))
"
```

Verifique visualmente:

- [ ] Cabeçalho com data de hoje e sinal de tendência
- [ ] Seção RECAP de Janeiro com faturamento, meta, YoY, melhor dia, top filiais, cliente destaque
- [ ] Seção FOTO DE ONTEM com faturamento, NFs, vendedores, filiais
- [ ] Acumulado do mês com % da meta e comparativo 2025
- [ ] Nenhum placeholder `{{ ... }}` restante no texto

- [ ] **Step 4: Se houver placeholder restante, identificar e corrigir em generator.py**

```bash
python -c "
from pathlib import Path
import glob
files = sorted(glob.glob('data/outputs/DAILY_ROBERTO_*.md'))
content = Path(files[-1]).read_text(encoding='utf-8')
import re
placeholders = re.findall(r'\{\{[^}]+\}\}', content)
print('Placeholders restantes:', placeholders)
"
```

Esperado: `Placeholders restantes: []`

- [ ] **Step 5: Commit final**

```bash
git add .
git commit -m "feat(inova-daily): pipeline completo pronto para entrega segunda 18/05"
```
