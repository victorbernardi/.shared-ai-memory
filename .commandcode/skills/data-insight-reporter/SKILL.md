---
name: data-insight-reporter
version: 1.0.0
description: Use when you need to report business impact from data analysis. Traduz resultados de análise de dados em relatórios de impacto de negócio e insights acionáveis.
when_to_use: relatório de impacto, insights de dados, apresentação de resultados, data storytelling, business impact, actionable insights, data reporting
allowed-tools: [Read, Write, Edit, AskUserQuestion]
---

# data-insight-reporter

Esta habilidade foca no "Storytelling" dos dados, garantindo que a análise técnica resulte em decisões de negócio.

## Estrutura do Relatório

### 1. Headline (O "So What?")
- Qual a principal descoberta em uma frase?

### 2. Contexto e Dados
- Quais fontes foram usadas?
- Qual o período da análise?

### 3. Principais Descobertas (The Meat)
- Use visualizações sugeridas (Gráficos de barras, tendências).
- Foque em anomalias e padrões interessantes.

### 4. Impacto de Negócio e Recomendações
- **Impacto:** O que isso significa em termos de custo, tempo ou receita?
- **Recomendação:** Qual o próximo passo concreto? (ex: "Ajustar o orçamento da campanha X em 20%").

## Related Skills
- **explore**: Use para obter os dados brutos antes do relatório.
- **brd-generator**: Verifique se as descobertas respondem aos KPIs definidos no BRD.

## Comandos
| Comando | Descrição |
|---------|-----------|
| `/report-insight` | Gera um resumo executivo de impacto de dados |

## Governança e Segurança
- **Nível de Governança:** 1 (Logging).
- **Segurança:** Não processa dados sensíveis sem mascaramento (PII protection).
