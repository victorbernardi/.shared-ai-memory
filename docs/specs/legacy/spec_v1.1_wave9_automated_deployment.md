# Spec: Wave 9 — Automação de Deployment (OnePage Dashboard) - v1.1

- **Status:** Finalized (Design Lock)
- **Data:** 2026-04-30
- **Autor:** Antigravity (Stout Edition)
- **Versão:** 1.1

## 1. Objetivo
Automatizar a atualização do Dashboard OnePage (`index.html`) garantindo que a publicação dos dados só ocorra após a validação bem-sucedida da **Wave 8 (Auditoria)**.

## 2. Requisitos Refinados

### 2.1 Funcionais
- **Orquestração:** Executar sequencialmente a Wave 4 (Processamento) e a Wave 8 (Auditoria).
- **Extração de Dados:** Converter as abas `GESTAO_PERFORMANCE` e `GESTAO_STATUS_FUNIL` do Excel `Motor_Gestao_M6_v4_3.xlsx` para o formato `data.json`.
- **Shadow Deploy:** Gerar um arquivo temporário (`data_staging.json`) antes de substituir o arquivo de produção.

### 2.2 Validação e Qualidade (O Coração da Spec)
Para evitar bloqueios falsos por granularidade de itens:
- **Paridade Financeira (Soberania):** Diferença absoluta entre CSV e Excel deve ser < R$ 1,00.
- **Integridade Transacional (Novo):** A verificação de duplicatas deve ser feita **agrupando por Chave de Transação** (`NUMERO_ORCAMENTO` ou `NUMERO_NF`). 
  - Se após o agrupamento houver duplicatas da mesma chave, o deploy é bloqueado.
  - Múltiplas linhas com a mesma chave (itens da mesma nota) são permitidas e devem ser somadas.

## 3. Arquitetura Atualizada

### Fluxo de Trabalho (Pipeline)
1. **Wave 4:** Gera o `Motor_Gestao_M6_v4_3.xlsx` com aba `DETALHE_TRANSACIONAL`.
2. **Wave 8 (Auditoria Inteligente):** 
   - Realiza o Cross-Check financeiro.
   - Executa de-duplicação baseada em chaves de transação para validar se há "dobra" de faturamento.
3. **Extractor:** Gera o `data_staging.json`.
4. **Pre-Flight:** Compara totais do JSON com os auditados.
5. **Atomic Swap:** Substitui `data.json` e dispara `aggregator.py`.

## 4. Decision Log
- **Decisão (v1.1):** Aceitar múltiplas linhas por NF no detalhe.
- **Motivo:** O ERP trabalha em nível de item. Agrupar no Master perderia a precisão do ticket médio por item se tentássemos forçar "Zero Linhas Repetidas".
- **Decisão:** Manter a aba `DETALHE_TRANSACIONAL` no Excel.
- **Motivo:** Essencial para a auditoria de qualidade (Root Cause Discovery).

## 5. Plano de Testes (Validação)
- **Teste de Item:** Inserir manualmente dois itens na mesma NF no CSV e verificar se o pipeline aprova (Sucesso esperado na v1.1).
- **Teste de Dobra:** Inserir a mesma NF duas vezes com todos os itens repetidos e verificar se a Auditoria bloqueia (Sucesso esperado).
