# Knowledge Graph → Obsidian Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estender o Trigger Gamma do `librarian_policy.md` para extrair automaticamente entidades e conceitos da sessão e incluí-los no handoff existente de `raw/_pending/`.

**Architecture:** Edição cirúrgica em um único arquivo markdown. O Trigger Gamma já escreve handoffs em `raw/_pending/` e dispara o wiki-compiler — a extensão adiciona uma seção `## Entidades Detectadas` ao handoff quando a sessão produzir entidades novas (verificadas contra `wiki/INDEX.md`).

**Tech Stack:** Markdown (instrução para Gemini CLI), leitura de `wiki/INDEX.md` para deduplicação.

---

## Mapa de Arquivos

| Arquivo | Ação |
|---------|------|
| `C:\Users\victor.bernardi\.gemini\antigravity\knowledge\knowledge_librarian_policy\artifacts\librarian_policy.md` | Modificar — estender Trigger Gamma |

---

## Task 1: Estender Trigger Gamma com extração de entidades

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\antigravity\knowledge\knowledge_librarian_policy\artifacts\librarian_policy.md`

- [ ] **Step 1: Ler o arquivo atual para confirmar a estrutura do Trigger Gamma**

```bash
cat "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: seção `## Gatilhos de Memória (Memory Hooks):` com item `1. **Trigger Gamma (Handoff de Sessão):**` contendo sub-itens a, b, c.

- [ ] **Step 2: Substituir o item 1a do Trigger Gamma pelo conteúdo estendido**

Localizar este trecho exato:

```markdown
   a. Se a sessão contiver decisões arquiteturais, mudanças de nomenclatura ou contexto técnico relevante para projetos ativos: escrever um arquivo de handoff em `C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/raw/_pending/` com o nome `YYYY-MM-DD-HH-MM-handoff-<tema-da-sessao>.md`. O handoff deve conter: decisões tomadas, mudanças de código ou nomenclatura, e contexto arquitetural novo. Este passo é **opcional** — apenas quando houver conteúdo que enriqueceria a wiki.
```

Substituir por:

```markdown
   a. Se a sessão contiver decisões arquiteturais, mudanças de nomenclatura, contexto técnico relevante para projetos ativos, **ou entidades/conceitos novos** (ver taxonomia abaixo): escrever um arquivo de handoff em `C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/raw/_pending/` com o nome `YYYY-MM-DD-HH-MM-handoff-<tema-da-sessao>.md`. O handoff deve conter: decisões tomadas, mudanças de código ou nomenclatura, e contexto arquitetural novo. Este passo é **opcional** — apenas quando houver conteúdo que enriqueceria a wiki.

      **Extração de Entidades (quando aplicável):** Após redigir o corpo do handoff, verificar se a sessão produziu entidades ou conceitos novos:

      1. Ler `C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/INDEX.md`
      2. Para cada entidade ou conceito identificado na sessão, verificar se já existe nota correspondente no INDEX.md
         - Já existe → omitir (não duplicar)
         - Não existe → incluir na seção abaixo
      3. Se houver ao menos um item novo, adicionar ao final do handoff:

      ```markdown
      ## Entidades Detectadas

      ### Concretas
      <!-- Engines, clientes, projetos, ferramentas, pessoas novos na sessão -->
      - <nome> — <contexto de uma linha: onde/como apareceu na sessão>

      ### Conceitos
      <!-- Decisões, metodologias, padrões descobertos na sessão -->
      - <nome> — <contexto de uma linha: decisão tomada ou padrão identificado>
      ```

      4. Se INDEX.md não estiver acessível → listar entidades sem verificação e adicionar ao handoff: `(deduplicação não verificada — INDEX.md inacessível)`
      5. Se nenhuma entidade nova for detectada → omitir a seção inteiramente

      **Taxonomia — O que conta como entidade:**
      - **Concretas:** engines por nome (engine_M0 a engine_M4 e variantes), clientes ou empresas pelo nome, projetos ativos (Inova, Stout, Obsidian, novos projetos em `C:\Projetos\`), ferramentas com contexto específico (n8n, wiki-compiler, Antigravity, pandas), pessoas além do Victor
      - **Conceitos:** decisões arquiteturais tomadas na sessão, metodologias discutidas ou validadas, padrões descobertos ou nomeados, problemas recorrentes com causa raiz identificada
      - **Não entra:** comentários casuais sem impacto técnico, ferramentas genéricas sem contexto (Python, bash, git), entidades já indexadas no wiki
```

- [ ] **Step 3: Verificar que os sub-itens b e c do Trigger Gamma permanecem inalterados**

```bash
grep -n "Após gravar o handoff\|NÃO.*escrever diretamente" \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: ambas as linhas encontradas — confirma que b e c não foram alterados.

- [ ] **Step 4: Verificar que a taxonomia está presente no arquivo**

```bash
grep -n "Taxonomia\|Concretas\|Conceitos\|engine_M0\|deduplicação não verificada" \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: todas as 5 keywords encontradas — confirma que o conteúdo foi inserido corretamente.

- [ ] **Step 5: Verificar a estrutura completa do arquivo**

```bash
grep -n "^##\|^###\|^1\.\|^2\." \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: seções originais preservadas (`## Gatilhos de Memória`, `## Diretrizes Mandatórias`, `## Retroalimentação Wiki`) + nova taxonomia dentro do item 1a.

---

## Task 2: Verificação Final

- [ ] **Step 1: Confirmar que o arquivo modificado é válido**

```bash
cat "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: arquivo completo com o Trigger Gamma estendido e todas as seções originais intactas.

- [ ] **Step 2: Teste manual do protocolo**

Simular o cenário mais comum:

1. Abrir nova sessão no Gemini CLI
2. Conduzir uma conversa que mencione uma engine (ex: `engine_M2`) e uma decisão arquitetural
3. Ao encerrar a sessão, verificar que o agente:
   - Lê `wiki/INDEX.md` antes de listar entidades
   - Inclui `## Entidades Detectadas` no handoff apenas se houver itens novos
   - Omite a seção quando todas as entidades já estão indexadas

Critério de sucesso: o handoff em `raw/_pending/` contém a seção de entidades corretamente preenchida — sem duplicatas, com contexto de uma linha por item.
