# OpenCode Global Tool Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configurar o OpenCode do Stout para usar Tavily como busca web padrão, Context7 para documentação técnica e `context-agent` como referência global de memória, sem afetar o Antigravity.

**Architecture:** A implementação centraliza a política de roteamento em um arquivo de instrução global novo, referenciado por `C:/Projetos/Stout/.opencode/opencode.json`. O mesmo `opencode.json` também recebe a configuração do MCP `tavily-search`, mantendo `context7` já existente e usando variável de ambiente para a credencial.

**Tech Stack:** JSON, Markdown, OpenCode config, MCP servers

---

## File Map

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `C:/Projetos/Stout/.opencode/opencode.json` | Modificar | Registrar `tavily-search` no bloco `mcp` e incluir a instrução global nas `instructions` |
| `C:/Projetos/Stout/rules/opencode_tool_routing.md` | Criar | Definir a política global de roteamento de ferramentas do OpenCode |

---

## Task 1: Criar a política global do OpenCode

**Files:**
- Create: `C:/Projetos/Stout/rules/opencode_tool_routing.md`

- [ ] **Step 1: Escrever o arquivo de política global**

Criar `C:/Projetos/Stout/rules/opencode_tool_routing.md` com este conteúdo:

```md
# OpenCode Tool Routing

Escopo: esta política vale para o OpenCode rodando no Stout. Não altera o Antigravity.

## Regras

- Para pesquisa aberta na web, usar prioritariamente o MCP `tavily-search`.
- Para documentação técnica, APIs, SDKs e referências oficiais, usar prioritariamente o MCP `context7`.
- Para salvar contexto, decisões, pendências e memória de continuidade entre sessões, usar o `context-agent`.

## Fallbacks

- Só usar ferramentas genéricas de web fetch quando o caso não for coberto pelo MCP prioritário.
- Só usar busca web comum para documentação quando o `context7` não atender o caso.

## Guardrails

- Não aplicar esta política ao Antigravity.
- Não hardcodar credenciais neste arquivo.
```

- [ ] **Step 2: Verificar o conteúdo escrito**

Run:

```powershell
python -c "from pathlib import Path; print(Path(r'C:\Projetos\Stout\rules\opencode_tool_routing.md').read_text(encoding='utf-8'))"
```

Expected: o texto inclui `tavily-search`, `context7`, `context-agent` e a frase de escopo separando OpenCode de Antigravity.

---

## Task 2: Ligar a política global ao OpenCode e adicionar Tavily

**Files:**
- Modify: `C:/Projetos/Stout/.opencode/opencode.json`

- [ ] **Step 1: Escrever o teste mental/falha inicial pela ausência de Tavily e da instrução**

Estado atual esperado antes da edição:

```json
"instructions": [
  "GEMINI.md",
  "MISSION_STOUT.md",
  "memory/ecosystem.md",
  "memory/preferences.md"
]
```

E no bloco `mcp` não existe nenhuma chave `tavily-search`.

- [ ] **Step 2: Adicionar a nova instrução global em `instructions`**

O array `instructions` deve ficar assim:

```json
"instructions": [
  "GEMINI.md",
  "MISSION_STOUT.md",
  "memory/ecosystem.md",
  "memory/preferences.md",
  "rules/opencode_tool_routing.md"
]
```

- [ ] **Step 3: Adicionar o MCP `tavily-search` ao bloco `mcp`**

Inserir este bloco no objeto `mcp` de `C:/Projetos/Stout/.opencode/opencode.json`:

```json
"tavily-search": {
  "type": "local",
  "command": ["npx", "-y", "tavily-mcp"],
  "enabled": true,
  "environment": {
    "TAVILY_API_KEY": "{env:TAVILY_API_KEY}"
  }
}
```

- [ ] **Step 4: Validar que o JSON continua válido**

Run:

```powershell
python -c "import json; json.load(open(r'C:\Projetos\Stout\.opencode\opencode.json', encoding='utf-8')); print('JSON válido')"
```

Expected: `JSON válido`

- [ ] **Step 5: Verificar o diff estrutural da config**

Run:

```powershell
git -C "C:\Projetos\Stout" diff -- ".opencode/opencode.json"
```

Expected: apenas a entrada `rules/opencode_tool_routing.md` em `instructions` e o novo bloco `tavily-search` em `mcp`.

---

## Task 3: Verificação final sem tocar Antigravity

**Files:**
- Verify only: `C:/Projetos/Stout/.opencode/opencode.json`
- Verify only: `C:/Projetos/Stout/rules/opencode_tool_routing.md`

- [ ] **Step 1: Confirmar que nenhum arquivo em `antigravity/` foi alterado**

Run:

```powershell
git -C "C:\Projetos\Stout" diff --name-only
```

Expected: aparecem apenas `.opencode/opencode.json` e `rules/opencode_tool_routing.md`.

- [ ] **Step 2: Confirmar que a política está explícita**

Run:

```powershell
python -c "from pathlib import Path; print(Path(r'C:\Projetos\Stout\rules\opencode_tool_routing.md').read_text(encoding='utf-8'))"
```

Expected: a política menciona claramente OpenCode, Tavily, Context7 e `context-agent`.

---

## Self-Review

- **Spec coverage:** o plano cobre configuração global do OpenCode, inclusão do MCP Tavily, política de roteamento e isolamento do Antigravity.
- **Placeholder scan:** não há `TODO`, `TBD` ou passos genéricos sem conteúdo concreto.
- **Type consistency:** o nome do arquivo de política, a chave `tavily-search` e o uso de `rules/opencode_tool_routing.md` permanecem consistentes em todo o plano.
