# Especificação Técnica: CDD Skill Alignment & Local Orchestrator

**Data:** 2026-05-15
**Status:** Proposta (Fase de Design)
**Versão:** 1.0
**Autor:** Gemini CLI Builder

## 1. Objetivo

Alinhar a arquitetura de Agent Skills ao padrão **Configuration-Driven Development (CDD)**, movendo a lógica de negócio, metadados e parâmetros das habilidades para arquivos de configuração centralizados (`data/config/`), desacoplando a intenção da execução.

## 2. Requisitos Funcionais

### FR-001: Catálogo Central de Skills (`skills_catalog.yaml`)

- O sistema deve manter um catálogo YAML contendo a "alma" de cada skill local.
- Cada entrada deve seguir estritamente o `data/config/skills.schema.json`.
- Deve conter: `id`, `name`, `description`, `level` (Tier), `instruction_template` e `resources`.

### FR-002: Orquestrador Local de CDD (`stout-cdd-orchestrator`)

- Criação de uma Agent Skill local que substitui o launcher global dentro deste workspace.
- **Responsabilidade:** Carregar o `skills_catalog.yaml`, validar contra o schema e injetar as instruções dinâmicas na sessão do agente.

### FR-003: Scripts de Execução Opacos (Level 3)

- Os scripts Python dentro das pastas de skill (`scripts/*.py`) NÃO devem conter regras de negócio hardcoded.
- Eles devem ler os parâmetros de execução a partir do `src/config.py` ou do catálogo CDD injetado.

### FR-004: Validação Rigorosa (Fail-Fast)

- Qualquer tentativa de ativar uma skill cujo registro no catálogo CDD esteja inválido (conforme o schema) deve ser bloqueada pelo `stout-immunity-gate`.

## 3. Arquitetura Proposta

### Camadas de Dados:

1. **Schema:** `data/config/skills.schema.json` (O Contrato).
2. **Catálogo:** `data/config/skills_catalog.yaml` (A Inteligência).

### Camada de Execução:

1. **Executor:** `skills/stout-cdd-orchestrator/scripts/launcher.py`.
2. **Interface:** `skills/stout-cdd-orchestrator/SKILL.md` (Interface mínima de ativação).

## 4. Matriz de Rastreabilidade

| ID | Descrição | Implementa (Plano Executivo) |
| :--- | :--- | :--- |
| FR-001 | Catálogo Central | KPI 6.4 (Redução de Retrabalho via Centralização) |
| FR-002 | Orquestrador CDD | Valor 1 (Soberania de Dados/Config) |
| FR-003 | Scripts Opacos | Valor 5 (Simplicidade Radical - Código desacoplado) |
| FR-004 | Validação Fail-Fast | Valor 7 (Confiabilidade Radical) |

## 5. Plano de Validação (TDD)

- **T-001:** Validar se o carregamento de uma skill via catálogo YAML injeta o `instruction_template` correto na memória.
- **T-002:** Validar se a modificação de um parâmetro no YAML altera o comportamento da skill sem mudar o arquivo `.py`.
- **T-003:** Validar se o `stout-immunity-gate` bloqueia a execução caso o `skills_catalog.yaml` seja corrompido propositalmente.

## 6. Log de Decisões

- **Decisão:** Criar um orquestrador local em vez de modificar o global.
- **Motivo:** Manter a integridade do ecossistema e permitir experimentação segura (Sandboxing) no projeto CDD.
- **Decisão:** Uso do formato YAML para o catálogo.
- **Motivo:** Legibilidade para humanos e suporte nativo a multi-line strings para templates de instrução.
