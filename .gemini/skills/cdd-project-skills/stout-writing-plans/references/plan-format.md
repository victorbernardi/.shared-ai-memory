---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task, before touching code"
risk: critical
source: community
date_added: "2026-02-27"
---

# 🧠 Antigravity Skill: Writing Plans (Stout Edition)

Esta skill é responsável por transformar uma especificação técnica (Spec) em um plano de execução detalhado, seguro e atômico para o Stout.

## 📋 Diretrizes de Execução (Stout Edition)

- **Pré-requisito:** Só inicie o plano se localizar uma **Spec aprovada** na pasta `./docs/specs/` (ou providenciada pelo usuário). Se não existir, PARE e solicite o `/brainstorm`.
- **Quebra de Tarefas:** Divida a implementação em subtarefas atômicas (2-5 min de execução).
- **Rastreabilidade:** Cada tarefa deve citar explicitamente os arquivos envolvidos.
- **Validação Integrada:** Cada passo do plano deve prever como a mudança será verificada.
- **Alinhamento Nativo:** OBRIGATÓRIO invocar a ferramenta `write_todos` com o array de todas as tarefas atômicas imediatamente após salvar o arquivo Markdown, garantindo visibilidade no `Ctrl+T`.

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**

- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```text

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python

def test_specific_behavior():
    result = function(input)
    assert result == expected

```text

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python

def function(input):
    return expected

```text

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash

git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"

```text

```text

## Remember

- Exact file paths always
- Complete code in plan (not "add validation")
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD, frequent commits

## 🛑 STANDBY MODE (Modo de Espera)

Ao finalizar o plano, você deve seguir este protocolo rigoroso:

1. **Gravação:** Salve o plano completo na pasta `./docs/plans/` com um nome descritivo (ex: `./docs/plans/plan_feature_name.md`). Nunca sobrescreva planos anteriores.
2. **Registro Nativo:** Invoque a ferramenta `write_todos` com a lista de tarefas atômicas para que apareçam no `Ctrl+T`.
3. **Mensagem de Gatilho:** Informe ao usuário o caminho exato do plano gerado para encerrar o turno:

   *"Plano de execução detalhado em `./docs/plans/plan_nome_da_task.md` e tarefas populadas no `Ctrl+T`. Aguardando aprovação para iniciar a implementação."*

4. **Imobilidade:** Você NÃO deve realizar nenhuma alteração em arquivos de código fonte (.py, .js, .sql, etc.) após esta mensagem sem o comando explícito `/build`.

---
*Assinado: Antigravity (Phase: Strategy)*

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to docs/plans/plan_<filename>.md. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**

- **REQUIRED SUB-SKILL:** Use subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review

**If Parallel Session chosen:**

- Guide them to open new session in worktree
- **REQUIRED SUB-SKILL:** New session uses executing-plans

## When to Use

This skill is applicable to execute the workflow or actions described in the overview.
