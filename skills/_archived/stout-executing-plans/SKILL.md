---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-executing-plans
description: "Execução de planos de implementação atômicos tarefa por tarefa em sessões dedicadas. Triggers: executar plano, iniciar build, rodar tasks, implementar projeto, fase de construção."
version: 1.0.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-16"
category: engineering
---

# 🛠️ Stout Executing Plans (O Construtor)

Esta skill é o braço executor do ecossistema. Ela é ativada após a aprovação de um plano de implementação para transformar tarefas atômicas em código funcional e validado.

## 🚀 Quando Usar
- Para implementar um plano gerado pela `stout-writing-plans`.
- Em sessões de subagentes ou sessões paralelas dedicadas ao build.
- Quando o objetivo é a execução rigorosa de um roteiro pré-aprovado.

---

## 🔄 Fluxo de Trabalho
As diretrizes de setup de sessão, ciclo de execução (TDD) e protocolos de finalização foram movidas para referências técnicas.

**CONSULTE OBRIGATORIAMENTE:** `@references/execution-protocols.md` antes de iniciar a primeira task.

---

## 📦 Instalação
Skill de engenharia local. Requer acesso aos arquivos de plano em `docs/plans/`.

## 💻 Comandos
Para ativar via orquestrador local:
```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-executing-plans
```

## 🛡️ Governanca
- **Fidelidade ao Plano:** Proibido adicionar funcionalidades fora do escopo do plano original.
- **TDD Mandatório:** Cada task deve seguir o ciclo Red-Green-Refactor integralmente.
- **Atomicidade:** Commits obrigatórios após cada tarefa concluída.

## When to Use
This skill is applicable to execute the workflow or actions described in the overview.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
