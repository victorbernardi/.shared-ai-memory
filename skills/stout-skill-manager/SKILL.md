---
name: stout-skill-manager
description: Use quando o usuario quer buscar, instalar ou adicionar skills ao projeto.
---

# stout-skill-manager

## Objetivo

Orquestrar o ciclo completo de adicao de skills ao ecossistema Stout: busca local, busca externa, auditoria de conflito, renderizacao multi-plataforma, e instalacao global.

## Fluxo

### 1. Busca Local

Consulta `stout-skill-registry/registry.json` via `local_search.py`.

- Match semantico por `role` + `triggers` (threshold >= 60%)
- Se skill local suficiente, apresenta ao usuario e encerra
- Se insuficiente, avanca para busca externa

### 2. Busca Externa

```bash
skillfish search <query>
```

- Apresenta resultados com nome, fonte e descricao
- Usuario escolhe skill ou decide criar uma nova

### 3. Auditoria de Conflito

```bash
python stout-skill-auditor/scripts/semantic_overlap.py --proposed-name "<nome>"
```

- **APPROVED** → avanca para instalacao
- **QUESTIONED** → pergunta ao usuario antes de continuar
- **REJECTED** → aborta e sugere alternativa local

### 4. Renderizacao e Instalacao

```bash
python scripts/global_installer.py --source-path skills/<skill> --artifacts-dir <artifacts>
```

- Renderiza pacotes para cada plataforma
- Instala em `~/.agents/skills/`, `~/.claude/skills/`, `~/.commandcode/skills/`
- Suporta `--replace` para sobrescrever destinos existentes
- Rollback automatico em caso de falha

### 5. Controle de Qualidade

```bash
python skill-sentinel/scripts/run_audit.py --skill <nome>
```

- Score >= 70 → registra como `active`
- Score < 70 → invoca `stout-improve-skill` (max 2 ciclos)

## Constraints

- NUNCA instalar sem aprovacao do usuario na fase de auditoria
- SEMPRE usar o path canonico para fontes
- NUNCA editar copias instaladas como fonte de verdade

## Scripts

- `scripts/orchestrator.py` — orquestra as 5 fases
- `scripts/global_installer.py` — instalacao transacional global
- `scripts/local_search.py` — busca semantica no registry
- `scripts/install_validator.py` — valida SKILL.md pos-download
