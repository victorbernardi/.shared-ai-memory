# Plan: Shared Sync Motor Identidade v11.7 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Atualizar o script de batch v11.7 para exportar os resultados no formato Parquet para a área compartilhada, mantendo a compatibilidade de colunas com o ecossistema Inova.

**Architecture:** Modificação do script `seo_ge_batch_v11_7.py` para integrar o `shared/config.py`, normalizar o schema de saída e salvar em dois destinos (Local XLSX e Shared Parquet).

**Tech Stack:** Python, Pandas, Pathlib.

---

### Task 1: Preparação e Importação de Configs
**Files:**
- Modify: `c:\Projetos\Inova\pipelines\potencial-clientes\00_Motor_Identidade\scripts\seo_ge_batch_v11_7.py`

**Step 1: Adicionar importação dinâmica do config compartilhado**
Adicionar o bloco de código que localiza a pasta `shared` e importa `SHARED_DATA`.

**Step 2: Substituir caminhos hardcoded**
Substituir `DIR_PROJETO`, `DIR_RESULTADOS` e `DIR_CACHE` por caminhos baseados no `Path(__file__)` ou `SHARED_DATA`.

**Step 3: Validar imports**
Rodar `python seo_ge_batch_v11_7.py` (apenas check de erro de import, sem execução total).

### Task 2: Normalização do Schema (Maestro Ouro)
**Files:**
- Modify: `c:\Projetos\Inova\pipelines\potencial-clientes\00_Motor_Identidade\scripts\seo_ge_batch_v11_7.py`

**Step 1: Renomear colunas base**
Mapear `A1_NOME` -> `NOME_ORIGINAL` e `A1_CGC` -> `CNPJ_ORIGINAL`.

**Step 2: Calcular colunas de Grupo**
Criar as colunas `NOME_GRUPO_ORIGINAL` (extraindo do prefixo "GRUPO "), `NOME_DNA_GRUPO` e `ID_GRUPO_MAESTRO`.

**Step 3: Reordenar e filtrar colunas**
Garantir que o dataframe final tenha apenas as 11 colunas do schema ouro.

### Task 3: Exportação e Backup
**Files:**
- Modify: `c:\Projetos\Inova\pipelines\potencial-clientes\00_Motor_Identidade\scripts\seo_ge_batch_v11_7.py`

**Step 1: Implementar Backup Preventivo**
Adicionar lógica para renomear o arquivo `dataset_ouro_identidade.parquet` existente para `.bak` antes de sobrescrever.

**Step 2: Salvar em Parquet (Shared)**
Adicionar o `to_parquet` para o caminho `SHARED_DATA / 'dataset_ouro_identidade.parquet'`.

**Step 3: Teste de Execução Final**
Rodar o batch completo e verificar se os dois arquivos (XLSX e Parquet) foram gerados com o schema correto.

---
*Assinado: Antigravity (Phase: Strategy)*
