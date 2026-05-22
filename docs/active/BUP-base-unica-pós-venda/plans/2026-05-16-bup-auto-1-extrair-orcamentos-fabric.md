# BUP-AUTO-1: Extrair Orçamentos Direto do Fabric — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir a exportação manual do PowerBI por um script `scripts/extract_orcamentos.py` que consulta a `VS1010` no Fabric e salva os dois xlsx em `shared/data/`, replicando exatamente o schema atual.

**Architecture:** Script único ETL puro — conecta ao Fabric via `ConexaoFabric` (shared/config.py), executa duas queries na VS1010 (abertos + cancelados), salva em `shared/data/`. Sem lógica de negócio, sem transformações além do que o PowerBI já fazia. BUP e CEVAP continuam lendo os mesmos caminhos de sempre.

**Tech Stack:** pandas, ConexaoFabric (shared/fabric_db.py), openpyxl, pytest

---

## Contexto

Os xlsx que o PowerBI exporta manualmente:

| Arquivo | Schema | Grain |
|---------|--------|-------|
| `shared/data/tabela_orçamentos_abertos.xlsx` | `Num Orc, Filial, Cliente, Data Abertura, Data Validade, Reservado, Orc. em Aberto, Tempo Orc em Aberto` | orçamento |
| `shared/data/tabela_orçamentos_cancelados.xlsx` | `Codigo da Peça, Número Orc, Cliente, Filial, Data Orc, Canceladas, Motivo Cancelado` | peça |

A tabela Fabric é `VS1010` (orçamentos Protheus). O BUP já a consulta em `scripts/consolidate_bup.py` para pegar o último orçamento por cliente ativo. O campo de join com cliente é `SA1010` via `VS1_CLIFAT` / `VS1_LOJA`.

**Caminhos importantes:**

```python
# shared/config.py
from config import SHARED_DATA, FABRIC_SERVER, FABRIC_BANCO, FABRIC_JVM, FABRIC_JAR, FABRIC_CONNECTOR
```

**Profundidade N para parents:**

- `projects/BUP-base-unica-pós-venda/scripts/extract_orcamentos.py` → `parents[3]` para chegar na raiz Inova

---

## File Map

| Ação | Arquivo |
|------|---------|
| Create | `scripts/extract_orcamentos.py` |
| Create | `tests/test_extract_orcamentos.py` |

---

### Task 1: Explorar VS1010 no Fabric — mapear campos de status e motivo

**Files:**

- Create: `scripts/scratch_explorar_vs1010.py` (rascunho, deletar após)

Esta task não tem testes — é exploração pura. O objetivo é descobrir:

1. Quais valores de campo identificam orçamento "aberto" vs "cancelado"
2. Qual campo contém o motivo do cancelamento
3. Qual campo contém o valor do orçamento (equivalente a "Orc. em Aberto")
4. Qual campo contém o código da peça (para cancelados)
5. Qual campo contém a filial no formato `0201 - Contagem` (ou se precisa join)

- [ ] **Step 1: Criar script de exploração**

