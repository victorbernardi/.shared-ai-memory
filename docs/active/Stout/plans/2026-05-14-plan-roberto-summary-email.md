# Projeto Roberto Summary Email Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Build a script to generate a parts sales summary for Roberto based on Fabric and CEVAP data.

**Architecture:** A standalone Python script in `Projetos/Roberto-Summary` that loads data via `fabric_db` and `pandas`, aggregates metrics, and formats a Markdown output.

**Tech Stack:** Python, Pandas, SQL (Fabric), Markdown.

---

### Task 1: Project Setup

**Files:**
- Create: `Projetos/Roberto-Summary/src/config.py`
- Create: `Projetos/Roberto-Summary/src/main.py`
- Create: `Projetos/Roberto-Summary/.env`

**Step 1: Create directory structure**
Run: `mkdir -p Projetos/Roberto-Summary/src`

**Step 2: Create .env with credentials**
(Copying from Inova projects)

**Step 3: Commit setup**
Run: `git add Projetos/Roberto-Summary`
Run: `git commit -m "feat: initialize Roberto Summary project structure"`

### Task 2: Data Extraction (Sales)

**Files:**
- Modify: `Projetos/Roberto-Summary/src/main.py`

**Step 1: Implement SQL query for vw_VENDAS**
Fetch current month sales data with CC and Vendedor.

**Step 2: Test extraction**
Run: `python Projetos/Roberto-Summary/src/main.py --test-sales`

### Task 3: Data Extraction (Opportunities)

**Files:**
- Modify: `Projetos/Roberto-Summary/src/main.py`

**Step 1: Implement Excel load for CEVAP_ATIVACAO.xlsx**
Load and filter open opportunities.

**Step 2: Test extraction**
Run: `python Projetos/Roberto-Summary/src/main.py --test-opps`

### Task 4: KPI Aggregation & Formatting

**Files:**
- Modify: `Projetos/Roberto-Summary/src/main.py`
- Create: `Projetos/Roberto-Summary/templates/email_template.md`

**Step 1: Aggregate data by CC and Vendedor**

**Step 2: Implement Markdown generator**

**Step 3: Run full generation**
Run: `python Projetos/Roberto-Summary/src/main.py --generate`

### Task 5: Final Review & Delivery

**Files:**
- Create: `Projetos/Roberto-Summary/output/SUMMARY_ROBERTO.md`

**Step 1: Verify output formatting**

**Step 2: Final Commit**
Run: `git commit -m "feat: complete Roberto Summary email generator"`
