---
name: data-sql-queries
description: "Write correct, performant SQL across all major data warehouse dialects (Fabric, Snowflake, BigQuery, etc.). Use when writing queries, optimizing slow SQL, or translating between dialects."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - write sql, fabric sql, t-sql, optimize query, translate sql, snowflake syntax, bigquery sql, postgresql help
    - escrever sql, sql fabric, t-sql, otimizar consulta, traduzir sql, sintaxe snowflake, sql bigquery, ajuda postgres
---

# SQL Specialist (Cross-Dialect)

Expert in writing performant, readable SQL across major data warehouse dialects. This skill is optimized for **Microsoft Fabric (T-SQL)** as used in the local connector.

## When to Use
- **Query Writing**: Creating complex queries with CTEs and Window Functions.
- **Dialect Translation**: Converting code between PostgreSQL, Snowflake, and BigQuery.
- **Optimization**: Improving slow queries for specific engines (e.g., Fabric/Synapse).

## 🚀 Microsoft Fabric (T-SQL/Synapse) - Special Support
User utilizes a JDBC connector at `C:\Users\victor.bernardi\Documents\Fabric_Database_Connector`.

### Core Syntax Patterns
- **Limiting Rows**: `SELECT TOP (100) * FROM table` (T-SQL standard).
- **Date Truncation**: `DATETRUNC(month, date_column)` or `CAST(date_column AS DATE)`.
- **Date Differences**: `DATEDIFF(day, start_date, end_date)`.
- **JSON Handling**: `JSON_VALUE(json_column, '$.key')`.
- **String Aggregation**: `STRING_AGG(column, ', ') WITHIN GROUP (ORDER BY column)`.

### Performance Tips (Fabric)
- Use **CTEs (Common Table Expressions)** for readability and plan stability.
- Prefer `JOIN` over large `IN (...)` lists.
- For Delta tables, ensure filtering on partition columns if available.

## Cross-Dialect Reference

### PostgreSQL
- `DATE_TRUNC('month', col)`, `ILIKE '%pattern%'`, `col->>'key'`.
- Use `EXPLAIN ANALYZE` for profiling.

### BigQuery
- `DATE_TRUNC(col, MONTH)`, `SAFE_DIVIDE(a, b)`, `UNNEST(array)`.
- Filter on partition columns to save cost.

### Snowflake
- `DATE_TRUNC('month', col)`, `col:key::STRING`, `LATERAL FLATTEN`.
- Use clustering keys instead of traditional indexes.

## Pro Patterns
- **Deduplication**: `ROW_NUMBER() OVER (PARTITION BY id ORDER BY date DESC)`.
- **Cohort Analysis**: Using `DATETRUNC` to align users by month of first activity.
- **Safety**: Always use `NULLIF(denominator, 0)` to prevent division errors.

## Operating Mode
O agente atua como **Senior Database Engineer**, priorizando a sintaxe T-SQL quando operando no Fabric e sempre utilizando CTEs para clareza.
