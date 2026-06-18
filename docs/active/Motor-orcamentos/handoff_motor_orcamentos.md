# Handoff: Motor de Orçamentos

## 📅 Status Atual (Sessão Encerrada)
**Data:** 11/06/2026
**Branch:** `feat/lead-csc-pops-retorno-contato`
**Objetivo Atingido:** Validação da extração de cancelados diretamente via Microsoft Fabric e integração no pipeline unificado de orçamentos.

## 🛠️ O que foi construído
1. **Infraestrutura Base (`src/config.py` e `run.py`)**:
   - Mapeamento das URLs e diretórios (`data/output`).
   - Reaproveitamento do perfil de navegador persistente do projeto `dashboard-inova-data-export` para evitar bloqueios de login/SSO.
2. **Engenharia de Extração de Orçamentos Abertos (`src/extract.py` - Scraper)**:
   - Implementada a função `extrair_orcamentos_abertos(data_inicio, data_fim)`.
   - Navegação automatizada para a aba "Orçamento em Aberto" do Power BI Embedded.
   - **Tratamento de DOM (Power BI Quirks)**: Mapeamento de `.tableEx` / `.pivotTable` e estado `.wait_for(state="attached")`.
3. **Engenharia de Extração de Orçamentos Cancelados (`src/extract.py` - Fabric)**:
   - Implementada a função `extrair_orcamentos_cancelados_fabric(data_inicio, data_fim)`.
   - Consulta direta via JDBC no Microsoft Fabric na tabela de itens `VS3010` (Protheus) com filtro por `VS3_MOTPED` não vazio.
   - **Normalização de Dados**: Decodificação dos motivos de cancelamento com dicionário de 8 códigos e formatação de filiais de interesse (`02%` e `03%`).
4. **Validação e Match Rate (Prova Real)**:
   - Testada e validada equivalência de orçamentos cancelados entre o Power BI e o Fabric. O match rate final de orçamentos únicos foi de **97.77%** no histórico completo de 2025/2026 (10.317 no Power BI vs 10.552 no Fabric).
5. **Integração no Pipeline Principal (`run.py`)**:
   - Integrado o script `run.py` para executar de forma unificada:
     - `extrair_orcamentos_abertos` (Scraper) -> `data/output/data.xlsx` (546 linhas atuais).
     - `extrair_orcamentos_cancelados_fabric` (Fabric) -> `data/output/tabela_orçamentos_cancelados.xlsx` (61.839 linhas históricas).

## 🚀 Próximos Passos (Próxima Sessão)
1. **Transformação & Limpeza (`src/transform.py` - a ser criado)**:
   - Organizar as colunas, tipagens e limpar DataFrames gerados de ambas as extrações.
2. **Cruzamento de Dados / Enriquecimento (Fabric)**:
   - Para os **Orçamentos Abertos** (vindos do Scraper), efetuar o cruzamento com tabelas do Fabric (ex: vendedores, informações de clientes e peças) para enriquecer o DataFrame final com "mais informações".
3. **Migração de Pipeline**:
   - ICM-izar os estágios na pasta do pipeline do potencial de clientes para integração final.

