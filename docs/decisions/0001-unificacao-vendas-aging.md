---
status: "accepted"
date: 2026-04-29
decision-makers: victor.bernardi, antigravity-ai
consulted: Gestão Comercial Inova
informed: Time de Analytics
---

# ADR-0001: Unificação de Fontes de Faturamento e Lógica de Aging no Motor M6

## Context and Problem Statement
O Motor de Relatórios M6 requer visão histórica completa (YoY) e um funil de vendas limpo. Atualmente, os dados de faturamento estão fragmentados entre a `vw_VENDAS` (pós-Nov/25) e a tabela `f_vendas_hist31102025`. Além disso, a `VS1010` contém orçamentos "zumbis" (abertos há meses) que distorcem o pipeline.

## Decision Outcome
Decidimos adotar as seguintes estratégias arquiteturais:
1. **Unificação via UNION ALL:** Consolidar as duas fontes de faturamento em um único pipeline de dados, realizando o aliasing de colunas e normalização de datas.
2. **Lógica de Aging de 60 Dias:** Implementar um filtro de expurgo automático que reclassifica status `0` (Aberto) para `X` (Expirado) caso `Data_Atual - VS1_DATORC > 60`.

### Consequences
- **Positivo:** Visão completa de performance desde 2017 sem intervenção manual.
- **Positivo:** Funil de vendas higienizado, refletindo apenas propostas com chance real de conversão.
- **Negativo:** Ligeiro aumento no tempo de processamento devido ao `UNION` de grandes volumes históricos.

### Confirmation
A verificação será feita via script de QA comparando o faturamento total consolidado contra o Motor M2 oficial. A regra de Aging será validada via amostragem de orçamentos emitidos há > 60 dias.
