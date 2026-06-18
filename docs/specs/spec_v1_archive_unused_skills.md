# Especificação Técnica: Arquivamento de Skills Não Utilizadas (v1)

## 1. Contexto e Objetivo
O diretório `C:\Users\victor.bernardi\.shared-ai-memory\skills` acumulou um volume muito grande de skills (mais de 130 diretórios), das quais a maioria é raramente utilizada. Para otimizar a infraestrutura de desenvolvimento do agente e evitar sobrecarga de contexto e lentidão de busca, o usuário solicitou o arquivamento de uma lista específica de 80 skills.

O objetivo é mover estas skills fisicamente para a subpasta `_archived/` sob o mesmo diretório de skills e atualizar a fonte de verdade do ecossistema (`registry.json`) de acordo com as regras de governança Stout (não deletar, apenas marcar como deprecada/inativa).

## 2. Escopo do Arquivamento
As seguintes skills serão movidas do diretório principal para `_archived/`:

- `audit-context-guardian`
- `audit-logging-system`
- `audit-verification`
- `audit-webapp-testing`
- `caveman`
- `cdd-governance`
- `code-documentation-code-explain`
- `code-documentation-doc-generate`
- `code-refactoring-context-restore`
- `code-refactoring-refactor-clean`
- `code-refactoring-tech-debt`
- `code-review-ai-ai-review`
- `code-review-checklist`
- `code-reviewer`
- `code-review-excellence`
- `code-simplifier`
- `context-agent`
- `context-degradation`
- `context-driven-development`
- `context-fundamentals`
- `context-guardian`
- `context-management`
- `context-manager`
- `context-optimization`
- `data-build-dashboard`
- `data-context-extractor`
- `data-create-viz`
- `data-explore-code`
- `data-explore-data`
- `data-insight-reporter`
- `data-statistical-analysis`
- `data-storytelling`
- `data-validate-data`
- `data-validation`
- `data-visualization`
- `design-antigravity-expert`
- `design-high-end-visual`
- `design-industrial-brutalist`
- `design-kpi-dashboard`
- `design-liquid-glass`
- `diagnose`
- `improve-codebase-architecture`
- `internal-comms`
- `process-brd-generator`
- `process-context-compression`
- `process-context-degradation`
- `process-context-driven-development`
- `process-context-fundamentals`
- `process-context-management`
- `process-context-manager`
- `process-context-optimization`
- `process-context-restore`
- `process-context-save`
- `process-deep-research`
- `process-doc-orchestrator`
- `process-internal-comms`
- `process-meeting-assistant`
- `process-superantigravity`
- `process-user-story`
- `prototype`
- `stout-brainstorming`
- `stout-cdd-orchestrator`
- `stout-commit`
- `stout-data-analyze`
- `stout-data-sql-queries`
- `stout-data-write-query`
- `stout-dev-tdd`
- `stout-executing-plans`
- `stout-finishing-a-development-branch`
- `stout-immunity-gate`
- `stout-improve-skill`
- `stout-spec-validation`
- `stout-subagent-driven-development`
- `stout-systematic-debugging`
- `stout-writing-plans`
- `systematic-debugging`
- `tag-taxonomy`
- `tdd`
- `write-a-skill`
- `zoom-out`

## 3. Impacto no Ledger (`registry.json`)
As seguintes skills constantes no ledger `skills/stout-skill-registry/registry.json` deverão ser alteradas para `"status": "deprecated"` em conformidade com as diretrizes de governança (nunca deletar do registro, apenas mudar status):

- `stout-brainstorming`
- `stout-cdd-orchestrator`
- `stout-commit`
- `stout-data-analyze`
- `stout-data-sql-queries`
- `stout-data-write-query`
- `stout-dev-tdd`
- `stout-executing-plans`
- `stout-finishing-a-development-branch`
- `stout-immunity-gate`
- `stout-improve-skill`
- `stout-spec-validation`
- `stout-subagent-driven-development`
- `stout-systematic-debugging`
- `stout-writing-plans`

## 4. Requisitos de Implementação e Segurança
- O arquivamento será feito de forma atômica por meio de scripts seguros via terminal PowerShell.
- Não haverá deleção física. Todos os diretórios devem ser movidos para a pasta `C:\Users\victor.bernardi\.shared-ai-memory\skills\_archived`.
- Se uma pasta de destino em `_archived` já existir, o script tratará de mesclar/sobrescrever de forma limpa sem erros de permissão ou duplicação.
- O arquivo `registry.json` será editado cirurgicamente mantendo a conformidade com o esquema JSON aplicável.
