# Design: Knowledge Graph — Mapeamento de Relações

**Data:** 2026-04-17  
**Escopo:** Extensão do `librarian_policy.md` — camada de relacionamento semântico sobre a extração de entidades já implementada  
**Dependência:** Extração de entidades (Trigger Gamma estendido) já ativa em `librarian_policy.md`

---

## Objetivo

Adicionar ao Bibliotecário Autônomo a capacidade de detectar e registrar **relações entre entidades** — não apenas listar entidades isoladas, mas mapear como elas se conectam. As relações confirmadas por Victor são registradas no handoff com links tipados inline (`evolução de [[X]]`), que o wiki-compiler processa e insere nas notas do Obsidian.

---

## Arquitetura

**Componente único:** extensão cirúrgica de `librarian_policy.md` com dois acréscimos:

1. **Nova seção de comportamento durante a conversa** — define quando e como sinalizar relações detectadas
2. **Nova subseção `### Relações`** no template do handoff — registra relações confirmadas junto com as entidades

---

## Comportamento Durante a Conversa

O agente avalia continuamente se o que está sendo discutido tem relação com uma entidade já conhecida (no wiki ou mencionada na sessão).

### Alta Confiança
Ativado quando há marcador semântico explícito na conversa:
- "isso é uma evolução do Motor M1"
- "esse script substitui o engine_M0"
- "o Antigravity Hooks implementa a mandatory_standby_policy"

Sinal inline ao usuário:
```
[Relação detectada] <entidade nova> — <tipo> [[<entidade existente>]]
Registro? (S/N)
```

### Incerto
Ativado quando a relação é inferida por contexto sem marcador explícito.

Sinal inline ao usuário:
```
[Relação possível] Parece que <X> conecta-se a [[<Y>]].
Confirma e descreve a relação? (ou N para ignorar)
```

### Não Sinalizar Quando
- A relação já existe no wiki (verificar INDEX.md)
- A entidade relacionada não tem nota no wiki (sem `[[link]]` para criar)
- A conversa é puramente operacional sem conexão conceitual clara

---

## Vocabulário de Relações (fechado)

| Tipo | Uso |
|------|-----|
| `evolução de` | Versão melhorada ou extensão de algo anterior |
| `substitui` | Substituto direto de algo descontinuado |
| `implementa` | Concretização de uma política, regra ou spec |
| `alimenta` | Provê dados ou output para outro componente |
| `pertence a` | Pertencimento organizacional ou de projeto |
| `usado por` | Ferramenta ou componente consumido por outro |
| `baseado em` | Derivado de uma metodologia ou referência |

Se a relação não couber em nenhum tipo → usar o mais próximo e indicar no sinal para Victor confirmar.

---

## Formato no Handoff

A subseção `### Relações` é adicionada dentro de `## Entidades Detectadas`, após `### Conceitos`:

```markdown
## Entidades Detectadas

### Concretas
- <nome> — <contexto de uma linha>

### Conceitos
- <nome> — <contexto de uma linha>

### Relações
- <entidade nova> — <tipo de relação> [[<entidade existente>]]
- <entidade nova> — <tipo de relação> [[<entidade existente>]]
```

Exemplos reais:
```markdown
### Relações
- Script de Varredura — evolução de [[engine_M1]]
- Antigravity Hooks — implementa [[mandatory_standby_policy]]
- wiki-compiler — usado por [[Projeto Stout]]
```

**Regras:**
- Apenas relações confirmadas por Victor (S/N durante a sessão) são registradas
- Se nenhuma relação foi confirmada → omitir a subseção inteiramente
- Uma linha por relação, sempre com link `[[...]]` para a entidade de destino

---

## Arquivo Afetado

| Arquivo | Ação |
|---------|------|
| `C:\Users\victor.bernardi\.gemini\antigravity\knowledge\knowledge_librarian_policy\artifacts\librarian_policy.md` | Editar — adicionar comportamento de detecção de relações + subseção `### Relações` no template do handoff |

---

## Critérios de Sucesso

- O agente sinaliza relações inline durante a conversa sem interromper o fluxo
- Apenas relações com alta confiança ou confirmadas explicitamente são registradas
- O handoff inclui `### Relações` quando há relações confirmadas
- O wiki-compiler processa os links `[[...]]` e cria/atualiza as notas no Obsidian
- Relações já existentes no wiki não são sinalizadas novamente (sem ruído)
