---
name: Docs Centralizados — Modelo B + PROJECT_ID
description: Decisão de centralizar docs/specs e docs/plans de todos os projetos em Stout/docs/projects/, com PROJECT_ID definido verbalmente no início de cada sessão
type: project
---
Decisão tomada em 2026-05-04. Contexto: docs estavam sendo duplicados porque as skills process-superantigravity, process-brainstorming e process-writing-plans usam caminho relativo `./docs/` — gravando em cada projeto separado sem visibilidade cruzada entre motores.

**Modelo escolhido (B):** todos os docs vão para `C:\Projetos\Stout\docs\projects\<project_id>\specs\` e `plans\`.

**PROJECT_ID:** definido verbalmente no início de cada sessão pela skill de inicialização (process-superantigravity / using-superpowers). Formato kebab-case `cliente/nome-projeto` (ex: `inova/motor-m6`, `notebooklm/kb-builder`, `stout/wiki-compiler`). Não usa arquivo de config — é efêmero por sessão.

**Por que verbal e não arquivo:** GEMINI.md/ANTIGRAVITY.md cobre múltiplos projetos (ex: Inova tem M1-M6, Wave9, OnePage no mesmo diretório). Um único project_id no manifesto não funciona.

**Fluxo de inicialização:**
1. Skill lista projetos existentes em `Stout/docs/projects/`
2. Pergunta ao usuário qual projeto
3. Normaliza para kebab-case automaticamente
4. Define DOCS_SPECS_PATH e DOCS_PLANS_PATH para a sessão

**`./memory/` removida das skills:** instrução obsoleta — context-agent cobre memória de sessão, wiki cobrirá conhecimento consolidado pós-Fase 3.

**Migração de `docs/superpowers/`:** adiada para pós-deploy. Mover para `docs/projects/stout/` após Modelo B validado. Estrutura atual mantida durante o deploy para não quebrar referências nos planos ativos.

**O que muda nas skills (pendente de implementação):**
- `process-superantigravity` — adicionar bloco de inicialização PROJECT_ID
- `process-brainstorming` — trocar `./docs/specs/` por `$DOCS_SPECS_PATH`
- `process-writing-plans` — trocar `./docs/plans/` por `$DOCS_PLANS_PATH`
- `using-superpowers` (Claude) — espelhar o bloco de inicialização
- Remover instrução `./memory/` do process-superantigravity

**How to apply:** implementar após fechar Fase 1 do LLM Wiki Reforma (bugs save + FTS5 search.py). Criar spec formal antes de tocar nas skills.
