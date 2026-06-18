---
name: stout-data-sql-queries
description: "SQL Specialist (Elite Stout Edition). Write correct, performant SQL across all major data warehouse dialects (Fabric, Snowflake, BigQuery, etc.). Triggers: write sql, fabric sql, t-sql, optimize query, translate sql, snowflake syntax, bigquery sql, postgresql help."
version: 1.3.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-17"
metadata:
  category: data-intelligence
  triggers: 
    - write sql, fabric sql, t-sql, optimize query, translate sql, snowflake syntax, bigquery sql, postgresql help
    - escrever sql, sql fabric, t-sql, otimizar consulta, traduzir sql, sintaxe snowflake, sql bigquery, ajuda postgres
---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace

# 🏗️ Stout SQL Specialist (Elite)

Especialista na escrita de SQL performante e legível nos principais dialetos de data warehouse, com suporte avançado a Microsoft Fabric (T-SQL).

## 📋 Diretrizes de Execução (Stout Edition)

- **Modo Engenharia:** O agente atua como **Senior Database Engineer**, priorizando a segurança e eficiência do plano de execução.
- **Padrão de Escrita:** OBRIGATÓRIO o uso de CTEs (Common Table Expressions) para modularização da lógica.
- **Prevenção de Erros:** Sempre valide tipos de dados e use `NULLIF` em divisões.
- **Rastreabilidade:** Consultas complexas devem ser acompanhadas de uma breve explicação da estratégia de join utilizada.

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

## 📦 Instalacao

Skill integrada localmente ao projeto CDD e disponível como utilitário técnico de Level 2 no ecossistema Stout.

## 🛡️ Governanca

- **Segurança de Schema:** Nunca execute comandos DDL (DROP, TRUNCATE) sem confirmação explícita de `risk_level: CRITICAL`.
- **Compliance:** Alinhado com o Protocolo Stout de Engenharia de Dados.

## 📚 Referencias

- Documentação T-SQL (Microsoft Fabric).
- SQL Antipatterns (Bill Karwin).

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
