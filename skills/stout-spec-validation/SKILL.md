---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-spec-validation
description: "Validação de consistência entre SOW e Especificações Técnicas no ecossistema Stout. Garante rastreabilidade total (AC -> FR -> Teste). Triggers: validar especificação, consistência, rastreabilidade, validação de requisitos, spec validation, consistency check."
version: 1.2.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-16"
category: governance
---

# 🧠 Stout Spec Validation (Local Elite)

Esta skill é o portão de qualidade final da fase de Design. Ela garante que tudo o que foi prometido no SOW (Critérios de Aceitação) esteja mapeado na Spec Técnica e coberto por Testes.

## 🚀 Quando Usar

- OBRIGATORIAMENTE após gerar uma Spec via `stout-brainstorming`.
- Antes de iniciar a implementação (`dev-tdd`).
- Para auditar a integridade da Matriz de Rastreabilidade.

---

## 🔄 Fluxo de Trabalho

Toda a inteligência técnica integral (168+ linhas), incluindo o sistema de IDs (AC, FR, T), as 11 categorias de checagem técnica e o checklist de integridade, foi preservada e movida para o arquivo de referência técnica.

**CONSULTE OBRIGATORIAMENTE:** `@references/check-list.md` antes de emitir o laudo.

---

## 📦 Instalação

Skill integrada localmente ao projeto CDD. Análise de Markdown 100% isolada.

## 💻 Comandos

Para ativar via orquestrador local:

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-spec-validation
```

## 🛡️ Governanca

- Nenhuma Spec é considerada "READY FOR DEV" com erros P0.
- Exige mapeamento explícito de AC para FR.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.
