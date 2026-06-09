# Platform Reference: Antigravity CLI

## Diretórios de Skills

```
CLI-only:  ~/.gemini/antigravity-cli/skills/<nome-da-skill>/   ← CORRETO
Shared:    ~/.gemini/skills/<nome-da-skill>/                    ← todos os produtos Antigravity
Projeto:   .agents/skills/<nome-da-skill>/
```

No ecossistema Stout (Windows), o diretório CLI é uma **junction** para:

```
%USERPROFILE%\.shared-ai-memory\skills\<nome-da-skill>\
```

> **Atenção:** O path `~/.gemini/antigravity/skills/` está **incorreto** e não funciona.
> O correto é `~/.gemini/antigravity-cli/skills/`.

---

## Frontmatter — Campos com Efeito no Antigravity

| Campo | Comportamento |
|-------|--------------|
| `description` | Trigger semântico. Limite: 1024 chars. |
| `name` | Deve coincidir com o nome da pasta. Lowercase com hífens. |

O Antigravity CLI não lê campos extras do frontmatter além de `name` e `description`. Campos como `tier`, `tools`, `triggers` são ignorados pelo runtime — servem para governança Stout apenas.

---

## Capacidades e Limitações

| Capacidade | Suporte |
|-----------|---------|
| Scripts Python/Bash | ✅ via `scripts/` |
| Jinja2 / templates `.hbs` | ✅ referenciados em scripts |
| Tool use (nativo) | ❌ não disponível como no Claude |
| MCP servers | ✅ configurados separadamente em `~/.gemini/settings.json` |
| Subagentes | ✅ via configuração de agentes |
| Invocação de outras skills | ❌ sem mecanismo nativo |

---

## Estrutura Recomendada para Antigravity

```
<nome-da-skill>/
  SKILL.md           ← conciso: objetivo + fluxo + constraints (≤ 200 linhas)
  scripts/
    main.py          ← script principal
    validate.py      ← validações
  references/
    criteria.md      ← critérios detalhados (não carregados por padrão)
```

---

## Boas Práticas para Antigravity

1. **SKILL.md conciso**: o runtime carrega o arquivo inteiro no contexto — mantenha ≤ 200 linhas
2. **Mova detalhes para `references/`**: o agente só carrega referencias quando invocado explicitamente
3. **Scripts determinísticos**: use scripts para validações binárias (pass/fail), não para raciocínio
4. **Sem Tool use direto**: instrua o agente a usar comandos shell ou scripts Python
5. **"Progressive Disclosure"**: exponha apenas metadados no SKILL.md; lógica detalhada vai em scripts

---

## Exemplo de Seção Antigravity-Only

```markdown
<!-- @if platform=antigravity -->

## Fluxo

1. Execute `python scripts/main.py --input <arquivo>`
2. Verifique o resultado em `output/report.json`
3. Se falhar: `python scripts/validate.py --fix`

<!-- @endif -->
```

---

## Instalação via skillfish

```bash
# Instala no diretório antigravity-cli
skillfish add owner/repo --output ~/.gemini/antigravity-cli/skills

# No ecossistema Stout (instala no canonical e junction distribui)
skillfish add owner/repo --output ~/.shared-ai-memory/skills
```
