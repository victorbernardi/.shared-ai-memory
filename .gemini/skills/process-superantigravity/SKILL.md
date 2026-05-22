---
name: using-superantigravity
description: "Orquestrador Global do Ecossistema Antigravity (Stout Edition). Nível 1: Launcher & Infraestrutura."
risk: safe
source: custom
date_added: "2026-04-28"
---

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Inicialização de Sessão

Ao iniciar qualquer sessão com esta skill, execute imediatamente em background:

```powershell
Start-Process python -ArgumentList "C:\Projetos\Stout\wiki-compiler\brain-watcher.py" -NoNewWindow
```

Isso ativa o monitoramento automático do brain do Gemini. Quando `implementation_plan.md` ou `walkthrough.md` mudarem, são promovidos automaticamente para `docs/` do projeto com confirmação visual no VS Code.

## Como Usar esta Skill (Progressive Disclosure)

Esta skill agora opera em 3 níveis (Regra 1 GEMINI.md):

1. **Nível 1 (Atual):** Monitoramento de infraestrutura e automação de brain.
2. **Nível 2 (Processo):** Leia `references/stout-lifecycle.md` para iniciar uma fase de projeto (Pesquisa/Estratégia/Execução) e alinhar com a memória do projeto (`ACTIVE_CONTEXT.md`).
3. **Nível 3 (Base):** Consulte `references/philosophy.md` ou `infrastructure.md` para diretrizes teóricas, Red Flags e gestão de ecossistema.

## Quando Usar
Esta skill é aplicável para orquestrar o fluxo de trabalho Stout, gerenciar a disciplina de skills ou ativar a automação de monitoramento de cérebro.

## Limitações
- Use esta skill apenas quando o tarefa exigir alinhamento com o framework Stout.
- As instruções densas de ciclo de vida não estão mais no corpo desta skill; elas devem ser lidas cirurgicamente conforme a fase.
