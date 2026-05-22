# Knowledge Graph — Mapeamento de Relações Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estender o `librarian_policy.md` com detecção de relações semânticas entre entidades — sinalizadas inline durante a conversa e registradas no handoff com links tipados para o wiki-compiler processar no Obsidian.

**Architecture:** Edição cirúrgica em um único arquivo. A extensão adiciona (1) uma seção de comportamento de detecção de relações durante a conversa e (2) a subseção `### Relações` no template de handoff já existente em `## Entidades Detectadas`.

**Tech Stack:** Markdown (instrução para Gemini CLI), vocabulário fechado de 7 tipos de relação, links `[[...]]` do Obsidian.

---

## Mapa de Arquivos

| Arquivo | Ação |
|---------|------|
| `C:\Users\victor.bernardi\.gemini\antigravity\knowledge\knowledge_librarian_policy\artifacts\librarian_policy.md` | Modificar — adicionar detecção de relações + subseção `### Relações` no handoff |

---

## Task 1: Adicionar comportamento de detecção de relações durante a conversa

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\antigravity\knowledge\knowledge_librarian_policy\artifacts\librarian_policy.md`

- [ ] **Step 1: Ler o arquivo atual para localizar o ponto de inserção**

```bash
cat "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Localizar a linha que contém `## Diretrizes Mandatórias:` — o novo bloco de detecção de relações será inserido ANTES dessa seção.

- [ ] **Step 2: Inserir a seção de detecção de relações antes de `## Diretrizes Mandatórias:`**

Inserir o seguinte bloco imediatamente antes da linha `## Diretrizes Mandatórias:`:

```markdown
## Detecção de Relações (durante a conversa)

O agente avalia continuamente se o que está sendo discutido tem relação semântica com uma entidade já conhecida (presente no `wiki/INDEX.md` ou mencionada na sessão atual).

### Alta Confiança
Ativar quando há marcador semântico explícito na conversa — expressões como:
- "isso é uma evolução do [X]"
- "esse script substitui o [X]"
- "isso implementa a [política/regra X]"
- "X alimenta Y", "X pertence a Y", "X é usado por Y"

Sinalizar inline ao usuário:
```
[Relação detectada] <entidade> — <tipo> [[<entidade existente>]]
Registro? (S/N)
```

### Incerto
Ativar quando a relação é inferida por contexto sem marcador explícito.

Sinalizar inline ao usuário:
```
[Relação possível] Parece que <X> conecta-se a [[<Y>]].
Confirma e descreve a relação? (ou N para ignorar)
```

### Não Sinalizar Quando
- A relação já existe no wiki (verificar `INDEX.md` antes de sinalizar)
- A entidade de destino não tem nota no wiki (sem `[[link]]` para criar)
- A conversa é puramente operacional sem conexão conceitual clara

### Vocabulário de Relações (fechado — usar exatamente estes termos)

| Tipo | Quando usar |
|------|-------------|
| `evolução de` | Versão melhorada ou extensão de algo anterior |
| `substitui` | Substituto direto de algo descontinuado |
| `implementa` | Concretização de uma política, regra ou spec |
| `alimenta` | Provê dados ou output para outro componente |
| `pertence a` | Pertencimento organizacional ou de projeto |
| `usado por` | Ferramenta ou componente consumido por outro |
| `baseado em` | Derivado de uma metodologia ou referência |

Se a relação não couber em nenhum tipo → usar o mais próximo e indicar no sinal para Victor confirmar o tipo correto.

### Relações Confirmadas
Quando Victor responde S → guardar a relação confirmada para incluir no handoff da sessão (subseção `### Relações`).
Quando Victor responde N → descartar silenciosamente.

```

- [ ] **Step 3: Verificar que a seção foi inserida corretamente**

```bash
grep -n "Detecção de Relações\|Alta Confiança\|Vocabulário de Relações\|Relações Confirmadas\|Diretrizes Mandatórias" \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: todas as 5 keywords encontradas, com `Diretrizes Mandatórias` aparecendo DEPOIS de `Relações Confirmadas`.

