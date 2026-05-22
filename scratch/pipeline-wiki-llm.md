---
title: Pipeline Wiki-LLM
created_at: 2026-05-21
updated_at: 2026-05-21
summary: Diagnostico completo das 15 falhas no pipeline de ingestao de conhecimento do context-agent para o wiki vault, com gaps entre coleta automatica e ingest manual.
base_confidence: 0.67
lifecycle: draft
lifecycle_changed: "2026-05-21"
provenance:
  extracted: 0.5
  inferred: 0.35
  ambiguous: 0.15
tags: [stout, wiki, pipeline, diagnostico, engenharia]
sources: [wiki-llm-failure-analysis.md]
---

## O que e

Pipeline que conecta sessoes de agentes LLM (Claude/Antigravity) ao vault Obsidian, composto por: coleta automatica (`wiki-stage.sh`) e ingest manual (`/wiki-ingest` raw mode). Diagnosticado com 15 falhas em maio/2026.

## Arquitetura atual

```
Sessao Claude/Antigravity
    |
    v
context_manager.py save
    |  session-NNN.md, ACTIVE_CONTEXT.md, MEMORY.md, context.db
    v
wiki-stage.sh (automatico)
    |  superpowers_cleaner (docs de projeto) + session_to_cleaned + commandcode_to_cleaned
    v
cleaned/  -->  pending_to_ar9av_raw  -->  vault/_raw/
                                              |
                                     /wiki-ingest (MANUAL)
                                              v
                                        wiki vault (Obsidian)
```

## Falhas diagnosticadas (15)

### Criticas (5) — Quebram silenciosamente

| # | Falha | Impacto |
|---|-------|---------|
| 1 | 116 arquivos parados no `_raw/` ha 15 dias | Pipeline estagnado, conhecimento nao destilado |
| 2 | Duplicacao massiva no ACTIVE_CONTEXT.md com truncamento | Tarefas reais perdidas no truncamento de 150 linhas |
| 3 | Colisao de nomenclatura: 267 sessoes Claude sem numero sequencial | Busca FTS5 quebrada, sessoes Claude invisiveis no ACTIVE_CONTEXT |
| 4 | `cleaned/` vazio por design errado | Sessoes do context-agent nunca entravam no pipeline wiki |
| 5 | Paths hardcoded no wiki-stage.sh e context_manager.py | Scripts nao portaveis entre maquinas |

### Altas (5) — Degradam progressivamente

| # | Falha | Impacto |
|---|-------|---------|
| 6 | `/wiki-ingest` manual por design, sem alerta de backlog | `_raw/` cresce indefinidamente |
| 7 | Parse de JSONL silencioso (linhas invalidas puladas) | Perda de dados sem deteccao |
| 8 | Descoberta de sessao depende de mtime | Sessao errada pode ser processada |
| 9 | `repo_root` do Git com 5 niveis de `parent` | Git sync fragil a reorganizacao |
| 10 | Reindexacao FTS5 com ID errado (string vs int) | Indice de busca inconsistente |

### Medias (5) — Inconvenientes

| # | Falha |
|---|-------|
| 11 | Double-processing no raw mode (sem checkpoint atomico) |
| 12 | DRIFT detection fragil no MEMORY.md |
| 13 | `wiki_health_check.py` standalone, nunca chamado |
| 14 | `ARCHIVE_AFTER_SESSIONS=20` prematuro sem ingest previo |
| 15 | Sem validacao de integridade dos arquivos em `_raw/` |

## Correcoes implementadas

- **Adapters criados**: `session_to_cleaned.py` e `commandcode_to_cleaned.py` para fechar o gap entre context-agent e pipeline wiki
- **wiki-stage.sh estendido**: Passos 1.5 (sessoes) e 1.6 (planos CC) adicionados
- **Lote piloto**: Ingest fracionada para validar pipeline antes de processar 249 arquivos

## Conceitos relacionados

[[wiki-compiler]], [[context-agent]], [[stout-knowledge-fortress]], [[governanca-recencia]], [[sentinel]]
