---
name: data-context-extractor
description: "Generate or improve a company-specific data analysis skill by extracting tribal knowledge from analysts. Use when data analysts want Claude to understand their company's specific data warehouse, terminology, metrics definitions, and common query patterns."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: meta-analytics
  triggers: 
    - bootstrap data skill, extract context, create data skill, data warehouse setup, knowledge extraction
    - criar skill de dados, extrair contexto, configurar warehouse, documentar métricas, mapear banco de dados
---

# Data Context Extractor (Meta-Skill)

Generate or improve a company-specific data analysis skill by extracting tribal knowledge from analysts.

## When to Use
- **Bootstrap Mode**: Create a new data analysis skill for a specific warehouse.
- **Iteration Mode**: Improve an existing skill with new domain-specific reference files.

## Workflow

### Phase 1: Database Discovery
Identify database type (BigQuery, Snowflake, etc.) and explore the schema to identify top 3-5 tables analysts query most often.

### Phase 2: Core Interview (Critical Questions)
Ask these questions conversationally to capture specific business logic:
- **Entity Disambiguation**: "When you say 'user', what exactly does that mean? Are there different types?"
- **Primary Identifiers**: "What is the main identifier? Are there multiple IDs for the same entity?"
- **Key Metrics**: "What are the 2-3 most important metrics and how are they calculated?"
- **Data Hygiene**: "What should ALWAYS be filtered out? (test data, internal users, fraud, etc.)"
- **Common Gotchas**: "What mistakes do new analysts typically make with this data?"

### Phase 3: Skill Generation
Generate a structured skill directory:
- `[company]-data-analyst/`
  - `SKILL.md`: Master instructions and SQL dialect notes.
  - `references/entities.md`: Definitions and relationships.
  - `references/metrics.md`: KPI formulas.
  - `references/tables/[domain].md`: Deep dive into specific table groups.

## Operating Mode
O agente atua como **Knowledge Engineer**, conduzindo entrevistas técnicas para mapear o "cérebro" do analytics da empresa.

## Reference File Standards
Reference files must include full table paths, primary keys, update frequency, column definitions, and sample query patterns.

## Limitations
- Requires active participation from a human with domain knowledge.
- Relies on manual installation of the generated skill to the skills directory.

## Examples
- "Create a data context skill for our new BigQuery warehouse."
- "Update the data skill with metrics definitions for the Marketing domain."
