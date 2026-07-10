# Platform Reference: Claude Code

## Diretório de Skills

```
Global:   %USERPROFILE%\.claude\skills\<nome-da-skill>\
Projeto:  .claude\skills\<nome-da-skill>\
```

No ecossistema Stout, o diretório global é uma **junction** para:

```
%USERPROFILE%\.shared-ai-memory\skills\<nome-da-skill>\
```

---

## Frontmatter — Campos Específicos Claude Code

Claude Code lê o frontmatter YAML padrão. Não há campos exclusivos, mas os seguintes têm efeito direto:

| Campo | Comportamento |
|-------|--------------|
| `description` | Usado pelo sistema de roteamento para decidir quando carregar a skill. Máximo 1024 chars. Prefixar com "Use when" ou "Use quando". |
| `name` | Identificador único. Deve coincidir com o nome da pasta. |

---

## Capacidades Exclusivas do Claude Code

### Tool Use

Skills podem referenciar e invocar tools diretamente:

```markdown
Use a ferramenta `Read` para ler o arquivo, depois `Edit` para modificar.
```

### MCP (Model Context Protocol)

Skills podem instruir o uso de servidores MCP:

```markdown
Use o MCP `context7` para buscar documentação atualizada antes de implementar.
```

### Skill Tool

Skills podem invocar outras skills:

```markdown
Invoque a skill `stout-commit` ao finalizar a implementação.
```

### Subagentes (Agent Tool)

```markdown
Dispatche um subagente com `subagent_type=Explore` para mapear o codebase.
```

---

## Limites e Comportamento

- **Tamanho do SKILL.md:** sem limite prático — Claude lê o arquivo completo
- **Memória entre sessões:** não há — use `references/` para conhecimento persistente
- **Ativação:** baseada no campo `description` + contexto da conversa
- **Ordem de busca:** projeto → global (`~/.claude/skills/`) → plugins

---

## Boas Práticas para Claude Code

1. **SKILL.md rico**: use seções completas, exemplos detalhados, diagramas em ASCII
2. **References/**: mova documentação longa para `references/*.md` e referencie no SKILL.md
3. **Constraints explícitas**: use NUNCA/SEMPRE/NÃO para regras críticas
4. **Tool mapping**: liste quais tools o agente deve usar em cada passo
5. **Anti-patterns**: inclua seção "Do Not Use When" para reduzir ativações incorretas

---

## Exemplo de Seção Claude-Only

```markdown
<!-- @if platform=claude -->

## Fluxo Detalhado

### Passo 1 — Análise
Use a tool `Read` para ler `src/` e mapear a estrutura.
Dispatche subagente `Explore` para buscas amplas.

### Passo 2 — Implementação
Siga o ciclo TDD: invoque `superpowers:test-driven-development`.

### Referências
- `references/architecture.md` — decisões arquiteturais
- `references/patterns.md` — padrões do projeto

<!-- @endif -->
```
