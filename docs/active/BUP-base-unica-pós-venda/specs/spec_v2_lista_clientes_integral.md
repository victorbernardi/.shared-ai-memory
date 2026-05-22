# Spec: Lista Integral de Clientes (Atribuição Transacional)

> **Versão:** v2
> **Data:** 2026-05-13
> **Status:** Finalizada para Planejamento

## 1. Objetivo
Criar uma lista integral de contatos por Grupo Econômico, utilizando como critério de "Dono do Cliente" o consultor responsável pela última venda realizada.

## 2. Requisitos de Negócio
*   **RN01 - Visão Integral:** A base de saída deve conter o universo total de Grupos Econômicos, removendo filtros de inatividade ou de oportunidade (motor sem travas).
*   **RN02 - Consultor Oficial (Última Venda):** O consultor exibido deve ser aquele vinculado à nota fiscal de saída (`SF2010`) mais recente do cliente/grupo.
*   **RN03 - Fallback de Cadastro:** Caso não haja histórico de vendas ou a última venda não possua consultor identificado, utilizar o consultor do cadastro (`SA1010`) como contingência.
*   **RN04 - Governança de Conflitos:** Identificar grupos econômicos que possuem vendas recentes realizadas por mais de um consultor diferente e sinalizar para decisão humana.

## 3. Requisitos Técnicos
*   **Fonte de Dados (Last Sale):** Join entre `SF2010` (Cabeçalho de NF), `SA1010` (Clientes) e `SA3010` (Vendedores).
*   **Lógica de Atribuição:** `ROW_NUMBER() OVER(PARTITION BY CNPJ ORDER BY DATA_EMISSAO DESC, VALOR DESC)`.
*   **Saída:** Arquivo Excel com colunas adicionais para `Consultor_Ultima_Venda` e `Status_Conflito`.

## 4. Plano de Validação (Smoke Test)
*   **Sucesso:** CNPJ X possui última venda em Y com Vendedor Z. O relatório deve refletir Z.
*   **Exceção:** Grupo A possui Filial 1 (Vendedor X) e Filial 2 (Vendedor Y). Ambas com vendas em datas próximas. Marcar como `CONFLITO`.

## 5. Critério de Saída (Fase Research)
*   [x] Caminhos de dados validados via Smoke Test.
*   [x] Regra de atribuição de consultores definida.
*   [x] Modelo de escalação de conflitos aprovado.
