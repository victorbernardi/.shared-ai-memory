---
name: context-agent
description: Agente de contexto para continuidade entre sessoes. Salva resumos, decisoes, tarefas pendentes e carrega briefing automatico na sessao seguinte.
risk: safe
source: community
date_added: '2026-03-06'
author: renat
tags:
- context
- session-management
- continuity
- memory
tools:
- claude-code
- antigravity
- cursor
- gemini-cli
- codex-cli
---

# Context Agent

## Overview

Agente de contexto para continuidade entre sessoes. Salva resumos, decisoes, tarefas pendentes e carrega briefing automatico na sessao seguinte.

## When to Use This Skill

- When the user mentions "salvar contexto" or related topics
- When the user mentions "salva o contexto" or related topics
- When the user mentions "proxima sessao" or related topics
- When the user mentions "briefing sessao" or related topics
- When the user mentions "resumo sessao" or related topics
- When the user mentions "continuidade sessao" or related topics

## Do Not Use This Skill When

- The task is unrelated to context agent
- A simpler, more specific tool can handle the request
- The user needs general-purpose assistance without domain expertise

## How It Works

Continuidade perfeita entre sessões. Captura, comprime e restaura contexto
automaticamente — tópicos, decisões, tarefas, erros, arquivos modificados
e descobertas técnicas.

**Antigravity e Gemini CLI compartilham esta instalação** — são o mesmo motor
acessando os mesmos arquivos via chain de symlinks/junctions.

## Localização

**Produção (source of truth dos dados):** `~/.shared-ai-memory/context-agent/`

**Código (projeto):** `C:\Projetos\Stout\wiki-compiler\skills\process-context-agent\`

**Produção (skill instalada):** `~/.shared-ai-memory/skills/process-context-agent\`

Workflow: desenvolver em `wiki-compiler` → copiar para `shared-ai-memory/skills` quando pronto.

```
~/.shared-ai-memory/skills/process-context-agent/
├── SKILL.md
├── scripts/
│   ├── config.py               # Paths e constantes
│   ├── models.py               # Dataclasses
│   ├── governance.py           # Regras de governança
│   ├── session_parser.py       # Parser do brain do Antigravity
│   ├── session_summary.py      # Gerador de resumos
│   ├── active_context.py       # Gerencia ACTIVE_CONTEXT.md
│   ├── project_registry.py     # Registro de projetos
│   ├── compressor.py           # Compressão e arquivamento
│   ├── docs_archiver.py        # Ciclo de vida docs/active → docs/legacy
│   ├── search.py               # Busca FTS5
│   ├── context_loader.py       # Carrega contexto
│   └── context_manager.py      # CLI entry point
├── references/
│   ├── context-format.md       # Especificação de formatos
│   └── compression-rules.md    # Regras de compressão
```

**Storage unificado** (fonte da verdade dos dados):
```
~/.shared-ai-memory/context-agent/
├── sessions/    # session-NNN-<origin>.md  (origin: antigravity | opencode | claude)
├── archive/
├── cleaned/
├── pending/
├── logs/
├── ACTIVE_CONTEXT.md
├── PROJECT_REGISTRY.md
└── context.db   # SQLite FTS5
```

## ⚠️ Atenção: Bash Tool vs PowerShell (Claude Code)

Os comandos abaixo usam `$HOME` ou `$env:USERPROFILE` — sintaxe **PowerShell**.
Quando o agente executa via **Bash tool** (Claude Code), essas variáveis não são expandidas.

**Use sempre o path absoluto na Bash tool:**

```bash
# Bash tool — path absoluto obrigatório
PYTHONIOENCODING=utf-8 python "C:/Users/victor.bernardi/.shared-ai-memory/.commandcode/skills/process-context-agent/scripts/context_manager.py" <comando> [args]
```

**Ou use a PowerShell tool:**
```powershell
# PowerShell tool — $HOME funciona normalmente
python "$HOME\.shared-ai-memory\.commandcode\skills\process-context-agent\scripts\context_manager.py" <comando> [args]
```

> Passar `--session` com o path do JSONL da sessão atual quando o save automático não encontrar o arquivo.

---

## Inicialização (Primeira Vez)

```powershell
# PowerShell (Padrão Gemini CLI/Claude Code)
python "$HOME\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" init

# CMD
python "%USERPROFILE%\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" init
```

## Salvar Contexto Da Sessão Atual

Quando a sessão está terminando ou antes de uma tarefa longa, salvar o contexto. O fluxo é **híbrido**: se argumentos manuais forem fornecidos, eles têm precedência; caso contrário, o sistema utiliza a extração automática.

### Fluxo Automático (Padrão)

```powershell
# PowerShell
python "$HOME\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" save

