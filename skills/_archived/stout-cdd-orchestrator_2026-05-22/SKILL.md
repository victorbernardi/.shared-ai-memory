---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-cdd-orchestrator
description: "Motor Mãe do ecossistema local. Orquestra a injeção dinâmica de instruções baseada no catálogo CDD (skills_catalog.yaml). Triggers: launch, init cdd, orquestrar skills, cdd core."
version: 1.0.0
author: Arquiteto Stout
tier: 1
category: meta-orchestrator
---

# Stout CDD Orchestrator

## [LEI GLOBAL - KARPATHY LAWS]

Qualquer sessão orquestrada por este motor DEVE obedecer às seguintes diretrizes comportamentais:

1. **Pense Antes de Codificar:** Nunca assuma interpretações silenciosamente. Explicite suposições e trade-offs. Pare se houver confusão.
2. **Simplicidade Primeiro:** Código mínimo necessário. Proibido abstrações especulativas ou overengineering.
3. **Mudanças Cirúrgicas:** Toque apenas no necessário. Não reformate ou "melhore" código adjacente não relacionado à tarefa.
4. **Execução Orientada a Metas:** Defina critérios de sucesso verificáveis e loops de validação (TDD) antes de implementar.

## Visão Geral

Esta é a skill fundamental do projeto. Ela transforma habilidades estáticas em entidades dinâmicas governadas por arquivos de configuração. Nenhuma skill local deve ser usada sem passar por este motor.

## 🚀 Como Usar

Para ativar qualquer skill local seguindo o padrão CDD:

```bash
python scripts/launcher.py --skill stout-immunity-gate
```

## 📦 Instalação

Skill de infraestrutura local. Requer `PyYAML` instalado no ambiente Python.

## 📚 Referências

- `data/config/skills_catalog.yaml` — Catálogo Central de Inteligência.
- `data/config/skills.schema.json` — Contrato de dados das habilidades.

## Idioma

Obrigatório o uso de **Português (PT-BR)** para o gerenciamento de sessões CDD.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.
