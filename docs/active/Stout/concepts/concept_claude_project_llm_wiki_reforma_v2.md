---
name: LLM Wiki — Reforma Z Híbrido
description: Reforma do wiki-compiler com Ar9av/obsidian-wiki como motor novo, context-agent unificado como peneira, reset+rebuild do vault. 5 planos em docs/superpowers/plans/.
type: project
originSessionId: d9514933-84d2-47e9-8a28-1c957cdf5527
---
Reforma arquitetural do wiki pessoal iniciada em 2026-04-23. Motivada por poluição acumulada no vault atual e falta de unificação do context-agent entre os 4 agentes (Claude Code, OpenCode, Gemini CLI, Antigravity).

**Arquitetura Z Híbrido:** trocar o motor de compile (Gemini CLI + SCHEMA.md → Ar9av/obsidian-wiki) preservando contratos externos (`raw/_pending/`, SUGESTOES-HOJE.md, audit engine, estrutura flat kebab-case).

**Storage unificado:** `memory/context-agent/` (sessions/, cleaned/, archive/). Todas as 4 instalações de context-agent apontam para cá via env var `STOUT_ROOT` (default `C:/Projetos/Stout`).

**Peneira em 4 camadas:**
1. Session clean (context-agent session_summary.py)
2. Spec/plan clean (novo: context-agent superpowers_cleaner.py)
3. Ingest + audit (Ar9av + audit engine existente, sem check NLM)
4. Review gate humano (batch diff antes de commit)

**Spec:** `docs/superpowers/specs/2026-04-23-llm-wiki-reforma-design.md`

**Planos (5 fases sequenciais):**
1. `docs/superpowers/plans/2026-04-23-fase1-context-agent-unificado.md` — storage unificado + install Claude Code + origin tagging
2. `docs/superpowers/plans/2026-04-23-fase2-superpowers-cleaner.md` — Layer 2 da peneira
3. `docs/superpowers/plans/2026-04-23-fase3-ar9av-compilador.md` — motor novo em test-vault isolado
4. `docs/superpowers/plans/2026-04-23-fase4-reset-rebuild.md` — backup + git init + esvaziar + reseed híbrido em produção
5. `docs/superpowers/plans/2026-04-23-fase5-index-nlm-feedback.md` — INDEX.md + SUGESTOES acumulativo + NLM sync

**NLM output:** notebook fixo `987bb91c-86a3-4a9a-a3db-4dbaa150bd18` — auto-sync após cada compile, manifesto SHA256 local.

**NLM research (para sugestões):** cross_notebook_query filtrado por notebooks com "estudo" no título (ex: `857e52cf-639c-4043-9d62-22606442b2e9` — Estudo LLM Wiki).

**Componentes deprecados (Fase 4 remove):** `harvest_brain.sh`, escrita do Bibliotecário em raw/_pending/, fragmentos NLM-synthesis em pending, sobrescrita de SUGESTOES-HOJE.md.

**How to apply:** quando retomar a execução, começar pela Fase 1 (plan é auto-contido, TDD passo-a-passo). Usar `superpowers:subagent-driven-development` para planos longos (recomendado pelo próprio plan). Fase 4 exige 2h sem interrupções e tem pontos de no-go claros.
