# Ajuste Final de Conformidade (Motor CEVAP v4) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Alinhar o output do motor `consolidate_cevap.py` com o Dicionário de Dados oficial (`docs/DICIONARIO_DADOS_CEVAP.md`), garantindo as 17 colunas solicitadas e a qualidade dos dados.

**Architecture:** Refatoração baseada no grão de Grupo Econômico (Raiz 8) para inatividade e saldos, assegurando a fidelidade de cada coluna.

**Tech Stack:** Python, Pandas, Openpyxl.

---

### Task 1: Mapeamento Final e Inclusão de Colunas

**Files:**
- Modify: `C:/Projetos/Inova/Motor CEVAP/scripts/consolidate_cevap.py`

**Step 1: Mapear 'Equipamentos' e 'N_Orcamento_12m'**
- Incluir lógica de leitura e agrupamento para `dataset_ouro_maquinas_v1.parquet` (Consolidar modelos).
- Incluir leitura das tabelas de orçamento (`abertos.xlsx` e `cancelados.xlsx`), unificar e agrupar por Raiz (contagem).

**Step 2: Ajuste de Nomes e Ordem**
- Renomear colunas para bater com o Dicionário: `Cidade`, `Cliente`, `Classificacao` (Segmento), `Telefones`, `E-mail`, `SOW`, `DT_Ultima_Compra`, `Valor_12m`, `Pontos_Seedz`, `InovaPay_Limite_Dis`, `Equipamentos`, `N_Orcamento_12m`, `Data_Tentativa_1`, `Status_Contato_1`, `Data_Tentativa_2`, `Status_Contato_2`, `Observacao`.

**Step 3: Commit**
```bash
git add scripts/consolidate_cevap.py
git commit -m "feat: complete column mapping as per dictionary"
```

### Task 2: Validação Automatizada (TDD)

**Files:**
- Modify: `C:/Projetos/Inova/Motor CEVAP/tests/test_columns.py`

**Step 1: Atualizar Teste**
- Atualizar `expected_cols` com as 17 colunas exatas.

**Step 2: Executar TDD**
- Rodar: `python tests/test_columns.py`
- Confirmar PASS.

**Step 3: Commit**
```bash
git add tests/test_columns.py
git commit -m "test: ensure column integrity"
```
