---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

name: stout-adr
description: "Gestão de Architecture Decision Records (ADR) seguindo o padrão MADR v4 local. Triggers: adr, arquitetura, decisão técnica, documentação, MADR, decision record, design data, infraestrutura."
version: 1.2.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-16"
category: governance
---

# 🧠 Stout ADR (Local Elite)

Esta skill é responsável por oficializar escolhas técnicas, mudanças de processo e padrões de infraestrutura. Segue o padrão MADR v4.

## 🚀 Quando Usar

- Para registrar decisões de arquitetura e design de dados.
- Para registrar mudanças em fluxos de trabalho ou políticas de segurança.
- Para retiring (depreciação) de tecnologias.

---

## 🔄 Fluxo de Trabalho

Toda a inteligência técnica (templates, heurísticas, procedimentos de substituição e scripts de validação) está fragmentada para otimização de contexto.

**CONSULTE OBRIGATORIAMENTE:**

1. `@references/madr-format.md` - Formato e seções obrigatórias.
2. `@scripts/` - Automações de pre-check e validação.
3. `@templates/` - Modelos para cada tipo de decisão.

---

| Topic     | Resource                                      |
| --------- | --------------------------------------------- |
| MADR      | ${CLAUDE_SKILL_DIR}/references/madr-format.md |
| Fowler    | ${CLAUDE_SKILL_DIR}/references/fowler-adr.md  |
| Templates | ${CLAUDE_SKILL_DIR}/templates/                |
| Scripts   | ${CLAUDE_SKILL_DIR}/scripts/                  |

## 📦 Instalação

Skill integrada localmente ao projeto CDD. Armazenamento em `docs/decisions/`.

## 💻 Comandos

Para ativar via orquestrador local:

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-adr
```text

## 🛡️ Governanca

- Decisões aceitas são imutáveis.
- Exige validação via `validate_adr.py` antes da oficialização.

## When to Use

This skill is applicable to execute the workflow or actions described in the overview.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
