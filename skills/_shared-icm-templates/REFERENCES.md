---
system: stout-global
layer: 3
role: references_and_knowledge
---

# REFERENCES.md — Caminhos Canônicos

## Caminhos do Workspace ICM

| Recurso | Caminho | Propósito |
|---------|---------|-----------|
| Banco SQLite | `.stout/session_learning.db` | Memória semântica persistente |
| Catálogo CDD | `_config/skills_catalog.yaml` | Índice global de skills (addon CDD) |
| Issues Conhecidos | `docs/governance/known_issues.md` | Incidentes reincidentes |
| Backlog Evolução | `docs/governance/evolution_backlog.md` | Melhorias arquiteturais |
| Scripts compartilhados | `shared/` | Utilitários reutilizados entre estágios |
| Infra CDD | `_config/` | router.py, rules.yaml, schemas/ (se addon ativo) |

## Artefatos de Saída

- `docs/specs/YYYY-MM-DD-nome.md` — Especificações
- `docs/plans/YYYY-MM-DD-nome.md` — Planos de implementação

## Convenções

- Governança: **Português (PT-BR)**
- Encoding UTF-8 obrigatório (sem BOM)
- Caminhos relativos à raiz do workspace
