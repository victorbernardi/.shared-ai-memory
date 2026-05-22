---
name: PLACEHOLDER_NAME
description: >
  Use quando PLACEHOLDER_TRIGGER. Orquestra processos complexos de PLACEHOLDER_DOMINIO
  via subagentes isolados com aprovação humana obrigatória (HITL) no fluxo.
  Skill de Orquestração (Tier 4) para gerenciamento de ecossistema e automação de elite.
version: 1.0.0
tier: 4
category: meta-factory
source: custom
date_added: '2026-05-15'
author: Victor
---

# PLACEHOLDER_NAME

## PRÉ-REQUISITOS OBRIGATÓRIOS
- SEMPRE verificar `enableSubagents: true` em `.gemini/settings.json`
- NUNCA executar sem aprovação explícita de Victor no ponto de HITL
- SEMPRE criar artefatos em `/tmp` antes de mover para produção

## Subagentes utilizados
- `@PLACEHOLDER_AGENT_1` — PLACEHOLDER_AGENT_1_DESC
- `@PLACEHOLDER_AGENT_2` — PLACEHOLDER_AGENT_2_DESC

## Fluxo de orquestração

### Etapa 1 — Pré-check
Verificar pré-requisitos antes de qualquer ação.

### Etapa 2 — Planejamento (contexto leve)
Ler configurações e gerar plano de execução.

### Etapa 3 — HUMAN-IN-THE-LOOP
Exibir plano para Victor. AGUARDAR aprovação explícita.

### Etapa 4 — Execução via subagentes
Instruir agentes especializados para as tarefas pesadas.

### Etapa 5 — Conclusão e Registro
Validar resultado, mover para pasta final e atualizar o Ledger.

## Constraints
- NUNCA executar sem aprovação de Victor na Etapa 3.
- SEMPRE usar subagentes para manter o Context Window principal leve.

## Examples

**Caso típico:**
Input: "PLACEHOLDER_INPUT"
Etapas: 1 → 2 → 3 (HITL) → 4 → 5
Output: "Processo concluído com sucesso."