```python
# scripts/scratch_explorar_vs1010.py
import sys
from pathlib import Path

_shared = Path(__file__).parents[3] / "shared"
sys.path.insert(0, str(_shared))
from config import SHARED_DATA, FABRIC_SERVER, FABRIC_BANCO, FABRIC_JVM, FABRIC_JAR
from fabric_db import ConexaoFabric

DATA_DIR = Path(__file__).parent.parent / "data"

db = ConexaoFabric(
    servidor=FABRIC_SERVER,
    banco_dados=FABRIC_BANCO,
    caminho_jvm=str(FABRIC_JVM),
    caminho_jar=str(FABRIC_JAR),
    cache_dir=str(DATA_DIR),
)

# 1. Schema da VS1010
df_schema = db.consultar("""
    SELECT TOP 1 * FROM VS1010 WHERE D_E_L_E_T_ = ''
""", use_cache=True, save_cache=True)
print("=== COLUNAS VS1010 ===")
print(df_schema.columns.tolist())
print(df_schema.dtypes)
print(df_schema.head(2).to_string())

# 2. Valores únicos de campos de status/situação
df_status = db.consultar("""
    SELECT DISTINCT VS1_SITUAC, COUNT(*) as qtd
    FROM VS1010
    WHERE D_E_L_E_T_ = ''
      AND (VS1_FILIAL LIKE '02%' OR VS1_FILIAL LIKE '03%')
    GROUP BY VS1_SITUAC
    ORDER BY qtd DESC
""", use_cache=True, save_cache=True)
print("\n=== STATUS (VS1_SITUAC) ===")
print(df_status)

# 3. Valores únicos de motivo cancelamento (se houver campo)
# Tentar campos comuns: VS1_MOTCNC, VS1_MOTCAN, etc.
for campo in ["VS1_MOTCNC", "VS1_MOTCAN", "VS1_MOTIVO", "VS1_OBS"]:
    try:
        df_mot = db.consultar(f"""
            SELECT DISTINCT {campo}, COUNT(*) as qtd
            FROM VS1010
            WHERE D_E_L_E_T_ = ''
              AND {campo} IS NOT NULL AND {campo} != ''
              AND (VS1_FILIAL LIKE '02%' OR VS1_FILIAL LIKE '03%')
            GROUP BY {campo}
            ORDER BY qtd DESC
        """, use_cache=True, save_cache=True)
        print(f"\n=== {campo} ===")
        print(df_mot.head(10))
    except Exception as e:
        print(f"{campo}: erro — {e}")

# 4. Amostra de orçamentos recentes com campos-chave
df_amostra = db.consultar("""
    SELECT TOP 20
        VS1_FILIAL, VS1_NUM, VS1_CLIFAT, VS1_LOJA,
        VS1_DATORC, VS1_DATVAL, VS1_SITUAC, VS1_TOTAL,
        VS1_CODVEN
    FROM VS1010
    WHERE D_E_L_E_T_ = ''
      AND (VS1_FILIAL LIKE '02%' OR VS1_FILIAL LIKE '03%')
      AND VS1_DATORC >= '2026-01-01'
    ORDER BY VS1_DATORC DESC
""", use_cache=True, save_cache=True)
print("\n=== AMOSTRA RECENTE ===")
print(df_amostra.to_string())
```

- [ ] **Step 2: Rodar o script**

```
cd C:\Projetos\Inova\projects\BUP-base-unica-pós-venda
python scripts/scratch_explorar_vs1010.py
```

- [ ] **Step 3: Anotar os resultados**

Preencha com o que o script retornar:

```
Campo status "aberto":    VS1_SITUAC = ___
Campo status "cancelado": VS1_SITUAC = ___  (ou outro campo: ___)
Campo motivo cancelamento: ___
Campo valor orçamento:    VS1_TOTAL (ou ___?)
Campo código peça:        ___ (pode estar em tabela de itens VS2010?)
Campo filial (formato):   VS1_FILIAL = "0201" → precisa join com nome? ___
```

> ⚠️ **Se os campos de peça/motivo não estiverem na VS1010:** Os cancelamentos por peça provavelmente estão na tabela de itens `VS2010` (itens do orçamento) com join na VS1010 para status. Explorar com:
>
> ```sql
> SELECT TOP 5 * FROM VS2010 WHERE D_E_L_E_T_ = ''
> ```

- [ ] **Step 4: Deletar o rascunho**

```
del scripts\scratch_explorar_vs1010.py
```

---

### Task 2: Implementar `extract_orcamentos.py` com TDD

**Files:**

- Create: `scripts/extract_orcamentos.py`
- Create: `tests/test_extract_orcamentos.py`

> ⚠️ **Antes de implementar:** preencha as constantes abaixo com os valores descobertos na Task 1.

- [ ] **Step 1: Criar teste falhando para `extrair_abertos()`**

