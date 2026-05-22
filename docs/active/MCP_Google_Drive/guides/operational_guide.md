# Guia Operacional: Google Drive MCP (Stout Edition)

Este documento descreve como configurar e manter a integração do Google Drive via Model Context Protocol.

## 🛠️ Stack Técnica
- **Server:** `@piotr-agier/google-drive-mcp` (v2.2.0+)
- **Protocolo:** JSON-RPC sobre `stdio`
- **Autenticação:** OAuth2 (Google Cloud Console)

## 📂 Configuração de Ambiente (.env)
Para que o servidor funcione, as seguintes variáveis devem estar no `.env` global:
```bash
# CAMINHO ABSOLUTO para o JSON de credenciais gerado no Google Cloud
GOOGLE_DRIVE_OAUTH_CREDENTIALS=C:\Users\victor.bernardi\.credentials\GOOGLE_DRIVE_OAUTH_CREDENTIALS.json

# IMPORTANTE: Mantenha GOOGLE_APPLICATION_CREDENTIALS comentada para evitar conflito
# GOOGLE_APPLICATION_CREDENTIALS=...
```

## 🛠️ Troubleshooting (Bugs Comuns)

### 1. Erro `invalid_grant: account not found`
- **Causa:** O MCP está tentando usar uma Service Account inválida ou não autorizada.
- **Solução:** Comente a variável `GOOGLE_APPLICATION_CREDENTIALS` no `.env`. O servidor fará fallback para o OAuth2.

### 2. Ferramentas Não Visíveis (Tool Missing)
- **Sintoma:** O LLM não vê as funções `createFolder`, `listFolder`, etc.
- **Solução:** Verifique se o `settings.json` do Gemini CLI aponta corretamente para o pacote `@piotr-agier/google-drive-mcp`. Se o problema persistir, use um script bridge em Node.js (ex: `scripts/gdrive_validation_final.js`) para testar a comunicação direta.

### 3. Nomes de Ferramentas (Case Sensitive)
- **Padrão Atual:** O servidor utiliza **camelCase**. 
- **Correto:** `createFolder`, `createTextFile`, `listFolder`.
- **Incorreto:** `create_folder`, `list_files`.

## 🧪 Script de Validação de Emergência
Caso haja dúvida sobre a integridade, execute:
`node scripts/gdrive_validation_final.js` (na raiz da Shared AI Memory).
