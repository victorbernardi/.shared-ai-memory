# Plano de Execução: Análise de Dropout por Subgrupo

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Criar um gráfico de barras horizontais agrupadas (12, 24, 36) para os 5 subgrupos com maior queda de vendas, validando os dados no Fabric.

**Architecture:** Script de laboratório (`scripts/lab_dropout_analysis.py`) que processa o Excel para identificação e o Fabric para auditoria mensal.

**Tech Stack:** Python, Pandas, Matplotlib, SQL (Fabric).

---

### Task 1: Setup do Script de Laboratório e Testes de Lógica
**Files:**
- Create: `scripts/lab_dropout_analysis.py`
- Create: `tests/test_dropout_logic.py`

**Step 1: Escrever teste de falha para o cálculo de Dropout**
```python
import pytest
from scripts.lab_dropout_analysis import calculate_dropout_score

def test_dropout_score_calculation():
    # Cenário: Venda caiu de 100 para 10
    v12, v36 = 10, 100
    score = calculate_dropout_score(v12, v36)
    assert score == pytest.approx(0.108, 0.01) # (10+1)/(100+1)
```

**Step 2: Rodar teste e confirmar falha**
`pytest tests/test_dropout_logic.py`

**Step 3: Implementar a função de cálculo mínima**
```python
def calculate_dropout_score(v12, v36):
    return (v12 + 1) / (v36 + 1)
```

**Step 4: Validar teste**
`pytest tests/test_dropout_logic.py`

---

### Task 2: Enriquecimento e Identificação dos Top 5 (Subgrupos)
**Files:**
- Modify: `scripts/lab_dropout_analysis.py`

**Step 1: Implementar Join entre Excel e Parquet**
```python
def load_and_identify_worst_subgroups(excel_path, mapping_path):
    # 1. Carrega Excel (Item + Vendas)
    # 2. Carrega map_subgrupos.parquet (Item -> COD_SUBGRUPO)
    # 3. pd.merge(df_excel, df_map, on='ITEM', how='left')
    # 4. Agrupar por COD_SUBGRUPO ou DESC_SUBGRUPO
    ...
    return piores_df
```

---

### Task 3: Geração do Gráfico de Barras Agrupadas
**Files:**
- Modify: `scripts/lab_dropout_analysis.py`

**Step 1: Implementar visualização com Matplotlib**
- Criar 3 barras por subgrupo (isoladas: V12, V24, V36).
- Usar legendas "12", "24", "36".
- Salvar em `data/lab_dropout_subgroups.png`.

---

### Task 4: Validação Cruzada (Fabric)
**Files:**
- Modify: `scripts/lab_dropout_analysis.py`

**Step 1: Integrar MotorExtracaoGenerico**
- Para cada um dos 5 subgrupos, rodar a query de tendência mensal.
- Imprimir no terminal o comparativo de volume total (Excel vs Fabric) para auditoria.

---

### Task 5: Execução Final e Verificação
**Step 1: Rodar o laboratório completo**
`python scripts/lab_dropout_analysis.py`

**Step 2: Verificar artefato visual**
Abrir `data/lab_dropout_subgroups.png`.