```python
# tests/test_extract_orcamentos.py
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch


def _df_abertos_fabric():
    """Simula retorno bruto da VS1010 para orçamentos abertos."""
    return pd.DataFrame({
        "VS1_NUM":    ["00016325", "00017928"],
        "VS1_FILIAL": ["0202", "0203"],
        "NOME_FILIAL": ["Tanguá", "Serra"],          # vem do join SA1010 ou mapa
        "A1_NOME":    ["Barcas Rio", "Josenir Hubner"],
        "VS1_DATORC": pd.to_datetime(["2025-04-29", "2025-06-09"]),
        "VS1_DATVAL": pd.to_datetime(["2026-05-20", "2028-12-25"]),
        "RESERVADO":  ["NÃO RESERVADO", "NÃO RESERVADO"],
        "VS1_TOTAL":  [463693.41, 1717.59],
        "DIAS_ABERTO": [379.0, 338.0],
    })


def test_extrair_abertos_retorna_schema_correto():
    from scripts.extract_orcamentos import extrair_abertos

    mock_db = MagicMock()
    mock_db.consultar.return_value = _df_abertos_fabric()

    df = extrair_abertos(mock_db)

    assert list(df.columns) == [
        "Num Orc", "Filial", "Cliente",
        "Data Abertura", "Data Validade",
        "Reservado", "Orc. em Aberto", "Tempo Orc em Aberto",
    ]
    assert len(df) == 2
    assert df["Num Orc"].iloc[0] == "00016325"
```

- [ ] **Step 2: Rodar — deve falhar**

```
cd C:\Projetos\Inova\projects\BUP-base-unica-pós-venda
pytest tests/test_extract_orcamentos.py::test_extrair_abertos_retorna_schema_correto -v
```

Esperado: `FAILED` com `ModuleNotFoundError`

- [ ] **Step 3: Criar `scripts/extract_orcamentos.py` com `extrair_abertos()`**

> Substitua `STATUS_ABERTO`, `NOME_FILIAL_CAMPO` e `JOIN_FILIAL` pelos valores da Task 1.

