---
name: Knowledge Graph → Obsidian — Implementado
description: Extração de entidades e mapeamento de relações implementados no Trigger Gamma do librarian_policy.md
type: project
originSessionId: 5e7de749-7590-4e46-a483-9260d9448d89
---

Implementado em 2026-04-17. Extensão do `librarian_policy.md` em duas fases:

**Fase 1 — Extração de Entidades:**
- Trigger Gamma estendido para detectar entidades (concretas e conceitos) na sessão
- Deduplicação via `wiki/INDEX.md`
- Seção `## Entidades Detectadas` com `### Concretas`, `### Conceitos`, `### Relações` no handoff

**Fase 2 — Mapeamento de Relações:**
- Nova seção `## Detecção de Relações` com comportamento inline durante a conversa
- Alta confiança → `[Relação detectada]` sinalizado imediatamente
- Incerto → `[Relação possível]` com confirmação de Victor
- Vocabulário fechado de 7 tipos: evolução de, substitui, implementa, alimenta, pertence a, usado por, baseado em
- Relações confirmadas (S/N) registradas em `### Relações` no handoff

**Why:** Victor quer que o Obsidian Graph View mostre conexões entre entidades do ecossistema (Inova, Stout, Antigravity) sem precisar criar links manualmente.

**How to apply:** Feature está ativa — não reabrir como pendência. Próxima evolução possível: banco de grafo explícito para consultas semânticas ("quais engines foram usadas pelo cliente XYZ?") — mas fora do escopo atual.
