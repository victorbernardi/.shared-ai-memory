# Estratgia de Estabilizao: Google Drive MCP (v2 - Framework GCC)

> **Status:** 🏃 EM EXECUO (Aprovado)
> **Relacionado:** Resoluo de MCPs Obrigatrios (NotebookLM, Context7, Google Drive)

## 1. Objetivo
Resolver a falha de conexo com o Google Drive MCP utilizando isolamento de memria (Git-Context-Controller), garantindo estabilidade e documentao tcnica atualizada.

## 2. Diagnstico Atual (Corrigido)
- **Pacote Original:** `@modelcontextprotocol/server-google-drive` retorna 404.
- **Alternativa Descoberta:** `@piotr-agier/google-drive-mcp` (identificado via Context7).
- **Falso Positivo de Auth:** O erro HTTP 400 em `test_mcp_script.py`  referente a um MCP interno do Google Developer Knowledge, no ao servidor Node.js do Google Drive. No devemos focar nele.

## 3. Plano de Ao (Ciclo Antifrgil)

### Passo 1: Laboratrio e Pesquisa (Regra 3 - GCC)
- Ativar branch isolado: `python scripts/gcc_controller.py branch exp-drive-mcp`.
- Instalar temporariamente `@piotr-agier/google-drive-mcp` via `npx` e rodar `--help` para mapear os requisitos exatos de autenticao (ex: precisa de `GOOGLE_APPLICATION_CREDENTIALS` ou OAuth?).

### Passo 2: Configurao Cirrgica (Settings)
- Preencher as credenciais exigidas (com base no Passo 1) no `.env`.
- Atualizar o `.gemini/settings.json` do projeto com o pacote verificado.

### Passo 3: Validao Emprica (TDD Post-Fix)
- Iniciar o MCP isoladamente (mock/help check).
- **Caso Falhe:** Acionar `gcc discard` para limpar o contexto envenenado e replanejar.
- **Caso Sucesso:** Acionar `gcc merge` para consolidar a alterao na raiz.

### Passo 4: Consolidao na Golden Copy
- Atualizar o `ANTIGRAVITY.md` (seo MCPs) com o novo pacote, status e ferramentas oferecidas.
- Persistir o novo estado na memria de longo prazo usando a skill `context-agent`.