```python
# scripts/extract_orcamentos.py
import logging
from datetime import datetime, date
from pathlib import Path
import sys

import pandas as pd

_shared = Path(__file__).parents[3] / "shared"
sys.path.insert(0, str(_shared))
from config import SHARED_DATA, FABRIC_SERVER, FABRIC_BANCO, FABRIC_JVM, FABRIC_JAR
from fabric_db import ConexaoFabric

# ── Preencher com valores descobertos na Task 1 ──────────────────────────────
STATUS_ABERTO    = "A"      # ← ajustar com valor real de VS1_SITUAC
STATUS_CANCELADO = "C"      # ← ajustar com valor real
CAMPO_MOTIVO     = "VS1_MOTCNC"  # ← ajustar com campo real
# ─────────────────────────────────────────────────────────────────────────────

_FILIAIS = {
    "0201": "0201 - Contagem",
    "0202": "0202 - Tanguá",
    "0203": "0203 - Serra",
    "0301": "0301 - Uberlândia",
}

_DATA_HOJE = datetime.now().date()


def _fmt_filial(codigo: str) -> str:
    return _FILIAIS.get(str(codigo).strip(), str(codigo).strip())


def extrair_abertos(db: ConexaoFabric) -> pd.DataFrame:
    query = f"""
        SELECT
            v.VS1_NUM       AS [Num Orc],
            v.VS1_FILIAL,
            c.A1_NOME       AS [Cliente],
            v.VS1_DATORC    AS [Data Abertura],
            v.VS1_DATVAL    AS [Data Validade],
            'NÃO RESERVADO' AS [Reservado],
            v.VS1_TOTAL     AS [Orc. em Aberto]
        FROM VS1010 v
        INNER JOIN SA1010 c
            ON c.A1_COD = v.VS1_CLIFAT
           AND c.A1_LOJA = v.VS1_LOJA
           AND c.D_E_L_E_T_ = ''
        WHERE v.D_E_L_E_T_ = ''
          AND v.VS1_SITUAC = '{STATUS_ABERTO}'
          AND (v.VS1_FILIAL LIKE '02%' OR v.VS1_FILIAL LIKE '03%')
    """
    df = db.consultar(query, use_cache=False)
    assert df is not None and not df.empty, "Nenhum orçamento aberto encontrado"

    df["Data Abertura"] = pd.to_datetime(df["Data Abertura"])
    df["Data Validade"] = pd.to_datetime(df["Data Validade"])
    df["Tempo Orc em Aberto"] = (
        pd.Timestamp(_DATA_HOJE) - df["Data Abertura"]
    ).dt.days.astype(float)
    df["Filial"] = df["VS1_FILIAL"].apply(_fmt_filial)

    return df[[
        "Num Orc", "Filial", "Cliente",
        "Data Abertura", "Data Validade",
        "Reservado", "Orc. em Aberto", "Tempo Orc em Aberto",
    ]]


def extrair_cancelados(db: ConexaoFabric) -> pd.DataFrame:
    # ── Implementar após confirmar se cancelados vêm de VS1010 ou VS2010 ──
    # Se VS2010 (itens): grain = peça, join VS1010 para status e SA1010 para cliente
    # Se VS1010 (cabeçalho): grain = orçamento, sem código de peça
    raise NotImplementedError("Implementar após exploração da Task 1")


def salvar_xlsx(df: pd.DataFrame, caminho: Path) -> None:
    df.to_excel(caminho, index=False)
    logging.info("Salvo: %s (%d linhas)", caminho, len(df))


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    db = ConexaoFabric(
        servidor=FABRIC_SERVER,
        banco_dados=FABRIC_BANCO,
        caminho_jvm=str(FABRIC_JVM),
        caminho_jar=str(FABRIC_JAR),
        cache_dir=str(Path(__file__).parent.parent / "data"),
    )

    logging.info("Extraindo orçamentos abertos...")
    df_abertos = extrair_abertos(db)
    salvar_xlsx(df_abertos, SHARED_DATA / "tabela_orçamentos_abertos.xlsx")

    logging.info("Extraindo orçamentos cancelados...")
    df_cancelados = extrair_cancelados(db)
    salvar_xlsx(df_cancelados, SHARED_DATA / "tabela_orçamentos_cancelados.xlsx")

    logging.info("Concluído.")


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: Rodar — deve passar**

```
pytest tests/test_extract_orcamentos.py::test_extrair_abertos_retorna_schema_correto -v
```

Esperado: `PASSED`

- [ ] **Step 5: Adicionar testes de schema para `extrair_cancelados()`**

> ⚠️ Implemente `extrair_cancelados()` somente após confirmar na Task 1 se os dados de peça/motivo estão na `VS1010` ou na `VS2010`. Adapte a query e o mock abaixo conforme o resultado.

```python
def _df_cancelados_fabric():
    """Simula retorno bruto para cancelados (ajustar conforme Task 1)."""
    return pd.DataFrame({
        "COD_PECA":   ["Z957366", "Z32156"],
        "VS1_NUM":    [178608.0, 167546.0],
        "A1_NOME":    ["HM TRATORPECAS LTDA", "GILBERTO ANTENOR APPELT"],
        "VS1_FILIAL": ["0201", "0201"],
        "VS1_DATORC": pd.to_datetime(["2025-10-02", "2025-07-21"]),
        "VALOR_CANC": [13.904, 158.213],
        "MOTIVO":     ["APENAS CONSULTA DE PRECO", "INDISPONIBILIDADE DE PECA"],
    })


