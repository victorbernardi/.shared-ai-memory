---
name: using-matt
description: Use at the start of every conversation to determine which skill applies before any response or action. Routes debugging, TDD, planning, brainstorming, code review, and execution to the best skill available.
---

# Using Matt (Skill Orchestrator)

Route every task to the right skill before responding. Check this table first — always.

## The Rule

**Invoke the relevant skill BEFORE any response or action.**

If you think there is even a 1% chance a skill applies, invoke it.

## Routing Table

| Situation / Situação | Skill | Source |
|----------------------|-------|--------|
| Bug reported, test failing, unexpected behavior / "tá quebrando", "erro em produção", "comportamento estranho", "teste falhando" | `diagnose` | Matt |
| Implementing a feature or bugfix / "vamos implementar", "vamos codar", "vamos começar", "me ajuda a escrever" | `tdd` | Matt |
| Creating a PRD from current context / "cria um PRD", "documenta isso como PRD", "gera a especificação" | `to-prd` | Matt |
| Breaking a plan into issues/tickets / "quebra em issues", "cria as tasks", "gera os tickets" | `to-issues` | Matt |
| Stress-testing a plan (no codebase needed) / "me questiona sobre isso", "faz perguntas sobre o plano", "quero pensar melhor antes" | `grill-me` | Matt |
| Stress-testing a plan against the codebase / "como a gente faz X?", "como implementar Y no projeto?", "qual a melhor abordagem?" | `grill-with-docs` | Matt |
| Completing a task and requesting code review / "terminou", "tá pronto", "revisa o que fiz" | `superpowers:requesting-code-review` | Superpowers |
| Receiving and processing code review feedback / "recebi review", "tem comentários no PR", "o revisor disse que..." | `superpowers:receiving-code-review` | Superpowers |
| Executing a written implementation plan / "executa o plano", "segue o plano", "implementa conforme spec" | `superpowers:executing-plans` | Superpowers |
| Multiple independent tasks to run in parallel / "faz isso em paralelo", "são tarefas independentes", "roda os dois ao mesmo tempo" | `superpowers:subagent-driven-development` | Superpowers |

## Red Flags — You Are Rationalizing

| Thought | Reality |
|---------|---------|
| "This is too simple for a skill" | Simple tasks have skills too. Check first. |
| "I need context before invoking" | Invoke first. Skills tell you how to gather context. |
| "I already know how to do this" | Skills evolve. Invoke and read the current version. |
| "This doesn't match any trigger exactly" | Pick closest match. Invoke it. |
| "I'll just do this one quick thing first" | Check BEFORE doing anything. |
| "The question is exploratory, not a formal plan" | `grill-with-docs` is for exactly this — exploring before committing. Invoke it. |
| "Invoking a skill would feel too heavy here" | Heavy is better than wrong. Invoke it. |
| "I'll ask a few clarifying questions first, then invoke" | Invoke first. The skill handles clarification. |
| "This looks like planning, so grill-me fits" | If there's code involved, use `grill-with-docs`. If there's implementation, use `tdd`. `grill-me` is for plans with no codebase. |
| "I can see the bug, let me just hypothesise" | Without `diagnose`, you skip building a feedback loop — the most critical phase. Invoke it. |

## Skill Priority

When multiple skills could apply:

1. **Process skills first** — `diagnose`, `tdd`, `grill-with-docs` determine HOW to approach
2. **Output skills second** — `to-prd`, `to-issues` produce artifacts after the approach is clear

"There's a bug" → `diagnose` first, then `tdd` to fix it.
"Let's build X" → `grill-with-docs` first, then `to-prd`, then `to-issues`.
"Plan is ready" → `superpowers:executing-plans`.

## grill-me vs grill-with-docs vs tdd

This is the most common confusion point:

| Situation / Situação | Skill |
|----------------------|-------|
| Plan discussion, no code / Quer discutir um plano sem codebase | `grill-me` |
| Feature touches existing code / "como a gente faz X no projeto?", "como implementar Y aqui?" | `grill-with-docs` |
| Ready to implement / "vamos começar", "vamos codar", "implementa isso" | `tdd` |
| Asking how to build X / "qual a melhor abordagem?", "como estruturar isso?" | `grill-with-docs` |

When in doubt between `grill-with-docs` and `tdd`: if implementation hasn't started, use `grill-with-docs`. If the user is ready to write code, use `tdd`.
