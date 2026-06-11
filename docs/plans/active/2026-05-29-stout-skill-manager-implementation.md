# Plano: stout-skill-manager + Multi-plataforma

**Spec:** `docs/superpowers/specs/2026-05-29-stout-skill-manager-design.md`  
**Data:** 2026-05-29  
**Status:** ativo

---

## Batch 1 — Proteção de Junctions (junction_guard.py)

### T1.1 — Criar `junction_map.yaml`

Arquivo de configuração com mapa canônico de junctions esperadas.

- Path: `skills/stout-skill-manager/config/junction_map.yaml`
- Conteúdo: dict `{path_junction: path_target}` para as 4 junctions ativas

### T1.2 — Criar `junction_guard.py`

Script que lê `junction_map.yaml`, verifica LinkType de cada path e recria junctions destruídas.

- Path: `skills/stout-skill-manager/scripts/junction_guard.py`
- Comportamento: exit 0 se tudo ok, exit 1 + log se recriou alguma

### T1.3 — Testar junction_guard.py

Executar o script e verificar saída com as junctions atuais intactas.

---

## Batch 2 — stout-skill-manager: estrutura base

### T2.1 — Criar SKILL.md do stout-skill-manager

Frontmatter universal com blocos `@if` por plataforma.

- Triggers: "busque skills", "instale skill", "adicionar skill ao projeto"
- Tier 1, category: orchestrator

### T2.2 — Criar `local_search.py`

Busca semântica no `registry.json` por role + triggers. Threshold 60%.

- Retorna lista ranqueada de skills ativas relevantes

### T2.3 — Criar `install_validator.py`

Valida SKILL.md pós-download: presença de frontmatter `name`, `version`, campo `tools`.

### T2.4 — Criar `thresholds.yaml`

Configuração de limiares: sentinel_min_score=70, local_match_threshold=60, improve_max_cycles=2.

---

## Batch 3 — stout-skill-manager: orquestrador

### T3.1 — Criar `orchestrator.py`

Implementa as 5 fases do fluxo:

1. Busca local via `local_search.py`
2. Busca externa via `skillfish search`
3. Auditoria via `stout-skill-auditor/scripts/semantic_overlap.py`
4. Instalação via `skillfish add --output <canonical_path>`
5. Qualidade via `skill-sentinel run_audit.py --skill <nome>`

- Chama `junction_guard.py` antes de qualquer escrita
- HITL no passo 2 (escolha do usuário) e passo 3 se QUESTIONED

---

## Batch 4 — stout-create-skill: arquivos de referência

### T4.1 — Criar `references/skill-anatomy.md`

Frontmatter obrigatório e opcional por plataforma (name, description, version, tools, tier).

### T4.2 — Criar `references/template-engine.md`

Sintaxe completa: `@if`, `@unless`, `@endif`, `@endunless`, `{{variable}}` com exemplos.

### T4.3 — Criar `references/platform-claude.md`

Especificações Claude Code: sem limite de tamanho, Tool use, MCP, seções recomendadas.

### T4.4 — Criar `references/platform-antigravity.md`

Especificações Antigravity CLI: dir `~/.gemini/antigravity-cli/skills/`, Jinja2, Jinja2 scripts.

### T4.5 — Criar `references/platform-commandcode.md`

Especificações CommandCode: dir `~/.commandcode/skills/`, frontmatter conciso, triggers obrigatórios.

---

## Batch 5 — stout-create-skill: atualização dos templates e agentes

### T5.1 — Atualizar `templates/tier-2-feature.md`

Adicionar blocos `<!-- @if platform=X -->` para Claude, Antigravity e CommandCode.

### T5.2 — Atualizar `scripts/blueprint_engine.py`

Adicionar campo `target_platforms[]` no blueprint e geração do `skill.config.json`.

### T5.3 — Atualizar `agents/code_drafter_agent.md`

Adicionar instrução explícita para consultar `references/` antes de gerar qualquer SKILL.md.

---

## Batch 6 — skillfish: atualização multi-plataforma + registry

### T6.1 — Atualizar `skills/skillfish/SKILL.md`

Frontmatter universal + blocos `@if` para Claude, Antigravity e CommandCode.
Atualizar `scripts/install.py` para usar `--output` canônico.

### T6.2 — Registrar skillfish no stout-skill-registry

Adicionar entrada com status `active` no `registry.json`.

### T6.3 — Deprecar audit-skill-manager

Adicionar header `[DEPRECADO]` no SKILL.md e atualizar status no `registry.json`.

---

## Critérios de conclusão

- `junction_guard.py` executa sem erros com as junctions atuais
- `orchestrator.py` tem os 5 métodos implementados com HITL nos pontos corretos
- `stout-create-skill/references/` contém os 5 arquivos
- Templates e agente atualizados com template engine
- `skillfish` usa path canônico e está no registry
- `audit-skill-manager` marcado como deprecated
