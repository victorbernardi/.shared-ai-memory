# Plano de Execução: Refatoração de Colunas e Dados (Motor CEVAP v4)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ajustar o `consolidate_cevap.py` para produzir a planilha final exatamente conforme o Dicionário de Dados oficial, garantindo a inclusão das 17 colunas solicitadas, a correção do cálculo de inatividade por grupo, a unificação de telefones e a remoção de ruídos (como colunas vazias ou erradas).

**Architecture:** Refatoração baseada no grão de Grupo Econômico (Raiz 8) para inatividade e saldos, garantindo integridade financeira e comercial.

**Tech Stack:** Python, Pandas, Openpyxl (Excel).

---

### Task 1: Ajuste da Lógica de Telefones e Filtros de Colunas

**Files:**

- Modify: `C:/Projetos/Inova/Motor CEVAP/scripts/consolidate_cevap.py`

**Step 1: Renomear Colunas e Garantir Ordem Final**

- Alterar o mapeamento dentro do `df_cevap.rename` para incluir todas as colunas do dicionário.
- Garantir que `cols_finais` liste exatamente as 17 colunas definidas.

**Step 2: Lógica de Contatos**

- Consolidar a lógica de unificação de telefones: `df_cevap["Telefones"] = df_cevap["Telefone_Seedz"].combine_first(df_cevap["A1_TEL"])` (exemplo).
- Aplicar limpeza de strings (apenas números distintos).

**Step 3: Ajuste de Segmentação**

- Garantir que a coluna `Classificacao` (A1, A2, etc.) esteja presente e correta.

---

### Task 2: Validação Automatizada (TDD)

**Files:**

- Modify: `C:/Projetos/Inova/Motor CEVAP/tests/test_columns.py`

**Step 1: Atualizar Teste**

- Atualizar a lista `expected_cols` no `test_columns.py` para refletir as 17 colunas exatas do Dicionário (`docs/DICIONARIO_DADOS_CEVAP.md`).

**Step 2: Executar TDD**

- Rodar o teste e confirmar o "PASS".

---

### Task 3: Canary Deployment e Finalização

**Step 1: Canary Deployment**

- Executar o script com `python scripts/consolidate_cevap.py`.
- Verificar se o arquivo gerado em `data/` existe e está desbloqueado.

**Step 2: Log**

- Registrar no `canary-log.md` a conclusão da refatoração de colunas.
