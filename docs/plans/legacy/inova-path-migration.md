---
title: Atualização de Paths Hardcoded (Inova)
category: plans/legacy
tags:
  - infra/path
  - refactoring/inova
sources:
  - docs/plans/plan_v1_inova_path_migration.md
updated: 2026-05-16
summary: Estratégia para remover caminhos hardcoded e adotar configuração dinâmica para os projetos de Pós-Venda (Inova).
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: 2026-05-16
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
---

# Atualização de Paths Hardcoded (Inova)

Este plano documenta a migração do padrão de caminhos absolutos (`C:\Projetos\Inova\...`) para um sistema de configuração dinâmica, utilizando um módulo `shared/config.py`.

## Objetivos
- Eliminar referências absolutas hardcoded em 52 scripts.
- Implementar descoberta dinâmica de diretórios (baseada em `pathlib`).
- Garantir portabilidade do pipeline.

## Abordagem
A solução adotada foi a injeção do diretório `shared` no `sys.path` dos scripts, utilizando `pathlib` para localizar a raiz do projeto de forma relativa. Foi mapeado um padrão de substituição para converter todos os diretórios obsoletos de `Potencial Clientes` em variáveis centralizadas.

## Ordem de Execução
1. Scripts de Raiz e Orquestradores.
2. Scripts de Produção (Pipelines).
3. Scripts de Suporte e Documentação.
4. Rascunhos e Diagnósticos.

---
*Fonte: [[docs/plans/plan_v1_inova_path_migration.md]]*
