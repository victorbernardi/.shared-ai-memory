---
name: data-data-visualization
description: "Expert guidance for choosing and designing effective data visualizations. Use when you need to decide the best chart type, apply design principles (color theory, accessibility), or format charts for professional delivery."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - chart selection, visualization principles, color theory, accessible charts, design best practices
    - escolher gráfico, princípios de visualização, teoria das cores, acessibilidade em gráficos, boas práticas de design
---

# Data Visualization (Design & Principles)

Chart selection guidance, design principles, and accessibility considerations for creating effective data visualizations.

## When to Use
- **Chart Selection**: Choose the best chart type for your dataset.
- **Design Principles**: Apply professional styling, color theory, and accessibility.
- **Accuracy**: Ensure charts don't mislead and follow standard conventions.

## Chart Selection Guide
- **Trend over time**: Line chart (Area for cumulative).
- **Comparison**: Bar chart (Horizontal for many categories).
- **Composition**: Stacked bar or area chart.
- **Distribution**: Histogram or Box plot.
- **Correlation**: Scatter plot or Heatmap.
- **Flow/Process**: Sankey diagram or Funnel chart.

## Forbidden Patterns (What NOT to do)
- **Pie charts**: Avoid unless <6 categories. Humans are bad at comparing angles.
- **3D charts**: Never use them. They distort perception.
- **Dual-axis charts**: Use with extreme caution; they can imply false correlation.
- **Chart Junk**: Remove gridlines, borders, and backgrounds that don't carry information.

## Python Setup and Style
Use colorblind-friendly palettes (e.g., `PALETTE_CATEGORICAL = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']`).
Titles should state the **insight** (e.g., "Revenue grew 23%") rather than just the metric.

## Operating Mode
O agente atua como **Information Designer**, focando na psicologia da percepção e clareza da comunicação.

## Accessibility Checklist
- [ ] Chart works without color (patterns or labels used).
- [ ] Text is readable (Title >= 12pt, Labels >= 10pt).
- [ ] Legend is clear and positioned without obscuring data.
- [ ] Data source and date range are noted.

## Examples
- "Recommend the best chart to show regional sales composition over the last year."
- "Apply accessibility best practices to this Matplotlib code."
