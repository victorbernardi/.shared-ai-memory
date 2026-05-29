---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

name: stout-improve-skill
description: "Orquestrador de refatoração e Auto-Healing de Tier 4. Diagnostica gaps de qualidade e governança baseando-se no Sentinel e aplica patches automáticos ou assistidos. Triggers de ativação: melhorar skill, refatorar skill, atualizar skill, otimizar, auto-healing, tuning ecossistema."
version: 1.1.0
author: Victor
tier: 4
source: custom
date_added: "2026-05-15"
category: meta-factory
---

# Stout Improve Skill (O Melhorador)

## Visão Geral

Enquanto a `stout-create-skill` constrói do zero, o Melhorador atua sobre skills existentes para elevar o Tier, resolver sobreposições e aplicar melhorias de código e documentação (Padrão Ouro).

## 🚀 Quando Usar

- Para refatorar uma skill existente (ex: código, segurança, performance).
- Quando o `stout-skill-auditor` rejeitar uma ideia por sobreposição (indicando mesclagem).
- Para executar o Auto-Healing baseado em laudos do Skill Sentinel.

## 📦 Instalação

Skill de manutenção pré-instalada. Requer acesso ao `stout-skill-registry` e ao diretório global do `skill-sentinel`.

## Como Funciona (Fluxo de Melhoria)

1. **Diagnóstico (`diag_runner.py`):** Consome analisadores do Sentinel e gera o `elite_audit_report.json`.
2. **Plano e HITL:** O orquestrador (`apply_patch.py`) apresenta as alterações e aguarda autorização [Y/N] para mudanças em código.
3. **Execução:** Delega edições para subagentes em `agents/`.
4. **Registro:** Conecta-se ao Ledger para realizar o *bump* de versão.

## Comandos Principais

```bash
# Diagnosticar
python scripts/diag_runner.py --target "stout-nome-da-skill"

# Aplicar patches automáticos em documentação
python scripts/apply_patch.py --target "stout-nome-da-skill" --auto
```text

## 📚 Referências

- `docs/specs/2026-05-15-spec-ecosystem-tuning.md` — Especificação de Auto-Healing.
- `elite_audit_report.json` — Laudo de diagnóstico processável.

## Idioma

Obrigatório o uso de **Português (PT-BR)** para todas as interações e relatórios de melhoria.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
