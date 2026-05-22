# 🗺️ PLANO DE MINERAÇÃO DE INSIGHTS — Inova Daily

> **Versão:** 1.0
> **Fase:** Research (Deep Mining)
> **Objetivo:** Explorar sistematicamente os dados do Fabric e datasets Ouro para encontrar anomalias, padrões e histórias que agreguem valor ao Relatório de Comando.

---

## FILOSOFIA

Não sabemos exatamente o que procuramos. Sabemos que os dados escondem padrões que ninguém está olhando. A estratégia é **pesquisas exploratórias em 7 eixos**, cada uma com múltiplas "sondas" — queries que atacam ângulos diferentes até encontrarmos a mina de ouro.

---

## EIXO 1: TEMPORAL (Sazonalidade & Tendência)
**Pergunta-mãe:** O comportamento de 2026 é normal ou estamos fora da curva?

| Sonda | Query | Status |
| :--- | :--- | :--- |
| T1 | Faturamento semanal 2026 — qual semana foi a melhor e a pior? | ⬜ |
| T2 | Comparativo mensal 2025 vs 2026 — estamos acima ou abaixo? | ⬜ |
| T3 | Dia da semana mais forte — sexta vende mais que segunda? | ✅ INSIGHT #008 |
| T4 | Efeito "primeiro dia do mês" — existe rush de NF no dia 1? | ⬜ |
| T5 | Meses com mais devoluções — correlação com volume de vendas? | ⬜ |

## EIXO 2: CLIENTES (Concentração & Comportamento)
**Pergunta-mãe:** Quem são os clientes que realmente importam e como eles se comportam?

| Sonda | Query | Status |
| :--- | :--- | :--- |
| C1 | Top 10 clientes por faturamento acumulado 2026 vs participação % | ✅ INSIGHT #011 |
| C2 | Clientes que compraram em Jan mas NÃO compraram em Abr/Mai (Churn real) | ✅ INSIGHT #007 |
| C3 | Clientes que apareceram pela 1ª vez em 2026 (Novos entrantes) | ⬜ |
| C4 | Ticket médio por cliente — quem compra pouco mas frequente? | ⬜ |
| C5 | Clientes com maior diversidade de SKUs (mix amplo) vs monotema | ⬜ |
| C6 | CSN: taxa de conversão (faturado vs cancelado) | ⬜ |

## EIXO 3: PRODUTO (Mix & Anomalias)
**Pergunta-mãe:** Quais produtos estão morrendo e quais estão nascendo?

| Sonda | Query | Status |
| :--- | :--- | :--- |
| P1 | Subgrupos com crescimento > 50% mês a mês (Estrelas nascentes) | ⬜ |
| P2 | Subgrupos com queda > 50% mês a mês (Produtos morrendo) | ⬜ |
| P3 | SKUs vendidos apenas 1x no ano (One-hit wonders como o TMG) | ⬜ |
| P4 | Top 20 SKUs por volume de unidades (não valor) — o que gira mais? | ⬜ |
| P5 | Margem bruta por subgrupo (custo vs valor) — onde ganhamos mais? | ✅ INSIGHT #009 |

## EIXO 4: CONSULTORES (Performance & Eficiência)
**Pergunta-mãe:** Quem está trazendo valor real e quem está apenas emitindo notas?

| Sonda | Query | Status |
| :--- | :--- | :--- |
| V1 | Ranking de consultores por faturamento acumulado 2026 | ⬜ |
| V2 | Ticket médio por consultor — quem vende projetos vs quem vende prateleira | ✅ INSIGHT #010 |
| V3 | Diversidade de mix por consultor — SKUs únicos por vendedor | ⬜ |
| V4 | Evolução mensal por consultor — quem está crescendo, quem está caindo | ⬜ |
| V5 | Consultor vs cancelamento — correlação entre vendedor e taxa de perda | ⬜ |

## EIXO 5: FILIAIS (Distribuição Geográfica)
**Pergunta-mãe:** A concentração em Contagem é um risco ou uma vantagem?

| Sonda | Query | Status |
| :--- | :--- | :--- |
| F1 | Participação % de cada filial no acumulado — "Índice de Concentração" | ⬜ |
| F2 | Filial com maior crescimento % mês a mês (A estrela escondida) | ⬜ |
| F3 | Filial com maior queda % (O alarme silencioso) | ⬜ |
| F4 | Mix de produtos por filial — cada filial tem sua "personalidade"? | ⬜ |

## EIXO 6: CANCELAMENTOS (O Ralo Sob o Microscópio)
**Pergunta-mãe:** O que podemos aprender com o que perdemos?

| Sonda | Query | Status |
| :--- | :--- | :--- |
| X1 | Evolução mensal de cancelamentos — está piorando ou melhorando? | ⬜ |
| X2 | Motivos de cancelamento por filial — cada unidade perde por razão diferente? | ⬜ |
| X3 | SKUs mais cancelados — existe produto "difícil de vender"? | ⬜ |
| X4 | Tempo médio entre orçamento e cancelamento — perda rápida ou negociação longa? | ⬜ |

## EIXO 7: CRUZAMENTOS PROFUNDOS (A Mina de Ouro)
**Pergunta-mãe:** O que acontece quando cruzamos fontes que nunca foram cruzadas?

| Sonda | Query | Status |
| :--- | :--- | :--- |
| Z1 | Clientes com alto potencial (dataset Ouro) que NUNCA compraram em 2026 | ⬜ |
| Z2 | Frotas grandes (dataset máquinas) vs faturamento real — o mapa do vazamento | ⬜ |
| Z3 | Orçamentos cancelados por preço vs GAP estratégico — estamos perdendo os clientes certos? | ⬜ |
| Z4 | RFM vs Faturamento 2026 — os "VIPs antigos" ainda são VIPs? | ⬜ |

---

## PROTOCOLO DE EXECUÇÃO

1. **Batch de 5 sondas** por sessão de mineração.
2. Todo achado relevante é **imediatamente** registrado no `insight_log.md`.
3. Achados com impacto financeiro > R$ 1M são marcados como **"Candidatos ao Relatório de Comando"**.
4. Ao final de cada batch, atualizar o status das sondas (⬜ → ✅ ou ❌).

---

## CRITÉRIO DE "MINA DE OURO"

Um insight é considerado "mina de ouro" quando atende a pelo menos 2 dos 3 critérios:
- **Surpreendente:** Roberto não sabe disso e vai querer saber.
- **Acionável:** É possível tomar uma decisão imediata com base nesse dado.
- **Quantificável:** O impacto financeiro pode ser calculado (R$ ou %).

---
*Plano criado em 2026-05-14. Estimativa: 35 sondas em 7 eixos.*
