# Especificação: Lista Integral de Clientes com Consultores

## 1. Objetivo
Transformar o motor CEVAP em uma ferramenta de geração de lista integral de clientes por Grupo Econômico, removendo filtros de inatividade e orçamento, e enriquecendo com o nome do consultor responsável.

## 2. Requisitos Funcionais
*   **RF01 - Remoção de Filtros:** O sistema deve retornar TODOS os clientes da base M0/M5, independentemente de terem comprado nos últimos 90 dias ou possuírem orçamentos abertos.
*   **RF02 - Inclusão de Consultores:** Cada linha do relatório deve conter o nome do consultor (vendedor) responsável pelo cliente, extraído das tabelas `SA1010` (A1_VEND) e `SA3010` (A3_NOME).
*   **RF03 - Status Informativo:** Manter a lógica de marcação de "Status_Oportunidade" (CONVERSÃO: COMPRA, CONVERSÃO: ORÇAMENTO, PENDENTE: INATIVO) apenas como informação visual, sem excluir registros.
*   **RF04 - Grão de Saída:** Manter a regra de "Filial Campeã" (uma linha por Grupo Econômico), mas garantir que o consultor exibido seja o da filial principal do grupo.

## 3. Arquitetura de Dados
*   **Fonte de Identidade:** `dataset_ouro_identidade.parquet` (M0).
*   **Fonte de Vendas:** `cache_vendas_rfm.parquet` (M3).
*   **Fonte de Cadastro (Fabric):**
    *   `SA1010`: Para obter o código do vendedor (`A1_VEND`).
    *   `SA3010`: Para obter o nome do vendedor (`A3_NOME`).

## 4. Plano de Validação
*   **Teste 1 (Volume):** Comparar o total de linhas do `df_final` com o total de grupos únicos no `M0`. O match deve ser próximo de 100%.
*   **Teste 2 (Integridade):** Verificar se a coluna "Consultor" está preenchida para a maioria dos registros.
*   **Teste 3 (Filtros):** Confirmar que clientes com compra recente (Dias_Inativo < 90) aparecem no Excel final.
