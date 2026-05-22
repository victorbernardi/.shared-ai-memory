# 📑 Especificação Técnica: stout-skill-registry (Tier 3 Ledger)

> **Status:** Aprovado (Brainstorming Concluído)
> **Data:** 2026-05-15
> **Versão:** 1.0.0

---

## 1. Objetivo
O `stout-skill-registry` é a fonte única de verdade (Ledger) do Ecossistema de Elite Stout. Seu objetivo é armazenar metadados de todas as habilidades criadas, evitando ambiguidades e mantendo um histórico claro de versionamento, status (ativo, depreciado) e dependências entre skills (Impacto).

## 2. Requisitos

### 2.1 Funcionais (RF)
- **RF01 (Registro Único):** O sistema deve registrar novas skills em um arquivo central `registry.json` garantindo que o campo `role` seja único em todo o ecossistema.
- **RF02 (Consulta e Impacto):** Permitir a busca de skills por nome, categoria ou triggers, e identificar dependências ("quais skills dependem desta?") para análise de impacto antes de modificações.
- **RF03 (Depreciação com Histórico):** Em vez de excluir uma skill do registro, o sistema deve alterar seu status para `deprecated`, exigindo uma justificativa (`reason`) que será preservada no histórico.
- **RF04 (Integração com Criação):** Deve ser consumido (chamado) de forma automatizada pelo fim do fluxo de manufatura da `stout-create-skill`, condicionado à aprovação explícita (HITL) do usuário.
- **RF05 (Validação de Esquema):** Toda inserção ou alteração no `registry.json` deve ser validada contra um JSON Schema (`schemas/skill_entry.schema.json`).

### 2.2 Não-Funcionais (RNF)
- **RNF01 (Idempotência/Imutabilidade):** Modificações devem atualizar o campo `version` e preservar o histórico; o ledger em si nunca deve perder dados.
- **RNF02 (Baixo Acoplamento):** É um banco de dados de metadados simples operado por scripts `.py`; não executa lógica complexa de IA diretamente.
- **RNF03 (Formato Legível):** O arquivo `registry.json` deve ser mantido com formatação amigável (indentação de 2 espaços e suporte a UTF-8) para inspeção manual.
- **RNF04 (Idioma):** Comentários, documentação (`SKILL.md`) e mensagens do sistema primariamente em Português (PT-BR).

## 3. Arquitetura do Ledger

### 3.1 Estrutura da Skill
```text
skills/stout-skill-registry/
├── SKILL.md                  # Governança e manual da skill
├── registry.json             # O Ledger principal de metadados
├── schemas/
│   └── skill_entry.schema.json # JSON Schema para a entrada de skills
├── scripts/
│   ├── register_skill.py     # Lógica de inserção e bump de versão
│   ├── query_registry.py     # Consulta de skills e árvore de impacto
│   └── deregister_skill.py   # Lógica de marcação como deprecated
└── references/
    └── versioning_guide.md   # Regras de SemVer para as skills
```

### 3.2 Esquema Base de Dados (`skill_entry.schema.json`)
A entrada para uma skill incluirá, no mínimo:
- `name`: Identificador único no formato `stout-kebab-case`.
- `path`: Caminho no sistema de arquivos.
- `tier`: 1 (Utility), 2 (Feature), 3 (Platform) ou 4 (Orchestrator).
- `category`: Classificação geral.
- `role`: Descrição do papel único no ecossistema (usado para checar ambiguidades).
- `triggers`: Array de strings que disparam a skill.
- `dependencies`: Array de nomes de skills das quais esta depende (crucial para o RF02 - Impacto).
- `version`: Versionamento SemVer (MAJOR.MINOR.PATCH).
- `status`: `active`, `beta`, ou `deprecated`.
- `created_at`, `updated_at`: Datas de gestão.
- `author`: Padrão "Victor".

## 4. Integração

A integração principal ocorrerá com a `stout-create-skill` e o `stout-skill-auditor`.
1.  **Auditor:** Lê ativamente o `registry.json` via `query_registry.py` antes de aprovar a criação de uma skill.
2.  **Factory (stout-create-skill):** Executa o `register_skill.py` após o sucesso do Quality Gate para materializar a nova skill no ecossistema.

## 5. Validação (Critérios de Aceite)
- [ ] Schema bloqueia registros com papéis ou nomes duplicados se a versão não for modificada.
- [ ] Script `deregister_skill.py` não exclui o objeto JSON, mas o move/modifica para `status: "deprecated"`.
- [ ] O comando de query por impacto (`query_registry.py --impact <nome>`) retorna corretamente skills filhas.

---
*Assinado: Arquiteto Stout Inova*