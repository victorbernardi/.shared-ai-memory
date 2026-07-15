# Template Engine — Sintaxe de Compilação Condicional

Referência para gerar SKILL.md multi-plataforma a partir de uma única fonte.

---

## Estrutura de Artefatos

O manifesto `skill.platforms.yaml` declara targets e extensões:

```yaml
targets:
  - codex
  - claude-code
  - commandcode
extensions:
  - id: claude.allowed-tools
    required: false
    value:
      - Read
      - Grep
```

O renderer `platform_renderer.py` copia o fonte canônico para cada plataforma e aplica extensões registradas.

---

## Variáveis `{{var}}`

Substituídas na compilação com valores do manifesto.

```markdown
Esta skill se chama **{{name}}**.
Criada por {{author}}.
```

**Variáveis disponíveis:** `name`, `description`

---

## Plataformas Suportadas

| Plataforma | ID | Diretório de Instalação |
|-----------|-----|------------------------|
| Codex | `codex` | `~/.agents/skills/` |
| Claude Code | `claude-code` | `~/.claude/skills/` |
| CommandCode | `commandcode` | `~/.commandcode/skills/` |

---

## Padrão de SKILL.md Multi-plataforma (template base)

```markdown
---
name: {{name}}
description: Use quando [TRIGGER]. Executa [ACAO] para [DOMINIO].
---

# {{name}}

## Objetivo
[OBJETIVO — aparece em todas as plataformas]

## Fluxo

1. [PASSO 1]
2. [PASSO 2]
3. [PASSO 3]

## Constraints

- NUNCA [RESTRICAO_1]
- SEMPRE [RESTRICAO_2]
- NÃO [RESTRICAO_3]

## Scripts

- `scripts/[SCRIPT].py` — [DESCRICAO]
```

---

## Regras de Uso

1. **Frontmatter universal** — `name` e `description` são obrigatórios
2. **Constraints e Scripts ficam no corpo** — aparecem em todas as plataformas
3. **Extensões são declaradas em `skill.platforms.yaml`** — não no frontmatter
4. **O renderer aplica extensões automaticamente** — não inclua `@if` no fonte canônico