def test_extrair_cancelados_retorna_schema_correto():
    from scripts.extract_orcamentos import extrair_cancelados

    mock_db = MagicMock()
    mock_db.consultar.return_value = _df_cancelados_fabric()

    df = extrair_cancelados(mock_db)

    assert list(df.columns) == [
        "Codigo da Peça", "Número Orc", "Cliente",
        "Filial", "Data Orc", "Canceladas", "Motivo Cancelado",
    ]
    assert len(df) == 2
    assert df["Motivo Cancelado"].iloc[0] == "APENAS CONSULTA DE PRECO"
```

- [ ] **Step 6: Implementar `extrair_cancelados()` (adaptar query conforme Task 1)**

Se cancelados vierem da **VS2010** (itens), a query base é:

```sql
SELECT
    i.VS2_CODPRO  AS [Codigo da Peça],
    i.VS2_NUM     AS [Número Orc],
    c.A1_NOME     AS [Cliente],
    v.VS1_FILIAL,
    v.VS1_DATORC  AS [Data Orc],
    i.VS2_QTDVEN  AS [Canceladas],   -- ← confirmar campo de valor/qtd cancelada
    v.<CAMPO_MOTIVO> AS [Motivo Cancelado]
FROM VS2010 i
INNER JOIN VS1010 v
    ON v.VS1_NUM = i.VS2_NUM AND v.VS1_FILIAL = i.VS2_FILIAL AND v.D_E_L_E_T_ = ''
INNER JOIN SA1010 c
    ON c.A1_COD = v.VS1_CLIFAT AND c.A1_LOJA = v.VS1_LOJA AND c.D_E_L_E_T_ = ''
WHERE i.D_E_L_E_T_ = ''
  AND v.VS1_SITUAC = '<STATUS_CANCELADO>'
  AND (v.VS1_FILIAL LIKE '02%' OR v.VS1_FILIAL LIKE '03%')
  AND v.VS1_DATORC >= '2025-01-01'
```

- [ ] **Step 7: Rodar suite de testes**

```
pytest tests/test_extract_orcamentos.py -v
```

Esperado: 2 testes `PASSED`

- [ ] **Step 8: Commit**

```
git add scripts/extract_orcamentos.py tests/test_extract_orcamentos.py
git commit -m "feat(bup-auto-1): extract_orcamentos.py — VS1010 → shared/data xlsx"
```

---

### Task 3: Smoke test com dados reais + validação de schema

**Files:**

- Nenhum arquivo modificado — verificação manual

- [ ] **Step 1: Rodar contra o Fabric real**

```
python scripts/extract_orcamentos.py
```

- [ ] **Step 2: Comparar schema com os xlsx anteriores**

```python
import pandas as pd

# Novo (gerado pelo script)
novo = pd.read_excel("C:/Projetos/Inova/shared/data/tabela_orçamentos_abertos.xlsx")
print("Novo — colunas:", novo.columns.tolist())
print("Novo — shape:", novo.shape)
print(novo.head(3).to_string())

# Verificar que não há NaN em colunas obrigatórias
assert novo["Num Orc"].notna().all(), "Num Orc com nulos"
assert novo["Cliente"].notna().all(), "Cliente com nulos"
assert novo["Orc. em Aberto"].notna().all(), "Valor com nulos"
print("Schema OK")
```

- [ ] **Step 3: Rodar Motor BUP para validar integração**

```
python scripts/consolidate_bup.py
```

Verificar que `dataset_final_estrategico_v1.parquet` é gerado sem erros.

- [ ] **Step 4: Commit final**

```
git add -p
git commit -m "test(bup-auto-1): smoke test VS1010 → xlsx → BUP validado"
```

---

## Notas para execução

- `STATUS_ABERTO` e `STATUS_CANCELADO` em `extract_orcamentos.py` **devem ser preenchidos** com os valores descobertos na Task 1 antes de rodar a Task 2
- Se orçamentos cancelados estiverem na `VS2010` (itens), o join muda — a query sugerida na Task 2 Step 6 já cobre esse caso
- O campo `Reservado` nos abertos pode exigir lógica adicional se houver valores além de "NÃO RESERVADO" — verificar na exploração
