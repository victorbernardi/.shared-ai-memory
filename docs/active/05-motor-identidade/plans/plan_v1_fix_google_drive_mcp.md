# Estratgia de Estabilizao: Google Drive MCP (v1)

> **Status:** ⏳ AGUARDANDO APROVAO
> **Relacionado:** Resoluo de MCPs Obrigatrios (NotebookLM, Context7, Google Drive)

## 1. Objetivo
Resolver a falha de conexo com o Google Drive MCP, garantindo que o servidor seja inicializado corretamente e que as credenciais permitam o acesso aos arquivos.

## 2. Diagnstico Atual
- **Pacote:** `@modelcontextprotocol/server-google-drive` no `settings.json` retorna 404 (Inexistente).
- **Credenciais:** `GOOGLE_DRIVE_API_KEY` vazia no `.env`.
- **Token:** Script de teste falha com HTTP 400 (Bad Request).

## 3. Plano de Ao

### Passo 1: Pesquisa de Implementao (Research)
- Utilizar o **Context7** para obter os detalhes de configurao do pacote `/piotr-agier/google-drive-mcp` (identificado como alternativa vivel).
- Verificar se o projeto exige o uso de **Service Account** (conforme `google-service-account.json` existente) ou **OAuth Manual** (como o NotebookLM).

### Passo 2: Reconfigurao do Servidor (Settings)
- Atualizar o `.gemini/settings.json` com o pacote correto (ex: `@piotr-agier/google-drive-mcp` ou similar verificado).
- Configurar as variveis de ambiente necessrias (`GOOGLE_DRIVE_API_KEY` ou caminhos para `google-service-account.json`).

### Passo 3: Correo de Autenticao (Auth)
- Se usar Service Account: Corrigir o script de gerao de JWT para evitar o erro HTTP 400.
- Se usar OAuth: Implementar um script de trigger similar ao usado no NotebookLM para abrir a janela de login e capturar cookies/tokens.

### Passo 4: Verificao de Integridade (Validation)
- Executar o CLI do MCP com a flag `--help`.
- Realizar uma listagem real de arquivos na raiz do Google Drive do usurio.

## 4. Riscos e Mitigaes
- **Risco:** Incompatibilidade do pacote com a verso do Node.js (v20).
- **Mitigao:** Testar via `npx` isolado antes de integrar ao `settings.json`.

---

## 🛑 STANDBY MODE: AGUARDANDO APROVAO HUMANA
*Por favor, valide os passos acima para que eu possa prosseguir com a execuo.*