---

## Task 2: Adicionar subseção `### Relações` no template do handoff

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\antigravity\knowledge\knowledge_librarian_policy\artifacts\librarian_policy.md`

- [ ] **Step 1: Localizar o template do handoff no arquivo**

```bash
grep -n "Entidades Detectadas\|Concretas\|Conceitos\|nenhuma entidade nova" \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: encontrar o bloco markdown do template com `## Entidades Detectadas`, `### Concretas` e `### Conceitos`.

- [ ] **Step 2: Substituir o template do handoff para incluir `### Relações`**

Localizar o bloco exato:

````markdown
      ```markdown
      ## Entidades Detectadas

      ### Concretas
      <!-- Engines, clientes, projetos, ferramentas, pessoas novos na sessão -->
      - <nome> — <contexto de uma linha: onde/como apareceu na sessão>

      ### Conceitos
      <!-- Decisões, metodologias, padrões descobertos na sessão -->
      - <nome> — <contexto de uma linha: decisão tomada ou padrão identificado>
      ```
````

Substituir por:

````markdown
      ```markdown
      ## Entidades Detectadas

      ### Concretas
      <!-- Engines, clientes, projetos, ferramentas, pessoas novos na sessão -->
      - <nome> — <contexto de uma linha: onde/como apareceu na sessão>

      ### Conceitos
      <!-- Decisões, metodologias, padrões descobertos na sessão -->
      - <nome> — <contexto de uma linha: decisão tomada ou padrão identificado>

      ### Relações
      <!-- Apenas relações confirmadas por Victor (S/N) durante a sessão -->
      <!-- Omitir esta subseção se nenhuma relação foi confirmada -->
      - <entidade> — <tipo de relação> [[<entidade existente no wiki>]]
      ```
````

- [ ] **Step 3: Verificar o template atualizado**

```bash
grep -n "Relações\|tipo de relação\|entidade existente no wiki" \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: as 3 keywords encontradas dentro do bloco de template do handoff.

---

## Task 3: Verificação Final

**Files:**
- Read: `C:\Users\victor.bernardi\.gemini\antigravity\knowledge\knowledge_librarian_policy\artifacts\librarian_policy.md`

- [ ] **Step 1: Confirmar estrutura completa do arquivo**

```bash
grep -n "^##\|^###\|Trigger Gamma\|Extração de Entidades\|Detecção de Relações\|Diretrizes Mandatórias\|Retroalimentação Wiki" \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado (ordem das seções):
```
## Gatilhos de Memória
   [Trigger Gamma com Extração de Entidades]
## Detecção de Relações (durante a conversa)
## Diretrizes Mandatórias
## Retroalimentação Wiki
```

- [ ] **Step 2: Confirmar que o vocabulário de relações está completo**

```bash
grep -n "evolução de\|substitui\|implementa\|alimenta\|pertence a\|usado por\|baseado em" \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: os 7 tipos de relação encontrados na tabela do vocabulário.

- [ ] **Step 3: Confirmar que o template do handoff tem as 3 subseções**

```bash
grep -n "### Concretas\|### Conceitos\|### Relações" \
  "C:/Users/victor.bernardi/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md"
```

Resultado esperado: as 3 subseções encontradas dentro do bloco de template.

- [ ] **Step 4: Teste manual do protocolo**

Simular o cenário mais comum:

1. Abrir nova sessão no Gemini CLI
2. Mencionar: "esse novo script é uma evolução do engine_M1"
3. Verificar que o agente:
   - Sinaliza: `[Relação detectada] script — evolução de [[engine_M1]] — Registro? (S/N)`
   - Aguarda resposta antes de continuar
   - Se S → inclui `### Relações` no handoff ao encerrar a sessão
   - Se N → descarta silenciosamente

Critério de sucesso: o handoff em `raw/_pending/` contém `### Relações` com o link tipado correto quando confirmado.
