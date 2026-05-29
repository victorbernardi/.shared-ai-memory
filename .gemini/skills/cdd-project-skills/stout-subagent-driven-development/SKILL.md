---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

name: stout-subagent-driven-development
description: "Execução de planos de implementação via subagentes especialistas com revisão em dois estágios. Triggers: delegar, subagente, invocar agente, implementar via subagente, linha de montagem, assembly line."
version: 1.0.0
author: Arquiteto Stout
tier: 4
source: custom
date_added: "2026-05-16"
category: meta-factory
---

# 🏭 Stout Subagent-Driven Development (Linha de Montagem)

Esta skill permite que o Maestro execute planos complexos delegando tarefas atômicas para subagentes especializados, garantindo alta fidelidade à especificação e código de elite.

## 🚀 Quando Usar

- Para executar planos gerados pela `stout-writing-plans` que possuam tarefas independentes.
- Quando o volume de código a ser gerado for superior a 100 linhas (para preservar contexto).
- Em situações onde a qualidade do código exige revisões duplas (Spec + Code Quality).

---

## 🔄 Fluxo de Trabalho (Multinível)

O processo detalhado de despacho, revisão de conformidade e garantia de qualidade foi fragmentado para otimização de contexto.

**CONSULTE OBRIGATORIAMENTE:**

- `@references/process-details.md` para o fluxo de orquestração.
- `@references/prompts/` para templates de despacho.

---

## 📦 Instalação

Skill de orquestração de Tier 4. Requer a ferramenta nativa `invoke_agent` do Gemini CLI.

## 💻 Comandos

Para ativar via orquestrador local:

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-subagent-driven-development
```text

## 🛡️ Governanca

- **Checkpoints:** Cada tarefa concluída exige um commit via subagente.
- **Rigor de Revisão:** Proibido iniciar Code Quality review antes da aprovação de Spec Compliance.
- **Bypass:** A execução manual pelo Maestro só é permitida em correções de infraestrutura crítica (src/core).

## When to Use

This skill is applicable to execute the workflow or actions described in the overview.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
