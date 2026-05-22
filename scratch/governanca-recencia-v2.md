---
title: Governanca de Recencia
created_at: 2026-05-21
updated_at: 2026-05-21
summary: Sistema de validacao pre-flight e atualizacao post-flight do relatorio de recencia dos motores de dados, com padronizacao entre motores e fail-fast na orquestracao.
base_confidence: 0.83
lifecycle: draft
lifecycle_changed: "2026-05-21"
provenance:
  extracted: 0.75
  inferred: 0.2
  ambiguous: 0.05
sources: [bup-recency-governance-integration.md, session_audit_20260519.md]
tags: [stout, governanca, automacao, dados]
---

## O que e

Sistema de governanca que garante a atualizacao continua do relatorio de recencia dos motores de dados. Opera em duas fases: **pre-flight** (validacao antes da execucao) e **post-flight** (atualizacao de timestamps apos processamento).

## Como funciona

O relatorio `shared/recency_status.md` rastreia a ultima atualizacao de 13 fontes de dados. Motores como o BUP **leem** esse relatorio para alertar sobre dados stale, mas **nunca o atualizam** apos processar.

### Pre-flight (`governance_sensor.py`)

Executado com `fail_fast=False` — falhas geram warnings, nao interrompem o pipeline. Valida encoding UTF-8, conectividade Fabric, e parse do `recency_status.md`.

### Post-flight

Apos exportacao bem-sucedida, dispara `generate_recency_report.py` via subprocess para atualizar timestamps.

## Motores integrados

| Motor | Status |
|-------|--------|
| Motor M5 (Inova) | Integrado |
| Motor DNA (M1) | Integrado (audit 2026-05-19) |
| BUP (Pos-Venda) | Em implementacao |

## Decisoes de design

- `fail_fast=False`: Pre-flight nunca bloqueia o pipeline principal ^[inferred]
- Post-flight nao-bloqueante: Falha ao atualizar recencia nao interrompe o fluxo
- Padronizacao entre motores: Mesmo contrato replicado para todos os motores
- Orquestracao deve validar `recency_status.md` antes de prosseguir; fail-fast comeca na orquestracao, nao apenas no Python

## Licoes da auditoria M1 (2026-05-19)

- Nao assumir isolamento de projetos: sempre auditar Motor de Referencia (M0) antes de implementar motores derivados
- Template de ingestao (`ingestor_base.py`) evitaria replicacao de logica boilerplate entre motores

## Conceitos relacionados

[[pipeline-inova]], [[motores-inova]], [[motor-dna]], [[wiki-compiler]], [[context-agent]], [[bup-recency-integration]]
