# Templates de Inicialização Stout (Core)

## 1. Layer 0 — CLAUDE.md (Identidade do Workspace ICM)

Template canônico em `@../_shared-icm-templates/CLAUDE.md.template`.

Copiar e personalizar: nome do projeto, domínio, lista de estágios do mapa do workspace.

**NÃO gerar** `GEMINI.md` (legado) — Layer 0 é sempre `CLAUDE.md`.

## 2. Ponteiro Codex/OpenAI — AGENTS.md

Template canônico em `@../_shared-icm-templates/AGENTS.md.template`.

Copiar sem modificação — apenas substituir `<nome-do-projeto>` no cabeçalho.

## 3. Modelo known_issues.md (Bugs Conhecidos)

```markdown
# 🐛 Lista de Bugs Conhecidos & Workarounds

Este documento registra de forma viva, imutável e estruturada todos os bugs de ambiente, bibliotecas ou travas físicas reincidentes descobertos nas sessões do ecossistema Stout, juntamente com suas soluções temporárias (workarounds) e status de correção definitiva.

---

| Bug ID | Categoria | Descrição | Ocorrências | Workaround Conhecido | Correção Definitiva | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |

---

> [!NOTE]
> Este arquivo é atualizado de forma dinâmica e programática pela skill `stout-session-learning` ao final de cada sessão.
```

## 4. Modelo evolution_backlog.md (Evolução Técnica)

```markdown
# 🚀 Backlog de Evolução Técnica & Estética

Este documento centraliza e prioriza todas as sugestões de otimização agêntica, melhorias estéticas de interface, refatorações de código e avanços na infraestrutura do ecossistema Stout sugeridos pelas habilidades a partir do aprendizado consolidado de sessões passadas.

---

## 📅 Sugestões de Melhoria e Propostas

| ID | Data | Origem (Sessão) | Proposta / Oportunidade de Melhoria | Impacto Esperado | Prioridade | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |

---

> [!NOTE]
> Novas propostas identificadas são compiladas e integradas aqui pela skill `stout-session-learning` de forma autônoma.
```
