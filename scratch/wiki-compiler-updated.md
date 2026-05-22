---
title: Wiki Compiler
created_at: 2026-04-13
updated_at: 2026-05-21
summary: Motor de geracao e manutencao da base de conhecimento que automatiza a estruturacao de logs e linkagem bidirecional. Diagnosticado com 15 falhas no pipeline wiki-llm.
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: "2026-05-05"
provenance:
  extracted: 0.7
  inferred: 0.25
  ambiguous: 0.05
sources: [session-20260505-113302-claude-e51f4438, wiki-llm-failure-analysis.md]
tags: [stout, automacao, wiki, markdown, conhecimento]
---

## O que e
O Wiki Compiler e o motor de geracao e manutencao desta base de conhecimento. Ele automatiza a transformacao de logs brutos em notas estruturadas, garantindo a linkagem bidirecional e a atualizacao de indices.

## Como uso no meu trabalho
- **Processamento de Pendencias**: O compilador le a pasta `_pending`, tria sugestoes do Cortex e realiza o Smart Merge em notas existentes.
- **Manutencao de Indices**: Atualizacao automatica do `INDEX.md` e do log de processamento.
---
- **Linting Autonomo [2026-04-20]**: Integracao de rotinas de auditoria (links orfaos, conteudo raso e contradicoes) diretamente no cycle de Heartbeat.
---
- **Fase 3 [2026-05-05]**: Fase 3 finalizada. Deploy pendente de reset de tokens.
---
- **Diagnostico de Falhas [2026-05-21]**: 15 falhas mapeadas no pipeline wiki-llm (5 criticas, 5 altas, 5 medias). Principais: 116 arquivos estagnados no `_raw/`, colisao de nomenclatura de sessoes, duplicacao no ACTIVE_CONTEXT.md, e paths hardcoded. Adapters `session_to_cleaned.py` e `commandcode_to_cleaned.py` criados para fechar o gap entre context-agent e wiki.

## Historico de Decisoes Arquiteturais
- [2026-04-13] Criacao do protocolo `SCHEMA.md` para garantir consistencia kebab-case.
- [2026-04-15] Implementacao da Rota Referencia para separar conhecimento externo de decisoes de projeto.
- [2026-04-20] Decisao de adotar **Delegar Autonomia Reflexiva**: O compilador deve consultar o Grafo de Conhecimento antes de criar novas notas para evitar redundancias.

## Conceitos relacionados
[[antigravity-memory-core]], [[context-agent]], [[stout-knowledge-fortress]], [[sentinel]], [[pipeline-wiki-llm]], [[governanca-recencia]]

## Referencias externas
> **Fonte externa** -- nao reflete pratica implementada na Inova.
- **Linting Autonomo**: Integrar rotinas de auditoria (links orfaos, conteudo raso e contradicoes) diretamente no cycle de Heartbeat para manter a saude da base proativamente.
- **Grafo de Conhecimento Dinamico (Graphify)**: Adotar uma camada de indexacao de grafo para evitar que o agente precise reler todos os arquivos a cada sessao.

- Manual do Wiki Compiler (Stout)
