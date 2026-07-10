---
name: stout-init-icm
description: "Inicialização modular de projetos Stout com arquitetura ICM nativa. Gera workspaces de estágios numerados com contratos explícitos (CONTEXT.md), envelope fino para progressive disclosure (SKILL.md), e infraestrutura GCC. Use para criar novo projeto, scaffold ICM, inicializar workspace, ou projeto modular. Triggers: inicializar projeto icm, novo workspace, scaffold icm, projeto novo no padrao, stout-init-icm."
version: 1.0.0
author: Arquiteto Stout
tier: 3
category: meta-governance
date_added: "2026-05-27"
---

# Stout Init ICM — Scaffolding de Workspaces Nativos

## Propósito

Gerar a estrutura completa de um novo projeto no padrão ICM nativo: workspaces com estágios numerados, contratos explícitos (`CONTEXT.md`), envelope fino para progressive disclosure (`SKILL.md`), e infraestrutura GCC.

**Paralelo ao `stout-init` (CDD tradicional).** Use `stout-init` para projetos CDD legados. Use `stout-init-icm` para novos projetos ICM-nativos.

## Fluxo de Trabalho (4 Fases)

### Fase 1: Inicialização
- Confirmar diretório do projeto em `<dominio>\Projetos\<projeto>\`

**Referência:** `@references/scaffolding-protocols.md`

### Fase 2: Templates
- Gerar `SKILL.md` fino (YAML frontmatter + apontadores)
- Gerar `CONTEXT.md` do pipeline
- Gerar `CONTEXT.md` para cada estágio a partir de templates
- Criar diretórios `output/` e `scripts/`

**Referência:** `@references/templates-core.md`

### Fase 3: Infraestrutura
- Configurar `.GCC/` para o novo projeto
- Configurar `.gemini/skills/` com symlinks ou thin wrappers
- Configurar `.agents/skills/` para Antigravity

**Referência:** `@references/infra-logic.md`

### Fase 4: Validação
- Verificar estrutura de diretórios
- Verificar encoding UTF-8 em todos os arquivos
- Verificar que todos os CONTEXT.md têm as 8 seções obrigatórias
- Verificar que SKILL.md tem YAML frontmatter válido
- Registrar no `.GCC/main.md`

## Estrutura Gerada

Os estágios ICM nascem DENTRO do diretório do projeto (que já está em `<dominio>\Projetos\`):

```
<raiz>\<dominio>\Projetos\<projeto>\
├── SKILL.md                    # Envelope fino (YAML)
├── CONTEXT.md                  # Contrato do pipeline
├── 00_research/                # Cold storage — pesquisas e referências
│   ├── CONTEXT.md
│   └── references/
├── 01_<estagio>/
│   ├── CONTEXT.md              # 8 seções obrigatórias
│   ├── scripts/                # Scripts mecânicos (se aplicável)
│   └── output/                 # Artefatos do estágio
├── 02_<estagio>/
│   ├── CONTEXT.md
│   ├── scripts/
│   └── output/
└── ...
```

## Parâmetros do Scaffold

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `dominio` | Sim | `Stout` (técnico) ou `Inova` (negócio) |
| `projeto` | Sim | Nome do projeto em kebab-case |
| `estagios` | Sim | Lista de nomes de estágios (ex: `extrair`, `auditar`, `gerar`, `validar`, `exportar`) |
| `descricao` | Sim | Descrição semântica para o SKILL.md fino |
| `gate` | Não | Qual estágio é o GATE de auditoria (ex: `auditar`). Bloqueia pipeline se falhar |
| `breakpoint` | Não | Qual estágio tem breakpoint humano (default: último) |
| `tem_infra` | Não | `true` se o domínio tem REFERENCES.md e .GCC/. Default: detectar automaticamente |

## Templates

- `@templates/workspace/SKILL.md.template` — Envelope fino (domínio COM infra)
- `@templates/workspace/CONTEXT.md.template` — Contrato do pipeline
- `@templates/workspace/01_estagio/CONTEXT.md.template` — Contrato de estágio
- `@templates/workspace/00_research/CONTEXT.md.template` — Cold storage
- `@templates/gemini-icm.md` — GEMINI.md com Regras 1-9
- `@templates/references.md` — REFERENCES.md inicial

## Idioma

Obrigatório o uso de **Português (PT-BR)** para todos os artefatos de governança.

## Escopo

Esta skill se aplica à criação de novos projetos ICM-nativos no ecossistema Stout.

## Critérios de Conclusão

A skill é considerada concluída quando a estrutura de diretórios está criada, todos os arquivos template foram gerados com as 8 seções obrigatórias, e o projeto está registrado no `.GCC/main.md`.
