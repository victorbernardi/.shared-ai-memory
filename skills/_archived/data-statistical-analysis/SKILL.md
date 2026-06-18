---
name: data-statistical-analysis
description: "Apply statistical methods including descriptive stats, trend analysis, outlier detection, and hypothesis testing. Use when analyzing distributions, testing for significance, detecting anomalies, computing correlations, or interpreting statistical results."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - statistical analysis, hypothesis test, outlier detection, distribution analysis, correlation check
    - análise estatística, teste de hipótese, detecção de outliers, análise de distribuição, correlação
---

# Statistical Analyst (Core Intelligence)

Provides the mathematical foundation for valid data interpretation, moving from descriptive to inferential analysis.

## When to Use
- **Distribution Analysis**: Understand the shape, center, and spread of business metrics.
- **Hypothesis Testing**: Validate A/B test results or before/after comparisons.
- **Anomaly Detection**: Identify outliers that might skew results or indicate data quality issues.
- **Forecasting Basics**: Project future trends based on historical seasonality and growth.

## Methodologies

### 1. Central Tendency & Spread
- **Always report Mean + Median** together. A large gap indicates skewness.
- **IQR (Interquartile Range)**: Use for spread in skewed data (p25 to p75).
- **StdDev**: Use only for normally distributed data.

### 2. Trend Analysis
- **Moving Averages**: Use 7-day windows for weekly seasonality and 28-day for monthly.
- **Growth Rates**: YoY (Year-over-Year) is the gold standard for seasonal business context.

### 3. Outlier Handling
- **Identify**: Use Z-score (>3) or IQR (1.5x) methods.
- **Action**: Do not auto-delete. Investigate if it's a data error, genuine extreme, or different population.

### 4. Hypothesis Testing
- **Significance**: p-value < 0.05 indicates the result is likely not due to chance.
- **Practical Impact**: A result can be statistically significant but too small to matter for the business. Always report Effect Size.

## Critical Guards (The "Think Twice" Checklist)
- **Simpson's Paradox**: Check if aggregate trends reverse when segmented.
- **Survivorship Bias**: Account for users or entities that are missing from the dataset.
- **Correlation != Causation**: Be explicit about the difference.

## Operating Mode
O agente atua como **Senior Data Scientist**, sendo rigoroso com a validade estatística e cético em relação a correlações simples.

## Examples
- `Analyze the distribution of 'order_value' and detect outliers using the IQR method.`
- `Run a t-test to see if Variant B significantly improved the conversion rate.`
