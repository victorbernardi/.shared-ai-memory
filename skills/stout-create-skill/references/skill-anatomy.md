# Anatomia Universal de uma Skill

Referência obrigatória para o `code_drafter_agent`. Consultar antes de gerar qualquer SKILL.md.

---

## Estrutura de Diretório Padrão

```
<nome-da-skill>/
  SKILL.md           ← obrigatório — definição e instruções
  skill.platforms.yaml  ← manifesto de plataformas e extensões
  scripts/           ← opcional — Python, Bash, Node
  references/        ← opcional — docs, templates, critérios
  assets/            ← opcional — arquivos estáticos
  examples/          ← opcional — exemplos de uso
```

---

## Frontmatter YAML — Campos Universais

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
| `tier` | int | 1=utility, 2=feature, 3=platform, 4=orchestrator |
| `category` | string | engineering, governance, meta-governance, orchestrator, design |
| `author` | string | Nome do criador |

---

## Plataformas Suportadas

| Plataforma | ID | Diretório de Instalação |
|-----------|-----|------------------------|
| Codex | `codex` | `~/.agents/skills/` |
| Claude Code | `claude-code` | `~/.claude/skills/` |
| CommandCode | `commandcode` | `~/.commandcode/skills/` |

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

- Todas as plataformas: use seções ricas
- Description no frontmatter: ≤ 1024 chars
