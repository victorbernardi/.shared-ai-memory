---
name: data-write-query
description: "Write optimized SQL for your dialect with best practices. Use when translating a natural-language data need into SQL, building a multi-CTE query with joins and aggregations, optimizing a query against a large partitioned table, or getting dialect-specific syntax for Snowflake, BigQuery, Postgres, etc."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - write query, generate sql, create query, sql syntax, write t-sql, convert to sql
    - escrever query, gerar sql, criar consulta, sintaxe sql, escrever t-sql, converter para sql
---

# SQL Query Architect (Execution Engine)

Transforms natural language requirements into high-performance, production-ready SQL queries optimized for your specific dialect.

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

## Examples
- `/write-query Show the top 10 products by revenue in the last 30 days for our Fabric database.`
- `/write-query Generate a monthly cohort retention query for users signed up in 2023.`
