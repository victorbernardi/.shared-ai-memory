---
name: PLACEHOLDER_NAME
version: 1.0.0
tier: 2
category: PLACEHOLDER_CATEGORY
description: >
  Use quando PLACEHOLDER_TRIGGER. Provê capacidades de PLACEHOLDER_ACAO
  suportando múltiplos cenários e integração com scripts auxiliares.
  Skill de característica (feature) para processamento de PLACEHOLDER_DOMINIO.
tools:
  - claude-code
  - antigravity
  - commandcode
triggers:
  - PLACEHOLDER_TRIGGER_1
  - PLACEHOLDER_TRIGGER_2
author: Victor
---

# PLACEHOLDER_NAME

## Objetivo

PLACEHOLDER_OBJETIVO.

## Inputs esperados

- PLACEHOLDER_INPUT_1: descrição
- PLACEHOLDER_INPUT_2: descrição

<!-- @if platform=claude -->

## Fluxo Detalhado

1. PLACEHOLDER_PASSO_1
2. PLACEHOLDER_PASSO_2
3. Se necessário: `python scripts/PLACEHOLDER_SCRIPT.py --arg <valor>`
4. PLACEHOLDER_PASSO_4

## Exemplos

**Caso simples:**
Input: "PLACEHOLDER_INPUT_SIMPLES"
Ação: PLACEHOLDER_ACAO_SIMPLES
Output: PLACEHOLDER_OUTPUT_SIMPLES

**Caso complexo:**
Input: "PLACEHOLDER_INPUT_COMPLEXO"
Ação: Usa `scripts/PLACEHOLDER_SCRIPT.py`
Output: PLACEHOLDER_OUTPUT_COMPLEXO

<!-- @endif -->

<!-- @if platform=antigravity,commandcode -->

## Fluxo

1. PLACEHOLDER_PASSO_1
2. PLACEHOLDER_PASSO_2
3. `python scripts/PLACEHOLDER_SCRIPT.py --arg <valor>`

<!-- @endif -->

## Constraints

- NUNCA PLACEHOLDER_RESTRICAO_1
- SEMPRE PLACEHOLDER_RESTRICAO_2
- NÃO PLACEHOLDER_RESTRICAO_3

## Scripts disponíveis

- `scripts/PLACEHOLDER_SCRIPT.py` — PLACEHOLDER_SCRIPT_DESC
