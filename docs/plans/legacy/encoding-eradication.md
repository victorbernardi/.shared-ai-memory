---
title: Erradicação de Erros de Encoding (Vacina Erro Zero)
category: plans/legacy
tags:
  - infra/encoding
  - quality/vacina-erro-zero
sources:
  - docs/plans/plan_v1_encoding_eradication.md
updated: 2026-05-16
summary: Estratégia para erradicar corrupção de caracteres (Mojibake) e garantir UTF-8 em toda a infraestrutura Stout/Antigravity.
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: 2026-05-16
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
---

# Erradicação de Erros de Encoding (Vacina Erro Zero)

Este plano define a estratégia para corrigir sistemicamente a corrupção de caracteres especiais ([[Mojibake]]) e garantir a integridade [[UTF-8]] em toda a infraestrutura.

## Diagnóstico
A corrupção era causada por falta de declaração de encoding em scripts (assumindo o padrão do sistema) e uso incorreto de comandos [[PowerShell]] que salvavam em [[UTF-16]] ou [[ANSI]].

## Abordagem de Implementação
1. **Blindagem de Infraestrutura:** Atualizar scripts Python e Powershell para forçar `UTF-8`.
2. **Sanitarização em Massa:** Limpeza do vault via script.
3. **Governança:** Inclusão da regra de obrigatoriedade do [[UTF-8]] no [[GEMINI.md]] e na skill [[using-superantigravity]].

## Validação
Auditoria via [[wiki_health_check.py]] e verificação visual de arquivos críticos.

---
*Fonte: [[docs/plans/plan_v1_encoding_eradication.md]]*
