---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-create-skill
description: "Fábrica autônoma de skills de Tier 4. Implementa manufatura agêntica baseada em blueprints e orquestração de subagentes. Triggers de ativação: criar skill, nova skill, gerar skill, manufatura agêntica, scaffolding, blueprinting. EXIGE VEREDITO DO AUDITOR."
version: 1.1.0
author: Victor
tier: 4
source: custom
date_added: "2026-05-15"
category: meta-factory
---

# Stout Create Skill (A Fábrica)

## Visão Geral

Esta é a ferramenta oficial de manufatura do ecossistema Stout Inova. Ela opera no Tier 4 (Orchestrator), atuando como um maestro: consome aprovações, gera blueprints, delega a codificação para subagentes especialistas e finaliza registrando a nova skill no Ledger oficial.

## 🚀 Quando Usar

- Quando o `stout-skill-manager` (Fase 2) determina que nenhuma skill externa satisfaz a necessidade e o usuário escolhe **"criar nova skill"**.
- Para criar uma nova Agent Skill do zero após aprovação do `stout-skill-auditor`.
- Quando precisar de uma estrutura padrão Stout (Scaffolding) gerada automaticamente.
- Para garantir que novas skills nasçam com metadados e governança nota 10.

> **Fluxo recomendado:** use sempre `stout-skill-manager` como ponto de entrada.
> Ele executa busca local → skillfish → auditor → e então invoca esta skill automaticamente se necessário.
> Invocar `stout-create-skill` diretamente é permitido apenas se o auditor já rodou e gerou `audit_result.json`.

## 📦 Instalação

Skill de manufatura pré-instalada. Requer permissões de escrita no diretório `skills/` e acesso ao `stout-skill-registry`.

## ATENÇÃO: Pré-Requisito Obrigatório

**NUNCA utilize esta skill para criar algo sem antes ter passado pelo `stout-skill-auditor`.**
A Fábrica exige a presença de um arquivo `audit_result.json` válido com o veredito `"APPROVED"`. Se o veredito for "REJECTED" ou "QUESTIONED", o processo será abortado deterministicamente.

Quando invocada via `stout-skill-manager`, o auditor já rodou na Fase 3 — o `audit_result.json` estará presente.

## Como Usar (Comandos)

1. **Via stout-skill-manager (recomendado):** o manager invoca esta skill automaticamente na Fase 2.
2. **Direto:** `python scripts/create_pipeline.py --check-audit` → valida auditoria e dispara pipeline.

## 📚 Referências

- `docs/specs/2026-05-15-spec-stout-create-skill.md` — Especificação Técnica.
- `blueprint.json` — Schema de design gerado no processo.

## Idioma

Obrigatório o uso de **Português (PT-BR)** para todas as interações e geração de documentação de novas skills.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
