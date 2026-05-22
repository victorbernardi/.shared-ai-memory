---
name: data-analyze
description: "Use when answering data questions, performing trend analysis, or preparing data reports for stakeholders."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - analyze data, lookup metric, investigate trend, data report, analytics
    - analisar dados, buscar métrica, investigar tendência, relatório de dados, análise de dados
---

# Data Analysis (Specialist)

Esta skill permite responder desde perguntas pontuais sobre métricas até investigações profundas de tendências e relatórios formais.

## When to Use
- **Quick Lookup**: Quando você precisa de um número rápido (ex: "Quantos usuários ativos ontem?").
- **Trend Investigation**: Para entender por que uma métrica subiu ou desceu (ex: "O que causou a queda na conversão?").
- **Formal Reporting**: Preparação de revisões trimestrais ou análises de qualidade para stakeholders.

## Operating Mode
O agente atua como **Senior Data Analyst**, priorizando a precisão estatística e a validação de dados antes de qualquer afirmação.

## Workflow

### 1. Understand the Question
Parse the user's question and determine complexity level (Quick answer, Full analysis, or Formal report), data requirements, and desired output format.

### 2. Gather Data
- **If MCP connected**: Explore schema, write SQL, and execute.
- **If no MCP**: Ask for CSV/Excel or manual data input.

### 3. Analyze
- Calculate metrics, aggregations, and comparisons.
- Identify patterns, trends, and outliers.

### 4. Validate Before Presenting
- Row count sanity check.
- Null checks and magnitude checks.
- Trend continuity and aggregation logic validation.

### 5. Present Findings
- **Quick answers**: Direct answer with context and query used.
- **Full analyses**: Lead with key insight, support with tables/viz, and suggest follow-ups.
- **Formal reports**: Executive summary, methodology, detailed findings, caveats, and recommendations.

## Examples
- `/analyze How many new users signed up in December?`
- `/analyze What's causing the increase in support ticket volume?`
- `/analyze Prepare a data quality assessment of our customer table.`

## Limitations
- Precision depends on data quality and warehouse connectivity.
- Large scale analyses may require sampling or multiple query steps.

## Tips
- Be specific about time ranges and segments.
- Mention known table names to speed up the schema discovery.
