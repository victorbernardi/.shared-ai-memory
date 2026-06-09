# Template Engine — Sintaxe de Compilação Condicional

Referência para gerar SKILL.md multi-plataforma a partir de uma única fonte.
Baseado no `universal-skill-kit` (jiangding1990/universal-skill-kit).

---

## Diretiva `@if`

Exibe o bloco apenas nas plataformas listadas.

```markdown
<!-- @if platform=claude -->
Conteúdo exclusivo para Claude Code — pode ser longo e detalhado.
<!-- @endif -->

<!-- @if platform=antigravity -->
Conteúdo para Antigravity CLI — conciso.
<!-- @endif -->

<!-- @if platform=claude,antigravity -->
Conteúdo compartilhado por Claude e Antigravity.
<!-- @endif -->
```

**Valores válidos de platform:** `claude`, `antigravity`, `commandcode`, `gemini`, `codex`, `cursor`

---

## Diretiva `@unless`

Exibe o bloco em **todas as plataformas exceto** as listadas.

```markdown
<!-- @unless platform=codex -->
Este bloco aparece em Claude, Antigravity e CommandCode, mas NÃO no Codex.
<!-- @endunless -->
```

---

## Variáveis `{{var}}`

Substituídas na compilação com valores do `skill.config.json`.

```markdown
Esta skill se chama **{{name}}** versão **{{version}}**.
Criada por {{author}} em {{created_at}}.
```

**Variáveis disponíveis:** `name`, `version`, `author`, `tier`, `category`, `created_at`

---

## `skill.config.json` — Schema

```json
{
  "name": "nome-da-skill",
  "version": "1.0.0",
  "author": "Victor",
  "platforms": {
    "claude": {
      "enabled": true,
      "output": ".claude/skills"
    },
    "antigravity": {
      "enabled": true,
      "output": ".gemini/antigravity-cli/skills"
    },
    "commandcode": {
      "enabled": true,
      "output": ".commandcode/skills"
    }
  },
  "description": {
    "full": "Descrição completa para Claude Code — sem limite de tamanho.",
    "short": "Descrição concisa ≤ 120 chars para Antigravity e CommandCode."
  },
  "body": {
    "source": "SKILL.md",
    "sections": {
      "claude": ["all"],
      "antigravity": ["Objetivo", "Fluxo", "Constraints"],
      "commandcode": ["Objetivo", "Fluxo", "Constraints"]
    }
  }
}
```

---

## Padrão de SKILL.md Multi-plataforma (template base)

```markdown
---
name: {{name}}
version: {{version}}
description: >
  Use quando [TRIGGER]. Provê [ACAO] para [DOMINIO].
tools:
  - claude-code
  - antigravity
  - commandcode
tier: [TIER]
category: [CATEGORY]
author: {{author}}
---

# {{name}}

## Objetivo
[OBJETIVO — aparece em todas as plataformas]

<!-- @if platform=claude -->
## Fluxo Detalhado

[FLUXO COM COMANDOS, EXEMPLOS E REFERÊNCIAS]

## Exemplos

[EXEMPLOS RICOS]

## Referências
- `references/[DOC].md`
<!-- @endif -->

<!-- @if platform=antigravity,commandcode -->
## Fluxo

1. [PASSO 1]
2. [PASSO 2]
3. [PASSO 3]
<!-- @endif -->

## Constraints

- NUNCA [RESTRICAO_1]
- SEMPRE [RESTRICAO_2]
- NÃO [RESTRICAO_3]

## Scripts

- `scripts/[SCRIPT].py` — [DESCRICAO]
```

---

## Regras de Uso

1. **Sempre incluir bloco `@if platform=claude`** com conteúdo rico
2. **Sempre incluir bloco `@if platform=antigravity,commandcode`** com versão concisa
3. **Constraints e Scripts ficam fora dos blocos** — aparecem em todas as plataformas
4. **Objetivo fica fora dos blocos** — sempre visível
5. O `skill.config.json` é gerado pelo `blueprint_engine.py` — não criar manualmente
