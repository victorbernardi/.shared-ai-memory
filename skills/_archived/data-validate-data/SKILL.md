---
name: data-validate-data
description: "QA an analysis before sharing -- methodology, accuracy, and bias checks. Use when reviewing an analysis before a stakeholder presentation, spot-checking calculations and aggregation logic, verifying a SQL query's results look right, or assessing whether conclusions are actually supported by the data."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - validate data, qa report, audit analysis, check calculations, review methodology
    - validar dados, qa de relatório, auditoria de análise, verificar cálculos, revisar metodologia
---

# Data QA & Validation (The "Elite Reviewer")

Final quality control layer to ensure analyses and reports are 100% accurate before reaching decision-makers.

## When to Use
- **Pre-Presentation**: Before any presentation to executives or stakeholders.
- **SQL Sanity Check**: To verify that complex JOINs haven't "exploded" row counts.
- **Metric Verification**: Ensure rates and ratios use the correct denominators.

## Validation Framework

### 1. Methodology Review
- **Framing**: Is the analysis answering the right question?
- **Population**: Is the cohort correctly defined? Are there unintended exclusions?
- **Metric Definition**: Do metrics match how stakeholders understand them?

### 2. Common Analytical Pitfalls (The "Red Flags")
- **Join Explosion**: Check if row counts multiplied unexpectedly after a JOIN.
- **Survivorship Bias**: Question who is NOT in the dataset (e.g., only analyzing current users).
- **Average of Averages**: Never average pre-computed averages without weighting.
- **Timezone Mismatch**: Ensure all systems are aligned (e.g., UTC).
- **Selection Bias**: Avoid segments defined by the outcomes you are measuring.

### 3. Sanity Checks
- **Magnitude**: Do the numbers pass the "smell test"? (e.g., Revenue matches finance data).
- **Sum to 100%**: Ensure segment parts add up to the whole.
- **Order of Magnitude**: Are counts in the right ballpark (MAU/DAU)?

## Confidence Assessment Scale
- **Ready to share**: Sound methodology, verified calculations, caveats noted.
- **Share with noted caveats**: Largely correct but with specific assumptions to communicate.
- **Needs revision**: Found specific errors or missing analyses that must be addressed.

## Operating Mode
O agente atua como um **Senior Data Auditor**, sendo hiper-crítico, procurando erros ocultos e desafiando conclusões precipitadas.

## Examples
- `/validate-data Review this quarterly revenue report for join explosion issues.`
- `/validate-data Check if the denominator for the 'Churn Rate' calculation is correct.`
