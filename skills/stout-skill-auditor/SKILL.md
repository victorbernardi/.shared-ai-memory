---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-skill-auditor
description: "Porteiro e Auditor de Elite do ecossistema Stout. Avalia intenções e papéis (roles) para detectar ambiguidade, redundância ou sobreposição semântica com habilidades existentes. Triggers de ativação: criar skill, nova skill, precisamos de, falta uma skill, ambiguidade, overlap, duplicidade, conflito semântico."
version: 1.1.0
author: Victor
tier: 3
source: custom
date_added: "2026-05-15"
category: meta-governance
---

# stout-skill-auditor

## Responsabilidade única

Ser o porteiro do ecossistema. Garantir que **nenhuma skill nova crie ambiguidade**
ou sobreposição de papel com skills existentes no Ledger.

## 🚀 Quando Usar

- OBRIGATORIAMENTE antes de criar ou planejar qualquer nova skill no ecossistema Stout.
- Quando houver dúvida se uma habilidade já existe sob outro nome.
- Para verificar se uma intenção de usuário ("preciso de x") já é atendida por uma skill ativa.

## 📦 Instalação

Skill de governança pré-instalada. Requer acesso de leitura ao `stout-skill-registry`.

## Fluxo de auditoria (Comandos)

### Passo 1 — Coletar intenção

Solicite ao usuário: Nome proposto, Papel (role), Triggers e Descrição.

### Passo 2 — Consultar Ledger

```bash
python ../stout-skill-registry/scripts/query_registry.py --status active
```

### Passo 3 — Calcular sobreposição semântica

```bash
python scripts/semantic_overlap.py --proposed-name "<nome>" --proposed-role "<papel>" --proposed-triggers "<t1,t2>"
```

### Passo 4 — Emitir veredicto

- **APPROVED:** Papel único confirmado. Avance para stout-create-skill.
- **QUESTIONED:** Sobreposição parcial. Requer decisão humana.
- **REJECTED:** Ambiguidade total. Use stout-improve-skill.

## 📚 Referências

- `docs/specs/2026-05-15-spec-stout-skill-auditor.md` — Especificação Técnica.
- `audit_result.json` — Artefato obrigatório para a Fábrica.

## Idioma

Obrigatório o uso de **Português (PT-BR)** para todas as interações e laudos.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
