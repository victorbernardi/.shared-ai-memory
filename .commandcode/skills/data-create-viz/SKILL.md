---
name: data-create-viz
description: "Create publication-quality visualizations with Python. Use when turning query results or a DataFrame into a chart, selecting the right chart type for a trend or comparison, generating a plot for a report or presentation, or needing an interactive chart with hover and zoom."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - create viz, plot chart, python chart, matplotlib, seaborn, plotly, data visualization
    - criar gráfico, gerar visualização, plotar dados, gráfico python
---

# Visualization Creator (Professional)

Create publication-quality data visualizations using Python. Generates charts from data with best practices for clarity, accuracy, and design.

## When to Use
- **Reports & Presentations**: Clean and formatted charts for stakeholders.
- **Data Exploration**: Identify correlations, distributions, or visual trends.
- **Interactive Dashboards**: When an "interactive" chart (Plotly) is requested.

## Workflow

### 1. Understand the Request
Determine data source, chart type (or recommend one), purpose, and audience.

### 2. Get and Prep Data
Load data into a pandas DataFrame. Clean and prepare (type conversions, null handling).

### 3. Select Chart Type (Decision Matrix)
- **Trend over time**: Line chart.
- **Comparison**: Bar chart (horizontal if many categories).
- **Composition**: Stacked bar or area chart.
- **Distribution**: Histogram or box plot.
- **Correlation**: Scatter plot.
- **Flow/Process**: Sankey diagram.

### 4. Generate Visualization (Python)
Use **matplotlib + seaborn** for static charts (default) or **plotly** for interactivity.

**Boilerplate Example:**
```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

# Set descriptive title and axis labels
ax.set_title('Insight-driven Title', fontsize=14, fontweight='bold')
ax.set_xlabel('Label', fontsize=11)

# Remove chart junk
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('chart.png', dpi=150)
```

## Design Best Practices
- **Color**: Use consistent, colorblind-friendly palettes. Highlight key points.
- **Typography**: Titles should state the insight (e.g., "Revenue grew 23% YoY").
- **Accuracy**: Y-axis starts at zero for bar charts. Avoid misleading scales.

## Operating Mode
O agente atua como **Data Visualist**, equilibrando estética e precisão técnica.

## Limitations
- Requires Python environment and data-specific libraries.
- Plots are saved as PNG files by default.

## Examples
- `/create-viz Show monthly revenue for the last 12 months as a line chart.`
- `/create-viz Create a horizontal bar chart ranking products by NPS score.`
