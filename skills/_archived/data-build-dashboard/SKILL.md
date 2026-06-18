---
name: data-build-dashboard
description: "Build an interactive HTML dashboard with charts, filters, and tables. Use when creating an executive overview with KPI cards, turning query results into a shareable self-contained report, building a team monitoring snapshot, or needing multiple charts with filters in one browser-openable file."
risk: safe
source: knowledge-work-plugins
date_added: "2026-04-29"
metadata:
  category: data-analytics
  triggers: 
    - build dashboard, kpi cards, interactive report, chart.js, dashboard html
    - criar dashboard, indicadores kpi, relatório interativo, painel de controle
---

# Dashboard Builder (Interactive)

Build a self-contained interactive HTML dashboard with charts, filters, tables, and professional styling. Opens directly in a browser -- no server or dependencies required.

## When to Use
- **Executive Overview**: KPI cards for headline numbers.
- **Team Monitoring**: Snapshots of operational data.
- **Deep-dive Analysis**: When you need multiple charts and filters in one file.

## Workflow

### 1. Requirements
Determine purpose, audience, key metrics, dimensions for filters, and data source.

### 2. Gather Data
Query data or parse uploaded files. Clean and embed as JSON within the HTML file.

### 3. Layout Design
Use a standard grid: KPI cards at the top, primary charts in the middle, and detail table at the bottom.

### 4. Build
Generate a single HTML file with:
- **HTML**: Semantic layout, filter controls, containers.
- **CSS**: Responsive Grid/Flexbox, professional color schemes.
- **JS**: Chart.js (via CDN), filter logic, sortable tables.

### 5. Standard Layout Pattern
```
┌──────────────────────────────────────────────────┐
│  Dashboard Title                    [Filters ▼]  │
├────────────┬────────────┬────────────┬───────────┤
│  KPI Card  │  KPI Card  │  KPI Card  │ KPI Card  │
├────────────┴────────────┼────────────┴───────────┤
│                         │                        │
│    Primary Chart        │   Secondary Chart      │
│                         │                        │
├─────────────────────────┴────────────────────────┤
│    Detail Table (sortable, scrollable)           │
└──────────────────────────────────────────────────┘
```

## Base Template (Condensed)
Include `Chart.js` CDN, CSS variables for colors, and a `Dashboard` class to handle data filtering and rendering. Use `canvas` elements for charts and `table` for data drills.

## Operating Mode
O agente atua como **Analytics Engineer**, focando em usabilidade e clareza visual.

## Limitations
- Data is static once generated.
- Requires internet for CDN libraries unless pre-bundled.

## Examples
- `/build-dashboard Create a sales performance view for Q1 using the provided CSV.`
- `/build-dashboard Build a data quality monitor for the customer table.`
