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

### 4. Copiar Ferramentas de Analytics e Self-Healing
Copie os arquivos de `addons/cdd/templates/tools/*` para `src/tools/` no projeto de destino.
- `gcc_analytics.py`
- `sentinel_agent.py`

## Stitching

### 1. Atualizar GEMINI.md (Operação)
Injete o seguinte bloco na seção `## 6. OPERAÇÃO E GOVERNANÇA` do `GEMINI.md`:

```markdown
### Monitoramento e Analytics
Para extrair métricas de performance e visualizar ativações em tempo real:
- Relatório Tático: `python src/tools/gcc_analytics.py`

### Otimização Autônoma (Self-Healing)
Para auditar o sistema e receber sugestões de novas regras de negócio:
- Auditoria Sentinela: `python src/tools/sentinel_agent.py`
```

### 2. Atualizar GEMINI.md (Regras Locais)
Injete na seção `## 3. REGRAS LOCAIS`:

```markdown
### Governança CDD (Configuration-Driven Development)
- **Roteamento:** Toda lógica de ativação de skills é mediada pelo `SkillRouter` em `src/router.py`.
- **Regras:** Definidas de forma declarativa em `data/config/rules.yaml`.
- **Validação:** Schemas JSON em `data/config/` garantem a integridade das configurações.
- **Rastreabilidade:** Checkpoints automáticos registrados em `.GCC/` via `GCCController`.
- **Auto-Otimização:** Agente Sentinela monitora lacunas de intenção e falhas.
```
