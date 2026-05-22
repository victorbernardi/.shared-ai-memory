---
name: process-gcc
description: >-
  Use when testing risky hypotheses, attempting destructive refactors,
  or before any operation that could poison the agent's reasoning chain.
  Implements the Git-Context-Controller (GCC) framework for memory isolation.
metadata:
  category: discipline
  version: 1.0.0
  triggers: branch, gcc, memória envenenada, poisoned memory, hipótese arriscada,
    refactor destrutivo, context wall, muralha de contexto, testar abordagem,
    sandbox cognitivo, isolamento de contexto
  tools:
    - antigravity
    - gemini-cli
risk: safe
source: custom
date_added: "2026-05-09"
author: stout-ecosystem
---

# Git-Context-Controller (GCC)

## Iron Law

**NUNCA teste hipóteses arriscadas diretamente no tronco principal do raciocínio.**

Violating the letter IS violating the spirit.

## Overview

Framework de blindagem contra **Memória Envenenada** (REGRA 3 do GEMINI.md).
Implementa versionamento do estado cognitivo do agente através de 3 operações
nucleares: BRANCH, DISCARD e MERGE.

Quando o agente precisa testar uma abordagem metodológica arriscada (migração
pesada, refatoração complexa, formatação experimental), ele DEVE criar um branch
isolado. Se a tentativa falhar, o branch é descartado — limpando o veneno
estrutural e preservando o tronco principal intacto.

## When to Use

- Antes de tentar um refactor destrutivo ou migração pesada
- Quando uma hipótese técnica tem chance significativa de falhar
- Antes de operações que modifiquem muitos arquivos simultaneamente
- Quando perceber que o raciocínio atual pode estar envenenado
- Ao receber o comando `/gcc branch` ou equivalente

## When NOT to Use

- Tarefas simples e seguras (editar 1-2 arquivos)
- Brainstorming ou pesquisa (read-only por natureza)
- Quando já existe um branch ativo (PROIBIDO branches aninhados)

## Step-by-Step

### 1. BRANCH — Criar ramo experimental

```bash
python "%USERPROFILE%\.shared-ai-memory\skills\process-gcc\scripts\gcc_controller.py" branch "<nome>" --reason "Motivo da hipótese"
```

**O que acontece:**

1. Copia `ACTIVE_CONTEXT.md` + `MEMORY.md` para `branches/<nome>/`
2. Gera `metadata.json` com timestamp e motivo
3. Injeta indicator `🔀 GCC Branch Ativo: <nome>` no MEMORY.md
4. Registra operação no log de auditoria

**APÓS O BRANCH:** Prossiga com a experimentação. Todo o trabalho acontece
no contexto atual, mas o estado pré-branch está salvo.

### 2. DISCARD — Descartar branch envenenado

```bash
python "%USERPROFILE%\.shared-ai-memory\skills\process-gcc\scripts\gcc_controller.py" discard "<nome>"
```

**O que acontece:**

1. Restaura `ACTIVE_CONTEXT.md` + `MEMORY.md` do snapshot pré-branch
2. Remove o indicator do MEMORY.md
3. Gera briefing de transição instruindo o agente a ignorar o trecho envenenado
4. Arquiva o branch descartado em `branches/_discarded/`

**APÓS O DISCARD:** O agente DEVE considerar todo raciocínio entre o branch
e o discard como **NULO E INVÁLIDO**. Reinicie a abordagem do zero.

### 3. MERGE — Consolidar aprendizado validado

**ANTES do merge**, o agente DEVE preencher `branches/<nome>/learnings.md` com:

- O que funcionou e por quê
- Decisões técnicas validadas
- Padrões descobertos

```bash
python "%USERPROFILE%\.shared-ai-memory\skills\process-gcc\scripts\gcc_controller.py" merge "<nome>"
```

**O que acontece:**

1. Verifica que `learnings.md` existe e não está vazio
2. Injeta conteúdo de learnings no `ACTIVE_CONTEXT.md` do trunk
3. Remove o indicator do MEMORY.md
4. Arquiva o branch mergeado em `branches/_merged/`

### 4. STATUS — Verificar estado

```bash
python "%USERPROFILE%\.shared-ai-memory\skills\process-gcc\scripts\gcc_controller.py" status
```

## Red Flags — STOP

- Código implementado sem branch antes de hipótese arriscada
- "É simples demais para precisar de branch"
- "Vou testar direto, se der errado eu desfaço"
- "Já sei que vai funcionar"
- Branch aberto há mais de 1 sessão sem merge ou discard

**Todos significam:** Pare. Crie o branch. Siga o protocolo.

## Common Rationalizations

| Desculpa | Realidade |
|----------|-----------|
| "É uma mudança pequena" | Mudanças pequenas envenenam contextos grandes |
| "Vou desfazer manualmente" | Você não consegue desfazer tokens já processados |
| "O branch é overhead" | O branch leva 2 segundos. Refazer 50 passos leva horas |
| "Já tentei e sei que funciona" | Se sabe que funciona, o branch é grátis. Se não sabe, é obrigatório |
| "Estou só explorando" | Exploração COM branch = exploração SEGURA |

## Integração com Ecossistema

```
process-gcc (DURANTE a sessão)      context-agent (PÓS-sessão)
         │                                    │
         ├── branch: snapshot pré-hipótese    ├── save: resumo ao final
         ├── discard: rollback + cleanup      ├── load: briefing próxima sessão
         ├── merge: consolida learnings       ├── search: busca histórica
         └── status: consciência do estado    └── maintain: arquivamento
```

## Referências

- [Especificação Completa](../../docs/specs/2026-05-09-git-context-controller.md)
- [Protocolo de Operações](references/operations-protocol.md)

## Limitations

- NÃO versiona o histórico de conversa real (tokens processados pelo LLM)
- NÃO substitui o `context-agent` ou `context-guardian`
- NÃO trigga wiki-compiler automaticamente
- Branches aninhados são PROIBIDOS (máximo 1 branch ativo por vez)
