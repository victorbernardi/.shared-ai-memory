---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

name: stout-skill-registry
description: "Fonte única de verdade e Ledger de todas as skills do ecossistema Stout. Gerencia inventário, metadados, versões e dependências. Triggers de ativação: registrar skill, remover skill, listar skills, consultar registry, skill já existe, ledger, inventário, metadados, dependencies."
version: 1.2.0
author: Victor
tier: 3
source: custom
date_added: "2026-05-15"
category: meta-governance
---

# stout-skill-registry

## Responsabilidade única

Este registro é a **única fonte de verdade** sobre quais skills existem no
ecossistema Stout, seus papéis, versões e status. Toda skill criada, melhorada
ou depreciada DEVE ser registrada aqui.

## 🚀 Quando Usar

- Antes de criar uma skill → verificar se papel já existe.
- Após criar uma skill → registrar a nova entrada.
- Após melhorar uma skill → fazer bump de versão no Ledger.
- Para auditar o ecossistema → listar todas as skills ativas.
- Para gerenciar dependências entre as habilidades de elite.

## 📦 Instalação

A skill já vem pré-instalada no núcleo do ecossistema Stout. Não requer dependências externas.

## Operações disponíveis (Comandos)

### Registrar nova skill

```bash
python scripts/register_skill.py --name "stout-<nome>" --path "skills/stout-<nome>" --tier <1|2|3|4> --category "<categoria>" --role "<papel único>" --triggers "<t1,t2>"
```text

### Consultar skills existentes

```bash
python scripts/query_registry.py --status active
python scripts/query_registry.py --category "meta-governance"
python scripts/query_registry.py --impact "stout-<nome>"
```text

### Deprecar skill obsoleta

```bash
python scripts/deregister_skill.py --name "stout-<nome>" --reason "<motivo>"
```text

## Regras de governança

- TODA skill nova deve ser registrada antes de ser usada em produção.
- NUNCA deletar entradas do registry.json — apenas deprecar.
- SEMPRE garantir que o campo `role` seja ÚNICO.
- Nomes seguem padrão `stout-kebab-case` obrigatoriamente.

## 📚 Referências

- `references/versioning_guide.md` — Guia SemVer e Ciclo de Vida.
- `schemas/skill_entry.schema.json` — Estrutura de dados do Ledger.

## Integração com o ecossistema

```text
stout-skill-auditor  ──lê──▶  registry.json
stout-create-skill   ──grava▶  registry.json
stout-improve-skill  ──grava▶  registry.json (bump-version)
```text

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando o objetivo declarado foi atingido e o artefato gerado está salvo.
