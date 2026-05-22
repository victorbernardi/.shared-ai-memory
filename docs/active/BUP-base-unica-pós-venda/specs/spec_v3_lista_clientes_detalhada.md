# Spec: Lista Integral de Clientes (Detalhamento Transacional)

> **Versão:** v3
> **Data:** 2026-05-13
> **Status:** Finalizada para Planejamento

## 1. Objetivo
Evoluir a lista integral de clientes para incluir o histórico granular de interações (Última Compra e Último Orçamento), permitindo ao consultor uma abordagem baseada em fatos recentes.

## 2. Requisitos de Negócio (Atualizados)
*   **RN01 - Visão Integral:** Sem filtros de exclusão.
*   **RN02 - Consultor da Última Venda:** Atribuição baseada na transação mais recente (`SF2010`).
*   **RN03 - Histórico de Compra:** Coluna `Data_Ultima_Compra` com a data real da última NF.
*   **RN04 - Histórico de Orçamento:** 
    *   `Data_Ultimo_Orcamento`: Data do orçamento mais recente (independente de status).
    *   `Status_Ultimo_Orcamento`: "Aberto" ou "Cancelado".
    *   `Numero_Ultimo_Orcamento`: Número identificador do orçamento no ERP.

## 3. Arquitetura de Dados
*   **Orçamentos Abertos:** Fonte `tabela_orçamentos_abertos.xlsx`.
*   **Orçamentos Cancelados:** Fonte `tabela_orçamentos_cancelados.xlsx`.
*   **Vendas:** `SF2010` (para consultor) e `cache_vendas_rfm.parquet` (para data).

## 4. Plano de Validação
*   **Teste 1 (Cruzamento):** Validar se o `Numero_Ultimo_Orcamento` corresponde à `Data_Ultimo_Orcamento` no Excel final.
*   **Teste 2 (Datas):** Garantir que a `Data_Ultima_Compra` está em formato de data (YYYY-MM-DD) e não apenas "há X dias".
