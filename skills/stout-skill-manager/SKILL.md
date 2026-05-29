---
name: stout-skill-manager
version: 1.0.0
tier: 1
category: orchestrator
description: >
  Use quando o usuário quer buscar, instalar ou adicionar skills ao projeto.
  Portão único de entrada para qualquer adição ao ecossistema — busca local,
  busca externa via skillfish, auditoria de conflito e controle de qualidade.
triggers:
  - busque skills
  - buscar skills
  - instale skill
  - adicionar skill ao projeto
  - encontre skills para esse projeto
  - quero instalar uma skill
tools:
  - claude-code
  - antigravity
  - commandcode
  - gemini-cli
author: Victor
---

# stout-skill-manager

## Objetivo

Orquestrar o ciclo completo de adição de skills ao ecossistema Stout: busca local → busca externa → auditoria de conflito → instalação → controle de qualidade.

<!-- @if platform=claude -->

## Fluxo Completo (5 Fases)

### Fase 1 — Busca Local

Consulta `stout-skill-registry/registry.json` via `local_search.py`.

- Match semântico por `role` + `triggers` (threshold >= 60%)
- Se skill local suficiente → apresenta ao usuário e encerra
- Se insuficiente → avança para Fase 2

### Fase 2 — Busca Externa

```bash
skillfish search <query>
```

- Apresenta resultados com nome, fonte e descrição
- **HITL obrigatório**: usuário escolhe skill ou decide criar uma nova
- "criar" → invoca `stout-create-skill`
- skill escolhida → avança para Fase 3

### Fase 3 — Auditoria de Conflito

```bash
python stout-skill-auditor/scripts/semantic_overlap.py \
  --proposed-name "<nome>" \
  --proposed-role "<role>" \
  --proposed-triggers "<t1,t2>"
```

- **APPROVED** → avança para Fase 4
- **QUESTIONED** → **PARA e pergunta ao usuário** antes de continuar
- **REJECTED** → aborta e sugere alternativa local

### Fase 4 — Instalação

```bash
python scripts/orchestrator.py --install <owner/repo> \
  --output "C:\Users\victor.bernardi\.shared-ai-memory\skills"
```

- Sempre usa path canônico — **nunca** escreve via junction
- Roda `junction_guard.py` antes de qualquer escrita
- Valida estrutura pós-download com `install_validator.py`

### Fase 5 — Controle de Qualidade

```bash
python skill-sentinel/scripts/run_audit.py --skill <nome>
```

- Score >= 70 → registra no `registry.json` como `active`
- Score < 70 → invoca `stout-improve-skill` (máx 2 ciclos)
- Após 2 ciclos sem sucesso → registra como `quarantine` e avisa usuário

## Constraints

- NUNCA escrever via paths de junction — sempre usar o path canônico
- SEMPRE executar `junction_guard.py` antes de qualquer escrita
- NUNCA instalar sem HITL explícito do usuário na Fase 2
- PARAR e perguntar ao usuário se o auditor retornar QUESTIONED

<!-- @endif -->

<!-- @if platform=antigravity,commandcode -->

## Fluxo

1. **Busca local** — `python scripts/local_search.py --query "<termo>"`
2. **Busca externa** — `skillfish search <query>` + HITL
3. **Auditoria** — `stout-skill-auditor` (APPROVED/QUESTIONED/REJECTED)
4. **Instalação** — `python scripts/orchestrator.py --install <repo>`
5. **Qualidade** — `skill-sentinel --skill <nome>` (score >= 70)

## Regras

- Instalar SEMPRE via path canônico `.shared-ai-memory\skills`
- Executar `junction_guard.py` antes de qualquer escrita
- HITL obrigatório antes de instalar

<!-- @endif -->

## Scripts

- `scripts/orchestrator.py` — orquestra as 5 fases
- `scripts/local_search.py` — busca semântica no registry
- `scripts/install_validator.py` — valida SKILL.md pós-download
- `scripts/junction_guard.py` — protege as junctions
- `config/thresholds.yaml` — limiares configuráveis
- `config/junction_map.yaml` — mapa canônico de junctions

## Critérios de Conclusão

A skill é concluída (done) quando:

1. `junction_guard.py` encerra com 0 erros
2. A skill escolhida passou pela auditoria (APPROVED ou QUESTIONED+confirmado)
3. `skillfish add` instalou a skill no path canônico
4. `install_validator.py` retornou `[OK]`
5. `skill-sentinel` deu score >= 70 ou status `quarantine` registrado com ciência do usuário
6. Entrada criada/atualizada em `stout-skill-registry/registry.json`
