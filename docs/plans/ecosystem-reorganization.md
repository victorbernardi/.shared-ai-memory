---
title: Plano de Reorganização do Ecossistema
category: plans/active
tags:
  - plan/active
  - infrastructure/reorganization
  - stout-edition
sources:
  - docs/plans/active/2026-05-07-ecosystem-reorganization.md
updated: 2026-05-16
summary: Plano para consolidar a infraestrutura do Gemini CLI e Antigravity, eliminando junctions e centralizando memória e skills.
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: 2026-05-16
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
---

# Plano de Reorganização do Ecossistema

Este documento estabelece as diretrizes para a reorganização da infraestrutura do [[Gemini CLI]] e [[Antigravity]], consolidando configurações e memória em locais canônicos.

## Objetivos
1. Estabelecer `~/.gemini` como home real do [[Gemini CLI]].
2. Consolidar memória e skills em `~/.shared-ai-memory`.
3. Eliminar junctions desnecessários.
4. Integrar Gemini CLI como extensão do [[Antigravity]].

## Fases da Migração
- **Fase 0:** Inversão da home do Gemini CLI.
- **Fase 1:** Consolidação da memória em `~/.shared-ai-memory`.
- **Fase 2:** Backup completo do ecossistema.
- **Fase 3:** Migração das skills para pasta real.
- **Fase 4:** Limpeza de junctions antigos.
- **Fase 5:** Integração com Antigravity IDE.
- **Fase 6:** Limpeza final de arquivos obsoletos.

## Status
Em andamento. Seguir as tarefas detalhadas na fonte original: [[docs/plans/active/2026-05-07-ecosystem-reorganization.md]].
