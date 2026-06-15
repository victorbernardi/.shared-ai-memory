# 🧩 ADDON: Configuration-Driven Development (CDD)

## Metadata

- **ID:** cdd
- **Version:** 1.3.0
- **Description:** Injeta a arquitetura orientada a configuração (Motor de Regras, Skill Router, GCC, Analytics e Sentinel).
- **Dependencies:** `jsonschema>=4.17`, `pyyaml>=6.0`

## Prerequisites

- A Phase 2 (Core Scaffolding ICM) deve ter sido concluída.
- O arquivo `CLAUDE.md` e o diretório `_config/` devem existir na raiz do projeto.

## Installation Steps

### 1. Criar estrutura `_config/`

O diretório `_config/` já existe (criado na Phase 2 ICM). Criar subpastas:

```
_config/
  config/        ← schemas e regras declarativas
  tools/         ← ferramentas de session-learning
```

### 2. Copiar Templates de Configuração

Copie os arquivos de `addons/cdd/templates/config/*` para `_config/config/` no projeto de destino.

- `rules.schema.json`
- `skills.schema.json`
- `rules.yaml`

### 3. Copiar Scripts de Core

Copie os arquivos de `addons/cdd/templates/*` (exceto as pastas config e tools) para `_config/` no projeto de destino.

- `config.py`
- `router.py`
- `gcc_controller.py`

### 4. Copiar Ferramentas de Session-Learning e Captura

Copie os arquivos de `addons/cdd/templates/tools/*` para `_config/tools/` no projeto de destino.

- `stout_memory_capture.py`

## Stitching

### 1. Atualizar CLAUDE.md (Seção Governança CDD)

Injete o seguinte bloco na seção `## Governança` do `CLAUDE.md`:

```markdown
### CDD — Configuration-Driven Development

- **Roteamento:** Toda lógica de ativação de skills é mediada pelo `SkillRouter` em `_config/router.py`.
- **Regras:** Definidas de forma declarativa em `_config/config/rules.yaml`.
- **Validação:** Schemas JSON em `_config/config/` garantem a integridade das configurações.
- **Rastreabilidade:** Checkpoints automáticos registrados em `.GCC/` via `GCCController`.
- **Session-Learning:** Captação de fatos e bugs gravada no SQLite `.stout/session_learning.db` via `_config/tools/stout_memory_capture.py`.
```

### 2. Atualizar CLAUDE.md (Seção Ferramentas e Skills)

Injete na seção `## Ferramentas e Skills`:

```markdown
#### CDD Runtime

- Destilar aprendizados: `python _config/tools/stout_memory_capture.py --transcript <caminho>`
- Injetar fatos anteriores: `python _config/tools/stout_memory_capture.py --inject --query "<termo>"`
```
