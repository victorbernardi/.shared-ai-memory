# Anatomia Universal de uma Skill

Referência obrigatória para o `code_drafter_agent`. Consultar antes de gerar qualquer SKILL.md.

---

## Estrutura de Diretório Padrão

```
<nome-da-skill>/
  SKILL.md           ← obrigatório — definição e instruções
  skill.config.json  ← obrigatório para skills multi-plataforma
  scripts/           ← opcional — Python, Bash, Node
  references/        ← opcional — docs, templates, critérios
  assets/            ← opcional — arquivos estáticos
  examples/          ← opcional — exemplos de uso
```

---

## Frontmatter YAML — Campos por Plataforma

O frontmatter é o bloco `---` no topo do SKILL.md. Deve ser o **primeiro conteúdo do arquivo**, sem espaço antes do `---` de abertura.

### Campos Obrigatórios (todas as plataformas)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `name` | string | Identificador único. Lowercase com hífens. Sem espaços. Ex: `stout-commit` |
| `description` | string | Determina quando a skill é ativada. Limite: 1024 chars. Iniciar com "Use quando..." |

### Campos Recomendados (Stout Ecosystem)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `version` | string | SemVer. Ex: `1.0.0` |
| `tier` | int | 1=orchestrator, 2=feature, 3=platform, 4=meta-factory |
| `category` | string | engineering, governance, meta-governance, orchestrator, design |
| `tools` | list | Plataformas suportadas (ver abaixo) |
| `author` | string | Nome do criador |
| `triggers` | list | Frases exatas que ativam a skill |

### Campo `tools` — Valores Válidos

```yaml
tools:
  - claude-code       # Claude Code CLI (~/.claude/skills/)
  - antigravity       # Antigravity CLI (~/.gemini/antigravity-cli/skills/)
  - commandcode       # CommandCode CLI (~/.commandcode/skills/)
  - gemini-cli        # Gemini CLI compartilhado (~/.gemini/skills/)
  - codex             # OpenAI Codex CLI
  - cursor            # Cursor IDE
```

### Campos Opcionais

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `tags` | list | Categorias livres para busca |
| `dependencies` | list | Skills que devem existir antes desta |
| `risk` | string | `safe`, `moderate`, `high` |
| `source` | string | `custom`, `community`, `official` |

---

## Exemplo de Frontmatter Completo

```yaml
---
name: minha-skill
version: 1.0.0
tier: 2
category: engineering
description: >
  Use quando o usuário precisar de X. Provê capacidade de Y
  em projetos Z.
tools:
  - claude-code
  - antigravity
  - commandcode
triggers:
  - fazer X
  - execute X
  - X para o projeto
author: Victor
---
```

---

## Corpo do SKILL.md

Após o frontmatter, o conteúdo é Markdown livre lido pelo agente como instrução.

**Seções recomendadas:**

1. `## Objetivo` — o que a skill faz
2. `## Fluxo` — passo a passo
3. `## Constraints` — regras NUNCA/SEMPRE/NÃO
4. `## Scripts` — lista de scripts disponíveis (se houver)
5. `## Examples` — casos simples e complexos

**Regra de tamanho:**

- Claude Code: sem limite prático — use seções ricas
- Antigravity / CommandCode: prefira SKILL.md ≤ 300 linhas; mova detalhes para `references/`
- Description no frontmatter: ≤ 1024 chars em todas as plataformas
