---
title: SEO GE Scanner
created_at: 2026-05-21
updated_at: 2026-05-21
summary: Ferramenta interativa e autonoma para auditoria de grupos economicos usando score multidimensional de confianca, operavel por humanos e agentes AI.
base_confidence: 0.92
lifecycle: draft
lifecycle_changed: "2026-05-21"
provenance:
  extracted: 0.85
  inferred: 0.15
  ambiguous: 0.0
tags: [inova, motor-identidade, automacao, grupos-economicos]
sources: [seo-ge-scanner-v2.md, seo-ge-interface-cli.md]
---

## O que e

Scanner interativo/autonomo para validacao de grupos economicos no Motor Identidade. Opera em dois modos: **interativo** (humano guiado por estados) e **autonomo** (`--auto`, para agentes AI). Calcula veredictos (WELD/DISCARD/PENDING) usando score multidimensional.

## Modos de operacao

| Modo | Comando | Uso |
|------|---------|-----|
| Interativo | `--busca "NOME OU CNPJ"` | Curadoria humana com exibicao de sugestoes |
| Autonomo | `--auto --a ID_A --b ID_B` | Auditoria sem interacao, persiste decisao automatica |
| Auditoria | `--audit --a ID_A --b ID_B` | Deep dive entre dois IDs |
| Decisao | `--decide WELD --a ID_A --b ID_B` | Registro manual de decisao |

## Score Multidimensional de Confianca

| Elo | Peso | Gatilho |
|-----|------|---------|
| C10: CEP exato | +3 | CEPs identicos |
| C10: CEP divergente | -2 | CEPs diferentes |
| GEO: Logradouro similar | +2 | Fuzzy >= 85% |
| GEO: Logradouro divergente | -1 | Fuzzy < 40% |
| C7: Email corporativo | +4 | Mesmo dominio nao-generico |
| C5: Telefone | +3 | Telefones identicos apos limpeza |

**Thresholds autonomicos:**
- score >= 3 → WELD (`expert_welds.json`)
- score <= -2 → DISCARD (`negative_welds.json`)
- outros → PENDING (`pending_welds.json` + revisao humana)

## Arquitetura

- **Zero duplicacao de logica**: importa `deep_dive_audit`, `record_decision` de `seo_ge_audit_tool.py` e `limpar_cnpj`, `limpar_telefone_c8` de `engine/welders.py`
- **Anti-duplicata**: `record_decision_safe()` normaliza IDs antes de persistir
- **CLI Gemini-friendly**: argparse robusto, zero `input()` no fluxo padrao, output estruturado

## Conceitos relacionados

[[motor-identidade]], [[motor-identidade-m0]], [[identidade-grupos-economicos]], [[reconciliacao-fuzzy]]
