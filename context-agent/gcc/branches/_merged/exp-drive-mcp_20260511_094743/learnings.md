# Aprendizados da Estabilizao do Google Drive MCP

## O que foi testado?

- A inicializao e a autenticao do pacote `@piotr-agier/google-drive-mcp`.

## O que funcionou?

- O pacote suporta autenticao OAuth segura via arquivo local JSON isolado.
- O usurio realizou o login via navegador (`vobernardi@gmail.com`) com sucesso.
- Restringimos os escopos explicitamente na tela de consentimento para no sobrecarregar o MCP (focando apenas em Drive, excluindo Docs, Sheets e Calendar).

## O que falhou / Gaps preenchidos?

- A hiptese inicial de consertar o script Python e usar a Service Account estava errada. O pacote exige fluxo OAuth para ter o consentimento explcito do usurio.

## Como o veneno foi evitado?

- Utilizando esta branch isolada (exp-drive-mcp) para realizar os testes de listagem e autenticao antes de oficializar o servidor no Kernel do projeto.
