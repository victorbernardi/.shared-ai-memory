---
title: Context Agent (Skill)
created_at: 2026-04-13
updated_at: 2026-05-21
summary: Skill de gestao de contexto que captura, persiste e recupera o estado das sessoes. Diagnosticada com falhas no pipeline de ingest ao wiki vault.
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: "2026-05-05"
provenance:
  extracted: 0.8
  inferred: 0.15
  ambiguous: 0.05
sources: [session-20260505-113302-claude-e51f4438, wiki-llm-failure-analysis.md]
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
- **Orquestracao de Conhecimento [2026-04-17]**: Integracao do `orchestrate_knowledge.py` ao ritual de encerramento. Ordem de Execucao: 1. Salva Sessao -> 2. Copia Artefatos -> 3. Sincroniza NotebookLM -> 4. Compila Wiki.
---
- **Fluxo Unificado de Salvamento [2026-04-18]**: O comando `/context_agent save` agora dispara silenciosamente a sincronizacao do NotebookLM e a compilacao da Wiki via Stout, garantindo Backup local + Sync de Pesquisa + Publicacao na Wiki.
---
- **Refatoracao de Caminhos [2026-04-20]**: Migracao para paths flexiveis via variaveis de ambiente (`OBSIDIAN_WIKI_PENDING`), eliminando dependencias de caminhos absolutos engessados.
---
- **Briefing Recovery [2026-05-05]**: Uso do `context-agent` para recuperar briefings de sessoes anteriores e garantir continuidade apos resets de token.
---
- **Diagnostico Pipeline [2026-05-21]**: 15 falhas diagnosticadas. Principais: 267 sessoes Claude sem numero sequencial (invisiveis no ACTIVE_CONTEXT), duplicacao truncando ACTIVE_CONTEXT.md (limite 150 linhas), pipeline manual `/wiki-ingest` acumulou 116+ arquivos sem ingest. Adapters `session_to_cleaned.py` e `commandcode_to_cleaned.py` criados como correcao.

## Historico de Decisoes Arquiteturais
- [2026-04-13] Decisao de separar sessoes por projeto para evitar poluicao de contexto.
- [2026-04-15] Hibridizacao v3.0: Transicao para o `Stout Knowledge Fortress` como repositorio central.
- [2026-04-15] Confirmacao de fontes complementares: separacao tecnica entre logs do Claude Code (JSONL) e logs do Gemini (Markdown/Brain), garantindo cobertura total do ecossistema.
- [2026-04-17] Artifact Copy: Implementada etapa 10 no `context_manager.py` com log de idempotencia (`ARTIFACT_COPY_LOG_PATH`) e configuracao em `config.py`.   
- [2026-04-17] **Hook de Convergencia**: Insercao do orquestrador de conhecimento logo apos a copia de artefatos para centralizar o ritual de encerramento no `context_manager.py`.
- [2026-04-20] Auditoria de 50 erros: Refatoracao profunda do `context_manager.py` para tratar caminhos absolutos, subprocessos frageis (uso de `shutil.which`) e tratamento de excecoes.
- [2026-05-05] **Refatoracao context_manager.py**: Atualizacao do script para lidar com comportamentos especificos do Claude Code (subprocess issues) e remocao de erros cosmeticos de IDEClient.

## Conceitos relacionados
[[antigravity-memory-core]], [[stout-knowledge-fortress]], [[sentinel]], [[wiki-compiler]], [[pipeline-wiki-llm]], [[artifact-auto-copy]], [[notebooklm]]

## Referencias externas
> **Fonte externa** -- nao reflete pratica implementada na Inova.
- **Gestao de Handoffs (Limite 60%)**: Implementar a geracao proativa de "Handoff Documents" quando o contexto atingir 60% para evitar a degradacao da memoria (context rot).
- **Mecanismo hot.md**: Formalizar o uso do `hot.md` como cache de curto prazo para recuperacao imediata de estado em sessoes subsequentes.
- **Carregamento Progressivo**: Adotar o "Progressive Context Loading" (nivel 1: apenas frontmatter/metadados) para economizar tokens durante a descoberta de notas relevantes.

- Documentacao interna do Antigravity Framework.
