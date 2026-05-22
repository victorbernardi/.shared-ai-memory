# ADR-0009: Adoção do Plan Mode para Native Task Planning

## Status
Aceito (2026-05-16)

## Contexto
Durante as execuções de Brainstorming, Design e Planejamento (via skills como `stout-writing-plans` e `stout-brainstorming`), o sistema CDD estava suscetível a realizar modificações prematuras ou rodar comandos não desejados antes da consolidação de uma estratégia explícita. Para alinharmos a governança local à arquitetura nativa do Gemini CLI, precisávamos de um mecanismo que travasse as alterações (sandboxing/isolation) enquanto o agente formula a sua especificação técnica ou roteiro de execução.

## Decisão
Formalizamos o **Native Task Planning** como o padrão ouro para as fases de especificação e roteirização:

1.  **Imutabilidade Preventiva:** É obrigatório o uso do `enter_plan_mode` (Plan Mode) pelo agente ao iniciar tarefas que exijam reflexão aprofundada, análise ou design, a fim de garantir que nenhum código-fonte seja modificado (prevenção física).
2.  **Governança CDD:** O catálogo principal `skills_catalog.yaml` e a skill física `stout-writing-plans/SKILL.md` foram alterados para mandatoriamente acionar o modo de planejamento.
3.  **Validação Empírica (Smoke Test):** O subagente (`@generalist`) comprovou ser capaz de absorver a diretriz da skill e se auto-isolar chamando a ferramenta de `enter_plan_mode` nativamente sem fricções com o modelo CDD.

## Consequências

### Positivas
- **Prevenção de Danos:** Zero risco de subagentes ou prompts criarem arquivos ou executarem comandos (`write_file`, `run_shell_command`) por engano no meio da fase de elaboração de ideias.
- **Rastreabilidade Limpa:** Os Planos são formalmente aprovados e persistidos antes de qualquer escrita no workspace real.
- **Sinergia Stout Elite:** Integra-se perfeitamente com a diretriz do Guardrail V2.0 e do Stout Immunity Gate (proteção física).

### Negativas
- **Fricção Inicial:** Obriga o fluxo de trabalho automatizado a ter um *step* (passo) a mais de confirmação e aprovação do usuário para a saída do modo de planejamento (`exit_plan_mode`).

## Referências
- `docs/specs/2026-05-16-spec-native-task-planning.md`
- `docs/governance/protocolo_ferramentas_cli.md`