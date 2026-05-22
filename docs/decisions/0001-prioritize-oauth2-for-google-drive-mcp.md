# ADR-0001: Priorizar OAuth2 sobre Service Account no Google Drive MCP

* Status: accepted
* Date: 2026-05-11
* Decision-makers: Gemini CLI, Victor Bernardi
* Consulted: Antigravity

## Context and Problem Statement

O servidor MCP `@piotr-agier/google-drive-mcp` estava configurado com credenciais duplas: `Service Account` (via `GOOGLE_APPLICATION_CREDENTIALS`) e `OAuth2` (via `GOOGLE_DRIVE_OAUTH_CREDENTIALS`). Durante a inicialização, o servidor priorizava a Service Account, que retornava o erro `invalid_grant: Invalid grant: account not found`, bloqueando todas as operações de escrita e leitura.

## Decision Outcome

Decidimos desativar a `Service Account` e forçar o uso do fluxo **OAuth2**. 

### Consequences
* **Positivo:** Estabilização imediata do acesso CRUD, Busca e Mover.
* **Positivo:** Maior segurança e controle granular via conta de usuário.
* **Neutro:** Necessidade de monitorar a expiração dos tokens (refresh token automático está funcional).

## Confirmation
A validação foi confirmada via script `gdrive_validation_oauth.js`, executando o ciclo completo de criação e exclusão de arquivos no Drive do usuário.

---
*Referência: docs/active/MCP_Google_Drive/status/VALIDATION_REPORT_2026-05-11.md*
