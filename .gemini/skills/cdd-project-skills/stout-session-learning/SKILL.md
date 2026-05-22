---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-session-learning
description: "Destilador de Cognição Local. Consolida aprendizados, erros e heurísticas via banco SQLite, exporta o relatório Markdown padrão e atualiza automaticamente os logs de bugs conhecidos e backlog de evolução."
version: 1.0.0
author: Engenheiro Stout
tier: 2
category: governance
---

# Stout Session Learning

## [LEI GLOBAL - KARPATHY LAWS]

Qualquer sessão orquestrada por este motor DEVE obedecer às seguintes diretrizes comportamentais:

1. **Pense Antes de Codificar:** Nunca assuma interpretações silenciosamente. Explicite suposições e trade-offs. Pare se houver confusão.
2. **Simplicidade Primeiro:** Código mínimo necessário. Proibido abstrações especulativas ou overengineering.
3. **Mudanças Cirúrgicas:** Toque apenas no necessário. Não reformate ou "melhore" código adjacente não relacionado à tarefa.
4. **Execução Orientada a Metas:** Defina critérios de sucesso verificáveis e loops de validação (TDD) antes de implementar.

## Visão Geral

Esta skill encapsula o mecanismo híbrido de **Session-Learning** local do ecossistema Stout. Ela atua na triagem léxica e regex offline dos logs do transcript para extrair fatos, decisões arquiteturais, heurísticas de self-healing e incidentes técnicos, alimentando uma base SQLite persistente e gerando artefatos vivos de governança de documentação.

Ela atua integrada por ganchos (`pre_action`) ao comando de salvamento do `context-agent` global via motor de regras CDD.

## 🚀 Como Usar

### Execução Automática (Pipeline Unificado)
A skill é acionada autonomamente como `pre_action` de qualquer intenção de fechar sessão ou salvar contexto:
```bash
# O motor CDD interceptará a intenção e executará o pipeline
"salvar contexto" ou "fechar sessão"
```

### Invocação Direta da Skill
Para acionar especificamente a destilação de aprendizados da sessão atual de forma manual:
```bash
python skills/stout-session-learning/scripts/stout-memory-capture.py
```

### Geração de Relatórios e Consultas
O script local suporta argumentos de interface para consultas e visualização tática:
```bash
# Consultar aprendizados indexados por relevância lexical
python skills/stout-session-learning/scripts/stout-memory-capture.py --query "PermissionError"

# Regenerar os Markdowns conhecidos e backlogs
python skills/stout-session-learning/scripts/stout-memory-capture.py --export
```

## 📦 Estrutura de Artefatos Gerados

- `.stout/session_learning.db` — Banco de dados SQLite indexado via FTS5 de longo prazo.
- `aprendizados_sessao.md` — Relatório individual e estético pós-morte da sessão ativa.
- `docs/governance/known_issues.md` — Lista viva consolidada de incidentes reincidentes e workarounds.
- `docs/governance/evolution_backlog.md` — Lista prioritária de melhorias arquiteturais e estéticas.

## 📚 Referências

- `data/config/skills_catalog.yaml` — Catálogo Central de Inteligência CDD.
- `skills/stout-session-learning/scripts/stout-memory-capture.py` — Motor programático de destilação.
- `notes/failure-log.md` — Log local de incidentes e falhas humanas/técnicas.

## Idioma

Obrigatório o uso de **Português (PT-BR)** para o gerenciamento de sessões CDD.

## Quando Usar

- Quando a sessão de desenvolvimento for finalizada e for necessário consolidar o conhecimento, aprendizados, erros e incidentes.
- Para gerar relatórios e alimentar o banco SQLite tático de auto-healing.

## Escopo

Esta skill se aplica a todas as sessões de desenvolvimento no ecossistema Stout.

## Critérios de Conclusão

A execução é considerada concluída quando o script programático encerra com sucesso, persistindo os dados no SQLite e exportando o arquivo `aprendizados_sessao.md`.
