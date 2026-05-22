# Merge Skills: Writing Plans & Brainstorming Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Mesclar as regras da "Stout Edition" (travas, standby mode, specs) com o conteúdo completo e detalhado das skills originais do repositório de plugins, sem perder o fôlego instrucional de 100-200 linhas.

**Architecture:** Utilizar as skills originais como base e injetar as seções específicas do Stout (Headers, Standby Mode, Exit Criteria) via edição cirúrgica de markdown.

**Tech Stack:** Markdown, PowerShell, Git (para commits de checkpoint).

---

### Task 1: Mesclagem da Skill `brainstorming`

**Files:**
- Modify: `C:\Motores-LLM\antigravity\skills\brainstorming\SKILL.md`
- Source (Original): `C:\Projetos\Stout\Plugins\antigravity-awesome-skills\skills\brainstorming\SKILL.md`

**Step 1: Ler a base original**
Já realizado. A base original tem 238 linhas.

**Step 2: Aplicar o Header "Stout Edition" e Seções de Travas**
Inserir o título e as regras de "Understanding Lock" adaptadas para gerar o arquivo `./docs/spec.md`.

**Step 3: Verificar e Commit**
Garantir que o arquivo final mantenha a profundidade original com as novas travas.

---

### Task 2: Mesclagem da Skill `writing-plans`

**Files:**
- Modify: `C:\Motores-LLM\antigravity\skills\writing-plans\SKILL.md`
- Source (Original): `C:\Projetos\Stout\Plugins\antigravity-awesome-skills\skills\writing-plans\SKILL.md`

**Step 1: Injetar o Header e Standby Mode**
Adicionar a obrigatoriedade da Spec aprovada e o protocolo de `STANDBY MODE` (salvamento em `./docs/plan.md.response` e gatilho `/build`).

**Step 2: Preservar as seções de TDD e Granularidade**
Garantir que os exemplos de TDD da skill original permaneçam intactos.

**Step 3: Commit**
Finalizar a unificação das skills core.

---

## Perguntas para Discussão (Writing Plans Mode)

> [!IMPORTANT]
> **Decisões Críticas:**
> 1. **Local de Salvamento:** A skill `writing-plans` original salva em `docs/plans/`. A versão Stout salva em `./docs/plan.md.response`. Vou manter AMBOS: salvar o log histórico em `docs/plans/` e o arquivo de gatilho em `plan.md.response`. Tudo bem?
