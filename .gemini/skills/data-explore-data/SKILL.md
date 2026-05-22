---
name: data-explore-data
description: "Profile and explore a dataset to understand its shape, quality, and patterns. Use when encountering a new table or file, checking null rates and column distributions, spotting data quality issues like duplicates or suspicious values, or deciding which dimensions and metrics to analyze."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - explore data, profile dataset, data quality check, null rates, table schema, data exploration
    - explorar dados, perfil de dataset, verificar qualidade, taxa de nulos, esquema de tabela, explorar tabela
---

# Data Explorer & Profiler (Integrity Scanner)

Generate a comprehensive data profile for a table or uploaded file. Understand its shape, quality, and patterns before diving into analysis.

## When to Use
- **New Tables/Files**: Get the lay of the land for an unfamiliar dataset.
- **Data Quality Audit**: Check null rates, duplicates, and suspicious values (e.g., placeholder "999999").
- **Schema Discovery**: Identify the grain (what one row represents) and primary keys.

## Workflow

### 1. Access and Classification
Resolve table names or load files. Classify columns into:
- **Identifiers**: IDs, Keys.
- **Dimensions**: Categories for grouping/filtering.
- **Metrics**: Quantitative values (Revenue, counts).
- **Temporal**: Timestamps and dates.

### 2. Generate Data Profile
- **Table-level**: Row counts, column types, date range coverage.
- **Numeric**: Min, max, mean, median, percentiles (p5, p95), null rates.
- **Categorical**: Distinct counts (cardinality), top 10 most common values.
- **Temporal**: Gaps in time series, min/max dates, future date alerts.

### 3. Data Quality Flags (Red Flags)
- **High Nulls**: >5% (warn), >20% (critical).
- **Placeholder Detection**: Values like "N/A", "test", "0", or "-1" in key fields.
- **Logical Violations**: Negative prices, future birthdates, inconsistent case (US vs usa).

## Operating Mode
O agente atua como **Data Quality Engineer**, sendo cético em relação aos dados e buscando proativamente por falhas de integridade.

## Output Structure
A clean summary table grouped by column type, followed by a prioritized list of data quality issues and recommended follow-up analyses.

## Limitations
- Large tables (100M+ rows) use sampling for profiling queries by default.
- Quality flags are heuristic and should be verified by the analyst.

## Examples
- `/explore-data orders_table`
- `/explore-data Analyze the uploaded 'user_feedback.csv' for data quality issues.`
