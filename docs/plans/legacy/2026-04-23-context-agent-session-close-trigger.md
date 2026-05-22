# Context-Agent Session Close Trigger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Registrar oficialmente que a frase `encerrar sessão` aciona o `context-agent`, tanto na política global do OpenCode quanto na documentação do próprio skill.

**Architecture:** A regra vai viver em dois pontos complementares: `rules/opencode_tool_routing.md` como fonte operacional global, e `.opencode/skills/context-agent/SKILL.md` como contrato do comportamento do skill. O escopo é apenas documental e de instrução, sem alterar código de execução, parsing ou persistência.

**Tech Stack:** Markdown, OpenCode rules, skill documentation

---

## File Map

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `C:/Projetos/Stout/rules/opencode_tool_routing.md` | Modificar | Explicitar que `encerrar sessão` aciona o `context-agent` no roteamento global do OpenCode |
| `C:/Projetos/Stout/.opencode/skills/context-agent/SKILL.md` | Modificar | Registrar a mesma frase como gatilho oficial do skill de contexto |

---

## Task 1: Tornar a regra explícita no roteamento global

**Files:**
- Modify: `C:/Projetos/Stout/rules/opencode_tool_routing.md`

- [ ] **Step 1: Atualizar a seção de regras com a frase exata**

Substituir a linha atual de memória por uma forma explícita que inclua o gatilho textual:

```md
- Para salvar contexto, decisões, pendências e memória de continuidade entre sessões, usar o `context-agent`.
- A frase `encerrar sessão` aciona o `context-agent`.
```

- [ ] **Step 2: Manter o escopo separado de Antigravity**

Garantir que o cabeçalho e os guardrails continuem deixando claro que a política vale só para o OpenCode no Stout e não altera o Antigravity.

- [ ] **Step 3: Validar a redação final do arquivo**

Run:

```powershell
python -c "from pathlib import Path; text = Path(r'C:\Projetos\Stout\rules\opencode_tool_routing.md').read_text(encoding='utf-8'); print(text)"
```

Expected: o arquivo contém a frase literal `encerrar sessão` e ainda preserva o escopo do OpenCode.

---

## Task 2: Registrar o gatilho no skill de contexto

**Files:**
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/SKILL.md`

- [ ] **Step 1: Adicionar o gatilho textual na seção `When to Use This Skill`**

Inserir uma linha nova no bloco de uso para cobrir o comando explícito do usuário:

```md
- When the user says `encerrar sessão`
```

- [ ] **Step 2: Reforçar a intenção na descrição do skill**

Atualizar a descrição curta e/ou o overview para deixar claro que `encerrar sessão` é um sinônimo operacional de acionar o `context-agent` antes de fechar a conversa.

- [ ] **Step 3: Validar que o gatilho ficou documentado sem ambiguidade**

Run:

```powershell
python -c "from pathlib import Path; text = Path(r'C:\Projetos\Stout\.opencode\skills\context-agent\SKILL.md').read_text(encoding='utf-8'); print(text)"
```

Expected: o arquivo menciona `encerrar sessão` na seção de uso e não cria conflito com os gatilhos já existentes de salvar contexto.

---

## Task 3: Revisão final do contrato

**Files:**
- Verify only: `C:/Projetos/Stout/rules/opencode_tool_routing.md`
- Verify only: `C:/Projetos/Stout/.opencode/skills/context-agent/SKILL.md`

- [ ] **Step 1: Confirmar que os dois arquivos usam a mesma semântica**

Run:

```powershell
git -C "C:\Projetos\Stout" diff -- "rules/opencode_tool_routing.md" ".opencode/skills/context-agent/SKILL.md"
```

Expected: ambos os arquivos convergem para a mesma regra, sem contradição entre roteamento global e skill.

- [ ] **Step 2: Confirmar que nenhum arquivo fora do escopo foi alterado**

Run:

```powershell
git -C "C:\Projetos\Stout" diff --name-only
```

Expected: apenas `rules/opencode_tool_routing.md` e `.opencode/skills/context-agent/SKILL.md` aparecem no diff quando a implementação for executada.

---

## Self-Review

- **Spec coverage:** o plano cobre o registro da regra no roteamento global e no skill de contexto, que foi exatamente o escopo escolhido.
- **Placeholder scan:** não há `TBD`, `TODO` ou passos vagos; cada etapa aponta um arquivo e uma alteração concreta.
- **Type consistency:** os caminhos de arquivo e o gatilho textual `encerrar sessão` são consistentes em todo o plano.
