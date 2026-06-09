# Platform Reference: CommandCode

## Diretórios de Skills

```
Global:   ~/.commandcode/skills/<nome-da-skill>/
Projeto:  .commandcode/skills/<nome-da-skill>/
```

No ecossistema Stout (Windows), o diretório global é uma **junction** para:

```
%USERPROFILE%\.shared-ai-memory\skills\<nome-da-skill>\
```

---

## Frontmatter — Campos com Efeito no CommandCode

| Campo | Comportamento |
|-------|--------------|
| `name` | Obrigatório. Lowercase com hífens. Coincide com nome da pasta. |
| `description` | Obrigatório. Determina quando a skill é ativada. Prefixar com "Use when" ou "Use quando". Limite: 1024 chars. |
| `version` | Opcional mas recomendado. SemVer. |
| `author` | Opcional. |
| `tags` | Opcional. Lista para categorização. |
| `agents` | Opcional. Lista de agentes compatíveis (ex: `["commandcode", "claude"]`). |

---

## Capacidades e Limitações

| Capacidade | Suporte |
|-----------|---------|
| Scripts Python/Bash/Node | ✅ via `scripts/` |
| Frontmatter YAML | ✅ padrão completo |
| Tool use nativo | ❌ depende da implementação do agente |
| MCP servers | ✅ via configuração separada |
| Invocação de outras skills | ❌ sem mecanismo nativo |

---

## Estrutura Recomendada para CommandCode

```
<nome-da-skill>/
  SKILL.md           ← frontmatter + instruções claras
  scripts/           ← scripts auxiliares (opcional)
  templates/         ← templates reutilizáveis (opcional)
  resources/         ← documentação de suporte (opcional)
```

---

## Boas Práticas para CommandCode

1. **`description` preciso**: é o mecanismo primário de ativação — use linguagem próxima ao que o usuário digita
2. **Triggers explícitos**: inclua variações de português e inglês no `description` ou em campo `triggers`
3. **Passos numerados**: CommandCode responde bem a fluxos em lista numerada clara
4. **Scripts opcionais mas recomendados**: separe lógica de validação em `scripts/` para reutilização
5. **Sem complexidade no SKILL.md**: instruções simples e diretas; complexidade vai em `references/`

---

## Exemplo de Seção CommandCode-Only

```markdown
<!-- @if platform=commandcode -->

## Fluxo

1. Identifique o objetivo: `<descreva em uma linha>`
2. Execute `scripts/run.py --mode <modo>`
3. Valide o resultado antes de prosseguir
4. Registre o output em `output/<data>-resultado.md`

<!-- @endif -->
```

---

## Instalação via skillfish

```bash
# Instala diretamente no CommandCode
skillfish add owner/repo --output ~/.commandcode/skills

# No ecossistema Stout (instala no canonical e junction distribui)
skillfish add owner/repo --output ~/.shared-ai-memory/skills
```

---

## Diferenças em Relação ao Claude Code

| Aspecto | Claude Code | CommandCode |
|---------|-------------|-------------|
| Tool use nativo | ✅ (Read, Edit, Bash, Agent...) | ❌ via scripts |
| Tamanho do SKILL.md | Sem limite | Prefira ≤ 150 linhas |
| MCP | ✅ nativo | ✅ via config |
| Ativação | description + contexto | description (match direto) |
