# Motor M6 Data Restructuring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Separar as visões de Metas (Agregada) e Clientes (Granular) e corrigir o mapeamento da filial CRC.

**Architecture:** Transição de uma tabela única "Flat" para um modelo Multi-Tabela (Estrela simplificado), onde as Metas não dependem do grão de Cliente.

**Tech Stack:** Python (Pandas), Excel (XlsxWriter), HTML/JS (Chart.js).

---

### Task 1: Limpeza de Bases (Filtro Depósito Fechado)

**Files:**
- Modify: `C:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos\Wave3_Processador_Metas.py`
- Modify: `C:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos\Wave4_Orquestrador_M6.py`

**Step 1: Aplicar filtro na Wave 3**
Garantir que a filial `0205` seja removida do processamento de metas.

**Step 2: Aplicar filtro na Wave 4**
Remover `0205` das bases de faturamento e funil antes de qualquer agrupamento.

---

### Task 2: Refatoração do Mapeamento de Filiais e Segmentos

**Files:**
- Modify: `C:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos\Wave4_Orquestrador_M6.py`

**Step 1: Ajustar map_nomes_filiais**
Alterar `'0211': 'CONTAGEM'` e remover `'0205'`.

**Step 2: Forçar Segmento CRC**
Na lógica de vendas e funil, se a filial original for `0211`, forçar `SEGMENTO_M6 = 'Peças CRC'`.

---

### Task 3: Criação da Tabela de Performance (Agregada)

**Files:**
- Modify: `C:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos\Wave4_Orquestrador_M6.py`

**Step 1: Gerar df_performance**
Realizar o merge de Metas, Vendas e Funil apenas nos campos: `['NOME_FILIAL', 'SEGMENTO_M6', 'ANO', 'MES_NOME']`.

**Step 2: Validar Totais**
Garantir que o `VALOR_META` total nesta tabela seja idêntico ao total processado na Wave 3.

---

### Task 4: Criação da Tabela Transacional (Granular)

**Files:**
- Modify: `C:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos\Wave4_Orquestrador_M6.py`

**Step 1: Gerar df_transactional**
Concatenar apenas Vendas e Funil, mantendo colunas de Clientes e Quadrantes. **Não incluir linhas de meta aqui.**

---

### Task 5: Atualização do Dashboard HTML (Multi-Source)

**Files:**
- Modify: `C:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos\Wave7_Dashboard_HTML.py`

**Step 1: Exportar dois JSONs**
Exportar `data_performance` e `data_transactional`.

**Step 2: Ajustar Lógica JS**
Os gráficos de KPI e Segmentos devem ler `data_performance`. A tabela de detalhes e filtros de clientes devem ler `data_transactional`.

---

### Task 6: Validação e Canary

**Step 1: Executar fluxo completo**
Rodar Wave 3 -> Wave 4 -> Wave 7.

**Step 2: Verificação Visual**
Abrir `Dashboard_Executivo_M6.html` e validar se os totais batem com o Excel.
