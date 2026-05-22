# Modular Storytelling Report Architecture

* Status: accepted
* Date: 2026-05-13
* Decision-makers: Antigravity, User

## Context and Problem Statement

The `generate_pdf_report_v2.py` script was a monolith combining data loading, complex financial calculations, and PDF drawing logic. As we add more "Magnifying Glass" (Lupa) analyses, the script becomes brittle and hard to maintain. We need a way to add new insights without risking regressions in the core KPIs.

## Decision Outcome

Chosen option: **Modular Analysis Ecosystem**, because it isolates analytical logic, facilitates unit testing of insights, and follows a clear Data Storytelling narrative flow.

### Architecture

1.  **Analyses (`src/analyses/`)**: Each analysis (Macro, Dead Capital, Popularity, etc.) is a standalone module.
2.  **Orchestrator (`src/report_orchestrator.py`)**: Responsible only for assembling the PDF, handling layout, and injecting the branding.
3.  **Utils (`src/utils/report_utils.py`)**: Centralizes styles, colors, and shared formatting logic.

## Consequences

* **Good:** Isolated maintenance of each analysis page.
* **Good:** Narrative flow follows `@data-storytelling` principles (Setup -> Conflict -> Deep Dive -> Resolution).
* **Good:** Reusable visual assets and branding.
* **Bad:** Increased number of files in the project.

## Narrative Flow

1.  **Page 1: Executive Summary (Setup)** - Macro context.
2.  **Page 2: The Cost of Inactivity (Conflict)** - Dead Capital and Dropout.
3.  **Page 3: The Profile of Abandonment (Deep Dive)** - Popularity Decay and Regional Impact.
4.  **Page 4: Recovery Matrix (Resolution)** - Action Plan.
