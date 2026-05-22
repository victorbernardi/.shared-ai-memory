# Granularidade e Comportamento Assimétrico Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implementar filtragem assimétrica (grid fixo vs KPIs filtrados), metas nominais e luminescência de status no Dashboard M6.

**Architecture:** Refatoração da função `updateDashboard` para operar com dois datasets distintos (`perfFiltered` e `perfAllBranches`) e injeção de classes de status via JavaScript para controle de Glow.

**Tech Stack:** JavaScript (ES6+), GSAP (Motion), ApexCharts (Donut), Vanilla CSS (Glows).

---

### Task 1: Preparação de Estilos (Glows)

**Files:**
- Modify: `c:\Projetos\Inova\Metas Peças\05_Resultados\index.html` (Seção CSS)

**Step 1: Adicionar classes de luminescência conforme DESIGN_RULES**
Adicionar os seletores `.status-success`, `.status-alert` e `.status-critical` com as propriedades de `box-shadow` e `border-color` definidas no DESIGN_RULES.md.

### Task 2: Refatoração da Lógica de Filtragem

**Files:**
- Modify: `c:\Projetos\Inova\Metas Peças\05_Resultados\index.html`

**Step 1: Implementar separação de datasets em `updateDashboard`**
Criar `perfFiltered` (respeita filial) e `perfAllBranches` (ignora filial).
Atualizar cálculos de KPI Hero para usar `perfFiltered`.
Atualizar chamadas de renderização:
- `renderMainCharts(..., perfFiltered, ...)`
- `renderBranchGrid(perfAllBranches)`

### Task 3: Aprimoramento do Grid de Filiais (Metas e Status)

**Files:**
- Modify: `c:\Projetos\Inova\Metas Peças\05_Resultados\index.html`

**Step 1: Atualizar template do card em `renderBranchGrid`**
Incluir exibição da Meta Nominal (`fmtK(meta)`).
Injetar a classe de status baseada no percentual de atingimento (>=90, <90, <70) conforme a nova regra.

### Task 4: Interatividade do Gráfico de Pipeline

**Files:**
- Modify: `c:\Projetos\Inova\Metas Peças\05_Resultados\index.html`

**Step 1: Configurar labels centrais no ApexCharts**
Habilitar `plotOptions.pie.donut.labels.show` e configurar o `total.formatter` para exibir o valor consolidado.

---

## 🛑 STANDBY MODE

Plano de execução detalhado gerado como artefato. Aguardando aprovação para iniciar a implementação.

*Assinado: Antigravity (Phase: Strategy)*
