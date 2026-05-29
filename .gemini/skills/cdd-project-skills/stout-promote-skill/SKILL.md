---
name: stout-promote-skill
description: "Promove skills desenvolvidas no projeto CDD para o golden copy (~/.shared-ai-memory/skills/). Executa auditoria, exibe pendências, dry-run e gate de aprovação humana antes de copiar. Triggers: promover skill, promote skill, publicar skill, enviar para global."
version: 1.0.0
author: Victor
tier: 2
source: custom
date_added: "2026-05-22"
category: meta-governance
---

# stout-promote-skill

## Responsabilidade única

Promover skills do projeto CDD ao golden copy com auditoria, rastreabilidade e aprovação humana obrigatória.

## Quando Usar

- Quando uma skill foi desenvolvida e testada no projeto CDD e está pronta para ser usada globalmente.
- Para verificar quais skills estão pendentes de promoção (`promoted_at == null` e audit PASS).

## Pré-Requisitos

- `scripts/audit_skills.py` presente no projeto
- `scripts/promote_skills.py` presente no projeto
- Campo `promoted_at` no `skills/stout-skill-registry/registry.json`

## Como Usar

```bash
python skills/stout-promote-skill/scripts/promote_runner.py
```text

## Fluxo

1. Roda `audit_skills.py` — gera relatório de qualidade
2. Exibe skills com `promoted_at = null` e audit PASS (prontas) vs FAIL (não prontas)
3. Usuário escolhe qual skill (ou todas) promover
4. Dry-run com preview do que será copiado
5. Confirmação humana obrigatória
6. Executa `promote_skills.py` e atualiza `promoted_at` no registry

## Escopo

Aplica-se apenas ao projeto CDD e projetos que sigam o padrão Stout com `registry.json` e scripts de audit/promote.

## Critérios de Conclusão

A skill é concluída quando `promote_runner.py` encerra com código 0 e o campo `promoted_at` da skill promovida está atualizado no `registry.json`.
