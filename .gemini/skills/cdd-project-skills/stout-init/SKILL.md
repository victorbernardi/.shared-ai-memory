---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

name: stout-init
description: "Inicialização modular de projetos Stout com arquitetura de Addons. Triggers: inicializar projeto, novo projeto, scaffold, stout-init, projeto modular."
version: 2.1.0
author: Arquiteto Stout
tier: 3
source: custom
date_added: "2026-05-16"
category: meta-governance
---

# 🚀 SKILL: STOUT-INIT V2.1 — Scaffolding Modular de Alta Fidelidade

## Propósito

Garantir que todo novo projeto nasça com a base técnica nota 100 da Stout, unindo o scaffolding dinâmico da V2 com a inteligência de templates da V1.

---

## 🔄 Fluxo de Trabalho e Inteligência

A inteligência de inicialização está fragmentada para máxima eficiência:

1. **Protocólos de Scaffolding:** `@references/scaffolding-protocols.md` (As 4 fases).
2. **Templates de Arquivo:** `@references/templates-core.md` (GEMINI.md, ANTIGRAVITY.md).
3. **Configuração Técnica:** `@references/infra-logic.md` (MCPs, Junctions, Comandos).
4. **Sistema de Addons:** Localizado em `/addons/` (Injeção de CDD, Schemas e Ferramentas).

---

## 🚀 Addons Disponíveis (Stout Registry)

- **CDD Addon:** Injeta o Motor de Regras, GCC Controller e Analytics.
  - Ver `@addons/cdd/ADDON.md` para instruções de injeção.

## 📦 Instalação

Skill de infraestrutura local integrada ao ecossistema Stout.

## 💻 Comandos

Para ativar via orquestrador local:

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-init
```text

## 🛡️ Governanca

- **Modularidade:** Proibido injetar lógica de addon no orquestrador core.
- **Qualidade:** Uso obrigatório do `markdown_auto_fixer_v1.py` na finalização.
- **Encoding:** Cabeçalho UTF-8 mandatório em todos os scripts gerados.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
