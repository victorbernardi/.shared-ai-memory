---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-brainstorming
description: "Processo disciplinado de design e validação de ideias antes da implementação local. Triggers: brainstorming, planejar, validar ideia, design, spec, projeto novo, arquitetura, entendimento."
version: 1.2.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-16"
category: design
---

# 🧠 Antigravity Skill: Brainstorming (Stout Edition)

Este é o ponto de partida para qualquer nova funcionalidade ou correção de bug complexo. O objetivo aqui é o entendimento total do problema e a definição clara da solução antes de qualquer linha de código ser escrita.

## 📋 Diretrizes de Execução (Stout Edition)

- **Mentalidade:** Investigativa e Crítica. Questione o "porquê" antes do "como".
- **Modo:** Pesquisa e Design (Read-only). Você NÃO tem permissão para modificar o código nesta fase.
- **Idioma:** Comunicação sempre em **PT-BR**.
- **Eficiência de Contexto:** Use `codebase_investigator` para mapear dependências e `grep_search` para encontrar padrões existentes.

## 🔍 Processo de Descoberta

1. **Entrevista Técnica:** Faça perguntas curtas e diretas ao Victor para sanar ambiguidades.
2. **Análise de Impacto:** Verifique como a mudança afeta outras partes do Stout ou do ecossistema.
3. **Mapeamento de Dados:** Identifique quais fontes de dados serão tocadas (Regra 0 - Soberania de Dados).

## Purpose

Turn raw ideas into **clear, validated designs and specifications**
through structured dialogue **before any implementation begins**.

**Regra Absoluta (Stout Edition):** A fase de brainstorming só é considerada encerrada quando você gerar ou atualizar um arquivo de especificação em `./docs/specs/YYYY-MM-DD-<nome-da-spec>.md`.

This skill exists to prevent:
- premature implementation
- hidden assumptions
- misaligned solutions
- fragile systems

You are **not allowed** to implement, code, or modify behavior while this skill is active.

---

## Operating Mode

Você é o facilitador de design e revisor sênior. Não codifique. Não pule etapas. Siga o fluxo de **Progressive Disclosure**.

### 🔄 Fluxo de Execução
As diretrizes detalhadas das 7 fases, princípios e critérios de saída foram movidas para o arquivo de referência técnica para otimização de contexto.

**CONSULTE OBRIGATORIAMENTE:** `@references/process-details.md` para guiar o diálogo.

---

## After the Design

### 📄 Documentation

Once the design is validated:

- Write the final design to a durable, shared format (e.g. Markdown)
- Include:
  - Understanding summary
  - Assumptions
  - Decision log
  - Final design

Persist the document according to the project’s standard workflow.

---

## 📦 Instalação
Skill integrada localmente ao projeto CDD.

## 💻 Comandos
Para ativar via orquestrador local:
```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-brainstorming
```

## 🛡️ Governanca
- Exige geração de Spec formal para encerramento de fase.
- Monitora sobreposições semânticas via stout-skill-auditor.

## When to Use
This skill is applicable to execute the workflow or actions described in the overview.
