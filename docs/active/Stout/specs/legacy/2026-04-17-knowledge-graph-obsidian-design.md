# Design: Knowledge Graph → Obsidian — Extração de Entidades via Trigger Gamma

**Data:** 2026-04-17  
**Escopo:** Extensão do Trigger Gamma no `librarian_policy.md` — sem nova infraestrutura  
**Dependência:** Trigger Gamma já ativo em `knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md`

---

## Objetivo

Enriquecer o handoff de sessão existente com uma seção estruturada de entidades detectadas — entidades concretas (engines, clientes, projetos, ferramentas) e conceitos tácitos (decisões, metodologias, padrões) — para que o wiki-compiler processe e crie notas no Obsidian automaticamente.

Invisível quando não há entidades novas. Automático quando há.

---

## Arquitetura

**Componente único:** extensão cirúrgica do Trigger Gamma em `librarian_policy.md`.

O Trigger Gamma já:
- Detecta conteúdo relevante ao final de cada sessão
- Escreve handoff em `raw/_pending/`
- Dispara o wiki-compiler em background

A extensão adiciona uma seção obrigatória `## Entidades Detectadas` ao handoff quando a sessão produziu entidades ou conceitos novos.

**Sem novos arquivos. Sem nova skill. Sem nova infraestrutura.**

---

## Taxonomia de Entidades

### Concretas
Referências a objetos reais do ecossistema do Victor:
- Engines por nome: `engine_M0` a `engine_M4` e variantes
- Clientes ou empresas mencionados pelo nome
- Projetos ativos: Inova, Stout, Obsidian, novos projetos em `C:\Projetos\`
- Ferramentas e bibliotecas com contexto específico: n8n, wiki-compiler, Antigravity, pandas, etc.
- Pessoas além do Victor (stakeholders, times)

### Conceitos
Conhecimento tácito produzido na sessão:
- Decisões arquiteturais tomadas ("decidimos usar X ao invés de Y")
- Metodologias discutidas ou validadas
- Padrões descobertos ou nomeados
- Problemas recorrentes identificados com causa raiz

### Não entra
- Comentários casuais sem impacto técnico
- Entidades que já têm nota no `wiki/INDEX.md` (deduplicação)
- Ferramentas genéricas sem contexto específico: Python, bash, git

---

## Formato da Seção no Handoff

```markdown
## Entidades Detectadas

### Concretas
<!-- Engines, clientes, projetos, ferramentas, pessoas mencionados na sessão -->
- engine_M2 — mencionada no contexto de auditoria de outliers
- Cliente XYZ — novo cliente citado pela primeira vez

### Conceitos
<!-- Decisões, metodologias, padrões descobertos na sessão -->
- Abordagem de deduplicação via hash — discutida como alternativa ao JOIN duplo
- Padrão de rollback com .stable.* — implementado e validado
```

Cada item: `- <nome> — <contexto de uma linha de onde/como apareceu na sessão>`

---

## Regras de Deduplicação

1. Antes de listar qualquer entidade, ler `C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/INDEX.md`
2. Se a entidade já tem nota correspondente no índice → omitir da lista
3. Se a entidade é nova → incluir com linha de contexto
4. Se o índice não estiver acessível → listar entidades sem verificação e indicar no handoff: `(deduplicação não verificada — INDEX.md inacessível)`

---

## Quando Ativar e Quando Omitir

**Ativar** (adicionar seção ao handoff) quando a sessão produziu:
- Pelo menos uma entidade concreta nova (não presente no INDEX.md)
- Pelo menos um conceito com impacto arquitetural ou metodológico

**Omitir** (não adicionar seção) quando:
- Sessão foi puramente operacional sem entidades novas
- Todas as entidades detectadas já existem no wiki
- Sessão não produziu handoff (conteúdo insuficiente para Trigger Gamma)

---

## Arquivo Afetado

| Arquivo | Ação |
|---------|------|
| `C:\Users\victor.bernardi\.gemini\antigravity\knowledge\knowledge_librarian_policy\artifacts\librarian_policy.md` | Editar — estender Trigger Gamma com seção de entidades |

---

## Critérios de Sucesso

- Handoffs com entidades novas incluem a seção `## Entidades Detectadas`
- Nenhuma entidade já indexada no wiki é listada (deduplicação ativa)
- O wiki-compiler processa a seção e cria notas sem intervenção manual
- Sessões sem entidades novas não geram seção desnecessária (zero ruído)
