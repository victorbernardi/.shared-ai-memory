# 🧠 ANTIGRAVITY.md — Kernel Agêntico (Global)

> **Ambiente:** Gemini CLI
> **Projeto:** MCP_Google_Drive
> **Objetivo:** Estabilização e Governança Universal de Servidores MCP

## 1. MCPs Configurados

- **context7**  Ingesto de documentao tcnica via `@upstash/context7-mcp` (Tools: `resolve-library-id`, `query-docs`)
- **google-drive**  Acesso a arquivos via `@piotr-agier/google-drive-mcp`. (Autenticado via OAuth `google-oauth-client.json` )
- **notebooklm**  Pesquisa e anlise via `notebooklm-mcp` (Autenticado via login OAuth )

## 2.  Regras de Segurana e Autenticao (OAuth)

**Google Drive MCP:** Foi configurado utilizando o pacote `@piotr-agier/google-drive-mcp` com fluxo de autenticao OAuth isolado.
- **Credenciais:** Salvas de forma segura em `C:\Users\victor.bernardi\.credentials\GOOGLE_DRIVE_OAUTH_CREDENTIALS.json` e passadas via varivel global.
- **Escopos Liberados (Opt-In):** Para no sobrecarregar a permisso, foram habilitados apenas os seguintes escopos (Conta: `vobernardi@gmail.com` | App: `Codex Second Brain`):
  1. *Ver, editar, criar e excluir todos os seus arquivos do Google Drive.*
  2. *Ver e baixar todos os seus arquivos do Google Drive.*
  3. *Ver, editar, criar e excluir apenas os arquivos do Google Drive que voc usa com este app.*
- **Restrio:** Escopos de Calendar, Spreadsheets, Docs e Slides no foram explicitamente checados na tela de consentimento para focar estritamente na gesto de arquivos.

## 3. Uso dos MCPs

- Sempre inicializar no incio da sesso
- Usar `context7` para validar documentao de bibliotecas
- Usar `google-drive` para ler/salvar arquivos de referncia
- Usar `notebooklm` para criar notebooks de pesquisa
