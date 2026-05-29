# 🧩 ADDON: Configuration-Driven Development (CDD)

## Metadata

- **ID:** cdd
- **Version:** 1.2.0
- **Description:** Injeta a arquitetura orientada a configuração (Motor de Regras, Skill Router, GCC, Analytics e Sentinel).
- **Dependencies:** `jsonschema>=4.17`, `pyyaml>=6.0`

## Prerequisites

- A Phase 2 (Core Scaffolding) deve ter sido concluída.
- O diretório `src/` e o arquivo `GEMINI.md` devem existir na raiz do projeto.

## Installation Steps

### 1. Criar estrutura de dados

Crie o diretório `data/config/` na raiz do projeto.

### 2. Copiar Templates de Configuração

Copie os arquivos de `addons/cdd/templates/config/*` para `data/config/` no projeto de destino.

- `rules.schema.json`
- `skills.schema.json`
- `rules.yaml`

### 3. Copiar Scripts de Core

Copie os arquivos de `addons/cdd/templates/*` (exceto as pastas config e tools) para `src/` no projeto de destino.

- `config.py`
- `router.py`
- `gcc_controller.py`

### 4. Copiar Ferramentas de Session-Learning e Captura

Copie os arquivos de `addons/cdd/templates/tools/*` para `src/tools/` no projeto de destino.

- `stout_memory_capture.py`

## Stitching

### 1. Atualizar GEMINI.md (Operação)

Injete o seguinte bloco na seção `## 6. OPERAÇÃO E GOVERNANÇA` do `GEMINI.md`:

```markdown
### Rastreabilidade de Sessão e Aprendizados (Session-Learning)
Para registrar aprendizados da sessão e gerar relatórios de governança locais de forma autônoma:
- Destilar Aprendizados da Sessão: `python src/tools/stout_memory_capture.py --transcript <caminho_do_transcript>`
- Injetar Fatos de Sessões Anteriores no Contexto Ativo: `python src/tools/stout_memory_capture.py --inject --query "<termo_ou_projeto>"`

### Monitoramento e Analytics Centralizado (Global)
Utilize as ferramentas centrais do ecossistema global para relatórios e auditorias estratégicas.
```text

### 2. Atualizar GEMINI.md (Regras Locais)

Injete na seção `## 3. REGRAS LOCAIS`:

```markdown
### Governança CDD e Session-Learning
- **Roteamento:** Toda lógica de ativação de skills é mediada pelo `SkillRouter` em `src/router.py`.
- **Regras:** Definidas de forma declarativa em `data/config/rules.yaml`.
- **Validação:** Schemas JSON em `data/config/` garantem a integridade das configurações.
- **Rastreabilidade:** Checkpoints automáticos registrados em `.GCC/` via `GCCController`.
- **Session-Learning:** Captação de fatos, decisões e bugs locais gravada no SQLite `.stout/session_learning.db` e consolidada em `docs/governance/known_issues.md` e `docs/governance/evolution_backlog.md` via `stout_memory_capture.py`.
```text