# CMD
python "%USERPROFILE%\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" save
```

### Fluxo Híbrido (Com Overrides Manuais)
Use argumentos para garantir que a memória de longo prazo capture exatamente o que é importante:

```powershell
# PowerShell
python "$HOME\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" save ^
  --topic "Arquitetura de Plugins" \
  --summary "Implementação da nova interface de plugins para o core do projeto." \
  --decisions "Utilizar gRPC para comunicação entre plugins" \
  --tasks "Implementar o plugin de autenticação"
```

**Argumentos Disponíveis:**
- `--topic`: Define o título principal da sessão (substitui o automático).
- `--summary`: Resumo executivo (injetado no topo das descobertas).
- `--decisions`: Adiciona decisões específicas (aceita múltiplas linhas).
- `--tasks`: Adiciona tarefas pendentes específicas (aceita múltiplas linhas).

O que faz:
1. Encontra o arquivo JSONL mais recente da sessão
2. Analisa todas as mensagens, tool calls e resultados
3. Gera resumo estruturado (session-NNN.md)
4. Atualiza ACTIVE_CONTEXT.md com novas informações
5. Sincroniza com MEMORY.md (carregado no system prompt)
6. Indexa para busca full-text
7. Executa `wiki-stage.sh` — varre `Stout/**\docs` e `Inova/**\docs`, limpa via superpowers_cleaner e move para `vault/_raw/`

**Após o save, execute `/wiki-ingest` manualmente para sincronizar o vault Obsidian.**
O pipeline até o `_raw/` é automático; o `/wiki-ingest` requer ação manual.

## Carregar Contexto (Briefing)

No início de uma nova sessão, carregar o contexto:

```bash
python "%USERPROFILE%\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" load
```

Gera briefing com: projetos ativos, tarefas pendentes (por prioridade),
bloqueadores, decisões recentes, convenções e resumo das últimas sessões.

## Status Rápido

```bash
python "%USERPROFILE%\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" status
```

Resumo em poucas linhas: projetos, pendências críticas, bloqueadores.

## Buscar No Histórico

```bash
python "%USERPROFILE%\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" search "rate limit"
```

Busca full-text (SQLite FTS5) em todas as sessões — tópicos, decisões,
erros, arquivos, etc.

## Manutenção

```bash
python "%USERPROFILE%\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" maintain
```

Arquiva sessões antigas, comprime arquivo, ressincroniza MEMORY.md,
reconstrói índice de busca.

## Fluxo De Trabalho

```
[Sessão termina]
  → save → session-NNN.md + ACTIVE_CONTEXT.md + MEMORY.md

[Nova sessão começa]
  → MEMORY.md já está no system prompt (automático)
  → load → briefing detalhado com tudo que precisa saber

[Contexto cresce demais]
  → maintain → arquiva sessões antigas, comprime, otimiza
```

## O Que É Capturado Em Cada Sessão

- **Tópicos**: assuntos discutidos
- **Decisões**: escolhas técnicas e de arquitetura
- **Tarefas concluídas**: o que foi feito
- **Tarefas pendentes**: o que falta (com prioridade)
- **Arquivos modificados**: quais arquivos foram editados/criados
- **Descobertas**: insights técnicos importantes
- **Erros resolvidos**: problemas e suas soluções
- **Questões em aberto**: perguntas sem resposta
- **Métricas**: tokens consumidos, mensagens, tool calls

## Integração Com Memory.Md

`ACTIVE_CONTEXT.md` e `PROJECT_REGISTRY.md` ficam em `~/.shared-ai-memory/context-agent/`
(storage unificado) e são carregados no briefing de qualquer motor via `context_manager.py load`.

`MEMORY.md` global fica em `~/.shared-ai-memory/memory/MEMORY.md`. É incluído no system
prompt automático de sessões que configuram esse path.

## Referências

- Para formato detalhado dos arquivos: `references/context-format.md`
- Para regras de compressão e arquivamento: `references/compression-rules.md`

## Best Practices

- Provide clear, specific context about your project and requirements
- Review all suggestions before applying them to production code
- Combine with other complementary skills for comprehensive analysis

## Common Pitfalls

- Using this skill for tasks outside its domain expertise
- Applying recommendations without understanding your specific context
- Not providing enough project context for accurate analysis

## Related Skills

- `context-guardian` - Complementary skill for enhanced analysis
