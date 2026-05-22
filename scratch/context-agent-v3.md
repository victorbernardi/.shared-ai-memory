---
title: Context Agent (Skill)
created_at: 2026-04-13
updated_at: 2026-05-21
summary: Skill de gestao de contexto que captura, persiste e recupera o estado das sessoes. Diagnosticada com falhas no pipeline e sistemas de memoria paralelos.
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: "2026-05-05"
provenance:
  extracted: 0.75
  inferred: 0.2
  ambiguous: 0.05
sources: [session-20260505-113302-claude-e51f4438, wiki-llm-failure-analysis.md, session_20260504.md]
tags: [antigravity, skills, context-management, python]
---

## O que e
Skill de gestao de contexto do Antigravity responsavel por capturar, persistir e recuperar o estado das sessoes de trabalho. A versao 3.0 (Hibridizacao) integra a skill ao Antigravity Brain, realizando a captura hibrida de diferentes fontes de LLM. Inclui automacao para alimentacao da wiki corporativa.

## Como uso no meu trabalho
- **Captura Hibrida**: O agente processa sessoes do Claude Code (via arquivos JSONL) e sessoes do Gemini/Antigravity (via `harvest_brain.sh` na pasta `brain/`).  
- **Persistencia**: Uso do comando `/save` para persistir o contexto atual em arquivos `session-NNN.md`.
- **Sincronizacao**: Mantem o `ACTIVE_CONTEXT.md` atualizado com as metas e sub-tarefas extraidas de Planos de Implementacao.
---
- **Artifact Auto-Copy [2026-04-17]**: Copia arquivos `.md` modificados de diretorios monitorados (plans/specs) para a wiki (`_pending`) durante o save.        
---
- **Orquestracao de Conhecimento [2026-04-17]**: Integracao do `orchestrate_knowledge.py` ao ritual de encerramento.
---
- **Fluxo Unificado de Salvamento [2026-04-18]**: O comando `/context_agent save` agora dispara silenciosamente a sincronizacao do NotebookLM e a compilacao da Wiki via Stout.
---
- **Refatoracao de Caminhos [2026-04-20]**: Migracao para paths flexiveis via variaveis de ambiente (`OBSIDIAN_WIKI_PENDING`).
---
- **Briefing Recovery [2026-05-05]**: Uso do `context-agent` para recuperar briefings de sessoes anteriores e garantir continuidade apos resets de token.
---
- **Diagnostico Pipeline [2026-05-21]**: 15 falhas diagnosticadas. Principais: 267 sessoes Claude sem numero sequencial, duplicacao truncando ACTIVE_CONTEXT.md, pipeline manual `/wiki-ingest` acumulou 116+ arquivos. Adapters `session_to_cleaned.py` e `commandcode_to_cleaned.py` criados como correcao.
---
- **Sistemas de Memoria Paralelos [2026-05-04]**: Descoberta de dois sistemas de memoria rodando em paralelo sem comunicacao — Claude (JSONL) e Antigravity/Gemini (brain/). O context-agent integra ambos via captura hibrida mas o deploy do wiki-compiler ficou pendente na sessao 023-024 (abril/2026).

## Historico de Decisoes Arquiteturais
- [2026-04-13] Decisao de separar sessoes por projeto para evitar poluicao de contexto.
- [2026-04-15] Hibridizacao v3.0: Transicao para o `Stout Knowledge Fortress` como repositorio central.
- [2026-04-15] Confirmacao de fontes complementares: separacao tecnica entre logs do Claude Code (JSONL) e logs do Gemini (Markdown/Brain).
- [2026-04-17] Artifact Copy + Hook de Convergencia no `context_manager.py`.
- [2026-04-20] Auditoria de 50 erros: Refatoracao profunda do `context_manager.py`.
- [2026-05-05] Refatoracao context_manager.py para Claude Code.

## Conceitos relacionados
[[antigravity-memory-core]], [[stout-knowledge-fortress]], [[sentinel]], [[wiki-compiler]], [[pipeline-wiki-llm]], [[artifact-auto-copy]], [[notebooklm]]

## Referencias externas
> **Fonte externa** -- nao reflete pratica implementada na Inova.
- **Gestao de Handoffs (Limite 60%)**: Implementar geracao proativa de "Handoff Documents" quando o contexto atingir 60%.
- **Mecanismo hot.md**: Formalizar o uso do `hot.md` como cache de curto prazo.
- **Carregamento Progressivo**: Adotar "Progressive Context Loading" (nivel 1: apenas frontmatter/metadados).

- Documentacao interna do Antigravity Framework.
