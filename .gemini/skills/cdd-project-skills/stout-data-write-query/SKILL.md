---
name: stout-data-write-query
description: "SQL Query Architect (Elite Stout Edition). Write optimized SQL for your dialect with best practices. Triggers: write query, generate sql, create query, sql syntax, write t-sql, convert to sql."
version: 1.3.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-17"
metadata:
  category: data-intelligence
  triggers: 

    - write query, generate sql, create query, sql syntax, write t-sql, convert to sql
    - escrever query, gerar sql, criar consulta, sintaxe sql, escrever t-sql, converter para sql

---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace

# 📐 Stout SQL Query Architect (Elite)

Transforma requisitos de linguagem natural em consultas SQL de alta performance, otimizadas para dialetos específicos (Microsoft Fabric, Snowflake, BigQuery) e integradas ao motor CDD.

## 📋 Diretrizes de Execução (Stout Edition)

- **Modo Arquiteto:** O agente atua como **Senior SQL Developer**, priorizando a modularidade via CTEs e a performance via filtragem antecipada (pushdown).
- **Abstração de Negócio:** Traduza termos ambíguos de negócio para a lógica técnica exata do banco de dados.
- **Segurança de Execução:** Consultas que envolvam grandes volumes de dados devem incluir cláusulas `TOP` ou `LIMIT` para amostragem inicial.

## When to Use

- **Natural Language to SQL**: When you need to translate a data request into a query.
- **Complex Analytics**: Building queries with multiple CTEs, joins, and window functions.
- **Dialect Optimization**: Getting the correct syntax for **Microsoft Fabric (T-SQL)**, Snowflake, BigQuery, etc.

## Workflow

### 1. Requirements Gathering

Identify:

- **Output Columns**: What needs to be in the result?
- **Filters**: Time ranges, segments, or specific status codes.
- **Aggregations**: SUM, COUNT, AVG, and the corresponding GROUP BY.
- **Dialect**: Default to **Microsoft Fabric (T-SQL)** for this workspace.

### 2. Architecture (CTEs First)

- **Modularity**: Use Common Table Expressions (WITH clauses) to break logic into readable steps.
- **Naming**: Use descriptive names for CTEs (e.g., `active_users`, `filtered_orders`).

### 3. Optimization

- **Filter Early**: Apply WHERE clauses as close to the source as possible.
- **Be Specific**: Never use `SELECT *`; specify exactly what columns are needed.
- **Dialect Specifics**: Use `TOP` for Fabric, `DATETRUNC` for time periods, and `JSON_VALUE` for semi-structured data.

## Operating Mode

O agente atua como **Senior SQL Developer**, priorizando a legibilidade via CTEs e a performance via filtragem antecipada (pushdown).

## 📦 Instalacao

Skill integrada localmente ao projeto CDD e disponível para arquitetura de dados Level 2.

## 🛡️ Governanca

- **Padrão de Qualidade:** Todas as queries geradas devem passar pelo validador de sintaxe do dialeto alvo.
- **Rastreabilidade:** O orquestrador CDD audita o uso desta skill via `stout_architectural_alignment`.

## 📚 Referencias

- Padrões de Arquitetura SQL (Kimball/Inmon).
- Guia de Performance Pushdown.

## Examples

- `/write-query Show the top 10 products by revenue in the last 30 days for our Fabric database.`
- `/write-query Generate a monthly cohort retention query for users signed up in 2023.`

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
