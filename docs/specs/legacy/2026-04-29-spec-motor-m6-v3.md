# Spec Técnica: Refatoração Motor M6 (V3 - Gestão de Performance)

**Data:** 2026-04-29  
**Status:** Pesquisa Concluída / Aguardando Implementação  
**Autor:** Antigravity (Stout Edition)

## 1. Objetivo
Migrar o Motor de Relatórios M6 de um modelo de listagem transacional para um modelo de **Gestão Agregada**, focando em produtividade comercial, saúde de pipeline e visibilidade por consultor/origem.

## 2. Abas e Estrutura de Dados

### A. GESTAO_PERFORMANCE
*   **Chave:** Filial + Segmento + Mês.
*   **Colunas:**
    *   `FILIAL_COD`, `NOME_FILIAL`, `SEGMENTO`, `DATA_REFERENCIA` (dd/mm/aaaa), `ANO`, `MES_NOME`.
    *   `VALOR_META`: Meta orçada para o mês.
    *   `VALOR_REALIZADO`: Faturamento líquido real.
    *   `VALOR_FUNIL`: Total de atividade de orçamentos (independente do status).
    *   `GAP_META`: `VALOR_REALIZADO - VALOR_META`.
    *   `%_ATINGIMENTO`: `VALOR_REALIZADO / VALOR_META`.

### B. GESTAO_CONSULTOR
*   **Chave:** Filial + Consultor + Segmento + Mês.
*   **Colunas:**
    *   `FILIAL_COD`, `NOME_FILIAL`, `CONSULTOR`, `SEGMENTO`, `DATA_REFERENCIA`, `ANO`, `MES_NOME`.
    *   `VALOR_REALIZADO`: Faturamento do vendedor no mês.
    *   `VALOR_FUNIL`: Total orçado pelo vendedor no mês.
    *   `PARTICIPACAO_%`: Faturamento do consultor / Total da Filial no mês.

### C. GESTAO_FUNIL
*   **Chave:** Filial + Segmento + Origem + Status + Mês.
*   **Colunas:**
    *   `FILIAL_COD`, `NOME_FILIAL`, `SEGMENTO`, `ORIGEM`, `STATUS_ORC`, `DATA_REFERENCIA`.
    *   `VALOR_FUNIL`: Soma monetária dos orçamentos.
    *   `QTD_ORCAMENTOS`: Contagem de IDs únicos.
    *   `TAXA_CONVERSAO_%`: (Valor Faturado / Valor Total Orçado) do bucket.

### D. GESTAO_FUNIL_CONSULTOR
*   **Chave:** Consultor + Status + Mês.
*   **Colunas:**
    *   `CONSULTOR`, `STATUS_ORC`, `DATA_REFERENCIA`, `VALOR_FUNIL`, `QTD_ORCAMENTOS`, `TAXA_CONVERSAO_%`.

### E. DETALHE_TRANSACIONAL
*   Aba de auditoria técnica contendo todos os campos brutos normalizados.

## 3. Regras de Negócio e Transformações

### 3.1 Identificação de ORIGEM
*   **OFICINA:** Se `DESCRICAO_CC` contiver as palavras "OFICINA", "SERVICO", "MECANICA" ou "ELETRICA".
*   **BALCÃO:** Demais casos (ex: "PECAS E ACESSORIOS").

### 3.2 Normalização de Consultores
*   Manter nomes como vêm da base (Caixa Alta), preservando registros como "VENDEDOR EXTERNO 01".

### 3.3 Formatação de Datas
*   A coluna `DATA_REFERENCIA` deve ser formatada como string `dd/mm/aaaa` para garantir ordenação visual correta no Excel.

## 4. Plano de Validação
*   **Audit Financeira:** O somatório de `VALOR_REALIZADO` em todas as novas abas de gestão deve ser **exatamente igual** ao somatório da fonte bruta `faturamento_unificado_2025_2026.csv`.
*   **Audit de Funil:** O somatório de `VALOR_FUNIL` deve bater com a fonte `funil_saneado_2025_2026.csv`.
