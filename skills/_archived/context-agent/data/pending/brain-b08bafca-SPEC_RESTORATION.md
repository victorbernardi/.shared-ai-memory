# Technical Specification: Inova Dashboard Restoration

## Overview
This specification details the restoration of the "Liquid Glass" (v4.3/v5.0) design aesthetic while maintaining the high-performance snapshot engine and fixing chronological sorting in filial charts.

## 1. UI/UX Architecture
- **Aesthetic**: Apple-style "Liquid Glass" (Light Theme).
- **Core Styles**:
  - `background`: `#F5F5F7` (Apple Light Grey)
  - `accent`: `#367C2B` (John Deere Green) / `#FFDE00` (John Deere Yellow)
  - `corners`: `24px` radius for glass cards.
  - `blur`: `15px` backdrop-filter.
- **Frameworks**: GSAP 3.12 (Animations), ApexCharts (DataViz), Lucide (Icons).

## 2. Data Logic & Mapping
The system must bridge the gap between English-abbreviated raw data and Portuguese UI display names.

### 2.1 Month Mapping
| Data Key (data.json) | UI Label | Index |
|----------------------|----------|-------|
| Jan                  | Janeiro  | 0     |
| Feb                  | Fevereiro| 1     |
| Mar                  | Março    | 2     |
| ...                  | ...      | ...   |

### 2.2 Chronological Sorting (Branches)
To prevent the "sorting failure" in filial cards, the rendering logic must:
1.  Initialize a 12-month array of `0` values.
2.  Iterate through the filtered branch data.
3.  Place each value in the array at the position corresponding to its month index.
4.  Render the chart using this fixed-length array.

## 3. Snapshot Architecture (Performance)
- **Engine**: Python Aggregator (`aggregator.py`).
- **Endpoints**:
  - `snapshot_kpis.json`: Global KPIs + Pipeline + Metadata (Years/Segments).
  - `snapshot_evolution.json`: Year-to-date monthly progression.
  - `snapshot_filiais.json`: Detailed branch-level performance.

## 4. Flaw Analysis & Mitigation

| Potential Flaw | Impact | Mitigation Strategy |
|----------------|--------|---------------------|
| **Data Mismatch** | Filters show empty charts. | Update `aggregator.py` to extract unique years/segments directly from `data.json` instead of hardcoding. |
| **Sorting Drift** | Branch charts start in mid-year. | Force chart categories to `MONTH_ORDER` constant and pad missing months with `0`. |
| **Animation Jitter** | Content flashes during filter changes. | Use GSAP `autoAlpha` and staggered reveals when DOM elements are recreated. |
| **Missing Totals** | Discrepancy with Excel reports. | Implement a "Parity Check" log in the console comparing snapshot sum vs raw sum. |

## 5. Deployment Checklist
- [ ] Rename `index.html` to `index_v5_industrial.html` (backup).
- [ ] Write new `index.html` with restored Liquid Glass structure.
- [ ] Run `python aggregator.py` to sync snapshots.
- [ ] Verify TTI (Time to Interactive) < 1s.
