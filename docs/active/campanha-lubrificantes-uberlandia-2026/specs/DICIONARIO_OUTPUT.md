# 📚 DICIONÁRIO DE DADOS: OUTPUT DA CAMPANHA (UBERLÂNDIA 2026) - VERSÃO FINAL (V2.1)

Este documento atua como o contrato oficial de dados do arquivo `MATRIZ_ESTRATEGICA_UBERLANDIA.xlsx`.

---

## ABA 1: `METAS_POR_CLIENTE`

Visão granular por conta, vinculada ao "Dono" (Consultor) atual.

| Coluna | Descrição / Regra de Negócio |
| :--- | :--- |
| **CNPJ** | Identificador único do cliente (14 dígitos). |
| **Consultor_Responsavel** | Consultor ativo que registrou a *última venda* em 2026. |
| **Cliente** | Nome do cliente extraído da base de vendas. |
| **Fat_25** | Faturamento bruto de lubrificantes em 2025. |
| **Fat_26** | Faturamento bruto de lubrificantes em 2026 (até o momento). |
| **Valor_Devolvido** | Total de devoluções de lubrificantes em 2026. |
| **Faturado_LUB_2026** | **Faturamento Líquido 2026**: `Fat_26` - `Valor_Devolvido`. |
| **Potencial Lubrificantes Anual** | Capacidade teórica de consumo da frota (Motor M3). |
| **Potencial_Est_Anual** | **Teto Estratégico (Regra MAX)**: `MAX( Potencial_M3 * 0.50 , Fat_25 * 1.20 )`. |
| **GAP_Bruto** | Oportunidade total no ano: `Potencial_Est_Anual` - `Faturado_LUB_2026`. |
| **GAP_Ajustado** | **Amortecimento de Inércia (Baseado em SOW)**: <br> - SOW < 5%: GAP sofre deságio de 90%. <br> - SOW 5-20%: GAP sofre deságio de 70%. <br> - SOW > 20%: GAP integral. |
| **Meta_Piso** | Parte da meta global (20%) distribuída pelo peso do `Fat_25` (Manutenção). |
| **Meta_Aceleracao** | Parte da meta global (80%) distribuída pelo peso do `GAP_Ajustado` (Recuperação). |
| **Meta_Final_3Sem** | Somatório `Meta_Piso` + `Meta_Aceleracao`. Alvo para os 21 dias. |
| **Mix_Sugerido** | Top 3 produtos históricos (Ativos) ou Recomendação por Categoria (Potenciais). |

---

## ABA 2: `PERF_POR_CONSULTOR`

Consolidação gerencial para avaliação de equilíbrio da força de vendas.

| Coluna | Descrição / Regra de Negócio |
| :--- | :--- |
| **Consultor_Responsavel** | Nome do profissional. |
| **Faturado_LUB_2026** | Total realizado líquido pela carteira no ano atual. |
| **Meta_Campanha_3Sem** | Soma das metas individuais dos clientes da carteira. |
| **Agressividade_Perc** | `Meta_Campanha_3Sem / (Fat_25 / 52 * 3)`. <br> Compara a meta com a média histórica de 3 semanas do consultor. |
| **Folga_Teto_Perc** | Percentual da carteira ainda não faturado em 2026 (Mato Alto). |

---
*Atualizado em: 19/05/2026 - Motor V2.1 (Ajuste de Colunas)*
